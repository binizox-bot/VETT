from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from .spec import ANSWER_BLIND_VERSION, MEASUREMENT_VALIDITY_VERSION, POSITION_FORMS


def _hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def evidence_span_ids(gold: dict[str, Any]) -> set[str]:
    return {
        str(span_id)
        for answer in gold["decision_answers"]
        for span_id in answer["minimum_evidence_spans"]
    }


def proof_span_ids(gold: dict[str, Any]) -> set[str]:
    """All spans required by the positive proof and explicit conflict rejection."""
    return evidence_span_ids(gold) | {
        str(span_id)
        for answer in gold["decision_answers"]
        for span_id in answer.get("rejected_evidence_spans", [])
    }


def _position_target_ids(public: dict[str, Any], gold: dict[str, Any]) -> set[str]:
    if public.get("dataset_version") in {
        MEASUREMENT_VALIDITY_VERSION,
        ANSWER_BLIND_VERSION,
    }:
        return proof_span_ids(gold)
    return evidence_span_ids(gold)


def make_position_variant(
    public: dict[str, Any],
    gold: dict[str, Any],
    form: str,
) -> dict[str, Any]:
    if form not in POSITION_FORMS:
        raise ValueError(f"unknown R26 position form: {form}")
    result = copy.deepcopy(public)
    evidence_ids = _position_target_ids(public, gold)
    for document in result["documents"]:
        selected = [span for span in document["spans"] if str(span["span_id"]) in evidence_ids]
        other = [span for span in document["spans"] if str(span["span_id"]) not in evidence_ids]
        if form == "head":
            spans = selected + other
        elif form == "tail":
            spans = other + selected
        else:
            split = len(other) // 2
            spans = other[:split] + selected + other[split:]
        document["spans"] = spans
        document["text"] = "\n".join(str(span["text"]) for span in spans)
    contract = result.setdefault("r26_stability_contract", {})
    contract["active_position_form"] = form
    contract["semantic_content_sha256"] = _hash(sorted(
        (str(span["span_id"]), str(span["text"]))
        for document in result["documents"]
        for span in document["spans"]
    ))
    return result


def make_proof_only_variant(
    public: dict[str, Any],
    gold: dict[str, Any],
) -> dict[str, Any]:
    """Create a synthesis diagnostic containing the unlabeled proof-span union.

    Positive and rejected spans for all five questions are retained together. The
    model is not told which question or role any span belongs to, so this is a
    recognition upper bound rather than an answer-revealing oracle prompt.
    """
    result = copy.deepcopy(public)
    keep = proof_span_ids(gold)
    documents = []
    for document in result["documents"]:
        spans = [
            span for span in document["spans"]
            if str(span["span_id"]) in keep
        ]
        if spans:
            document["spans"] = spans
            document["text"] = "\n".join(str(span["text"]) for span in spans)
            documents.append(document)
    result["documents"] = documents
    contract = result.setdefault("r26_stability_contract", {})
    contract["active_position_form"] = "proof_only"
    contract["diagnostic_only"] = True
    contract["span_selection"] = "unlabeled_union_of_positive_and_rejected_proof_spans"
    contract["semantic_content_sha256"] = _hash(sorted(
        (str(span["span_id"]), str(span["text"]))
        for document in result["documents"]
        for span in document["spans"]
    ))
    return result


def audit_proof_only_variant(
    official: dict[str, Any],
    gold: dict[str, Any],
    variant: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    expected_ids = proof_span_ids(gold)
    official_text = {
        str(span["span_id"]): str(span["text"])
        for document in official["documents"] for span in document["spans"]
    }
    variant_text = {
        str(span["span_id"]): str(span["text"])
        for document in variant.get("documents", []) for span in document.get("spans", [])
    }
    if set(variant_text) != expected_ids:
        errors.append("proof-only span set differs from registered proof union")
    if any(official_text.get(span_id) != text for span_id, text in variant_text.items()):
        errors.append("proof-only span text changed")
    if variant.get("decision_question_schema") != official.get("decision_question_schema"):
        errors.append("proof-only question schema changed")
    contract = variant.get("r26_stability_contract", {})
    if contract.get("active_position_form") != "proof_only" or contract.get("diagnostic_only") is not True:
        errors.append("proof-only diagnostic contract missing")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "spans": len(variant_text),
        "documents": len(variant.get("documents", [])),
        "positive_spans": len(evidence_span_ids(gold)),
        "rejected_spans": len(expected_ids - evidence_span_ids(gold)),
    }


def position_statistics(public: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    evidence_ids = _position_target_ids(public, gold)
    positions: list[float] = []
    by_question: dict[str, list[float]] = {}
    location: dict[str, float] = {}
    for document in public["documents"]:
        count = len(document["spans"])
        for index, span in enumerate(document["spans"]):
            location[str(span["span_id"])] = index / max(1, count - 1)
    for span_id in evidence_ids:
        if span_id in location:
            positions.append(location[span_id])
    for answer in gold["decision_answers"]:
        values = [location[str(span_id)] for span_id in answer["minimum_evidence_spans"]]
        by_question[str(answer["question_id"])] = values
    return {
        "position_target_contract": (
            "positive_and_rejected_proof_spans"
            if public.get("dataset_version")
            in {MEASUREMENT_VALIDITY_VERSION, ANSWER_BLIND_VERSION}
            else "positive_evidence_spans"
        ),
        "evidence_spans": len(positions),
        "mean_relative_position": round(sum(positions) / len(positions), 6) if positions else 0.0,
        "min_relative_position": round(min(positions), 6) if positions else 0.0,
        "max_relative_position": round(max(positions), 6) if positions else 0.0,
        "question_mean_relative_position": {
            qid: round(sum(values) / len(values), 6)
            for qid, values in by_question.items()
        },
    }


def audit_position_variants(
    official: dict[str, Any],
    gold: dict[str, Any],
    variants: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    official_content = sorted(
        (str(span["span_id"]), str(span["text"]))
        for document in official["documents"]
        for span in document["spans"]
    )
    stats: dict[str, Any] = {"uniform": position_statistics(official, gold)}
    for form in POSITION_FORMS:
        variant = variants.get(form)
        if not variant:
            errors.append(f"missing position form: {form}")
            continue
        content = sorted(
            (str(span["span_id"]), str(span["text"]))
            for document in variant["documents"]
            for span in document["spans"]
        )
        if content != official_content:
            errors.append(f"semantic span content changed in {form}")
        if variant.get("decision_question_schema") != official.get("decision_question_schema"):
            errors.append(f"question schema changed in {form}")
        stats[form] = position_statistics(variant, gold)
    if "head" in stats and stats["head"]["mean_relative_position"] > 0.30:
        errors.append("head form does not place evidence near the head")
    if "middle" in stats and not 0.30 <= stats["middle"]["mean_relative_position"] <= 0.70:
        errors.append("middle form does not place evidence near the middle")
    if "tail" in stats and stats["tail"]["mean_relative_position"] < 0.70:
        errors.append("tail form does not place evidence near the tail")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "forms": stats,
    }


__all__ = [
    "audit_position_variants",
    "audit_proof_only_variant",
    "evidence_span_ids",
    "proof_span_ids",
    "make_proof_only_variant",
    "make_position_variant",
    "position_statistics",
]
