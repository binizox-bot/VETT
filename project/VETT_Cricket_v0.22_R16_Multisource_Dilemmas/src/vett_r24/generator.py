from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .knowledge import RULE_CARDS, RULE_CARDS_BY_ID, SCENARIO_SPLITS
from .spec import BASE_VERSION, DEFAULT_SEED, LEVELS, OPEN_REASONING_ATOMS, RELATION_ATOMS, RULESET, VERSION
from .text_embedding import embed_rule_evidence


@dataclass(frozen=True)
class Bundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _knowledge_questions(match_id: str, seed: int, variant_index: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    public_items: list[dict[str, Any]] = []
    gold_items: list[dict[str, Any]] = []
    for level_index, level in enumerate(LEVELS):
        pool = [card for card in RULE_CARDS if card["level"] == level]
        sequence_index = variant_index + level_index
        card = pool[sequence_index % len(pool)]
        occurrence_index = sequence_index // len(pool)
        question_id = f"r24k_{_digest(seed, match_id, card['rule_id'])[:18]}"
        incorrect = sorted([choice for choice in card["answer_choices"] if choice != card["answer_code"]], key=lambda choice: _digest(seed, match_id, question_id, choice))
        choices = list(incorrect)
        position_offset = int(_digest(seed, card["scenario_id"])[-2:], 16) % 3
        choices.insert((occurrence_index + position_offset) % 3, card["answer_code"])
        atoms = sorted(card["reasoning_atom_choices"], key=lambda atom: _digest(seed, question_id, atom))
        public_items.append({
            "question_id": question_id,
            "scenario_id": card["scenario_id"],
            "scenario_split": SCENARIO_SPLITS[card["scenario_id"]],
            "level": level,
            "mode": "hybrid_rule_text_reasoning",
            "ruleset_title": RULESET["title"],
            "ruleset_effective_date": RULESET["effective_date"],
            "question": card["question"],
            "answer_choices": choices,
            "reasoning_atom_choices": atoms,
            "output_fields": ["answer_code", "reasoning_atoms", "decisive_spans", "misleading_spans", "counterfactual_answer_code", "explanation", "confidence"],
        })
        gold_items.append({
            "question_id": question_id,
            "scenario_id": card["scenario_id"],
            "scenario_split": SCENARIO_SPLITS[card["scenario_id"]],
            "level": level,
            "rule_id": card["rule_id"],
            "answer_code": card["answer_code"],
            "required_atoms": card["required_atoms"],
            "rationale": card["rationale"],
            "source": {
                "authority": RULESET["authority"], "title": RULESET["title"],
                "effective_date": RULESET["effective_date"], "url": card["source_url"],
                "law_reference": card["law_reference"], "pages": card["source_pages"],
            },
        })
    return public_items, gold_items


def _open_questions(match_id: str, public_probes: list[dict[str, Any]], gold_probes: list[dict[str, Any]], probe_claims: list[dict[str, Any]], seed: int, variant_index: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    public_by_id = {item["probe_id"]: item for item in public_probes}
    public_items: list[dict[str, Any]] = []
    gold_items: list[dict[str, Any]] = []
    for level_index, level in enumerate(LEVELS):
        pool = [probe for probe in gold_probes if probe["level"] == level]
        probe = pool[(variant_index * 3 + level_index) % len(pool)]
        public_probe = public_by_id[probe["probe_id"]]
        question_id = f"r24o_{_digest(seed, match_id, probe['probe_id'])[:18]}"
        required_atoms = sorted({RELATION_ATOMS[edge["relation"]] for edge in probe["decisive_evidence"]["edges"]} | ({"SEPARATES_DECISIVE_FROM_PROVENANCE"} if probe["provenance_context"]["spans"] else set()))
        related = [claim for claim in probe_claims if claim["probe_id"] == probe["probe_id"]]
        forbidden = sorted({str(claim["value"]) for claim in related if claim.get("value") is not None and str(claim["value"]) != str(probe["value"])})
        public_items.append({
            "question_id": question_id, "level": level, "mode": "open_grounded_reasoning",
            "linked_probe_id": probe["probe_id"], "target_family": probe["target_family"],
            "query_docket": probe["query_docket"],
            "question": f"Resolve query docket {probe['query_docket']}. State the conclusion, construct the decisive relation chain, reject stale or wrongly scoped alternatives, and separate provenance-only evidence.",
            "reasoning_atom_choices": list(OPEN_REASONING_ATOMS),
            "output_fields": ["conclusion_value", "reasoning_atoms", "decisive_spans", "decisive_edges", "provenance_spans", "provenance_edges", "explanation", "confidence"],
            "base_probe_question": public_probe["question"],
        })
        gold_items.append({
            "question_id": question_id, "level": level, "linked_probe_id": probe["probe_id"],
            "target_family": probe["target_family"], "conclusion_value": str(probe["value"]),
            "required_atoms": required_atoms, "forbidden_conclusions": forbidden,
            "decisive_evidence": _clone(probe["decisive_evidence"]),
            "provenance_context": _clone(probe["provenance_context"]),
        })
    return public_items, gold_items


def augment_instance(public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any], *, seed: int = DEFAULT_SEED, variant_index: int = 0) -> Bundle:
    versions = {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")}
    if versions != {BASE_VERSION}:
        raise ValueError(f"R24 requires R22 base, found {versions}")
    match_id = str(public["instance_id"])
    if {match_id, gold.get("instance_id"), evidence.get("instance_id")} != {match_id}:
        raise ValueError("base instance IDs do not match")
    kp, kg = _knowledge_questions(match_id, seed, variant_index)
    op, og = _open_questions(match_id, public["probe_schema"], gold["probes"], evidence["probe_claims"], seed, variant_index)
    result_public, result_gold, result_evidence = _clone(public), _clone(gold), _clone(evidence)
    integrity = {
        "documents_sha256": _hash(public["documents"]),
        "table_targets_sha256": _hash(gold["table_targets"]),
        "probes_sha256": _hash(gold["probes"]),
    }
    protected = {str(claim["span_id"]) for collection in (evidence.get("table_claims", []), evidence.get("probe_claims", [])) for claim in collection if claim.get("span_id")}
    documents, patches, claims = embed_rule_evidence(result_public["documents"], kp, kg, RULE_CARDS_BY_ID, match_id=match_id, seed=seed, protected_span_ids=protected)
    result_public["documents"] = documents
    integrity["embedded_documents_sha256"] = _hash(documents)
    result_public.update({
        "dataset_version": VERSION, "base_dataset_version": BASE_VERSION,
        "task": public["task"] + " Track C: resolve five levelled MCC-2026 rule scenarios from dispersed evidence and cricket-law knowledge, including an evidence-ablation counterfactual. Track D: produce open, auditable conclusions and relation chains.",
        "knowledge_question_schema": kp, "open_qa_schema": op, "r24_variant_index": variant_index,
        "r24_output_contract": {
            "knowledge_predictions": ["question_id", "answer_code", "reasoning_atoms", "decisive_spans", "misleading_spans", "counterfactual_answer_code", "explanation", "confidence"],
            "open_qa_predictions": ["question_id", "conclusion_value", "reasoning_atoms", "decisive_spans", "decisive_edges", "provenance_spans", "provenance_edges", "explanation", "confidence"],
        },
    })
    result_gold.update({
        "dataset_version": VERSION, "base_dataset_version": BASE_VERSION,
        "knowledge_answers": kg, "open_qa_answers": og, "r22_integrity": integrity,
        "r24_variant_index": variant_index,
    })
    result_evidence.update({
        "dataset_version": VERSION, "base_dataset_version": BASE_VERSION,
        "policy": evidence["policy"] + "+R24_sparse_cross_document_rule_evidence_and_counterfactual_open_reasoning",
        "r24_text_patches": patches, "rule_evidence_claims": claims,
    })
    return Bundle(result_public, result_gold, result_evidence)


__all__ = ["Bundle", "augment_instance"]
