#!/usr/bin/env python3
"""Combine frozen V3 controls with fresh V4-SDC treatment predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOTS = {"match_0185", "match_0106", "match_0178"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", required=True)
    parser.add_argument("--frozen-v3", type=Path, required=True)
    parser.add_argument("--fresh-v4", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    controls = []
    for item in load_jsonl(args.frozen_v3):
        if item["instance_id"].endswith(".V3"):
            root = item["instance_id"].rsplit(".", 1)[0]
            if root in ROOTS:
                cloned = dict(item)
                cloned["instance_id"] = f"{root}.V3C"
                cloned["method"] = args.method
                controls.append(cloned)

    treatments = [
        item
        for item in load_jsonl(args.fresh_v4)
        if item["instance_id"].endswith(".V4SDC")
    ]
    if len(controls) != 3 or len(treatments) != 3:
        raise SystemExit(
            f"expected 3 controls and 3 treatments, got {len(controls)} and {len(treatments)}"
        )

    rows = sorted(controls + treatments, key=lambda item: item["instance_id"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(json.dumps({"method": args.method, "predictions": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
