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


def build_admission_report(
    release_dir: Path,
    analysis_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Combine static evidence without silently upgrading it to model evidence."""
    request_dir = analysis_dir.parent / "r26_13_request_readiness"
    language_dir = analysis_dir.parent / "r26_13_language_surface"
    inputs = {
        "release_summary": release_dir / "RELEASE_SUMMARY.json",
        "release_audit": release_dir / "STABILITY_AUDIT.json",
        "metadata_shortcut": analysis_dir / "METADATA_SHORTCUT_AUDIT.json",
        "proof_certificate": analysis_dir / "PROOF_CERTIFICATE_AUDIT.json",
        "semantic_shortcut": analysis_dir / "SEMANTIC_SHORTCUT_AUDIT.json",
        "difficulty_ledger": analysis_dir / "difficulty_ledger" / "DIFFICULTY_LEDGER_AUDIT.json",
        "difficulty_stability": analysis_dir / "difficulty_stability" / "DIFFICULTY_STABILITY_AUDIT.json",
        "level_surface_confound": analysis_dir / "LEVEL_SURFACE_CONFOUND_AUDIT.json",
        "identifiability": analysis_dir / "IDENTIFIABILITY_ADMISSION.json",
        "adjustment_authority": analysis_dir / "ADJUSTMENT_AUTHORITY_AUDIT.json",
        "answer_prior_shortcut": analysis_dir / "ANSWER_PRIOR_SHORTCUT_AUDIT.json",
        "streaming_220": analysis_dir / "STREAMING_EXPANSION_PREFLIGHT_220.json",
        "oracle_score": analysis_dir / "ORACLE_SCORE.json",
        "determinism": analysis_dir / "DETERMINISM_CHECK.json",
        "language_surface": language_dir / "LANGUAGE_SURFACE_AUDIT.json",
        "assistant_language_review": language_dir / "ASSISTANT_STRATIFIED_LANGUAGE_REVIEW.json",
        "sentinel_zero_request": request_dir / "SENTINEL5_ZERO_REQUEST_PREFLIGHT.json",
        "protocol_fault_matrix": request_dir / "PROTOCOL_FAULT_MATRIX.json",
        "diagnostic_next_action": request_dir / "NEXT_ACTION.json",
    }
    payloads = {name: _read(path) for name, path in inputs.items()}
    summary = payloads["release_summary"]
    release_audit = payloads["release_audit"]
    metadata = payloads["metadata_shortcut"]
    proof = payloads["proof_certificate"]
    semantic = payloads["semantic_shortcut"]
    ledger = payloads["difficulty_ledger"]
    stability = payloads["difficulty_stability"]
    level_confound = payloads["level_surface_confound"]
    identifiability = payloads["identifiability"]
    adjustment_authority = payloads["adjustment_authority"]
    answer_prior = payloads["answer_prior_shortcut"]
    expansion = payloads["streaming_220"]
    oracle = payloads["oracle_score"]["score"]
    determinism = payloads["determinism"]
    language = payloads["language_surface"]
    language_review = payloads["assistant_language_review"]
    request = payloads["sentinel_zero_request"]
    fault_matrix = payloads["protocol_fault_matrix"]
    next_action = payloads["diagnostic_next_action"]

    static_gates = {
        "release_20_pass": summary.get("status") == "PASS",
        "integrated_release_audit_pass": release_audit.get("status") == "PASS",
        "metadata_shortcut_audit_pass": metadata.get("status") == "PASS",
        "proof_certificate_audit_pass": proof.get("status") == "PASS",
        "semantic_shortcut_audit_pass": semantic.get("status") == "PASS",
        "difficulty_ledger_pass": ledger.get("status") == "PASS",
        "difficulty_stability_ready": stability.get("status") == "READY_FOR_220",
        "level_surface_confound_has_complete_matched_control": (
            level_confound.get("status")
            == "CONFOUND_DETECTED_MATCHED_CONTROL_READY"
            and all(level_confound.get("matched_control_gates", {}).values())
        ),
        "static_identifiability_admission_pass": identifiability.get("status")
        == "STATIC_IDENTIFIABILITY_PASS_EMPIRICAL_REQUIRED"
        and all(identifiability.get("gates", {}).values()),
        "difficulty_adjustment_authority_is_preregistered": (
            adjustment_authority.get("status") == "PASS"
            and adjustment_authority.get("sentinel_content_mutation_permitted")
            is False
            and adjustment_authority.get("one_family_promotion_permitted")
            is False
        ),
        "question_only_factual_answer_shortcut_absent": answer_prior.get(
            "status"
        )
        == "PASS",
        "streaming_220_static_preflight_pass": expansion.get("status") == "STATIC_PREFLIGHT_PASS",
        "oracle_factual_chain_exact": oracle.get("factual_evidence_chain_joint_exact") == 1.0,
        "independent_rebuild_byte_identical": (
            determinism.get("status") == "PASS"
            and determinism.get("manifest_byte_identical") is True
        ),
        "zero_provider_requests_in_preflight": expansion.get("provider_requests_made") == 0,
        "automated_language_surface_pass": (
            language.get("status") == "AUTOMATED_PASS_HUMAN_REVIEW_REQUIRED"
            and all(language.get("gates", {}).values())
        ),
        "assistant_stratified_language_review_pass": (
            language_review.get("status") == "PASS_WITH_DISCLOSED_LIMITATIONS"
            and language_review.get("review_counts", {}).get(
                "blocking_language_defects_after_revision"
            )
            == 0
        ),
        "sentinel5_request_fail_closes_on_known_shortcut": (
            request.get("status") == "NOT_READY"
            and request.get("execution_authorized") is False
            and request.get("gates", {}).get(
                "no_question_only_factual_answer_shortcut"
            )
            is False
            and all(
                passed
                for name, passed in request.get("gates", {}).items()
                if name != "no_question_only_factual_answer_shortcut"
            )
        ),
        "protocol_fault_attribution_pass": fault_matrix.get("status") == "PASS",
        "diagnostic_escalation_stops_before_provider_spend": (
            next_action.get("next_action")
            == "STOP_AND_REPAIR_QUESTION_ONLY_ANSWER_SHORTCUT"
        ),
        "zero_external_requests_in_readiness_checks": (
            request.get("provider_requests_made") == 0
            and fault_matrix.get("provider_requests_made") == 0
            and next_action.get("external_requests_made") == 0
            and language.get("provider_requests_made") == 0
            and language_review.get("provider_requests_made") == 0
        ),
    }
    empirical = summary.get("empirical_calibration", {}).get("status") == "PASS"
    blockers = []
    if answer_prior.get("status") != "PASS":
        blockers.append("QUESTION_ONLY_FACTUAL_ANSWER_SHORTCUT")
    if not empirical:
        blockers.extend([
            "R26_13_SENTINEL5_UNIFORM_NOT_RUN",
            "R26_13_PAIRED_PROOF_ONLY_NOT_RUN",
            "R26_13_PILOT20_TWO_STRONG_MODEL_FAMILIES_NOT_RUN",
            "EMPIRICAL_DIFFICULTY_TARGETS_UNCALIBRATED",
            "MATCHED_ANCHOR_MODEL_EFFECT_NOT_RUN",
        ])
    if language_review.get("independent_human_review_status") != "PASS":
        blockers.append("INDEPENDENT_HUMAN_NATURALNESS_REVIEW_NOT_RUN")
    if not all(static_gates.values()):
        blockers.insert(0, "STATIC_ADMISSION_GATE_FAILED")

    static_pass = all(static_gates.values())
    report = {
        "protocol_version": "VETT-R26.13-MEASUREMENT-ADMISSION-1",
        "dataset_version": summary.get("dataset_version"),
        "status": (
            "STATIC_ADMISSION_PASS_EMPIRICAL_BLOCKED"
            if static_pass and not empirical
            else "FULL_ADMISSION_PASS"
            if static_pass and empirical
            else "STATIC_ADMISSION_FAIL"
        ),
        "static_gates": static_gates,
        "static_constructability_20": static_pass,
        "static_constructability_220": static_pass,
        "empirical_difficulty_calibrated": empirical,
        "full_220_materialization_authorized": static_pass and empirical,
        "official_release_authorized": static_pass and empirical,
        "next_authorized_experiment": (
            "uniform_sentinel5_one_economic_strong_model_after_explicit_user_authorization"
            if static_pass and not empirical
            else "build_versioned_shadow_candidate_repairing_answer_prior_shortcut"
            if answer_prior.get("status") != "PASS"
            else None
        ),
        "external_execution_authorized": request.get("execution_authorized") is True,
        "blockers": blockers,
        "key_evidence": {
            "pilot_matches": summary.get("instances"),
            "pilot_questions": summary.get("decision_questions"),
            "proof_questions_passed": proof.get("status_counts", {}).get("PASS", 0),
            "metadata_span_id_macro_f1": metadata.get("baselines", {}).get(
                "span_identifier_morphology", {}
            ).get("leave_one_match_out_macro_f1"),
            "streamed_matches": expansion.get("matches_planned"),
            "streamed_questions": expansion.get("questions_audited"),
            "global_public_span_ids": expansion.get("global_public_span_ids"),
            "cross_match_public_span_id_collisions": expansion.get(
                "cross_match_public_span_id_collisions"
            ),
            "mean_structural_load_by_level": expansion.get(
                "mean_structural_load_by_level"
            ),
            "mean_adjacent_structural_deltas": expansion.get(
                "mean_adjacent_structural_deltas"
            ),
            "within_match_nonpositive_transition_shares": expansion.get(
                "within_match_nonpositive_transition_shares"
            ),
            "question_only_level_macro_f1": level_confound.get(
                "question_only_baseline", {}
            ).get("leave_one_match_out_macro_f1"),
            "intervention_only_level_macro_f1": level_confound.get(
                "intervention_only_baseline", {}
            ).get("leave_one_match_out_macro_f1"),
            "matched_anchor_level_cell_counts": level_confound.get(
                "anchor_level_cell_counts"
            ),
            "static_identifiability_status": identifiability.get("status"),
            "sentinel_content_mutation_permitted": adjustment_authority.get(
                "sentinel_content_mutation_permitted"
            ),
            "question_only_1nn_field_accuracy": answer_prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("question", {})
            .get("field_accuracy"),
            "question_only_1nn_full_record_exact": answer_prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("question", {})
            .get("full_record_exact"),
            "unconditional_field_prior_accuracy": answer_prior.get("baselines", {})
            .get("unconditional", {})
            .get("field_accuracy"),
            "oracle_factual_evidence_chain_joint_exact": oracle.get(
                "factual_evidence_chain_joint_exact"
            ),
            "provider_requests_made": expansion.get("provider_requests_made"),
            "sentinel5_estimated_cost_cny_zero_cache": request.get(
                "estimated_cost_cny_zero_cache"
            ),
            "sentinel5_minimum_oracle_output_headroom_ratio": request.get(
                "minimum_oracle_output_headroom_ratio"
            ),
            "assistant_language_review_status": language_review.get("status"),
            "independent_human_review_status": language_review.get(
                "independent_human_review_status"
            ),
        },
        "input_fingerprints": {
            name: {"path": str(path), "sha256": _sha256(path)}
            for name, path in inputs.items()
        },
        "claim_boundary": (
            "Static admission proves deterministic constructability, invariants, "
            "shortcut controls, matched-anchor identifiability and evaluator self-consistency only when all gates pass. "
            "Public intervention wording still predicts private levels above chance, so "
            "model level effects must also be reported inside the matched anchor design. "
            "R26.13 currently fails because public question wording predicts factual records without dossier documents. It does not establish "
            "strong-model accuracy, adjacent empirical gaps or publication readiness."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "MEASUREMENT_ADMISSION.json"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# R26.13 measurement admission",
        "",
        f"- Status: `{report['status']}`",
        f"- Static 20-match constructability: `{report['static_constructability_20']}`",
        f"- Static 220-match constructability: `{report['static_constructability_220']}`",
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
    (output_dir / "MEASUREMENT_ADMISSION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-measurement-admission")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_admission_report(args.release, args.analysis, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_admission_report"]
