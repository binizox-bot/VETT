from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from vett_r25.evaluation import score_predictions as score_factual_predictions

from .evaluation import score_predictions


FACTUAL_DIAGNOSTIC_KEYS = (
    "instances",
    "questions",
    "decision_field_macro_accuracy",
    "decision_field_accuracy_by_level",
    "level_macro_accuracy",
    "full_record_exact_match",
    "full_record_exact_by_level",
    "full_record_exact_counts_by_level",
    "adjacent_level_exact_gaps",
    "adjacent_level_gap_target",
    "adjacent_level_gap_pass",
    "factual_record_macro_accuracy",
    "latent_state_accuracy",
    "counterfactual_field_accuracy",
    "counterfactual_full_record_exact_match",
    "counterfactual_state_accuracy",
    "paired_factual_counterfactual_exact",
    "confidence_brier_score",
)


def _evidence_only_validation_errors(errors: list[str]) -> bool:
    """True only when invalidity is confined to R26 evidence fields.

    This intentionally uses a small allowlist. Unknown error messages never qualify
    for factual diagnostics, so a future validator cannot silently weaken the gate.
    """
    markers = (
        "evidence span",
        "rejected evidence",
        "evidence edge",
    )
    return bool(errors) and all(any(marker in error for marker in markers) for error in errors)


def _factual_diagnostic_safe(
    batch: dict[str, Any], checkpoint: dict[str, Any]
) -> bool:
    errors = list(checkpoint.get("batch_record", {}).get("validation_errors", []))
    predictions = checkpoint.get("predictions", {})
    requested = int(batch.get("requested_targets", -1))
    returned = int(batch.get("returned_targets", -2))
    return (
        batch.get("status") in {"INVALID", "INVALID_OUTPUT"}
        and batch.get("output_truncated") is not True
        and batch.get("finish_reason") not in {"length", "max_tokens"}
        and not batch.get("parse_error")
        and requested >= 0
        and returned == requested
        and isinstance(predictions, dict)
        and len(predictions) == requested
        and _evidence_only_validation_errors(errors)
    )


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _failure_class(batch: dict[str, Any]) -> str:
    error = str(batch.get("error", "")).lower()
    if "http 402" in error or "balance is insufficient" in error:
        return "ACCOUNT_BALANCE"
    if "http 429" in error or "rate limit" in error:
        return "RATE_LIMIT"
    if "timeout" in error or "timed out" in error:
        return "TIMEOUT"
    if batch.get("output_truncated") is True or batch.get("finish_reason") in {
        "length",
        "max_tokens",
    }:
        return "OUTPUT_TRUNCATED"
    if batch.get("status") in {"INVALID", "INVALID_OUTPUT"}:
        return "SCHEMA_OR_PROTOCOL"
    if "ambiguousinflightrequest" in error:
        return "AMBIGUOUS_IN_FLIGHT"
    return "TRANSPORT_OR_PROVIDER"


def _output_conformance_summary(metadata: dict[str, Any]) -> dict[str, Any]:
    warnings: list[dict[str, Any]] = []
    attempted_questions = 0
    attempted_batches = 0
    failed_batches = 0
    strict_duplicate_errors: list[dict[str, Any]] = []
    affected_questions: set[tuple[str, str]] = set()
    by_field: dict[str, dict[str, int]] = {}
    for record in metadata.get("records", []):
        instance_id = str(record.get("instance_id"))
        for batch in record.get("batches", []):
            attempted_batches += 1
            attempted_questions += int(batch.get("requested_targets", 0))
            batch_warnings = [
                item
                for item in batch.get("conformance_warnings", [])
                if isinstance(item, dict)
                and item.get("warning_type")
                == "DUPLICATE_EVIDENCE_CANONICALIZED"
            ]
            for error in batch.get("validation_errors", []):
                if "repeats evidence" in str(error):
                    strict_duplicate_errors.append({
                        "instance_id": instance_id,
                        "batch_index": int(batch.get("batch_index", 0)),
                        "error": str(error),
                    })
            if batch_warnings:
                failed_batches += 1
            for item in batch_warnings:
                warning = {"instance_id": instance_id, **item}
                warnings.append(warning)
                affected_questions.add(
                    (instance_id, str(item.get("question_id")))
                )
                field = str(item.get("evidence_field"))
                counts = by_field.setdefault(
                    field,
                    {
                        "warning_events": 0,
                        "duplicate_groups": 0,
                        "redundant_count": 0,
                    },
                )
                counts["warning_events"] += 1
                counts["duplicate_groups"] += int(
                    item.get("duplicate_groups", 0)
                )
                counts["redundant_count"] += int(
                    item.get("redundant_count", 0)
                )
    affected_count = len(affected_questions)
    return {
        "protocol": metadata.get(
            "r26_evidence_set_protocol", "strict_unique_v1"
        ),
        "status": (
            "FAIL_HARD_STRICT" if strict_duplicate_errors
            else "FAIL_CANONICALIZED" if warnings
            else "PASS"
        ),
        "semantic_scoreability_affected": bool(strict_duplicate_errors),
        "attempted_batches": attempted_batches,
        "failed_conformance_batches": failed_batches,
        "attempted_questions": attempted_questions,
        "affected_questions": affected_count,
        "question_conformance_rate": (
            None
            if strict_duplicate_errors
            else round(1.0 - affected_count / attempted_questions, 6)
            if attempted_questions
            else 0.0
        ),
        "warning_events": len(warnings),
        "duplicate_groups": sum(
            int(item.get("duplicate_groups", 0)) for item in warnings
        ),
        "redundant_count": sum(
            int(item.get("redundant_count", 0)) for item in warnings
        ),
        "maximum_multiplicity": max(
            (int(item.get("maximum_multiplicity", 0)) for item in warnings),
            default=1,
        ),
        "by_field": dict(sorted(by_field.items())),
        "warnings": warnings,
        "strict_duplicate_errors": strict_duplicate_errors,
        "interpretation": (
            "Exact duplicates are removed before set-semantic scoring and receive no "
            "credit. Conformance remains a separately reported model output failure."
        ),
    }


def materialize_semantic_predictions(release_dir: Path, run_dir: Path) -> dict[str, Any]:
    """Separate semantically complete predictions from transport-contract validity."""
    metadata = json.loads((run_dir / "RUN_METADATA.json").read_text(encoding="utf-8"))
    public_rows: dict[str, dict[str, Any]] = {}
    for line in (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            public_rows[str(row["instance_id"])] = row

    output_rows: list[dict[str, Any]] = []
    factual_diagnostic_rows: list[dict[str, Any]] = []
    recoveries: list[dict[str, Any]] = []
    factual_diagnostic_recoveries: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    semantic_warnings: list[dict[str, Any]] = []
    scored_instance_ids: list[str] = []
    factual_diagnostic_instance_ids: list[str] = []
    for record in metadata.get("records", []):
        instance_id = str(record["instance_id"])
        row = public_rows.get(instance_id, {"instance_id": instance_id, "decision_predictions": []})
        predictions = {
            str(item["question_id"]): item
            for item in row.get("decision_predictions", [])
            if isinstance(item, dict) and isinstance(item.get("question_id"), str)
        }
        factual_diagnostic_predictions = dict(predictions)
        semantically_complete = True
        factually_complete = True
        for batch in record.get("batches", []):
            checkpoint_path = run_dir / "checkpoints" / instance_id / f"batch_{int(batch['batch_index']):03d}.json"
            if not checkpoint_path.is_file():
                rejected.append({
                    "instance_id": instance_id,
                    "batch_index": int(batch["batch_index"]),
                    "reason": "checkpoint_absent",
                    "failure_class": _failure_class(batch),
                    "error": str(batch.get("error", "")),
                })
                semantically_complete = False
                factually_complete = False
                continue
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint_predictions = checkpoint.get("predictions", {})
            checkpoint_record = checkpoint.get("batch_record", {})
            errors = list(checkpoint_record.get("validation_errors", []))
            complete = (
                isinstance(checkpoint_predictions, dict)
                and len(checkpoint_predictions) == int(batch.get("requested_targets", -1))
                and int(batch.get("returned_targets", -1))
                == int(batch.get("requested_targets", -2))
            )
            if batch.get("status") == "OK":
                if checkpoint_record.get("status") != "OK" or errors or not complete:
                    rejected.append({
                        "instance_id": instance_id,
                        "batch_index": int(batch["batch_index"]),
                        "reason": "ok_checkpoint_inconsistent",
                        "failure_class": "LOCAL_ARTIFACT_INTEGRITY",
                        "validation_errors": errors,
                    })
                    semantically_complete = False
                    factually_complete = False
                    continue
                for warning in checkpoint_record.get("semantic_warnings", []):
                    if isinstance(warning, dict):
                        semantic_warnings.append({
                            "instance_id": instance_id,
                            "batch_index": int(batch["batch_index"]),
                            **warning,
                        })
                for question_id, value in checkpoint_predictions.items():
                    normalized_item = {"question_id": str(question_id), **value}
                    predictions[str(question_id)] = normalized_item
                    factual_diagnostic_predictions[str(question_id)] = normalized_item
                continue
            allowed_error = errors == ["response instance_id mismatch"]
            if not allowed_error or not complete:
                rejected.append({
                    "instance_id": instance_id,
                    "batch_index": int(batch["batch_index"]),
                    "reason": "not_semantically_recoverable",
                    "failure_class": _failure_class(batch),
                    "validation_errors": errors,
                })
                semantically_complete = False
                if _factual_diagnostic_safe(batch, checkpoint):
                    for question_id, value in checkpoint_predictions.items():
                        factual_diagnostic_predictions[str(question_id)] = {
                            "question_id": str(question_id),
                            **value,
                        }
                    factual_diagnostic_recoveries.append({
                        "instance_id": instance_id,
                        "batch_index": int(batch["batch_index"]),
                        "factual_predictions": len(checkpoint_predictions),
                        "official_protocol_status_preserved": str(batch["status"]),
                        "validation_errors": errors,
                        "valid_for": "DIAGNOSTIC_FACTUAL_METRICS_ONLY",
                    })
                else:
                    factually_complete = False
                continue
            for question_id, value in checkpoint_predictions.items():
                predictions[str(question_id)] = {"question_id": str(question_id), **value}
                factual_diagnostic_predictions[str(question_id)] = {
                    "question_id": str(question_id),
                    **value,
                }
            recoveries.append({
                "instance_id": instance_id,
                "batch_index": int(batch["batch_index"]),
                "semantic_predictions": len(checkpoint_predictions),
                "protocol_status_preserved": str(batch["status"]),
                "validation_errors": errors,
            })
        expected_targets = int(
            record.get(
                "targets",
                sum(int(batch.get("requested_targets", 0)) for batch in record.get("batches", [])),
            )
        )
        if len(predictions) != expected_targets:
            rejected.append({
                "instance_id": instance_id,
                "reason": "materialized_prediction_count_mismatch",
                "failure_class": "LOCAL_ARTIFACT_INTEGRITY",
                "expected_targets": expected_targets,
                "materialized_targets": len(predictions),
            })
            semantically_complete = False
        if len(factual_diagnostic_predictions) != expected_targets:
            factually_complete = False
        if semantically_complete:
            output_rows.append({
                "instance_id": instance_id,
                "decision_predictions": [predictions[key] for key in sorted(predictions)],
            })
            scored_instance_ids.append(instance_id)
        if factually_complete:
            factual_diagnostic_rows.append({
                "instance_id": instance_id,
                "decision_predictions": [
                    factual_diagnostic_predictions[key]
                    for key in sorted(factual_diagnostic_predictions)
                ],
            })
            factual_diagnostic_instance_ids.append(instance_id)

    prediction_path = run_dir / "SEMANTIC_PREDICTIONS.jsonl"
    prediction_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in output_rows),
        encoding="utf-8",
    )
    factual_diagnostic_path = run_dir / "DIAGNOSTIC_FACTUAL_PREDICTIONS.jsonl"
    factual_diagnostic_path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            for row in factual_diagnostic_rows
        ),
        encoding="utf-8",
    )
    scores = (
        score_predictions(release_dir, prediction_path, instance_ids=scored_instance_ids)
        if scored_instance_ids else None
    )
    factual_diagnostic_scores = None
    if factual_diagnostic_instance_ids:
        raw_factual_scores = score_factual_predictions(
            release_dir,
            factual_diagnostic_path,
            instance_ids=factual_diagnostic_instance_ids,
        )
        factual_diagnostic_scores = {
            key: raw_factual_scores[key]
            for key in FACTUAL_DIAGNOSTIC_KEYS
        }
    requested_instances = len(metadata.get("records", []))
    report = {
        "status": (
            "NO_SCOREABLE_INSTANCES" if not scored_instance_ids
            else "PARTIAL_SEMANTIC_COVERAGE" if rejected
            else "SEMANTIC_RESCORE_WITH_PROTOCOL_FAILURES" if recoveries
            else "COMPLETE_SEMANTIC_COVERAGE"
        ),
        "protocol_failures_remain": len(recoveries) + len(rejected),
        "requested_instances": requested_instances,
        "scored_instances": len(scored_instance_ids),
        "scored_instance_ids": scored_instance_ids,
        "semantic_coverage": round(len(scored_instance_ids) / requested_instances, 6) if requested_instances else 0.0,
        "recoveries": recoveries,
        "rejected": rejected,
        "semantic_warning_count": len(semantic_warnings),
        "semantic_warnings": semantic_warnings,
        "output_conformance": _output_conformance_summary(metadata),
        "scores": scores,
        "prediction_path": str(prediction_path),
        "diagnostic_factual_scored_instances": len(factual_diagnostic_instance_ids),
        "diagnostic_factual_instance_ids": factual_diagnostic_instance_ids,
        "diagnostic_factual_coverage": (
            round(len(factual_diagnostic_instance_ids) / requested_instances, 6)
            if requested_instances else 0.0
        ),
        "diagnostic_factual_recoveries": factual_diagnostic_recoveries,
        "diagnostic_factual_scores": factual_diagnostic_scores,
        "diagnostic_factual_prediction_path": str(factual_diagnostic_path),
        "warning": (
            "Recovered semantic rows do not change runner protocol status or checkpoint validity. "
            "Diagnostic factual scores may reuse complete factual fields from an evidence-only "
            "protocol failure; they are non-official and must never be reported as benchmark scores."
        ),
    }
    _write(run_dir / "SEMANTIC_SCORES.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-protocol-analysis")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(materialize_semantic_predictions(args.release, args.run), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["materialize_semantic_predictions"]
