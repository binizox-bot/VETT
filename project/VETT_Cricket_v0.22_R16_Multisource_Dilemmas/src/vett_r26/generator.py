from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

from vett_r25.generator import FACT_DOMAINS

from .anchors import ANCHOR_BY_SCENARIO_FAMILY
from .operators import operator_profile
from .renderer import authority_contract, authority_policy_text, bridge_text, conflict_text, fact_text, question_text, rule_text
from .scenario_kernel import counterfactual_blast_radius, digest, natural_identity
from .spec import (
    BASE_VERSION,
    DEFAULT_SEED,
    DIFFICULTY_DESIGN_REVISION,
    MEASUREMENT_VALIDITY_VERSION,
    SEMANTIC_BRIDGE_DEPTH,
    VERSION,
)


TEMPORAL_REASONING_RULES = {
    "EARLY_DEAD",
    "CAUGHT_CONTROL",
    "DEAD_SEQUENCE",
    "OVERTHROW",
    "DECEPTION",
}


@dataclass(frozen=True)
class Bundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


def _clone(value: Any) -> Any:
    return copy.deepcopy(value)


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _span_index(documents: list[dict[str, Any]]) -> dict[str, tuple[dict[str, Any], int]]:
    result: dict[str, tuple[dict[str, Any], int]] = {}
    for document in documents:
        for index, span in enumerate(document["spans"]):
            result[str(span["span_id"])] = (document, index)
    return result


def _replace_span(
    documents: list[dict[str, Any]],
    span_id: str,
    text: str,
    patches: list[dict[str, Any]],
) -> None:
    lookup = _span_index(documents)
    if span_id not in lookup:
        raise KeyError(f"R26 replacement span is absent: {span_id}")
    document, index = lookup[span_id]
    old_text = str(document["spans"][index]["text"])
    document["spans"][index]["text"] = text
    patches.append({
        "operation": "replace_r25_span",
        "document_id": document["document_id"],
        "span_index": index,
        "span_id": span_id,
        "old_text": old_text,
        "new_text": text,
    })


def _insert_span(
    documents: list[dict[str, Any]],
    span_id: str,
    text: str,
    *,
    identity: tuple[object, ...],
    patches: list[dict[str, Any]],
) -> None:
    doc_index = int(digest(*identity, "document")[:8], 16) % len(documents)
    spans = documents[doc_index]["spans"]
    span_index = int(digest(*identity, "position")[:8], 16) % (len(spans) + 1)
    spans.insert(span_index, {"span_id": span_id, "text": text})
    patches.append({
        "operation": "insert",
        "document_id": documents[doc_index]["document_id"],
        "span_index": span_index,
        "inserted_span_id": span_id,
        "text": text,
    })


def reconstruct_r25_documents(
    r26_documents: list[dict[str, Any]],
    patches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    documents = _clone(r26_documents)
    for patch in reversed(patches):
        lookup = _span_index(documents)
        if patch["operation"] == "insert":
            span_id = patch["inserted_span_id"]
            if span_id not in lookup:
                raise KeyError(f"R26 inserted span missing during reconstruction: {span_id}")
            document, index = lookup[span_id]
            document["spans"].pop(index)
        elif patch["operation"] == "replace_r25_span":
            span_id = patch["span_id"]
            if span_id not in lookup:
                raise KeyError(f"R26 replacement span missing during reconstruction: {span_id}")
            document, index = lookup[span_id]
            if str(document["spans"][index]["text"]) != str(patch["new_text"]):
                raise ValueError(f"R26 replacement text drift: {span_id}")
            document["spans"][index]["text"] = patch["old_text"]
        else:
            raise ValueError(f"unknown R26 patch operation: {patch['operation']}")
    for document in documents:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    return documents


def _semantic_projection(gold: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "question_id": answer["question_id"],
        "scenario_family": answer["scenario_family"],
        "level": answer["level"],
        "decision_record": answer["decision_record"],
        "state": answer["state"],
        "minimum_evidence_spans": answer["minimum_evidence_spans"],
        "counterfactual": answer["counterfactual"],
        "rule_keys": answer["rule_keys"],
    } for answer in gold["decision_answers"]]


def _context_band(estimated_tokens: int) -> str:
    if estimated_tokens < 24_000:
        return "16K"
    if estimated_tokens < 48_000:
        return "32K"
    if estimated_tokens < 80_000:
        return "64K"
    return "96K_PLUS"


def _alternate_fact_value(field: str, value: Any, *, identity: tuple[object, ...]) -> Any:
    choices = [candidate for candidate in FACT_DOMAINS[field] if candidate != value]
    return choices[int(digest(*identity, field, "alternate")[:8], 16) % len(choices)]


def _edge(source_id: str, relation: str, target_id: str) -> dict[str, str]:
    return {"source_id": source_id, "relation": relation, "target_id": target_id}


def _build_evidence_edges(
    *,
    question_id: str,
    bridge_ids: list[str],
    authority_id: str,
    fact_ids: list[str],
    conflict_ids: list[str],
    rule_ids: list[str],
) -> list[dict[str, str]]:
    decision_id = f"decision:{question_id}"
    edges = [_edge(question_id, "identifies", bridge_ids[0])]
    edges.extend(
        _edge(source, "resolves_to", target)
        for source, target in zip(bridge_ids, bridge_ids[1:])
    )
    if authority_id != bridge_ids[-1]:
        edges.append(_edge(bridge_ids[-1], "governed_by", authority_id))
    edges.extend(_edge(authority_id, "authorizes", span_id) for span_id in fact_ids)
    edges.extend(_edge(authority_id, "rejects", span_id) for span_id in conflict_ids)
    edges.extend(_edge(span_id, "supports_decision", decision_id) for span_id in fact_ids)
    edges.extend(_edge(span_id, "governs_decision", decision_id) for span_id in rule_ids)
    unique = {(edge["source_id"], edge["relation"], edge["target_id"]): edge for edge in edges}
    return [unique[key] for key in sorted(unique)]


def _difficulty_vector(
    public: dict[str, Any],
    answer: dict[str, Any],
    *,
    semantic_bridge_depth: int,
) -> dict[str, Any]:
    locations: dict[str, tuple[int, int, int]] = {}
    all_spans: list[tuple[str, int, int]] = []
    characters = 0
    for doc_index, document in enumerate(public["documents"]):
        count = len(document["spans"])
        for span_index, span in enumerate(document["spans"]):
            span_id = str(span["span_id"])
            locations[span_id] = (doc_index, span_index, count)
            all_spans.append((span_id, doc_index, span_index))
            characters += len(str(span["text"]))
    global_order = {span_id: index for index, (span_id, _, _) in enumerate(all_spans)}
    decisive = list(map(str, answer["minimum_evidence_spans"]))
    normalized = [global_order[span_id] / max(1, len(all_spans) - 1) for span_id in decisive]
    mean = sum(normalized) / len(normalized)
    dispersion = math.sqrt(sum((value - mean) ** 2 for value in normalized) / len(normalized))
    evidence_docs = {locations[span_id][0] for span_id in decisive}
    blast, changed_outputs = counterfactual_blast_radius(answer)
    estimated_tokens = math.ceil(characters / 4)
    base_graph = answer.get("difficulty_graph", {})
    profile = operator_profile(answer.get("rule_keys", []))
    if answer.get("difficulty_design_revision") == DIFFICULTY_DESIGN_REVISION:
        authority_decisions = int(any(
            edge.get("relation") in {"authorizes", "rejects"}
            for edge in answer.get("minimum_evidence_edges", [])
        ))
        # Revision precedence and pre-lock precedence are ordered-source
        # dependencies expressed in the public authority text.  Count them
        # from the observed active-source policy, not from the private level.
        source_order_depth = int(
            str(answer.get("state", {}).get("active_source", ""))
            in {"HIGHEST_REVISION", "LAST_PRE_LOCK"}
        )
        temporal_depth = min(
            2,
            source_order_depth + sum(
                str(rule_key) in TEMPORAL_REASONING_RULES
                for rule_key in set(answer.get("rule_keys", []))
            ),
        )
    else:
        authority_decisions = int(base_graph.get("scope_decisions", 0))
        temporal_depth = int(base_graph.get("temporal_joins", 0))
    return {
        "context_band": _context_band(estimated_tokens),
        "estimated_context_tokens": estimated_tokens,
        "evidence_span_count": len(decisive),
        "evidence_doc_count": len(evidence_docs),
        "evidence_dispersion": round(dispersion, 6),
        "evidence_position_mean": round(mean, 6),
        "lexical_bridge_depth": semantic_bridge_depth,
        "binding_collision_count": len(answer.get("distractor_spans", [])),
        "hard_negative_similarity": "HIGH" if answer.get("distractor_spans") else "NONE",
        "temporal_depth": temporal_depth,
        "authority_decisions": authority_decisions,
        **profile,
        "derivation_depth": max(1, int(base_graph.get("rule_operators", 1))),
        "global_coverage": round(len(evidence_docs) / max(1, len(public["documents"])), 6),
        "counterfactual_path_length": semantic_bridge_depth + max(1, int(base_graph.get("rule_operators", 1))),
        "counterfactual_blast_radius": blast,
        "counterfactual_changed_outputs": list(changed_outputs),
        "output_payload": 7,
    }


def augment_r25_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    *,
    seed: int = DEFAULT_SEED,
    variant_index: int = 0,
    dataset_version: str = VERSION,
    candidate_difficulty_design: bool = False,
) -> Bundle:
    versions = {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")}
    if versions != {BASE_VERSION}:
        raise ValueError(f"R26 requires frozen R25.2 base, found {versions}")
    match_id = str(public["instance_id"])
    naturalized_v2 = dataset_version == MEASUREMENT_VALIDITY_VERSION
    if {match_id, str(gold.get("instance_id")), str(evidence.get("instance_id"))} != {match_id}:
        raise ValueError("R25 base instance IDs do not match")

    result_public, result_gold, result_evidence = _clone(public), _clone(gold), _clone(evidence)
    documents = result_public["documents"]
    patches: list[dict[str, Any]] = []
    new_claims: list[dict[str, Any]] = []
    base_projection = _semantic_projection(gold)
    claims = result_evidence["r25_evidence_claims"]
    claim_by_id = {str(claim["inserted_span_id"]): claim for claim in claims}
    question_claims: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        qid = claim.get("question_id")
        if qid:
            question_claims.setdefault(str(qid), []).append(claim)

    # Shared rule text is rewritten once into cricket-native source genres.
    for claim in claims:
        if claim.get("role") == "rule":
            _replace_span(
                documents,
                str(claim["inserted_span_id"]),
                rule_text(str(claim["rule_key"]), match_id=match_id),
                patches,
            )

    public_questions = {str(item["question_id"]): item for item in result_public["decision_question_schema"]}
    for item_index, answer in enumerate(result_gold["decision_answers"]):
        qid = str(answer["question_id"])
        level = str(answer["level"])
        depth = SEMANTIC_BRIDGE_DEPTH[level]
        identity = natural_identity(
            match_id,
            qid,
            gold,
            index=item_index + variant_index,
            depth=depth,
            fixture_context=dataset_version == MEASUREMENT_VALIDITY_VERSION,
        )
        item_claims = question_claims.get(qid, [])
        active_source = str(answer.get("state", {}).get("active_source", "DIRECT_OBSERVATION"))
        separate_authority = level in {"L1", "L2"}
        existing_bridge_claims = [
            claim for claim in item_claims if claim.get("role") in {"locator", "bridge"}
        ]
        bridge_ids = [str(claim["inserted_span_id"]) for claim in existing_bridge_claims]
        while len(bridge_ids) < depth:
            hop = len(bridge_ids) + 1
            span_id = f"r26bridge_{digest(seed, match_id, qid, hop)[:20]}"
            source = identity.target_description if hop == 1 else identity.labels[hop - 2]
            target = identity.labels[hop - 1]
            text = bridge_text(
                source,
                target,
                hop=hop,
                identity=identity,
                authority_contract=(
                    authority_contract(active_source, key=qid)
                    if hop == depth and not separate_authority else None
                ),
                naturalized_v2=naturalized_v2,
            )
            _insert_span(
                documents,
                span_id,
                text,
                identity=(seed, match_id, qid, hop, "semantic-bridge"),
                patches=patches,
            )
            bridge_ids.append(span_id)
            new_claims.append({
                "question_id": qid,
                "inserted_span_id": span_id,
                "role": "semantic_bridge",
                "hop": hop,
                "source_label": source,
                "target_label": target,
            })

        for hop, span_id in enumerate(bridge_ids, start=1):
            source = identity.target_description if hop == 1 else identity.labels[hop - 2]
            target = identity.labels[hop - 1]
            _replace_span(
                documents,
                span_id,
                bridge_text(
                    source,
                    target,
                    hop=hop,
                    identity=identity,
                    authority_contract=(
                        authority_contract(active_source, key=qid)
                        if hop == depth and not separate_authority else None
                    ),
                    naturalized_v2=naturalized_v2,
                ),
                patches,
            ) if span_id in claim_by_id else None

        terminal_subject = identity.labels[-1]
        authority_policy_id: str | None = None
        if separate_authority:
            authority_policy_id = f"r26authority_{digest(seed, match_id, qid)[:20]}"
            authority_text = authority_policy_text(
                terminal_subject,
                active_source,
                question_id=qid,
            )
            _insert_span(
                documents,
                authority_policy_id,
                authority_text,
                identity=(seed, match_id, qid, "authority-policy"),
                patches=patches,
            )
            new_claims.append({
                "question_id": qid,
                "inserted_span_id": authority_policy_id,
                "role": "authority_policy",
                "active_source": active_source,
            })
        incident_claims = [claim for claim in item_claims if claim.get("role") == "incident_fact"]
        authority_conflicts = [
            claim for claim in item_claims if claim.get("role") in {"same_case_conflict", "other_incident_fact"}
        ]
        if not authority_conflicts:
            fact_claim = incident_claims[0]
            field = str(fact_claim["field"])
            alternate = _alternate_fact_value(field, fact_claim["value"], identity=(seed, match_id, qid, 0))
            span_id = f"r26conflict_{digest(seed, match_id, qid, field)[:20]}"
            _insert_span(
                documents,
                span_id,
                conflict_text(
                    terminal_subject,
                    field,
                    alternate,
                    active_source=active_source,
                    question_id=qid,
                    naturalized_v2=naturalized_v2,
                ),
                identity=(seed, match_id, qid, "authority-conflict"),
                patches=patches,
            )
            authority_conflicts.append({
                "question_id": qid,
                "inserted_span_id": span_id,
                "role": "authority_conflict",
                "field": field,
                "value": alternate,
            })
            new_claims.append(authority_conflicts[-1])
            answer.setdefault("distractor_spans", []).append(span_id)

        repurposed_conflicts: list[str] = []
        for conflict_index, claim in enumerate(authority_conflicts):
            fact_claim = incident_claims[conflict_index % len(incident_claims)]
            field = str(fact_claim["field"])
            alternate = _alternate_fact_value(
                field,
                fact_claim["value"],
                identity=(seed, match_id, qid, conflict_index),
            )
            span_id = str(claim["inserted_span_id"])
            if span_id in claim_by_id:
                _replace_span(
                    documents,
                    span_id,
                    conflict_text(
                        terminal_subject,
                        field,
                        alternate,
                        active_source=active_source,
                        question_id=qid,
                        naturalized_v2=naturalized_v2,
                    ),
                    patches,
                )
                claim["r26_original_role"] = claim.get("role")
                claim["role"] = "same_case_conflict"
                claim["field"] = field
                claim["value"] = alternate
            repurposed_conflicts.append(span_id)
        for claim in item_claims:
            role = str(claim.get("role"))
            span_id = str(claim["inserted_span_id"])
            if role == "incident_fact":
                _replace_span(
                    documents,
                    span_id,
                    fact_text(
                        terminal_subject,
                        str(claim["field"]),
                        claim["value"],
                        question_id=qid,
                        active_source=active_source,
                        naturalized_v2=naturalized_v2,
                    ),
                    patches,
                )
            elif role == "same_case_conflict":
                if span_id in repurposed_conflicts:
                    continue
                _replace_span(
                    documents,
                    span_id,
                    fact_text(terminal_subject, str(claim["field"]), claim["value"], question_id=qid, shadow=True),
                    patches,
                )
            elif role == "other_incident_fact":
                if span_id in repurposed_conflicts:
                    continue
                alternate = f"the parallel {identity.bowler.split()[-1]} review in over {identity.over_number + 1}"
                _replace_span(
                    documents,
                    span_id,
                    fact_text(alternate, str(claim["field"]), claim["value"], question_id=qid, shadow=True),
                    patches,
                )
            elif role == "source_policy":
                old = _span_index(documents)[span_id][0]["spans"][_span_index(documents)[span_id][1]]["text"]
                policy = str(old).split(": ", 1)[-1]
                _replace_span(
                    documents,
                    span_id,
                    f"The signed match-control procedure for {terminal_subject} states: {policy} "
                    f"{authority_contract(active_source, key=qid)}",
                    patches,
                )

        question = public_questions[qid]
        intervention = answer["counterfactual"]
        question["question"] = question_text(identity, intervention["changed_field"], intervention["new_value"])
        question.pop("level", None)
        question["r26_public_contract"] = {
            "single_atomic_intervention": True,
            "difficulty_label_is_private": True,
            "minimum_evidence_required": True,
            "evidence_span_roles": {
                "evidence_spans": "decisive positive spans only: identity, authority, accepted facts and governing rules",
                "rejected_evidence_spans": "same-incident conflicting fact spans that must be explicitly rejected",
            },
            "evidence_edge_relations": [
                "identifies", "resolves_to", "governed_by", "authorizes", "rejects",
                "supports_decision", "governs_decision",
            ],
            "decision_node": f"decision:{qid}",
        }

        answer["r25_minimum_evidence_spans"] = list(answer["minimum_evidence_spans"])
        added_bridge_ids = [span_id for span_id in bridge_ids if span_id not in answer["minimum_evidence_spans"]]
        answer["minimum_evidence_spans"] = list(dict.fromkeys(answer["minimum_evidence_spans"] + added_bridge_ids))
        if authority_policy_id:
            answer["minimum_evidence_spans"].append(authority_policy_id)
            answer["evidence_necessity"].append({
                "span_id": authority_policy_id,
                "dependency": "SOURCE_AUTHORITY",
                "removal_result": "UNRESOLVED_SOURCE_AUTHORITY",
            })
        answer["semantic_bridge_spans"] = bridge_ids
        answer["authority_policy_span"] = authority_policy_id
        answer["semantic_bridge_depth"] = depth
        answer["natural_identity"] = {
            "batter": identity.batter,
            "bowler": identity.bowler,
            "over_number": identity.over_number,
            "minute": identity.minute,
            "target_description": identity.target_description,
            "terminal_subject": terminal_subject,
        }
        existing_policy = next(
            (str(claim["inserted_span_id"]) for claim in item_claims if claim.get("role") == "source_policy"),
            None,
        )
        authority_id = authority_policy_id or existing_policy or bridge_ids[-1]
        rule_span_ids = [
            str(claim["inserted_span_id"])
            for claim in claims
            if claim.get("role") == "rule" and claim.get("rule_key") in set(answer["rule_keys"])
        ]
        answer["minimum_evidence_edges"] = _build_evidence_edges(
            question_id=qid,
            bridge_ids=bridge_ids,
            authority_id=authority_id,
            fact_ids=[str(claim["inserted_span_id"]) for claim in incident_claims],
            conflict_ids=repurposed_conflicts,
            rule_ids=rule_span_ids,
        )
        answer["rejected_evidence_spans"] = sorted(set(repurposed_conflicts))
        answer["evidence_graph_contract"] = {
            "authority_span": authority_id,
            "conflict_spans": repurposed_conflicts,
            "query_node": qid,
            "decision_node": f"decision:{qid}",
            "edge_count": len(answer["minimum_evidence_edges"]),
        }
        for span_id in added_bridge_ids:
            answer["evidence_necessity"].append({
                "span_id": span_id,
                "dependency": "SEMANTIC_TARGET_BINDING",
                "removal_result": "UNRESOLVED_SEMANTIC_TARGET_BINDING",
            })
        answer["r26_no_regression"] = {
            "r25_decision_record_sha256": _hash(answer["decision_record"]),
            "r25_counterfactual_record_sha256": _hash(answer["counterfactual"]["decision_record"]),
            "r25_evidence_is_subset": True,
        }
        if candidate_difficulty_design:
            answer["cross_level_anchor_family"] = ANCHOR_BY_SCENARIO_FAMILY[
                str(answer["scenario_family"])
            ]
            answer["difficulty_design_revision"] = DIFFICULTY_DESIGN_REVISION

    for document in documents:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])

    # Difficulty is measured after final placement and includes rule identity, not just a count.
    for answer in result_gold["decision_answers"]:
        answer["difficulty_vector"] = _difficulty_vector(
            result_public,
            answer,
            semantic_bridge_depth=answer["semantic_bridge_depth"],
        )

    base_documents_hash = _hash(public["documents"])
    base_projection_hash = _hash(base_projection)
    result_public.update({
        "dataset_version": dataset_version,
        "base_dataset_version": BASE_VERSION,
        "task": (
            "Reconstruct cricket tables and evidence graphs, then resolve five long-context "
            "decision records using natural semantic identity chains and single-fact counterfactuals."
        ),
        "r26_stability_contract": {
            "difficulty_labels_private": True,
            "position_forms": ["uniform", "head", "middle", "tail"],
            "protocol_failures_scored_separately": True,
            "difficulty_design_revision": (
                DIFFICULTY_DESIGN_REVISION if candidate_difficulty_design else "R26.7"
            ),
        },
    })
    result_gold.update({
        "dataset_version": dataset_version,
        "base_dataset_version": BASE_VERSION,
        "r26_no_regression": {
            "r25_documents_sha256": base_documents_hash,
            "r25_semantic_projection_sha256": base_projection_hash,
        },
    })
    result_evidence.update({
        "dataset_version": dataset_version,
        "base_dataset_version": BASE_VERSION,
        "r26_text_patches": patches,
        "r26_evidence_claims": new_claims,
        "r26_minimum_evidence_edges": [
            {"question_id": answer["question_id"], "edges": answer["minimum_evidence_edges"]}
            for answer in result_gold["decision_answers"]
        ],
        "r26_rejected_evidence_spans": [
            {"question_id": answer["question_id"], "span_ids": answer["rejected_evidence_spans"]}
            for answer in result_gold["decision_answers"]
        ],
        "r26_no_regression": {
            "r25_documents_sha256": base_documents_hash,
            "r25_semantic_projection_sha256": base_projection_hash,
        },
    })
    return Bundle(result_public, result_gold, result_evidence)


__all__ = ["Bundle", "augment_r25_instance", "reconstruct_r25_documents"]
