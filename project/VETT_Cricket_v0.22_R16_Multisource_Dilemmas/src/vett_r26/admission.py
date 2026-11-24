from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from vett_eval.runner import estimate_config

from .auditor import audit_release
from .evaluation import score_predictions


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_admission_report(
    *,
    release_dir: Path,
    ledger_audit_path: Path,
    stability_audit_path: Path,
    shortcut_audit_path: Path,
    expansion_plan_path: Path,
    expansion_input_audit_path: Path,
    adjustment_registry_audit_path: Path,
    oracle_predictions_path: Path,
    cohort_index_path: Path,
    pending_eval_config_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    static = audit_release(release_dir)
    ledger = _read(ledger_audit_path)
    stability = _read(stability_audit_path)
    shortcut = _read(shortcut_audit_path)
    expansion = _read(expansion_plan_path)
    expansion_inputs = _read(expansion_input_audit_path)
    adjustment_registry = _read(adjustment_registry_audit_path)
    cohort_index = _read(cohort_index_path)
    estimate = estimate_config(pending_eval_config_path)
    oracle = score_predictions(release_dir, oracle_predictions_path)
    cohort = cohort_index["cohorts"][0]

    oracle_fields = {
        key: oracle[key]
        for key in (
            "factual_record_macro_accuracy",
            "counterfactual_field_accuracy",
            "latent_state_accuracy",
            "minimal_evidence_f1",
            "rejected_evidence_f1",
            "minimal_evidence_edge_f1",
            "evidence_chain_joint_exact",
            "factual_evidence_chain_joint_exact",
        )
    }
    checks = {
        "release_static_semantics": static["status"] == "PASS",
        "difficulty_ledger_reproduces": (
            ledger["status"] == "PASS"
            and ledger["difficulty_vector_reproduction_errors"] == 0
        ),
        "pre220_structural_stability": stability["status"] == "READY_FOR_220",
        "shortcut_resistance": shortcut["status"] == "PASS",
        "oracle_scoring_closure": all(value == 1.0 for value in oracle_fields.values()),
        "balanced_220_private_allocation": expansion["audit"]["status"] == "PASS",
        "preregistered_adjustment_policy": adjustment_registry["status"] == "PASS",
    }
    structural_pass = all(checks.values())
    request_equivalent_members = sum(
        member.get("request_equivalence", {}).get("status") == "PASS"
        for member in cohort.get("member_reports", [])
    )
    empirical_complete = (
        cohort.get("status") == "COMPLETE_COHORT"
        and cohort.get("frozen_metric_gate") is not None
    )
    difficulty_permitted = bool(
        empirical_complete
        and cohort["frozen_metric_gate"].get(
            "difficulty_conclusion_permitted", False
        )
    )
    full_generation_blockers: list[str] = []
    if not structural_pass:
        full_generation_blockers.append("PRE220_STRUCTURAL_DESIGN_GATE")
    if expansion_inputs["status"] != "READY":
        full_generation_blockers.append("SEMANTIC_BASE_COVERAGE")
    if not empirical_complete:
        full_generation_blockers.append("INCOMPLETE_SENTINEL5")
    if not difficulty_permitted:
        full_generation_blockers.append("DIFFICULTY_CONCLUSION_NOT_PERMITTED")
    # This report has no registered pair of complete Pilot20 cohorts from
    # distinct strong-model families.  Sentinel5 can screen, never authorize
    # full expansion by itself.
    cross_family_pilot20_complete = False
    if not cross_family_pilot20_complete:
        full_generation_blockers.append("PILOT20_TWO_STRONG_MODEL_FAMILIES")
    report = {
        "protocol_version": "VETT-R26-ADMISSION-1",
        "dataset_version": summary["dataset_version"],
        "difficulty_design_revision": summary["difficulty_design_revision"],
        "checks": checks,
        "pre220_structural_design_gate": "PASS" if structural_pass else "BLOCKED",
        "difficulty_design_admission": "PASS" if structural_pass else "BLOCKED",
        "full_220_generation_input_readiness": expansion_inputs["status"],
        "full_220_generation_authorized": not full_generation_blockers,
        "full_220_generation_blockers": full_generation_blockers,
        "cross_family_pilot20_complete": cross_family_pilot20_complete,
        "empirical_calibration": {
            "status": "COMPLETE" if empirical_complete else "INCOMPLETE_SENTINEL5",
            "cohort_status": cohort["status"],
            "collected_instances": cohort["collected_instances"],
            "expected_instances": cohort["expected_instances"],
            "request_equivalent_historical_members": request_equivalent_members,
            "difficulty_conclusion_permitted": difficulty_permitted,
        },
        "oracle_closure_metrics": oracle_fields,
        "structural_stability": {
            "mean_adjacent_deltas": {
                pair: row["mean_structural_delta"]
                for pair, row in stability["transition_summary"].items()
            },
            "negative_transition_shares": {
                pair: row["negative_structural_delta_share"]
                for pair, row in stability["transition_summary"].items()
            },
            "minimum_anchor_transition": min(
                value
                for transitions in stability["anchor_transition_summary"].values()
                for value in transitions.values()
            ),
            "unique_difficulty_vector_ratio": stability[
                "unique_difficulty_vector_ratio"
            ],
        },
        "expansion_allocation": {
            "matches": expansion["audit"]["matches"],
            "assignments": expansion["audit"]["assignments"],
            "blocks": expansion["audit"]["blocks"],
            "per_anchor_level": expansion["audit"][
                "anchor_level_expected_count"
            ],
            "private_only": expansion["audit"]["private_only"],
        },
        "expansion_input_coverage": {
            "status": expansion_inputs["status"],
            "required_matches": expansion_inputs["required_matches"],
            "complete_matches": expansion_inputs["complete_matches"],
            "incomplete_matches": expansion_inputs["incomplete_matches"],
            "partial_generation_permitted": expansion_inputs[
                "partial_generation_permitted"
            ],
        },
        "pending_paid_collection": {
            "provider_requests_made_by_this_report": 0,
            "instances": estimate["runs"][0]["instances"],
            "targets": estimate["runs"][0]["targets"],
            "zero_cache_estimate_cny": estimate[
                "estimated_total_cost_cny_zero_cache"
            ],
            "configured_estimate_ceiling_cny": estimate[
                "configured_total_cost_ceiling_cny"
            ],
            "post_instance_stop_threshold_cny": _read(
                pending_eval_config_path
            )["runs"][0]["max_actual_cost_cny"],
            "requires_explicit_user_approval": True,
        },
        "release_state": {
            "pilot_candidate_built": True,
            "full_220_dataset_built": False,
            "full_220_semantic_base_ready": expansion_inputs["status"] == "READY",
            "strong_model_five_level_separation_proven": False,
            "publication_ready": False,
        },
        "claim_boundary": [
            "Structural PASS authorizes controlled generation work only.",
            "Oracle closure validates gold and scoring, not model difficulty.",
            "The private 220 allocation is a plan, not generated instances.",
            "Full generation is blocked until all 220 matches have complete semantic-base bundles; partial generation is forbidden.",
            "No strong-model difficulty claim is permitted until a complete valid Sentinel5, followed by the preregistered Pilot20 panel.",
        ],
    }
    _write_json(output_dir / "R26_12_ADMISSION_REPORT.json", report)
    lines = [
        "# R26.12 admission report",
        "",
        f"- Dataset: `{report['dataset_version']}`",
        f"- Pre-220 structural design gate: **{report['pre220_structural_design_gate']}**",
        f"- Full 220 semantic-base readiness: **{report['full_220_generation_input_readiness']}** "
        f"({expansion_inputs['complete_matches']}/{expansion_inputs['required_matches']} matches)",
        f"- Empirical calibration: **{report['empirical_calibration']['status']}** "
        f"({cohort['collected_instances']}/{cohort['expected_instances']} instances)",
        "- Full 220 dataset built: **NO**",
        "- Publication ready: **NO**",
        "",
        "## Structural evidence",
        "",
    ]
    lines.extend(
        f"- {name}: {'PASS' if passed else 'FAIL'}"
        for name, passed in checks.items()
    )
    lines.extend([
        "",
        "## Claim boundary",
        "",
    ])
    lines.extend(f"- {value}" for value in report["claim_boundary"])
    lines.extend([
        "",
        "## Pending paid step (not executed)",
        "",
        f"Four instances / 20 questions; conservative zero-cache estimate "
        f"¥{estimate['estimated_total_cost_cny_zero_cache']:.4f}; configured "
        f"post-instance cost stop threshold "
        f"¥{report['pending_paid_collection']['post_instance_stop_threshold_cny']:.2f}. "
        "Execution requires explicit approval.",
        "",
    ])
    (output_dir / "R26_12_ADMISSION_REPORT.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-admission")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--ledger-audit", type=Path, required=True)
    parser.add_argument("--stability-audit", type=Path, required=True)
    parser.add_argument("--shortcut-audit", type=Path, required=True)
    parser.add_argument("--expansion-plan", type=Path, required=True)
    parser.add_argument("--expansion-input-audit", type=Path, required=True)
    parser.add_argument("--adjustment-registry-audit", type=Path, required=True)
    parser.add_argument("--oracle-predictions", type=Path, required=True)
    parser.add_argument("--cohort-index", type=Path, required=True)
    parser.add_argument("--pending-eval-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_admission_report(
        release_dir=args.release,
        ledger_audit_path=args.ledger_audit,
        stability_audit_path=args.stability_audit,
        shortcut_audit_path=args.shortcut_audit,
        expansion_plan_path=args.expansion_plan,
        expansion_input_audit_path=args.expansion_input_audit,
        adjustment_registry_audit_path=args.adjustment_registry_audit,
        oracle_predictions_path=args.oracle_predictions,
        cohort_index_path=args.cohort_index,
        pending_eval_config_path=args.pending_eval_config,
        output_dir=args.output,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_admission_report"]
