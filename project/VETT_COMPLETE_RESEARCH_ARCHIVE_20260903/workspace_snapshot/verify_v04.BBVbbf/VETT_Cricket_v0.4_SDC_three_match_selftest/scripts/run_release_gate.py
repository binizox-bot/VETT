#!/usr/bin/env python3
"""Aggregate mechanical and scientific release gates for VETT-Cricket."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def gate(
    gates: list[dict[str, Any]],
    gate_id: str,
    passed: bool,
    observed: Any,
    requirement: str,
    category: str,
    blocker: bool = True,
) -> None:
    gates.append(
        {
            "gate_id": gate_id,
            "category": category,
            "blocker": blocker,
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
            "requirement": requirement,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-repeated-sentence-rate", type=float, default=0.60)
    args = parser.parse_args()

    project = args.project
    validation = project / "validation"
    data = project / "data"
    generation = project / "generation"
    baselines = project / "baselines"
    gates: list[dict[str, Any]] = []

    construction = load_json(validation / "full_validation_report.json")
    deep = load_json(validation / "deep_cricket_audit.json")
    schemas = load_json(validation / "json_schema_validation.json")
    leakage = load_json(validation / "leakage_scope_audit.json")
    mutations = load_json(validation / "scorer_mutation_test.json")
    deterministic = load_json(validation / "deterministic_rebuild_audit.json")
    blind_package = load_json(validation / "baseline_blind_package_audit.json")
    runner_selftest = load_json(validation / "baseline_runner_selftest.json")
    oracle = load_json(validation / "full_oracle_score.json")
    semantic_oracle = load_json(validation / "semantic_oracle_score.json")
    fingerprints = load_json(validation / "template_fingerprint_report.json")
    manifest = load_json(data / "manifest.json")
    instances = load_jsonl(data / "full_instances_868_candidate.jsonl")
    calibration = load_jsonl(generation / "calibration_match_0009_V2_model_naturalized.jsonl")
    support_proposals = load_jsonl(project / "annotations" / "v0_support_proposals_full.jsonl")

    gate(
        gates,
        "construction_validator",
        construction.get("status") == "PASS" and construction.get("checks_failed") == 0,
        {
            "checks": construction.get("checks_total"),
            "failures": construction.get("checks_failed"),
        },
        "all construction and provenance checks pass",
        "mechanical",
    )
    gate(
        gates,
        "deep_cricket_invariants",
        deep.get("status") == "PASS" and deep.get("blocking_failures") == 0,
        {
            "checks": deep.get("checks_total"),
            "blocking_failures": deep.get("blocking_failures"),
        },
        "all ready roots pass cricket arithmetic and cross-table invariants",
        "mechanical",
    )
    gate(
        gates,
        "json_schema",
        schemas.get("status") == "PASS" and schemas.get("failures") == 0,
        {
            "roots": schemas.get("roots"),
            "instances": schemas.get("instances"),
            "provenance_items": schemas.get("provenance_items"),
            "failures": schemas.get("failures"),
        },
        "all serialized artifacts validate against JSON Schema 2020-12",
        "mechanical",
    )
    gate(
        gates,
        "leakage_and_scope",
        leakage.get("status") == "PASS"
        and leakage.get("failures") == 0
        and leakage.get("warnings") == 0,
        {
            "checks": leakage.get("checks_total"),
            "failures": leakage.get("failures"),
            "warnings": leakage.get("warnings"),
        },
        "no split leakage, construction leakage, duplicate warning, or ambiguous V3 scope",
        "mechanical",
    )
    gate(
        gates,
        "scorer_mutations",
        mutations.get("status") == "PASS" and mutations.get("assertions_failed") == 0,
        {
            "mutation_cases": mutations.get("mutation_cases"),
            "failed": mutations.get("assertions_failed"),
        },
        "scorer detects wrong values, omissions, and hallucinations across V1-V3",
        "mechanical",
    )
    oracle_overall = oracle.get("groups", {}).get("overall", {})
    semantic_oracle_overall = semantic_oracle.get("groups", {}).get("overall", {})
    gate(
        gates,
        "oracle_round_trip",
        oracle_overall.get("cell_accuracy") == 1.0
        and oracle_overall.get("table_exact_rate") == 1.0
        and oracle_overall.get("hallucinated") == 0
        and semantic_oracle_overall.get("cell_accuracy") == 1.0
        and semantic_oracle_overall.get("table_exact_rate") == 1.0
        and semantic_oracle_overall.get("hallucinated") == 0,
        {
            "private_id_oracle": oracle_overall,
            "public_semantic_oracle": semantic_oracle_overall,
        },
        "private-ID and ID-free semantic oracles both score 100% cell accuracy and table exact match",
        "mechanical",
    )
    gate(
        gates,
        "deterministic_rebuild",
        deterministic.get("status") == "PASS"
        and deterministic.get("all_byte_identical") is True,
        {
            "files_compared": deterministic.get("files_compared"),
            "all_byte_identical": deterministic.get("all_byte_identical"),
        },
        "a clean rebuild is byte-identical for all core data and split artifacts",
        "mechanical",
    )
    gate(
        gates,
        "baseline_harness",
        blind_package.get("status") == "PASS"
        and runner_selftest.get("status") == "PASS"
        and blind_package.get("forbidden_tokens_found") == [],
        {
            "blind_inputs": blind_package.get("blind_inputs"),
            "jobs": blind_package.get("jobs"),
            "forbidden_tokens_found": blind_package.get("forbidden_tokens_found"),
            "runner_selftest": runner_selftest.get("status"),
        },
        "gold-free paired jobs and all baseline runner paths pass self-test",
        "mechanical",
    )

    repeated = {
        view: stats.get("repeated_sentence_rate")
        for view, stats in fingerprints.get("views", {}).items()
    }
    fingerprint_pass = bool(repeated) and all(
        value is not None and value <= args.max_repeated_sentence_rate
        for value in repeated.values()
    )
    gate(
        gates,
        "surface_form_diversity",
        fingerprint_pass,
        repeated,
        f"each view repeated-sentence rate <= {args.max_repeated_sentence_rate:.2f}",
        "scientific_release",
    )

    release_instances = [
        item for item in instances if item.get("release_status") == "RELEASE_CANDIDATE"
    ]
    approved_naturalized = sum(
        item.get("private_metadata", {})
        .get("generator", {})
        .get("model_assisted_polish_status")
        in {"PASS", "APPROVED"}
        for item in release_instances
    )
    calibration_drafts = sum(
        item.get("private_metadata", {})
        .get("generator", {})
        .get("model_assisted_polish_status")
        == "CALIBRATION_DRAFT"
        for item in calibration
    )
    gate(
        gates,
        "model_naturalization",
        approved_naturalized == len(release_instances) and len(release_instances) > 0,
        {
            "release_instances": len(release_instances),
            "approved": approved_naturalized,
            "separate_calibration_drafts": calibration_drafts,
        },
        "every release instance is naturalized and approved after inverse extraction",
        "scientific_release",
    )

    human_pass = sum(
        item.get("private_metadata", {})
        .get("validation", {})
        .get("human_review")
        in {"PASS", "APPROVED"}
        for item in release_instances
    )
    unique_pass = sum(
        item.get("private_metadata", {})
        .get("validation", {})
        .get("unique_solution")
        in {"PASS", "APPROVED"}
        for item in release_instances
    )
    inverse_pass = sum(
        item.get("private_metadata", {})
        .get("validation", {})
        .get("independent_inverse_extractor")
        in {"PASS", "APPROVED"}
        for item in release_instances
    )
    gate(
        gates,
        "human_cricket_review",
        human_pass == len(release_instances) and len(release_instances) > 0,
        {"release_instances": len(release_instances), "approved": human_pass},
        "all release instances pass independent cricket-domain review",
        "scientific_release",
    )
    gate(
        gates,
        "unique_solution_review",
        unique_pass == len(release_instances) and len(release_instances) > 0,
        {"release_instances": len(release_instances), "approved": unique_pass},
        "all release instances are independently judged to have a unique target",
        "scientific_release",
    )
    gate(
        gates,
        "independent_inverse_extraction",
        inverse_pass == len(release_instances) and len(release_instances) > 0,
        {"release_instances": len(release_instances), "approved": inverse_pass},
        "an extractor isolated from construction reconstructs every release target",
        "scientific_release",
    )

    ready_v0 = manifest.get("root_status_counts", {}).get("READY_FOR_GENERATED_VIEWS", 0)
    accepted_support = sum(item.get("annotation_status") in {"PASS", "APPROVED"} for item in support_proposals)
    gate(
        gates,
        "v0_human_support_annotation",
        ready_v0 > 0 and accepted_support == ready_v0,
        {
            "ready_v0_instances": ready_v0,
            "proposal_records": len(support_proposals),
            "accepted": accepted_support,
        },
        "every V0 instance has human-adjudicated cell support or is excluded from release",
        "scientific_release",
    )

    required_baselines = ("t3", "mapmake", "direct_cot")
    baseline_results = {}
    for method in required_baselines:
        candidates = list((baselines / "results").glob(f"{method}*.json")) if (baselines / "results").exists() else []
        baseline_results[method] = [path.name for path in candidates]
    gate(
        gates,
        "real_baseline_runs",
        all(baseline_results[method] for method in required_baselines),
        baseline_results,
        "reproducible held-out result files exist for T3, MapMake, and Direct-CoT",
        "scientific_release",
    )

    mechanical = [item for item in gates if item["category"] == "mechanical" and item["blocker"]]
    scientific = [
        item for item in gates if item["category"] == "scientific_release" and item["blocker"]
    ]
    report = {
        "gate_version": "0.1",
        "dataset_version": manifest.get("version"),
        "mechanical_status": "PASS" if all(item["status"] == "PASS" for item in mechanical) else "FAIL",
        "public_release_status": (
            "READY_FOR_PUBLIC_RELEASE"
            if all(item["status"] == "PASS" for item in mechanical + scientific)
            else "NOT_READY_FOR_PUBLIC_RELEASE"
        ),
        "gate_counts": {
            "total": len(gates),
            "passed": sum(item["status"] == "PASS" for item in gates),
            "failed": sum(item["status"] == "FAIL" for item in gates),
        },
        "gates": gates,
        "claim_guardrail": (
            "Diagnostic perturbations are not measurements of T3, MapMake, or Direct-CoT. "
            "Do not report baseline error rates until real held-out runs exist."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["mechanical_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
