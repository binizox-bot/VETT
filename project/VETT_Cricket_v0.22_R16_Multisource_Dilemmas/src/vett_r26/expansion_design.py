from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .anchors import ANCHOR_BY_SCENARIO_FAMILY
from .spec import CANDIDATE_VERSION, DEFAULT_SEED, DIFFICULTY_DESIGN_REVISION


LEVELS = ("L1", "L2", "L3", "L4", "L5")
ALGORITHM = "seeded_block_latin_square_v1"
EXPECTED_MATCHES = 220


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _family_index() -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for family, anchor in ANCHOR_BY_SCENARIO_FAMILY.items():
        level = family.split("_", 1)[0]
        key = (anchor, level)
        if key in result:
            raise ValueError(f"duplicate anchor-level family: {key}")
        result[key] = family
    return result


def audit_expansion_plan(plan: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    rows = plan.get("assignments", [])
    match_ids = plan.get("match_ids", [])
    anchors = sorted(set(ANCHOR_BY_SCENARIO_FAMILY.values()))
    expected_pairs = {(anchor, level) for anchor in anchors for level in LEVELS}
    expected_families = set(ANCHOR_BY_SCENARIO_FAMILY)
    if plan.get("algorithm") != ALGORITHM:
        errors.append(f"algorithm:{plan.get('algorithm')}")
    if plan.get("dataset_version") != CANDIDATE_VERSION:
        errors.append(f"dataset_version:{plan.get('dataset_version')}")
    if plan.get("difficulty_design_revision") != DIFFICULTY_DESIGN_REVISION:
        errors.append("difficulty_design_revision")
    if len(match_ids) != EXPECTED_MATCHES or len(set(match_ids)) != EXPECTED_MATCHES:
        errors.append(f"match_ids:{len(match_ids)}:{len(set(match_ids))}")
    if len(rows) != EXPECTED_MATCHES * len(LEVELS):
        errors.append(f"assignment_count:{len(rows)}")

    by_match: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_block: dict[int, list[dict[str, Any]]] = defaultdict(list)
    pair_counts: Counter[tuple[str, str]] = Counter()
    family_counts: Counter[str] = Counter()
    row_keys: set[tuple[str, str]] = set()
    for row in rows:
        match_id = str(row.get("match_id"))
        level = str(row.get("level"))
        anchor = str(row.get("cross_level_anchor_family"))
        family = str(row.get("scenario_family"))
        key = (match_id, level)
        if key in row_keys:
            errors.append(f"duplicate_assignment:{match_id}:{level}")
        row_keys.add(key)
        if ANCHOR_BY_SCENARIO_FAMILY.get(family) != anchor:
            errors.append(f"family_anchor:{match_id}:{level}:{family}:{anchor}")
        if not family.startswith(f"{level}_"):
            errors.append(f"family_level:{match_id}:{level}:{family}")
        by_match[match_id].append(row)
        try:
            by_block[int(row.get("block_id"))].append(row)
        except (TypeError, ValueError):
            errors.append(f"block_id:{match_id}:{level}:{row.get('block_id')}")
        pair_counts[(anchor, level)] += 1
        family_counts[family] += 1

    for match_id in match_ids:
        match_rows = by_match.get(match_id, [])
        if {str(row.get("level")) for row in match_rows} != set(LEVELS):
            errors.append(f"match_levels:{match_id}")
        if {
            str(row.get("cross_level_anchor_family")) for row in match_rows
        } != set(anchors):
            errors.append(f"match_anchors:{match_id}")
    expected_blocks = EXPECTED_MATCHES // len(LEVELS)
    if set(by_block) != set(range(expected_blocks)):
        errors.append(f"block_ids:{sorted(by_block)}")
    for block_id in range(expected_blocks):
        block_rows = by_block.get(block_id, [])
        block_matches = {str(row.get("match_id")) for row in block_rows}
        if len(block_matches) != len(LEVELS):
            errors.append(f"block_matches:{block_id}:{len(block_matches)}")
        for level in LEVELS:
            level_anchors = {
                str(row.get("cross_level_anchor_family"))
                for row in block_rows
                if row.get("level") == level
            }
            if level_anchors != set(anchors):
                errors.append(f"block_latin:{block_id}:{level}")

    expected_per_pair = EXPECTED_MATCHES // len(anchors)
    if set(pair_counts) != expected_pairs or set(pair_counts.values()) != {
        expected_per_pair
    }:
        errors.append("anchor_level_balance")
    if set(family_counts) != expected_families or set(family_counts.values()) != {
        expected_per_pair
    }:
        errors.append("scenario_family_balance")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "matches": len(match_ids),
        "assignments": len(rows),
        "blocks": len(by_block),
        "anchor_level_expected_count": expected_per_pair,
        "anchor_level_counts": {
            f"{anchor}|{level}": pair_counts[(anchor, level)]
            for anchor, level in sorted(expected_pairs)
        },
        "scenario_family_counts": dict(sorted(family_counts.items())),
        "private_only": True,
        "semantic_difficulty_claim": "NOT_APPLICABLE_ALLOCATION_ONLY",
    }


def build_expansion_plan(
    source_summary_path: Path,
    output_path: Path,
    *,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    source = json.loads(source_summary_path.read_text(encoding="utf-8"))
    match_ids = [str(value) for value in source.get("match_ids", [])]
    if len(match_ids) != EXPECTED_MATCHES or len(set(match_ids)) != EXPECTED_MATCHES:
        raise ValueError("source summary must contain exactly 220 unique match_ids")
    anchors = sorted(set(ANCHOR_BY_SCENARIO_FAMILY.values()))
    families = _family_index()
    rows: list[dict[str, Any]] = []
    for block_id, start in enumerate(range(0, len(match_ids), len(LEVELS))):
        block_matches = match_ids[start : start + len(LEVELS)]
        block_rng = random.Random(f"{seed}:{block_id}:{ALGORITHM}")
        anchor_order = list(anchors)
        shifts = list(range(len(LEVELS)))
        block_rng.shuffle(anchor_order)
        block_rng.shuffle(shifts)
        for row_index, match_id in enumerate(block_matches):
            shift = shifts[row_index]
            for level_index, level in enumerate(LEVELS):
                anchor = anchor_order[(level_index + shift) % len(anchors)]
                rows.append(
                    {
                        "match_id": match_id,
                        "level": level,
                        "cross_level_anchor_family": anchor,
                        "scenario_family": families[(anchor, level)],
                        "block_id": block_id,
                    }
                )
    plan: dict[str, Any] = {
        "dataset_version": CANDIDATE_VERSION,
        "difficulty_design_revision": DIFFICULTY_DESIGN_REVISION,
        "algorithm": ALGORITHM,
        "seed": seed,
        "source_release_summary": str(source_summary_path),
        "source_release_summary_sha256": _sha256(source_summary_path),
        "match_ids": match_ids,
        "assignments": rows,
        "privacy": "PRIVATE_DESIGN_LEDGER_DO_NOT_EXPOSE_TO_MODEL",
        "claim_boundary": (
            "This plan balances scenario allocation only. It does not prove text "
            "difficulty, answer validity, or empirical model separation."
        ),
    }
    audit = audit_expansion_plan(plan)
    if audit["status"] != "PASS":
        raise ValueError(f"expansion plan audit failed: {audit['errors'][:20]}")
    plan["audit"] = audit
    _write_json(output_path, plan)
    return audit


def audit_expansion_input_coverage(
    expansion_plan_path: Path,
    semantic_base_release: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Fail closed unless every planned match has a complete semantic base bundle."""
    plan = json.loads(expansion_plan_path.read_text(encoding="utf-8"))
    required = list(map(str, plan.get("match_ids", [])))
    base_summary_path = semantic_base_release / "RELEASE_SUMMARY.json"
    if not base_summary_path.is_file():
        raise FileNotFoundError(f"missing semantic base summary: {base_summary_path}")
    base_summary = json.loads(base_summary_path.read_text(encoding="utf-8"))
    declared = set(map(str, base_summary.get("match_ids", [])))
    complete: list[str] = []
    incomplete: dict[str, list[str]] = {}
    for match_id in required:
        expected = (
            Path("public") / match_id / "public_instance.json",
            Path("private") / match_id / "private_gold.json",
            Path("private") / match_id / "private_evidence.json",
        )
        missing = [
            relative.as_posix()
            for relative in expected
            if not (semantic_base_release / relative).is_file()
        ]
        if match_id not in declared:
            missing.insert(0, "RELEASE_SUMMARY.match_ids")
        if missing:
            incomplete[match_id] = missing
        else:
            complete.append(match_id)
    extra = sorted(declared - set(required))
    report = {
        "protocol_version": "VETT-R26-EXPANSION-INPUT-COVERAGE-1",
        "status": "READY" if not incomplete and len(required) == EXPECTED_MATCHES else "BLOCKED",
        "semantic_base_release": str(semantic_base_release),
        "semantic_base_dataset_version": base_summary.get("dataset_version"),
        "required_matches": len(required),
        "complete_matches": len(complete),
        "incomplete_matches": len(incomplete),
        "complete_match_ids": complete,
        "incomplete": incomplete,
        "extra_declared_matches": extra,
        "partial_generation_permitted": False,
        "block_reason": (
            None
            if not incomplete and len(required) == EXPECTED_MATCHES
            else "Every planned match requires public, private-gold and evidence inputs from the semantic base release."
        ),
    }
    _write_json(output_path, report)
    return report


__all__ = [
    "audit_expansion_input_coverage",
    "audit_expansion_plan",
    "build_expansion_plan",
]
