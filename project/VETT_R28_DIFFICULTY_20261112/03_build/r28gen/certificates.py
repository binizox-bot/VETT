"""Deterministic certificates: evidence necessity, rule path, replay, authority.

Everything in this module is computed from the frozen solver and the rendered span
registry - no language model writes any part of a certificate.

Evidence tiers (each backed by a mechanical removal test on this arm's dossier):

``minimum_evidence_spans``
    Spans whose removal either changes the record or makes the derivation
    unresolvable: pivotal facts, the rules of necessary operators, the identity
    binding chain, the revision policy and the currently controlling version, and
    the authority policy that adjudicates a conflict.
``rejected_evidence_spans``
    Conflicting claims from the non-controlling source.  They must be explicitly
    set aside; they are not evidence to cite.
``process_support_spans``
    Superseded versions: needed to see the revision chain, not part of a strict
    minimum (removing them does not change the answer).
``context_spans`` / ``distractor_spans``
    Non-pivotal facts, presentation-only rules and parallel incidents.
"""

from __future__ import annotations

from typing import Any

from .canonical import canon, sha256_text
from .constants import CERTIFICATE_SCHEMA
from .derivation import (
    NECESSARY,
    analyse_derivation,
    fact_pivot_scan,
    run_pipeline,
)
from .doses import DoseSet, resolve_revisions
from .solver_bridge import solve_flat


def drop_fact_test(facts: dict[str, Any], field_name: str, *, gold_sha256: str) -> dict[str, Any]:
    """Remove one fact (the span is absent) and re-derive.

    Returns ``UNRESOLVED``, ``RECORD_CHANGES`` or ``NO_EFFECT``.  A fact whose
    absence changes or blocks the derivation is genuinely required in the evidence
    set; a fact whose absence changes nothing is context only.
    """

    trimmed = {key: value for key, value in facts.items() if key != field_name}
    try:
        result = run_pipeline(trimmed)
    except Exception as exc:  # noqa: BLE001
        return {"outcome": "UNRESOLVED", "detail": f"{type(exc).__name__}: {exc}"}
    if not result.resolved:
        return {"outcome": "UNRESOLVED", "detail": result.unresolved}
    if result.flat_sha256 != gold_sha256:
        changed = sorted(
            key for key in result.flat
            if result.flat.get(key) != (solve_flat(facts)[1].get(key))
        )
        return {"outcome": "RECORD_CHANGES", "changed_fields": changed,
                "record_sha256": result.flat_sha256}
    return {"outcome": "NO_EFFECT"}


def _edges(
    question_id: str,
    *,
    binding_chain: list[str],
    authority_span: str | None,
    fact_spans: list[str],
    conflict_spans: list[str],
    rule_spans: list[str],
    start_span: str | None,
) -> list[dict[str, str]]:
    decision = f"decision:{question_id}"

    def edge(source: str, relation: str, target: str) -> dict[str, str]:
        return {"source_id": source, "relation": relation, "target_id": target}

    rows: list[dict[str, str]] = []
    head = binding_chain[0] if binding_chain else start_span
    if head:
        rows.append(edge(question_id, "identifies", head))
    rows.extend(
        edge(source, "resolves_to", target)
        for source, target in zip(binding_chain, binding_chain[1:])
    )
    terminal = binding_chain[-1] if binding_chain else None
    if authority_span:
        if terminal:
            rows.append(edge(terminal, "governed_by", authority_span))
        rows.extend(edge(authority_span, "authorizes", span) for span in fact_spans)
        rows.extend(edge(authority_span, "rejects", span) for span in conflict_spans)
    rows.extend(edge(span, "supports_decision", decision) for span in fact_spans)
    rows.extend(edge(span, "governs_decision", decision) for span in rule_spans)
    unique = {(row["source_id"], row["relation"], row["target_id"]): row for row in rows}
    return [unique[key] for key in sorted(unique)]


def build_certificate(
    *,
    question_id: str,
    arm: str,
    dataset_version: str,
    facts: dict[str, Any],
    flat: dict[str, Any],
    analysis,  # DerivationAnalysis
    pivot_scan: dict[str, Any],
    span_index: dict[str, Any],
    dose_set: DoseSet,
    solver_provenance: dict[str, Any],
) -> dict[str, Any]:
    """Build one arm's certificate from the rendered span registry."""

    gold_sha = sha256_text(canon(flat))
    fact_rows: list[dict[str, Any]] = []
    minimum: list[str] = []
    context: list[str] = []
    for field_name in sorted(facts):
        span_id = span_index["fact"].get(field_name)
        if span_id is None:
            continue  # carried by a revision chain instead
        drop = drop_fact_test(facts, field_name, gold_sha256=gold_sha)
        flip = next(
            (row["countermodel"] for row in pivot_scan["fields"] if row["field"] == field_name),
            None,
        )
        necessary = drop["outcome"] in {"UNRESOLVED", "RECORD_CHANGES"}
        row = {
            "span_id": span_id,
            "field": field_name,
            "value": facts[field_name],
            "dependency": "PIVOTAL_FACT",
            "removal_result": drop["outcome"],
            "removal_detail": drop.get("detail") or drop.get("changed_fields"),
            "countermodel": flip,
            "in_minimum_evidence": necessary,
        }
        fact_rows.append(row)
        (minimum if necessary else context).append(span_id)

    rule_rows: list[dict[str, Any]] = []
    presentation_rows: list[dict[str, Any]] = []
    for operator_row in analysis.operators:
        rule_key = operator_row.get("rule_key")
        if not operator_row["fired"] or not rule_key:
            continue
        span_id = span_index["rule"].get(rule_key)
        verdict = operator_row["verdict"]
        necessary = verdict == NECESSARY
        row = {
            "operator_id": operator_row["operator_id"],
            "rule_key": rule_key,
            "span_id": span_id,
            "verdict": verdict,
            "necessity_kind": operator_row["necessity_kind"],
            "removal_result": (
                "UNRESOLVED_RULE_JUSTIFICATION" if necessary else "NO_EFFECT"
            ),
        }
        if necessary:
            # rule_path carries ONLY load-bearing operators (t6 requirement 5)
            rule_rows.append(row)
            if span_id:
                minimum.append(span_id)
        else:
            presentation_rows.append(row)

    binding_rows: list[dict[str, Any]] = []
    for order, span_id in enumerate(span_index["binding"]):
        binding_rows.append({
            "span_id": span_id,
            "dependency": "IDENTITY_BINDING",
            "removal_result": "UNRESOLVED_SEMANTIC_TARGET",
            "order": order,
            "in_minimum_evidence": True,
        })
        minimum.append(span_id)

    revision_decision: dict[str, Any] | None = None
    revision_witness = dose_set.mechanisms["D2"].witness
    if span_index["revision_policy"]:
        revision_decision = {
            "policy": revision_witness.get("policy"),
            "policy_span_id": span_index["revision_policy"],
            "cells_revised": revision_witness.get("cells_revised"),
            "version_count": revision_witness.get("version_count"),
            "replay_order": revision_witness.get("replay_order"),
            "replay_trace": revision_witness.get("replay_trace"),
            "recovered_values": revision_witness.get("recovered_values"),
            "gold_values": revision_witness.get("gold_values"),
            "recovered_equals_gold": revision_witness.get("recovered_equals_gold"),
            "removal_result": "UNRESOLVED_REVISION_PRECEDENCE",
        }
        minimum.append(span_index["revision_policy"])
        minimum.extend(span_index["revision_current"])

    authority_decision: dict[str, Any] | None = None
    masked_cell: dict[str, Any] | None = None
    rejected: list[str] = []
    authority_witness = dose_set.mechanisms["D3"].witness
    if span_index["authority_policy"]:
        rejected = list(span_index["conflicts"])
        authority_decision = {
            "policy": authority_witness.get("policy"),
            "policy_span_id": span_index["authority_policy"],
            "conflicts": authority_witness.get("conflicts"),
            "adjudications": authority_witness.get("adjudications"),
            "resolved_facts_sha256": authority_witness.get("resolved_facts_sha256"),
            "gold_facts_sha256": authority_witness.get("gold_facts_sha256"),
            "resolved_equals_gold": authority_witness.get("resolved_equals_gold"),
            "removal_result": "UNRESOLVED_SOURCE_AUTHORITY",
        }
        minimum.append(span_index["authority_policy"])
        masked = authority_witness.get("masked_cells") or []
        if masked:
            masked_cell = masked[0]

    why_not_distractor = dose_set.mechanisms["D4"].witness.get("distractors") or []

    derivation_check = {
        "operator_version": analysis.operator_version,
        "replayed_record_sha256": analysis.record_sha256,
        "gold_record_sha256": gold_sha,
        "replay_equal": analysis.record_sha256 == gold_sha,
        "steps_sha256": sha256_text(canon(analysis.steps)),
        "operator_count_fired": sum(1 for row in analysis.operators if row["fired"]),
        "derivation_depth_verified": analysis.derivation_depth_verified,
        "derivation_depth_content": analysis.derivation_depth_content,
        "derivation_depth_structural": analysis.derivation_depth_structural,
        "necessary_operators": analysis.necessary,
        "presentation_only_operators": analysis.presentation_only,
        "not_on_path_operators": analysis.not_on_path,
        "operators": analysis.operators,
        "solver_equivalence": {
            "module": "vett_r25.solver",
            "sha256": solver_provenance["sha256"],
            "flat_record_equal": canon(solve_flat(facts)[1]) == canon(flat),
        },
    }

    evidence_edges = _edges(
        question_id,
        binding_chain=span_index["binding"],
        authority_span=span_index["authority_policy"],
        fact_spans=span_index["fact"].values() if isinstance(span_index["fact"], dict) else [],
        conflict_spans=rejected,
        rule_spans=[row["span_id"] for row in rule_rows if row["span_id"]],
        start_span=next(iter(span_index["fact"].values()), None) if span_index["fact"] else None,
    )

    return {
        "schema": CERTIFICATE_SCHEMA,
        "question_id": question_id,
        "arm": arm,
        "dataset_version": dataset_version,
        "solver": {
            "module": solver_provenance["module"],
            "sha256": solver_provenance["sha256"],
            "scenarios_sha256": solver_provenance["scenarios_sha256"],
        },
        "solver_facts_sha256": sha256_text(canon(facts)),
        "decision_record_flat_sha256": gold_sha,
        "decision_record_flat": dict(flat),
        "minimum_evidence_spans": sorted(set(minimum)),
        "minimum_evidence_count": len(set(minimum)),
        "evidence_necessity": fact_rows + binding_rows,
        "rejected_evidence_spans": sorted(set(rejected)),
        "process_support_spans": sorted(span_index["revision_superseded"]),
        "context_spans": sorted(set(context)),
        "distractor_spans": sorted(span_index["distractors"]),
        "masked_cell_spans": sorted(span_index["masked"]),
        "rule_path": rule_rows,
        "rule_path_rule_keys": [row["rule_key"] for row in rule_rows],
        "presentation_only_operators": presentation_rows,
        "presentation_only_rule_keys": sorted({row["rule_key"] for row in presentation_rows}),
        "authority_decision": authority_decision,
        "revision_chain": revision_decision,
        "masked_cell": masked_cell,
        "why_not_distractor": why_not_distractor,
        "derivation_check": derivation_check,
        "evidence_edges": evidence_edges,
        "dose_assignment": dict(dose_set.doses),
        "dose_witness_digest": sha256_text(canon(dose_set.witness())),
    }


# ---------------------------------------------------------------------------
# Replay: reconstruct the facts from the dossier span registry only
# ---------------------------------------------------------------------------
def reconstruct_facts(
    present_span_ids: set[str],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Rebuild ``solver_facts`` from the spans that are actually present.

    The reconstruction is deliberately mechanical: direct fact spans fill cells,
    revision chains are replayed with the stated policy, conflicts are set aside
    because the policy names the controlling source, and masked cells are taken
    from the signed copy.  A missing controlling span therefore produces a
    different fact set (or an explicit failure), which is what makes the
    certificate replay a real check rather than a tautology.
    """

    facts: dict[str, Any] = {}
    missing: list[str] = []
    for span_id, payload in evidence["fact_spans"].items():
        if span_id not in present_span_ids:
            missing.append(span_id)
            continue
        facts.update(payload)

    revisions = evidence.get("revisions") or []
    if revisions:
        policy_span = evidence.get("revision_policy_span")
        if policy_span and policy_span not in present_span_ids:
            return {"ok": False, "reason": "revision policy span absent", "facts": facts,
                    "missing": missing + [policy_span]}
        present_versions = [
            version for version in revisions
            if f"r28rev_{version['version_id'].lower()}" in present_span_ids
        ]
        if len(present_versions) != len(revisions):
            return {
                "ok": False,
                "reason": "revision chain incomplete",
                "facts": facts,
                "missing": missing + [
                    f"r28rev_{version['version_id'].lower()}"
                    for version in revisions
                    if f"r28rev_{version['version_id'].lower()}" not in present_span_ids
                ],
            }
        replay = resolve_revisions(present_versions, str(evidence["revision_policy"]))
        facts.update(replay["chosen"])
        revision_trace = replay["trace"]
    else:
        revision_trace = []

    conflicts = evidence.get("conflicts") or []
    if conflicts:
        policy_span = evidence.get("authority_policy_span")
        if policy_span and policy_span not in present_span_ids:
            return {"ok": False, "reason": "authority policy span absent", "facts": facts,
                    "missing": missing + [policy_span]}
        for conflict in conflicts:
            if conflict["span_id"] in present_span_ids:
                # explicitly rejected: the controlling source supplies the cell
                facts[conflict["cell"]] = conflict["resolved_value"]

    return {
        "ok": True,
        "facts": facts,
        "missing": missing,
        "revision_trace": revision_trace,
    }


def replay_certificate_arm(
    *,
    certificate: dict[str, Any],
    present_span_ids: set[str],
    evidence: dict[str, Any],
    expected_facts: dict[str, Any],
    expected_flat: dict[str, Any],
) -> dict[str, Any]:
    """End-to-end replay of one arm: dossier -> facts -> record -> certificate."""

    reconstruction = reconstruct_facts(present_span_ids, evidence)
    problems: list[str] = []
    if not reconstruction["ok"]:
        problems.append(str(reconstruction["reason"]))
    facts = reconstruction["facts"]
    if canon(facts) != canon(expected_facts):
        problems.append("reconstructed facts differ from solver_facts")
    try:
        _, flat, flat_sha = solve_flat(facts)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "problems": problems + [f"solver rejected reconstructed facts: {exc}"],
            "reconstructed_facts_sha256": sha256_text(canon(facts)),
        }
    if canon(flat) != canon(expected_flat):
        problems.append("replayed record differs from the gold record")
    if flat_sha != certificate["decision_record_flat_sha256"]:
        problems.append("replayed record digest differs from the certificate digest")
    if certificate["solver_facts_sha256"] != sha256_text(canon(expected_facts)):
        problems.append("certificate facts digest mismatch")
    minimum = set(certificate["minimum_evidence_spans"])
    absent = sorted(minimum - present_span_ids)
    if absent:
        problems.append(f"minimum evidence spans absent from the dossier: {absent}")
    return {
        "ok": not problems,
        "problems": problems,
        "reconstructed_facts_sha256": sha256_text(canon(facts)),
        "replayed_record_sha256": flat_sha,
        "minimum_evidence_present": not absent,
        "revision_trace_steps": len(reconstruction.get("revision_trace") or []),
    }


def analyse_instance(facts: dict[str, Any], domains: dict[str, list]) -> tuple[Any, dict[str, Any]]:
    """Convenience: derivation analysis + countermodel scan for one fact set."""

    analysis = analyse_derivation(facts)
    pivot_scan = fact_pivot_scan(facts, domains, gold_sha256=analysis.record_sha256)
    return analysis, pivot_scan


__all__ = [
    "analyse_instance",
    "build_certificate",
    "drop_fact_test",
    "reconstruct_facts",
    "replay_certificate_arm",
]
