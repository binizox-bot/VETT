from __future__ import annotations

import hashlib
import json
from typing import Any

from .spec import EVIDENCE_PROFILE


SUPPORT_PROFILES = {
    "L1": "single_explicit_paraphrased_clue",
    "L2": "two_complementary_cross_document_clues",
    "L3": "two_decisive_clues_plus_plausible_conflict",
    "L4": "three_step_authority_scope_correction_chain",
    "L5": "three_law_composition_with_two_counterclaims",
}


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _surface_form(text: str, *identity: object) -> tuple[str, int]:
    digest = _digest(*identity)
    code = f"R24-{digest[:12].upper()}"
    frames = (
        "Reconciliation leaf {code} records: {text}",
        "The late technical packet labels entry {code}: {text}",
        "Scoring-control note {code}, filed out of sequence, states: {text}",
        "A separate adjudication slip, {code}, contains: {text}",
        "Registry fragment {code} preserves this scoped statement: {text}",
        "The match-office appendix includes item {code}: {text}",
        "Handover folio {code} gives the following case detail: {text}",
        "Audit insert {code}, separated from its companion pages, reads: {text}",
    )
    variant = int(digest[12:14], 16) % len(frames)
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
    """Apply exactly six reversible replacements and nine inserts per match."""
    result = _clone(documents)
    public_by_id = {item["question_id"]: item for item in knowledge_public}
    routing: list[tuple[int, str]] = []
    for doc_index, document in enumerate(result):
        for span in document["spans"]:
            span_id = str(span["span_id"])
            if ".routing" in span_id and span_id not in protected_span_ids:
                routing.append((doc_index, span_id))
    if len(routing) < 6:
        raise ValueError(f"{match_id}: fewer than six unprotected routing spans")

    patches: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    decisive_by_question: dict[str, list[str]] = {}
    misleading_by_question: dict[str, list[str]] = {}
    used_routing: set[str] = set()
    replacement_count = 0

    for answer in knowledge_gold:
        question_id = answer["question_id"]
        card = cards_by_id[answer["rule_id"]]
        fragments = list(card["embedded_fragments"])
        replace_indexes = {0}
        if answer["level"] == "L5":
            replace_indexes.add(1)
        used_docs: set[int] = set()
        decisive: list[str] = []
        misleading: list[str] = []

        for fragment_index, fragment in enumerate(fragments):
            span_id = f"r24span_{_digest(seed, match_id, question_id, fragment_index)[:20]}"
            rendered, surface_variant = _surface_form(
                fragment["text"], seed, match_id, question_id, fragment_index
            )
            new_span = {"span_id": span_id, "text": rendered}
            operation = "insert"

            if fragment_index in replace_indexes:
                choices = [
                    item for item in routing
                    if item[1] not in used_routing and item[0] not in used_docs
                ]
                if not choices:
                    choices = [item for item in routing if item[1] not in used_routing]
                if not choices:
                    raise ValueError(f"{match_id}: routing replacement budget exhausted")
                choice_index = int(_digest(seed, match_id, question_id, fragment_index)[:8], 16) % len(choices)
                doc_index, target_span_id = choices[choice_index]
                used_routing.add(target_span_id)
                document = result[doc_index]
                span_index = next(i for i, span in enumerate(document["spans"]) if span["span_id"] == target_span_id)
                original = _clone(document["spans"][span_index])
                document["spans"][span_index] = new_span
                patches.append({
                    "operation": "replace",
                    "document_id": document["document_id"],
                    "span_index": span_index,
                    "inserted_span_id": span_id,
                    "original_span": original,
                    "question_id": question_id,
                })
                operation = "replace"
                replacement_count += 1
            else:
                candidates = [i for i in range(len(result)) if i not in used_docs]
                if not candidates:
                    raise ValueError(f"{match_id}: insufficient documents for cross-document evidence")
                doc_index = candidates[int(_digest(seed, question_id, fragment_index)[:8], 16) % len(candidates)]
                document = result[doc_index]
                spans = document["spans"]
                span_index = int(_digest(question_id, fragment_index, seed)[:8], 16) % (len(spans) + 1)
                spans.insert(span_index, new_span)
                patches.append({
                    "operation": "insert",
                    "document_id": document["document_id"],
                    "span_index": span_index,
                    "inserted_span_id": span_id,
                    "question_id": question_id,
                })
            used_docs.add(doc_index)
            claims.append({
                "question_id": question_id,
                "rule_id": answer["rule_id"],
                "level": answer["level"],
                "span_id": span_id,
                "document_id": result[doc_index]["document_id"],
                "evidence_role": fragment["role"],
                "surface_variant": surface_variant,
                "patch_operation": operation,
            })
            (misleading if fragment["role"] == "misleading" else decisive).append(span_id)

        decisive_by_question[question_id] = decisive
        misleading_by_question[question_id] = misleading
        case_code = f"QD-{_digest(seed, match_id, question_id)[:10].upper()}"
        instruction_frames = (
            "Resolve the controlling rule state and reject any non-authoritative alternative.",
            "Reconcile the dispersed case notes before selecting the legally supported outcome.",
            "Apply timing, scope and authority in that order; do not decide by document position.",
            "Treat apparently plausible case notes as claims to test, not as automatic authority.",
            "Construct the shortest sufficient rule chain and separate contrary commentary.",
            "Use the fixed ruleset to adjudicate the docket, including every stated exception.",
        )
        instruction = instruction_frames[int(_digest(question_id, match_id)[-2:], 16) % len(instruction_frames)]
        public_by_id[question_id].update({
            "mode": "hybrid_rule_text_reasoning",
            "support_profile": SUPPORT_PROFILES[answer["level"]],
            "question": f"Case {case_code}. {card['question']} {instruction} Cite only spans directly bearing on this scenario.",
            "counterfactual_probe": {
                "question": "If every decisive evidence span for this item were removed, would the original answer remain uniquely supported by the dossier?",
                "answer_choices": ["SUPPORTED_SAME", "NO_UNDERDETERMINED", "SUPPORTED_DIFFERENT"],
            },
        })

    if replacement_count != 6:
        raise ValueError(f"{match_id}: expected six replacements, got {replacement_count}")
    for document in result:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    for answer in knowledge_gold:
        answer.update({
            "mode": "hybrid_rule_text_reasoning",
            "support_profile": SUPPORT_PROFILES[answer["level"]],
            "decisive_evidence_spans": decisive_by_question[answer["question_id"]],
            "misleading_evidence_spans": misleading_by_question[answer["question_id"]],
            "counterfactual_answer_code": "NO_UNDERDETERMINED",
            "counterfactual_removed_spans": decisive_by_question[answer["question_id"]],
        })
        profile = EVIDENCE_PROFILE[answer["level"]]
        if len(answer["decisive_evidence_spans"]) != profile["decisive"] or len(answer["misleading_evidence_spans"]) != profile["misleading"]:
            raise ValueError(f"{match_id}: evidence profile mismatch for {answer['question_id']}")
    return result, patches, claims


def reconstruct_base_documents(documents: list[dict[str, Any]], patches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = _clone(documents)
    by_id = {document["document_id"]: document for document in result}
    for patch in reversed(patches):
        document = by_id[patch["document_id"]]
        spans = document["spans"]
        index = int(patch["span_index"])
        if index >= len(spans) or spans[index]["span_id"] != patch["inserted_span_id"]:
            raise ValueError("R24 patch position or identity mismatch")
        if patch["operation"] == "insert":
            spans.pop(index)
        elif patch["operation"] == "replace":
            spans[index] = _clone(patch["original_span"])
        else:
            raise ValueError(f"unknown R24 patch operation: {patch['operation']}")
    for document in result:
        document["text"] = "\n".join(str(span["text"]) for span in document["spans"])
    return result


__all__ = ["SUPPORT_PROFILES", "embed_rule_evidence", "reconstruct_base_documents"]
