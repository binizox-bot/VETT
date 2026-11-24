from __future__ import annotations

from typing import Iterable


# These are diagnostic weights learned from rule structure, not an item-level score.
# Empirical calibration remains authoritative.
OPERATOR_COST = {
    "LEGAL_COUNT": 1,
    "NB_COUNT": 1,
    "WIDE_COUNT": 1,
    "BAT_CREDIT": 1,
    "BOWLER_DEBIT": 2,
    "NB_SCORE": 2,
    "WIDE_SCORE": 2,
    "BOUNDARY_NORMAL": 2,
    "APPEAL": 2,
    "BOWLED_TEST": 2,
    "LBW_TEST": 3,
    "RUNOUT_TEST": 3,
    "CAUGHT_CONTROL": 3,
    "STUMPED_TEST": 4,
    "WIDE_CONTACT": 4,
    "NB_DISMISSAL_GATE": 4,
    "WIDE_DISMISSAL_GATE": 4,
    "NB_KEEPER_RUNOUT_EXCEPTION": 5,
    "DEAD_SEQUENCE": 5,
    "NB_PRECEDENCE": 5,
    "OVERTHROW": 6,
    "DECEPTION": 6,
    "SOURCE_ORDER": 5,
}


def operator_profile(rule_keys: Iterable[str]) -> dict[str, object]:
    signature = tuple(sorted(set(map(str, rule_keys))))
    costs = tuple(OPERATOR_COST.get(key, 3) for key in signature)
    return {
        "rule_signature": list(signature),
        "operator_count": len(signature),
        "operator_cost_sum": sum(costs),
        "operator_cost_max": max(costs, default=0),
        "operator_interaction_count": max(0, len(signature) - 1),
    }


__all__ = ["OPERATOR_COST", "operator_profile"]
