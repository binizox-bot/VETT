#!/usr/bin/env python3
"""Build controlled diagnostic predictions.

These are oracle ablations, not model baselines. They isolate the measurable
penalty from ignoring derivations, revisions, or document scope.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def slug(column: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")


def remove_cells(tables: list[dict[str, Any]], removed: set[str]) -> None:
    for table in tables:
        for row_index, row in enumerate(table.get("rows", []), 1):
            row_id = row.get("row_id", f"r{row_index:03d}")
            for column in table.get("columns", []):
                cell_id = f"{table['table_id']}.{row_id}.{slug(column)}"
                if cell_id in removed:
                    row.pop(column, None)


def replace_cell(tables: list[dict[str, Any]], cell_id: str, value: Any) -> bool:
    for table in tables:
        for row_index, row in enumerate(table.get("rows", []), 1):
            row_id = row.get("row_id", f"r{row_index:03d}")
            for column in table.get("columns", []):
                if f"{table['table_id']}.{row_id}.{slug(column)}" == cell_id:
                    row[column] = value
                    return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument(
        "--mode",
        required=True,
        choices=["no_derivation", "version_unaware", "scope_misselection"],
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    instances = load_jsonl(args.dataset)
    roots = {root["root_id"]: root for root in load_jsonl(args.roots)}
    predictions = []
    for instance in instances:
        if instance["release_status"] != "RELEASE_CANDIDATE":
            continue
        tables = json.loads(json.dumps(instance["gold"]["tables"]))
        if args.mode == "no_derivation":
            removed = {
                item["cell_id"]
                for item in instance["gold"]["cell_provenance"]
                if item["support_type"] in {"DERIVED_LOCAL", "DERIVED_GLOBAL"}
            }
            remove_cells(tables, removed)
        elif args.mode == "version_unaware":
            grouped: dict[str, list[dict[str, Any]]] = {}
            for claim in instance["private_metadata"].get("revision_claims", []):
                grouped.setdefault(claim["cell_id"], []).append(claim)
            for cell_id, claims in grouped.items():
                stale = next(
                    (claim for claim in claims if claim["status"] in {"stale", "retracted"}),
                    None,
                )
                if stale:
                    replace_cell(tables, cell_id, stale["value"])
        elif args.mode == "scope_misselection" and instance["view"] == "V3":
            distractor = (
                instance["private_metadata"]
                .get("generator", {})
                .get("distractor_selection", {})
                .get("root_id")
            )
            if distractor in roots:
                tables = json.loads(json.dumps(roots[distractor]["tables"]))
        predictions.append({"instance_id": instance["instance_id"], "tables": tables})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in predictions),
        encoding="utf-8",
    )
    print(json.dumps({"mode": args.mode, "predictions": len(predictions)}, indent=2))


if __name__ == "__main__":
    main()
