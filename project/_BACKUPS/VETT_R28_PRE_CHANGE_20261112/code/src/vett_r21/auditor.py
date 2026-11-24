from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any

from .generator import VERSION, resolve


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ratio(a: int, b: int) -> float:
    return round(a / b, 6) if b else 0.0


def heuristic_metrics(
    public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    span_position: dict[str, int] = {}
    position = 0
    for document in public["documents"]:
        for span in document["spans"]:
            span_position[span["span_id"]] = position
            position += 1
    by_target: dict[str, list[dict[str, Any]]] = {}
    for claim in evidence["claims"]:
        if claim["value"] is not None:
            by_target.setdefault(claim["target_id"], []).append(claim)
    counts = Counter()
    for target in gold["targets"]:
        claims = by_target[target["target_id"]]
        ordered = sorted(claims, key=lambda claim: span_position[claim["span_id"]])
        frequencies = Counter(str(claim["value"]) for claim in claims)
        predictions = {
            "first_public_value": str(ordered[0]["value"]),
            "last_public_value": str(ordered[-1]["value"]),
            "majority_value": sorted(
                frequencies, key=lambda value: (-frequencies[value], value)
            )[0],
        }
        for name, prediction in predictions.items():
            counts[name] += prediction == target["value"]
    total = len(gold["targets"])
    return {
        name: {"correct": value, "total": total, "accuracy": _ratio(value, total)}
        for name, value in sorted(counts.items())
    }


def audit_instance(
    public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    if {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")} != {VERSION}:
        errors.append("version mismatch")
    if len({public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")}) != 1:
        errors.append("instance mismatch")
    schema_ids = [target["target_id"] for target in public.get("target_schema", [])]
    gold_ids = [target["target_id"] for target in gold.get("targets", [])]
    if schema_ids != gold_ids:
        errors.append("target schema mismatch")

    spans: dict[str, tuple[str, str]] = {}
    public_words = 0
    public_blob_parts: list[str] = []
    for document in public.get("documents", []):
        for span in document.get("spans", []):
            span_id = span["span_id"]
            if span_id in spans:
                errors.append(f"duplicate span: {span_id}")
            spans[span_id] = (document["document_id"], span["text"])
            public_words += len(re.findall(r"\b\w+\b", span["text"]))
            public_blob_parts.append(span["text"])
    claims = {claim["claim_id"]: claim for claim in evidence.get("claims", [])}
    for claim in claims.values():
        found = spans.get(claim["span_id"])
        if found is None:
            errors.append(f"missing claim span: {claim['claim_id']}")
            continue
        document_id, text = found
        if document_id != claim["document_id"]:
            errors.append(f"document mismatch: {claim['claim_id']}")
        if _hash(text) != claim["span_sha256"]:
            errors.append(f"span hash mismatch: {claim['claim_id']}")
        if claim["docket"] not in text:
            errors.append(f"docket not visible: {claim['claim_id']}")
        if claim["value"] is not None and str(claim["value"]) not in text:
            errors.append(f"value not visible: {claim['claim_id']}")
        parent = claim.get("parent_claim_id")
        if parent:
            if parent not in claims:
                errors.append(f"unknown parent: {claim['claim_id']}")
            elif claims[parent]["docket"] not in text:
                errors.append(f"parent docket not visible: {claim['claim_id']}")

    expected = {target["target_id"]: target["value"] for target in gold["targets"]}
    try:
        resolved = resolve(evidence)
    except ValueError as exc:
        errors.append(str(exc))
        resolved = {}
    if resolved != expected:
        errors.append("private graph does not uniquely resolve to gold")

    mechanisms = Counter(target["mechanism"] for target in gold["targets"])
    required_mechanisms = {"one_step", "two_step", "copy_trap", "retract_replace", "scoped"}
    if set(mechanisms) != required_mechanisms:
        errors.append(f"mechanism coverage mismatch: {sorted(mechanisms)}")
    for target in gold["targets"]:
        for span_id in target["required_evidence_spans"]:
            if span_id not in spans:
                errors.append(f"unknown required span: {target['target_id']}:{span_id}")
        for edge in target["required_edges"]:
            if edge["from_span"] not in spans or edge["to_span"] not in spans:
                errors.append(f"unknown required edge span: {target['target_id']}")
            if edge["relation"] not in {"supersedes", "retracts", "copies_from"}:
                errors.append(f"unknown required relation: {edge['relation']}")

    public_blob = "\n".join(public_blob_parts)
    for target in public.get("target_schema", []):
        if target["target_id"] in public_blob or target["table_id"] in public_blob:
            errors.append(f"literal target coordinate leaked: {target['target_id']}")
            break
    if public_words < 8000:
        errors.append(f"public evidence too short: {public_words}")
    heuristics = heuristic_metrics(public, gold, evidence)
    for name, metric in heuristics.items():
        if metric["accuracy"] > 0.60:
            errors.append(f"shortcut too strong: {name}={metric['accuracy']}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {
            "targets": len(gold_ids),
            "claims": len(claims),
            "documents": len(public.get("documents", [])),
            "words": public_words,
            "mechanisms": dict(sorted(mechanisms.items())),
            "required_evidence_spans": sum(len(target["required_evidence_spans"]) for target in gold["targets"]),
            "required_edges": sum(len(target["required_edges"]) for target in gold["targets"]),
        },
        "heuristics": heuristics,
    }


__all__ = ["audit_instance", "heuristic_metrics"]
