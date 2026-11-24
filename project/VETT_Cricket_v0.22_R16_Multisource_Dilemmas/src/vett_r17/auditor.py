from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import replace
from typing import Any

from .generator import REQUIRED_MECHANISMS
from .model import Claim, Target
from .resolver import resolve_target


FORBIDDEN_PUBLIC_MARKERS = (
    "source_priority",
    "authority_policy",
    "trust_tier",
    "supersedes",
    "invalidates",
    "derived_from",
    "gold_value",
    "decisive_support",
    "canonical_source_coordinate",
    "private_evidence",
)


def _claim_from_dict(raw: dict[str, Any]) -> Claim:
    return Claim(
        claim_id=raw["claim_id"],
        document_id=raw["document_id"],
        span_id=raw["span_id"],
        docket_id=raw["docket_id"],
        observed_at=int(raw["observed_at"]),
        innings=raw.get("innings"),
        field=raw["field"],
        entity=raw.get("entity"),
        value=raw.get("value"),
        status=raw.get("status", "asserted"),
        supersedes=tuple(raw.get("supersedes", [])),
        invalidates=tuple(raw.get("invalidates", [])),
        derived_from=tuple(raw.get("derived_from", [])),
    )


def _target_from_schema(raw: dict[str, Any]) -> Target:
    return Target(
        target_id=raw["target_id"],
        innings=raw.get("innings"),
        field=raw["field"],
        entity=raw.get("entity"),
    )


def _gate(name: str, passed: bool, details: Any) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details}


def _public_minute(document: dict[str, Any]) -> int:
    match = re.fullmatch(r"T\+(\d+)m", str(document.get("published_at", "")))
    if not match:
        raise ValueError(f"invalid public timestamp: {document.get('published_at')!r}")
    return int(match.group(1))


def _baseline_prediction(
    name: str,
    eligible: list[Claim],
    document_order: dict[str, int],
    span_order: dict[tuple[str, str], int],
) -> Any:
    assertions = [claim for claim in eligible if claim.status == "asserted"]
    if not assertions:
        return None
    if name == "first_mention":
        return min(assertions, key=lambda item: (item.observed_at, item.claim_id)).value
    if name == "latest_timestamp":
        return max(assertions, key=lambda item: (item.observed_at, item.claim_id)).value
    if name == "last_array_mention":
        return max(
            assertions,
            key=lambda item: (
                document_order[item.document_id],
                span_order[(item.document_id, item.span_id)],
                item.claim_id,
            ),
        ).value
    if name == "majority_vote":
        counts = Counter(claim.value for claim in assertions)
        top_count = max(counts.values())
        top = [value for value, count in counts.items() if count == top_count]
        return top[0] if len(top) == 1 else None
    raise ValueError(f"unknown baseline: {name}")


def _without_edge(claim: Claim, relation: str, referenced_id: str) -> Claim | None:
    if relation == "supersedes":
        return replace(
            claim,
            supersedes=tuple(item for item in claim.supersedes if item != referenced_id),
        )
    if relation == "derived_from":
        return replace(
            claim,
            derived_from=tuple(item for item in claim.derived_from if item != referenced_id),
        )
    if relation == "invalidates":
        remaining = tuple(item for item in claim.invalidates if item != referenced_id)
        if claim.status == "retraction" and not remaining:
            return None
        return replace(claim, invalidates=remaining)
    raise ValueError(f"unsupported edge relation: {relation}")


def audit_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    target_results: list[dict[str, Any]] = []
    counterfactuals: list[dict[str, Any]] = []
    edge_ablations: list[dict[str, Any]] = []

    instance_ids = {
        public.get("instance_id"),
        gold.get("instance_id"),
        evidence.get("instance_id"),
    }
    versions = {
        public.get("dataset_version"),
        gold.get("dataset_version"),
        evidence.get("dataset_version"),
    }
    gates.append(
        _gate(
            "artifact_identity",
            len(instance_ids) == 1 and None not in instance_ids and len(versions) == 1,
            {
                "instance_ids": sorted(str(item) for item in instance_ids),
                "versions": sorted(str(item) for item in versions),
            },
        )
    )

    public_text = json.dumps(public, ensure_ascii=False, sort_keys=True)
    leaked = [marker for marker in FORBIDDEN_PUBLIC_MARKERS if marker in public_text]
    gates.append(
        _gate("public_policy_hidden", not leaked, {"leaked_markers": leaked})
    )

    documents = public.get("documents", [])
    document_map = {item.get("document_id"): item for item in documents}
    chronology_errors: list[str] = []
    public_times: list[int] = []
    for document in documents:
        try:
            public_times.append(_public_minute(document))
        except ValueError as exc:
            chronology_errors.append(str(exc))
    chronology_passed = (
        len(document_map) == len(documents)
        and len(public_times) == len(documents)
        and public_times != sorted(public_times)
        and bool(public_times)
        and public_times[-1] != max(public_times)
    )
    gates.append(
        _gate(
            "shuffled_chronology",
            chronology_passed and not chronology_errors,
            {"published_minutes_in_array_order": public_times, "errors": chronology_errors},
        )
    )

    spans: dict[tuple[str, str], str] = {}
    span_order: dict[tuple[str, str], int] = {}
    span_errors: list[str] = []
    for document in documents:
        document_id = document.get("document_id")
        for index, span in enumerate(document.get("spans", [])):
            key = (document_id, span.get("span_id"))
            if key in spans:
                span_errors.append(f"duplicate span: {key}")
            spans[key] = span.get("text", "")
            span_order[key] = index
            marker = f"[{span.get('span_id')}] {span.get('text', '')}"
            if marker not in document.get("text", ""):
                span_errors.append(f"span absent from document text: {key}")

    raw_claims = evidence.get("claims", [])
    claims: list[Claim] = []
    claim_parse_errors: list[str] = []
    for raw in raw_claims:
        try:
            claims.append(_claim_from_dict(raw))
        except (KeyError, TypeError, ValueError) as exc:
            claim_parse_errors.append(f"{raw.get('claim_id', '<missing>')}: {exc}")
    raw_by_id = {
        raw.get("claim_id"): raw for raw in raw_claims if raw.get("claim_id") is not None
    }
    if len(raw_by_id) != len(raw_claims):
        claim_parse_errors.append("duplicate or missing raw claim IDs")

    for raw in raw_claims:
        key = (raw.get("document_id"), raw.get("span_id"))
        if key not in spans:
            span_errors.append(f"claim references missing span: {key}")
            continue
        expected_hash = hashlib.sha256(spans[key].encode("utf-8")).hexdigest()
        if raw.get("span_sha256") != expected_hash:
            span_errors.append(f"span hash mismatch: {key}")
        document = document_map.get(raw.get("document_id"))
        if document:
            try:
                if int(raw.get("observed_at", -1)) != _public_minute(document):
                    span_errors.append(f"timestamp mismatch: {key}")
            except ValueError:
                span_errors.append(f"invalid document timestamp: {key}")
    gates.append(
        _gate(
            "span_and_claim_integrity",
            not span_errors and not claim_parse_errors,
            {"span_errors": span_errors, "claim_errors": claim_parse_errors},
        )
    )

    identifier_errors: list[str] = []
    role_tokens = (
        "final",
        "draft",
        "amend",
        "wire",
        "web",
        "radio",
        "archive",
        "void",
        "review",
        "live",
    )
    for document_id in document_map:
        identifier = str(document_id)
        if not re.fullmatch(r"packet_[0-9a-f]{10}", identifier):
            identifier_errors.append(f"non-opaque document ID: {identifier}")
        if any(token in identifier.lower() for token in role_tokens):
            identifier_errors.append(f"role-bearing document ID: {identifier}")
    for raw in raw_claims:
        docket_id = str(raw.get("docket_id", ""))
        if not re.fullmatch(r"K[0-9A-F]{8}-(?:M|I1|I2)", docket_id):
            identifier_errors.append(
                f"{raw.get('claim_id')}: non-opaque docket ID {docket_id}"
            )
    gates.append(
        _gate(
            "opaque_identifiers",
            not identifier_errors,
            {"errors": identifier_errors},
        )
    )

    witness_errors: list[str] = []
    witness_count = 0
    for raw in raw_claims:
        key = (raw.get("document_id"), raw.get("span_id"))
        text = spans.get(key, "")
        if raw.get("docket_id") not in text:
            witness_errors.append(f"{raw.get('claim_id')}: own docket absent")
        expected_edges = {
            *(("supersedes", item) for item in raw.get("supersedes", [])),
            *(("invalidates", item) for item in raw.get("invalidates", [])),
            *(("derived_from", item) for item in raw.get("derived_from", [])),
        }
        actual_edges: set[tuple[str, str]] = set()
        for witness in raw.get("edge_witnesses", []):
            witness_count += 1
            relation = witness.get("relation")
            normalized_relation = "invalidates" if relation == "withdraws" else relation
            referenced_id = witness.get("referenced_claim_id")
            actual_edges.add((str(normalized_relation), str(referenced_id)))
            token = witness.get("token", "")
            if not token or token not in text:
                witness_errors.append(
                    f"{raw.get('claim_id')}: missing literal witness {token!r}"
                )
            parent = raw_by_id.get(referenced_id)
            if not parent:
                witness_errors.append(
                    f"{raw.get('claim_id')}: witness references unknown claim {referenced_id}"
                )
            elif parent.get("docket_id") not in token:
                witness_errors.append(
                    f"{raw.get('claim_id')}: parent docket absent from witness"
                )
        if expected_edges != actual_edges:
            witness_errors.append(
                f"{raw.get('claim_id')}: edge/witness mismatch "
                f"expected={sorted(expected_edges)} actual={sorted(actual_edges)}"
            )
    gates.append(
        _gate(
            "edge_witness_visibility",
            not witness_errors and witness_count >= 90,
            {"witness_count": witness_count, "errors": witness_errors},
        )
    )

    span_text_values = list(spans.values())
    combined_language = " ".join(span_text_values).lower()
    artifact_patterns = {
        "match match winner": r"\bmatch match winner\b",
        "innings innings total": r"\binnings innings total\b",
        "1 wides": r"\b1 wides\b",
        "1 byes": r"\b1 byes\b",
        "1 leg-byes": r"\b1 leg-byes\b",
        "other fields are unchanged": r"\bother fields are unchanged\b",
    }
    banned = [
        label
        for label, pattern in artifact_patterns.items()
        if re.search(pattern, combined_language)
    ]
    prefixes = Counter(
        " ".join(text.lower().split()[:4]) for text in span_text_values if text.strip()
    )
    span_count = len(span_text_values)
    average_length = (
        sum(len(text) for text in span_text_values) / span_count if span_count else 0.0
    )
    prefix_ratio = (
        prefixes.most_common(1)[0][1] / span_count if prefixes and span_count else 1.0
    )
    unique_ratio = len(set(span_text_values)) / span_count if span_count else 0.0
    gates.append(
        _gate(
            "document_naturalness_proxy",
            not banned
            and average_length >= 80
            and prefix_ratio <= 0.15
            and unique_ratio >= 0.90,
            {
                "banned_artifacts": banned,
                "average_span_length": round(average_length, 3),
                "maximum_four_word_prefix_ratio": round(prefix_ratio, 6),
                "unique_span_ratio": round(unique_ratio, 6),
                "boundary": "mechanical anti-template proxy; not human judgment",
            },
        )
    )

    schema = public.get("target_schema", [])
    schema_by_id = {item.get("target_id"): item for item in schema}
    gold_targets = gold.get("targets", [])
    gold_by_id = {item.get("target_id"): item for item in gold_targets}
    schema_ids = set(schema_by_id)
    gold_ids = set(gold_by_id)
    gates.append(
        _gate(
            "target_contract",
            len(schema_by_id) == len(schema)
            and len(gold_by_id) == len(gold_targets)
            and schema_ids == gold_ids,
            {
                "schema_only": sorted(str(item) for item in schema_ids - gold_ids),
                "gold_only": sorted(str(item) for item in gold_ids - schema_ids),
            },
        )
    )

    direct_ids = [
        target_id
        for target_id, raw in schema_by_id.items()
        if "allowed_rule" not in raw
    ]
    derived_ids = [target_id for target_id in schema_by_id if target_id not in direct_ids]
    resolved_values: dict[str, Any] = {}
    resolution_errors: list[str] = []
    for target_id in sorted(direct_ids):
        target = _target_from_schema(schema_by_id[target_id])
        try:
            resolution = resolve_target(claims, target)
        except ValueError as exc:
            resolution_errors.append(f"{target_id}: {exc}")
            continue
        expected = gold_by_id[target_id]["value"]
        expected_support = tuple(gold_by_id[target_id].get("decisive_support", []))
        correct = (
            resolution.status == "resolved"
            and resolution.value == expected
            and resolution.decisive_claim_ids == expected_support
        )
        if not correct:
            resolution_errors.append(
                f"{target_id}: {resolution.status} {resolution.value!r} "
                f"support={resolution.decisive_claim_ids!r}, expected {expected!r} "
                f"support={expected_support!r}"
            )
        else:
            resolved_values[target_id] = resolution.value
        target_results.append(
            {
                "target_id": target_id,
                "status": resolution.status,
                "value": resolution.value,
                "expected": expected,
                "decisive_claim_ids": list(resolution.decisive_claim_ids),
                "correct": correct,
            }
        )
    gates.append(
        _gate(
            "unique_graph_resolution",
            not resolution_errors and len(resolved_values) == len(direct_ids),
            {"errors": resolution_errors},
        )
    )

    coherence_errors: list[str] = []
    checked_worlds: list[str] = []
    score_fields = {"total_runs", "total_extras", "wides", "byes", "leg_byes"}
    assertions_by_world: dict[tuple[str, str], list[Claim]] = {}
    for claim in claims:
        if claim.status == "asserted" and claim.innings in {"I1", "I2"}:
            assertions_by_world.setdefault(
                (claim.document_id, str(claim.innings)), []
            ).append(claim)
    for (document_id, innings_id), world_claims in sorted(assertions_by_world.items()):
        values_by_field: dict[str, list[Any]] = {}
        for claim in world_claims:
            values_by_field.setdefault(claim.field, []).append(claim.value)
        if not score_fields.issubset(values_by_field):
            continue
        world_name = f"{document_id}:{innings_id}"
        checked_worlds.append(world_name)
        if any(len(values_by_field[field]) != 1 for field in score_fields):
            coherence_errors.append(f"{world_name}: non-unique score fields")
            continue
        try:
            world = {field: int(values_by_field[field][0]) for field in score_fields}
            canonical = {
                field: int(gold_by_id[f"{innings_id}.{field}"]["value"])
                for field in score_fields
            }
        except (KeyError, TypeError, ValueError) as exc:
            coherence_errors.append(f"{world_name}: invalid numeric field ({exc})")
            continue
        no_balls = (
            canonical["total_extras"]
            - canonical["wides"]
            - canonical["byes"]
            - canonical["leg_byes"]
        )
        component_extras = (
            world["wides"] + world["byes"] + world["leg_byes"] + no_balls
        )
        if no_balls < 0 or world["total_extras"] != component_extras:
            coherence_errors.append(
                f"{world_name}: extras {world['total_extras']} != {component_extras}"
            )
        if (
            world["total_runs"] - world["total_extras"]
            != canonical["total_runs"] - canonical["total_extras"]
        ):
            coherence_errors.append(f"{world_name}: batting subtotal changed")
    gates.append(
        _gate(
            "alternate_world_cricket_coherence",
            not coherence_errors and len(checked_worlds) >= 14,
            {
                "checked_worlds": checked_worlds,
                "minimum_complete_worlds": 14,
                "errors": coherence_errors,
            },
        )
    )

    derivations = {
        item.get("target_id"): item for item in evidence.get("derivations", [])
    }
    derivation_errors: list[str] = []
    for target_id in sorted(derived_ids):
        derivation = derivations.get(target_id)
        if not derivation:
            derivation_errors.append(f"{target_id}: missing derivation")
            continue
        dependencies = derivation.get("dependencies", [])
        if (
            derivation.get("operator") != "subtract"
            or len(dependencies) != 3
            or any(item not in resolved_values for item in dependencies)
        ):
            derivation_errors.append(f"{target_id}: invalid or unresolved derivation")
            continue
        value = (
            resolved_values[dependencies[0]]
            - resolved_values[dependencies[1]]
            - resolved_values[dependencies[2]]
        )
        expected = gold_by_id[target_id]["value"]
        if value != expected or value != derivation.get("value"):
            derivation_errors.append(f"{target_id}: derived {value}, expected {expected}")
        else:
            resolved_values[target_id] = value
            target_results.append(
                {
                    "target_id": target_id,
                    "status": "derived",
                    "value": value,
                    "expected": expected,
                    "dependencies": dependencies,
                    "correct": True,
                }
            )
    gates.append(
        _gate("derived_constraints", not derivation_errors, {"errors": derivation_errors})
    )

    counterfactual_errors: list[str] = []
    for target_id in sorted(direct_ids):
        target = _target_from_schema(schema_by_id[target_id])
        decisive_spans = set(gold_by_id[target_id].get("decisive_spans", []))
        if not decisive_spans:
            counterfactual_errors.append(f"{target_id}: no decisive span")
            continue
        reduced = [claim for claim in claims if claim.span_id not in decisive_spans]
        try:
            resolution = resolve_target(reduced, target)
            changed = not (
                resolution.status == "resolved"
                and resolution.value == gold_by_id[target_id]["value"]
            )
        except ValueError:
            changed = True
            resolution = None
        if not changed:
            counterfactual_errors.append(f"{target_id}: gold survived span deletion")
        counterfactuals.append(
            {
                "target_id": target_id,
                "removed_span_ids": sorted(decisive_spans),
                "passed": changed,
                "post_delete_status": resolution.status if resolution else "invalid_graph",
                "post_delete_value": resolution.value if resolution else None,
            }
        )
    gates.append(
        _gate(
            "decisive_span_counterfactual",
            not counterfactual_errors and len(counterfactuals) == len(direct_ids),
            {"errors": counterfactual_errors},
        )
    )

    edge_ablation_errors: list[str] = []
    for claim in claims:
        relations = (
            [("supersedes", item) for item in claim.supersedes]
            + [("invalidates", item) for item in claim.invalidates]
            + [("derived_from", item) for item in claim.derived_from]
        )
        if not relations:
            continue
        target_id = next(
            (
                candidate_id
                for candidate_id in direct_ids
                if _target_from_schema(schema_by_id[candidate_id]).innings == claim.innings
                and _target_from_schema(schema_by_id[candidate_id]).field == claim.field
                and _target_from_schema(schema_by_id[candidate_id]).entity == claim.entity
            ),
            None,
        )
        if target_id is None:
            edge_ablation_errors.append(f"{claim.claim_id}: no matching target")
            continue
        target = _target_from_schema(schema_by_id[target_id])
        for relation, referenced_id in relations:
            replacement = _without_edge(claim, relation, referenced_id)
            mutated = [
                candidate
                for candidate in claims
                if candidate.claim_id != claim.claim_id
            ]
            if replacement is not None:
                mutated.append(replacement)
            try:
                result = resolve_target(mutated, target)
                passed = not (
                    result.status == "resolved"
                    and result.value == gold_by_id[target_id]["value"]
                )
                post_status = result.status
                post_value = result.value
            except ValueError:
                passed = True
                post_status = "invalid_graph"
                post_value = None
            if not passed:
                edge_ablation_errors.append(
                    f"{claim.claim_id}:{relation}:{referenced_id} is not necessary"
                )
            edge_ablations.append(
                {
                    "target_id": target_id,
                    "claim_id": claim.claim_id,
                    "relation": relation,
                    "referenced_claim_id": referenced_id,
                    "passed": passed,
                    "post_ablation_status": post_status,
                    "post_ablation_value": post_value,
                }
            )
    gates.append(
        _gate(
            "graph_edge_necessity",
            not edge_ablation_errors and len(edge_ablations) >= 90,
            {"ablations": len(edge_ablations), "errors": edge_ablation_errors},
        )
    )

    document_order = {
        document.get("document_id"): index for index, document in enumerate(documents)
    }
    baselines: dict[str, dict[str, Any]] = {}
    for name in (
        "first_mention",
        "last_array_mention",
        "latest_timestamp",
        "majority_vote",
    ):
        correct_count = 0
        predictions: list[dict[str, Any]] = []
        for target_id in sorted(direct_ids):
            target = _target_from_schema(schema_by_id[target_id])
            eligible = [claim for claim in claims if claim.matches(target)]
            prediction = _baseline_prediction(
                name, eligible, document_order, span_order
            )
            is_correct = prediction == gold_by_id[target_id]["value"]
            correct_count += int(is_correct)
            predictions.append(
                {"target_id": target_id, "prediction": prediction, "correct": is_correct}
            )
        total = len(direct_ids)
        baselines[name] = {
            "correct": correct_count,
            "total": total,
            "accuracy": round(correct_count / total, 6) if total else 0.0,
            "predictions": predictions,
        }
    maximum_shortcut = max(item["accuracy"] for item in baselines.values())
    gates.append(
        _gate(
            "shortcut_resistance",
            maximum_shortcut <= 0.25,
            {"maximum_shortcut_accuracy": maximum_shortcut},
        )
    )

    mechanisms = set(evidence.get("difficulty_mechanisms", []))
    difficulty_errors: list[str] = []
    missing = set(REQUIRED_MECHANISMS) - mechanisms
    if missing:
        difficulty_errors.append(f"missing mechanisms: {sorted(missing)}")
    if len(documents) < 10:
        difficulty_errors.append(f"only {len(documents)} documents")
    if not any(claim.status == "retraction" for claim in claims):
        difficulty_errors.append("no retraction")
    if not any(
        claim.derived_from
        and any(raw_by_id[parent].get("derived_from") for parent in claim.derived_from)
        for claim in claims
    ):
        difficulty_errors.append("no multi-hop copy lineage")
    if not any(
        claim.supersedes
        and any(raw_by_id[parent].get("supersedes") for parent in claim.supersedes)
        for claim in claims
    ):
        difficulty_errors.append("no correction-of-correction chain")
    gates.append(
        _gate(
            "difficulty_structure",
            not difficulty_errors,
            {"errors": difficulty_errors, "mechanisms": sorted(mechanisms)},
        )
    )

    passed = all(gate["passed"] for gate in gates)
    return {
        "instance_id": public.get("instance_id"),
        "dataset_version": public.get("dataset_version"),
        "status": "PASS" if passed else "FAIL",
        "summary": {
            "documents": len(documents),
            "claims": len(claims),
            "direct_targets": len(direct_ids),
            "derived_targets": len(derived_ids),
            "passed_gates": sum(int(gate["passed"]) for gate in gates),
            "total_gates": len(gates),
        },
        "gates": gates,
        "target_results": sorted(target_results, key=lambda item: item["target_id"]),
        "counterfactuals": counterfactuals,
        "edge_ablations": edge_ablations,
        "baselines": baselines,
        "limitations": [
            "No human naturalness audit was performed.",
            "No external blind language-model evaluation was performed.",
            "Shortcut failure is not proof that a language model fails.",
        ],
    }
