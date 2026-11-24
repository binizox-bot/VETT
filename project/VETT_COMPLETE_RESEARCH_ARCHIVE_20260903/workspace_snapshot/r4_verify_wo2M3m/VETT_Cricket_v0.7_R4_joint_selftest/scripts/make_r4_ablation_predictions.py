#!/usr/bin/env python3
"""Create private mechanism-ablation predictions for R4 candidate states."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def set_cell(tables: list[dict[str, Any]], cell_id: str, value: Any) -> None:
    for table in tables:
        for row in table["rows"]:
            for column in table["columns"]:
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                if f"{table['table_id']}.{row['row_id']}.{suffix}" == cell_id:
                    row[column] = value
                    return
    raise KeyError(cell_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    dataset = load_jsonl(args.dataset)
    manifest = {row["root_id"]: row for row in json.loads(args.manifest.read_text(encoding="utf-8"))}
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for method in ("block_a_unresolved", "block_b_unresolved", "both_blocks_unresolved"):
        predictions = []
        for instance in dataset:
            tables = copy.deepcopy(instance["gold"]["tables"])
            if instance["view"] == "R4S":
                blocks = manifest[instance["root_id"]]["joint_constraint_blocks"]
                selected = blocks[:1] if method == "block_a_unresolved" else blocks[1:] if method == "block_b_unresolved" else blocks
                for block in selected:
                    for target in block["targets"]:
                        set_cell(tables, target["cell_id"], target["alternate_value"])
            predictions.append({"instance_id": instance["instance_id"], "method": method, "tables": tables})
        write_jsonl(args.output_dir / f"{method}.predictions.jsonl", predictions)
    print(json.dumps({"methods": 3, "instances_per_method": len(dataset)}, indent=2))


if __name__ == "__main__":
    main()
