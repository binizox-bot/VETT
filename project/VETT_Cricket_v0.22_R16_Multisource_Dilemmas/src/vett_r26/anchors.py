from __future__ import annotations

from collections import defaultdict

from vett_r25.scenarios import SCENARIOS


# These are capability anchors, not answer templates.  Each anchor keeps one
# primary cricket-decision dependency visible at every level while the identity,
# authority, temporal, evidence and counterfactual burdens change.
ANCHOR_BY_SCENARIO_FAMILY = {
    # Delivery-call precedence and extras accounting.
    "L1_NB_DOT": "CALL_PRECEDENCE_AND_EXTRAS",
    "L2_NB_OVER_WIDE": "CALL_PRECEDENCE_AND_EXTRAS",
    "L3_NB_LBW": "CALL_PRECEDENCE_AND_EXTRAS",
    "L4_REVIEW_NB_OVER_WIDE": "CALL_PRECEDENCE_AND_EXTRAS",
    "L5_NB_WIDE_CONTACT_OVERTHROW": "CALL_PRECEDENCE_AND_EXTRAS",
    # Wicket eligibility under an invalid delivery.
    "L1_WIDE_DOT": "INVALID_DELIVERY_WICKET_GATE",
    "L2_WIDE_STUMP": "INVALID_DELIVERY_WICKET_GATE",
    "L3_NB_KEEPER_EXCEPTION": "INVALID_DELIVERY_WICKET_GATE",
    "L4_REVIEW_WIDE_STUMP": "INVALID_DELIVERY_WICKET_GATE",
    "L5_WIDE_STUMP_REVIEW": "INVALID_DELIVERY_WICKET_GATE",
    # Boundary and run-ledger attribution.
    "L1_LEGAL_FOUR": "BOUNDARY_AND_LEDGER_ATTRIBUTION",
    "L2_NB_BAT_FOUR": "BOUNDARY_AND_LEDGER_ATTRIBUTION",
    "L3_OVERTHROW_CROSS": "BOUNDARY_AND_LEDGER_ATTRIBUTION",
    "L4_REVIEW_OVERTHROW": "BOUNDARY_AND_LEDGER_ATTRIBUTION",
    "L5_NB_OVERTHROW": "BOUNDARY_AND_LEDGER_ATTRIBUTION",
    # Event ordering determines which later event remains effective.
    "L1_EARLY_DEAD": "EVENT_ORDER_AND_TERMINAL_STATE",
    "L2_WIDE_BOUNDARY": "EVENT_ORDER_AND_TERMINAL_STATE",
    "L3_DEAD_BEFORE_RUNOUT": "EVENT_ORDER_AND_TERMINAL_STATE",
    "L4_REVIEW_DEAD_SEQUENCE": "EVENT_ORDER_AND_TERMINAL_STATE",
    "L5_RUNOUT_LATER_BOUNDARY": "EVENT_ORDER_AND_TERMINAL_STATE",
    # Appeal/dismissal requirements and controlling observations.
    "L1_LEGAL_BOWLED": "DISMISSAL_AND_APPEAL_CONTROL",
    "L2_NB_BOWLED": "DISMISSAL_AND_APPEAL_CONTROL",
    "L3_CATCH_BOUNDARY": "DISMISSAL_AND_APPEAL_CONTROL",
    "L4_REVIEW_CATCH_CONTROL": "DISMISSAL_AND_APPEAL_CONTROL",
    "L5_NB_DECEPTION": "DISMISSAL_AND_APPEAL_CONTROL",
}


def validate_anchor_design() -> dict[str, object]:
    scenario_levels = {scenario.family_id: scenario.level for scenario in SCENARIOS}
    errors: list[str] = []
    if set(ANCHOR_BY_SCENARIO_FAMILY) != set(scenario_levels):
        missing = sorted(set(scenario_levels) - set(ANCHOR_BY_SCENARIO_FAMILY))
        extra = sorted(set(ANCHOR_BY_SCENARIO_FAMILY) - set(scenario_levels))
        errors.append(f"scenario_coverage:missing={missing}:extra={extra}")
    covered: dict[str, set[str]] = defaultdict(set)
    for family, anchor in ANCHOR_BY_SCENARIO_FAMILY.items():
        if family in scenario_levels:
            covered[anchor].add(scenario_levels[family])
    expected_levels = {"L1", "L2", "L3", "L4", "L5"}
    for anchor, levels in sorted(covered.items()):
        if levels != expected_levels:
            errors.append(f"anchor_levels:{anchor}:{sorted(levels)}")
    if len(covered) != 5:
        errors.append(f"anchor_count:{len(covered)}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "anchor_families": len(covered),
        "levels_by_anchor": {
            anchor: sorted(levels) for anchor, levels in sorted(covered.items())
        },
    }


_VALIDATION = validate_anchor_design()
if _VALIDATION["status"] != "PASS":
    raise RuntimeError(f"invalid R26 anchor design: {_VALIDATION['errors']}")


__all__ = ["ANCHOR_BY_SCENARIO_FAMILY", "validate_anchor_design"]
