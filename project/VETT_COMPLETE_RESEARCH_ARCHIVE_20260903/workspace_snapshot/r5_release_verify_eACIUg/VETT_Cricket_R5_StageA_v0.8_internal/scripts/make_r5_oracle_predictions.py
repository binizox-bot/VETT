#!/usr/bin/env python3
"""Create format-only oracle predictions for testing the R5 scorer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.private.read_text(encoding="utf-8").splitlines() if line.strip()]
    predictions = []
    for row in rows:
        predictions.append({
            "instance_id": row["instance_id"],
            "method": "semantic_oracle",
            "tables": [
                {
                    "table_type": table["table_type"],
                    "innings_id": table["innings_id"],
                    "columns": table["columns"],
                    "rows": table["rows"],
                }
                for table in row["gold_tables"]
            ],
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in predictions),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
