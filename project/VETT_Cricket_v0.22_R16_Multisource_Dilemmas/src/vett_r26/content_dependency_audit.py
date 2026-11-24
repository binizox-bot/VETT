from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .auditor import audit_release
from .content_dependency import derive_content_dependency_edges
from .spec import (
    ANSWER_BLIND_VERSION,
    CONTENT_DEPENDENCY_DESIGN_REVISION,
    CONTENT_DEPENDENCY_RELATIONS,
    CONTENT_DEPENDENCY_VERSION,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _edge_set(edges: list[dict[str, Any]]) -> set[tuple[str, str, str]]:
    return {
        (
            str(edge["source_id"]),
            str(edge["relation"]),
            str(edge["target_id"]),
        )
        for edge in edges
    }


def _is_acyclic(edges: set[tuple[str, str, str]]) -> bool:
    adjacency: dict[str, set[str]] = {}
    nodes: set[str] = set()
    for source, _, target in edges:
        adjacency.setdefault(source, set()).add(target)
        nodes.update((source, target))
    state: dict[str, int] = {}

    def visit(node: str) -> bool:
        if state.get(node) == 1:
            return False
        if state.get(node) == 2:
            return True
        state[node] = 1
        for target in adjacency.get(node, ()):
            if not visit(target):
                return False
        state[node] = 2
        return True

    return all(visit(node) for node in nodes if not state.get(node))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_content_dependency_release(
    parent_release: Path,
    candidate_release: Path,
    contract_path: Path,
) -> dict[str, Any]:
    contract = _read(contract_path)
    parent_summary = _read(parent_release / "RELEASE_SUMMARY.json")
    candidate_summary = _read(candidate_release / "RELEASE_SUMMARY.json")
    errors: list[str] = []
    parent_audit = audit_release(parent_release)
    if parent_audit.get("status") != "PASS":
        errors.append("parent R26.14 release no longer passes its own audit")
    if parent_summary.get("dataset_version") != ANSWER_BLIND_VERSION:
        errors.append("unexpected parent dataset version")
    if candidate_summary.get("dataset_version") != CONTENT_DEPENDENCY_VERSION:
        errors.append("unexpected candidate dataset version")
    if parent_summary.get("match_ids") != candidate_summary.get("match_ids"):
        errors.append("match selection changed")

    text_changes = 0
    question_changes = 0
    semantic_changes = 0
    span_membership_changes = 0
    inherited_edge_changes = 0
    added_edges = 0
    expected_added_edges = 0
    maximum_edges = 0
    questions = 0
    content_edges_by_level: Counter[str] = Counter()
    all_dag = True
    all_endpoints_valid = True
    registry_exact = True
    enriched_registry_exact = True
    intervention_linked_questions = 0
    for match_id in map(str, parent_summary["match_ids"]):
        parent_public = _read(
            parent_release / "public" / match_id / "public_instance.json"
        )
        candidate_public = _read(
            candidate_release / "public" / match_id / "public_instance.json"
        )
        parent_gold = _read(
            parent_release / "private" / match_id / "private_gold.json"
        )
        candidate_gold = _read(
            candidate_release / "private" / match_id / "private_gold.json"
        )
        candidate_evidence = _read(
            candidate_release
            / "private"
            / match_id
            / "private_evidence.json"
        )
        text_changes += int(
            parent_public["documents"] != candidate_public["documents"]
        )
        parent_questions = {
            str(item["question_id"]): str(item["question"])
            for item in parent_public["decision_question_schema"]
        }
        candidate_questions = {
            str(item["question_id"]): str(item["question"])
            for item in candidate_public["decision_question_schema"]
        }
        question_changes += sum(
            parent_questions.get(qid) != text
            for qid, text in candidate_questions.items()
        )
        for question in candidate_public["decision_question_schema"]:
            public_contract = question.get("r26_public_contract", {})
            if set(public_contract.get("evidence_edge_relations", [])) != set(
                CONTENT_DEPENDENCY_RELATIONS
            ):
                errors.append(f"{match_id}: public relation contract mismatch")
            if public_contract.get("content_dependency_required") is not True:
                errors.append(f"{match_id}: content dependency flag absent")
        parent_answers = {
            str(item["question_id"]): item
            for item in parent_gold["decision_answers"]
        }
        evidence_registry = {
            str(item["question_id"]): _edge_set(item["edges"])
            for item in candidate_evidence["r26_minimum_evidence_edges"]
        }
        content_registry = {
            str(item["question_id"]): item["edges"]
            for item in candidate_evidence.get(
                "r26_15_content_dependency_edges", []
            )
        }
        for candidate_answer in candidate_gold["decision_answers"]:
            questions += 1
            qid = str(candidate_answer["question_id"])
            parent_answer = parent_answers[qid]
            for key in (
                "decision_record",
                "decision_record_flat",
                "state",
                "solver_facts",
                "counterfactual",
                "required_fact_fields",
                "rule_keys",
            ):
                semantic_changes += int(
                    parent_answer.get(key) != candidate_answer.get(key)
                )
            for key in (
                "minimum_evidence_spans",
                "rejected_evidence_spans",
            ):
                span_membership_changes += int(
                    parent_answer.get(key) != candidate_answer.get(key)
                )
            parent_edges = _edge_set(parent_answer["minimum_evidence_edges"])
            candidate_edges = _edge_set(
                candidate_answer["minimum_evidence_edges"]
            )
            expected_enriched = derive_content_dependency_edges(
                candidate_answer, candidate_evidence, contract
            )
            expected_added = {
                (
                    edge["source_id"],
                    edge["relation"],
                    edge["target_id"],
                )
                for edge in expected_enriched
            }
            actual_added = candidate_edges - parent_edges
            expected_added_edges += len(expected_added)
            inherited_edge_changes += int(
                not parent_edges <= candidate_edges
            )
            if actual_added != expected_added:
                errors.append(f"{match_id}:{qid}: content edges mismatch")
            registry_exact &= evidence_registry.get(qid) == candidate_edges
            registry_content_edges = {
                (
                    str(edge["source_id"]),
                    str(edge["relation"]),
                    str(edge["target_id"]),
                )
                for edge in content_registry.get(qid, [])
            }
            registry_exact &= registry_content_edges == expected_added
            enriched_registry_exact &= content_registry.get(qid, []) == expected_enriched
            changed_field = str(
                candidate_answer["counterfactual"]["changed_field"]
            )
            intervention_linked = any(
                edge["dependency_field"] == changed_field
                for edge in expected_enriched
            )
            intervention_linked_questions += int(intervention_linked)
            if not intervention_linked:
                errors.append(
                    f"{match_id}:{qid}: counterfactual changed field is not linked"
                )
            positive = set(
                map(str, candidate_answer["minimum_evidence_spans"])
            )
            all_endpoints_valid &= all(
                source in positive and target in positive
                for source, _, target in expected_added
            )
            all_dag &= _is_acyclic(candidate_edges)
            added_edges += len(actual_added)
            maximum_edges = max(maximum_edges, len(candidate_edges))
            content_edges_by_level[str(candidate_answer["level"])] += len(
                actual_added
            )
            if candidate_answer.get(
                "content_dependency_design_revision"
            ) != CONTENT_DEPENDENCY_DESIGN_REVISION:
                errors.append(f"{match_id}:{qid}: design revision absent")

    manifest = _read(candidate_release / "MANIFEST.json")
    expected_manifest = {
        str(item["path"]): item for item in manifest.get("files", [])
    }
    actual_files = {
        path.relative_to(candidate_release).as_posix(): path
        for path in candidate_release.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    manifest_mismatches = 0
    if set(expected_manifest) != set(actual_files):
        manifest_mismatches += len(set(expected_manifest) ^ set(actual_files))
    for name in set(expected_manifest) & set(actual_files):
        item = expected_manifest[name]
        path = actual_files[name]
        if item.get("bytes") != path.stat().st_size or item.get("sha256") != _sha256(path):
            manifest_mismatches += 1

    gates = {
        "parent_release_passes": parent_audit.get("status") == "PASS",
        "all_100_questions_present": questions == 100,
        "public_documents_unchanged": text_changes == 0,
        "public_question_text_unchanged": question_changes == 0,
        "facts_states_and_counterfactuals_unchanged": semantic_changes == 0,
        "positive_and_rejected_span_membership_unchanged": span_membership_changes == 0,
        "all_inherited_edges_preserved": inherited_edge_changes == 0,
        "content_dependency_edge_count_matches_frozen_derivation": (
            added_edges
            == expected_added_edges
            == int(
                contract["admission"][
                    "pilot_expected_content_dependency_edges"
                ]
            )
        ),
        "all_content_edges_match_frozen_registry": not any(
            "content edges mismatch" in error for error in errors
        ),
        "private_edge_registries_exact": registry_exact,
        "enriched_dependency_registry_exact": enriched_registry_exact,
        "all_questions_link_counterfactual_changed_field": (
            intervention_linked_questions == questions
        ),
        "all_content_edge_endpoints_are_positive_spans": all_endpoints_valid,
        "all_augmented_graphs_are_acyclic": all_dag,
        "maximum_edge_count_at_most_48": maximum_edges <= 48,
        "manifest_complete_and_hash_valid": manifest_mismatches == 0,
    }
    return {
        "protocol_version": "VETT-R26.15-CONTENT-DEPENDENCY-RELEASE-AUDIT-2",
        "status": "PASS" if all(gates.values()) and not errors else "FAIL",
        "dataset_version": candidate_summary.get("dataset_version"),
        "matches": len(parent_summary["match_ids"]),
        "questions": questions,
        "content_dependency_edges": added_edges,
        "expected_content_dependency_edges": expected_added_edges,
        "intervention_linked_questions": intervention_linked_questions,
        "content_dependency_edges_by_level": dict(
            sorted(content_edges_by_level.items())
        ),
        "maximum_edges_per_question": maximum_edges,
        "public_document_changes": text_changes,
        "public_question_changes": question_changes,
        "semantic_field_changes": semantic_changes,
        "span_membership_changes": span_membership_changes,
        "inherited_edge_changes": inherited_edge_changes,
        "manifest_mismatches": manifest_mismatches,
        "gates": gates,
        "errors": errors[:100],
        "provider_requests_made": 0,
        "claim_boundary": (
            "PASS proves a narrow, deterministic graph-only extension. It does "
            "not establish model difficulty, empirical level gaps or publication "
            "readiness."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-content-dependency-audit")
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_content_dependency_release(
        args.parent, args.candidate, args.contract
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()


__all__ = ["audit_content_dependency_release"]
