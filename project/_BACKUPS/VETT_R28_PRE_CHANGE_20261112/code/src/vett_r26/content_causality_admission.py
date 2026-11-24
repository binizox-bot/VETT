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


def build_content_causality_admission(
    candidate_dir: Path,
    prior_admission_path: Path,
    causality_report_path: Path,
    sensitivity_report_path: Path,
    expansion_report_path: Path,
    causality_contract_path: Path,
    metric_contract_path: Path,
) -> dict[str, Any]:
    prior = _read(prior_admission_path)
    causality = _read(causality_report_path)
    sensitivity = _read(sensitivity_report_path)
    expansion = _read(expansion_report_path)
    manifest_path = candidate_dir / "MANIFEST.json"
    manifest_sha = _sha256(manifest_path)
    expected_manifest_sha = str(
        prior["input_fingerprints"]["candidate_manifest"]["sha256"]
    )
    gates = {
        "prior_static_admission_remains_passed": prior["status"]
        == "STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED"
        and all(prior["gates"].values()),
        "candidate_manifest_unchanged": manifest_sha == expected_manifest_sha,
        "pilot_content_causality_certified": causality["status"]
        == "PASS_WITH_MEASUREMENT_WARNINGS"
        and all(causality["gates"].values()),
        "content_metric_mutations_all_detected": sensitivity["status"] == "PASS"
        and all(sensitivity["gates"].values()),
        "full_220_streaming_causality_certified": expansion["status"]
        == "STATIC_PREFLIGHT_PASS"
        and expansion["static_gates"][
            "full_cohort_content_causality_certified"
        ],
        "full_220_counts_exact": (
            expansion["content_causality_instances_passed"] == 220
            and expansion["content_causality_exact_questions"] == 1100
            and expansion["content_causality_expected_edges"] == 3564
            and expansion["content_causality_public_semantic_edges"] == 3564
        ),
        "no_provider_requests_made": sum(
            int(value)
            for value in (
                prior["provider_requests_made"],
                causality["provider_requests"],
                sensitivity["provider_requests"],
                expansion["provider_requests_made"],
            )
        )
        == 0,
    }
    return {
        "protocol_version": "VETT-R26.15-CAUSAL-MEASUREMENT-ADMISSION-1",
        "status": (
            "STATIC_CAUSAL_MEASUREMENT_PASS_EMPIRICAL_BLOCKED"
            if all(gates.values())
            else "STATIC_CAUSAL_MEASUREMENT_FAIL"
        ),
        "gates": gates,
        "data_change_decision": {
            "decision": "NO_R26_16_DATASET_MUTATION",
            "reason": (
                "All 324 pilot and 3,564 planned full-cohort content edges match "
                "the independently implemented input/output certificate. The "
                "reproducible defect is measurement masking and opportunity "
                "imbalance, which is repaired by additive reporting metrics. "
                "Changing facts, text or gold edges would not be evidence-based."
            ),
            "candidate_dataset_version_unchanged": True,
        },
        "pilot": {
            "matches": causality["counts"]["matches"],
            "questions": causality["counts"]["questions"],
            "scenario_families": causality["counts"]["scenario_families"],
            "certified_content_edges": causality["counts"][
                "independently_reconstructed_content_edges"
            ],
            "public_semantic_anchor_edges": causality["counts"][
                "public_semantic_anchor_edges"
            ],
            "content_opportunity_level_ratio": causality["opportunity"][
                "maximum_to_minimum_level_mean_ratio"
            ],
            "all_content_omitted_overall_edge_f1": causality["masking_probe"]
            ["omit_content_edges"]["overall_edge_f1"],
            "all_content_omitted_content_edge_f1": causality["masking_probe"]
            ["omit_content_edges"]["content_edge_f1"],
        },
        "full_cohort": {
            "matches": expansion["content_causality_instances_passed"],
            "questions": expansion["content_causality_exact_questions"],
            "certified_content_edges": expansion[
                "content_causality_expected_edges"
            ],
            "public_semantic_anchor_edges": expansion[
                "content_causality_public_semantic_edges"
            ],
            "materialized": expansion["full_candidate_materialized"],
            "streamed_candidate_artifact_sha256": expansion[
                "streamed_candidate_artifact_sha256"
            ],
        },
        "input_fingerprints": {
            "candidate_manifest": {"path": str(manifest_path), "sha256": manifest_sha},
            "prior_admission": {
                "path": str(prior_admission_path),
                "sha256": _sha256(prior_admission_path),
            },
            "causality_report": {
                "path": str(causality_report_path),
                "sha256": _sha256(causality_report_path),
            },
            "sensitivity_report": {
                "path": str(sensitivity_report_path),
                "sha256": _sha256(sensitivity_report_path),
            },
            "expansion_report": {
                "path": str(expansion_report_path),
                "sha256": _sha256(expansion_report_path),
            },
            "causality_contract": {
                "path": str(causality_contract_path),
                "sha256": _sha256(causality_contract_path),
            },
            "metric_contract": {
                "path": str(metric_contract_path),
                "sha256": _sha256(metric_contract_path),
            },
        },
        "claim_boundary": (
            "This admits R26.15 as an internally consistent static causal-graph "
            "candidate with sensitive reporting metrics. It does not establish "
            "independent human agreement, a <=65% strong-model score, adjacent "
            "empirical gaps, or permission to publish/materialize 220 matches."
        ),
        "next_empirical_boundary": prior["next_empirical_boundary"],
        "provider_requests_made": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--prior-admission", type=Path, required=True)
    parser.add_argument("--causality-report", type=Path, required=True)
    parser.add_argument("--sensitivity-report", type=Path, required=True)
    parser.add_argument("--expansion-report", type=Path, required=True)
    parser.add_argument("--causality-contract", type=Path, required=True)
    parser.add_argument("--metric-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_content_causality_admission(
        args.candidate,
        args.prior_admission,
        args.causality_report,
        args.sensitivity_report,
        args.expansion_report,
        args.causality_contract,
        args.metric_contract,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
