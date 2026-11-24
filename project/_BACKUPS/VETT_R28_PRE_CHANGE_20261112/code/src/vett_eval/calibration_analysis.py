from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from vett_r25.solver import flatten_record

from .metric_contract import LEVELS


def question_field_accuracy_rows(
    release_dir: Path,
    predictions_path: Path,
    instance_ids: list[str],
) -> list[dict[str, Any]]:
    """Materialize private per-question accuracies for paired calibration only."""
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in predictions_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            submitted[str(row["instance_id"])] = {
                str(item["question_id"]): item
                for item in row.get("decision_predictions", [])
                if isinstance(item, dict) and "question_id" in item
            }
    rows: list[dict[str, Any]] = []
    for match_id in instance_ids:
        gold = json.loads(
            (release_dir / "private" / match_id / "private_gold.json").read_text(
                encoding="utf-8"
            )
        )
        predictions = submitted.get(match_id, {})
        seen_levels: set[str] = set()
        for answer in gold["decision_answers"]:
            level = str(answer["level"])
            if level in seen_levels:
                raise ValueError(f"{match_id} has more than one question at {level}")
            seen_levels.add(level)
            prediction = predictions.get(str(answer["question_id"]))
            if prediction is None:
                raise ValueError(
                    f"missing prediction for {match_id}:{answer['question_id']}"
                )
            try:
                predicted = flatten_record(prediction.get("decision_record", {}))
            except (KeyError, TypeError, ValueError):
                predicted = {}
            expected = answer["decision_record_flat"]
            correct = sum(predicted.get(key) == value for key, value in expected.items())
            rows.append({
                "match_id": match_id,
                "question_id": str(answer["question_id"]),
                "level": level,
                "cross_level_anchor_family": str(
                    answer.get("cross_level_anchor_family", "UNREGISTERED")
                ),
                "correct_fields": correct,
                "total_fields": len(expected),
                "accuracy": correct / len(expected),
            })
        if seen_levels != set(LEVELS):
            raise ValueError(
                f"{match_id} must contribute exactly one question at every level"
            )
    return rows


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot compute a percentile of an empty sequence")
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def match_stratified_paired_bootstrap(
    rows: list[dict[str, Any]],
    *,
    resamples: int,
    seed: int,
) -> dict[str, Any]:
    """Bootstrap match blocks, retaining the five paired level observations."""
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    by_match: dict[str, dict[str, float]] = {}
    for row in rows:
        match_id = str(row["match_id"])
        level = str(row["level"])
        if level in by_match.setdefault(match_id, {}):
            raise ValueError(f"duplicate row for {match_id}:{level}")
        by_match[match_id][level] = float(row["accuracy"])
    if not by_match:
        raise ValueError("bootstrap requires at least one match")
    for match_id, values in by_match.items():
        if set(values) != set(LEVELS):
            raise ValueError(f"incomplete five-level block: {match_id}")
    match_ids = sorted(by_match)
    point_levels = {
        level: sum(by_match[match_id][level] for match_id in match_ids)
        / len(match_ids)
        for level in LEVELS
    }
    pairs = list(zip(LEVELS, LEVELS[1:]))
    point_gaps = {
        f"{left}-{right}": point_levels[left] - point_levels[right]
        for left, right in pairs
    }
    samples: dict[str, list[float]] = {key: [] for key in point_gaps}
    rng = random.Random(seed)
    for _ in range(resamples):
        selected = [rng.choice(match_ids) for _ in match_ids]
        level_means = {
            level: sum(by_match[match_id][level] for match_id in selected)
            / len(selected)
            for level in LEVELS
        }
        for left, right in pairs:
            samples[f"{left}-{right}"].append(
                level_means[left] - level_means[right]
            )
    intervals = {
        key: {
            "point": round(point_gaps[key], 6),
            "lower_95": round(_percentile(values, 0.025), 6),
            "upper_95": round(_percentile(values, 0.975), 6),
        }
        for key, values in samples.items()
    }
    return {
        "method": "match_block_paired_percentile_bootstrap",
        "match_blocks": len(match_ids),
        "levels_per_block": len(LEVELS),
        "resamples": resamples,
        "seed": seed,
        "percentile_method": "linear interpolation at index (n-1)*p",
        "level_point_estimates": {
            key: round(value, 6) for key, value in point_levels.items()
        },
        "adjacent_gap_intervals": intervals,
    }


def build_pilot20_bootstrap(
    release_dir: Path,
    predictions_path: Path,
    instance_ids: list[str],
    metric_contract: dict[str, Any],
) -> dict[str, Any]:
    if len(instance_ids) != 20:
        raise ValueError("pilot20 bootstrap requires exactly 20 matches")
    settings = metric_contract["difficulty_curve"]["pilot20_acceptance"]
    rows = question_field_accuracy_rows(release_dir, predictions_path, instance_ids)
    primary = match_stratified_paired_bootstrap(
        rows,
        resamples=int(settings["bootstrap_resamples"]),
        seed=int(settings["bootstrap_seed"]),
    )
    primary["anchor_standardized_diagnostic"] = (
        anchor_standardized_match_block_bootstrap(
            rows,
            resamples=int(settings["bootstrap_resamples"]),
            seed=int(settings["bootstrap_seed"]) + 131,
        )
    )
    return primary


def anchor_standardized_match_block_bootstrap(
    rows: list[dict[str, Any]],
    *,
    resamples: int,
    seed: int,
) -> dict[str, Any]:
    """Match-block bootstrap standardized to equal anchor-by-level weights.

    Resampled match blocks occasionally omit one of the 25 cells. Those draws are
    rejected and disclosed; accepted draws retain match-level dependence and then
    standardize every level over the same five cricket-law anchors.
    """
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    by_match: dict[str, list[dict[str, Any]]] = {}
    anchors = sorted(
        {
            str(row.get("cross_level_anchor_family", "UNREGISTERED"))
            for row in rows
        }
    )
    if len(anchors) != 5 or "UNREGISTERED" in anchors:
        raise ValueError("anchor-standardized bootstrap requires five registered anchors")
    for row in rows:
        by_match.setdefault(str(row["match_id"]), []).append(row)
    match_ids = sorted(by_match)
    if len(match_ids) != 20:
        raise ValueError("anchor-standardized bootstrap requires exactly 20 matches")
    expected_cells = {(anchor, level) for anchor in anchors for level in LEVELS}

    def standardized(selected: list[str]) -> tuple[dict[str, float], dict[str, dict[str, float]]] | None:
        cells: dict[tuple[str, str], list[float]] = {
            cell: [] for cell in expected_cells
        }
        for match_id in selected:
            for row in by_match[match_id]:
                cells[(
                    str(row["cross_level_anchor_family"]),
                    str(row["level"]),
                )].append(float(row["accuracy"]))
        if any(not values for values in cells.values()):
            return None
        by_anchor = {
            anchor: {
                level: sum(cells[(anchor, level)]) / len(cells[(anchor, level)])
                for level in LEVELS
            }
            for anchor in anchors
        }
        by_level = {
            level: sum(by_anchor[anchor][level] for anchor in anchors) / len(anchors)
            for level in LEVELS
        }
        return by_level, by_anchor

    point = standardized(match_ids)
    if point is None:
        raise ValueError("observed Pilot20 lacks a complete anchor-by-level design")
    point_levels, point_by_anchor = point
    pairs = list(zip(LEVELS, LEVELS[1:]))
    samples = {f"{left}-{right}": [] for left, right in pairs}
    rng = random.Random(seed)
    rejected_draws = 0
    attempts = 0
    maximum_attempts = resamples * 20
    while len(next(iter(samples.values()))) < resamples and attempts < maximum_attempts:
        attempts += 1
        selected = [rng.choice(match_ids) for _ in match_ids]
        result = standardized(selected)
        if result is None:
            rejected_draws += 1
            continue
        level_means, _ = result
        for left, right in pairs:
            samples[f"{left}-{right}"].append(
                level_means[left] - level_means[right]
            )
    if len(next(iter(samples.values()))) != resamples:
        raise RuntimeError("could not obtain requested complete anchor bootstrap draws")
    intervals = {
        key: {
            "point": round(
                point_levels[left] - point_levels[right], 6
            ),
            "lower_95": round(_percentile(values, 0.025), 6),
            "upper_95": round(_percentile(values, 0.975), 6),
        }
        for (left, right), (key, values) in zip(pairs, samples.items())
    }
    direction = {
        f"{left}-{right}": {
            "positive_anchor_count": sum(
                point_by_anchor[anchor][left] > point_by_anchor[anchor][right]
                for anchor in anchors
            ),
            "zero_anchor_count": sum(
                point_by_anchor[anchor][left] == point_by_anchor[anchor][right]
                for anchor in anchors
            ),
            "negative_anchor_count": sum(
                point_by_anchor[anchor][left] < point_by_anchor[anchor][right]
                for anchor in anchors
            ),
        }
        for left, right in pairs
    }
    return {
        "method": "match_block_anchor_standardized_percentile_bootstrap",
        "match_blocks": len(match_ids),
        "anchors": anchors,
        "anchor_level_cells": len(expected_cells),
        "resamples": resamples,
        "seed": seed,
        "attempted_draws": attempts,
        "rejected_incomplete_cell_draws": rejected_draws,
        "level_point_estimates": {
            key: round(value, 6) for key, value in point_levels.items()
        },
        "adjacent_gap_intervals": intervals,
        "within_anchor_direction_counts": direction,
        "claim_boundary": (
            "This is a matched diagnostic standardized over five anchors. The frozen "
            "unadjusted match-block bootstrap remains the primary difficulty gate."
        ),
    }


__all__ = [
    "build_pilot20_bootstrap",
    "anchor_standardized_match_block_bootstrap",
    "match_stratified_paired_bootstrap",
    "question_field_accuracy_rows",
]
