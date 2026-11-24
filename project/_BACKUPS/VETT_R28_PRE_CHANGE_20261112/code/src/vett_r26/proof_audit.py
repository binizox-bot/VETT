from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from vett_r25.solver import flatten_record, solve, trace_state

from .renderer import fact_clause


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _outputs(
    facts: dict[str, Any],
    *,
    intervention_field: str,
    intervention_value: Any,
    active_source: str,
) -> dict[str, Any]:
    factual = solve(facts)
    changed = json.loads(json.dumps(facts, ensure_ascii=False))
    changed[intervention_field] = intervention_value
    counterfactual = solve(changed)
    result: dict[str, Any] = {}
    for prefix, record, state_facts in (
        ("factual", factual, facts),
        ("counterfactual", counterfactual, changed),
    ):
        result.update({
            f"{prefix}.record.{key}": value
            for key, value in flatten_record(record).items()
        })
        result.update({
            f"{prefix}.state.{key}": value
            for key, value in trace_state(state_facts, record, active_source).items()
        })
    return result


def _reachable(
    edges: list[dict[str, str]],
    source: str,
    target: str,
    *,
    removed_node: str | None = None,
) -> bool:
    if removed_node in {source, target}:
        return False
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        left = str(edge["source_id"])
        right = str(edge["target_id"])
        if removed_node in {left, right}:
            continue
        adjacency[left].add(right)
    seen = {source}
    frontier = [source]
    while frontier:
        node = frontier.pop()
        if node == target:
            return True
        for neighbor in adjacency.get(node, set()) - seen:
            seen.add(neighbor)
            frontier.append(neighbor)
    return target in seen


def _edge_key(edge: dict[str, str]) -> tuple[str, str, str]:
    return (
        str(edge.get("source_id", "")),
        str(edge.get("relation", "")),
        str(edge.get("target_id", "")),
    )


def _edge_obligation_holds(
    edges: list[dict[str, str]],
    *,
    query_id: str,
    decision_id: str,
    authority_id: str,
    accepted_fact_ids: set[str],
    rejected_ids: set[str],
    rule_ids: set[str],
) -> bool:
    triples = {_edge_key(edge) for edge in edges}
    bridge_reachable = all(
        _reachable(edges, query_id, fact_id) for fact_id in accepted_fact_ids
    )
    accepted_covered = all(
        (authority_id, "authorizes", span_id) in triples
        and (span_id, "supports_decision", decision_id) in triples
        for span_id in accepted_fact_ids
    )
    rejected_covered = all(
        (authority_id, "rejects", span_id) in triples for span_id in rejected_ids
    )
    rules_covered = all(
        (span_id, "governs_decision", decision_id) in triples for span_id in rule_ids
    )
    return bridge_reachable and accepted_covered and rejected_covered and rules_covered


def _audit_question(
    answer: dict[str, Any],
    claims: list[dict[str, Any]],
    public_span_ids: set[str],
    public_span_text: dict[str, str],
) -> dict[str, Any]:
    errors: list[str] = []
    qid = str(answer["question_id"])
    decision_id = f"decision:{qid}"
    decisive = set(map(str, answer.get("minimum_evidence_spans", [])))
    rejected = set(map(str, answer.get("rejected_evidence_spans", [])))
    edges = list(answer.get("minimum_evidence_edges", []))
    witnesses = {
        str(item.get("span_id")): item
        for item in answer.get("evidence_necessity", [])
    }
    item_claims = [claim for claim in claims if str(claim.get("question_id", "")) == qid]
    claim_by_span: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        claim_by_span[str(claim.get("inserted_span_id", ""))].append(claim)

    fact_claims = [
        claim for claim in item_claims
        if claim.get("role") == "incident_fact"
        and str(claim.get("inserted_span_id")) in decisive
    ]
    facts: dict[str, Any] = {}
    duplicate_fact_fields: list[str] = []
    for claim in fact_claims:
        field = str(claim.get("field"))
        if field in facts:
            duplicate_fact_fields.append(field)
        facts[field] = claim.get("value")
    required_fields = set(map(str, answer.get("required_fact_fields", [])))
    if set(facts) != required_fields:
        errors.append("sufficiency_required_fact_coverage")
    if duplicate_fact_fields:
        errors.append("duplicate_accepted_fact_dependency")

    counterfactual = answer.get("counterfactual", {})
    try:
        factual_record = solve(facts)
        changed_facts = json.loads(json.dumps(facts, ensure_ascii=False))
        changed_facts[str(counterfactual["changed_field"])] = counterfactual["new_value"]
        counterfactual_record = solve(changed_facts)
        if factual_record != answer.get("decision_record"):
            errors.append("minimal_facts_do_not_reconstruct_factual_record")
        if counterfactual_record != counterfactual.get("decision_record"):
            errors.append("minimal_facts_do_not_reconstruct_counterfactual_record")
    except (KeyError, TypeError, ValueError) as exc:
        factual_record = None
        counterfactual_record = None
        errors.append(f"minimal_fact_solver_error:{exc}")

    rule_dependencies = {
        str(item.get("dependency", "")).split(":", 1)[1]: span_id
        for span_id, item in witnesses.items()
        if str(item.get("dependency", "")).startswith("RULE:")
    }
    rule_ids = set(rule_dependencies.values())
    if set(rule_dependencies) != set(map(str, answer.get("rule_keys", []))):
        errors.append("rule_dependency_coverage")
    for rule_key, span_id in rule_dependencies.items():
        candidates = [
            claim for claim in claims
            if claim.get("role") == "rule" and claim.get("rule_key") == rule_key
        ]
        if len(candidates) != 1 or str(candidates[0].get("inserted_span_id")) != span_id:
            errors.append(f"non_unique_rule_premise:{rule_key}")

    fact_ids = {
        str(claim.get("inserted_span_id")) for claim in fact_claims
    }
    authority_id = str(answer.get("evidence_graph_contract", {}).get("authority_span", ""))
    if authority_id not in decisive:
        errors.append("authority_not_decisive")
    if not (decisive | rejected) <= public_span_ids:
        errors.append("proof_span_missing_from_public_context")

    # Registered uniqueness alone is insufficient: an unregistered public span
    # containing the same decisive proposition would still provide a shortcut.
    exact_text_counts = Counter(text.casefold() for text in public_span_text.values())
    duplicated_decisive_surface = sorted(
        span_id
        for span_id in decisive
        if exact_text_counts[public_span_text.get(span_id, "").casefold()] != 1
    )
    if duplicated_decisive_surface:
        errors.append(
            f"unregistered_exact_surface_substitutes:{len(duplicated_decisive_surface)}"
        )
    fact_surface_candidate_counts: dict[str, int] = {}
    terminal_subject = str(
        answer.get("natural_identity", {}).get("terminal_subject", "")
    ).casefold()
    for claim in fact_claims:
        field = str(claim.get("field"))
        try:
            clause = fact_clause(field, claim.get("value")).casefold()
        except (KeyError, TypeError, ValueError):
            fact_surface_candidate_counts[field] = 0
            continue
        fact_surface_candidate_counts[field] = sum(
            clause in text.casefold()
            and bool(terminal_subject)
            and terminal_subject in text.casefold()
            for text in public_span_text.values()
        )
    non_unique_fact_surface = {
        field: count
        for field, count in fact_surface_candidate_counts.items()
        if count != 1
    }
    if non_unique_fact_surface:
        errors.append(
            f"unregistered_fact_proposition_substitutes:{len(non_unique_fact_surface)}"
        )

    full_obligation = _edge_obligation_holds(
        edges,
        query_id=qid,
        decision_id=decision_id,
        authority_id=authority_id,
        accepted_fact_ids=fact_ids,
        rejected_ids=rejected,
        rule_ids=rule_ids,
    )
    if not full_obligation:
        errors.append("full_graph_does_not_satisfy_proof_obligation")
    undetected_edge_deletions = []
    for index, edge in enumerate(edges):
        reduced = edges[:index] + edges[index + 1 :]
        if _edge_obligation_holds(
            reduced,
            query_id=qid,
            decision_id=decision_id,
            authority_id=authority_id,
            accepted_fact_ids=fact_ids,
            rejected_ids=rejected,
            rule_ids=rule_ids,
        ):
            undetected_edge_deletions.append(_edge_key(edge))
    if undetected_edge_deletions:
        errors.append(f"redundant_registered_edges:{len(undetected_edge_deletions)}")

    invalid_witnesses: list[str] = []
    causal_fact_witnesses = 0
    structural_witnesses = 0
    for span_id in sorted(decisive):
        witness = witnesses.get(span_id)
        if witness is None:
            invalid_witnesses.append(span_id)
            continue
        dependency = str(witness.get("dependency", ""))
        if dependency.startswith("FACT:"):
            field = dependency.split(":", 1)[1]
            countermodel = witness.get("countermodel", {})
            try:
                base_outputs = _outputs(
                    answer["solver_facts"],
                    intervention_field=counterfactual["changed_field"],
                    intervention_value=counterfactual["new_value"],
                    active_source=answer["state"]["active_source"],
                )
                alternate = json.loads(json.dumps(answer["solver_facts"], ensure_ascii=False))
                alternate[field] = countermodel["alternate_value"]
                alternate_outputs = _outputs(
                    alternate,
                    intervention_field=counterfactual["changed_field"],
                    intervention_value=counterfactual["new_value"],
                    active_source=answer["state"]["active_source"],
                )
                changed_outputs = sorted(
                    key for key, value in base_outputs.items()
                    if alternate_outputs.get(key) != value
                )
                if not changed_outputs or changed_outputs != countermodel.get("changed_outputs"):
                    invalid_witnesses.append(span_id)
                else:
                    causal_fact_witnesses += 1
            except (KeyError, TypeError, ValueError):
                invalid_witnesses.append(span_id)
        elif dependency.startswith("RULE:"):
            rule_key = dependency.split(":", 1)[1]
            registered = [
                claim for claim in claim_by_span.get(span_id, [])
                if claim.get("role") == "rule" and claim.get("rule_key") == rule_key
            ]
            if len(registered) != 1:
                invalid_witnesses.append(span_id)
            else:
                structural_witnesses += 1
        elif dependency in {
            "TARGET_BINDING",
            "SEMANTIC_TARGET_BINDING",
            "SOURCE_AUTHORITY",
            "SOURCE_SELECTION",
        }:
            if all(
                _reachable(edges, qid, fact_id, removed_node=span_id)
                for fact_id in fact_ids
            ):
                invalid_witnesses.append(span_id)
            else:
                structural_witnesses += 1
        else:
            invalid_witnesses.append(span_id)
    if invalid_witnesses:
        errors.append(f"invalid_single_span_deletion_witnesses:{len(invalid_witnesses)}")

    alternate_candidates: dict[str, int] = {}
    for field in sorted(required_fields):
        candidates = [
            claim for claim in item_claims
            if claim.get("role") == "incident_fact" and str(claim.get("field")) == field
        ]
        alternate_candidates[f"FACT:{field}"] = len(candidates)
    for rule_key in sorted(rule_dependencies):
        alternate_candidates[f"RULE:{rule_key}"] = sum(
            claim.get("role") == "rule" and claim.get("rule_key") == rule_key
            for claim in claims
        )
    non_unique_dependencies = {
        dependency: count
        for dependency, count in alternate_candidates.items()
        if count != 1
    }
    if non_unique_dependencies:
        errors.append(f"registered_alternative_proofs:{len(non_unique_dependencies)}")

    return {
        "question_id": qid,
        "level": answer.get("level"),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "minimal_fact_reconstruction": (
            factual_record == answer.get("decision_record")
            and counterfactual_record == counterfactual.get("decision_record")
        ),
        "decisive_spans": len(decisive),
        "rejected_spans": len(rejected),
        "typed_edges": len(edges),
        "all_single_edge_deletions_detected": not undetected_edge_deletions,
        "causal_fact_witnesses": causal_fact_witnesses,
        "structural_dependency_witnesses": structural_witnesses,
        "invalid_single_span_deletion_witnesses": invalid_witnesses,
        "registered_dependency_candidate_counts": alternate_candidates,
        "registered_minimal_proof_unique": not non_unique_dependencies,
        "decisive_exact_surface_substitutes": duplicated_decisive_surface,
        "fact_surface_candidate_counts": fact_surface_candidate_counts,
        "public_surface_proof_unique": (
            not duplicated_decisive_surface and not non_unique_fact_surface
        ),
        "claim_boundary": (
            "Fact necessity is causal under a reproduced countermodel. Rule, identity "
            "and authority necessity is structural under the declared proof contract."
        ),
    }


def audit_proof_certificates(release_dir: Path) -> dict[str, Any]:
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    certificates: list[dict[str, Any]] = []
    for match_id in map(str, summary.get("match_ids", [])):
        public = _read(release_dir / "public" / match_id / "public_instance.json")
        gold = _read(release_dir / "private" / match_id / "private_gold.json")
        evidence = _read(release_dir / "private" / match_id / "private_evidence.json")
        instance = audit_proof_instance(public, gold, evidence)
        for certificate in instance["certificates"]:
            certificate["match_id"] = match_id
            certificates.append(certificate)
    status_counts = Counter(item["status"] for item in certificates)
    errors = [
        f"{item['match_id']}:{item['question_id']}:{error}"
        for item in certificates for error in item["errors"]
    ]
    by_level = {
        level: {
            "questions": sum(item["level"] == level for item in certificates),
            "passed": sum(
                item["level"] == level and item["status"] == "PASS"
                for item in certificates
            ),
            "mean_decisive_spans": round(
                sum(item["decisive_spans"] for item in certificates if item["level"] == level)
                / max(1, sum(item["level"] == level for item in certificates)),
                6,
            ),
        }
        for level in ("L1", "L2", "L3", "L4", "L5")
    }
    return {
        "protocol_version": "VETT-R26.13-PROOF-CERTIFICATE-AUDIT-1",
        "status": "PASS" if not errors and certificates else "FAIL",
        "errors": errors,
        "matches": len(set(item["match_id"] for item in certificates)),
        "questions": len(certificates),
        "status_counts": dict(sorted(status_counts.items())),
        "by_level": by_level,
        "minimal_fact_reconstruction_passes": sum(
            item["minimal_fact_reconstruction"] for item in certificates
        ),
        "single_edge_deletion_passes": sum(
            item["all_single_edge_deletions_detected"] for item in certificates
        ),
        "unique_registered_proof_passes": sum(
            item["registered_minimal_proof_unique"] for item in certificates
        ),
        "unique_public_surface_proof_passes": sum(
            item["public_surface_proof_unique"] for item in certificates
        ),
        "certificates": certificates,
    }


def audit_proof_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    public_ids = {
        str(span["span_id"])
        for document in public.get("documents", [])
        for span in document.get("spans", [])
    }
    public_text = {
        str(span["span_id"]): str(span["text"])
        for document in public.get("documents", [])
        for span in document.get("spans", [])
    }
    claims = list(evidence.get("r25_evidence_claims", [])) + list(
        evidence.get("r26_evidence_claims", [])
    )
    certificates = [
        _audit_question(answer, claims, public_ids, public_text)
        for answer in gold.get("decision_answers", [])
    ]
    errors = [
        f"{item['question_id']}:{error}"
        for item in certificates for error in item["errors"]
    ]
    return {
        "status": "PASS" if certificates and not errors else "FAIL",
        "errors": errors,
        "questions": len(certificates),
        "certificates": certificates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-proof-audit")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit_proof_certificates(args.release)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        key: value for key, value in report.items() if key != "certificates"
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["audit_proof_certificates", "audit_proof_instance"]
