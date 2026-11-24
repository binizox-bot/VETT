from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any, Callable

from vett_eval.runner import (
    _chat_response_diagnostics,
    _normalize_response,
    _public_span_ids,
    _response_diagnostic_errors,
)

from .evaluation import score_predictions
from .sentinel_preflight import _oracle_response


SENSITIVITY_METRICS = (
    "factual_record_macro_accuracy",
    "decision_field_macro_accuracy",
    "decision_informative_field_accuracy",
    "decision_informative_field_value_balanced_accuracy",
    "decision_informative_field_skill_over_unconditional_prior",
    "minimal_evidence_f1",
    "rejected_evidence_f1",
    "minimal_evidence_edge_f1",
    "minimal_evidence_edge_question_macro_f1",
    "minimal_evidence_edge_exact",
    "evidence_chain_joint_exact",
    "factual_evidence_chain_joint_exact",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(
    public: dict[str, Any], response: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    return _normalize_response(
        response,
        str(public["instance_id"]),
        {
            str(question["question_id"])
            for question in public["decision_question_schema"]
        },
        "r26_decision",
        _public_span_ids(public),
        "edge_derived_v3",
        "request_bound_v2",
    )


def _prediction_row(instance_id: str, normalized: dict[str, Any]) -> dict[str, Any]:
    return {
        "instance_id": instance_id,
        "decision_predictions": [
            {"question_id": question_id, **prediction}
            for question_id, prediction in normalized.items()
        ],
    }


def _score_normalized(
    release_dir: Path, instance_id: str, normalized: dict[str, Any]
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="vett_r26_fault_") as directory:
        prediction_path = Path(directory) / "predictions.jsonl"
        prediction_path.write_text(
            json.dumps(
                _prediction_row(instance_id, normalized),
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return score_predictions(
            release_dir, prediction_path, instance_ids=[instance_id]
        )


def _remove_first_relation(response: dict[str, Any], relation: str) -> None:
    for prediction in response["decision_predictions"]:
        edges = prediction["evidence_edges"]
        for index, edge in enumerate(edges):
            if edge["relation"] == relation:
                edges.pop(index)
                return
    raise ValueError(f"no edge relation available for mutation: {relation}")


def _replace_first_relation(
    response: dict[str, Any], relation: str, replacement: str
) -> None:
    for prediction in response["decision_predictions"]:
        for edge in prediction["evidence_edges"]:
            if edge["relation"] == relation:
                edge["relation"] = replacement
                return
    raise ValueError(f"no edge relation available for mutation: {relation}")


def audit_protocol_fault_matrix(
    release_dir: Path,
    instance_id: str = "match_0021",
    output_path: Path | None = None,
) -> dict[str, Any]:
    public = _read(release_dir / "public" / instance_id / "public_instance.json")
    gold = _read(release_dir / "private" / instance_id / "private_gold.json")
    oracle = _oracle_response(gold)
    baseline_normalized, baseline_errors = _normalize(public, oracle)
    baseline_scores = _score_normalized(
        release_dir, instance_id, baseline_normalized
    )
    cases: list[dict[str, Any]] = []

    protocol_mutations: list[
        tuple[str, Callable[[dict[str, Any]], None], str]
    ] = [
        (
            "missing_question",
            lambda value: value["decision_predictions"].pop(),
            "protocol",
        ),
        (
            "duplicate_evidence_span",
            lambda value: value["decision_predictions"][0]["evidence_spans"].append(
                value["decision_predictions"][0]["evidence_spans"][0]
            ),
            "protocol",
        ),
        (
            "unknown_neutral_span",
            lambda value: value["decision_predictions"][0]["evidence_spans"].append(
                "s_000000000000000000000000"
            ),
            "protocol",
        ),
        (
            "overlong_explanation",
            lambda value: value["decision_predictions"][0].__setitem__(
                "explanation", "x" * 481
            ),
            "protocol",
        ),
        (
            "wrong_explicit_instance_identity",
            lambda value: value.__setitem__("instance_id", "match_wrong"),
            "protocol",
        ),
        (
            "incomplete_counterfactual_record",
            lambda value: value["decision_predictions"][0][
                "counterfactual_record"
            ].pop("dismissal"),
            "protocol",
        ),
    ]
    for name, mutate, expected_layer in protocol_mutations:
        candidate = copy.deepcopy(oracle)
        mutate(candidate)
        _normalized, errors = _normalize(public, candidate)
        observed_layer = "protocol" if errors else "accepted"
        cases.append(
            {
                "case": name,
                "expected_layer": expected_layer,
                "observed_layer": observed_layer,
                "passed": observed_layer == expected_layer,
                "diagnostic_count": len(errors),
                "diagnostic_preview": errors[:3],
            }
        )

    semantic_mutations: list[
        tuple[str, Callable[[dict[str, Any]], None], str, set[str], set[str]]
    ] = [
        (
            "wrong_factual_total_runs",
            lambda value: value["decision_predictions"][0]["decision_record"].__setitem__(
                "total_runs",
                value["decision_predictions"][0]["decision_record"]["total_runs"]
                + 1,
            ),
            "factual_record_macro_accuracy",
            {
                "factual_record_macro_accuracy",
                "decision_field_macro_accuracy",
                "decision_informative_field_accuracy",
                "decision_informative_field_value_balanced_accuracy",
                "decision_informative_field_skill_over_unconditional_prior",
                "factual_evidence_chain_joint_exact",
            },
            {
                "minimal_evidence_f1",
                "rejected_evidence_f1",
                "minimal_evidence_edge_f1",
                "minimal_evidence_edge_question_macro_f1",
                "minimal_evidence_edge_exact",
                "evidence_chain_joint_exact",
            },
        ),
        (
            "missing_supports_decision_edge",
            lambda value: _remove_first_relation(value, "supports_decision"),
            "minimal_evidence_edge_f1",
            {
                "minimal_evidence_edge_f1",
                "minimal_evidence_edge_question_macro_f1",
                "minimal_evidence_edge_exact",
                "evidence_chain_joint_exact",
                "factual_evidence_chain_joint_exact",
            },
            {
                "factual_record_macro_accuracy",
                "decision_field_macro_accuracy",
                "decision_informative_field_accuracy",
                "decision_informative_field_value_balanced_accuracy",
                "decision_informative_field_skill_over_unconditional_prior",
                "minimal_evidence_f1",
                "rejected_evidence_f1",
            },
        ),
        (
            "wrong_relation_same_endpoints",
            lambda value: _replace_first_relation(
                value, "supports_decision", "governs_decision"
            ),
            "minimal_evidence_edge_exact",
            {
                "minimal_evidence_edge_f1",
                "minimal_evidence_edge_question_macro_f1",
                "minimal_evidence_edge_exact",
                "evidence_chain_joint_exact",
                "factual_evidence_chain_joint_exact",
            },
            {
                "factual_record_macro_accuracy",
                "decision_field_macro_accuracy",
                "decision_informative_field_accuracy",
                "decision_informative_field_value_balanced_accuracy",
                "decision_informative_field_skill_over_unconditional_prior",
                "minimal_evidence_f1",
                "rejected_evidence_f1",
            },
        ),
        (
            "missing_rejects_edge",
            lambda value: _remove_first_relation(value, "rejects"),
            "rejected_evidence_f1",
            {
                "rejected_evidence_f1",
                "minimal_evidence_edge_f1",
                "minimal_evidence_edge_question_macro_f1",
                "minimal_evidence_edge_exact",
                "evidence_chain_joint_exact",
                "factual_evidence_chain_joint_exact",
            },
            {
                "factual_record_macro_accuracy",
                "decision_field_macro_accuracy",
                "decision_informative_field_accuracy",
                "decision_informative_field_value_balanced_accuracy",
                "decision_informative_field_skill_over_unconditional_prior",
                "minimal_evidence_f1",
            },
        ),
    ]
    for name, mutate, metric, expected_decreased, expected_unchanged in semantic_mutations:
        candidate = copy.deepcopy(oracle)
        mutate(candidate)
        normalized, errors = _normalize(public, candidate)
        scores = _score_normalized(release_dir, instance_id, normalized)
        deltas = {
            key: round(float(scores[key]) - float(baseline_scores[key]), 6)
            for key in SENSITIVITY_METRICS
        }
        decreased_ok = all(deltas[key] < 0 for key in expected_decreased)
        unchanged_ok = all(deltas[key] == 0 for key in expected_unchanged)
        metric_decreased = float(scores[metric]) < float(baseline_scores[metric])
        sensitivity_ok = metric_decreased and decreased_ok and unchanged_ok
        observed_layer = "semantic" if not errors and sensitivity_ok else (
            "protocol" if errors else "undetected"
        )
        cases.append(
            {
                "case": name,
                "expected_layer": "semantic",
                "observed_layer": observed_layer,
                "passed": observed_layer == "semantic",
                "normalization_errors": errors,
                "affected_metric": metric,
                "baseline_metric": baseline_scores[metric],
                "mutated_metric": scores[metric],
                "metric_deltas": deltas,
                "expected_decreased_metrics": sorted(expected_decreased),
                "expected_unchanged_metrics": sorted(expected_unchanged),
                "sensitivity_fingerprint_pass": sensitivity_ok,
            }
        )

    transport_inputs = [
        (
            "provider_finish_reason_length",
            {
                "choices": [
                    {"finish_reason": "length", "message": {"content": "{"}}
                ]
            },
        ),
        (
            "json_closure_repair_required",
            {
                "choices": [
                    {"finish_reason": "stop", "message": {"content": "{}"}}
                ],
                "vett_json_repair": {"appended_suffix": "]}"},
            },
        ),
    ]
    for name, raw in transport_inputs:
        diagnostics = _chat_response_diagnostics(raw)
        errors = _response_diagnostic_errors(diagnostics)
        cases.append(
            {
                "case": name,
                "expected_layer": "transport_or_envelope",
                "observed_layer": "transport_or_envelope" if errors else "accepted",
                "passed": bool(errors),
                "diagnostics": diagnostics,
            }
        )

    baseline_ok = (
        not baseline_errors
        and baseline_scores["factual_evidence_chain_joint_exact"] == 1.0
    )
    report = {
        "protocol_version": "VETT-R26-PROTOCOL-FAULT-MATRIX-2",
        "status": (
            "PASS" if baseline_ok and all(case["passed"] for case in cases) else "FAIL"
        ),
        "release": str(release_dir),
        "instance_id": instance_id,
        "baseline_normalization_errors": baseline_errors,
        "baseline_factual_evidence_chain_joint_exact": baseline_scores[
            "factual_evidence_chain_joint_exact"
        ],
        "baseline_metric_vector": {
            key: baseline_scores[key] for key in SENSITIVITY_METRICS
        },
        "cases": cases,
        "case_counts_by_expected_layer": {
            layer: sum(case["expected_layer"] == layer for case in cases)
            for layer in ("transport_or_envelope", "protocol", "semantic")
        },
        "provider_requests_made": 0,
        "claim_boundary": (
            "Synthetic faults validate attribution and fail-closed behavior. They do "
            "not estimate how often a real provider or model will produce each fault."
        ),
    }
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-protocol-fault-matrix")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--instance-id", default="match_0021")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_protocol_fault_matrix(
        args.release, args.instance_id, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_protocol_fault_matrix"]
