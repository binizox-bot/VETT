from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from vett_r21.generator import resolve as resolve_r21

from .generator import resolve_probe
from .spec import ALLOWED_RELATIONS, LEVELS, LEVEL_CONTRACTS, TARGET_FAMILIES, VERSION


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _edge_tuple(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (str(edge["from_span"]), str(edge["relation"]), str(edge["to_span"]))


def _depth(edges: list[dict[str, Any]]) -> int:
    parents: dict[str, list[str]] = {}
    for edge in edges:
        parents.setdefault(edge["from_span"], []).append(edge["to_span"])

    def walk(node: str, seen: set[str]) -> int:
        if node in seen:
            raise ValueError("cycle")
        return max((1 + walk(parent, seen | {node}) for parent in parents.get(node, [])), default=0)

    return max((walk(node, set()) for node in parents), default=0)


def _extract(source_value: str, extractor: str) -> str:
    if extractor == "exact":
        return source_value
    if extractor == "leading_int":
        match = re.match(r"^\s*(-?\d+)", source_value)
        if not match:
            raise ValueError("leading integer missing")
        return match.group(1)
    if extractor == "legal_balls":
        parts = source_value.split(".", 1)
        if not all(part.isdigit() for part in parts):
            raise ValueError("invalid overs")
        return str(int(parts[0]) * 6 + (int(parts[1]) if len(parts) == 2 else 0))
    raise ValueError(f"unknown extractor {extractor}")


def _derive(operation: str, values: list[str]) -> str:
    two = lambda value: str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    if operation == "sum_int":
        return str(sum(int(value) for value in values))
    if operation == "ratio_percent_2dp":
        return two(Decimal(values[0]) * 100 / Decimal(values[1]))
    if operation == "economy_2dp":
        return two(Decimal(values[0]) * 6 / Decimal(values[1]))
    if operation == "weighted_boundary_runs":
        return str(int(values[0]) * 4 + int(values[1]) * 6)
    raise ValueError(f"unknown public derivation {operation}")


def audit_instance(
    public: dict[str, Any], gold: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    versions = {public.get("dataset_version"), gold.get("dataset_version"), evidence.get("dataset_version")}
    if versions != {VERSION}:
        errors.append(f"version mismatch: {sorted(map(str, versions))}")
    if len({public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")}) != 1:
        errors.append("instance mismatch")

    table_targets = gold.get("table_targets", [])
    table_by_id = {target["target_id"]: target for target in table_targets}
    public_table_ids = [target["target_id"] for target in public.get("target_schema", [])]
    if public_table_ids != [target["target_id"] for target in table_targets]:
        errors.append("Track A target schema changed from R21 order/content")
    if len(table_by_id) != len(table_targets):
        errors.append("duplicate Track A target")
    expected_table = {target["target_id"]: str(target["value"]) for target in table_targets}
    baseline = gold.get("baseline", {})
    if len(table_targets) != baseline.get("table_target_count"):
        errors.append("Track A target count regressed")
    digest = _hash(json.dumps(expected_table, sort_keys=True, ensure_ascii=False))
    if digest != baseline.get("table_target_digest"):
        errors.append("Track A target digest mismatch")
    try:
        resolved_table = resolve_r21({"claims": evidence.get("table_claims", [])})
        if resolved_table != expected_table:
            errors.append("Track A R21 graph no longer resolves to the same table gold")
    except (KeyError, ValueError) as exc:
        errors.append(f"Track A resolver failure: {exc}")

    spans: dict[str, tuple[str, str]] = {}
    public_words = 0
    public_text: list[str] = []
    for document in public.get("documents", []):
        for span in document.get("spans", []):
            span_id = span.get("span_id")
            if not isinstance(span_id, str) or span_id in spans:
                errors.append(f"invalid or duplicate public span: {span_id}")
                continue
            text = str(span.get("text", ""))
            spans[span_id] = (document["document_id"], text)
            public_words += len(re.findall(r"\b\w+\b", text))
            public_text.append(text)
    if public_words < int(baseline.get("public_words", 0)):
        errors.append("public evidence length regressed below R21")
    if len(public.get("documents", [])) < int(baseline.get("document_count", 0)):
        errors.append("public document count regressed below R21")

    probe_claims = evidence.get("probe_claims", [])
    claim_ids: set[str] = set()
    span_to_claim: dict[str, dict[str, Any]] = {}
    for claim in probe_claims:
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or claim_id in claim_ids:
            errors.append(f"invalid or duplicate probe claim: {claim_id}")
            continue
        claim_ids.add(claim_id)
        found = spans.get(claim.get("span_id"))
        if found is None:
            errors.append(f"missing public probe span: {claim_id}")
            continue
        document_id, text = found
        span_to_claim[claim["span_id"]] = claim
        if document_id != claim.get("document_id"):
            errors.append(f"probe claim document mismatch: {claim_id}")
        if _hash(text) != claim.get("span_sha256"):
            errors.append(f"probe claim hash mismatch: {claim_id}")
        if claim.get("docket") not in text:
            errors.append(f"probe docket not public: {claim_id}")
        if claim.get("relation") not in ALLOWED_RELATIONS | {"asserts"}:
            errors.append(f"unknown claim relation: {claim_id}")
        for parent_id in claim.get("parent_claim_ids", []):
            parent = next((item for item in probe_claims if item.get("claim_id") == parent_id), None)
            if parent is None:
                errors.append(f"unknown parent claim: {claim_id}:{parent_id}")
            elif parent.get("docket") not in text:
                errors.append(f"parent docket not witnessed: {claim_id}:{parent_id}")

    probes = gold.get("probes", [])
    public_probes = public.get("probe_schema", [])
    if len(probes) != 25 or len(public_probes) != 25:
        errors.append(f"probe matrix size is not 25: gold={len(probes)} public={len(public_probes)}")
    if [item.get("probe_id") for item in public_probes] != [item.get("probe_id") for item in probes]:
        errors.append("public/private probe order mismatch")
    matrix = Counter((probe.get("level"), probe.get("target_family")) for probe in probes)
    expected_matrix = {(level, family) for level in LEVELS for family in TARGET_FAMILIES}
    if set(matrix) != expected_matrix or any(matrix[key] != 1 for key in expected_matrix):
        errors.append("probe matrix is not a complete 5x5 design")
    source_ids = [probe.get("source_target_id") for probe in probes]
    if len(set(source_ids)) != len(source_ids):
        errors.append("probe source target reused within match")

    by_level: Counter[str] = Counter()
    by_family: Counter[str] = Counter()
    total_decisive_spans = 0
    total_decisive_edges = 0
    necessity_checks = 0
    for probe in probes:
        probe_id = probe.get("probe_id")
        level = probe.get("level")
        family = probe.get("target_family")
        by_level[str(level)] += 1
        by_family[str(family)] += 1
        if probe.get("source_target_id") not in table_by_id:
            errors.append(f"{probe_id}: source target is not an R21 scored target")
            continue
        contract = LEVEL_CONTRACTS.get(str(level))
        if contract is None:
            errors.append(f"{probe_id}: unknown level")
            continue
        relevant_claims = [claim for claim in probe_claims if claim.get("probe_id") == probe_id]
        decisive = probe.get("decisive_evidence", {})
        provenance = probe.get("provenance_context", {})
        decisive_spans = list(decisive.get("spans", []))
        decisive_edges = list(decisive.get("edges", []))
        provenance_spans = list(provenance.get("spans", []))
        provenance_edges = list(provenance.get("edges", []))
        total_decisive_spans += len(decisive_spans)
        total_decisive_edges += len(decisive_edges)
        if set(decisive_spans) & set(provenance_spans):
            errors.append(f"{probe_id}: decisive/provenance span overlap")
        if {_edge_tuple(edge) for edge in decisive_edges} & {_edge_tuple(edge) for edge in provenance_edges}:
            errors.append(f"{probe_id}: decisive/provenance edge overlap")
        for span_id in decisive_spans + provenance_spans:
            if span_id not in spans:
                errors.append(f"{probe_id}: unknown proof span {span_id}")
        for edge in decisive_edges + provenance_edges:
            relation = edge.get("relation")
            if relation not in ALLOWED_RELATIONS:
                errors.append(f"{probe_id}: invalid proof relation {relation}")
            child = span_to_claim.get(edge.get("from_span"))
            parent = span_to_claim.get(edge.get("to_span"))
            if child is None or parent is None:
                errors.append(f"{probe_id}: proof edge references unknown probe claim")
            elif child.get("relation") != relation or parent.get("claim_id") not in child.get("parent_claim_ids", []):
                errors.append(f"{probe_id}: proof edge disagrees with private graph")

        candidate_values = {str(claim.get("value")) for claim in relevant_claims if claim.get("value") is not None}
        if family == "derived_indicator":
            candidate_values.add(str(probe.get("value")))
        metrics = {
            "decisive_spans": len(decisive_spans),
            "decisive_edges": len(decisive_edges),
            "provenance_spans": len(provenance_spans),
            "provenance_edges": len(provenance_edges),
            "depth": _depth(decisive_edges),
            "candidate_values": len(candidate_values),
            "derivation_hops": sum(claim.get("relation") == "computed_from" and claim.get("span_id") in decisive_spans for claim in relevant_claims),
        }
        if metrics != probe.get("complexity"):
            errors.append(f"{probe_id}: stored complexity does not match graph")
        if not contract.min_decisive_spans <= metrics["decisive_spans"] <= contract.max_decisive_spans:
            errors.append(f"{probe_id}: decisive span count outside {level} contract")
        if not contract.min_decisive_edges <= metrics["decisive_edges"] <= contract.max_decisive_edges:
            errors.append(f"{probe_id}: decisive edge count outside {level} contract")
        if not contract.min_depth <= metrics["depth"] <= contract.max_depth:
            errors.append(f"{probe_id}: depth outside {level} contract")
        if metrics["candidate_values"] < contract.min_candidate_values:
            errors.append(f"{probe_id}: too few coherent candidate values for {level}")
        if level == "L4" and metrics["derivation_hops"] < 1:
            errors.append(f"{probe_id}: L4 lacks deterministic reconciliation")
        if level == "L5" and metrics["derivation_hops"] < 2:
            errors.append(f"{probe_id}: L5 lacks two-hop reconciliation")
        baseline_complexity = probe.get("r21_baseline", {})
        if metrics["decisive_spans"] < baseline_complexity.get("required_spans", 10**9):
            errors.append(f"{probe_id}: decisive spans regress below R21")
        if metrics["decisive_edges"] < baseline_complexity.get("required_edges", 10**9):
            errors.append(f"{probe_id}: decisive edges regress below R21")
        if metrics["depth"] < baseline_complexity.get("depth", 10**9):
            errors.append(f"{probe_id}: graph depth regresses below R21")

        decisive_span_set = set(decisive_spans)
        decisive_edge_set = {_edge_tuple(edge) for edge in decisive_edges}
        try:
            answer = resolve_probe(
                probe, relevant_claims,
                available_spans=decisive_span_set,
                available_edges=decisive_edge_set,
            )
            if answer != str(probe.get("value")):
                errors.append(f"{probe_id}: decisive proof resolves to wrong answer")
        except (KeyError, ValueError, ArithmeticError) as exc:
            errors.append(f"{probe_id}: decisive proof is insufficient: {exc}")
        for span_id in decisive_spans:
            necessity_checks += 1
            try:
                result = resolve_probe(
                    probe, relevant_claims,
                    available_spans=decisive_span_set - {span_id},
                    available_edges=decisive_edge_set,
                )
                if result == str(probe.get("value")):
                    errors.append(f"{probe_id}: non-necessary decisive span {span_id}")
            except (KeyError, ValueError, ArithmeticError):
                pass
        for edge in decisive_edges:
            edge_tuple = _edge_tuple(edge)
            necessity_checks += 1
            try:
                result = resolve_probe(
                    probe, relevant_claims,
                    available_spans=decisive_span_set,
                    available_edges=decisive_edge_set - {edge_tuple},
                )
                if result == str(probe.get("value")):
                    errors.append(f"{probe_id}: non-necessary decisive edge {edge_tuple}")
            except (KeyError, ValueError, ArithmeticError):
                pass

        if family == "derived_indicator":
            derivation = probe.get("derivation", {})
            values: list[str] = []
            try:
                for component in derivation.get("components", []):
                    target = table_by_id[component["target_id"]]
                    if str(target["value"]) != str(component["source_value"]):
                        raise ValueError("component source value disagrees with Track A")
                    extracted = _extract(str(target["value"]), component["extractor"])
                    if extracted != str(component["value"]):
                        raise ValueError("component extraction mismatch")
                    values.append(extracted)
                independently_derived = _derive(derivation["operation"], values)
                if independently_derived != str(probe.get("value")):
                    raise ValueError("independent derivation does not match probe gold")
            except (KeyError, ValueError, ArithmeticError) as exc:
                errors.append(f"{probe_id}: derivation audit failed: {exc}")

    public_blob = "\n".join(public_text + [json.dumps(public.get("probe_schema", []), ensure_ascii=False)])
    if re.search(r"\bL[1-5]\b", public_blob):
        errors.append("private difficulty label leaked into public data")
    for probe in probes:
        public_probe = next((item for item in public_probes if item.get("probe_id") == probe.get("probe_id")), {})
        answer = str(probe.get("value"))
        prompt_surface = f"{public_probe.get('question', '')}\n{public_probe.get('query_docket', '')}"
        if len(answer) >= 5 and answer in prompt_surface:
            errors.append(f"{probe.get('probe_id')}: gold answer leaked in public probe schema")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "summary": {
            "table_targets": len(table_targets),
            "probes": len(probes),
            "probe_claims": len(probe_claims),
            "documents": len(public.get("documents", [])),
            "public_words": public_words,
            "baseline_words": baseline.get("public_words", 0),
            "decisive_spans": total_decisive_spans,
            "decisive_edges": total_decisive_edges,
            "counterfactual_checks": necessity_checks,
            "by_level": dict(sorted(by_level.items())),
            "by_family": dict(sorted(by_family.items())),
        },
    }


__all__ = ["audit_instance"]
