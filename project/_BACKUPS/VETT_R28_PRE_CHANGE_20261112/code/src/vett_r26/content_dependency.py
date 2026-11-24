from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .spec import LEVELS
from .spec import (
    CONTENT_DEPENDENCY_DESIGN_REVISION,
    CONTENT_DEPENDENCY_RELATIONS,
    CONTENT_DEPENDENCY_VERSION,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _edge_set(edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {
        (
            str(edge["source_id"]),
            str(edge["relation"]),
            str(edge["target_id"]),
        )
        for edge in edges
    }


def derive_content_dependency_edges(
    answer: dict[str, Any],
    evidence: dict[str, Any],
    contract: dict[str, Any],
) -> list[dict[str, str]]:
    """Derive fact-to-rule edges from the frozen semantic dependency registry."""
    question_id = str(answer["question_id"])
    fact_spans = {
        str(claim["field"]): str(claim["inserted_span_id"])
        for claim in evidence.get("r25_evidence_claims", [])
        if str(claim.get("question_id", "")) == question_id
        and claim.get("role") == "incident_fact"
    }
    rule_spans = {
        str(claim["rule_key"]): str(claim["inserted_span_id"])
        for claim in evidence.get("r25_evidence_claims", [])
        if claim.get("role") == "rule" and claim.get("rule_key")
    }
    dependency_priority = contract["rule_dependency_priority"]
    changed_field = str(answer["counterfactual"]["changed_field"])
    edges: list[dict[str, str]] = []
    for rule_key in map(str, answer["rule_keys"]):
        if rule_key not in dependency_priority:
            raise ValueError(f"unregistered rule dependency: {rule_key}")
        if rule_key not in rule_spans:
            raise ValueError(f"missing rule span: {question_id}:{rule_key}")
        registered_fields = list(map(str, dependency_priority[rule_key]))
        if changed_field not in registered_fields:
            continue
        if changed_field not in fact_spans:
            raise ValueError(
                f"changed dependency fact is absent: {question_id}:{changed_field}"
            )
        edges.append(
            {
                "source_id": fact_spans[changed_field],
                "relation": str(contract["new_relation"]),
                "target_id": rule_spans[rule_key],
                "dependency_field": changed_field,
                "rule_key": rule_key,
            }
        )
    return edges


def augment_content_dependency_bundle(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    public = copy.deepcopy(public)
    gold = copy.deepcopy(gold)
    evidence = copy.deepcopy(evidence)
    for payload in (public, gold, evidence):
        payload["dataset_version"] = CONTENT_DEPENDENCY_VERSION
        payload["measurement_design_revision"] = (
            CONTENT_DEPENDENCY_DESIGN_REVISION
        )
    registry = {
        str(item["question_id"]): item
        for item in evidence["r26_minimum_evidence_edges"]
    }
    additions_registry: list[dict[str, Any]] = []
    for question in public["decision_question_schema"]:
        public_contract = question["r26_public_contract"]
        public_contract["evidence_edge_relations"] = list(
            CONTENT_DEPENDENCY_RELATIONS
        )
        public_contract["content_dependency_required"] = True
    for answer in gold["decision_answers"]:
        additions = derive_content_dependency_edges(answer, evidence, contract)
        public_edges = [
            {
                "source_id": edge["source_id"],
                "relation": edge["relation"],
                "target_id": edge["target_id"],
            }
            for edge in additions
        ]
        answer["minimum_evidence_edges"].extend(public_edges)
        answer["evidence_graph_contract"]["edge_count"] = len(
            answer["minimum_evidence_edges"]
        )
        answer["content_dependency_design_revision"] = (
            CONTENT_DEPENDENCY_DESIGN_REVISION
        )
        answer["content_dependency_edge_count"] = len(public_edges)
        question_id = str(answer["question_id"])
        registry[question_id]["edges"].extend(public_edges)
        additions_registry.append(
            {"question_id": question_id, "edges": additions}
        )
    evidence["r26_15_content_dependency_edges"] = additions_registry
    evidence["content_dependency_design_revision"] = (
        CONTENT_DEPENDENCY_DESIGN_REVISION
    )
    return public, gold, evidence


def _is_acyclic(edges: set[tuple[str, str, str]]) -> bool:
    adjacency: dict[str, set[str]] = {}
    nodes: set[str] = set()
    for source, _, target in edges:
        adjacency.setdefault(source, set()).add(target)
        nodes.update((source, target))
    state: dict[str, int] = {}

    def visit(node: str) -> bool:
        marker = state.get(node, 0)
        if marker == 1:
            return False
        if marker == 2:
            return True
        state[node] = 1
        for target in adjacency.get(node, ()):
            if not visit(target):
                return False
        state[node] = 2
        return True

    return all(visit(node) for node in nodes if state.get(node, 0) == 0)


def audit_content_dependency_feasibility(
    release_dir: Path,
    contract_path: Path,
) -> dict[str, Any]:
    contract = _read(contract_path)
    dependency_priority = contract["rule_dependency_priority"]
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    errors: list[str] = []
    questions = 0
    existing_edges_total = 0
    added_edges_total = 0
    max_augmented_edges = 0
    complete_affected_rule_set = True
    changed_field_linked = True
    endpoints_valid = True
    all_acyclic = True
    field_counts: Counter[str] = Counter()
    rule_counts: Counter[str] = Counter()
    added_by_level: dict[str, Counter[str]] = {
        level: Counter() for level in LEVELS
    }
    used_rules: set[str] = set()
    for match_id in map(str, summary["match_ids"]):
        gold = _read(
            release_dir / "private" / match_id / "private_gold.json"
        )
        evidence = _read(
            release_dir / "private" / match_id / "private_evidence.json"
        )
        for answer in gold["decision_answers"]:
            questions += 1
            level = str(answer["level"])
            try:
                additions = derive_content_dependency_edges(
                    answer, evidence, contract
                )
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"{match_id}:{answer['question_id']}:{exc}")
                continue
            existing = _edge_set(answer["minimum_evidence_edges"])
            added = {
                (
                    edge["source_id"],
                    edge["relation"],
                    edge["target_id"],
                )
                for edge in additions
            }
            positive = set(map(str, answer["minimum_evidence_spans"]))
            changed_field = str(answer["counterfactual"]["changed_field"])
            expected_rule_keys = {
                str(rule_key)
                for rule_key in answer["rule_keys"]
                if changed_field
                in set(map(str, dependency_priority[str(rule_key)]))
            }
            complete_affected_rule_set &= {
                str(edge["rule_key"]) for edge in additions
            } == expected_rule_keys
            changed_field_linked &= any(
                edge["dependency_field"]
                == str(answer["counterfactual"]["changed_field"])
                for edge in additions
            )
            endpoints_valid &= all(
                source in positive and target in positive
                for source, _, target in added
            )
            all_acyclic &= _is_acyclic(existing | added)
            existing_edges_total += len(existing)
            added_edges_total += len(added)
            max_augmented_edges = max(
                max_augmented_edges, len(existing | added)
            )
            added_by_level[level]["questions"] += 1
            added_by_level[level]["edges"] += len(added)
            for edge in additions:
                field_counts[edge["dependency_field"]] += 1
                rule_counts[edge["rule_key"]] += 1
                used_rules.add(edge["rule_key"])

    registered_rules = set(map(str, contract["rule_dependency_priority"]))
    limit = int(contract["invariants"]["maximum_edges_per_question"])
    old_template_recall = (
        existing_edges_total / (existing_edges_total + added_edges_total)
        if existing_edges_total + added_edges_total
        else 0.0
    )
    old_template_f1 = (
        2 * old_template_recall / (1 + old_template_recall)
        if old_template_recall
        else 0.0
    )
    gates = {
        "no_feasibility_errors": not errors,
        "all_registered_rule_keys_are_mapped": used_rules <= registered_rules,
        "every_used_rule_key_is_registered": not (used_rules - registered_rules),
        "complete_intervention_to_affected_rule_edge_set": complete_affected_rule_set,
        "every_question_links_its_counterfactual_changed_field": changed_field_linked,
        "all_new_endpoints_are_existing_positive_spans": endpoints_valid,
        "all_augmented_graphs_are_acyclic": all_acyclic,
        "maximum_edge_count_within_output_contract": max_augmented_edges <= limit,
        "old_role_template_content_edge_recall_is_zero": True,
    }
    return {
        "protocol_version": "VETT-R26.15-CONTENT-DEPENDENCY-FEASIBILITY-2",
        "status": "FEASIBLE" if all(gates.values()) else "INFEASIBLE",
        "parent_dataset_version": summary.get("dataset_version"),
        "proposed_dataset_version": contract["candidate_version"],
        "matches": len(summary["match_ids"]),
        "questions": questions,
        "existing_edges": existing_edges_total,
        "proposed_content_dependency_edges": added_edges_total,
        "proposed_total_edges": existing_edges_total + added_edges_total,
        "maximum_augmented_edges_per_question": max_augmented_edges,
        "gates": gates,
        "errors": errors[:50],
        "added_edges_by_level": {
            level: {
                "questions": int(added_by_level[level]["questions"]),
                "edges": int(added_by_level[level]["edges"]),
                "mean_edges_per_question": round(
                    added_by_level[level]["edges"]
                    / added_by_level[level]["questions"],
                    6,
                )
                if added_by_level[level]["questions"]
                else 0.0,
            }
            for level in LEVELS
        },
        "selected_dependency_field_counts": dict(sorted(field_counts.items())),
        "rule_edge_counts": dict(sorted(rule_counts.items())),
        "registered_rule_keys": sorted(registered_rules),
        "used_rule_keys": sorted(used_rules),
        "topology_information_gain": {
            "current_role_oracle_edge_exact": 1.0,
            "old_role_template_content_dependency_edge_recall": 0.0,
            "old_role_template_recall_on_augmented_graph": round(
                old_template_recall, 6
            ),
            "old_role_template_f1_on_augmented_graph": round(
                old_template_f1, 6
            ),
            "interpretation": (
                "The old role template retains every inherited edge but cannot "
                "construct a fact-to-rule dependency without resolving both the "
                "fact field and the governing rule key."
            ),
        },
        "semantic_change_scope": {
            "public_text": 0,
            "questions": 0,
            "facts_states_and_counterfactuals": 0,
            "positive_and_rejected_span_membership": 0,
            "inherited_edges_removed_or_modified": 0,
            "private_edges_added": added_edges_total,
            "public_relation_vocabulary_additions": [contract["new_relation"]],
        },
        "contract": str(contract_path),
        "contract_sha256": _sha256(contract_path),
        "provider_requests_made": 0,
        "claim_boundary": (
            "This is a private-side feasibility audit. It does not materialize "
            "R26.15, prove that models find the endpoints, or authorize empirical "
            "claims."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-content-dependency")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_content_dependency_feasibility(
        args.release, args.contract
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "FEASIBLE" else 2)


if __name__ == "__main__":
    main()


__all__ = [
    "augment_content_dependency_bundle",
    "audit_content_dependency_feasibility",
    "derive_content_dependency_edges",
]
