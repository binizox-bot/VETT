from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


LEVELS = ("L1", "L2", "L3", "L4", "L5")


def validate_blueprint(path: Path) -> dict[str, Any]:
    design = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    scenarios = [
        scenario
        for cluster in design.get("scenario_clusters", [])
        for scenario in cluster.get("scenarios", [])
    ]
    ids = [scenario.get("id") for scenario in scenarios]
    level_counts = Counter(scenario.get("level") for scenario in scenarios)
    if design.get("status") not in {
        "DESIGN_ONLY_NOT_GENERATED",
        "IMPLEMENTED_FULL_220_STATIC_PASS_EMPIRICAL_CALIBRATION_PENDING",
    }:
        errors.append("unknown R24 lifecycle status")
    if design.get("status", "").startswith("IMPLEMENTED"):
        implementation = design.get("implementation", {})
        if implementation.get("instances") != 220 or implementation.get("static_audit") != "PASS":
            errors.append("implemented R24 status requires a 220-instance static PASS")
        if implementation.get("empirical_strong_model_calibration") != "PENDING":
            errors.append("R24 must not claim empirical calibration without model-panel evidence")
    if len(design.get("scenario_clusters", [])) != 12:
        errors.append("exactly 12 scenario clusters are required")
    if len(scenarios) != 60:
        errors.append("exactly 60 independent scenarios are required")
    if len(ids) != len(set(ids)):
        errors.append("scenario IDs must be unique")
    if level_counts != Counter({level: 12 for level in LEVELS}):
        errors.append(f"levels must contain 12 scenarios each: {dict(level_counts)}")
    for scenario in scenarios:
        if not scenario.get("laws"):
            errors.append(f"scenario has no law source: {scenario.get('id')}")
        if not scenario.get("answer_type") or not scenario.get("mechanism"):
            errors.append(f"scenario lacks scoring contract: {scenario.get('id')}")
    levels = {item.get("level"): item for item in design.get("difficulty_levels", [])}
    previous_high = None
    previous_midpoint = None
    band_midpoints: list[float] = []
    for level in LEVELS:
        item = levels.get(level)
        if item is None:
            errors.append(f"missing level contract: {level}")
            continue
        low, high = item["target_fact_accuracy_band"]
        if not 0 <= low <= high <= 1:
            errors.append(f"invalid accuracy band: {level}")
        if previous_high is not None and high >= previous_high:
            errors.append("difficulty accuracy bands must strictly decrease")
        midpoint = (low + high) / 2
        if previous_midpoint is not None and previous_midpoint - midpoint < 0.08:
            errors.append(f"adjacent target-band midpoint gap is below eight points: {level}")
        band_midpoints.append(midpoint)
        previous_high = high
        previous_midpoint = midpoint
    gate = design.get("acceptance_gates", {})
    if gate.get("strong_model_fact_macro_max", 1) > 0.65:
        errors.append("strong-model target is weaker than 65%")
    if gate.get("adjacent_level_fact_gap_min", 0) < 0.08:
        errors.append("adjacent-level gap target is below eight points")
    if band_midpoints and sum(band_midpoints) / len(band_midpoints) > gate.get("strong_model_fact_macro_max", 0):
        errors.append("target-band macro exceeds the strong-model release ceiling")
    mutation = design.get("mutation_budget_per_match", {})
    if mutation.get("touch_base_spans_percent_max", 100) > 1.2:
        errors.append("text mutation budget exceeds 1.2%")
    if not all(
        mutation.get(key) is True
        for key in (
            "must_be_reversible",
            "r22_table_gold_must_be_unchanged",
            "r22_probe_gold_must_be_unchanged",
        )
    ):
        errors.append("R22 no-regression and reversibility are mandatory")
    split = design.get("split_policy", {})
    if sum(split.get(key, 0) for key in ("development", "calibration", "held_out_test")) != 60:
        errors.append("scenario-family split must cover all 60 scenarios")
    if not split.get("same_family_cross_split_forbidden"):
        errors.append("scenario leakage across splits must be forbidden")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "scenario_count": len(scenarios),
        "cluster_count": len(design.get("scenario_clusters", [])),
        "level_counts": dict(sorted(level_counts.items())),
        "metric_count": len(design.get("primary_metrics", [])),
    }


__all__ = ["validate_blueprint"]
