from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def validate_adjustment_authority(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    contract = json.loads(raw.decode("utf-8"))
    errors: list[str] = []
    stages = contract.get("stage_authority", {})
    expected = {
        "static_only",
        "sentinel5",
        "pilot20_one_strong_family",
        "pilot20_two_strong_families",
    }
    if set(stages) != expected:
        errors.append(f"stage_coverage:{sorted(stages)}")
    if stages.get("static_only", {}).get("may_change_content_difficulty") is not False:
        errors.append("static_may_not_change_content")
    if stages.get("sentinel5", {}).get("may_change_content_difficulty") is not False:
        errors.append("sentinel_may_not_change_content")
    one_family = stages.get("pilot20_one_strong_family", {})
    if one_family.get("may_build_shadow_candidate") is not True:
        errors.append("one_family_shadow_build")
    if one_family.get("may_promote_shadow_candidate") is not False:
        errors.append("one_family_no_promotion")
    if int(one_family.get("minimum_anchors_reproducing_weak_transition", 0)) < 2:
        errors.append("one_family_anchor_replication")
    if int(one_family.get("minimum_questions_with_same_registered_error_mechanism", 0)) < 4:
        errors.append("one_family_error_replication")
    two_family = stages.get("pilot20_two_strong_families", {})
    required_true = (
        "may_promote_shadow_candidate",
        "requires_same_trigger_direction_in_both_families",
        "requires_no_l1_or_global_floor_effect",
        "requires_fresh_shadow_sentinel",
    )
    for key in required_true:
        if two_family.get(key) is not True:
            errors.append(f"two_family_required:{key}")
    triggers = contract.get("trigger_rules", {})
    if triggers.get("too_easy", {}).get("primary_field_macro_above") != 0.65:
        errors.append("too_easy_threshold")
    if triggers.get("weak_adjacent_transition", {}).get("adjacent_drop_below") != 0.08:
        errors.append("adjacent_threshold")
    floor = triggers.get("floor_effect", {})
    if floor.get("primary_field_macro_below") != 0.35 or floor.get("or_l1_below") != 0.60:
        errors.append("floor_thresholds")
    forbidden = set(map(str, contract.get("forbidden_triggers", [])))
    for required in (
        "structural load index alone",
        "one match or one anchor",
        "Oracle accuracy",
        "invalid, truncated or repaired provider output",
    ):
        if required not in forbidden:
            errors.append(f"missing_forbidden_trigger:{required}")
    budget = contract.get("shadow_candidate_budget", {})
    if budget.get("full_pilot20_rerun_before_shadow_sentinel") is not False:
        errors.append("economic_shadow_sequence")
    if budget.get("length_only_change_permitted") is not False:
        errors.append("length_only_forbidden")
    if int(budget.get("maximum_new_decisive_spans_per_question", 99)) > 2:
        errors.append("decisive_span_budget")
    parent = path.parent / str(contract.get("parent_registry", ""))
    if not parent.is_file():
        errors.append("parent_registry_missing")
        parent_sha256 = None
    else:
        parent_sha256 = hashlib.sha256(parent.read_bytes()).hexdigest()
    return {
        "protocol_version": "VETT-R26.13-ADJUSTMENT-AUTHORITY-AUDIT-1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "contract_version": contract.get("contract_version"),
        "contract_sha256": hashlib.sha256(raw).hexdigest(),
        "parent_registry_sha256": parent_sha256,
        "sentinel_content_mutation_permitted": stages.get("sentinel5", {}).get(
            "may_change_content_difficulty"
        ),
        "one_family_promotion_permitted": one_family.get(
            "may_promote_shadow_candidate"
        ),
        "two_family_promotion_requires_fresh_shadow_sentinel": two_family.get(
            "requires_fresh_shadow_sentinel"
        ),
        "provider_requests_made": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-adjustment-authority")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_adjustment_authority(args.contract)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["validate_adjustment_authority"]
