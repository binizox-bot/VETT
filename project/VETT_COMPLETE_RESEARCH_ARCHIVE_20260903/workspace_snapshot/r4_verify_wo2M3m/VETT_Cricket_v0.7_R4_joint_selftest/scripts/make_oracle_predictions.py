#!/usr/bin/env python3
"""Create perfect-format oracle predictions for scorer verification only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for line in args.dataset.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if not item["gold"]["scored_cell_ids"]:
            continue
        rows.append(
            {
                "instance_id": item["instance_id"],
                "method": "format_oracle",
                "model": "gold-copy-for-scorer-test",
                "tables": item["gold"]["tables"],
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} oracle predictions")


if __name__ == "__main__":
    main()
