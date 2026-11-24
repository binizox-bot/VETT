#!/usr/bin/env python3
"""Read-only verification for the frozen delivery."""

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def jsonl(name):
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    manifest = json.loads((HERE / "FROZEN_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "FROZEN"
    assert not manifest["reserved_root_overlap"]
    for item in manifest["files"]:
        assert sha_file(HERE / item["path"]) == item["sha256"], item["path"]

    checksum_rows = []
    for line in (HERE / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        checksum_rows.append(rel)
        assert sha_file(HERE / rel) == digest, rel
    assert len(checksum_rows) == len(set(checksum_rows))

    inputs = jsonl("model_inputs.jsonl")
    gold = jsonl("private_gold.jsonl")
    evidence = jsonl("evidence_chain.jsonl")
    assert len(inputs) == len(gold) == len(evidence) == 5
    assert {row["sample_id"] for row in inputs} == {row["sample_id"] for row in gold} == {row["sample_id"] for row in evidence}
    input_by_id = {row["sample_id"]: row for row in inputs}
    for row in inputs:
        assert sha_text(row["prompt"]) == row["prompt_sha256"]
        assert "gold" not in row
        assert "match_" not in row["prompt"]
    for row in gold:
        number = int(row["match_root"].split("_")[1])
        assert not 121 <= number <= 160
        assert row["field_order"] == list(row["gold"])
    for row in evidence:
        prompt = input_by_id[row["sample_id"]]["prompt"]
        for span in row["evidence_sentences"]:
            start = span["prompt_char_span"]["start"]
            end = span["prompt_char_span"]["end_exclusive"]
            assert prompt[start:end] == span["quote"], row["sample_id"]

    with (HERE / "historical_event_intersections.csv").open(encoding="utf-8-sig", newline="") as handle:
        intersections = list(csv.DictReader(handle))
    with (HERE / "full_window_transitions.csv").open(encoding="utf-8-sig", newline="") as handle:
        transitions = list(csv.DictReader(handle))
    assert len(intersections) == 24
    assert len(transitions) == 12
    blind = (HERE / "blind_review_40" / "BLIND_REVIEW_40.md").read_text(encoding="utf-8")
    assert sum(1 for line in blind.splitlines() if line.startswith("## S")) == 40
    print(json.dumps({
        "passed": True,
        "frozen_files_verified": len(manifest["files"]),
        "manifest_files_verified": len(checksum_rows),
        "model_inputs": len(inputs),
        "historical_event_intersections": len(intersections),
        "full_window_pairs": len(transitions),
        "blind_items": 40,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
