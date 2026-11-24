#!/usr/bin/env python3
"""Prepare one minimally curated root for the R6 event-level pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_ROOT_ID = "match_0031"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--root-id", default=DEFAULT_ROOT_ID)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    args = parser.parse_args()
    root = next(
        json.loads(line) for line in args.canonical.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line)["root_id"] == args.root_id
    )
    removed = []
    for table in root["tables"]:
        if table["table_type"] != "Batting":
            continue
        kept = []
        for row in table["rows"]:
            observable = int(row["B"]) > 0 or bool(str(row["Dismissal"]).strip())
            if observable:
                kept.append(row)
            else:
                removed.append({
                    "table_id": table["table_id"],
                    "row_id": row["row_id"],
                    "batter": row["Batter"],
                    "reason": "DNB roster placeholder has no delivery-level evidence",
                })
        table["rows"] = kept
    removed_coordinates = {(row["table_id"], row["row_id"]) for row in removed}
    original_cell_count = len(root.get("cells", []))
    root["cells"] = [
        cell for cell in root.get("cells", [])
        if (cell["table_id"], cell["row_id"]) not in removed_coordinates
    ]
    root["r6_curation"] = {
        "policy": "event_observable_batting_rows_only",
        "removed_rows": removed,
        "removed_cells": original_cell_count - len(root["cells"]),
        "source_root_unchanged": True,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(root, ensure_ascii=False, indent=2) + "\n"
    args.output_json.write_text(serialized, encoding="utf-8")
    args.output_jsonl.write_text(json.dumps(root, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "root_id": args.root_id,
        "removed_rows": len(removed),
        "removed_cells": root["r6_curation"]["removed_cells"],
        "policy": root["r6_curation"]["policy"],
    }, indent=2))


if __name__ == "__main__":
    main()
