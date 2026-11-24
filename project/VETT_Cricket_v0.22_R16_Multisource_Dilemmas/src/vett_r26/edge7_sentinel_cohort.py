from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .evaluation import score_predictions
from .protocol_analysis import materialize_semantic_predictions


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        instance_id = str(row["instance_id"])
        if instance_id in result:
            raise ValueError(f"duplicate semantic row: {instance_id}")
        result[instance_id] = row
    return result


def build_edge7_sentinel_cohort(
    release_dir: Path,
    parent_run: Path,
    continuation_run: Path,
    original_preflight_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Merge one valid Edge7 response per match; never repair invalid responses."""
    expected_ids = [
        "match_0021",
        "match_0066",
        "match_0067",
        "match_0162",
        "match_0220",
    ]
    preflight = _read(original_preflight_path)
    expected_hashes = {
        str(item["match_id"]): str(item["request_sha256"])
        for item in preflight["per_match"]
    }
    run_dirs = [parent_run, continuation_run]
    combined_rows: dict[str, dict[str, Any]] = {}
    successful_checkpoints: dict[str, dict[str, Any]] = {}
    attempt_events: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    total_cost = 0.0

    for run_dir in run_dirs:
        metadata = _read(run_dir / "RUN_METADATA.json")
        protocol = materialize_semantic_predictions(release_dir, run_dir)
        semantic_rows = _rows(Path(str(protocol["prediction_path"])))
        total_cost += float(metadata.get("actual_cost_cny") or 0.0)
        metadata_rows.append({
            "run_id": metadata.get("run_id"),
            "model": metadata.get("model"),
            "unknown_evidence_protocol": metadata.get(
                "r26_unknown_evidence_protocol"
            ),
            "protocol_status": protocol.get("status"),
            "actual_cost_cny": metadata.get("actual_cost_cny"),
            "metadata_sha256": _sha256(run_dir / "RUN_METADATA.json"),
        })
        for record in metadata.get("records", []):
            instance_id = str(record["instance_id"])
            for batch in record.get("batches", []):
                event = {
                    "run_id": metadata.get("run_id"),
                    "instance_id": instance_id,
                    "status": batch.get("status"),
                    "attempts": batch.get("attempts"),
                    "actual_cost_cny": batch.get("actual_cost_cny", 0.0),
                    "returned_targets": batch.get("returned_targets", 0),
                    "finish_reason": batch.get("finish_reason"),
                    "output_truncated": batch.get("output_truncated"),
                    "validation_errors": batch.get("validation_errors", []),
                    "error": batch.get("error"),
                }
                attempt_events.append(event)
                if batch.get("status") == "OK":
                    checkpoint_path = (
                        run_dir
                        / "checkpoints"
                        / instance_id
                        / f"batch_{int(batch['batch_index']):03d}.json"
                    )
                    checkpoint = _read(checkpoint_path)
                    if instance_id in successful_checkpoints:
                        raise ValueError(
                            f"more than one successful response for {instance_id}"
                        )
                    successful_checkpoints[instance_id] = checkpoint
        for instance_id, row in semantic_rows.items():
            if instance_id in combined_rows:
                raise ValueError(f"duplicate scoreable instance: {instance_id}")
            combined_rows[instance_id] = row

    model_values = {str(item["model"]) for item in metadata_rows}
    unknown_protocols = {
        str(item["unknown_evidence_protocol"]) for item in metadata_rows
    }
    request_hash_match = {
        instance_id: (
            instance_id in successful_checkpoints
            and successful_checkpoints[instance_id].get("request_sha256")
            == expected_hashes.get(instance_id)
        )
        for instance_id in combined_rows
    }
    errors: list[str] = []
    if model_values != {"zai-org/GLM-5.3-Flash"}:
        errors.append(f"model_mismatch:{sorted(model_values)}")
    if unknown_protocols != {"semantic_false_positive_v2"}:
        errors.append(f"unknown_protocol_mismatch:{sorted(unknown_protocols)}")
    if not set(combined_rows) <= set(expected_ids):
        errors.append("unexpected_scoreable_instance")
    if not all(request_hash_match.values()):
        errors.append("successful_request_hash_mismatch")

    output_dir.mkdir(parents=True, exist_ok=True)
    combined_path = output_dir / "COHORT_PREDICTIONS.jsonl"
    combined_path.write_text(
        "".join(
            json.dumps(combined_rows[key], ensure_ascii=False, sort_keys=True) + "\n"
            for key in expected_ids
            if key in combined_rows
        ),
        encoding="utf-8",
    )
    scoreable_ids = [key for key in expected_ids if key in combined_rows]
    missing_ids = [key for key in expected_ids if key not in combined_rows]
    scores = (
        score_predictions(
            release_dir, combined_path, instance_ids=scoreable_ids
        )
        if scoreable_ids
        else None
    )
    unresolved_failures = [
        event
        for event in attempt_events
        if event["status"] != "OK" and event["instance_id"] in missing_ids
    ]
    attempted_ids = [
        key
        for key in expected_ids
        if any(event["instance_id"] == key for event in attempt_events)
    ]
    request_attempts = sum(int(event.get("attempts") or 0) for event in attempt_events)
    billable_responses = sum(
        1 for event in attempt_events if float(event.get("actual_cost_cny") or 0.0) > 0
    )
    scoreable_questions = int(scores.get("questions", 0)) if scores else 0
    planned_questions = len(expected_ids) * 5
    official_complete = len(scoreable_ids) == len(expected_ids)
    subset_screen: dict[str, Any] | None = None
    if scores is not None:
        level_values = [
            float(scores["decision_field_accuracy_by_level"][level])
            for level in ("L1", "L2", "L3", "L4", "L5")
        ]
        adjacent_drops = [
            round(level_values[index] - level_values[index + 1], 6)
            for index in range(4)
        ]
        primary = float(scores["decision_field_macro_accuracy"])
        positive_drops = sum(drop > 0 for drop in adjacent_drops)
        mean_drop = round(sum(adjacent_drops) / len(adjacent_drops), 6)
        subset_screen = {
            "scope": "PROTOCOL_COMPLETE_4_OF_5_SUBSET_ONLY",
            "frozen_primary_metric": "decision_field_level_macro_accuracy",
            "primary_value": round(primary, 6),
            "target_interval": [0.45, 0.65],
            "primary_in_target_interval": 0.45 <= primary <= 0.65,
            "accuracy_by_level": dict(scores["decision_field_accuracy_by_level"]),
            "adjacent_drops": dict(
                zip(("L1-L2", "L2-L3", "L3-L4", "L4-L5"), adjacent_drops)
            ),
            "positive_adjacent_drops": positive_drops,
            "minimum_positive_adjacent_drops": 3,
            "mean_adjacent_drop": mean_drop,
            "minimum_mean_adjacent_drop": 0.08,
            "directionality_screen_pass_on_subset": (
                positive_drops >= 3 and mean_drop >= 0.08
            ),
            "official_gate_eligible": official_complete,
            "official_gate_pass": bool(
                official_complete
                and 0.45 <= primary <= 0.65
                and positive_drops >= 3
                and mean_drop >= 0.08
            ),
            "interpretation": (
                "This is a descriptive application of the frozen Sentinel5 screen "
                "to the four protocol-complete matches. It is not an official gate "
                "result because one planned match is protocol-invalid."
            ),
        }
    status = (
        "INCOMPATIBLE_COHORT"
        if errors
        else "COMPLETE_SENTINEL5"
        if len(scoreable_ids) == len(expected_ids)
        else "INCOMPLETE_SENTINEL5_PROTOCOL_FAILURE"
    )
    report = {
        "protocol_version": "VETT-R26.16-EDGE7-SENTINEL5-COHORT-1",
        "status": status,
        "dataset_version": _read(release_dir / "RELEASE_SUMMARY.json").get(
            "dataset_version"
        ),
        "model": next(iter(model_values)) if len(model_values) == 1 else None,
        "expected_instance_ids": expected_ids,
        "scoreable_instance_ids": scoreable_ids,
        "missing_instance_ids": missing_ids,
        "planned_instances": len(expected_ids),
        "attempted_instance_ids": attempted_ids,
        "attempted_instances": len(attempted_ids),
        "scoreable_instances": len(scoreable_ids),
        "planned_questions": planned_questions,
        "scoreable_questions": scoreable_questions,
        "request_attempts": request_attempts,
        "billable_responses": billable_responses,
        "planned_semantic_coverage": round(
            len(scoreable_ids) / len(expected_ids), 6
        ),
        "planned_question_coverage": round(
            scoreable_questions / planned_questions, 6
        ),
        "official_sentinel5_complete": official_complete,
        "paper_difficulty_claim_authorized": False,
        "errors": errors,
        "successful_request_hash_match": request_hash_match,
        "run_sources": metadata_rows,
        "attempt_events": attempt_events,
        "unresolved_failures": unresolved_failures,
        "actual_cost_cny": round(total_cost, 6),
        "scores": scores,
        "subset_screen_diagnostic": subset_screen,
        "prediction_path": str(combined_path),
        "claim_boundary": (
            "Scores describe only protocol-complete matches. The unresolved invalid "
            "match remains a protocol failure and is neither repaired nor converted "
            "to a semantic zero. An incomplete cohort cannot pass the frozen "
            "Sentinel5 difficulty gate or authorize dataset changes."
        ),
    }
    (output_dir / "COHORT_ANALYSIS.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if scores is None:
        metric_lines = "- Subset scores: unavailable\n"
    else:
        metric_lines = (
            f"- Factual record macro: {scores['factual_record_macro_accuracy']:.2%}\n"
            f"- Decision-field accuracy: {scores['decision_field_macro_accuracy']:.2%}\n"
            f"- Positive span F1: {scores['minimal_evidence_f1']:.2%}\n"
            f"- Rejected span F1: {scores['rejected_evidence_f1']:.2%}\n"
            f"- Typed-edge F1: {scores['minimal_evidence_edge_f1']:.2%}\n"
            f"- Content-dependency edge F1: {scores['content_dependency_edge_f1']:.2%}\n"
            f"- Factual plus complete-chain exact: {scores['factual_evidence_chain_joint_exact']:.2%}\n"
            f"- Frozen-primary target interval met on subset: "
            f"{'yes' if subset_screen and subset_screen['primary_in_target_interval'] else 'no'}\n"
            f"- Directionality screen met on subset: "
            f"{'yes' if subset_screen and subset_screen['directionality_screen_pass_on_subset'] else 'no'}\n"
        )
    (output_dir / "COHORT_ANALYSIS.md").write_text(
        "# R26.16 Edge7 Sentinel5 cohort\n\n"
        f"- Status: `{status}`\n"
        f"- Attempted: {len(attempted_ids)}/{len(expected_ids)} unique matches\n"
        f"- Scoreable coverage: {len(scoreable_ids)}/{len(expected_ids)} matches; "
        f"{scoreable_questions}/{planned_questions} questions\n"
        f"- Provider request attempts: {request_attempts}; billable responses: {billable_responses}\n"
        f"- Scoreable: {', '.join(scoreable_ids)}\n"
        f"- Missing/invalid: {', '.join(missing_ids) or 'none'}\n"
        f"- Recorded cost: CNY {report['actual_cost_cny']}\n"
        f"- Complete Sentinel5 conclusion permitted: {'yes' if official_complete else 'no'}\n\n"
        "## Protocol-complete subset diagnostics\n\n"
        + metric_lines
        + "\nDecision-field accuracy scores the frozen 12 individual output fields; "
        "factual-record macro requires the complete record to be correct. They are "
        "different estimands and must not be substituted for one another.\n\n"
        "The invalid match is retained as a protocol failure and is not scored as a "
        "factual zero. This incomplete cohort cannot validate the five-level gap target "
        "or authorize a paper-level difficulty claim.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-edge7-sentinel-cohort")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--parent-run", type=Path, required=True)
    parser.add_argument("--continuation-run", type=Path, required=True)
    parser.add_argument("--original-preflight", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_edge7_sentinel_cohort(
        args.release,
        args.parent_run,
        args.continuation_run,
        args.original_preflight,
        args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_edge7_sentinel_cohort"]
