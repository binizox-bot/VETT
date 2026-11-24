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


def corrupt_split_classification_only(
    ledger: dict[str, Any], revisions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Keep the certified class/legal status but retain the provisional numeral."""
    result = copy.deepcopy(ledger)
    events = {event["event_id"]: event for innings in result["innings"] for event in innings["events"]}
    for revision in revisions:
        event = events[revision["event_id"]]
        alternate = revision["alternate_value"]
        if event["extras_type"]:
            event["extras_runs"] = alternate
        else:
            event["batter_runs"] = alternate
            event["boundary_four"] = alternate == 4
            event["boundary_six"] = alternate in (6, 8)
    recompute_state(result)
    return result


def corrupt_split_magnitude_only(
    ledger: dict[str, Any], revisions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Keep the accepted numeral but retain the provisional semantic class."""
    result = copy.deepcopy(ledger)
    events = {event["event_id"]: event for innings in result["innings"] for event in innings["events"]}
    for revision in revisions:
        event = events[revision["event_id"]]
        alternate = revision["alternate_event"]
        correct_value = revision["correct_value"]
        event["is_legal"] = alternate["is_legal"]
        event["extras_type"] = alternate["extras_type"]
        if event["extras_type"]:
            event["batter_runs"] = 0
            event["extras_runs"] = correct_value
            event["boundary_four"] = False
            event["boundary_six"] = False
        else:
            event["batter_runs"] = correct_value
            event["extras_runs"] = 0
            event["boundary_four"] = correct_value == 4
            event["boundary_six"] = correct_value in (6, 8)
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


def duplicate_mentions_with_multiplicity(
    ledger: dict[str, Any], multiplicity: Counter[str]
) -> dict[str, Any]:
    """Duplicate events once per independently miscounted surface summary."""
    result = copy.deepcopy(ledger)
    for innings in result["innings"]:
        expanded = []
        for event in innings["events"]:
            expanded.append(event)
            for index in range(multiplicity[event["event_id"]]):
                duplicate = copy.deepcopy(event)
                duplicate["event_id"] = event["event_id"] + f".MENTION_{index+1}_COUNTED"
                expanded.append(duplicate)
        innings["events"] = expanded
    recompute_state(result)
    return result


def alias_cross_innings_delivery_labels(ledger: dict[str, Any]) -> dict[str, Any]:
    """Model a method that drops innings scope from repeated delivery labels.

    The second innings keeps its local participants, legal-ball skeleton and
    wicket positions but inherits scoring payloads from the first occurrence of
    the same 0.1/0.2-style label. Existing wicket mechanism/owner payloads are
    also collapsed to the local bowler. This preserves a fixed evaluation
    universe while modelling a state-key failure. It is not a model prediction
    and not a claim about any named method.
    """
    result = copy.deepcopy(ledger)
    if len(result["innings"]) < 2:
        return result
    source_by_label: dict[str, list[dict[str, Any]]] = {}
    for event in result["innings"][0]["events"]:
        label = event["delivery_label"].split("x", 1)[0]
        source_by_label.setdefault(label, []).append(event)
    seen: Counter[str] = Counter()
    for event in result["innings"][1]["events"]:
        label = event["delivery_label"].split("x", 1)[0]
        if label not in source_by_label:
            continue
        source_events = source_by_label[label]
        source = source_events[min(seen[label], len(source_events) - 1)]
        seen[label] += 1
        for field in (
            "batter_runs", "boundary_four", "boundary_six",
            "extras_type", "extras_runs",
        ):
            event[field] = source[field]
        if event["dismissal"]:
            event["dismissal"]["description"] = f"b {event['bowler']}"
            event["dismissal"]["credited_bowler"] = event["bowler"]
    recompute_state(result)
    return result


def mislink_relational_magnitudes(
    ledger: dict[str, Any], revisions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Rotate relational magnitudes within each innings while preserving event class."""
    result = copy.deepcopy(ledger)
    primary = {
        event["event_id"]: event for innings in result["innings"] for event in innings["events"]
        if ".MENTION_" not in event["event_id"] and ".REPLAY_COUNTED" not in event["event_id"]
    }
    by_innings: dict[str, list[dict[str, Any]]] = {}
    for record in revisions:
        if record.get("magnitude_mode") == "relation_to_provisional":
            by_innings.setdefault(record["event_id"].split(".", 1)[0], []).append(record)
    for records in by_innings.values():
        values = [record["correct_value"] for record in records]
        rotated = values[1:] + values[:1]
        for record, value in zip(records, rotated):
            event = primary.get(record["event_id"])
            if event is None:
                continue
            if event["extras_type"]:
                event["extras_runs"] = value
            else:
                event["batter_runs"] = value
                event["boundary_four"] = value == 4
                event["boundary_six"] = value in (6, 8)
    recompute_state(result)
    return result


def collapse_checkpoint_boundaries(
    ledger: dict[str, Any], checkpoint_groups: list[dict[str, Any]]
) -> dict[str, Any]:
    """Collapse each interval summary onto its endpoint delivery label."""
    result = copy.deepcopy(ledger)
    group_by_event = {
        event_id: group for group in checkpoint_groups for event_id in group["event_ids"]
    }
    for innings in result["innings"]:
        for event in innings["events"]:
            base_id = event["event_id"].split(".MENTION_", 1)[0].split(".REPLAY_COUNTED", 1)[0]
            if base_id in group_by_event:
                event["delivery_label"] = f"{group_by_event[base_id]['over_range'][1]}.6"
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
    expected_revisions = {
        "r6_broadcast": 12,
        "r7_live_blog": 24,
        "r8_radio_nonperiodic": 60,
        "r9_split_authority": 60,
        "r10_implicit_fourth_root": 60,
    }[profile_name]
    minimum_revision_delay = {
        "r6_broadcast": 8,
        "r7_live_blog": 18,
        "r8_radio_nonperiodic": 24,
        "r9_split_authority": 40,
        "r10_implicit_fourth_root": 40,
    }[profile_name]
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
    if profile_name in ("r7_live_blog", "r8_radio_nonperiodic", "r9_split_authority", "r10_implicit_fourth_root"):
        minimum_review_delay = 9 if profile_name in ("r8_radio_nonperiodic", "r9_split_authority", "r10_implicit_fourth_root") else 8
        if len(review_delays) != expected_revisions or min(review_delays, default=0) < minimum_review_delay:
            failures.append({"check": "pending_review_depth", "count": len(review_delays), "min_delay": min(review_delays, default=0)})
        minimum_replays = {
            "r7_live_blog": 170,
            "r8_radio_nonperiodic": 165,
            "r9_split_authority": 75,
            "r10_implicit_fourth_root": 140,
        }[profile_name]
        if len(evidence["replay_event_ids"]) < minimum_replays:
            failures.append({"check": "replay_density", "count": len(evidence["replay_event_ids"])})
        minimum_stale = 35 if profile_name in ("r8_radio_nonperiodic", "r9_split_authority", "r10_implicit_fourth_root") else expected_revisions // 2
        minimum_stale_delay = 9 if profile_name in ("r8_radio_nonperiodic", "r9_split_authority", "r10_implicit_fourth_root") else 6
        if len(stale_delays) < minimum_stale or min(stale_delays, default=0) < minimum_stale_delay:
            failures.append({"check": "post_correction_stale_depth", "count": len(stale_delays), "min_delay": min(stale_delays, default=0)})

    replay_gap_summary = None
    if profile_name in ("r8_radio_nonperiodic", "r9_split_authority", "r10_implicit_fourth_root"):
        flattened = [event["event_id"] for innings in ledger["innings"] for event in innings["events"]]
        positions = [pos for pos, event_id in enumerate(flattened) if event_id in set(evidence["replay_event_ids"])]
        gaps = [right - left for left, right in zip(positions, positions[1:])]
        counts = Counter(gaps)
        replay_gap_summary = {
            "distinct_gaps": len(counts),
            "most_common_gap": counts.most_common(1)[0][0] if counts else None,
            "most_common_share": counts.most_common(1)[0][1] / len(gaps) if gaps else 1.0,
            "gap_counts": {str(k): v for k, v in sorted(counts.items())},
        }
        # A truly periodic selector collapses to one dominant gap.  Dense
        # nonperiodic selection necessarily creates many adjacent pairs, so the
        # gate rejects dominance rather than requiring an arbitrary low gap-1 rate.
        if replay_gap_summary["distinct_gaps"] < 2 or replay_gap_summary["most_common_share"] >= 0.95:
            failures.append({"check": "nonperiodic_replay_pattern", "observed": replay_gap_summary})

    oracle = score_ledger(root, ledger)
    trust_provisional = score_ledger(root, corrupt_provisional(ledger, evidence["revision_records"]))
    count_replays = score_ledger(root, duplicate_replays(ledger, set(evidence["replay_event_ids"])))
    combined_ledger = duplicate_replays(
        corrupt_provisional(ledger, evidence["revision_records"]),
        set(evidence["replay_event_ids"]),
    )
    combined = score_ledger(root, combined_ledger)
    split_classification_only = score_ledger(
        root, corrupt_split_classification_only(ledger, evidence["revision_records"])
    )
    split_magnitude_only = score_ledger(
        root, corrupt_split_magnitude_only(ledger, evidence["revision_records"])
    )
    checkpoint_ids = {
        event_id for group in evidence.get("checkpoint_event_groups", [])
        for event_id in group["event_ids"]
    }
    count_interval_checkpoints = score_ledger(
        root, duplicate_replays(ledger, checkpoint_ids)
    )
    cross_innings_alias = score_ledger(root, alias_cross_innings_delivery_labels(ledger))
    triple_combined = score_ledger(
        root, alias_cross_innings_delivery_labels(combined_ledger)
    )
    mention_multiplicity: Counter[str] = Counter(evidence["replay_event_ids"])
    for group in evidence.get("checkpoint_event_groups", []):
        mention_multiplicity.update(group["event_ids"])
    four_mechanism_ledger = duplicate_mentions_with_multiplicity(
        corrupt_provisional(ledger, evidence["revision_records"]), mention_multiplicity
    )
    four_mechanism_combined = score_ledger(
        root, alias_cross_innings_delivery_labels(four_mechanism_ledger)
    )
    mislink_implicit_magnitudes = score_ledger(
        root, mislink_relational_magnitudes(ledger, evidence["revision_records"])
    )
    collapse_interval_boundaries = score_ledger(
        root, collapse_checkpoint_boundaries(ledger, evidence.get("checkpoint_event_groups", []))
    )
    six_mechanism_ledger = collapse_checkpoint_boundaries(
        mislink_relational_magnitudes(
            alias_cross_innings_delivery_labels(four_mechanism_ledger),
            evidence["revision_records"],
        ),
        evidence.get("checkpoint_event_groups", []),
    )
    six_mechanism_combined = score_ledger(root, six_mechanism_ledger)
    if oracle["wrong"]:
        failures.append({"check": "oracle_score", "observed": oracle})
    hardness_minimum = {
        "r7_live_blog": 0.60,
        "r8_radio_nonperiodic": 0.65,
        "r9_split_authority": 0.62,
        "r10_implicit_fourth_root": 0.63,
    }.get(profile_name)
    hardness_observed = (
        six_mechanism_combined["error_rate"]
        if profile_name == "r10_implicit_fourth_root"
        else (
            triple_combined["error_rate"]
            if profile_name in ("r8_radio_nonperiodic", "r9_split_authority")
            else combined["error_rate"]
        )
    )
    if hardness_minimum is not None and hardness_observed < hardness_minimum:
        failures.append({"check": "controlled_hardness_gate", "minimum": hardness_minimum, "observed": hardness_observed})

    r8_curation = root.get("r8_partnership_ball_curation")
    if profile_name in ("r8_radio_nonperiodic", "r9_split_authority"):
        if (
            root.get("curation_status") != "NEEDS_SUPPORT_ANNOTATION"
            or not r8_curation
            or not r8_curation.get("human_support_review_required")
            or len(r8_curation.get("changes", [])) != 4
        ):
            failures.append({"check": "r8_curation_disclosure", "observed": r8_curation})

    r10_link_audit = evidence.get("implicit_link_audit", [])
    relational_records = [
        record for record in evidence["revision_records"]
        if record.get("magnitude_mode") == "relation_to_provisional"
    ]
    relational_evidence_missing = 0
    if profile_name == "r10_implicit_fourth_root":
        if (
            root.get("curation_status") != "READY_FOR_GENERATED_VIEWS"
            or len(root.get("r6_curation", {}).get("removed_rows", [])) != 4
            or root.get("validation", {}).get("source_audit_action") != "AUTO_PASS_NEEDS_SUPPORT_AUDIT"
        ):
            failures.append({"check": "r10_root_curation_disclosure", "observed": root.get("validation")})
        implicit_links = [row for row in r10_link_audit if row["link_mode"] == "implicit_state_signature"]
        marker_fallbacks = [row for row in r10_link_audit if row["link_mode"] == "delivery_marker_fallback"]
        if len(implicit_links) < 50 or any(row["active_candidate_count"] != 1 for row in implicit_links) or len(marker_fallbacks) > 10:
            failures.append({"check": "implicit_link_uniqueness", "implicit": len(implicit_links), "fallbacks": len(marker_fallbacks)})
        if len(relational_records) < 40 or len(evidence.get("checkpoint_event_groups", [])) != 6:
            failures.append({"check": "r10_dependency_density", "relational": len(relational_records), "checkpoints": len(evidence.get("checkpoint_event_groups", []))})
        if re.search(r"production cue|scoring reference\s+\d+", text, re.I):
            failures.append({"check": "explicit_numeric_cue_remaining"})
        evidence_by_cell_local = {cell["cell_id"]: cell for cell in evidence["cells"]}
        relational_by_event = {record["event_id"]: record for record in relational_records}
        for cell in evidence["cells"]:
            refs = {ref["segment_id"] for ref in cell["evidence"]}
            for event_id in cell["event_ids"]:
                if event_id in relational_by_event:
                    record = relational_by_event[event_id]
                    required = {
                        record["provisional_segment"], record["classification_segment"],
                        record["magnitude_segment"],
                    }
                    if not required.issubset(refs):
                        relational_evidence_missing += 1

    decision = (
        "REVISE_SINGLE_ROOT"
        if failures
        else (
            "ADMIT_FOURTH_ROOT_PENDING_SOURCE_SUPPORT_AUDIT"
            if profile_name == "r10_implicit_fourth_root"
            else (
                "ADMIT_R9_STRESS_VARIANT_PENDING_HUMAN_SUPPORT_REVIEW"
                if profile_name == "r9_split_authority"
                else (
                    "ADMIT_THIRD_ROOT_PENDING_HUMAN_SUPPORT_REVIEW"
                    if profile_name == "r8_radio_nonperiodic"
                    else (
                        "ADMIT_SECOND_ROOT_FOR_THREE_ROOT_PILOT"
                        if profile_name == "r7_live_blog"
                        else "ADVANCE_TO_TWO_ADDITIONAL_ROOTS"
                    )
                )
            )
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
        "interval_conservation_checkpoints": len(evidence.get("checkpoint_event_groups", [])),
        "implicit_state_links": sum(row.get("link_mode") == "implicit_state_signature" for row in r10_link_audit),
        "delivery_marker_fallbacks": sum(row.get("link_mode") == "delivery_marker_fallback" for row in r10_link_audit),
        "relational_magnitude_chains": len(relational_records),
        "replay_gap_summary": replay_gap_summary,
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
            "relational_cells_missing_three_part_evidence": relational_evidence_missing,
        },
        "controlled_ledger_ablations": {
            "event_oracle": oracle,
            "trust_provisional_graphics": trust_provisional,
            "count_same_delivery_replays_as_new": count_replays,
            "combined_provisional_and_replay_failure": combined,
            "split_authority_classification_only": split_classification_only,
            "split_authority_magnitude_only": split_magnitude_only,
            "count_interval_checkpoints_as_new": count_interval_checkpoints,
            "cross_innings_delivery_label_alias": cross_innings_alias,
            "combined_revision_replay_and_cross_innings_alias_failure": triple_combined,
            "combined_revision_replay_scope_and_checkpoint_failure": four_mechanism_combined,
            "mislink_implicit_relational_magnitudes": mislink_implicit_magnitudes,
            "collapse_interval_checkpoints_to_endpoint": collapse_interval_boundaries,
            "combined_all_six_state_failures": six_mechanism_combined,
        },
        "failures": failures,
        "root_curation": {
            "status": root.get("curation_status"),
            "r8_changed_cells": (r8_curation or {}).get("changed_cells", 0),
            "human_support_review_required": (r8_curation or {}).get("human_support_review_required", False),
        },
        "limitations": [
            "Controlled ledger ablations are not Direct, CoT, T3 or Map&Make model evaluations.",
            "The delivery order is constrained synthetic data derived from a curated scorecard, not an observed ball-by-ball feed.",
            "Naturalness and unique full-table recovery still require independent human review.",
            (
                "The fourth root passes mechanical gates but its source remains flagged for support audit before freezing."
                if profile_name == "r10_implicit_fourth_root"
                else (
                    "The R9 stress variant shares the third root and still requires human support review of its four minimal partnership-ball repairs before freezing."
                    if profile_name == "r9_split_authority"
                    else (
                        "The third root passes mechanical gates but its four minimal partnership-ball repairs require human support review before freezing."
                        if profile_name == "r8_radio_nonperiodic"
                        else (
                            "Two distinct roots are now admitted; one more distinct root is required before blinded model evaluation."
                            if profile_name == "r7_live_blog"
                            else "Only one root is included; advancement permits two more roots, not corpus-scale expansion."
                        )
                    )
                )
            ),
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "decision": report["decision"],
        "oracle": oracle, "trust_provisional": trust_provisional,
        "count_replays": count_replays, "combined": combined,
        "cross_innings_alias": cross_innings_alias,
        "triple_combined": triple_combined,
        "split_classification_only": split_classification_only,
        "split_magnitude_only": split_magnitude_only,
        "count_checkpoints": count_interval_checkpoints,
        "four_mechanism_combined": four_mechanism_combined,
        "mislink_magnitudes": mislink_implicit_magnitudes,
        "collapse_boundaries": collapse_interval_boundaries,
        "six_mechanism_combined": six_mechanism_combined,
    }, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
