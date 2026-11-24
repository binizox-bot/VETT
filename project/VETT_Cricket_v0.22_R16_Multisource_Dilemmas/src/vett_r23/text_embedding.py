from __future__ import annotations

import hashlib
import json
from typing import Any


SUPPORT_PROFILES = {
    "L1": "single_explicit_rule_clue",
    "L2": "distributed_complementary_clues",
    "L3": "scoped_case_outcome_and_exclusions",
    "L4": "credible_conflict_then_authoritative_correction",
    "L5": "case_facts_requiring_rule_application",
}


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _surface_form(text: str, role: str, *identity: object) -> tuple[str, int]:
    digest = _digest(*identity)
    code = f"K{digest[:10].upper()}"
    frames = (
        "Dossier insert {code} preserves this entry: {text}",
        "The late handover filed {code} with the following wording: {text}",
        "Case slip {code}, circulated during reconciliation, reads: {text}",
        "The operations annex labels the following passage {code}: {text}",
        "A separate review leaf, {code}, records: {text}",
        "Registry item {code} adds this scoped note: {text}",
        "The match-office packet includes {code}: {text}",
        "Technical folio {code} carries the entry: {text}",
    )
    variant = int(digest[10:12], 16) % len(frames)
    # The role is deliberately not named in the frame; models must infer it from the content.
    return frames[variant].format(code=code, text=text), variant


def embed_rule_evidence(
    documents: list[dict[str, Any]],
    knowledge_public: list[dict[str, Any]],
    knowledge_gold: list[dict[str, Any]],
    cards_by_id: dict[str, dict[str, Any]],
    *,
    match_id: str,
    seed: int,
    protected_span_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Interleave a tiny, reversible rule-evidence patch into an R22 document bundle."""
    result = _clone(documents)
    public_by_id = {item["question_id"]: item for item in knowledge_public}
    routing: list[tuple[int, str]] = []
    for doc_index, document in enumerate(result):
        for span_index, span in enumerate(document["spans"]):
            span_id = str(span["span_id"])
            if ".routing" in span_id and span_id not in protected_span_ids:
                routing.append((doc_index, span_id))
    if len(routing) < len(knowledge_gold):
        raise ValueError(f"{match_id}: insufficient unprotected routing spans for embedded evidence")

    patches: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    decisive_by_question: dict[str, list[str]] = {}
    misleading_by_question: dict[str, list[str]] = {}
    replacement_cursor = 0
    for answer in knowledge_gold:
        question_id = answer["question_id"]
        card = cards_by_id[answer["rule_id"]]
        fragments = list(card["embedded_fragments"])
        decisive: list[str] = []
        misleading: list[str] = []
        first_document_index: int | None = None
        for fragment_index, fragment in enumerate(fragments):
            span_id = f"r23span_{_digest(seed, match_id, question_id, fragment_index)[:20]}"
            rendered_text, surface_variant = _surface_form(
                fragment["text"], fragment["role"], seed, match_id, question_id, fragment_index
            )
            new_span = {"span_id": span_id, "text": rendered_text}
            if fragment_index == 0:
                doc_index, target_span_id = routing[replacement_cursor]
                replacement_cursor += 1
                first_document_index = doc_index
                span_index = next(
                    index
                    for index, span in enumerate(result[doc_index]["spans"])
                    if span["span_id"] == target_span_id
                )
                original = _clone(result[doc_index]["spans"][span_index])
                result[doc_index]["spans"][span_index] = new_span
                patches.append(
                    {
                        "operation": "replace",
                        "document_id": result[doc_index]["document_id"],
                        "span_index": span_index,
                        "inserted_span_id": span_id,
                        "original_span": original,
                        "question_id": question_id,
                    }
                )
            else:
                doc_index = int(_digest(seed, match_id, question_id, fragment_index)[:8], 16) % len(result)
                if doc_index == first_document_index:
                    doc_index = (doc_index + 1) % len(result)
                spans = result[doc_index]["spans"]
                span_index = int(_digest(question_id, fragment_index, seed)[:8], 16) % (len(spans) + 1)
                spans.insert(span_index, new_span)
                patches.append(
                    {
                        "operation": "insert",
                        "document_id": result[doc_index]["document_id"],
                        "span_index": span_index,
                        "inserted_span_id": span_id,
                        "question_id": question_id,
                    }
                )
            claims.append(
                {
                    "question_id": question_id,
                    "rule_id": answer["rule_id"],
                    "level": answer["level"],
                    "span_id": span_id,
                    "document_id": result[doc_index]["document_id"],
                    "evidence_role": fragment["role"],
                    "surface_variant": surface_variant,
                }
            )
            (misleading if fragment["role"] == "misleading" else decisive).append(span_id)
        decisive_by_question[question_id] = decisive
        misleading_by_question[question_id] = misleading
        public_by_id[question_id]["mode"] = "hybrid_rule_text_reasoning"
        public_by_id[question_id]["support_profile"] = SUPPORT_PROFILES[answer["level"]]
        public_by_id[question_id]["question"] = (
            card["question"]
            + " Use the fixed ruleset together with relevant dossier evidence; reject scoped or non-authoritative commentary. "
            "Cite only spans directly concerning this rule scenario: evidence for another question is irrelevant, not misleading."
        )

    for document in result:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    for answer in knowledge_gold:
        answer["mode"] = "hybrid_rule_text_reasoning"
        answer["support_profile"] = SUPPORT_PROFILES[answer["level"]]
        answer["decisive_evidence_spans"] = decisive_by_question[answer["question_id"]]
        answer["misleading_evidence_spans"] = misleading_by_question[answer["question_id"]]
    return result, patches, claims


def reconstruct_base_documents(
    documents: list[dict[str, Any]], patches: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    result = _clone(documents)
    by_id = {document["document_id"]: document for document in result}
    for patch in reversed(patches):
        document = by_id[patch["document_id"]]
        spans = document["spans"]
        index = int(patch["span_index"])
        if patch["operation"] == "insert":
            if index >= len(spans) or spans[index]["span_id"] != patch["inserted_span_id"]:
                raise ValueError("embedded insert patch cannot be reversed")
            spans.pop(index)
        elif patch["operation"] == "replace":
            if index >= len(spans) or spans[index]["span_id"] != patch["inserted_span_id"]:
                raise ValueError("embedded replacement patch cannot be reversed")
            spans[index] = _clone(patch["original_span"])
        else:
            raise ValueError(f"unknown embedded patch operation: {patch['operation']}")
    for document in result:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    return result


__all__ = ["SUPPORT_PROFILES", "embed_rule_evidence", "reconstruct_base_documents"]
