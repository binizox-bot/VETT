#!/usr/bin/env python3
"""Create a gold-free R10 input compatible with the baseline runner.

This adapter reads only the public R10 instance. It never imports private gold
or evidence. The emitted JSONL can therefore be copied to an isolated model
worker together with the baseline prompts and runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    public = json.loads(args.public.read_text(encoding="utf-8"))
    contract = {
        "format": "json",
        "top_level": {"instance_id": public["instance_id"], "tables": public["tables"]},
        "rules": [
            public["output_rule"],
            "Return JSON only.",
            "Do not change table order, table_type, innings_id, columns, or row-key values.",
            "Preserve cricket over notation as x.y legal-ball notation, not a decimal.",
        ],
    }
    item = {
        "instance_id": public["instance_id"],
        "instruction": public["instruction"],
        "documents": [
            {
                "document_id": public["document"]["document_id"],
                "source_label": "delivery commentary",
                "source_tier": "public",
                "arrival_index": 0,
                "text": public["document"]["text"],
            }
        ],
        "output_contract": contract,
        "view": "R10_FIXED_SCHEMA",
        "difficulty": {"tier": 5},
    }
    canonical = json.dumps(item, ensure_ascii=False, sort_keys=True)
    item["input_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(item, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"instance_id": item["instance_id"], "input_sha256": item["input_sha256"]}))


if __name__ == "__main__":
    main()
