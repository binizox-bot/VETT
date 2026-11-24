from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


NUMERIC_FEATURES = (
    "words",
    "documents",
    "targets",
    "masked_cells",
    "innings_count",
    "table_count",
)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_roots(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _features(roots_path: Path, r20_release: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for root in _load_roots(roots_path):
        match_id = root["root_id"]
        audit = json.loads(
            (r20_release / "audit" / f"{match_id}.audit.json").read_text(
                encoding="utf-8"
            )
        )
        repair = root["r20_repair"]
        result.append(
            {
                "match_id": match_id,
                "independent_root": repair["independent_root"],
                "original_action": repair["original_recommended_action"],
                "original_status": repair["original_curation_status"],
                "words": audit["summary"]["words"],
                "documents": audit["summary"]["documents"],
                "targets": audit["summary"]["targets"],
                "masked_cells": repair["masked_conflict_cells"],
                "innings_count": len(root["innings"]),
                "table_count": len(root["tables"]),
                "failure_types": sorted(repair["masked_by_check"]),
            }
        )
    return result


def _distance(
    left: dict[str, Any],
    right: dict[str, Any],
    ranges: dict[str, tuple[float, float]],
) -> float:
    squared = 0.0
    for feature in NUMERIC_FEATURES:
        minimum, maximum = ranges[feature]
        scale = maximum - minimum or 1.0
        squared += ((left[feature] - right[feature]) / scale) ** 2
    distance = math.sqrt(squared)
    distance += 0.45 * (left["original_action"] != right["original_action"])
    distance += 0.20 * (bool(left["masked_cells"]) != bool(right["masked_cells"]))
    left_failures = set(left["failure_types"])
    right_failures = set(right["failure_types"])
    if left_failures or right_failures:
        union = left_failures | right_failures
        distance += 0.35 * (1 - len(left_failures & right_failures) / len(union))
    return distance


def select_pilot(
    roots_path: Path,
    r20_release: Path,
    output_path: Path,
    *,
    count: int = 20,
) -> dict[str, Any]:
    features = _features(roots_path, r20_release)
    eligible = [item for item in features if item["independent_root"]]
    if count > len(eligible):
        raise ValueError("requested pilot exceeds independent roots")
    by_id = {item["match_id"]: item for item in eligible}
    selected: list[str] = []
    reasons: dict[str, list[str]] = {}

    def add(match_id: str, reason: str) -> None:
        if match_id not in selected:
            selected.append(match_id)
        reasons.setdefault(match_id, []).append(reason)

    for item in eligible:
        if item["innings_count"] != 2:
            add(item["match_id"], f"special_{item['innings_count']}_innings_structure")
    for feature in ("words", "targets", "masked_cells"):
        add(min(eligible, key=lambda item: (item[feature], item["match_id"]))["match_id"], f"minimum_{feature}")
        add(max(eligible, key=lambda item: (item[feature], item["match_id"]))["match_id"], f"maximum_{feature}")
    for action in sorted({item["original_action"] for item in eligible}):
        candidates = [item for item in eligible if item["original_action"] == action]
        candidates.sort(key=lambda item: (_digest(f"R21|{action}|{item['match_id']}"), item["match_id"]))
        add(candidates[0]["match_id"], f"action_coverage:{action}")

    ranges = {
        feature: (
            min(float(item[feature]) for item in eligible),
            max(float(item[feature]) for item in eligible),
        )
        for feature in NUMERIC_FEATURES
    }
    masked_quota = count // 2
    clean_quota = count - masked_quota
    while len(selected) < count:
        remaining = [item for item in eligible if item["match_id"] not in selected]
        masked_selected = sum(by_id[match_id]["masked_cells"] > 0 for match_id in selected)
        clean_selected = len(selected) - masked_selected
        if masked_selected >= masked_quota:
            remaining = [item for item in remaining if item["masked_cells"] == 0]
        elif clean_selected >= clean_quota:
            remaining = [item for item in remaining if item["masked_cells"] > 0]
        candidate = max(
            remaining,
            key=lambda item: (
                min(
                    _distance(item, by_id[selected_id], ranges)
                    for selected_id in selected
                ),
                _digest(f"R21|diversity|{item['match_id']}"),
            ),
        )
        add(candidate["match_id"], "greedy_feature_diversity")

    selected = selected[:count]
    selected_features = [by_id[match_id] for match_id in selected]
    result = {
        "selection_version": "VETT-R21-PILOT-SELECTION-1",
        "count": len(selected),
        "independent_roots_only": True,
        "match_ids": selected,
        "records": [
            {**by_id[match_id], "selection_reasons": reasons[match_id]}
            for match_id in selected
        ],
        "coverage": {
            "original_actions": dict(
                sorted(Counter(item["original_action"] for item in selected_features).items())
            ),
            "innings_counts": dict(
                sorted(Counter(item["innings_count"] for item in selected_features).items())
            ),
            "masked_vs_clean": {
                "masked": sum(item["masked_cells"] > 0 for item in selected_features),
                "clean": sum(item["masked_cells"] == 0 for item in selected_features),
            },
            "failure_types": dict(
                sorted(
                    Counter(
                        failure
                        for item in selected_features
                        for failure in item["failure_types"]
                    ).items()
                )
            ),
            "word_range": [
                min(item["words"] for item in selected_features),
                max(item["words"] for item in selected_features),
            ],
            "target_range": [
                min(item["targets"] for item in selected_features),
                max(item["targets"] for item in selected_features),
            ],
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


__all__ = ["select_pilot"]
