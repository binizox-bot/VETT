from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any

from .generator import DATASET_VERSION, resolve_from_evidence


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _word_count(public: dict[str, Any]) -> int:
    return sum(
        len(re.findall(r"\b\w+\b", document.get("text", "")))
        for document in public.get("documents", [])
    )


def _mentions_in_public(
    public: dict[str, Any], claims: list[dict[str, Any]]
) -> tuple[dict[str, str], list[str]]:
    spans: dict[str, tuple[str, str]] = {}
    errors: list[str] = []
    for document in public.get("documents", []):
        for span in document.get("spans", []):
            span_id = span.get("span_id")
            if span_id in spans:
                errors.append(f"duplicate public span: {span_id}")
            spans[span_id] = (document.get("document_id", ""), span.get("text", ""))
    order: dict[str, str] = {}
    for claim in claims:
        span_id = claim.get("span_id")
        found = spans.get(span_id)
        if found is None:
            errors.append(f"missing claim span: {span_id}")
            continue
        document_id, text = found
        if document_id != claim.get("document_id"):
            errors.append(f"claim document mismatch: {claim.get('claim_id')}")
        if _hash(text) != claim.get("span_sha256"):
            errors.append(f"claim span hash mismatch: {claim.get('claim_id')}")
        if claim.get("docket") not in text:
            errors.append(f"docket absent from public span: {claim.get('claim_id')}")
        if str(claim.get("value")) not in text:
            errors.append(f"claim value absent from public span: {claim.get('claim_id')}")
        parent = claim.get("supersedes_docket")
        if parent and parent not in text:
            errors.append(f"superseded docket absent: {claim.get('claim_id')}")
        order[claim["claim_id"]] = span_id
    return order, errors


def heuristic_metrics(
    public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    span_order: dict[str, int] = {}
    position = 0
    for document in public.get("documents", []):
        for span in document.get("spans", []):
            span_order[span["span_id"]] = position
            position += 1
    claims_by_target: dict[str, list[dict[str, Any]]] = {}
    for claim in evidence.get("claims", []):
        claims_by_target.setdefault(claim["target_id"], []).append(claim)
    correct = Counter()
    total = len(gold.get("targets", []))
    for target in gold.get("targets", []):
        candidates = claims_by_target[target["target_id"]]
        ordered = sorted(candidates, key=lambda claim: span_order[claim["span_id"]])
        predictions = {
            "first_public_mention": ordered[0]["value"],
            "last_public_mention": ordered[-1]["value"],
            "shortest_revision_chain": candidates[0]["value"],
        }
        frequencies = Counter(claim["value"] for claim in candidates)
        predictions["majority_value"] = sorted(
            frequencies, key=lambda value: (-frequencies[value], value)
        )[0]
        for name, prediction in predictions.items():
            correct[name] += int(prediction == target["value"])
    return {
        name: {
            "correct": count,
            "total": total,
            "accuracy": round(count / total, 6) if total else 0.0,
        }
        for name, count in sorted(correct.items())
    }


def audit_instance(
    public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    identity = {
        public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")
    }
    if len(identity) != 1:
        errors.append("instance identity mismatch")
    versions = {
        public.get("dataset_version"),
        gold.get("dataset_version"),
        evidence.get("dataset_version"),
    }
    if versions != {DATASET_VERSION}:
        errors.append("dataset version mismatch")

    schema_ids = [target.get("target_id") for target in public.get("target_schema", [])]
    gold_ids = [target.get("target_id") for target in gold.get("targets", [])]
    if schema_ids != gold_ids:
        errors.append("public target schema does not match gold target order")
    if len(gold_ids) != len(set(gold_ids)):
        errors.append("duplicate gold target IDs")

    claims = evidence.get("claims", [])
    _, public_errors = _mentions_in_public(public, claims)
    errors.extend(public_errors)
    claim_ids = {claim.get("claim_id") for claim in claims}
    for claim in claims:
        parent = claim.get("supersedes")
        if parent and parent not in claim_ids:
            errors.append(f"unknown superseded claim: {parent}")
        if parent and parent == claim.get("claim_id"):
            errors.append(f"self supersession: {parent}")

    try:
        resolved = resolve_from_evidence(evidence)
    except ValueError as exc:
        errors.append(str(exc))
        resolved = {}
    expected = {target["target_id"]: target["value"] for target in gold.get("targets", [])}
    if resolved != expected:
        missing = sorted(set(expected) - set(resolved))
        wrong = sorted(
            target_id
            for target_id in set(expected) & set(resolved)
            if expected[target_id] != resolved[target_id]
        )
        errors.append(f"oracle resolution mismatch; missing={missing[:3]}, wrong={wrong[:3]}")

    depths = Counter(
        int(target["difficulty"].removeprefix("revision_depth_"))
        for target in gold.get("targets", [])
    )
    if set(depths) != {1, 2, 3}:
        errors.append(f"revision depth coverage missing: {sorted(depths)}")
    word_count = _word_count(public)
    if word_count < 5000:
        errors.append(f"public text too short: {word_count} words")
    document_count = len(public.get("documents", []))
    if document_count < 10:
        errors.append(f"too few public documents: {document_count}")

    public_blob = "\n".join(
        document.get("text", "") for document in public.get("documents", [])
    ).lower()
    for marker in ("correct answer", "gold value", "private evidence", "r20_verified"):
        if marker in public_blob:
            errors.append(f"public leakage marker: {marker}")

    metrics = heuristic_metrics(public, gold, evidence)
    for name, metric in metrics.items():
        if metric["accuracy"] > 0.60:
            errors.append(f"shortcut too strong: {name}={metric['accuracy']}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {
            "targets": len(gold_ids),
            "claims": len(claims),
            "documents": document_count,
            "words": word_count,
            "revision_depths": dict(sorted(depths.items())),
        },
        "heuristics": metrics,
    }


__all__ = ["audit_instance", "heuristic_metrics"]
