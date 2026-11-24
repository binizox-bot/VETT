from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from vett_eval.runner import (
    _evidence_grounding_warnings,
    _evidence_relations_by_target,
    _normalize_response,
    _public_span_ids,
)

from .evaluation import score_predictions


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for row, left_char in enumerate(left, start=1):
        current = [row]
        for column, right_char in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[column] + 1,
                previous[column - 1] + (left_char != right_char),
            ))
        previous = current
    return previous[-1]


def replay_unknown_evidence_policy(
    release_dir: Path,
    run_dir: Path,
    instance_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Replay an old invalid response diagnostically under the frozen Edge-7 rule.

    This never edits the source run and explicitly marks every score non-official.
    """
    metadata = _read(run_dir / "RUN_METADATA.json")
    matching = [
        record
        for record in metadata.get("records", [])
        if str(record.get("instance_id")) == instance_id
    ]
    if len(matching) != 1 or len(matching[0].get("batches", [])) != 1:
        raise ValueError("replay requires exactly one recorded batch for the instance")
    source_batch = matching[0]["batches"][0]
    if source_batch.get("status") not in {"INVALID", "INVALID_OUTPUT"}:
        raise ValueError("replay is reserved for a preserved invalid source response")
    raw_path = run_dir / "raw" / instance_id / "batch_000.json"
    checkpoint_path = run_dir / "checkpoints" / instance_id / "batch_000.json"
    raw = _read(raw_path)
    content = raw["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    public = _read(release_dir / "public" / instance_id / "public_instance.json")
    target_schema = public["decision_question_schema"]
    public_ids = _public_span_ids(public)
    normalized, errors = _normalize_response(
        parsed,
        instance_id,
        {str(item["question_id"]) for item in target_schema},
        "r26_decision",
        evidence_span_ids=public_ids,
        evidence_role_protocol="edge_derived_v3",
        response_envelope_protocol="request_bound_v2",
        unknown_evidence_protocol="semantic_false_positive_v2",
        evidence_relations_by_target=_evidence_relations_by_target(target_schema),
    )
    warnings = _evidence_grounding_warnings(normalized, public_ids)
    if errors:
        raise ValueError(f"response has non-unknown protocol errors: {errors}")

    span_text = {
        str(span["span_id"]): str(span["text"])
        for document in public["documents"]
        for span in document["spans"]
    }
    near_matches: list[dict[str, Any]] = []
    unknown_ids = sorted({
        value
        for warning in warnings
        for key in (
            "unknown_positive_span_ids",
            "unknown_rejected_span_ids",
            "unknown_edge_node_ids",
        )
        for value in warning[key]
    })
    for unknown_id in unknown_ids:
        distances = [
            (_levenshtein(unknown_id, public_id), public_id)
            for public_id in public_ids
        ]
        minimum = min(distance for distance, _ in distances)
        nearest = sorted(
            public_id for distance, public_id in distances if distance == minimum
        )
        near_matches.append({
            "unknown_id": unknown_id,
            "minimum_levenshtein_distance": minimum,
            "nearest_public_ids": nearest,
            "nearest_public_texts": [span_text[value] for value in nearest],
            "scoring_effect": "NONE_DIAGNOSTIC_ONLY",
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / "COUNTERFACTUAL_EDGE7_PREDICTIONS.jsonl"
    predictions_path.write_text(
        json.dumps({
            "instance_id": instance_id,
            "decision_predictions": [
                {"question_id": question_id, **prediction}
                for question_id, prediction in normalized.items()
            ],
        }, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    scores = score_predictions(
        release_dir, predictions_path, instance_ids=[instance_id]
    )
    report = {
        "protocol_version": "VETT-R26.16-UNKNOWN-EVIDENCE-REPLAY-1",
        "status": "COUNTERFACTUAL_POLICY_DIAGNOSTIC_ONLY",
        "official_score": False,
        "source_run_id": metadata.get("run_id", run_dir.name),
        "source_contract_version": source_batch.get("evaluation_contract_version"),
        "source_official_status": source_batch.get("status"),
        "source_status_unchanged": True,
        "instance_id": instance_id,
        "edge7_normalization_errors": errors,
        "semantic_warnings": warnings,
        "near_match_diagnostics": near_matches,
        "counterfactual_scores": scores,
        "source_artifact_sha256": {
            "raw": _sha256(raw_path),
            "checkpoint": _sha256(checkpoint_path),
            "run_metadata": _sha256(run_dir / "RUN_METADATA.json"),
        },
        "warning": (
            "These scores answer only how the preserved Edge-6 response would be "
            "classified by the preregistered Edge-7 policy. They are not an official "
            "benchmark result and must not be pooled with future Edge-7 requests."
        ),
    }
    (output_dir / "COUNTERFACTUAL_EDGE7_REPLAY.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-unknown-evidence-replay")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = replay_unknown_evidence_policy(
        args.release, args.run, args.instance_id, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["replay_unknown_evidence_policy"]
