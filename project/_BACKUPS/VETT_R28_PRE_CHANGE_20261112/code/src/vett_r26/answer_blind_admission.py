from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_answer_blind_admission(
    release_dir: Path,
    analysis_dir: Path,
    metric_addendum: Path,
    output_json: Path,
) -> dict[str, Any]:
    """Admit a static candidate without converting static checks into model claims."""
    paths = {
        "release_summary": release_dir / "RELEASE_SUMMARY.json",
        "release_audit": release_dir / "STABILITY_AUDIT.json",
        "answer_prior": analysis_dir / "ANSWER_PRIOR_SHORTCUT_AUDIT.json",
        "adversarial_static_shortcut": analysis_dir
        / "ADVERSARIAL_STATIC_SHORTCUT_AUDIT.json",
        "structural_shortcut": analysis_dir / "STRUCTURAL_SHORTCUT_AUDIT.json",
        "answer_blind_drift": analysis_dir / "ANSWER_BLIND_DRIFT_AUDIT.json",
        "proof_certificate": analysis_dir / "PROOF_CERTIFICATE_AUDIT.json",
        "language_surface": analysis_dir / "language_surface" / "LANGUAGE_SURFACE_AUDIT.json",
        "assistant_language_review": analysis_dir
        / "language_surface"
        / "ASSISTANT_STRATIFIED_LANGUAGE_REVIEW.json",
        "semantic_shortcut": analysis_dir / "SEMANTIC_SHORTCUT_AUDIT.json",
        "oracle_score": analysis_dir / "ORACLE_SCORE.json",
        "determinism": analysis_dir / "DETERMINISM_CHECK.json",
        "streaming_220": analysis_dir / "STREAMING_EXPANSION_PREFLIGHT_220.json",
        "level_confound": analysis_dir / "LEVEL_SURFACE_CONFOUND_AUDIT.json",
        "protocol_fault_matrix": analysis_dir / "PROTOCOL_FAULT_MATRIX.json",
        "sentinel_preflight": analysis_dir / "SENTINEL5_ZERO_REQUEST_PREFLIGHT.json",
        "next_action": analysis_dir / "NEXT_ACTION.json",
        "metric_addendum": metric_addendum,
        "structural_shortcut_contract": metric_addendum.parent
        / "r26_14_structural_shortcut_audit_contract.json",
    }
    payload = {name: _read(path) for name, path in paths.items()}
    summary = payload["release_summary"]
    audit = payload["release_audit"]
    prior = payload["answer_prior"]
    adversarial = payload["adversarial_static_shortcut"]
    structural_shortcut = payload["structural_shortcut"]
    drift = payload["answer_blind_drift"]
    proof = payload["proof_certificate"]
    language = payload["language_surface"]
    language_review = payload["assistant_language_review"]
    semantic_shortcut = payload["semantic_shortcut"]
    oracle_payload = payload["oracle_score"]
    oracle = oracle_payload.get("score", oracle_payload)
    determinism = payload["determinism"]
    expansion = payload["streaming_220"]
    confound = payload["level_confound"]
    fault = payload["protocol_fault_matrix"]
    sentinel = payload["sentinel_preflight"]
    next_action = payload["next_action"]
    addendum = payload["metric_addendum"]

    oracle_metrics = (
        "decision_field_macro_accuracy",
        "decision_informative_field_accuracy",
        "decision_informative_field_value_balanced_accuracy",
        "decision_field_skill_over_unconditional_prior",
        "decision_informative_field_skill_over_unconditional_prior",
        "factual_evidence_chain_joint_exact",
    )
    static_gates = {
        "release_20_pass": summary.get("status") == "PASS",
        "integrated_release_audit_pass": audit.get("status") == "PASS",
        "question_only_answer_shortcut_controlled": (
            prior.get("status") == "PASS" and all(prior.get("gates", {}).values())
        ),
        "stronger_question_only_and_scenario_holdout_baselines_pass": (
            adversarial.get("status")
            == "PASS_WITH_DISCLOSED_COMPONENT_LOCATOR"
            and all(adversarial.get("factual_shortcut_gates", {}).values())
        ),
        "structural_shortcut_audit_pass": (
            structural_shortcut.get("status") == "PASS"
            and all(structural_shortcut.get("gates", {}).values())
        ),
        "answer_blind_transform_is_narrow_and_semantics_preserving": (
            drift.get("status") == "PASS" and all(drift.get("gates", {}).values())
        ),
        "all_100_proof_certificates_pass": (
            proof.get("status") == "PASS"
            and proof.get("status_counts", {}).get("PASS") == 100
        ),
        "automated_language_surface_pass": (
            language.get("status") == "AUTOMATED_PASS_HUMAN_REVIEW_REQUIRED"
            and all(language.get("gates", {}).values())
        ),
        "assistant_stratified_language_review_pass": (
            language_review.get("status") == "PASS_WITH_DISCLOSED_LIMITATIONS"
            and language_review.get("review_counts", {}).get(
                "blocking_language_defects"
            )
            == 0
        ),
        "semantic_shortcut_audit_pass": (
            semantic_shortcut.get("status") == "PASS"
            and all(semantic_shortcut.get("gates", {}).values())
        ),
        "oracle_companion_metrics_all_one": all(
            oracle.get(metric) == 1.0 for metric in oracle_metrics
        ),
        "fresh_rebuild_byte_identical": (
            determinism.get("status") == "PASS"
            and determinism.get("manifest_byte_identical") is True
            and determinism.get("byte_mismatch_count") == 0
        ),
        "streaming_220_preflight_pass": expansion.get("status") == "STATIC_PREFLIGHT_PASS",
        "streaming_220_has_no_unapproved_question_duplicates": (
            expansion.get("unapproved_exact_question_duplicates") == 0
        ),
        "streaming_220_has_no_span_id_collisions": (
            expansion.get("cross_match_public_span_id_collisions") == 0
        ),
        "full_cohort_answer_prior_gates_pass": all(
            expansion.get("full_cohort_answer_prior_diagnostic", {})
            .get("gates", {})
            .values()
        ),
        "full_cohort_stronger_question_baselines_pass": (
            expansion.get(
                "full_cohort_adversarial_question_only_diagnostic", {}
            ).get("status")
            == "PASS"
            and all(
                expansion.get(
                    "full_cohort_adversarial_question_only_diagnostic", {}
                )
                .get("gates", {})
                .values()
            )
        ),
        "full_cohort_structural_shortcut_gates_pass": (
            expansion.get("full_cohort_structural_shortcut_diagnostic", {}).get(
                "status"
            )
            == "PASS"
            and all(
                expansion.get(
                    "full_cohort_structural_shortcut_diagnostic", {}
                )
                .get("gates", {})
                .values()
            )
        ),
        "matched_anchor_control_complete": (
            confound.get("status") == "CONFOUND_DETECTED_MATCHED_CONTROL_READY"
            and all(confound.get("matched_control_gates", {}).values())
        ),
        "protocol_fault_attribution_pass": fault.get("status") == "PASS",
        "sentinel_request_ready_but_not_authorized": (
            sentinel.get("status") == "REQUEST_READY_BLOCKED_BY_AUTHORIZATION"
            and sentinel.get("execution_authorized") is False
            and all(sentinel.get("gates", {}).values())
        ),
        "diagnostic_escalation_waits_for_explicit_authorization": (
            next_action.get("next_action")
            == "AWAIT_EXPLICIT_AUTHORIZATION_FOR_UNIFORM_SENTINEL5"
        ),
        "metric_addendum_frozen_before_provider_result": (
            addendum.get("status") == "FROZEN_BEFORE_ANY_R26_14_PROVIDER_RESULT"
            and addendum.get("parent_primary_metric_unchanged") is True
        ),
        "structural_shortcut_contract_frozen_before_result": (
            payload["structural_shortcut_contract"].get("status")
            == "FROZEN_BEFORE_R26_14_STRUCTURAL_AUDIT_RESULT"
            and payload["structural_shortcut_contract"].get(
                "provider_requests_authorized"
            )
            is False
        ),
        "zero_provider_requests": all(
            item.get(key, 0) == 0
            for item, key in (
                (prior, "provider_requests_made"),
                (adversarial, "provider_requests_made"),
                (structural_shortcut, "provider_requests_made"),
                (drift, "provider_requests_made"),
                (language, "provider_requests_made"),
                (language_review, "provider_requests_made"),
                (semantic_shortcut, "provider_requests_made"),
                (determinism, "provider_requests_made"),
                (expansion, "provider_requests_made"),
                (confound, "provider_requests_made"),
                (fault, "provider_requests_made"),
                (sentinel, "provider_requests_made"),
                (next_action, "external_requests_made"),
            )
        ),
    }
    static_pass = all(static_gates.values())
    empirical = summary.get("empirical_calibration", {}).get("status") == "PASS"
    blockers = []
    if not static_pass:
        blockers.append("STATIC_GATE_FAILED")
    if language_review.get("independent_human_review_status") != "PASS":
        blockers.append("INDEPENDENT_HUMAN_NATURALNESS_REVIEW_NOT_RUN")
    if not empirical:
        blockers.extend(
            [
                "R26_14_SENTINEL5_UNIFORM_NOT_RUN",
                "R26_14_PILOT20_TWO_STRONG_MODEL_FAMILIES_NOT_RUN",
                "STRONG_MODEL_65PCT_AND_ADJACENT_8PPT_TARGETS_UNCALIBRATED",
            ]
        )

    report = {
        "protocol_version": "VETT-R26.14-STATIC-ADMISSION-1",
        "dataset_version": summary.get("dataset_version"),
        "status": (
            "STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED"
            if static_pass and not empirical
            else "FULL_ADMISSION_PASS"
            if static_pass and empirical
            else "STATIC_CANDIDATE_FAIL"
        ),
        "static_gates": static_gates,
        "static_candidate_admitted": static_pass,
        "empirical_difficulty_calibrated": empirical,
        "full_220_materialization_authorized": static_pass and empirical,
        "official_release_authorized": static_pass and empirical,
        "external_execution_authorized": sentinel.get("execution_authorized") is True,
        "next_authorized_experiment": (
            "uniform_sentinel5_one_economic_strong_model_after_explicit_user_authorization"
            if static_pass and not empirical
            else None
        ),
        "blockers": blockers,
        "key_evidence": {
            "pilot_matches": summary.get("instances"),
            "pilot_questions": summary.get("decision_questions"),
            "proof_questions_passed": proof.get("status_counts", {}).get("PASS"),
            "literal_query_top_k_evidence_recall": semantic_shortcut.get(
                "literal_query_top_k_evidence_recall"
            ),
            "question_payload_1nn_field_accuracy_20": prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("public_question_payload", {})
            .get("field_accuracy"),
            "equal_prior_nb_informative_accuracy_20": adversarial.get(
                "question_only_baselines", {}
            ).get("equal_prior_word_nb", {}).get("informative_field_accuracy"),
            "scenario_held_out_1nn_informative_accuracy_20": adversarial.get(
                "question_only_baselines", {}
            ).get("scenario_family_held_out_1nn", {}).get(
                "informative_field_accuracy"
            ),
            "counterfactual_marker_top1_locator_accuracy_20": adversarial.get(
                "counterfactual_instruction_locator", {}
            ).get("top1_query_plus_marker_locator_accuracy"),
            "counterfactual_marker_only_decisive_span_recall_20": adversarial.get(
                "counterfactual_instruction_locator", {}
            ).get("mean_marker_only_decisive_span_recall"),
            "bm25_positive_evidence_recall_at_gold_k_20": structural_shortcut.get(
                "bm25_question_to_evidence", {}
            ).get("positive_recall_at_gold_k"),
            "bm25_non_entry_positive_evidence_recall_at_gold_k_20": structural_shortcut.get(
                "bm25_question_to_evidence", {}
            ).get(
                "non_entry_positive_recall_at_gold_k_after_removing_marker_and_semantic_bridge_spans"
            ),
            "question_only_topology_signature_exact_20": structural_shortcut.get(
                "question_only_topology_prior", {}
            ).get("typed_relation_count_signature_exact"),
            "public_numeric_level_macro_f1_20": structural_shortcut.get(
                "public_numeric_level_confound", {}
            ).get("leave_one_match_out_macro_f1"),
            "question_payload_1nn_informative_accuracy_20": prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("public_question_payload", {})
            .get("informative_field_accuracy"),
            "question_payload_1nn_full_record_exact_20": prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("public_question_payload", {})
            .get("full_record_exact"),
            "unconditional_field_prior_accuracy": prior.get("baselines", {})
            .get("unconditional", {})
            .get("field_accuracy"),
            "streamed_matches": expansion.get("matches_planned"),
            "streamed_questions": expansion.get("questions_audited"),
            "full_cohort_question_payload_1nn_field_accuracy": expansion.get(
                "full_cohort_answer_prior_diagnostic", {}
            ).get("question_payload_nearest_neighbor", {}).get("field_accuracy"),
            "full_cohort_question_payload_1nn_informative_accuracy": expansion.get(
                "full_cohort_answer_prior_diagnostic", {}
            ).get("question_payload_nearest_neighbor", {}).get(
                "informative_field_accuracy"
            ),
            "full_cohort_equal_prior_nb_informative_accuracy": expansion.get(
                "full_cohort_adversarial_question_only_diagnostic", {}
            ).get("baselines", {}).get("equal_prior_word_nb", {}).get(
                "informative_field_accuracy"
            ),
            "full_cohort_scenario_held_out_1nn_informative_accuracy": expansion.get(
                "full_cohort_adversarial_question_only_diagnostic", {}
            ).get("baselines", {}).get(
                "scenario_family_held_out_1nn", {}
            ).get("informative_field_accuracy"),
            "pilot_equal_prior_nb_highest_informative_field": adversarial.get(
                "field_signal_diagnostics", {}
            ).get("equal_prior_word_nb", {}).get("highest_informative_field"),
            "pilot_equal_prior_nb_highest_informative_field_value_balanced_accuracy": adversarial.get(
                "field_signal_diagnostics", {}
            ).get("equal_prior_word_nb", {}).get(
                "highest_informative_field_value_balanced_accuracy"
            ),
            "full_cohort_equal_prior_nb_highest_informative_field": expansion.get(
                "full_cohort_adversarial_question_only_diagnostic", {}
            ).get("field_signal_diagnostics", {}).get(
                "equal_prior_word_nb", {}
            ).get("highest_informative_field"),
            "full_cohort_equal_prior_nb_highest_informative_field_value_balanced_accuracy": expansion.get(
                "full_cohort_adversarial_question_only_diagnostic", {}
            ).get("field_signal_diagnostics", {}).get(
                "equal_prior_word_nb", {}
            ).get("highest_informative_field_value_balanced_accuracy"),
            "full_cohort_counterfactual_marker_top1_locator_accuracy": expansion.get(
                "full_cohort_counterfactual_locator_diagnostic", {}
            ).get("top1_query_plus_marker_locator_accuracy"),
            "full_cohort_bm25_non_entry_positive_evidence_recall_at_gold_k": expansion.get(
                "full_cohort_structural_shortcut_diagnostic", {}
            ).get("bm25_question_to_evidence", {}).get(
                "non_entry_positive_recall_at_gold_k_after_removing_marker_and_semantic_bridge_spans"
            ),
            "full_cohort_question_only_topology_signature_exact": expansion.get(
                "full_cohort_structural_shortcut_diagnostic", {}
            ).get("question_only_topology_prior", {}).get(
                "typed_relation_count_signature_exact"
            ),
            "full_cohort_public_numeric_level_macro_f1": expansion.get(
                "full_cohort_structural_shortcut_diagnostic", {}
            ).get("public_numeric_level_confound", {}).get(
                "leave_one_match_out_macro_f1"
            ),
            "unapproved_exact_question_duplicates": expansion.get(
                "unapproved_exact_question_duplicates"
            ),
            "approved_duplicate_control_questions": expansion.get(
                "approved_duplicate_control_questions"
            ),
            "byte_mismatch_count": determinism.get("byte_mismatch_count"),
            "sentinel5_estimated_zero_cache_cost_cny": sentinel.get(
                "estimated_cost_cny_zero_cache"
            ),
            "sentinel5_maximum_context_utilization": sentinel.get(
                "maximum_context_utilization_upper_bound"
            ),
            "sentinel5_minimum_oracle_output_headroom_ratio": sentinel.get(
                "minimum_oracle_output_headroom_ratio"
            ),
            "provider_requests_made": 0,
        },
        "input_fingerprints": {
            name: {"path": str(path), "sha256": _sha256(path)}
            for name, path in paths.items()
        },
        "claim_boundary": (
            "Static admission establishes deterministic construction, factual/proof "
            "invariants, shortcut controls, evaluator sensitivity, matched-anchor coverage "
            "and request safety. It does not establish strong-model accuracy, empirical "
            "adjacent-level gaps, human naturalness or publication readiness."
        ),
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_md = output_json.with_suffix(".md")
    lines = [
        "# R26.14 static admission",
        "",
        f"- Status: `{report['status']}`",
        f"- Static candidate admitted: `{report['static_candidate_admitted']}`",
        f"- Empirical difficulty calibrated: `{report['empirical_difficulty_calibrated']}`",
        f"- Full 220 materialization authorized: `{report['full_220_materialization_authorized']}`",
        f"- Next authorized experiment: `{report['next_authorized_experiment']}`",
        "",
        "## Static gates",
        "",
        *[f"- {name}: `{value}`" for name, value in static_gates.items()],
        "",
        "## Remaining blockers",
        "",
        *[f"- `{item}`" for item in blockers],
        "",
        "## Claim boundary",
        "",
        report["claim_boundary"],
        "",
    ]
    output_md.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-answer-blind-admission")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--metric-addendum", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_answer_blind_admission(
        args.release, args.analysis, args.metric_addendum, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_answer_blind_admission"]
