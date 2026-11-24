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


def build_identifiability_admission(
    analysis_dir: Path,
    request_dir: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    inputs = {
        "level_confound": analysis_dir / "LEVEL_SURFACE_CONFOUND_AUDIT.json",
        "proof": analysis_dir / "PROOF_CERTIFICATE_AUDIT.json",
        "oracle": analysis_dir / "ORACLE_SCORE.json",
        "expansion": analysis_dir / "STREAMING_EXPANSION_PREFLIGHT_220.json",
        "sentinel": request_dir / "SENTINEL5_ZERO_REQUEST_PREFLIGHT.json",
        "fault_matrix": request_dir / "PROTOCOL_FAULT_MATRIX.json",
        "answer_prior": analysis_dir / "ANSWER_PRIOR_SHORTCUT_AUDIT.json",
    }
    data = {name: _read(path) for name, path in inputs.items()}
    confound = data["level_confound"]
    proof = data["proof"]
    oracle = data["oracle"]["score"]
    expansion = data["expansion"]
    sentinel = data["sentinel"]
    fault = data["fault_matrix"]
    answer_prior = data["answer_prior"]
    anchor_oracle = oracle.get("cross_level_anchor_diagnostic", {})
    semantic_faults = [
        case for case in fault.get("cases", [])
        if case.get("expected_layer") == "semantic"
    ]
    gates = {
        "level_surface_confound_explicitly_measured": confound.get(
            "confound_detected"
        )
        is True,
        "pilot20_anchor_control_complete": confound.get("status")
        == "CONFOUND_DETECTED_MATCHED_CONTROL_READY"
        and all(confound.get("matched_control_gates", {}).values()),
        "sentinel5_anchor_latin_square_complete": sentinel.get("gates", {}).get(
            "complete_anchor_by_level_latin_square"
        )
        is True,
        "oracle_anchor_diagnostic_complete": anchor_oracle.get("status")
        == "COMPLETE_MATCHED_CONTROL",
        "registered_and_public_surface_proofs_unique": proof.get("status")
        == "PASS"
        and proof.get("unique_registered_proof_passes") == proof.get("questions")
        and proof.get("unique_public_surface_proof_passes")
        == proof.get("questions"),
        "semantic_metric_fault_fingerprints_separate": len(semantic_faults) >= 4
        and all(case.get("sensitivity_fingerprint_pass") for case in semantic_faults),
        "question_only_factual_answer_shortcut_absent": answer_prior.get("status")
        == "PASS",
        "full220_anchor_cells_balanced": expansion.get("static_gates", {}).get(
            "five_by_five_anchor_level_cells_balanced"
        )
        is True,
        "full220_structural_inversion_rate_within_contract": expansion.get(
            "static_gates", {}
        ).get("within_match_inversion_shares_meet_frozen_contract")
        is True,
        "zero_provider_requests": all(
            payload.get("provider_requests_made") == 0
            for payload in (confound, answer_prior, expansion, sentinel, fault)
        ),
    }
    inversions = expansion.get(
        "within_match_nonpositive_transition_examples", {}
    )
    report = {
        "protocol_version": "VETT-R26.13-IDENTIFIABILITY-ADMISSION-1",
        "status": "STATIC_IDENTIFIABILITY_PASS_EMPIRICAL_REQUIRED"
        if all(gates.values())
        else "STATIC_IDENTIFIABILITY_FAIL",
        "gates": gates,
        "measured_confound": {
            "question_only_level_macro_f1": confound[
                "question_only_baseline"
            ]["leave_one_match_out_macro_f1"],
            "intervention_only_level_macro_f1": confound[
                "intervention_only_baseline"
            ]["leave_one_match_out_macro_f1"],
            "question_prefix_level_macro_f1": confound[
                "question_prefix_without_intervention_baseline"
            ]["leave_one_match_out_macro_f1"],
            "interpretation": confound["claim_boundary"],
        },
        "answer_prior_shortcut": {
            "status": answer_prior.get("status"),
            "unconditional_field_accuracy": answer_prior.get("baselines", {})
            .get("unconditional", {})
            .get("field_accuracy"),
            "question_only_1nn_field_accuracy": answer_prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("question", {})
            .get("field_accuracy"),
            "question_only_1nn_full_record_exact": answer_prior.get("baselines", {})
            .get("question_surface_nearest_neighbor", {})
            .get("question", {})
            .get("full_record_exact"),
            "anchor_level_exact_record_purity": answer_prior.get(
                "anchor_level_exact_record_purity"
            ),
        },
        "matched_design": {
            "pilot20_count_per_anchor_level_cell": sorted(
                {
                    value
                    for levels in confound["anchor_level_cell_counts"].values()
                    for value in levels.values()
                }
            ),
            "sentinel5_count_per_anchor_level_cell": sorted(
                {
                    value
                    for levels in sentinel["matched_anchor_design"][
                        "cell_counts"
                    ].values()
                    for value in levels.values()
                }
            ),
        },
        "metric_sensitivity": {
            "semantic_single_fault_cases": len(semantic_faults),
            "all_sensitivity_fingerprints_pass": all(
                case.get("sensitivity_fingerprint_pass")
                for case in semantic_faults
            ),
            "warning": (
                "One missing edge changes micro edge F1 only slightly; question-exact "
                "and factual-plus-chain exact are required companion metrics."
            ),
        },
        "structural_transition_risk": {
            "counts": expansion.get(
                "within_match_nonpositive_transition_counts", {}
            ),
            "axis_counts": expansion.get(
                "within_match_nonpositive_transition_axis_counts", {}
            ),
            "example_count": sum(len(rows) for rows in inversions.values()),
            "interpretation": (
                "The 19 L4-L5 nonpositive structural transitions are disclosed, "
                "concentrate on lower temporal and counterfactual load in one L5 "
                "scenario, and remain below the preregistered 10% ceiling. They must "
                "not be edited solely to improve a hand-built index; empirical matched "
                "errors determine whether an item-level revision is justified."
            ),
        },
        "provider_requests_made": 0,
        "publication_requirements_remaining": [
            "versioned repair of the question-only factual-answer shortcut",
            "valid Sentinel5 uniform model outputs",
            "anchor-balanced and unadjusted empirical level curves",
            "Pilot20 results from two strong model families",
            "independent human naturalness review",
        ],
        "claim_boundary": (
            "Static identifiability now fail-closes on metadata, surface-proof, "
            "design-balance and no-document factual-answer shortcuts. It does not "
            "demonstrate strong-model difficulty without model observations."
        ),
        "input_fingerprints": {
            name: {"path": str(path), "sha256": _sha256(path)}
            for name, path in inputs.items()
        },
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-identifiability-admission")
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_identifiability_admission(
        args.analysis, args.request, args.output
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_identifiability_admission"]
