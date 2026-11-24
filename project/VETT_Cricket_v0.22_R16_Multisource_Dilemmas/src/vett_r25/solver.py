from __future__ import annotations

import copy
from typing import Any


LEDGER_ORDER = ("BATTER", "NO_BALL_EXTRA", "WIDE_EXTRA", "BYE", "LEG_BYE", "PENALTY")


def _dismissal(f: dict[str, Any], status: str) -> str:
    candidate = f.get("dismissal_candidate", "NONE")
    if (
        candidate == "NONE"
        or not f.get("appeal_made", f.get("appeal", True))
        or not f.get("appeal_in_time", True)
    ):
        return "NONE"
    if f.get("early_dead_reball") or f.get("dead_before_wicket") or f.get("wilful_deception"):
        return "NONE"
    if not f.get("wicket_fair", True):
        return "NONE"
    if candidate in {"BOWLED", "LBW", "CAUGHT"}:
        if status != "LEGAL":
            return "NONE"
        if candidate == "BOWLED" and not f.get("wicket_broken_by_delivery", True):
            return "NONE"
        if candidate == "LBW" and not all(
            (
                f.get("lbw_pitch_valid", False),
                f.get("lbw_impact_valid", False),
                f.get("lbw_would_hit_wicket", False),
            )
        ):
            return "NONE"
        if candidate == "CAUGHT":
            if (
                f.get("contact") != "BAT"
                or not f.get("catch_complete", True)
                or f.get("ball_grounded_before_control", False)
                or f.get("boundary_contact_before_completion")
            ):
                return "NONE"
        return candidate
    if candidate == "RUN_OUT":
        if not f.get("out_of_ground", True):
            return "NONE"
        if status == "NO_BALL" and f.get("keeper_only") and not f.get("attempting_run"):
            return "NONE"
        return "RUN_OUT"
    if candidate == "STUMPED_OR_RUN_OUT":
        if not f.get("out_of_ground", True):
            return "NONE"
        if status == "NO_BALL":
            if f.get("keeper_only") and not f.get("attempting_run"):
                return "NONE"
            return "RUN_OUT"
        if f.get("keeper_only") and not f.get("attempting_run"):
            return "STUMPED"
        return "RUN_OUT"
    if candidate in {"OBSTRUCTING_FIELD", "HIT_BALL_TWICE"}:
        return candidate
    raise ValueError(f"unsupported dismissal candidate: {candidate}")


def solve(facts: dict[str, Any]) -> dict[str, Any]:
    f = copy.deepcopy(facts)
    contact = f.get("contact", "NONE")
    if f.get("early_dead_reball"):
        status = "DEAD_REBALL"
    elif f.get("no_ball_called"):
        status = "NO_BALL"
    elif f.get("wide_called") and contact == "NONE":
        status = "WIDE"
    else:
        status = "LEGAL"

    dismissal = _dismissal(f, status)
    ledger = {key: 0 for key in LEDGER_ORDER}
    if status == "NO_BALL":
        ledger["NO_BALL_EXTRA"] = 1
    elif status == "WIDE":
        ledger["WIDE_EXTRA"] = 1

    boundary = int(f.get("boundary_allowance", 0))
    boundary_mode = f.get("boundary_mode", "NONE")
    completed = int(f.get("completed_runs", 0))
    movement = completed
    if boundary_mode == "OVERTHROW":
        movement += boundary + (1 if f.get("crossed_at_throw") else 0)
    elif boundary_mode == "NORMAL" and boundary:
        movement = boundary
    elif boundary_mode == "LATER_AFTER_WICKET":
        movement = completed if dismissal != "NONE" else max(boundary, completed)
    if f.get("award_run_in_progress") or f.get("wilful_deception"):
        movement += 1

    if status != "DEAD_REBALL" and movement:
        if contact == "BAT":
            ledger["BATTER"] += movement
        elif status == "WIDE":
            ledger["WIDE_EXTRA"] += movement
        elif contact == "PERSON":
            ledger["LEG_BYE"] += movement
        else:
            ledger["BYE"] += movement

    ledger["PENALTY"] += int(f.get("penalty_runs_batting", 0))
    if f.get("wilful_deception"):
        ledger["PENALTY"] += 5

    # Completed dismissals other than Run out cannot coexist with ordinary running
    # in the supported pilot templates. Keep only automatic and penalty awards.
    if dismissal in {"BOWLED", "LBW", "CAUGHT", "STUMPED"}:
        for key in ("BATTER", "BYE", "LEG_BYE"):
            ledger[key] = 0
        if status == "WIDE":
            ledger["WIDE_EXTRA"] = 1

    if status == "DEAD_REBALL":
        ledger = {key: 0 for key in LEDGER_ORDER}

    total = sum(ledger.values())
    bowler = ledger["BATTER"] + ledger["NO_BALL_EXTRA"] + ledger["WIDE_EXTRA"]
    record = {
        "delivery_status": status,
        "counts_in_over": (
            status == "LEGAL"
            and not f.get("forced_not_count", False)
            and not f.get("wilful_deception", False)
        ),
        "dismissal": dismissal,
        "total_runs": total,
        "batter_runs": ledger["BATTER"],
        "bowler_runs": bowler,
        "run_ledger": [
            {"account": account, "runs": value}
            for account, value in ledger.items()
            if value
        ] or [{"account": "NONE", "runs": 0}],
    }
    validate_record(record)
    return record


def intervene(facts: dict[str, Any], field: str, value: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if field not in facts:
        raise KeyError(field)
    changed = copy.deepcopy(facts)
    if changed[field] == value:
        raise ValueError("counterfactual intervention must change one value")
    changed[field] = value
    return changed, solve(changed)


def validate_record(record: dict[str, Any]) -> None:
    ledger_total = sum(int(row["runs"]) for row in record["run_ledger"])
    if ledger_total != record["total_runs"]:
        raise ValueError("run ledger does not conserve total runs")
    ledger = {row["account"]: row["runs"] for row in record["run_ledger"]}
    if ledger.get("BATTER", 0) != record["batter_runs"]:
        raise ValueError("batter runs disagree with ledger")
    expected_bowler = (
        ledger.get("BATTER", 0)
        + ledger.get("NO_BALL_EXTRA", 0)
        + ledger.get("WIDE_EXTRA", 0)
    )
    if expected_bowler != record["bowler_runs"]:
        raise ValueError("bowler runs disagree with ledger")
    if record["delivery_status"] in {"NO_BALL", "WIDE", "DEAD_REBALL"} and record["counts_in_over"]:
        raise ValueError("invalid delivery cannot count in over")


def flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    flat = {key: value for key, value in record.items() if key != "run_ledger"}
    ledger = {row["account"]: row["runs"] for row in record["run_ledger"]}
    for account in LEDGER_ORDER:
        flat[f"ledger.{account}"] = ledger.get(account, 0)
    return flat


def trace_state(facts: dict[str, Any], record: dict[str, Any], active_source: str) -> dict[str, Any]:
    movement = int(facts.get("completed_runs", 0))
    if facts.get("crossed_at_throw") or facts.get("award_run_in_progress") or facts.get("wilful_deception"):
        movement += 1
    no_ball = bool(facts.get("no_ball_called", False))
    wide = bool(facts.get("wide_called", False))
    initial_call_set = (
        "NO_BALL_AND_WIDE" if no_ball and wide
        else "NO_BALL_ONLY" if no_ball
        else "WIDE_ONLY" if wide
        else "NONE"
    )
    return {
        "active_source": active_source,
        "initial_call_set": initial_call_set,
        "observed_contact": str(facts.get("contact", "NONE")),
        "effective_delivery_status": record["delivery_status"],
        "movement_runs_before_boundary_allowance": movement,
        "boundary_allowance": int(facts.get("boundary_allowance", 0)),
        "pre_wicket_ball_state": (
            "NOT_APPLICABLE"
            if facts.get("dismissal_candidate", "NONE") == "NONE"
            else "DEAD" if facts.get("early_dead_reball") or facts.get("dead_before_wicket") or facts.get("wilful_deception") else "LIVE"
        ),
    }


__all__ = ["LEDGER_ORDER", "flatten_record", "intervene", "solve", "trace_state", "validate_record"]
