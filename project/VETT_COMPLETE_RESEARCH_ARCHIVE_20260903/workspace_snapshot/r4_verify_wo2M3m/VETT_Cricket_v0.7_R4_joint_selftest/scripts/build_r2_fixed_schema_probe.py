#!/usr/bin/env python3
"""Build the three-root R2 fixed-schema factual-reasoning probe."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


ROOTS = ("match_0185", "match_0106", "match_0178")
ROW_KEYS = {
    "Match Summary": "Field",
    "Innings Summary": "Field",
    "Batting": "Batter",
    "Bowling": "Bowler",
    "Partnerships": "Partnership",
    "Fall of Wickets": "Wkt",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def gold_cells(instance: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for table in instance["gold"]["tables"]:
        for row in table["rows"]:
            for column in table["columns"]:
                if column not in row:
                    continue
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                result[f"{table['table_id']}.{row['row_id']}.{suffix}"] = row[column]
    return result


def query_for_cell(instance: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for table in instance["gold"]["tables"]:
        innings_match = re.search(r"\.(I[12])\.", table["table_id"])
        innings = innings_match.group(1) if innings_match else None
        row_key = ROW_KEYS[table["table_type"]]
        for row in table["rows"]:
            for column in table["columns"]:
                suffix = re.sub(r"[^a-z0-9]+", "_", column.lower()).strip("_")
                observed = f"{table['table_id']}.{row['row_id']}.{suffix}"
                if observed == cell_id:
                    return {
                        "table_type": table["table_type"],
                        "innings": innings,
                        "row_key": row_key,
                        "row_value": row[row_key],
                        "target_column": column,
                    }
    raise KeyError(cell_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v4-scoring", type=Path, required=True)
    parser.add_argument("--construction-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    source = {
        row["root_id"]: row
        for row in load_jsonl(args.v4_scoring)
        if row["view"] == "V4SDC" and row["root_id"] in ROOTS
    }
    if set(source) != set(ROOTS):
        raise SystemExit(f"missing roots: {sorted(set(ROOTS) - set(source))}")

    scoring_rows = []
    blind_rows = []
    manifest = []
    for root_id in ROOTS:
        base = source[root_id]
        candidate = json.loads(
            (args.construction_dir / f"{root_id}.r2.json").read_text(encoding="utf-8")
        )
        challenge_ids = candidate["challenge_cell_ids"]
        if challenge_ids != base["gold"]["scored_cell_ids"]:
            raise SystemExit(f"{root_id}: R2 challenge cells differ from V4")
        if len(challenge_ids) != 12 or len(set(challenge_ids)) != 12:
            raise SystemExit(f"{root_id}: challenge IDs must be 12 unique cells")

        values = gold_cells(base)
        records = candidate["target_records"]
        if len(records) != 12 or {r["cell_id"] for r in records} != set(challenge_ids):
            raise SystemExit(f"{root_id}: target records do not cover challenge cells")
        for record in records:
            cell_id = record["cell_id"]
            if str(record["gold_value"]).strip() != str(values[cell_id]).strip():
                raise SystemExit(f"{root_id}: gold mismatch for {cell_id}")

        canonical_queries = [query_for_cell(base, cell_id) for cell_id in challenge_ids]
        if candidate["query_schema"] != canonical_queries:
            raise SystemExit(f"{root_id}: query schema differs from canonical locations")

        instance = copy.deepcopy(base)
        instance["instance_id"] = f"{root_id}.R2FS"
        instance["view"] = "R2FS"
        instance["difficulty"] = {
            "tier": 6,
            "axes": {
                "length": 0.88,
                "ordering": 0.95,
                "scope": 0.92,
                "versioning": 0.98,
                "repetition": 0.96,
                "state_revision": 0.98,
                "dependency_depth": 0.97,
                "cross_table_coupling": 0.96,
                "schema_entropy": 0.0
            },
        }
        instance["documents"] = [
            {
                "arrival_index": 0,
                "document_id": "r2_continuous_broadcast",
                "source_label": f"{root_id} target match — continuous broadcast",
                "source_tier": "trusted",
                "text": candidate["commentary_text"],
            }
        ]
        instance["instruction"] = (
            "Resolve repeated mentions, retractions, revisions, legal-ball state, "
            "distributed numerical dependencies and cross-table cricket constraints. "
            "Return only the values requested by the supplied value-free query schema."
        )
        instance["gold"]["scored_cell_ids"] = challenge_ids
        instance["private_metadata"]["r2_fixed_schema"] = {
            "target_records": records,
            "query_schema": canonical_queries,
            "commentary_word_count": len(candidate["commentary_text"].split()),
        }
        scoring_rows.append(instance)
        blind_rows.append(
            {
                "instance_id": instance["instance_id"],
                "instruction": instance["instruction"],
                "documents": instance["documents"],
                "queries": canonical_queries,
                "output_rule": (
                    "Return semantic tables containing exactly the requested row keys "
                    "and target columns. Do not invent unrequested values."
                ),
            }
        )
        manifest.append(
            {
                "root_id": root_id,
                "instance_id": instance["instance_id"],
                "challenge_cell_ids": challenge_ids,
                "queries": canonical_queries,
                "target_records": records,
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "r2_scoring_instances_3_private.jsonl", scoring_rows)
    write_jsonl(args.output_dir / "r2_blind_queries_3.jsonl", blind_rows)
    (args.output_dir / "r2_manifest_private.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"roots": 3, "instances": 3, "queries": 36}, indent=2))


if __name__ == "__main__":
    main()
