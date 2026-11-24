#!/usr/bin/env python3
"""Apply the first current-model naturalization calibration output.

The prose below was authored by the conversational model for match_0009.V2.
It is deliberately kept separate from the full candidate file until an
independent inverse extractor and human reviewer approve it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


INSTANCE_ID = "match_0009.V2"

PRELIMINARY = (
    "The early live ticker carried three figures while the scorer was still reviewing the innings: "
    "Tyler Grant was listed with 40, Noah Reed with five wickets, and the first-innings extras with "
    "22. A note beside the card said those numbers were provisional."
)

CORRECTIONS = [
    (
        "match_0009.I1.batting.r001.r",
        "After reviewing the scoring record, the official scorer confirmed that Tyler Grant made "
        "39 in the first innings, replacing the provisional figure of 40.",
    ),
    (
        "match_0009.I1.bowling.r001.w",
        "The same notice credited Noah Reed with three wickets rather than the five shown on the "
        "live card.",
    ),
    (
        "match_0009.I1.innings_summary.r002.value",
        "It also fixed the first-innings extras at 19, superseding the provisional total of 22.",
    ),
]

STALE = (
    "A fan mirror saved before the scorer's review still shows Tyler Grant on 40, gives Noah Reed "
    "five wickets and lists 22 extras for the first innings. The mirror does not carry the official "
    "correction."
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    instance = next(item for item in load_jsonl(args.instances) if item["instance_id"] == INSTANCE_ID)
    documents = {item["document_id"]: item for item in instance["documents"]}
    documents["preliminary_feed"]["text"] = PRELIMINARY
    documents["stale_repost"]["text"] = STALE

    correction_text = "\n".join(text for _, text in CORRECTIONS)
    documents["official_correction"]["text"] = correction_text
    new_spans = {}
    cursor = 0
    for cell_id, text in CORRECTIONS:
        start = correction_text.index(text, cursor)
        end = start + len(text)
        cursor = end
        new_spans[cell_id] = {
            "document_id": "official_correction",
            "start": start,
            "end": end,
            "quote_hash": sha256_text(text),
        }

    for provenance in instance["gold"]["cell_provenance"]:
        spans = [
            span
            for span in provenance["evidence_spans"]
            if span["document_id"] != "official_correction"
        ]
        if provenance["cell_id"] in new_spans:
            spans.append(new_spans[provenance["cell_id"]])
        provenance["evidence_spans"] = spans

    generator = instance["private_metadata"]["generator"]
    generator["model_assisted_polish_status"] = "CALIBRATION_DRAFT"
    generator["model_role"] = "current_conversational_model_verbalizer"
    instance["private_metadata"]["validation"]["human_review"] = "PENDING"
    instance["private_metadata"]["validation"]["independent_inverse_extractor"] = "PENDING"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(instance, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"instance_id": INSTANCE_ID, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
