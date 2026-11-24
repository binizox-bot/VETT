#!/usr/bin/env python3
"""Create an oracle in the public semantic-table format with all IDs removed."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    predictions = []
    for line in args.dataset.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        instance = json.loads(line)
        if not instance["gold"]["scored_cell_ids"]:
            continue
        tables = []
        for table in instance["gold"]["tables"]:
            match = re.search(r"\.(I[12])\.", table["table_id"])
            tables.append(
                {
                    "table_type": table["table_type"],
                    "innings": match.group(1) if match else None,
                    "columns": table["columns"],
                    "rows": [
                        {key: value for key, value in row.items() if key != "row_id"}
                        for row in table["rows"]
                    ],
                }
            )
        predictions.append(
            {
                "instance_id": instance["instance_id"],
                "method": "semantic_format_oracle",
                "tables": tables,
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in predictions),
        encoding="utf-8",
    )
    print(json.dumps({"predictions": len(predictions)}, indent=2))


if __name__ == "__main__":
    main()
