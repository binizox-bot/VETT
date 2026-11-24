from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from .generator import Bundle
from .spec import (
    DEFAULT_SEED,
    MEASUREMENT_DESIGN_REVISION,
    MEASUREMENT_VALIDITY_VERSION,
)


PUBLIC_SPAN_ID = re.compile(r"^s_[0-9a-f]{24}$")
ROLE_BEARING_TOKENS = (
    "authority",
    "bridge",
    "conflict",
    "distractor",
    "fact",
    "gold",
    "locator",
    "policy",
    "reject",
    "rule",
    "shadow",
    "support",
)


@dataclass(frozen=True)
class NeutralizedBundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _replace_exact(value: Any, mapping: dict[str, str]) -> Any:
    """Replace identifiers only when a complete JSON string equals an identifier."""
    if isinstance(value, str):
        return mapping.get(value, value)
    if isinstance(value, list):
        return [_replace_exact(item, mapping) for item in value]
    if isinstance(value, dict):
        return {
            mapping.get(str(key), str(key)): _replace_exact(item, mapping)
            for key, item in value.items()
        }
    return value


def _span_ids(public: dict[str, Any]) -> list[str]:
    return [
        str(span["span_id"])
        for document in public.get("documents", [])
        for span in document.get("spans", [])
    ]


def build_identifier_map(
    public: dict[str, Any],
    *,
    seed: int = DEFAULT_SEED,
) -> dict[str, str]:
    instance_id = str(public.get("instance_id", ""))
    old_ids = _span_ids(public)
    if len(old_ids) != len(set(old_ids)):
        raise ValueError("cannot neutralize duplicate public span IDs")
    mapping = {
        old_id: "s_" + hashlib.sha256(
            f"{seed}|{instance_id}|role-neutral-span-v1|{old_id}".encode("utf-8")
        ).hexdigest()[:24]
        for old_id in old_ids
    }
    if len(mapping) != len(set(mapping.values())):
        raise ValueError("role-neutral public span ID collision")
    return mapping


def neutralize_bundle(
    bundle: Bundle,
    *,
    seed: int = DEFAULT_SEED,
    dataset_version: str = MEASUREMENT_VALIDITY_VERSION,
    measurement_design_revision: str = MEASUREMENT_DESIGN_REVISION,
) -> NeutralizedBundle:
    """Remove generator/role names from every public span identifier.

    The reversible map is stored only in private evidence. Text, ordering, gold
    semantics and graph topology are unchanged. This is a measurement-validity
    transform, not a difficulty-label transform.
    """
    mapping = build_identifier_map(bundle.public, seed=seed)
    public = _replace_exact(_clone(bundle.public), mapping)
    gold = _replace_exact(_clone(bundle.gold), mapping)
    evidence = _replace_exact(_clone(bundle.evidence), mapping)
    for artifact in (public, gold, evidence):
        artifact["dataset_version"] = dataset_version
        artifact["measurement_design_revision"] = measurement_design_revision
    public["public_identifier_contract"] = {
        "scheme": "role_neutral_sha256_v1",
        "all_span_ids_same_shape": True,
        "private_inverse_map_excluded": True,
    }
    evidence["r26_13_identifier_map"] = {
        "scheme": "role_neutral_sha256_v1",
        "seed": seed,
        "instance_id": str(public["instance_id"]),
        "old_to_public": [
            {"internal_id": old_id, "public_id": mapping[old_id]}
            for old_id in sorted(mapping)
        ],
    }
    return NeutralizedBundle(public=public, gold=gold, evidence=evidence)


def restore_internal_identifiers(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
) -> NeutralizedBundle:
    registry = evidence.get("r26_13_identifier_map", {})
    rows = registry.get("old_to_public", [])
    inverse = {
        str(row["public_id"]): str(row["internal_id"])
        for row in rows
    }
    if len(inverse) != len(rows):
        raise ValueError("duplicate public IDs in private inverse registry")
    restored_public = _replace_exact(_clone(public), inverse)
    restored_gold = _replace_exact(_clone(gold), inverse)
    restored_evidence = _replace_exact(_clone(evidence), inverse)
    restored_evidence.pop("r26_13_identifier_map", None)
    restored_public.pop("public_identifier_contract", None)
    return NeutralizedBundle(
        public=restored_public,
        gold=restored_gold,
        evidence=restored_evidence,
    )


def audit_identifier_neutrality(
    public: dict[str, Any],
    gold: dict[str, Any],
    evidence: dict[str, Any],
    *,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    errors: list[str] = []
    public_ids = _span_ids(public)
    registry = evidence.get("r26_13_identifier_map", {})
    rows = registry.get("old_to_public", [])
    old_to_public = {
        str(row.get("internal_id")): str(row.get("public_id"))
        for row in rows
    }
    if len(public_ids) != len(set(public_ids)):
        errors.append("duplicate_public_span_ids")
    malformed = [span_id for span_id in public_ids if not PUBLIC_SPAN_ID.fullmatch(span_id)]
    if malformed:
        errors.append(f"non_neutral_id_shape:{len(malformed)}")
    role_bearing = [
        span_id for span_id in public_ids
        if any(token in span_id.casefold() for token in ROLE_BEARING_TOKENS)
    ]
    if role_bearing:
        errors.append(f"role_bearing_public_ids:{len(role_bearing)}")
    if set(old_to_public.values()) != set(public_ids):
        errors.append("private_identifier_registry_coverage")
    if len(old_to_public) != len(rows):
        errors.append("private_identifier_registry_duplicates")
    try:
        restored = restore_internal_identifiers(public, gold, evidence)
        expected = build_identifier_map(restored.public, seed=seed)
        if expected != old_to_public:
            errors.append("identifier_derivation_not_reproducible")
        round_trip = neutralize_bundle(
            Bundle(restored.public, restored.gold, restored.evidence),
            seed=seed,
            dataset_version=str(public.get("dataset_version")),
            measurement_design_revision=str(
                public.get("measurement_design_revision", MEASUREMENT_DESIGN_REVISION)
            ),
        )
        if round_trip.public != public or round_trip.gold != gold or round_trip.evidence != evidence:
            errors.append("identifier_round_trip_mismatch")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"identifier_round_trip_error:{exc}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "public_span_ids": len(public_ids),
        "unique_public_span_ids": len(set(public_ids)),
        "neutral_shape_ids": len(public_ids) - len(malformed),
        "role_bearing_public_ids": len(role_bearing),
        "private_mapping_entries": len(rows),
        "scheme": registry.get("scheme"),
        "semantic_text_changed": False,
    }


__all__ = [
    "NeutralizedBundle",
    "PUBLIC_SPAN_ID",
    "ROLE_BEARING_TOKENS",
    "audit_identifier_neutrality",
    "build_identifier_map",
    "neutralize_bundle",
    "restore_internal_identifiers",
]
