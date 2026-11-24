from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from vett_eval.runner import (
    _evidence_relations_by_target,
    _evidence_grounding_warnings,
    _load_public_instance,
    _normalize_response,
    _public_span_ids,
    _request_record,
    _request_sha256,
    estimate_config,
)

from .answer_prior_audit import audit_answer_priors


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _oracle_response(
    gold: dict[str, Any],
    response_envelope_protocol: str = "request_bound_v2",
) -> dict[str, Any]:
    """A request-bound, edge-derived response used only for protocol validation."""
    items = [
        {
                "question_id": answer["question_id"],
                "decision_record": answer["decision_record"],
                "state": answer["state"],
                "evidence_spans": answer["minimum_evidence_spans"],
                "evidence_edges": answer["minimum_evidence_edges"],
                "counterfactual_record": answer["counterfactual"]["decision_record"],
                "counterfactual_state": answer["counterfactual"]["state"],
                "explanation": (
                    "The evidence graph resolves identity, authority, incident facts "
                    "and governing rules."
                ),
                "confidence": 1.0,
        }
        for answer in gold["decision_answers"]
    ]
    if response_envelope_protocol == "exact_target_map_v3":
        return {
            "decision_predictions": {
                str(item["question_id"]): {
                    key: value
                    for key, value in item.items()
                    if key != "question_id"
                }
                for item in items
            }
        }
    return {"decision_predictions": items}


def _schema_identifier_errors(
    response: dict[str, Any], response_schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    container_schema = response_schema["properties"]["decision_predictions"]
    response_predictions = response["decision_predictions"]
    if container_schema["type"] == "object":
        allowed_questions = set(container_schema["properties"])
        prediction_items = list(response_predictions.items())
    else:
        item_schema = container_schema["items"]
        allowed_questions = set(
            item_schema["properties"]["question_id"].get("enum", [])
        )
        prediction_items = [
            (str(prediction["question_id"]), prediction)
            for prediction in response_predictions
        ]
    for qid, prediction in prediction_items:
        qid = str(qid)
        if qid not in allowed_questions:
            errors.append(f"schema_question_enum:{qid}")
            continue
        item_schema = (
            container_schema["properties"][qid]
            if container_schema["type"] == "object"
            else container_schema["items"]
        )
        span_pattern = item_schema["properties"]["evidence_spans"]["items"][
            "pattern"
        ]
        edge_properties = item_schema["properties"]["evidence_edges"]["items"][
            "properties"
        ]
        source_pattern = edge_properties["source_id"]["pattern"]
        target_pattern = edge_properties["target_id"]["pattern"]
        for span_id in prediction["evidence_spans"]:
            if re.fullmatch(span_pattern, str(span_id)) is None:
                errors.append(f"schema_span_pattern:{span_id}")
        for edge in prediction["evidence_edges"]:
            if re.fullmatch(source_pattern, str(edge["source_id"])) is None:
                errors.append(f"schema_edge_source_pattern:{edge['source_id']}")
            if re.fullmatch(target_pattern, str(edge["target_id"])) is None:
                errors.append(f"schema_edge_target_pattern:{edge['target_id']}")
    return errors


def compile_sentinel_preflight(
    config_path: Path,
    contract_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    config = _read(config_path)
    contract = _read(contract_path)
    errors: list[str] = []
    runs = config.get("runs", [])
    if len(runs) != 1:
        errors.append("config_must_contain_exactly_one_run")
        spec: dict[str, Any] = {}
    else:
        spec = runs[0]
    release_dir = Path(str(config.get("release_dir", "")))
    if not release_dir.is_dir():
        candidate = (config_path.resolve().parent / release_dir).resolve()
        if candidate.is_dir():
            release_dir = candidate
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    estimate = estimate_config(config_path)
    estimate_run = estimate.get("runs", [{}])[0]
    answer_prior = audit_answer_priors(release_dir)
    expected_ids = list(map(str, contract["instance_ids"]))
    selected_ids = list(map(str, spec.get("instance_ids", [])))
    generation = contract["generation_contract"]
    safety = contract["safety_gates"]
    unknown_evidence_protocol = str(
        spec.get("r26_unknown_evidence_protocol", "batch_invalid_v1")
    )
    response_envelope_protocol = str(
        generation.get("r26_response_envelope_protocol", "request_bound_v2")
    )
    evidence_set_protocol = str(
        spec.get("r26_evidence_set_protocol", "strict_unique_v1")
    )

    gates = {
        "dataset_version_frozen": summary.get("dataset_version")
        == contract.get("dataset_version"),
        "sentinel_instance_order_frozen": selected_ids == expected_ids,
        "model_frozen": spec.get("model") == contract.get("model"),
        "uniform_is_official_input": spec.get("public_input_form", "uniform")
        == contract.get("official_input_form"),
        "execution_authorization_is_required": config.get(
            "require_explicit_execution_authorization"
        )
        is True,
        "execution_remains_blocked": config.get("execution_authorized") is False,
        "fresh_output_directory": not Path(str(config.get("output_dir", ""))).exists(),
        "no_literal_api_secret_in_config": "sk-" not in config_path.read_text(
            encoding="utf-8"
        ).casefold(),
        "zero_retry_fail_closed": int(spec.get("max_retries", -1)) == 0
        and spec.get("stop_run_on_batch_failure") is True
        and spec.get("reuse_terminal_failures") is True
        and spec.get("prevent_duplicate_requests") is True,
        "one_batch_per_match": int(spec.get("target_batch_size", 0)) == 5
        and estimate_run.get("batches") == len(expected_ids),
        "request_bound_edge_derived": spec.get("r26_evidence_role_protocol")
        == "edge_derived_v3"
        and spec.get("r26_response_envelope_protocol")
        == response_envelope_protocol
        and response_envelope_protocol
        in {"request_bound_v2", "exact_target_map_v3"},
        "unknown_evidence_protocol_matches_contract": (
            unknown_evidence_protocol
            == generation.get(
                "r26_unknown_evidence_protocol", "batch_invalid_v1"
            )
        ),
        "evidence_set_protocol_matches_contract": (
            evidence_set_protocol
            == generation.get(
                "r26_evidence_set_protocol", "strict_unique_v1"
            )
        ),
        "structured_output_required": spec.get("response_format_mode")
        == "json_schema",
        "generation_parameters_match_contract": all(
            spec.get(key) == value for key, value in generation.items()
        ),
        "pricing_matches_verified_contract": spec.get("pricing_cny_per_million")
        == contract.get("pricing_cny_per_million"),
        "estimated_cost_within_contract": float(
            estimate.get("estimated_total_cost_cny_zero_cache") or math.inf
        )
        <= float(safety["maximum_zero_cache_cost_cny"]),
        "no_question_only_factual_answer_shortcut": answer_prior.get("status")
        == "PASS",
    }

    per_match: list[dict[str, Any]] = []
    request_hashes: list[str] = []
    anchor_level_cells: Counter[tuple[str, str]] = Counter()
    forbidden_private_keys = (
        '"solver_facts"',
        '"minimum_evidence_spans"',
        '"decision_answers"',
        '"r26_13_identifier_map"',
    )
    for match_id in selected_ids:
        public = _load_public_instance(release_dir, match_id, "uniform")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        anchor_level_cells.update(
            (
                str(answer.get("cross_level_anchor_family", "")),
                str(answer.get("level", "")),
            )
            for answer in gold["decision_answers"]
        )
        questions = public["decision_question_schema"]
        request = _request_record(
            release_dir,
            public,
            questions,
            0,
            "r26_decision",
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol=response_envelope_protocol,
            unknown_evidence_protocol=unknown_evidence_protocol,
            evidence_set_protocol=evidence_set_protocol,
        )
        response = _oracle_response(gold, response_envelope_protocol)
        normalized, normalize_errors = _normalize_response(
            response,
            match_id,
            {str(question["question_id"]) for question in questions},
            "r26_decision",
            _public_span_ids(public),
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol=response_envelope_protocol,
            unknown_evidence_protocol=unknown_evidence_protocol,
            evidence_relations_by_target=_evidence_relations_by_target(questions),
            evidence_set_protocol=evidence_set_protocol,
        )
        oracle_warnings = _evidence_grounding_warnings(
            normalized, _public_span_ids(public)
        )
        semantic_unknown_probe_passed = True
        if unknown_evidence_protocol == "semantic_false_positive_v2":
            mutated_response = json.loads(json.dumps(response))
            public_span_ids = _public_span_ids(public)
            unknown_id = "s_" + ("0" * 24)
            if unknown_id in public_span_ids:
                unknown_id = "s_" + ("f" * 24)
            if response_envelope_protocol == "exact_target_map_v3":
                first_question = next(iter(mutated_response["decision_predictions"]))
                mutated_response["decision_predictions"][first_question][
                    "evidence_spans"
                ][0] = unknown_id
            else:
                mutated_response["decision_predictions"][0]["evidence_spans"][0] = (
                    unknown_id
                )
            mutated, mutation_errors = _normalize_response(
                mutated_response,
                match_id,
                {str(question["question_id"]) for question in questions},
                "r26_decision",
                public_span_ids,
                evidence_role_protocol="edge_derived_v3",
                response_envelope_protocol=response_envelope_protocol,
                unknown_evidence_protocol=unknown_evidence_protocol,
                evidence_relations_by_target=_evidence_relations_by_target(questions),
                evidence_set_protocol=evidence_set_protocol,
            )
            mutation_warnings = _evidence_grounding_warnings(
                mutated, public_span_ids
            )
            semantic_unknown_probe_passed = (
                not mutation_errors
                and len(mutation_warnings) == 1
                and mutation_warnings[0]["unknown_positive_span_ids"]
                == [unknown_id]
            )
        canonical_duplicate_probe_passed = True
        if evidence_set_protocol == "canonical_set_v2":
            duplicate_response = json.loads(json.dumps(response))
            if response_envelope_protocol == "exact_target_map_v3":
                first_question = next(iter(duplicate_response["decision_predictions"]))
                duplicate_item = duplicate_response["decision_predictions"][
                    first_question
                ]
            else:
                duplicate_item = duplicate_response["decision_predictions"][0]
                first_question = str(duplicate_item["question_id"])
            duplicate_item["evidence_spans"].append(
                duplicate_item["evidence_spans"][0]
            )
            duplicate_item["evidence_edges"].append(
                json.loads(json.dumps(duplicate_item["evidence_edges"][0]))
            )
            duplicate_warnings: list[dict[str, Any]] = []
            duplicate_normalized, duplicate_errors = _normalize_response(
                duplicate_response,
                match_id,
                {str(question["question_id"]) for question in questions},
                "r26_decision",
                _public_span_ids(public),
                evidence_role_protocol="edge_derived_v3",
                response_envelope_protocol=response_envelope_protocol,
                unknown_evidence_protocol=unknown_evidence_protocol,
                evidence_relations_by_target=_evidence_relations_by_target(questions),
                evidence_set_protocol=evidence_set_protocol,
                conformance_warnings=duplicate_warnings,
            )
            canonical_duplicate_probe_passed = (
                not duplicate_errors
                and len(duplicate_warnings) == 2
                and sum(
                    int(item.get("redundant_count", 0))
                    for item in duplicate_warnings
                )
                == 2
                and len(
                    duplicate_normalized[first_question]["evidence_spans"]
                )
                == len(normalized[first_question]["evidence_spans"])
                and len(
                    duplicate_normalized[first_question]["evidence_edges"]
                )
                == len(normalized[first_question]["evidence_edges"])
            )
        schema_errors = _schema_identifier_errors(response, request["response_schema"])
        prompt = request["system_prompt"] + request["user_prompt"]
        private_leaks = [key for key in forbidden_private_keys if key in prompt]
        request_chars = (
            len(request["system_prompt"])
            + len(request["user_prompt"])
            + len(json.dumps(request["response_schema"], separators=(",", ":")))
            + 500
        )
        chars_per_token = float(spec["estimate_chars_per_input_token"])
        estimated_input_tokens = math.ceil(request_chars / chars_per_token)
        compact_response = json.dumps(
            response, ensure_ascii=False, separators=(",", ":")
        )
        prediction_schema = request["response_schema"]["properties"][
            "decision_predictions"
        ]
        question_ids = [str(question["question_id"]) for question in questions]
        exact_target_keys_exposed = (
            prediction_schema.get("type") == "object"
            and set(prediction_schema.get("properties", {})) == set(question_ids)
            and set(prediction_schema.get("required", [])) == set(question_ids)
            and prediction_schema.get("additionalProperties") is False
            and all(
                "question_id" not in item_schema.get("properties", {})
                for item_schema in prediction_schema.get("properties", {}).values()
            )
        )
        relation_item_schema = (
            next(iter(prediction_schema["properties"].values()))
            if prediction_schema["type"] == "object"
            else prediction_schema["items"]
        )
        relation_enum = relation_item_schema["properties"]["evidence_edges"][
            "items"
        ]["properties"]["relation"]["enum"]
        content_dependency_protocol_exposed = (
            "conditions_rule" in relation_enum
            and "conditions_rule" in request["user_prompt"]
        )
        oracle_output_tokens = math.ceil(len(compact_response) / chars_per_token)
        oracle_with_reasoning = oracle_output_tokens + int(spec["thinking_budget"])
        output_headroom = int(spec["max_tokens"]) / oracle_with_reasoning
        context_utilization = (
            estimated_input_tokens + int(spec["max_tokens"])
        ) / int(contract["model_context_tokens"])
        request_hash = _request_sha256(request, spec)
        request_hashes.append(request_hash)
        item_errors = [
            *[f"normalize:{item}" for item in normalize_errors],
            *[f"schema:{item}" for item in schema_errors],
            *[f"private_key:{item}" for item in private_leaks],
        ]
        if oracle_warnings:
            item_errors.append("oracle_has_unknown_evidence_warning")
        if not semantic_unknown_probe_passed:
            item_errors.append("semantic_unknown_evidence_probe_failed")
        if not canonical_duplicate_probe_passed:
            item_errors.append("canonical_duplicate_probe_failed")
        if len(normalized) != 5:
            item_errors.append(f"normalized_question_count:{len(normalized)}")
        per_match.append(
            {
                "match_id": match_id,
                "status": "PASS" if not item_errors else "FAIL",
                "errors": item_errors,
                "questions": len(questions),
                "public_span_ids": len(_public_span_ids(public)),
                "request_sha256": request_hash,
                "semantic_request_sha256": _canonical_sha256(
                    {
                        "system_prompt": request["system_prompt"],
                        "user_prompt": request["user_prompt"],
                        "response_schema": request["response_schema"],
                    }
                ),
                "estimated_input_tokens_conservative": estimated_input_tokens,
                "oracle_response_characters": len(compact_response),
                "oracle_output_tokens_conservative": oracle_output_tokens,
                "oracle_plus_reasoning_tokens_conservative": oracle_with_reasoning,
                "configured_max_tokens": int(spec["max_tokens"]),
                "content_dependency_protocol_exposed": (
                    content_dependency_protocol_exposed
                ),
                "exact_target_keys_exposed": exact_target_keys_exposed,
                "oracle_unknown_evidence_warnings": len(oracle_warnings),
                "semantic_unknown_evidence_probe_passed": (
                    semantic_unknown_probe_passed
                ),
                "canonical_duplicate_probe_passed": (
                    canonical_duplicate_probe_passed
                ),
                "oracle_output_headroom_ratio": round(output_headroom, 6),
                "context_utilization_upper_bound": round(context_utilization, 6),
            }
        )

    matched = contract.get("matched_design", {})
    expected_anchors = list(map(str, matched.get("expected_anchor_families", [])))
    expected_levels = list(map(str, matched.get("expected_levels", [])))
    expected_cell_count = int(
        matched.get("required_count_per_anchor_level_cell", 0)
    )
    gates.update(
        {
            "all_oracle_responses_normalize": all(
                item["status"] == "PASS" for item in per_match
            ),
            "request_hashes_unique": len(request_hashes) == len(set(request_hashes)),
            "oracle_output_headroom_sufficient": min(
                item["oracle_output_headroom_ratio"] for item in per_match
            )
            >= float(
                safety["minimum_oracle_output_headroom_ratio_including_reasoning"]
            ),
            "context_utilization_within_contract": max(
                item["context_utilization_upper_bound"] for item in per_match
            )
            <= float(safety["maximum_context_utilization"]),
            "empirical_calibration_still_not_run": summary.get(
                "empirical_calibration", {}
            ).get("status")
            == "NOT_RUN",
            "complete_anchor_by_level_latin_square": bool(expected_anchors)
            and bool(expected_levels)
            and all(
                anchor_level_cells[(anchor, level)] == expected_cell_count
                for anchor in expected_anchors
                for level in expected_levels
            )
            and set(anchor_level_cells)
            == {
                (anchor, level)
                for anchor in expected_anchors
                for level in expected_levels
            },
            "content_dependency_protocol_exposed_when_required": (
                not safety.get("content_dependency_relation_required", False)
                or all(
                    item["content_dependency_protocol_exposed"]
                    for item in per_match
                )
            ),
            "semantic_unknown_evidence_probe_passes_when_required": (
                unknown_evidence_protocol != "semantic_false_positive_v2"
                or all(
                    item["semantic_unknown_evidence_probe_passed"]
                    for item in per_match
                )
            ),
            "canonical_duplicate_probe_passes_when_required": (
                evidence_set_protocol != "canonical_set_v2"
                or all(
                    item["canonical_duplicate_probe_passed"]
                    for item in per_match
                )
            ),
            "exact_target_keys_exposed_when_required": (
                not safety.get("exact_target_keys_required", False)
                or all(item["exact_target_keys_exposed"] for item in per_match)
            ),
        }
    )
    errors.extend(name for name, passed in gates.items() if not passed)
    report = {
        "protocol_version": (
            "VETT-R26-SENTINEL5-ZERO-REQUEST-PREFLIGHT-4"
            if evidence_set_protocol == "canonical_set_v2"
            else "VETT-R26-SENTINEL5-ZERO-REQUEST-PREFLIGHT-3"
        ),
        "status": (
            "REQUEST_READY_BLOCKED_BY_AUTHORIZATION" if not errors else "NOT_READY"
        ),
        "errors": errors,
        "gates": gates,
        "config": str(config_path),
        "contract": str(contract_path),
        "release": str(release_dir),
        "run_id": spec.get("run_id"),
        "model": spec.get("model"),
        "public_input_form": spec.get("public_input_form", "uniform"),
        "r26_unknown_evidence_protocol": unknown_evidence_protocol,
        "r26_response_envelope_protocol": response_envelope_protocol,
        "r26_evidence_set_protocol": evidence_set_protocol,
        "instances": len(selected_ids),
        "questions": sum(item["questions"] for item in per_match),
        "estimated_cost_cny_zero_cache": estimate.get(
            "estimated_total_cost_cny_zero_cache"
        ),
        "maximum_context_utilization_upper_bound": max(
            item["context_utilization_upper_bound"] for item in per_match
        ),
        "minimum_oracle_output_headroom_ratio": min(
            item["oracle_output_headroom_ratio"] for item in per_match
        ),
        "provider_requests_made": 0,
        "execution_authorized": False,
        "matched_anchor_design": {
            "anchors": expected_anchors,
            "levels": expected_levels,
            "required_count_per_cell": expected_cell_count,
            "cell_counts": {
                anchor: {
                    level: anchor_level_cells[(anchor, level)]
                    for level in expected_levels
                }
                for anchor in expected_anchors
            },
        },
        "answer_prior_shortcut_status": answer_prior.get("status"),
        "answer_prior_shortcut_gates": answer_prior.get("gates"),
        "per_match": per_match,
        "claim_boundary": (
            contract["claim_boundary"]
            + " A failed answer-prior audit blocks provider execution even when cost, "
            "schema and context-capacity gates pass."
        ),
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-sentinel-preflight")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compile_sentinel_preflight(args.config, args.contract, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["compile_sentinel_preflight"]
