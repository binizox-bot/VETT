from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from typing import Any

from .generator import REQUIRED_MECHANISMS
from .model import AuthorityPolicy, Claim, Target
from .resolver import resolve_target


FORBIDDEN_PUBLIC_MARKERS = (
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
        source=raw["source"],
        observed_at=int(raw["observed_at"]),
        innings=raw.get("innings"),
        field=raw["field"],
        entity=raw.get("entity"),
        value=raw.get("value"),
        status=raw.get("status", "asserted"),
        supersedes=tuple(raw.get("supersedes", [])),
        invalidates=tuple(raw.get("invalidates", [])),
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


def _prediction_for_baseline(
    name: str,
    eligible: list[Claim],
    policy: AuthorityPolicy,
) -> Any:
    assertions = sorted(
        (claim for claim in eligible if claim.status == "asserted"),
        key=lambda claim: (claim.observed_at, claim.claim_id),
    )
    if not assertions:
        return None
    if name == "first_mention":
        return assertions[0].value
    if name == "last_mention":
        return assertions[-1].value
    if name == "majority_vote":
        counts = Counter(claim.value for claim in assertions)
        top_count = max(counts.values())
        top = [value for value, count in counts.items() if count == top_count]
        return top[0] if len(top) == 1 else None
    if name == "source_only":
        best_rank = min(policy.rank(claim.source) for claim in assertions)
        values = {
            claim.value for claim in assertions if policy.rank(claim.source) == best_rank
        }
        return next(iter(values)) if len(values) == 1 else None
    raise ValueError(f"unknown baseline: {name}")


def audit_instance(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    gates: list[dict[str, Any]] = []
    target_results: list[dict[str, Any]] = []
    counterfactuals: list[dict[str, Any]] = []

    instance_ids = {
        public.get("instance_id"), gold.get("instance_id"), evidence.get("instance_id")
    }
    version_ids = {
        public.get("dataset_version"),
        gold.get("dataset_version"),
        evidence.get("dataset_version"),
    }
    gates.append(
        _gate(
            "artifact_identity",
            len(instance_ids) == 1 and None not in instance_ids and len(version_ids) == 1,
            {"instance_ids": sorted(str(value) for value in instance_ids), "versions": sorted(str(value) for value in version_ids)},
        )
    )

    public_text = json.dumps(public, ensure_ascii=False, sort_keys=True)
    leaked = [marker for marker in FORBIDDEN_PUBLIC_MARKERS if marker in public_text]
    gates.append(_gate("public_private_separation", not leaked, {"leaked_markers": leaked}))

    document_map = {document["document_id"]: document for document in public.get("documents", [])}
    spans: dict[tuple[str, str], str] = {}
    duplicate_spans: list[str] = []
    malformed_spans: list[str] = []
    for document in public.get("documents", []):
        for span in document.get("spans", []):
            key = (document["document_id"], span["span_id"])
            if key in spans:
                duplicate_spans.append("|".join(key))
            spans[key] = span["text"]
            marker = f"[{span['span_id']}] {span['text']}"
            if marker not in document.get("text", ""):
                malformed_spans.append("|".join(key))

    raw_claims = evidence.get("claims", [])
    claim_parse_errors: list[str] = []
    claims: list[Claim] = []
    for raw in raw_claims:
        try:
            claims.append(_claim_from_dict(raw))
        except (KeyError, TypeError, ValueError) as exc:
            claim_parse_errors.append(f"{raw.get('claim_id', '<missing>')}: {exc}")

    span_errors: list[str] = []
    for raw in raw_claims:
        key = (raw.get("document_id"), raw.get("span_id"))
        if key not in spans:
            span_errors.append(f"missing span {key}")
            continue
        expected_hash = hashlib.sha256(spans[key].encode("utf-8")).hexdigest()
        if raw.get("span_sha256") != expected_hash:
            span_errors.append(f"hash mismatch {key}")
        document = document_map.get(raw.get("document_id"))
        if document and (
            raw.get("source") != document.get("source_class")
            or int(raw.get("observed_at", -1)) != int(document.get("observed_at", -2))
        ):
            span_errors.append(f"document metadata mismatch {key}")
    gates.append(
        _gate(
            "span_integrity",
            not (duplicate_spans or malformed_spans or span_errors or claim_parse_errors),
            {
                "duplicate_spans": duplicate_spans,
                "malformed_spans": malformed_spans,
                "claim_errors": claim_parse_errors,
                "span_errors": span_errors,
            },
        )
    )

    span_text_values = list(spans.values())
    combined_language = " ".join(span_text_values).lower()
    artifact_patterns = {
        "match match winner": r"\bmatch match winner\b",
        "innings innings total": r"\binnings innings total\b",
        "1 no-balls": r"\b1 no-balls\b",
        "1 wides": r"\b1 wides\b",
        "1 byes": r"\b1 byes\b",
        "1 leg-byes": r"\b1 leg-byes\b",
        "other fields are unchanged": r"\bother fields are unchanged\b",
    }
    banned_artifacts = [
        artifact
        for artifact, pattern in artifact_patterns.items()
        if re.search(pattern, combined_language)
    ]
    prefixes = Counter(
        " ".join(text.lower().split()[:4]) for text in span_text_values if text.strip()
    )
    span_count = len(span_text_values)
    average_span_length = (
        sum(len(text) for text in span_text_values) / span_count if span_count else 0.0
    )
    maximum_prefix_ratio = (
        prefixes.most_common(1)[0][1] / span_count if prefixes and span_count else 1.0
    )
    unique_span_ratio = len(set(span_text_values)) / span_count if span_count else 0.0
    language_proxy_passed = (
        not banned_artifacts
        and average_span_length >= 55
        and maximum_prefix_ratio <= 0.20
        and unique_span_ratio >= 0.75
    )
    gates.append(
        _gate(
            "document_naturalness_proxy",
            language_proxy_passed,
            {
                "banned_artifacts": banned_artifacts,
                "average_span_length": round(average_span_length, 3),
                "maximum_four_word_prefix_ratio": round(maximum_prefix_ratio, 6),
                "unique_span_ratio": round(unique_span_ratio, 6),
                "boundary": "mechanical anti-template proxy; not a human naturalness judgment",
            },
        )
    )

    policy = AuthorityPolicy(public.get("authority_policy", {}).get("source_priority", {}))
    schema = public.get("target_schema", [])
    schema_by_id = {item["target_id"]: item for item in schema}
    gold_by_id = {item["target_id"]: item for item in gold.get("targets", [])}
    schema_ids = set(schema_by_id)
    gold_ids = set(gold_by_id)
    gates.append(
        _gate(
            "target_contract",
            len(schema_ids) == len(schema) and len(gold_ids) == len(gold.get("targets", [])) and schema_ids == gold_ids,
            {
                "schema_only": sorted(schema_ids - gold_ids),
                "gold_only": sorted(gold_ids - schema_ids),
                "duplicate_schema_ids": len(schema_ids) != len(schema),
                "duplicate_gold_ids": len(gold_ids) != len(gold.get("targets", [])),
            },
        )
    )

    coherence_errors: list[str] = []
    checked_worlds: list[str] = []
    required_score_fields = {
        "total_runs",
        "total_extras",
        "wides",
        "byes",
        "leg_byes",
    }
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
        if not required_score_fields.issubset(values_by_field):
            continue
        world_name = f"{document_id}:{innings_id}"
        checked_worlds.append(world_name)
        duplicate_fields = sorted(
            field for field in required_score_fields if len(values_by_field[field]) != 1
        )
        if duplicate_fields:
            coherence_errors.append(
                f"{world_name}: non-unique fields {duplicate_fields}"
            )
            continue
        try:
            world = {
                field: int(values_by_field[field][0]) for field in required_score_fields
            }
            gold_values = {
                field: int(gold_by_id[f"{innings_id}.{field}"]["value"])
                for field in required_score_fields
            }
        except (KeyError, TypeError, ValueError) as exc:
            coherence_errors.append(f"{world_name}: invalid numeric field ({exc})")
            continue
        no_balls = (
            gold_values["total_extras"]
            - gold_values["wides"]
            - gold_values["byes"]
            - gold_values["leg_byes"]
        )
        expected_extras = (
            world["wides"] + world["byes"] + world["leg_byes"] + no_balls
        )
        if no_balls < 0 or world["total_extras"] != expected_extras:
            coherence_errors.append(
                f"{world_name}: extras {world['total_extras']} != components {expected_extras}"
            )
        canonical_batting_subtotal = (
            gold_values["total_runs"] - gold_values["total_extras"]
        )
        world_batting_subtotal = world["total_runs"] - world["total_extras"]
        if world_batting_subtotal != canonical_batting_subtotal:
            coherence_errors.append(
                f"{world_name}: batting subtotal {world_batting_subtotal} != {canonical_batting_subtotal}"
            )
    gates.append(
        _gate(
            "alternate_world_cricket_coherence",
            not coherence_errors and len(checked_worlds) >= 8,
            {
                "checked_worlds": checked_worlds,
                "minimum_complete_worlds": 8,
                "errors": coherence_errors,
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
    decisive_errors: list[str] = []
    for target_id in sorted(direct_ids):
        target = _target_from_schema(schema_by_id[target_id])
        try:
            resolution = resolve_target(claims, target, policy)
        except ValueError as exc:
            resolution_errors.append(f"{target_id}: {exc}")
            continue
        expected = gold_by_id[target_id]["value"]
        expected_support = tuple(gold_by_id[target_id].get("decisive_support", []))
        correct = resolution.status == "resolved" and resolution.value == expected
        support_correct = tuple(resolution.decisive_claim_ids) == expected_support
        if not correct:
            resolution_errors.append(
                f"{target_id}: {resolution.status} {resolution.value!r}, expected {expected!r}"
            )
        if not support_correct:
            decisive_errors.append(
                f"{target_id}: {resolution.decisive_claim_ids!r}, expected {expected_support!r}"
            )
        if correct:
            resolved_values[target_id] = resolution.value
        target_results.append(
            {
                "target_id": target_id,
                "status": resolution.status,
                "value": resolution.value,
                "expected": expected,
                "decisive_claim_ids": list(resolution.decisive_claim_ids),
                "correct": correct and support_correct,
            }
        )
    gates.append(
        _gate(
            "unique_gold_resolution",
            not resolution_errors and not decisive_errors and len(resolved_values) == len(direct_ids),
            {"resolution_errors": resolution_errors, "support_errors": decisive_errors},
        )
    )

    derivation_by_id = {item["target_id"]: item for item in evidence.get("derivations", [])}
    derivation_errors: list[str] = []
    for target_id in sorted(derived_ids):
        derivation = derivation_by_id.get(target_id)
        if not derivation:
            derivation_errors.append(f"{target_id}: missing derivation")
            continue
        dependencies = derivation.get("dependencies", [])
        if any(dependency not in resolved_values for dependency in dependencies):
            derivation_errors.append(f"{target_id}: unresolved dependency")
            continue
        if derivation.get("operator") != "subtract" or len(dependencies) != 3:
            derivation_errors.append(f"{target_id}: unsupported derivation")
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
    gates.append(_gate("derived_constraints", not derivation_errors, {"errors": derivation_errors}))

    counterfactual_errors: list[str] = []
    for target_id in sorted(direct_ids):
        target = _target_from_schema(schema_by_id[target_id])
        decisive = set(gold_by_id[target_id].get("decisive_support", []))
        decisive_spans = set(gold_by_id[target_id].get("decisive_spans", []))
        if not decisive or not decisive_spans:
            counterfactual_errors.append(f"{target_id}: incomplete decisive support")
            continue
        removed_claims = {
            claim.claim_id for claim in claims if claim.span_id in decisive_spans
        }
        reduced = [claim for claim in claims if claim.span_id not in decisive_spans]
        try:
            resolution = resolve_target(reduced, target, policy)
            changed = not (
                resolution.status == "resolved"
                and resolution.value == gold_by_id[target_id]["value"]
            )
        except ValueError:
            changed = True
            resolution = None
        if not changed:
            counterfactual_errors.append(f"{target_id}: gold survives decisive deletion")
        counterfactuals.append(
            {
                "target_id": target_id,
                "removed_claim_ids": sorted(removed_claims),
                "removed_span_ids": sorted(decisive_spans),
                "passed": changed,
                "post_delete_status": resolution.status if resolution else "invalid_graph",
                "post_delete_value": resolution.value if resolution else None,
            }
        )
    gates.append(
        _gate(
            "decisive_deletion_counterfactual",
            not counterfactual_errors and len(counterfactuals) == len(direct_ids),
            {"errors": counterfactual_errors},
        )
    )

    baselines: dict[str, dict[str, Any]] = {}
    for name in ("first_mention", "last_mention", "majority_vote", "source_only"):
        correct = 0
        predictions: list[dict[str, Any]] = []
        for target_id in sorted(direct_ids):
            target = _target_from_schema(schema_by_id[target_id])
            eligible = [claim for claim in claims if claim.matches(target)]
            prediction = _prediction_for_baseline(name, eligible, policy)
            expected = gold_by_id[target_id]["value"]
            is_correct = prediction == expected
            correct += int(is_correct)
            predictions.append(
                {"target_id": target_id, "prediction": prediction, "correct": is_correct}
            )
        total = len(direct_ids)
        baselines[name] = {
            "correct": correct,
            "total": total,
            "accuracy": round(correct / total, 6) if total else 0.0,
            "predictions": predictions,
        }
    weak_accuracy = max(
        baselines[name]["accuracy"]
        for name in ("first_mention", "last_mention", "majority_vote")
    )
    gates.append(
        _gate(
            "position_and_frequency_traps",
            weak_accuracy <= 0.25,
            {"maximum_weak_baseline_accuracy": weak_accuracy},
        )
    )

    mechanisms = set(evidence.get("difficulty_mechanisms", []))
    source_classes = {document.get("source_class") for document in public.get("documents", [])}
    difficulty_errors: list[str] = []
    missing_mechanisms = set(REQUIRED_MECHANISMS) - mechanisms
    if missing_mechanisms:
        difficulty_errors.append(f"missing mechanisms: {sorted(missing_mechanisms)}")
    if len(source_classes) < 4:
        difficulty_errors.append(f"only {len(source_classes)} source classes")
    cross_innings_fields = {
        claim.field
        for claim in claims
        if claim.innings == "I1"
        and any(other.field == claim.field and other.innings == "I2" for other in claims)
    }
    if not cross_innings_fields:
        difficulty_errors.append("no cross-innings field collision")
    if not any(claim.status == "retraction" for claim in claims):
        difficulty_errors.append("no explicit invalidation claim")
    gates.append(
        _gate(
            "difficulty_structure",
            not difficulty_errors,
            {
                "errors": difficulty_errors,
                "source_classes": sorted(str(value) for value in source_classes),
                "cross_innings_fields": sorted(cross_innings_fields),
            },
        )
    )

    passed = all(gate["passed"] for gate in gates)
    return {
        "instance_id": public.get("instance_id"),
        "dataset_version": public.get("dataset_version"),
        "status": "PASS" if passed else "FAIL",
        "summary": {
            "documents": len(public.get("documents", [])),
            "claims": len(claims),
            "direct_targets": len(direct_ids),
            "derived_targets": len(derived_ids),
            "passed_gates": sum(int(gate["passed"]) for gate in gates),
            "total_gates": len(gates),
        },
        "gates": gates,
        "target_results": sorted(target_results, key=lambda item: item["target_id"]),
        "counterfactuals": counterfactuals,
        "baselines": baselines,
        "limitations": [
            "No human naturalness audit was performed.",
            "No external blind language-model evaluation was performed.",
            "Weak-baseline failure is a structural diagnostic, not proof of model failure.",
        ],
    }
