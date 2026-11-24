#!/usr/bin/env python3
"""Create a value-free target-schema diagnostic for V4-SDC instances."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


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


def find_cell(instance: dict[str, Any], cell_id: str) -> dict[str, Any]:
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
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--scoring", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    blind = {row["instance_id"]: row for row in load_jsonl(args.blind)}
    scoring = {
        row["instance_id"]: row
        for row in load_jsonl(args.scoring)
        if row["view"] == "V4SDC"
    }
    rows = []
    for iid, instance in sorted(scoring.items()):
        public = blind[iid]
        rows.append(
            {
                "instance_id": iid,
                "instruction": public["instruction"],
                "documents": public["documents"],
                "queries": [
                    find_cell(instance, cell_id)
                    for cell_id in instance["gold"]["scored_cell_ids"]
                ],
                "output_rule": (
                    "Return only the requested row/column values in semantic cricket "
                    "tables. The queries disclose schema locations but no answers."
                ),
            }
        )
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({"instances": len(rows), "queries": sum(len(r["queries"]) for r in rows)}, indent=2))


if __name__ == "__main__":
    main()
