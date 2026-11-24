from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .knowledge import RULE_CARDS_BY_ID
from .spec import BASE_VERSION, EMBEDDED_VERSION, LEVELS, RELATION_ATOMS, VERSION
from .text_embedding import SUPPORT_PROFILES, reconstruct_base_documents


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def audit_instance(
    public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    versions = {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")}
    if len(versions) != 1 or next(iter(versions)) not in {VERSION, EMBEDDED_VERSION}:
        errors.append("R23 version mismatch")
    embedded = versions == {EMBEDDED_VERSION}
    if {public.get("base_dataset_version"), gold.get("base_dataset_version"), evidence.get("base_dataset_version")} != {BASE_VERSION}:
        errors.append("R22 base version mismatch")
    if len({public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")}) != 1:
        errors.append("instance ID mismatch")
    integrity = gold.get("r22_integrity", {})
    integrity_values = [
        ("table_targets_sha256", gold.get("table_targets", [])),
        ("probes_sha256", gold.get("probes", [])),
    ]
    if embedded:
        if _hash(public.get("documents", [])) != integrity.get("embedded_documents_sha256"):
            errors.append("R23 embedded-document digest mismatch")
        try:
            base_documents = reconstruct_base_documents(
                public.get("documents", []), evidence.get("r23_text_patches", [])
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"R23 text patch is not reversible: {exc}")
            base_documents = []
        integrity_values.append(("documents_sha256", base_documents))
    else:
        integrity_values.append(("documents_sha256", public.get("documents", [])))
    for name, value in integrity_values:
        if _hash(value) != integrity.get(name):
            errors.append(f"R22 no-regression digest mismatch: {name}")

    public_knowledge = public.get("knowledge_question_schema", [])
    gold_knowledge = gold.get("knowledge_answers", [])
    if len(public_knowledge) != 5 or len(gold_knowledge) != 5:
        errors.append("knowledge track must contain five questions")
    if [item.get("question_id") for item in public_knowledge] != [item.get("question_id") for item in gold_knowledge]:
        errors.append("knowledge public/private order mismatch")
    if Counter(item.get("level") for item in gold_knowledge) != Counter({level: 1 for level in LEVELS}):
        errors.append("knowledge track is not one question per level")
    for public_item, answer in zip(public_knowledge, gold_knowledge):
        card = RULE_CARDS_BY_ID.get(str(answer.get("rule_id")))
        if card is None:
            errors.append(f"unknown rule card: {answer.get('rule_id')}")
            continue
        if answer.get("answer_code") != card["answer_code"]:
            errors.append(f"knowledge answer disagrees with rule bank: {answer.get('question_id')}")
        if answer.get("answer_code") not in public_item.get("answer_choices", []):
            errors.append(f"knowledge answer absent from choices: {answer.get('question_id')}")
        if not set(answer.get("required_atoms", [])) <= set(public_item.get("reasoning_atom_choices", [])):
            errors.append(f"knowledge atoms absent from choices: {answer.get('question_id')}")
        if "source_url" in public_item or "law_reference" in public_item:
            errors.append(f"closed-book source leaked publicly: {answer.get('question_id')}")
        if embedded:
            if public_item.get("mode") != "hybrid_rule_text_reasoning":
                errors.append(f"embedded knowledge mode missing: {answer.get('question_id')}")
            if public_item.get("support_profile") != SUPPORT_PROFILES.get(answer.get("level")):
                errors.append(f"embedded support profile mismatch: {answer.get('question_id')}")
            decisive = set(answer.get("decisive_evidence_spans", []))
            misleading = set(answer.get("misleading_evidence_spans", []))
            if not decisive or decisive & misleading:
                errors.append(f"invalid embedded evidence roles: {answer.get('question_id')}")
            if not (decisive | misleading) <= {
                span["span_id"]
                for document in public.get("documents", [])
                for span in document.get("spans", [])
            }:
                errors.append(f"embedded knowledge evidence absent from documents: {answer.get('question_id')}")
            question_claims = [
                claim
                for claim in evidence.get("rule_evidence_claims", [])
                if claim.get("question_id") == answer.get("question_id")
            ]
            expected_spans = decisive | misleading
            if {claim.get("span_id") for claim in question_claims} != expected_spans:
                errors.append(f"embedded claim coverage mismatch: {answer.get('question_id')}")
            if len(expected_spans) > 1 and len({claim.get("document_id") for claim in question_claims}) != len(expected_spans):
                errors.append(f"embedded clues are not cross-document: {answer.get('question_id')}")

    public_open = public.get("open_qa_schema", [])
    gold_open = gold.get("open_qa_answers", [])
    if len(public_open) != 5 or len(gold_open) != 5:
        errors.append("open track must contain five questions")
    if [item.get("question_id") for item in public_open] != [item.get("question_id") for item in gold_open]:
        errors.append("open public/private order mismatch")
    if Counter(item.get("level") for item in gold_open) != Counter({level: 1 for level in LEVELS}):
        errors.append("open track is not one question per level")
    probes = {probe["probe_id"]: probe for probe in gold.get("probes", [])}
    public_spans = {
        span["span_id"]
        for document in public.get("documents", [])
        for span in document.get("spans", [])
    }
    for public_item, answer in zip(public_open, gold_open):
        probe = probes.get(answer.get("linked_probe_id"))
        if probe is None:
            errors.append(f"open question has unknown linked probe: {answer.get('question_id')}")
            continue
        if str(answer.get("conclusion_value")) != str(probe.get("value")):
            errors.append(f"open conclusion differs from R22 gold: {answer.get('question_id')}")
        expected_atoms = {RELATION_ATOMS[edge["relation"]] for edge in probe["decisive_evidence"]["edges"]}
        if probe["provenance_context"]["spans"]:
            expected_atoms.add("SEPARATES_DECISIVE_FROM_PROVENANCE")
        if set(answer.get("required_atoms", [])) != expected_atoms:
            errors.append(f"open reasoning atoms disagree with graph: {answer.get('question_id')}")
        if not set(answer["decisive_evidence"]["spans"] + answer["provenance_context"]["spans"]) <= public_spans:
            errors.append(f"open evidence references non-public span: {answer.get('question_id')}")
        if answer.get("conclusion_value") in answer.get("forbidden_conclusions", []):
            errors.append(f"gold conclusion listed as forbidden: {answer.get('question_id')}")
        if public_item.get("linked_probe_id") != answer.get("linked_probe_id"):
            errors.append(f"open linked probe mismatch: {answer.get('question_id')}")

    if embedded:
        embedded_texts = [
            span["text"]
            for document in public.get("documents", [])
            for span in document.get("spans", [])
            if str(span.get("span_id", "")).startswith("r23span_")
        ]
        if len(embedded_texts) != len(set(embedded_texts)):
            errors.append("embedded rule spans contain exact duplicate text within instance")

    summary = {
        "knowledge_questions": len(gold_knowledge),
        "open_questions": len(gold_open),
        "base_table_targets": len(gold.get("table_targets", [])),
        "base_probes": len(gold.get("probes", [])),
        "embedded_rule_spans": sum(
            len(item.get("decisive_evidence_spans", [])) + len(item.get("misleading_evidence_spans", []))
            for item in gold_knowledge
        ),
        "replaced_routing_spans": sum(
            patch.get("operation") == "replace" for patch in evidence.get("r23_text_patches", [])
        ),
        "inserted_rule_spans": sum(
            patch.get("operation") == "insert" for patch in evidence.get("r23_text_patches", [])
        ),
    }
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "summary": summary}


def audit_release(release_dir: Path) -> dict[str, Any]:
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    results: dict[str, str] = {}
    errors: list[str] = []
    embedded_texts: list[str] = []
    for match_id in summary["match_ids"]:
        public = json.loads((release_dir / "public" / match_id / "public_instance.json").read_text(encoding="utf-8"))
        audit = audit_instance(
            public,
            json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")),
            json.loads((release_dir / "private" / match_id / "private_evidence.json").read_text(encoding="utf-8")),
        )
        results[match_id] = audit["status"]
        errors.extend(f"{match_id}: {error}" for error in audit["errors"])
        embedded_texts.extend(
            span["text"]
            for document in public.get("documents", [])
            for span in document.get("spans", [])
            if str(span.get("span_id", "")).startswith("r23span_")
        )
    if embedded_texts and len(embedded_texts) != len(set(embedded_texts)):
        errors.append("release contains exact duplicate embedded rule spans")
    return {"status": "PASS" if not errors else "FAIL", "instances": results, "errors": errors}


__all__ = ["audit_instance", "audit_release"]
