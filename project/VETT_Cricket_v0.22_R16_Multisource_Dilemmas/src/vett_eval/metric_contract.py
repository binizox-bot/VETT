from __future__ import annotations

import json
from pathlib import Path
from typing import Any


LEVELS = ("L1", "L2", "L3", "L4", "L5")
EXPECTED_PRIMARY_METRIC = "decision_field_level_macro_accuracy"
EXPECTED_SECONDARY_METRICS = {
    "factual_full_record_exact",
    "counterfactual_field_level_macro_accuracy",
    "positive_evidence_span_micro_f1",
    "rejected_evidence_span_micro_f1",
    "typed_evidence_edge_micro_f1",
    "evidence_chain_joint_exact",
    "factual_evidence_chain_joint_exact",
    "paired_factual_counterfactual_exact",
    "confidence_brier_score",
}
CALIBRATION_STAGE_INSTANCE_COUNTS = {
    "single_protocol_gate": 1,
    "sentinel5": 5,
    "pilot20": 20,
}


def load_metric_contract(path: Path) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    validate_metric_contract(contract)
    return contract


def validate_metric_contract(contract: dict[str, Any]) -> None:
    """Fail closed if the frozen scientific contract drifts or becomes ambiguous."""
    errors: list[str] = []
    if contract.get("status") != "FROZEN_BEFORE_STRONG_MODEL_CALIBRATION":
        errors.append("contract is not frozen before strong-model calibration")
    primary = contract.get("primary_difficulty_metric", {})
    if primary.get("name") != EXPECTED_PRIMARY_METRIC:
        errors.append(f"primary metric must be {EXPECTED_PRIMARY_METRIC}")
    interval = primary.get("strong_model_target_interval")
    if interval != [0.45, 0.65]:
        errors.append("strong-model target interval must remain [0.45, 0.65]")
    curve = contract.get("difficulty_curve", {})
    if curve.get("level_order") != list(LEVELS):
        errors.append("level order must remain L1 through L5")
    if curve.get("l1_minimum_accuracy") != 0.60:
        errors.append("L1 minimum accuracy must remain 0.60")
    if curve.get("target_adjacent_drop") != 0.08:
        errors.append("adjacent target drop must remain 0.08")
    sentinel = curve.get("sentinel5_screen", {})
    if sentinel.get("minimum_positive_adjacent_drops") != 3:
        errors.append("sentinel5 must require three positive adjacent drops")
    if sentinel.get("minimum_mean_adjacent_drop") != 0.08:
        errors.append("sentinel5 mean drop must remain 0.08")
    pilot = curve.get("pilot20_acceptance", {})
    if pilot.get("all_four_point_estimate_drops_at_least") != 0.08:
        errors.append("pilot20 point-estimate gap must remain 0.08")
    if pilot.get("bootstrap_resamples") != 10000:
        errors.append("pilot20 bootstrap resamples must remain 10000")
    if pilot.get("bootstrap_seed") != 26091:
        errors.append("pilot20 bootstrap seed must remain 26091")
    if pilot.get("bootstrap_unit") != "match block with all five levels retained":
        errors.append("pilot20 bootstrap unit must remain the paired match block")
    if pilot.get("confidence_interval") != "two-sided percentile 95%":
        errors.append("pilot20 confidence interval must remain two-sided percentile 95%")
    if pilot.get("percentile_method") != "linear interpolation at index (n-1)*p":
        errors.append("pilot20 percentile interpolation method drifted")
    if pilot.get("minimum_adjacent_pairs_with_positive_95pct_lower_bound") != 3:
        errors.append("pilot20 must require three positive lower confidence bounds")
    secondary = contract.get("secondary_metrics", [])
    secondary_names = {item.get("name") for item in secondary}
    if secondary_names != EXPECTED_SECONDARY_METRICS:
        errors.append("secondary metric set drifted")
    if any(item.get("gate") is not False for item in secondary):
        errors.append("secondary metrics must remain non-gating")
    rules = contract.get("anti_contamination_rules", {})
    required_false = (
        "diagnostic_scores_may_trigger_dataset_changes",
        "free_4b_scores_may_calibrate_strong_model_difficulty",
        "invalid_protocol_outputs_count_as_factual_errors",
        "metric_thresholds_may_change_after_viewing_gate3_results",
        "single_match_scores_may_establish_level_ordering",
    )
    for key in required_false:
        if rules.get(key) is not False:
            errors.append(f"anti-contamination rule must remain false: {key}")
    if errors:
        raise ValueError("invalid frozen metric contract: " + "; ".join(errors))


def _adjacent_drops(level_values: dict[str, float]) -> dict[str, float]:
    return {
        f"{left}-{right}": round(
            float(level_values[left]) - float(level_values[right]), 6
        )
        for left, right in zip(LEVELS, LEVELS[1:])
    }


def evaluate_calibration_stage(
    contract: dict[str, Any],
    stage: str,
    *,
    protocol_status: str,
    planned_instances: int,
    scored_instances: int,
    batch_status_counts: dict[str, int],
    stopped_early: bool,
    scores: dict[str, Any] | None,
    bootstrap: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate only conclusions authorized by the frozen calibration stage.

    Pilot20 uncertainty is intentionally not inferred from aggregate scores. A
    question-level, match-stratified bootstrap artifact must be supplied by a
    later calibration analysis before that stage can pass.
    """
    validate_metric_contract(contract)
    if stage not in CALIBRATION_STAGE_INSTANCE_COUNTS:
        raise ValueError(f"unsupported calibration stage: {stage}")
    eligibility_failures: list[str] = []
    if protocol_status != "COMPLETE_SEMANTIC_COVERAGE":
        eligibility_failures.append(f"protocol_status:{protocol_status}")
    if planned_instances <= 0 or scored_instances != planned_instances:
        eligibility_failures.append(
            f"semantic_coverage:{scored_instances}/{planned_instances}"
        )
    non_ok = {
        key: int(value)
        for key, value in batch_status_counts.items()
        if key != "OK" and int(value) > 0
    }
    if non_ok:
        eligibility_failures.append(f"non_ok_batches:{non_ok}")
    if stopped_early:
        eligibility_failures.append("run_stopped_early")
    eligible = not eligibility_failures
    result: dict[str, Any] = {
        "contract_version": contract["contract_version"],
        "stage": stage,
        "officially_eligible": eligible,
        "eligibility_failures": eligibility_failures,
        "primary_metric": EXPECTED_PRIMARY_METRIC,
    }
    if not eligible:
        return {
            **result,
            "status": "INELIGIBLE_PROTOCOL",
            "difficulty_conclusion_permitted": False,
        }
    expected_instances = CALIBRATION_STAGE_INSTANCE_COUNTS[stage]
    if planned_instances != expected_instances:
        return {
            **result,
            "status": "INVALID_STAGE_SIZE",
            "difficulty_conclusion_permitted": False,
            "expected_instances": expected_instances,
            "actual_instances": planned_instances,
        }
    if stage == "single_protocol_gate":
        return {
            **result,
            "status": "PASS",
            "difficulty_conclusion_permitted": False,
            "decision": "Protocol gate passed; no difficulty claim is authorized.",
        }
    if scores is None:
        return {
            **result,
            "status": "MISSING_SCORES",
            "difficulty_conclusion_permitted": False,
        }
    level_values = {
        level: float(scores["decision_field_accuracy_by_level"][level])
        for level in LEVELS
    }
    primary_value = round(sum(level_values.values()) / len(LEVELS), 6)
    reported_value = round(float(scores["decision_field_macro_accuracy"]), 6)
    if primary_value != reported_value:
        return {
            **result,
            "status": "PRIMARY_METRIC_INCONSISTENT",
            "difficulty_conclusion_permitted": False,
            "computed_primary_value": primary_value,
            "reported_primary_value": reported_value,
        }
    drops = _adjacent_drops(level_values)
    positive_count = sum(value > 0 for value in drops.values())
    mean_drop = round(sum(drops.values()) / len(drops), 6)
    low, high = contract["primary_difficulty_metric"][
        "strong_model_target_interval"
    ]
    base = {
        **result,
        "primary_value": primary_value,
        "primary_target_interval": [low, high],
        "level_values": level_values,
        "adjacent_drops": drops,
        "positive_adjacent_drops": positive_count,
        "mean_adjacent_drop": mean_drop,
        "l1_floor_pass": level_values["L1"]
        >= float(contract["difficulty_curve"]["l1_minimum_accuracy"]),
    }
    if stage == "sentinel5":
        screen = contract["difficulty_curve"]["sentinel5_screen"]
        checks = {
            "primary_in_target_interval": low <= primary_value <= high,
            "l1_floor": base["l1_floor_pass"],
            "positive_drop_count": positive_count
            >= int(screen["minimum_positive_adjacent_drops"]),
            "mean_adjacent_drop": mean_drop
            >= float(screen["minimum_mean_adjacent_drop"]),
        }
        return {
            **base,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "difficulty_conclusion_permitted": True,
            "screen_only": True,
            "checks": checks,
        }
    if stage == "pilot20":
        acceptance = contract["difficulty_curve"]["pilot20_acceptance"]
        point_target = float(
            acceptance[
                "all_four_point_estimate_drops_at_least"
            ]
        )
        if bootstrap is None:
            return {
                **base,
                "status": "PENDING_MATCH_STRATIFIED_BOOTSTRAP",
                "difficulty_conclusion_permitted": False,
                "point_estimate_check": all(
                    value >= point_target for value in drops.values()
                ),
                "required_bootstrap_resamples": 10000,
                "required_bootstrap_seed": 26091,
            }
        expected_bootstrap = {
            "method": "match_block_paired_percentile_bootstrap",
            "match_blocks": 20,
            "levels_per_block": 5,
            "resamples": int(acceptance["bootstrap_resamples"]),
            "seed": int(acceptance["bootstrap_seed"]),
            "percentile_method": acceptance["percentile_method"],
        }
        bootstrap_valid = all(
            bootstrap.get(key) == value for key, value in expected_bootstrap.items()
        )
        intervals = bootstrap.get("adjacent_gap_intervals", {})
        expected_pairs = set(drops)
        interval_complete = set(intervals) == expected_pairs
        positive_lower_bounds = (
            sum(float(intervals[key]["lower_95"]) > 0 for key in expected_pairs)
            if interval_complete else 0
        )
        checks = {
            "primary_in_target_interval": low <= primary_value <= high,
            "l1_floor": base["l1_floor_pass"],
            "all_point_estimate_drops": all(
                value >= point_target for value in drops.values()
            ),
            "bootstrap_protocol": bootstrap_valid and interval_complete,
            "positive_95pct_lower_bounds": positive_lower_bounds
            >= int(acceptance[
                "minimum_adjacent_pairs_with_positive_95pct_lower_bound"
            ]),
        }
        return {
            **base,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "difficulty_conclusion_permitted": True,
            "checks": checks,
            "positive_95pct_lower_bounds": positive_lower_bounds,
            "bootstrap": bootstrap,
        }
    raise AssertionError(f"unreachable calibration stage: {stage}")


__all__ = [
    "EXPECTED_PRIMARY_METRIC",
    "CALIBRATION_STAGE_INSTANCE_COUNTS",
    "LEVELS",
    "evaluate_calibration_stage",
    "load_metric_contract",
    "validate_metric_contract",
]
