from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TRANSITIONS = {
    "L1-L2": "L2",
    "L2-L3": "L3",
    "L3-L4": "L4",
    "L4-L5": "L5",
}
LOAD_AXES = {
    "binding_load",
    "authority_conflict_load",
    "rule_reasoning_load",
    "temporal_load",
    "evidence_load",
    "counterfactual_load",
}


def validate_adjustment_registry(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    registry = json.loads(raw.decode("utf-8"))
    errors: list[str] = []
    metric_reference = str(registry.get("metric_contract", ""))
    metric_path = path.resolve().parent / metric_reference
    metric_sha256: str | None = None
    if not metric_path.is_file():
        errors.append(f"metric_contract_missing:{metric_reference}")
    else:
        metric_raw = metric_path.read_bytes()
        metric_sha256 = hashlib.sha256(metric_raw).hexdigest()
        metric = json.loads(metric_raw.decode("utf-8"))
        if metric.get("contract_version") != "VETT-R26-METRICS-1.0-FROZEN":
            errors.append("metric_contract_version")
        if metric.get("difficulty_curve", {}).get("target_adjacent_drop") != 0.08:
            errors.append("metric_adjacent_drop")
        if metric.get("primary_difficulty_metric", {}).get(
            "strong_model_target_interval"
        ) != [0.45, 0.65]:
            errors.append("metric_target_interval")
        if metric.get("anti_contamination_rules", {}).get(
            "single_match_scores_may_establish_level_ordering"
        ) is not False:
            errors.append("metric_single_match_rule")
    actions = registry.get("transition_actions", {})
    if set(actions) != set(TRANSITIONS):
        errors.append(f"transition_coverage:{sorted(actions)}")
    mechanism_ids: list[str] = []
    for transition, upper_level in TRANSITIONS.items():
        action = actions.get(transition, {})
        if action.get("upper_level") != upper_level:
            errors.append(f"upper_level:{transition}:{action.get('upper_level')}")
        axes = set(map(str, action.get("affected_axes", [])))
        if len(axes) < 2 or not axes <= LOAD_AXES:
            errors.append(f"affected_axes:{transition}:{sorted(axes)}")
        mechanism_id = str(action.get("mechanism_id", ""))
        if not mechanism_id:
            errors.append(f"mechanism_id:{transition}")
        mechanism_ids.append(mechanism_id)
        if not str(action.get("required_proof_effect", "")).strip():
            errors.append(f"required_proof_effect:{transition}")
        if not str(action.get("activation", "")).strip():
            errors.append(f"activation:{transition}")
        added = action.get("max_added_decisive_spans_per_question")
        if not isinstance(added, int) or not 0 <= added <= 2:
            errors.append(f"mutation_budget:{transition}:{added}")
    if len(mechanism_ids) != len(set(mechanism_ids)):
        errors.append("duplicate_mechanism_id")
    constraints = registry.get("mutation_constraints", {})
    required_true = {
        "preserve_r22_and_r25_semantics",
        "single_atomic_counterfactual",
    }
    required_false = {
        "length_only_difficulty_permitted",
        "irrelevant_noise_only_permitted",
        "answer_style_cues_permitted",
        "single_match_activation_permitted",
    }
    for key in sorted(required_true):
        if constraints.get(key) is not True:
            errors.append(f"constraint_must_be_true:{key}")
    for key in sorted(required_false):
        if constraints.get(key) is not False:
            errors.append(f"constraint_must_be_false:{key}")
    if int(constraints.get("minimum_affected_axes", 0)) < 2:
        errors.append("minimum_affected_axes")
    eligible = set(map(str, registry.get("eligible_evidence_stages", [])))
    if eligible != {"sentinel5", "pilot20"}:
        errors.append(f"eligible_evidence_stages:{sorted(eligible)}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "registry_version": registry.get("registry_version"),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "metric_contract_sha256": metric_sha256,
        "transition_actions": len(actions),
        "mechanism_ids": mechanism_ids,
        "single_match_activation_permitted": constraints.get(
            "single_match_activation_permitted"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-adjustment-registry")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate_adjustment_registry(args.registry)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["validate_adjustment_registry"]
