from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from vett_eval.runner import (
    _evidence_grounding_warnings,
    _evidence_relations_by_target,
    _load_public_instance,
    _normalize_response,
    _public_span_ids,
    _request_record,
    _request_sha256,
)

from .evaluation import score_predictions


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _prediction_row(
    instance_id: str, predictions: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    return {
        "instance_id": instance_id,
        "decision_predictions": [
            {"question_id": question_id, **predictions[question_id]}
            for question_id in sorted(predictions)
        ],
    }


def _write_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def replay_canonical_set(
    release_dir: Path,
    source_run_dir: Path,
    instance_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Replay a saved response under the prospective set protocol.

    This is deliberately post-hoc and can never change the source checkpoint's
    official status.  It proves whether exact-duplicate removal is semantically
    invariant and whether the proposed contract can score the already-paid output.
    """
    metadata = _read(source_run_dir / "RUN_METADATA.json")
    checkpoint_path = (
        source_run_dir / "checkpoints" / instance_id / "batch_000.json"
    )
    raw_path = source_run_dir / "raw" / instance_id / "batch_000.json"
    checkpoint = _read(checkpoint_path)
    raw = _read(raw_path)
    batch = checkpoint["batch_record"]
    validation_errors = list(batch.get("validation_errors", []))
    if batch.get("status") != "INVALID_OUTPUT":
        raise ValueError("source checkpoint must preserve INVALID_OUTPUT")
    if not validation_errors or not all(
        "repeats evidence" in str(error) for error in validation_errors
    ):
        raise ValueError(
            "replay is allowed only when every source validation error is an exact "
            "evidence-duplication failure"
        )
    if batch.get("output_truncated") is not False or batch.get("finish_reason") != "stop":
        raise ValueError("source response must be complete and non-truncated")
    content = raw.get("choices", [{}])[0].get("message", {}).get("content")
    if not isinstance(content, str):
        raise ValueError("saved response has no message content")
    parsed = json.loads(content)

    public = _load_public_instance(release_dir, instance_id, "uniform")
    questions = public["decision_question_schema"]
    question_ids = {str(item["question_id"]) for item in questions}
    conformance_warnings: list[dict[str, Any]] = []
    canonical, errors = _normalize_response(
        parsed,
        instance_id,
        question_ids,
        "r26_decision",
        evidence_span_ids=_public_span_ids(public),
        evidence_role_protocol="edge_derived_v3",
        response_envelope_protocol="exact_target_map_v3",
        unknown_evidence_protocol="semantic_false_positive_v2",
        evidence_relations_by_target=_evidence_relations_by_target(questions),
        evidence_set_protocol="canonical_set_v2",
        conformance_warnings=conformance_warnings,
    )
    if errors:
        raise ValueError("canonical replay still has hard errors: " + "; ".join(errors))
    if set(canonical) != question_ids:
        raise ValueError("canonical replay does not contain the exact question set")

    raw_predictions = checkpoint.get("predictions", {})
    raw_prediction_path = output_dir / "RAW_SET_SEMANTIC_PREDICTIONS.jsonl"
    canonical_prediction_path = output_dir / "CANONICAL_PREDICTIONS.jsonl"
    _write_jsonl(raw_prediction_path, _prediction_row(instance_id, raw_predictions))
    _write_jsonl(canonical_prediction_path, _prediction_row(instance_id, canonical))
    raw_scores = score_predictions(
        release_dir, raw_prediction_path, instance_ids=[instance_id]
    )
    canonical_scores = score_predictions(
        release_dir, canonical_prediction_path, instance_ids=[instance_id]
    )

    config_path = Path(
        str(metadata.get("experiment_provenance", {}).get("config_path", ""))
    )
    config = _read(config_path)
    source_spec = dict(config["runs"][0])
    prospective_spec = dict(source_spec)
    prospective_spec["r26_evidence_set_protocol"] = "canonical_set_v2"
    prospective_request = _request_record(
        release_dir,
        public,
        questions,
        0,
        "r26_decision",
        evidence_role_protocol="edge_derived_v3",
        response_envelope_protocol="exact_target_map_v3",
        unknown_evidence_protocol="semantic_false_positive_v2",
        evidence_set_protocol="canonical_set_v2",
    )
    prospective_hash = _request_sha256(prospective_request, prospective_spec)
    semantic_unknown_warnings = _evidence_grounding_warnings(
        canonical, _public_span_ids(public)
    )
    affected_questions = {
        str(item["question_id"]) for item in conformance_warnings
    }
    selected_score_keys = (
        "decision_field_macro_accuracy",
        "decision_informative_field_accuracy",
        "decision_informative_field_value_balanced_accuracy",
        "factual_record_macro_accuracy",
        "minimal_evidence_f1",
        "rejected_evidence_f1",
        "minimal_evidence_edge_f1",
        "content_dependency_edge_f1",
        "evidence_chain_joint_exact",
        "factual_evidence_chain_joint_exact",
        "unknown_evidence_question_rate",
        "unknown_evidence_reference_rate",
    )
    score_invariant = raw_scores == canonical_scores
    report = {
        "protocol_version": "VETT-R26.18-CANONICAL-SET-POSTHOC-REPLAY-1",
        "status": "NON_OFFICIAL_POST_HOC_REPLAY",
        "official_score": False,
        "provider_requests_made": 0,
        "dataset_bytes_changed": False,
        "source_run_id": metadata.get("run_id"),
        "source_instance_id": instance_id,
        "source_official_status_preserved": batch.get("status"),
        "source_validation_errors_preserved": validation_errors,
        "source_request_sha256": checkpoint.get("request_sha256"),
        "prospective_request_sha256": prospective_hash,
        "prospective_request_differs": prospective_hash
        != checkpoint.get("request_sha256"),
        "source_raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        "canonical_set_protocol": "canonical_set_v2",
        "canonical_question_count": len(canonical),
        "output_conformance": {
            "status": "FAIL_CANONICALIZED"
            if conformance_warnings
            else "PASS",
            "affected_questions": len(affected_questions),
            "question_conformance_rate": round(
                1.0 - len(affected_questions) / len(question_ids), 6
            ),
            "warning_events": len(conformance_warnings),
            "duplicate_groups": sum(
                int(item["duplicate_groups"])
                for item in conformance_warnings
            ),
            "redundant_count": sum(
                int(item["redundant_count"])
                for item in conformance_warnings
            ),
            "maximum_multiplicity": max(
                (
                    int(item["maximum_multiplicity"])
                    for item in conformance_warnings
                ),
                default=1,
            ),
            "warnings": conformance_warnings,
        },
        "semantic_unknown_evidence_warnings": semantic_unknown_warnings,
        "set_semantic_score_invariant_before_after_canonicalization": score_invariant,
        "diagnostic_scores": {
            key: canonical_scores[key] for key in selected_score_keys
        },
        "artifacts": {
            "raw_set_semantic_predictions": str(raw_prediction_path),
            "canonical_predictions": str(canonical_prediction_path),
        },
        "decision": {
            "historical_result_reclassified": False,
            "historical_or_future_runs_mergeable": False,
            "dataset_mutation_authorized": False,
            "external_execution_authorized": False,
            "local_protocol_candidate_supported": bool(score_invariant),
        },
        "claim_boundary": (
            "The source request did not contain the prospective canonical-set contract. "
            "This replay validates local semantics only; its scores are diagnostic and "
            "cannot be reported as an official Sentinel5 result."
        ),
    }
    _write(output_dir / "CANONICAL_SET_REPLAY.json", report)
    (output_dir / "README.md").write_text(
        "# R26.18 canonical-set post-hoc replay\n\n"
        f"- Status: `{report['status']}`\n"
        f"- Source status preserved: `{batch.get('status')}`\n"
        "- Provider requests: 0\n"
        f"- Affected questions: {len(affected_questions)}/{len(question_ids)}\n"
        f"- Duplicate groups / redundant copies: "
        f"{report['output_conformance']['duplicate_groups']}/"
        f"{report['output_conformance']['redundant_count']}\n"
        f"- Set-semantic score invariant: {score_invariant}\n\n"
        "This is a non-official replay. It validates that exact duplicate removal "
        "does not alter set-semantic scores while preserving a separate conformance "
        "failure. It does not reclassify the paid source run.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-canonical-set-replay")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = replay_canonical_set(
        args.release, args.source_run, args.instance_id, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["replay_canonical_set"]
