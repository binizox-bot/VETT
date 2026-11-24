from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from vett_eval.runner import (
    _evidence_grounding_warnings,
    _evidence_relations_by_target,
    _normalize_response,
    _public_span_ids,
    _request_record,
)

from .evaluation import score_predictions
from .sentinel_preflight import _oracle_response


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(
    public: dict[str, Any], response: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    questions = public["decision_question_schema"]
    return _normalize_response(
        response,
        str(public["instance_id"]),
        {str(question["question_id"]) for question in questions},
        "r26_decision",
        _public_span_ids(public),
        evidence_role_protocol="edge_derived_v3",
        response_envelope_protocol="exact_target_map_v3",
        unknown_evidence_protocol="semantic_false_positive_v2",
        evidence_relations_by_target=_evidence_relations_by_target(questions),
    )


def _score(
    release_dir: Path, instance_id: str, normalized: dict[str, Any]
) -> dict[str, Any]:
    row = {
        "instance_id": instance_id,
        "decision_predictions": [
            {"question_id": question_id, **prediction}
            for question_id, prediction in normalized.items()
        ],
    }
    with tempfile.TemporaryDirectory(prefix="vett_exact_map_") as directory:
        path = Path(directory) / "predictions.jsonl"
        path.write_text(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return score_predictions(release_dir, path, instance_ids=[instance_id])


def audit_exact_target_map(
    release_dir: Path,
    instance_id: str = "match_0220",
    output_dir: Path | None = None,
) -> dict[str, Any]:
    public = _read(release_dir / "public" / instance_id / "public_instance.json")
    gold = _read(release_dir / "private" / instance_id / "private_gold.json")
    questions = public["decision_question_schema"]
    question_ids = [str(question["question_id"]) for question in questions]
    request = _request_record(
        release_dir,
        public,
        questions,
        0,
        "r26_decision",
        evidence_role_protocol="edge_derived_v3",
        response_envelope_protocol="exact_target_map_v3",
        unknown_evidence_protocol="semantic_false_positive_v2",
    )
    oracle = _oracle_response(gold, "exact_target_map_v3")
    baseline, baseline_errors = _normalize(public, oracle)
    baseline_scores = _score(release_dir, instance_id, baseline)
    schema = request["response_schema"]["properties"]["decision_predictions"]
    schema_gates = {
        "prediction_container_is_object": schema.get("type") == "object",
        "properties_are_exact_question_ids": set(schema.get("properties", {}))
        == set(question_ids),
        "all_question_ids_are_required": set(schema.get("required", []))
        == set(question_ids),
        "additional_question_keys_forbidden": schema.get("additionalProperties")
        is False,
        "inner_question_id_removed": all(
            "question_id" not in item.get("properties", {})
            for item in schema.get("properties", {}).values()
        ),
        "oracle_normalizes_without_error": not baseline_errors
        and set(baseline) == set(question_ids),
    }

    first_id, second_id = question_ids[:2]
    first_value = oracle["decision_predictions"][first_id]
    cases: list[dict[str, Any]] = []

    repeated_array = {
        "decision_predictions": [
            {"question_id": first_id, **copy.deepcopy(first_value)}
            for _ in question_ids
        ]
    }
    _, errors = _normalize(public, repeated_array)
    cases.append({
        "case": "observed_repeated_id_array",
        "expected": "PROTOCOL_REJECT",
        "passed": errors
        == ["decision_predictions must be an exact target-keyed object"],
        "diagnostics": errors,
    })

    missing = copy.deepcopy(oracle)
    missing["decision_predictions"].pop(second_id)
    _, errors = _normalize(public, missing)
    cases.append({
        "case": "missing_required_target_key",
        "expected": "PROTOCOL_REJECT",
        "passed": any("missing 1 requested target" in error for error in errors),
        "diagnostics": errors,
    })

    unexpected = copy.deepcopy(oracle)
    unexpected["decision_predictions"]["r25q_unregistered"] = (
        unexpected["decision_predictions"].pop(second_id)
    )
    _, errors = _normalize(public, unexpected)
    cases.append({
        "case": "unexpected_target_key",
        "expected": "PROTOCOL_REJECT",
        "passed": any("unexpected target_id" in error for error in errors)
        and any("missing 1 requested target" in error for error in errors),
        "diagnostics": errors,
    })

    redundant = copy.deepcopy(oracle)
    redundant["decision_predictions"][first_id]["question_id"] = first_id
    _, errors = _normalize(public, redundant)
    cases.append({
        "case": "redundant_inner_question_id",
        "expected": "PROTOCOL_REJECT",
        "passed": any("redundantly contains question_id" in error for error in errors),
        "diagnostics": errors,
    })

    wrong_instance = copy.deepcopy(oracle)
    wrong_instance["instance_id"] = "match_wrong"
    _, errors = _normalize(public, wrong_instance)
    cases.append({
        "case": "conflicting_top_level_instance",
        "expected": "PROTOCOL_REJECT",
        "passed": "response instance_id mismatch" in errors,
        "diagnostics": errors,
    })

    swapped = copy.deepcopy(oracle)
    for field in (
        "decision_record",
        "state",
        "counterfactual_record",
        "counterfactual_state",
    ):
        (
            swapped["decision_predictions"][first_id][field],
            swapped["decision_predictions"][second_id][field],
        ) = (
            swapped["decision_predictions"][second_id][field],
            swapped["decision_predictions"][first_id][field],
        )
    swapped_normalized, errors = _normalize(public, swapped)
    swapped_scores = _score(release_dir, instance_id, swapped_normalized)
    cases.append({
        "case": "semantically_swapped_payloads",
        "expected": "SEMANTIC_SCORE_PENALTY",
        "passed": not errors
        and swapped_scores["decision_field_macro_accuracy"]
        < baseline_scores["decision_field_macro_accuracy"],
        "diagnostics": errors,
        "baseline_decision_field_macro_accuracy": baseline_scores[
            "decision_field_macro_accuracy"
        ],
        "mutated_decision_field_macro_accuracy": swapped_scores[
            "decision_field_macro_accuracy"
        ],
        "interpretation": (
            "The envelope guarantees target coverage, not semantic identity binding; "
            "payload swaps remain ordinary scored model errors."
        ),
    })

    unknown = copy.deepcopy(oracle)
    unknown_id = "s_ffffffffffffffffffffffff"
    if unknown_id in _public_span_ids(public):
        unknown_id = "s_000000000000000000000000"
    unknown["decision_predictions"][first_id]["evidence_spans"][0] = unknown_id
    unknown_normalized, errors = _normalize(public, unknown)
    warnings = _evidence_grounding_warnings(
        unknown_normalized, _public_span_ids(public)
    )
    cases.append({
        "case": "well_formed_unknown_evidence",
        "expected": "SEMANTIC_FALSE_POSITIVE_WARNING",
        "passed": not errors
        and len(warnings) == 1
        and warnings[0]["unknown_positive_span_ids"] == [unknown_id],
        "diagnostics": errors,
        "semantic_warnings": warnings,
    })

    all_pass = all(schema_gates.values()) and all(case["passed"] for case in cases)
    report = {
        "protocol_version": "VETT-R26.17-EXACT-TARGET-MAP-AUDIT-1",
        "status": "PASS_LOCAL_ONLY" if all_pass else "FAIL",
        "dataset_version": _read(release_dir / "RELEASE_SUMMARY.json").get(
            "dataset_version"
        ),
        "instance_id": instance_id,
        "response_envelope_protocol": "exact_target_map_v3",
        "evaluation_contract_version": request["evaluation_contract_version"],
        "schema_gates": schema_gates,
        "fault_cases": cases,
        "provider_requests_made": 0,
        "dataset_bytes_changed": False,
        "claim_boundary": (
            "This audit proves local schema and evaluator attribution behavior only. "
            "It does not prove provider support, improve historical Edge7 validity, "
            "or authorize an external request."
        ),
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "EXACT_TARGET_MAP_AUDIT.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (output_dir / "EXACT_TARGET_MAP_AUDIT.md").write_text(
            "# R26.17 exact-target-map local audit\n\n"
            f"- Status: `{report['status']}`\n"
            f"- Match: `{instance_id}`\n"
            "- Provider requests: 0\n"
            "- Dataset bytes changed: no\n\n"
            "The five requested question IDs are required JSON object keys. The "
            "observed repeated-ID array, a missing key, an unexpected key, a "
            "redundant inner ID and a conflicting instance identity are rejected. "
            "A payload attached to the wrong valid key remains a semantic error and "
            "is penalized by the frozen scorer. Well-formed unknown evidence remains "
            "a semantic false positive rather than a batch failure.\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-exact-target-map-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--instance-id", default="match_0220")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_exact_target_map(
        args.release, args.instance_id, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_exact_target_map"]
