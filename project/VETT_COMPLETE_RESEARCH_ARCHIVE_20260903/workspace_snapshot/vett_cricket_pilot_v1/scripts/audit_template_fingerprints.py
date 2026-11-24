#!/usr/bin/env python3
"""Measure repeated surface-form fingerprints in generated documents."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sentence_skeletons(text: str) -> list[str]:
    skeletons = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
        sentence = sentence.strip().casefold()
        if not sentence:
            continue
        sentence = re.sub(r"\b\d+(?:\.\d+)?\b", "<n>", sentence)
        sentence = re.sub(r"\b[a-z]+(?:\s+[a-z]+){1,3}\b(?='s\b)", "<entity>", sentence)
        sentence = re.sub(r"\s+", " ", sentence)
        skeletons.append(sentence)
    return skeletons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    instances = [
        item
        for item in load_jsonl(args.instances)
        if item["release_status"] == "RELEASE_CANDIDATE"
    ]
    report: dict[str, Any] = {"views": {}}
    for view in ("V1", "V2", "V3"):
        subset = [item for item in instances if item["view"] == view]
        skeletons = [
            skeleton
            for instance in subset
            for document in instance["documents"]
            for skeleton in sentence_skeletons(document["text"])
        ]
        counts = Counter(skeletons)
        repeated = sum(count for count in counts.values() if count > 1)
        top = counts.most_common(20)
        report["views"][view] = {
            "instances": len(subset),
            "sentences": len(skeletons),
            "unique_sentence_skeletons": len(counts),
            "unique_skeleton_ratio": round(len(counts) / len(skeletons), 6) if skeletons else None,
            "repeated_sentence_rate": round(repeated / len(skeletons), 6) if skeletons else None,
            "top_20_coverage": round(sum(count for _, count in top) / len(skeletons), 6)
            if skeletons
            else None,
            "top_skeletons": [{"skeleton": text, "count": count} for text, count in top],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
