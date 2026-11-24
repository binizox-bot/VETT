from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .content_dependency import audit_content_dependency_feasibility
from .content_dependency_audit import audit_content_dependency_release
from .content_dependency_release import verify_content_dependency_determinism
from .evaluation import score_predictions
from .structural_shortcut_audit import audit_structural_shortcuts


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_content_dependency_admission(
    parent_release: Path,
    candidate_release: Path,
    dependency_contract_path: Path,
    structural_contract_path: Path,
    oracle_predictions_path: Path,
    expansion_preflight_path: Path,
    sentinel_preflight_path: Path,
) -> dict[str, Any]:
    feasibility = audit_content_dependency_feasibility(
        parent_release, dependency_contract_path
    )
    release = audit_content_dependency_release(
        parent_release, candidate_release, dependency_contract_path
    )
    structural = audit_structural_shortcuts(
        candidate_release, structural_contract_path
    )
    oracle = score_predictions(candidate_release, oracle_predictions_path)
    determinism = verify_content_dependency_determinism(
        parent_release, candidate_release, dependency_contract_path
    )
    expansion = _read(expansion_preflight_path)
    sentinel = _read(sentinel_preflight_path)
    role_oracle = structural["role_oracle_topology_reconstructability"]
    gates = {
        "private_feasibility_passes": feasibility["status"] == "FEASIBLE"
        and all(feasibility["gates"].values()),
        "narrow_release_audit_passes": release["status"] == "PASS"
        and all(release["gates"].values()),
        "structural_shortcut_audit_passes": structural["status"] == "PASS"
        and all(structural["gates"].values()),
        "role_only_template_cannot_reconstruct_complete_graph": (
            role_oracle["edge_exact"] == 0.0
        ),
        "all_pilot_interventions_linked": (
            release["intervention_linked_questions"]
            == release["questions"]
            == 100
        ),
        "pilot_content_edges_match_frozen_unique_set": (
            release["content_dependency_edges"]
            == release["expected_content_dependency_edges"]
            == 324
        ),
        "pilot_graph_respects_output_limit": (
            release["maximum_edges_per_question"] <= 48
        ),
        "oracle_semantic_scores_are_exact": all(
            oracle[key] == 1.0
            for key in (
                "decision_field_macro_accuracy",
                "counterfactual_full_record_exact_match",
                "minimal_evidence_edge_f1",
                "conditional_edge_link_f1",
                "factual_evidence_chain_joint_exact",
            )
        ),
        "oracle_content_dependency_group_is_exact": (
            oracle["minimal_evidence_edge_f1_by_relation_group"][
                "content_dependency"
            ]
            == 1.0
        ),
        "byte_rebuild_is_deterministic": determinism["status"] == "PASS"
        and determinism["manifest_byte_identical"] is True,
        "full_220_streaming_preflight_passes": (
            expansion["status"] == "STATIC_PREFLIGHT_PASS"
            and all(expansion["static_gates"].values())
            and expansion["content_dependency_edges"] == 3564
            and expansion[
                "content_dependency_intervention_linked_questions"
            ]
            == 1100
        ),
        "sentinel_request_is_ready_but_not_authorized": (
            sentinel["status"] == "REQUEST_READY_BLOCKED_BY_AUTHORIZATION"
            and all(sentinel["gates"].values())
            and sentinel["execution_authorized"] is False
            and sentinel["provider_requests_made"] == 0
        ),
        "no_provider_requests_made": all(
            report.get("provider_requests_made", 0) == 0
            for report in (
                feasibility,
                release,
                structural,
                determinism,
                expansion,
                sentinel,
            )
        ),
    }
    passed = all(gates.values())
    paths = {
        "dependency_contract": dependency_contract_path,
        "structural_contract": structural_contract_path,
        "parent_manifest": parent_release / "MANIFEST.json",
        "candidate_manifest": candidate_release / "MANIFEST.json",
        "oracle_predictions": oracle_predictions_path,
        "expansion_preflight": expansion_preflight_path,
        "sentinel_preflight": sentinel_preflight_path,
    }
    return {
        "protocol_version": "VETT-R26.15-STATIC-ADMISSION-1",
        "status": (
            "STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED"
            if passed
            else "STATIC_CANDIDATE_FAIL"
        ),
        "gates": gates,
        "input_fingerprints": {
            name: {"path": str(path), "sha256": _sha256(path)}
            for name, path in paths.items()
        },
        "pilot": {
            "matches": release["matches"],
            "questions": release["questions"],
            "inherited_edges": 2492,
            "content_dependency_edges": release[
                "content_dependency_edges"
            ],
            "maximum_edges_per_question": release[
                "maximum_edges_per_question"
            ],
            "role_template_edge_f1": role_oracle["edge_f1"],
            "role_template_edge_exact": role_oracle["edge_exact"],
            "manifest_sha256": _sha256(
                candidate_release / "MANIFEST.json"
            ),
        },
        "full_cohort": {
            "matches": expansion["matches_planned"],
            "questions": expansion["questions_audited"],
            "content_dependency_edges": expansion[
                "content_dependency_edges"
            ],
            "maximum_edges_per_question": expansion[
                "maximum_augmented_edges_per_question"
            ],
            "role_template_edge_f1": expansion[
                "full_cohort_structural_shortcut_diagnostic"
            ]["role_oracle_topology_reconstructability"]["edge_f1"],
            "role_template_edge_exact": expansion[
                "full_cohort_structural_shortcut_diagnostic"
            ]["role_oracle_topology_reconstructability"]["edge_exact"],
        },
        "next_empirical_boundary": {
            "experiment": "uniform_sentinel5_one_economic_strong_model",
            "execution_authorized": False,
            "model": sentinel["model"],
            "matches": sentinel["instances"],
            "questions": sentinel["questions"],
            "estimated_zero_cache_cost_cny": sentinel[
                "estimated_cost_cny_zero_cache"
            ],
            "maximum_context_utilization_upper_bound": sentinel[
                "maximum_context_utilization_upper_bound"
            ],
            "minimum_oracle_output_headroom_ratio": sentinel[
                "minimum_oracle_output_headroom_ratio"
            ],
            "provider_requests_made": sentinel["provider_requests_made"],
        },
        "oracle_summary": {
            key: oracle[key]
            for key in (
                "decision_field_macro_accuracy",
                "counterfactual_full_record_exact_match",
                "minimal_evidence_edge_f1",
                "conditional_edge_link_f1",
                "factual_evidence_chain_joint_exact",
            )
        },
        "determinism": determinism,
        "provider_requests_made": 0,
        "claim_boundary": (
            "Admission proves static consistency, uniqueness of the registered "
            "intervention-to-rule graph, deterministic construction and 220-match "
            "constructability. It does not estimate model accuracy, prove adjacent "
            "empirical level gaps, or authorize publication claims. A preregistered "
            "multi-model sentinel remains required for empirical admission."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vett-r26-content-dependency-admission"
    )
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--dependency-contract", type=Path, required=True)
    parser.add_argument("--structural-contract", type=Path, required=True)
    parser.add_argument("--oracle-predictions", type=Path, required=True)
    parser.add_argument("--expansion-preflight", type=Path, required=True)
    parser.add_argument("--sentinel-preflight", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_content_dependency_admission(
        args.parent,
        args.candidate,
        args.dependency_contract,
        args.structural_contract,
        args.oracle_predictions,
        args.expansion_preflight,
        args.sentinel_preflight,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(
        0
        if report["status"] == "STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED"
        else 2
    )


if __name__ == "__main__":
    main()


__all__ = ["audit_content_dependency_admission"]
