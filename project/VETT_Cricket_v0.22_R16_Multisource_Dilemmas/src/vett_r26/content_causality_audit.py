from __future__ import annotations

import argparse
import ast
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .evaluation import score_predictions, write_oracle_predictions
from .spec import LEVELS


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_set(edges: Any, relation: str | None = None) -> set[tuple[str, str, str]]:
    result: set[tuple[str, str, str]] = set()
    if not isinstance(edges, list):
        return result
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        values = (edge.get("source_id"), edge.get("relation"), edge.get("target_id"))
        if not all(isinstance(value, str) for value in values):
            continue
        source, edge_relation, target = values
        if relation is None or edge_relation == relation:
            result.add((source, edge_relation, target))
    return result


def _mean(counter: Counter[str]) -> float:
    return (
        round(counter["edges"] / counter["questions"], 6)
        if counter["questions"]
        else 0.0
    )


def _opportunity_summary(
    groups: dict[str, Counter[str]],
) -> dict[str, dict[str, float | int]]:
    return {
        key: {
            "questions": groups[key]["questions"],
            "gold_edges": groups[key]["edges"],
            "mean_gold_edges_per_question": _mean(groups[key]),
        }
        for key in sorted(groups)
    }


def _iid_exact_expectation(edge_counts: dict[str, list[int]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for probability in (0.5, 0.7, 0.9):
        result[str(probability)] = {
            key: round(
                sum(probability**count for count in counts) / len(counts), 6
            )
            if counts
            else 0.0
            for key, counts in sorted(edge_counts.items())
        }
    return result


def certify_content_causality_bundle(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Certify one generated bundle without using the edge builder or its audit."""
    relation = str(contract["relation"])
    dependencies = {
        str(rule): set(map(str, fields))
        for rule, fields in contract["rule_input_dependencies"].items()
    }
    responsibilities = {
        str(rule): set(map(str, fields))
        for rule, fields in contract["rule_output_responsibilities"].items()
    }
    canonical_clauses = {
        str(rule): str(clause)
        for rule, clause in contract["canonical_public_rule_clauses"].items()
    }
    public_span_counts: Counter[str] = Counter(
        str(span["span_id"])
        for document in public["documents"]
        for span in document["spans"]
    )
    public_span_text = {
        str(span["span_id"]): str(span["text"])
        for document in public["documents"]
        for span in document["spans"]
    }
    rule_claims: dict[str, list[str]] = defaultdict(list)
    fact_claims: dict[tuple[str, str], list[str]] = defaultdict(list)
    for claim in evidence.get("r25_evidence_claims", []):
        if claim.get("role") == "rule" and claim.get("rule_key"):
            rule_claims[str(claim["rule_key"])].append(
                str(claim["inserted_span_id"])
            )
        if claim.get("role") == "incident_fact" and claim.get("field"):
            fact_claims[
                (str(claim.get("question_id", "")), str(claim["field"]))
            ].append(str(claim["inserted_span_id"]))

    errors: list[str] = []
    questions = 0
    actual_edges = 0
    expected_edges = 0
    exact_questions = 0
    linked_questions = 0
    nonempty_delta_questions = 0
    public_endpoint_edges = 0
    unique_endpoint_edges = 0
    public_semantic_anchor_edges = 0
    by_level: dict[str, Counter[str]] = defaultdict(Counter)
    by_field: dict[str, Counter[str]] = defaultdict(Counter)
    by_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    for answer in gold["decision_answers"]:
        questions += 1
        qid = str(answer["question_id"])
        level = str(answer["level"])
        scenario = str(answer.get("scenario_family", "UNREGISTERED"))
        changed_field = str(answer["counterfactual"]["changed_field"])
        factual = dict(answer["decision_record_flat"])
        counterfactual = dict(answer["counterfactual"]["decision_record_flat"])
        delta = {
            key
            for key in set(factual) | set(counterfactual)
            if factual.get(key) != counterfactual.get(key)
        }
        nonempty_delta_questions += int(bool(delta))
        sources = fact_claims.get((qid, changed_field), [])
        if len(sources) != 1:
            errors.append(f"{qid}: changed-field fact span count={len(sources)}")
            source = ""
        else:
            source = sources[0]
        expected: set[tuple[str, str, str]] = set()
        for rule in map(str, answer["rule_keys"]):
            if (
                rule not in dependencies
                or rule not in responsibilities
                or rule not in canonical_clauses
            ):
                errors.append(f"{qid}: unregistered rule={rule}")
                continue
            targets = rule_claims.get(rule, [])
            if len(targets) != 1:
                errors.append(f"{qid}: {rule} rule span count={len(targets)}")
                continue
            if (
                changed_field in dependencies[rule]
                and bool(delta & responsibilities[rule])
            ):
                expected.add((source, relation, targets[0]))
                semantic_anchor = canonical_clauses[rule] in public_span_text.get(
                    targets[0], ""
                )
                public_semantic_anchor_edges += int(semantic_anchor)
                if not semantic_anchor:
                    errors.append(f"{qid}: public rule clause mismatch={rule}")
        actual = _edge_set(answer["minimum_evidence_edges"], relation)
        if actual != expected:
            errors.append(
                f"{qid}: missing={len(expected - actual)} extra={len(actual - expected)}"
            )
        questions_edges = len(expected)
        for bucket in (by_level[level], by_field[changed_field], by_scenario[scenario]):
            bucket["questions"] += 1
            bucket["edges"] += questions_edges
        actual_edges += len(actual)
        expected_edges += questions_edges
        exact_questions += int(actual == expected)
        linked_questions += int(bool(expected))
        for source_id, _, target_id in actual:
            public_endpoint_edges += int(
                public_span_counts[source_id] > 0
                and public_span_counts[target_id] > 0
            )
            unique_endpoint_edges += int(
                public_span_counts[source_id] == 1
                and public_span_counts[target_id] == 1
            )
    gates = {
        "all_question_edge_sets_exact": exact_questions == questions,
        "all_questions_have_nonempty_record_delta": nonempty_delta_questions
        == questions,
        "all_questions_have_certified_content_edge": linked_questions == questions,
        "all_content_edge_endpoints_public": public_endpoint_edges == actual_edges,
        "all_content_edge_endpoints_unique": unique_endpoint_edges == actual_edges,
        "all_target_spans_contain_frozen_public_rule_clause": (
            public_semantic_anchor_edges == expected_edges
        ),
        "causal_registries_cover_the_same_rules": (
            set(dependencies) == set(responsibilities) == set(canonical_clauses)
        ),
        "actual_and_expected_edge_counts_match": actual_edges == expected_edges,
        "no_errors": not errors,
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "questions": questions,
        "actual_edges": actual_edges,
        "expected_edges": expected_edges,
        "public_semantic_anchor_edges": public_semantic_anchor_edges,
        "exact_questions": exact_questions,
        "opportunity_by_level": _opportunity_summary(by_level),
        "opportunity_by_intervention_field": _opportunity_summary(by_field),
        "opportunity_by_scenario_family": _opportunity_summary(by_scenario),
        "gates": gates,
        "errors": errors,
    }


def _remove_content_edges(source: Path, target: Path, relation: str) -> None:
    rows: list[str] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for prediction in row.get("decision_predictions", []):
            prediction["evidence_edges"] = [
                edge
                for edge in prediction.get("evidence_edges", [])
                if edge.get("relation") != relation
            ]
        rows.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
    target.write_text("\n".join(rows) + "\n", encoding="utf-8")


def audit_content_causality(
    release_dir: Path,
    contract_path: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Audit R26.15 without calling the candidate edge derivation implementation."""
    contract = _read(contract_path)
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    relation = str(contract["relation"])
    dependencies = {
        str(rule): set(map(str, fields))
        for rule, fields in contract["rule_input_dependencies"].items()
    }
    responsibilities = {
        str(rule): set(map(str, fields))
        for rule, fields in contract["rule_output_responsibilities"].items()
    }
    canonical_clauses = {
        str(rule): str(clause)
        for rule, clause in contract["canonical_public_rule_clauses"].items()
    }
    errors: list[str] = []
    warnings: list[str] = []
    questions = 0
    actual_edges_total = 0
    expected_edges_total = 0
    certified_edges = 0
    exact_questions = 0
    nonempty_delta_questions = 0
    linked_questions = 0
    public_endpoint_edges = 0
    unique_endpoint_edges = 0
    public_semantic_anchor_edges = 0
    scenarios: Counter[str] = Counter()
    opportunities_by_level = {level: Counter() for level in LEVELS}
    opportunities_by_field: dict[str, Counter[str]] = defaultdict(Counter)
    opportunities_by_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    edge_counts_by_level: dict[str, list[int]] = {level: [] for level in LEVELS}
    rule_certificates: Counter[str] = Counter()
    field_certificates: Counter[str] = Counter()
    delta_field_counts: Counter[str] = Counter()

    for match_id in map(str, summary["match_ids"]):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        evidence = _read(
            release_dir / "private" / match_id / "private_evidence.json"
        )
        public_span_counts: Counter[str] = Counter(
            str(span["span_id"])
            for document in public["documents"]
            for span in document["spans"]
        )
        public_span_text = {
            str(span["span_id"]): str(span["text"])
            for document in public["documents"]
            for span in document["spans"]
        }
        claims = evidence.get("r25_evidence_claims", [])
        rule_claims: dict[str, list[str]] = defaultdict(list)
        fact_claims: dict[tuple[str, str], list[str]] = defaultdict(list)
        for claim in claims:
            if claim.get("role") == "rule" and claim.get("rule_key"):
                rule_claims[str(claim["rule_key"])].append(
                    str(claim["inserted_span_id"])
                )
            if claim.get("role") == "incident_fact" and claim.get("field"):
                fact_claims[
                    (str(claim.get("question_id", "")), str(claim["field"]))
                ].append(str(claim["inserted_span_id"]))

        for answer in gold["decision_answers"]:
            questions += 1
            qid = str(answer["question_id"])
            level = str(answer["level"])
            scenario = str(answer.get("scenario_family", "UNREGISTERED"))
            changed_field = str(answer["counterfactual"]["changed_field"])
            scenarios[scenario] += 1
            factual = dict(answer["decision_record_flat"])
            counterfactual = dict(
                answer["counterfactual"]["decision_record_flat"]
            )
            if set(factual) != set(counterfactual):
                errors.append(f"{match_id}:{qid}: decision-record key mismatch")
            delta = {
                key
                for key in set(factual) | set(counterfactual)
                if factual.get(key) != counterfactual.get(key)
            }
            nonempty_delta_questions += int(bool(delta))
            for field in delta:
                delta_field_counts[field] += 1

            sources = fact_claims.get((qid, changed_field), [])
            if len(sources) != 1:
                errors.append(
                    f"{match_id}:{qid}: expected one changed-field fact span, got {len(sources)}"
                )
                source = ""
            else:
                source = sources[0]

            expected: set[tuple[str, str, str]] = set()
            certified_rules: set[str] = set()
            for rule in map(str, answer["rule_keys"]):
                if (
                    rule not in dependencies
                    or rule not in responsibilities
                    or rule not in canonical_clauses
                ):
                    errors.append(f"{match_id}:{qid}: unregistered rule {rule}")
                    continue
                targets = rule_claims.get(rule, [])
                if len(targets) != 1:
                    errors.append(
                        f"{match_id}:{qid}: expected one rule span for {rule}, got {len(targets)}"
                    )
                    continue
                if changed_field not in dependencies[rule]:
                    continue
                governed_delta = delta & responsibilities[rule]
                if not governed_delta:
                    continue
                expected.add((source, relation, targets[0]))
                semantic_anchor = canonical_clauses[rule] in public_span_text.get(
                    targets[0], ""
                )
                public_semantic_anchor_edges += int(semantic_anchor)
                if not semantic_anchor:
                    errors.append(
                        f"{match_id}:{qid}: public rule clause mismatch {rule}"
                    )
                certified_rules.add(rule)
                rule_certificates[rule] += 1
                field_certificates[changed_field] += 1

            actual = _edge_set(answer["minimum_evidence_edges"], relation)
            expected_edges_total += len(expected)
            actual_edges_total += len(actual)
            certified_edges += len(expected)
            exact_questions += int(actual == expected)
            linked_questions += int(bool(expected))
            if actual != expected:
                errors.append(
                    f"{match_id}:{qid}: content edge set differs; "
                    f"missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
                )
            for source_id, _, target_id in actual:
                endpoints_public = (
                    public_span_counts[source_id] > 0
                    and public_span_counts[target_id] > 0
                )
                endpoints_unique = (
                    public_span_counts[source_id] == 1
                    and public_span_counts[target_id] == 1
                )
                public_endpoint_edges += int(endpoints_public)
                unique_endpoint_edges += int(endpoints_unique)
            count = len(expected)
            edge_counts_by_level[level].append(count)
            for bucket in (
                opportunities_by_level[level],
                opportunities_by_field[changed_field],
                opportunities_by_scenario[scenario],
            ):
                bucket["questions"] += 1
                bucket["edges"] += count

    artifact_dir.mkdir(parents=True, exist_ok=True)
    oracle_path = artifact_dir / "ORACLE_PREDICTIONS.jsonl"
    omission_path = artifact_dir / "OMIT_CONTENT_EDGES_PREDICTIONS.jsonl"
    write_oracle_predictions(release_dir, oracle_path, test_only=True)
    _remove_content_edges(oracle_path, omission_path, relation)
    oracle_score = score_predictions(release_dir, oracle_path)
    omission_score = score_predictions(release_dir, omission_path)

    level_means = [
        _mean(opportunities_by_level[level])
        for level in LEVELS
        if opportunities_by_level[level]["questions"]
    ]
    opportunity_ratio = (
        round(max(level_means) / min(level_means), 6)
        if level_means and min(level_means) > 0
        else 0.0
    )
    policy = contract["measurement_policy"]
    if opportunity_ratio >= float(policy["opportunity_imbalance_warning_ratio"]):
        warnings.append(
            "content-edge opportunity differs by at least the frozen warning ratio; "
            "per-level exact is not a difficulty ordering metric"
        )
    masking_threshold = float(
        policy["masking_warning_overall_edge_f1_if_all_content_edges_omitted"]
    )
    if float(omission_score["minimal_evidence_edge_f1"]) >= masking_threshold:
        warnings.append(
            "overall edge F1 masks complete failure on content-dependency edges"
        )

    module_source = Path(__file__).read_text(encoding="utf-8")
    import_tree = ast.parse(module_source)
    observed_imports: list[str] = []
    for node in ast.walk(import_tree):
        if isinstance(node, ast.ImportFrom):
            module = (node.module or "").lstrip(".")
            observed_imports.extend(
                f"{module}.{alias.name}" for alias in node.names
            )
        elif isinstance(node, ast.Import):
            observed_imports.extend(alias.name for alias in node.names)
    forbidden_modules = {
        component
        for name in contract["audit_independence"]["must_not_import"]
        for component in str(name).split(".")
        if component.startswith("content_dependency")
    }
    forbidden_import_absent = not any(
        any(part == forbidden for part in imported.split("."))
        for imported in observed_imports
        for forbidden in forbidden_modules
    )
    gates = {
        "candidate_version_exact": summary.get("dataset_version")
        == contract["candidate_version"],
        "question_count_exact": questions
        == int(contract["admission_gates"]["questions"]),
        "scenario_family_count_exact": len(scenarios)
        == int(contract["admission_gates"]["scenario_families"]),
        "content_edge_count_exact": actual_edges_total
        == expected_edges_total
        == int(contract["admission_gates"]["expected_content_edges"]),
        "all_content_edge_sets_exact": exact_questions == questions,
        "all_questions_have_nonempty_record_delta": nonempty_delta_questions
        == questions,
        "all_questions_have_certified_content_edge": linked_questions == questions,
        "all_content_edges_have_output_responsibility_intersection": certified_edges
        == actual_edges_total,
        "all_content_edge_endpoints_public": public_endpoint_edges
        == actual_edges_total,
        "all_content_edge_endpoints_unique": unique_endpoint_edges
        == actual_edges_total,
        "all_target_spans_contain_frozen_public_rule_clause": (
            public_semantic_anchor_edges == expected_edges_total
        ),
        "causal_registries_cover_the_same_rules": (
            set(dependencies) == set(responsibilities) == set(canonical_clauses)
        ),
        "audit_implementation_avoids_candidate_deriver": forbidden_import_absent,
        "oracle_content_edge_f1_one": oracle_score.get(
            "content_dependency_edge_f1"
        )
        == 1.0,
        "content_omission_content_f1_zero": omission_score.get(
            "content_dependency_edge_f1"
        )
        == float(
            contract["admission_gates"][
                "content_omission_must_reduce_content_f1_to"
            ]
        ),
        "content_omission_factual_chain_exact_zero": omission_score.get(
            "factual_evidence_chain_joint_exact"
        )
        == float(
            contract["admission_gates"][
                "content_omission_must_reduce_factual_chain_exact_to"
            ]
        ),
    }
    if errors:
        gates["no_audit_errors"] = False
    else:
        gates["no_audit_errors"] = True
    status = "PASS_WITH_MEASUREMENT_WARNINGS" if all(gates.values()) else "FAIL"
    return {
        "protocol_version": contract["protocol_version"],
        "status": status,
        "claim_boundary": contract["claim_boundary"],
        "counts": {
            "matches": len(summary["match_ids"]),
            "questions": questions,
            "scenario_families": len(scenarios),
            "actual_content_edges": actual_edges_total,
            "independently_reconstructed_content_edges": expected_edges_total,
            "public_semantic_anchor_edges": public_semantic_anchor_edges,
            "exact_questions": exact_questions,
        },
        "causal_certificates": {
            "by_rule": dict(sorted(rule_certificates.items())),
            "by_intervention_field": dict(sorted(field_certificates.items())),
            "decision_record_delta_fields": dict(sorted(delta_field_counts.items())),
        },
        "opportunity": {
            "by_level": _opportunity_summary(opportunities_by_level),
            "by_intervention_field": _opportunity_summary(
                opportunities_by_field
            ),
            "by_scenario_family": _opportunity_summary(
                opportunities_by_scenario
            ),
            "maximum_to_minimum_level_mean_ratio": opportunity_ratio,
            "expected_exact_if_each_edge_is_independently_correct": (
                _iid_exact_expectation(edge_counts_by_level)
            ),
        },
        "masking_probe": {
            "mutation": "remove every conditions_rule edge while preserving all answers, spans and inherited edges",
            "oracle": {
                "overall_edge_f1": oracle_score["minimal_evidence_edge_f1"],
                "content_edge_f1": oracle_score[
                    "content_dependency_edge_f1"
                ],
                "factual_chain_exact": oracle_score[
                    "factual_evidence_chain_joint_exact"
                ],
            },
            "omit_content_edges": {
                "overall_edge_f1": omission_score[
                    "minimal_evidence_edge_f1"
                ],
                "content_edge_f1": omission_score[
                    "content_dependency_edge_f1"
                ],
                "content_question_macro_f1": omission_score[
                    "content_dependency_edge_question_macro_f1"
                ],
                "content_field_macro_f1": omission_score[
                    "content_dependency_edge_field_macro_f1"
                ],
                "content_scenario_macro_f1": omission_score[
                    "content_dependency_edge_scenario_macro_f1"
                ],
                "factual_chain_exact": omission_score[
                    "factual_evidence_chain_joint_exact"
                ],
            },
        },
        "gates": gates,
        "audit_implementation": {
            "observed_imports": sorted(observed_imports),
            "forbidden_candidate_derivation_import_absent": (
                forbidden_import_absent
            ),
        },
        "warnings": warnings,
        "errors": errors[:100],
        "provider_requests": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_content_causality(
        args.release, args.contract, args.artifact_dir
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
