#!/usr/bin/env python3
"""Run structural and controlled ledger ablations for the single R6 instance."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from validate_r6_delivery_ledger import validate_innings


FORBIDDEN_PUBLIC_KEYS = {
    "gold", "gold_tables", "root_id", "event_ledger", "revision_records",
    "replay_event_ids", "challenge_cell_ids", "scored_cell_ids", "operation",
}


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)


def walk_keys(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        result.update(value)
        for child in value.values():
            result.update(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            result.update(walk_keys(child))
    return result


def recompute_state(ledger: dict[str, Any]) -> None:
    for innings in ledger["innings"]:
        score = 0
        wickets = 0
        for event in innings["events"]:
            score += event["batter_runs"] + event["extras_runs"]
            if event["dismissal"]:
                wickets += 1
            event["team_score_after"] = score
            event["wickets_after"] = wickets


def corrupt_provisional(ledger: dict[str, Any], revisions: list[dict[str, Any]]) -> dict[str, Any]:
    result = copy.deepcopy(ledger)
    events = {event["event_id"]: event for innings in result["innings"] for event in innings["events"]}
    for revision in revisions:
        event = events[revision["event_id"]]
        alternate_event = revision.get("alternate_event")
        if alternate_event:
            for field in (
                "is_legal", "batter_runs", "boundary_four", "boundary_six",
                "extras_type", "extras_runs",
            ):
                event[field] = alternate_event[field]
        else:
            alternate = revision["alternate_value"]
            if event["extras_type"]:
                event["extras_runs"] = alternate
            else:
                event["batter_runs"] = alternate
                event["boundary_four"] = alternate == 4
                event["boundary_six"] = alternate in (6, 8)
    recompute_state(result)
    return result


def duplicate_replays(ledger: dict[str, Any], replay_ids: set[str]) -> dict[str, Any]:
    result = copy.deepcopy(ledger)
    for innings in result["innings"]:
        expanded = []
        for event in innings["events"]:
            expanded.append(event)
            if event["event_id"] in replay_ids:
                duplicate = copy.deepcopy(event)
                duplicate["event_id"] = event["event_id"] + ".REPLAY_COUNTED"
                expanded.append(duplicate)
        innings["events"] = expanded
    recompute_state(result)
    return result


def score_ledger(root: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    details = [validate_innings(root, innings) for innings in ledger["innings"]]
    checks = sum(row["checks"] for row in details)
    failures = [failure for row in details for failure in row["failures"]]
    return {
        "checks": checks,
        "correct": checks - len(failures),
        "wrong": len(failures),
        "error_rate": len(failures) / checks,
        "failed_check_families": sorted({failure["check"].split(".", 1)[0] for failure in failures}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--ledger-validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = load_json(args.root)
    public = load_json(args.public)
    private = load_json(args.private)
    evidence = load_json(args.evidence)
    validation = load_json(args.ledger_validation)
    ledger = evidence["event_ledger"]
    failures = []

    leaked = sorted(walk_keys(public) & FORBIDDEN_PUBLIC_KEYS)
    if leaked:
        failures.append({"check": "public_private_key_leak", "observed": leaked})
    text = public["document"]["text"]
    if hashlib.sha256(text.encode()).hexdigest() != evidence["document_sha256"]:
        failures.append({"check": "document_hash"})
    if validation["status"] != "PASS" or validation["failure_count"]:
        failures.append({"check": "ledger_round_trip", "observed": validation})

    compact_patterns = {
        "batting_row": r"\bscor(?:ed|ing)\s+\d+\s+(?:runs\s+)?from\s+\d+\s+balls\b",
        "bowling_row": r"\breturned\s+\d+(?:\.\d+)?\s+overs\b",
        "partnership_row": r"\badded\s+\d+\s+between\s+\d+\.\d+-\d+\.\d+\b",
        "construction_meta": r"\b(?:candidate state|joint constraint|the answer is|target value|challenge cell)\b",
    }
    pattern_hits = {name: len(re.findall(pattern, text, re.I)) for name, pattern in compact_patterns.items()}
    if any(pattern_hits.values()):
        failures.append({"check": "compact_or_meta_language", "observed": pattern_hits})

    normalized_sentences = [
        re.sub(r"\s+", " ", sentence.strip())
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if len(sentence.split()) >= 8
    ]
    repeated_sentences = sorted(
        ({"count": count, "sentence": sentence} for sentence, count in Counter(normalized_sentences).items() if count >= 2),
        key=lambda row: (-row["count"], row["sentence"]),
    )
    if any(row["count"] >= 3 for row in repeated_sentences):
        failures.append({"check": "template_repetition", "observed": repeated_sentences[:10]})

    segment_by_id = {s["segment_id"]: s for s in evidence["segments"]}
    span_errors = 0
    for segment in evidence["segments"]:
        if text[segment["start"]:segment["end"]] != segment["text"]:
            span_errors += 1
    evidence_by_cell = {cell["cell_id"]: cell for cell in evidence["cells"]}
    missing_evidence = []
    for cid in private["scored_cell_ids"]:
        cell = evidence_by_cell.get(cid)
        if not cell or not cell["evidence"]:
            missing_evidence.append(cid)
    if span_errors:
        failures.append({"check": "evidence_spans", "errors": span_errors})
    if missing_evidence:
        failures.append({"check": "missing_cell_evidence", "count": len(missing_evidence), "examples": missing_evidence[:10]})

    blank_violations = 0
    for table in public["tables"]:
        key = {
            "Match Summary": "Field", "Innings Summary": "Field", "Batting": "Batter",
            "Bowling": "Bowler", "Partnerships": "Partnership", "Fall of Wickets": "Wkt",
        }[table["table_type"]]
        for row in table["rows"]:
            for column in table["columns"]:
                if column != key and row[column] is not None:
                    blank_violations += 1
    if blank_violations:
        failures.append({"check": "nonblank_public_targets", "count": blank_violations})

    revision_delays = [
        int(row["correction_segment"][1:]) - int(row["provisional_segment"][1:])
        for row in evidence["revision_records"]
    ]
    profile_name = evidence.get("difficulty_profile", "r6_broadcast")
    expected_revisions = 24 if profile_name == "r7_live_blog" else 12
    minimum_revision_delay = 18 if profile_name == "r7_live_blog" else 8
    review_delays = [
        int(row["review_segment"][1:]) - int(row["provisional_segment"][1:])
        for row in evidence["revision_records"] if row.get("review_segment")
    ]
    stale_delays = [
        int(row["stale_segment"][1:]) - int(row["correction_segment"][1:])
        for row in evidence["revision_records"] if row.get("stale_segment")
    ]
    if len(evidence["revision_records"]) != expected_revisions or min(revision_delays) < minimum_revision_delay:
        failures.append({"check": "revision_depth", "count": len(revision_delays), "min_delay": min(revision_delays, default=0)})
    if profile_name == "r7_live_blog":
        if len(review_delays) != expected_revisions or min(review_delays, default=0) < 8:
            failures.append({"check": "pending_review_depth", "count": len(review_delays), "min_delay": min(review_delays, default=0)})
        if len(evidence["replay_event_ids"]) < 170:
            failures.append({"check": "replay_density", "count": len(evidence["replay_event_ids"])})
        if len(stale_delays) != expected_revisions // 2 or min(stale_delays, default=0) < 6:
            failures.append({"check": "post_correction_stale_depth", "count": len(stale_delays), "min_delay": min(stale_delays, default=0)})

    oracle = score_ledger(root, ledger)
    trust_provisional = score_ledger(root, corrupt_provisional(ledger, evidence["revision_records"]))
    count_replays = score_ledger(root, duplicate_replays(ledger, set(evidence["replay_event_ids"])))
    combined_ledger = duplicate_replays(
        corrupt_provisional(ledger, evidence["revision_records"]),
        set(evidence["replay_event_ids"]),
    )
    combined = score_ledger(root, combined_ledger)
    if oracle["wrong"]:
        failures.append({"check": "oracle_score", "observed": oracle})
    if profile_name == "r7_live_blog" and combined["error_rate"] < 0.60:
        failures.append({"check": "controlled_hardness_gate", "minimum": 0.60, "observed": combined["error_rate"]})

    decision = (
        "REVISE_SINGLE_ROOT"
        if failures
        else (
            "ADMIT_SECOND_ROOT_FOR_THREE_ROOT_PILOT"
            if profile_name == "r7_live_blog"
            else "ADVANCE_TO_TWO_ADDITIONAL_ROOTS"
        )
    )
    report = {
        "experiment": "R6_SINGLE_ROOT_EVENT_LEVEL",
        "status": "PASS" if not failures else "FAIL",
        "decision": decision,
        "root_id": root["root_id"],
        "difficulty_profile": profile_name,
        "public_words": len(text.split()),
        "segments": len(evidence["segments"]),
        "atomic_events": sum(len(x["events"]) for x in ledger["innings"]),
        "scored_cells": len(private["scored_cell_ids"]),
        "challenge_cells": len(private["challenge_cell_ids"]),
        "challenge_density": len(private["challenge_cell_ids"]) / len(private["scored_cell_ids"]),
        "revisions": len(evidence["revision_records"]),
        "stale_graphics": sum(bool(x["stale_segment"]) for x in evidence["revision_records"]),
        "same_delivery_replays": len(evidence["replay_event_ids"]),
        "revision_delay_segments": {"min": min(revision_delays), "max": max(revision_delays)},
        "review_delay_segments": (
            {"min": min(review_delays), "max": max(review_delays)} if review_delays else None
        ),
        "post_correction_stale_delay_segments": (
            {"min": min(stale_delays), "max": max(stale_delays)} if stale_delays else None
        ),
        "mechanical_checks": {
            "ledger_round_trip_checks": validation["checks"],
            "ledger_round_trip_failures": validation["failure_count"],
            "public_private_key_leaks": len(leaked),
            "blank_target_violations": blank_violations,
            "compact_or_meta_hits": pattern_hits,
            "exact_repeated_sentences_ge8_words": repeated_sentences,
            "evidence_span_errors": span_errors,
            "missing_scored_cell_evidence": len(missing_evidence),
        },
        "controlled_ledger_ablations": {
            "event_oracle": oracle,
            "trust_provisional_graphics": trust_provisional,
            "count_same_delivery_replays_as_new": count_replays,
            "combined_provisional_and_replay_failure": combined,
        },
        "failures": failures,
        "limitations": [
            "Controlled ledger ablations are not Direct, CoT, T3 or Map&Make model evaluations.",
            "The delivery order is constrained synthetic data derived from a curated scorecard, not an observed ball-by-ball feed.",
            "Naturalness and unique full-table recovery still require independent human review.",
            (
                "Two distinct roots are now admitted; one more distinct root is required before blinded model evaluation."
                if profile_name == "r7_live_blog"
                else "Only one root is included; advancement permits two more roots, not corpus-scale expansion."
            ),
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "decision": report["decision"],
        "oracle": oracle, "trust_provisional": trust_provisional,
        "count_replays": count_replays, "combined": combined,
    }, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
