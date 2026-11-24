"""R28 derivation pipeline: solver-equivalent staged resolution with mechanical ablation.

Why this module exists
----------------------
t3 found that R26's ``rule_operators`` moves 1 -> 2 -> 3 -> 4 while the gold record
stays byte-identical, i.e. the field may only count how many rule texts were
printed.  The contract therefore requires the derivation depth to be *proved with
the solver*: every claimed extra operator must be shown necessary by replaying the
derivation without it and observing that the gold record can no longer be obtained.

This module provides exactly that.  ``run_pipeline`` is a staged re-implementation
of ``vett_r25.solver.solve`` (verified equal on the enumerated fact space, see
``pipeline_equivalence``).  Each stage is an operator with:

* ``trigger``  - whether the operator actually acts on this fact set,
* ``apply``    - what it does (the correct behaviour),
* ``fallback`` - the countermodel used for ablation: "what you would compute if you
                 did not perform this test" (assume the test passes, no gate, no
                 credit routing, naive default, ...).

Ablating one operator and re-running the pipeline yields either the unchanged
record (=> the operator is PRESENTATION_ONLY for this instance) or a different /
unresolved record (=> NECESSARY, with the necessity kind recorded).  Nothing here
calls a language model; every verdict is a deterministic replay.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from .canonical import canon, digest, sha256_text
from .constants import DERIVATION_OPERATOR_VERSION, LEDGER_ORDER
from .solver_bridge import flatten_record, solve, validate_record

NECESSARY = "NECESSARY"
PRESENTATION_ONLY = "PRESENTATION_ONLY"
NOT_ON_PATH = "NOT_ON_PATH"
ABLATION_UNRESOLVED = "ABLATION_UNRESOLVED"

KIND_FACT = "FACT_CONDITION"
KIND_RULE = "RULE_RECOGNITION"
KIND_STRUCTURAL = "STRUCTURAL"

DISMISSAL_GATE_SET = {"BOWLED", "LBW", "CAUGHT", "STUMPED"}


class UnresolvedDerivation(RuntimeError):
    """The pipeline cannot produce a record (used as an ablation signal)."""


# ---------------------------------------------------------------------------
# Draft state
# ---------------------------------------------------------------------------
@dataclass
class Draft:
    status: str | None = None
    dismissal: str | None = None
    blocked: bool = False
    wide_revoked: bool = False
    ledger: dict[str, int] = field(default_factory=lambda: {key: 0 for key in LEDGER_ORDER})
    movement: int = 0
    counts_in_over: bool | None = None
    bowler_runs: int | None = None

    def clone(self) -> "Draft":
        return Draft(
            status=self.status,
            dismissal=self.dismissal,
            blocked=self.blocked,
            wide_revoked=self.wide_revoked,
            ledger=dict(self.ledger),
            movement=self.movement,
            counts_in_over=self.counts_in_over,
            bowler_runs=self.bowler_runs,
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dismissal": self.dismissal,
            "blocked": self.blocked,
            "wide_revoked": self.wide_revoked,
            "ledger": dict(self.ledger),
            "movement": self.movement,
            "counts_in_over": self.counts_in_over,
            "bowler_runs": self.bowler_runs,
        }


@dataclass(frozen=True)
class Operator:
    op_id: str
    stage: str
    necessity_kind: str
    reads: tuple[str, ...]
    writes: tuple[str, ...]
    description: str
    trigger: Callable[[Draft, dict], bool]
    apply: Callable[[Draft, dict], None]
    fallback: Callable[[Draft, dict], None]
    rule_key: Callable[[Draft, dict], str | None]


@dataclass(frozen=True)
class StepRecord:
    op_id: str
    stage: str
    fired: bool
    rule_key: str | None
    state_before_sha256: str
    state_after_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "operator_id": self.op_id,
            "stage": self.stage,
            "fired": self.fired,
            "rule_key": self.rule_key,
            "state_before_sha256": self.state_before_sha256,
            "state_after_sha256": self.state_after_sha256,
        }


@dataclass(frozen=True)
class PipelineResult:
    record: dict[str, Any] | None
    flat: dict[str, Any] | None
    flat_sha256: str | None
    steps: tuple[StepRecord, ...]
    fired_ops: tuple[str, ...]
    unresolved: str | None

    @property
    def resolved(self) -> bool:
        return self.unresolved is None


# ---------------------------------------------------------------------------
# Operator implementations (mirror vett_r25.solver._dismissal / solve)
# ---------------------------------------------------------------------------
def _t_status_early_dead(draft: Draft, facts: dict) -> bool:
    return bool(facts.get("early_dead_reball"))


def _a_status_early_dead(draft: Draft, facts: dict) -> None:
    draft.status = "DEAD_REBALL"


def _t_status_no_ball(draft: Draft, facts: dict) -> bool:
    return draft.status is None and bool(facts.get("no_ball_called"))


def _a_status_no_ball(draft: Draft, facts: dict) -> None:
    draft.status = "NO_BALL"


def _t_status_wide_revoke(draft: Draft, facts: dict) -> bool:
    return (
        draft.status is None
        and bool(facts.get("wide_called"))
        and str(facts.get("contact", "NONE")) != "NONE"
    )


def _a_status_wide_revoke(draft: Draft, facts: dict) -> None:
    draft.status = "LEGAL"
    draft.wide_revoked = True


def _t_status_wide(draft: Draft, facts: dict) -> bool:
    return draft.status is None and bool(facts.get("wide_called")) and not draft.wide_revoked


def _a_status_wide(draft: Draft, facts: dict) -> None:
    draft.status = "WIDE"


def _t_status_legal_default(draft: Draft, facts: dict) -> bool:
    return draft.status is None


def _a_status_legal_default(draft: Draft, facts: dict) -> None:
    draft.status = "LEGAL"


def _t_dismissal_none(draft: Draft, facts: dict) -> bool:
    return str(facts.get("dismissal_candidate", "NONE")) == "NONE"


def _a_dismissal_none(draft: Draft, facts: dict) -> None:
    draft.dismissal = "NONE"
    draft.blocked = True


def _t_gate_appeal(draft: Draft, facts: dict) -> bool:
    candidate = str(facts.get("dismissal_candidate", "NONE"))
    if candidate == "NONE" or draft.blocked:
        return False
    return not facts.get("appeal_made", True) or not facts.get("appeal_in_time", True)


def _a_gate_blocks(draft: Draft, facts: dict) -> None:
    draft.dismissal = "NONE"
    draft.blocked = True


def _t_gate_dead_sequence(draft: Draft, facts: dict) -> bool:
    if draft.blocked or str(facts.get("dismissal_candidate", "NONE")) == "NONE":
        return False
    return bool(facts.get("early_dead_reball")) or bool(facts.get("dead_before_wicket"))


def _t_gate_deception(draft: Draft, facts: dict) -> bool:
    if draft.blocked or str(facts.get("dismissal_candidate", "NONE")) == "NONE":
        return False
    return bool(facts.get("wilful_deception"))


def _t_gate_fair_wicket(draft: Draft, facts: dict) -> bool:
    if draft.blocked or str(facts.get("dismissal_candidate", "NONE")) == "NONE":
        return False
    return not facts.get("wicket_fair", True)


def _candidate(draft: Draft, facts: dict) -> str:
    return str(facts.get("dismissal_candidate", "NONE"))


def _t_bowled(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "BOWLED"


def _a_bowled(draft: Draft, facts: dict) -> None:
    if draft.status != "LEGAL" or not facts.get("wicket_broken_by_delivery", True):
        draft.dismissal = "NONE"
    else:
        draft.dismissal = "BOWLED"


def _f_bowled(draft: Draft, facts: dict) -> None:
    # Countermodel: take the opposite decision of the test.  If the test would
    # pass, the alternative is "not out"; if it would fail, the alternative is
    # "out".  Comparing the two outcomes is what makes the verdict symmetric.
    would_pass = draft.status == "LEGAL" and facts.get("wicket_broken_by_delivery", True)
    draft.dismissal = "NONE" if would_pass else "BOWLED"


def _t_lbw(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "LBW"


def _a_lbw(draft: Draft, facts: dict) -> None:
    tests_pass = all(
        facts.get(key, False)
        for key in ("lbw_pitch_valid", "lbw_impact_valid", "lbw_would_hit_wicket")
    )
    if draft.status != "LEGAL" or not tests_pass:
        draft.dismissal = "NONE"
    else:
        draft.dismissal = "LBW"


def _f_lbw(draft: Draft, facts: dict) -> None:
    tests_pass = all(
        facts.get(key, False)
        for key in ("lbw_pitch_valid", "lbw_impact_valid", "lbw_would_hit_wicket")
    )
    would_pass = draft.status == "LEGAL" and tests_pass
    draft.dismissal = "NONE" if would_pass else "LBW"


def _t_caught(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "CAUGHT"


def _a_caught(draft: Draft, facts: dict) -> None:
    if (
        str(facts.get("contact")) != "BAT"
        or not facts.get("catch_complete", True)
        or facts.get("ball_grounded_before_control", False)
        or facts.get("boundary_contact_before_completion")
    ):
        draft.dismissal = "NONE"
    else:
        draft.dismissal = "CAUGHT"


def _f_caught(draft: Draft, facts: dict) -> None:
    would_pass = not (
        str(facts.get("contact")) != "BAT"
        or not facts.get("catch_complete", True)
        or facts.get("ball_grounded_before_control", False)
        or facts.get("boundary_contact_before_completion")
    )
    draft.dismissal = "NONE" if would_pass else "CAUGHT"


def _t_run_out(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "RUN_OUT"


def _a_run_out(draft: Draft, facts: dict) -> None:
    draft.dismissal = "RUN_OUT" if facts.get("out_of_ground", True) else "NONE"


def _f_run_out(draft: Draft, facts: dict) -> None:
    would_pass = bool(facts.get("out_of_ground", True))
    draft.dismissal = "NONE" if would_pass else "RUN_OUT"


def _t_nb_keeper_exception(draft: Draft, facts: dict) -> bool:
    return (
        not draft.blocked
        and _candidate(draft, facts) == "RUN_OUT"
        and draft.status == "NO_BALL"
        and bool(facts.get("keeper_only"))
        and not facts.get("attempting_run")
    )


def _a_nb_keeper_exception(draft: Draft, facts: dict) -> None:
    draft.dismissal = "NONE"


def _f_nb_keeper_exception(draft: Draft, facts: dict) -> None:
    # Countermodel: keep the run-out that the ground test already produced.
    if draft.dismissal is None:
        draft.dismissal = "RUN_OUT"


def _t_stumped(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "STUMPED_OR_RUN_OUT"


def _a_stumped(draft: Draft, facts: dict) -> None:
    if not facts.get("out_of_ground", True):
        draft.dismissal = "NONE"
        return
    keeper_alone = bool(facts.get("keeper_only")) and not facts.get("attempting_run")
    if draft.status == "NO_BALL":
        # Law 38.2.2.2: after No ball a keeper-only put-down without an attempted
        # run is not out; otherwise the choice resolves to Run out.
        draft.dismissal = "NONE" if keeper_alone else "RUN_OUT"
        return
    draft.dismissal = "STUMPED" if keeper_alone else "RUN_OUT"


def _f_stumped(draft: Draft, facts: dict) -> None:
    keeper_alone = bool(facts.get("keeper_only")) and not facts.get("attempting_run")
    if not facts.get("out_of_ground", True):
        outcome = "NONE"
    elif draft.status == "NO_BALL":
        outcome = "NONE" if keeper_alone else "RUN_OUT"
    else:
        outcome = "STUMPED" if keeper_alone else "RUN_OUT"
    # countermodel: a different decision among the reachable outcomes
    alternative = {"STUMPED": "RUN_OUT", "RUN_OUT": "STUMPED", "NONE": "RUN_OUT"}
    draft.dismissal = alternative[outcome]


def _t_return_obstructing(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "OBSTRUCTING_FIELD"


def _t_return_hit_twice(draft: Draft, facts: dict) -> bool:
    return not draft.blocked and _candidate(draft, facts) == "HIT_BALL_TWICE"


def _a_return_candidate(draft: Draft, facts: dict) -> None:
    draft.dismissal = _candidate(draft, facts)


def _f_return_none(draft: Draft, facts: dict) -> None:
    draft.dismissal = "NONE"


def _t_ledger_status_extra(draft: Draft, facts: dict) -> bool:
    return draft.status in {"NO_BALL", "WIDE"}


def _a_ledger_status_extra(draft: Draft, facts: dict) -> None:
    if draft.status == "NO_BALL":
        draft.ledger["NO_BALL_EXTRA"] += 1
    else:
        draft.ledger["WIDE_EXTRA"] += 1


def _t_movement(draft: Draft, facts: dict) -> bool:
    return bool(
        int(facts.get("completed_runs", 0))
        or str(facts.get("boundary_mode", "NONE")) != "NONE"
        or facts.get("award_run_in_progress")
        or facts.get("wilful_deception")
    )


def _a_movement(draft: Draft, facts: dict) -> None:
    boundary = int(facts.get("boundary_allowance", 0))
    mode = str(facts.get("boundary_mode", "NONE"))
    completed = int(facts.get("completed_runs", 0))
    movement = completed
    if mode == "OVERTHROW":
        movement += boundary + (1 if facts.get("crossed_at_throw") else 0)
    elif mode == "NORMAL" and boundary:
        movement = boundary
    elif mode == "LATER_AFTER_WICKET":
        movement = completed if draft.dismissal != "NONE" else max(boundary, completed)
    if facts.get("award_run_in_progress") or facts.get("wilful_deception"):
        movement += 1
    draft.movement = movement


def _f_movement(draft: Draft, facts: dict) -> None:
    draft.movement = int(facts.get("completed_runs", 0))


def _t_run_credit(draft: Draft, facts: dict) -> bool:
    return draft.status != "DEAD_REBALL" and draft.movement != 0


def _a_run_credit(draft: Draft, facts: dict) -> None:
    contact = str(facts.get("contact", "NONE"))
    if contact == "BAT":
        draft.ledger["BATTER"] += draft.movement
    elif draft.status == "WIDE":
        draft.ledger["WIDE_EXTRA"] += draft.movement
    elif contact == "PERSON":
        draft.ledger["LEG_BYE"] += draft.movement
    else:
        draft.ledger["BYE"] += draft.movement


def _f_run_credit(draft: Draft, facts: dict) -> None:
    draft.ledger["BATTER"] += draft.movement


def _t_penalty(draft: Draft, facts: dict) -> bool:
    return int(facts.get("penalty_runs_batting", 0)) != 0 or bool(facts.get("wilful_deception"))


def _a_penalty(draft: Draft, facts: dict) -> None:
    draft.ledger["PENALTY"] += int(facts.get("penalty_runs_batting", 0))
    if facts.get("wilful_deception"):
        draft.ledger["PENALTY"] += 5


def _t_completed_dismissal_suppress(draft: Draft, facts: dict) -> bool:
    return draft.dismissal in DISMISSAL_GATE_SET


def _a_completed_dismissal_suppress(draft: Draft, facts: dict) -> None:
    for key in ("BATTER", "BYE", "LEG_BYE"):
        draft.ledger[key] = 0
    if draft.status == "WIDE":
        draft.ledger["WIDE_EXTRA"] = 1


def _t_dead_reball_zero(draft: Draft, facts: dict) -> bool:
    return draft.status == "DEAD_REBALL"


def _a_dead_reball_zero(draft: Draft, facts: dict) -> None:
    for key in LEDGER_ORDER:
        draft.ledger[key] = 0


def _t_bowler_debit(draft: Draft, facts: dict) -> bool:
    return True


def _a_bowler_debit(draft: Draft, facts: dict) -> None:
    draft.bowler_runs = (
        draft.ledger["BATTER"] + draft.ledger["NO_BALL_EXTRA"] + draft.ledger["WIDE_EXTRA"]
    )


def _f_bowler_debit(draft: Draft, facts: dict) -> None:
    draft.bowler_runs = draft.ledger["BATTER"]


def _t_counts(draft: Draft, facts: dict) -> bool:
    return True


def _a_counts(draft: Draft, facts: dict) -> None:
    draft.counts_in_over = (
        draft.status == "LEGAL"
        and not facts.get("forced_not_count", False)
        and not facts.get("wilful_deception", False)
    )


def _f_counts(draft: Draft, facts: dict) -> None:
    draft.counts_in_over = draft.status == "LEGAL"


def _never_rule(draft: Draft, facts: dict) -> str | None:
    return None


def _rule_early_dead(draft: Draft, facts: dict) -> str | None:
    return "EARLY_DEAD"


def _rule_nb_precedence(draft: Draft, facts: dict) -> str | None:
    return "NB_PRECEDENCE"


def _rule_wide_contact(draft: Draft, facts: dict) -> str | None:
    return "WIDE_CONTACT"


def _rule_wide_score(draft: Draft, facts: dict) -> str | None:
    return "WIDE_SCORE"


def _rule_legal_count(draft: Draft, facts: dict) -> str | None:
    return "LEGAL_COUNT"


def _rule_appeal(draft: Draft, facts: dict) -> str | None:
    return "APPEAL"


def _rule_dead_sequence(draft: Draft, facts: dict) -> str | None:
    return "DEAD_SEQUENCE"


def _rule_deception(draft: Draft, facts: dict) -> str | None:
    return "DECEPTION"


def _rule_bowled(draft: Draft, facts: dict) -> str | None:
    return "BOWLED_TEST"


def _rule_lbw(draft: Draft, facts: dict) -> str | None:
    return "LBW_TEST"


def _rule_caught(draft: Draft, facts: dict) -> str | None:
    return "CAUGHT_CONTROL"


def _rule_run_out(draft: Draft, facts: dict) -> str | None:
    return "RUNOUT_TEST"


def _rule_nb_keeper(draft: Draft, facts: dict) -> str | None:
    return "NB_KEEPER_RUNOUT_EXCEPTION"


def _rule_stumped(draft: Draft, facts: dict) -> str | None:
    return "STUMPED_TEST"


def _rule_special_dismissal(draft: Draft, facts: dict) -> str | None:
    if draft.status == "NO_BALL":
        return "NB_DISMISSAL_GATE"
    if draft.status == "WIDE":
        return "WIDE_DISMISSAL_GATE"
    return None


def _rule_ledger_extra(draft: Draft, facts: dict) -> str | None:
    return "NB_SCORE" if draft.status == "NO_BALL" else "WIDE_SCORE"


def _rule_movement(draft: Draft, facts: dict) -> str | None:
    mode = str(facts.get("boundary_mode", "NONE"))
    if mode == "OVERTHROW":
        return "OVERTHROW"
    if mode == "NORMAL":
        return "BOUNDARY_NORMAL"
    return None


def _rule_bat_credit(draft: Draft, facts: dict) -> str | None:
    return "BAT_CREDIT" if str(facts.get("contact")) == "BAT" else None


def _rule_penalty_deception(draft: Draft, facts: dict) -> str | None:
    return "DECEPTION" if facts.get("wilful_deception") else None


def _rule_dead_zero(draft: Draft, facts: dict) -> str | None:
    return "EARLY_DEAD"


def _rule_bowler(draft: Draft, facts: dict) -> str | None:
    return "BOWLER_DEBIT"


def _rule_counts(draft: Draft, facts: dict) -> str | None:
    if draft.status == "NO_BALL":
        return "NB_COUNT"
    if draft.status == "WIDE":
        return "WIDE_COUNT"
    return "LEGAL_COUNT"


def _noop(draft: Draft, facts: dict) -> None:  # noqa: ARG001 - uniform signature
    return None


OPERATORS: tuple[Operator, ...] = (
    Operator("STATUS_EARLY_DEAD", "STATUS", KIND_FACT, ("early_dead_reball",), ("delivery_status",),
             "early Dead ball becomes the delivery status before any other call",
             _t_status_early_dead, _a_status_early_dead, _noop, _rule_early_dead),
    Operator("STATUS_NO_BALL", "STATUS", KIND_FACT, ("no_ball_called",), ("delivery_status",),
             "a No-ball call outranks a Wide call",
             _t_status_no_ball, _a_status_no_ball, _noop, _rule_nb_precedence),
    Operator("STATUS_WIDE_REVOKE", "STATUS", KIND_FACT, ("wide_called", "contact"), ("delivery_status",),
             "a Wide call is revoked when the ball touched bat or person",
             _t_status_wide_revoke, _a_status_wide_revoke, _noop, _rule_wide_contact),
    Operator("STATUS_WIDE", "STATUS", KIND_FACT, ("wide_called", "contact"), ("delivery_status",),
             "an unrevoked Wide call becomes the delivery status",
             _t_status_wide, _a_status_wide, _noop, _rule_wide_score),
    Operator("STATUS_LEGAL_DEFAULT", "STATUS", KIND_STRUCTURAL, (), ("delivery_status",),
             "no overriding call: the delivery is legal",
             _t_status_legal_default, _a_status_legal_default, _noop, _rule_legal_count),
    Operator("DISMISSAL_NONE_CANDIDATE", "DISMISSAL", KIND_STRUCTURAL, ("dismissal_candidate",),
             ("dismissal",), "no wicket event was submitted",
             _t_dismissal_none, _a_dismissal_none, _noop, _never_rule),
    Operator("GATE_APPEAL", "DISMISSAL", KIND_FACT, ("appeal_made", "appeal_in_time"), ("dismissal",),
             "no dismissal without a timely fielding-side appeal",
             _t_gate_appeal, _a_gate_blocks, _noop, _rule_appeal),
    Operator("GATE_DEAD_SEQUENCE", "DISMISSAL", KIND_FACT, ("early_dead_reball", "dead_before_wicket"),
             ("dismissal",), "a wicket broken after the ball is dead cannot count",
             _t_gate_dead_sequence, _a_gate_blocks, _noop, _rule_dead_sequence),
    Operator("GATE_DECEPTION", "DISMISSAL", KIND_FACT, ("wilful_deception",), ("dismissal",),
             "wilful deception makes the ball dead and removes dismissal",
             _t_gate_deception, _a_gate_blocks, _noop, _rule_deception),
    Operator("GATE_FAIR_WICKET", "DISMISSAL", KIND_FACT, ("wicket_fair",), ("dismissal",),
             "an unfair put-down is not a dismissal",
             _t_gate_fair_wicket, _a_gate_blocks, _noop, _never_rule),
    Operator("BOWLED_TEST", "DISMISSAL", KIND_FACT, ("delivery_status", "wicket_broken_by_delivery"),
             ("dismissal",), "Bowled needs a legal delivery that broke the striker's wicket",
             _t_bowled, _a_bowled, _f_bowled, _rule_bowled),
    Operator("LBW_THREE_TESTS", "DISMISSAL", KIND_FACT,
             ("delivery_status", "lbw_pitch_valid", "lbw_impact_valid", "lbw_would_hit_wicket"),
             ("dismissal",), "LBW needs a legal delivery plus pitching, impact and wicket tests",
             _t_lbw, _a_lbw, _f_lbw, _rule_lbw),
    Operator("CAUGHT_CONTROL", "DISMISSAL", KIND_FACT,
             ("contact", "catch_complete", "ball_grounded_before_control",
              "boundary_contact_before_completion"),
             ("dismissal",), "Caught needs bat contact and a fair, complete catch",
             _t_caught, _a_caught, _f_caught, _rule_caught),
    Operator("RUNOUT_GROUND_TEST", "DISMISSAL", KIND_FACT, ("out_of_ground",), ("dismissal",),
             "Run out needs the batter to be out of ground",
             _t_run_out, _a_run_out, _f_run_out, _rule_run_out),
    Operator("NB_KEEPER_RUNOUT_EXCEPTION", "DISMISSAL", KIND_FACT,
             ("delivery_status", "keeper_only", "attempting_run"), ("dismissal",),
             "after No ball a keeper-only put-down without an attempted run is not Run out",
             _t_nb_keeper_exception, _a_nb_keeper_exception, _f_nb_keeper_exception, _rule_nb_keeper),
    Operator("STUMPED_KEEPER_TEST", "DISMISSAL", KIND_FACT,
             ("delivery_status", "out_of_ground", "keeper_only", "attempting_run"), ("dismissal",),
             "Stumped vs Run out is decided by keeper-only control and the attempted run",
             _t_stumped, _a_stumped, _f_stumped, _rule_stumped),
    Operator("DISMISSAL_RETURN_OBSTRUCTING", "DISMISSAL", KIND_RULE, ("dismissal_candidate",),
             ("dismissal",), "Obstructing the field remains available as a dismissal",
             _t_return_obstructing, _a_return_candidate, _f_return_none, _rule_special_dismissal),
    Operator("DISMISSAL_RETURN_HIT_BALL_TWICE", "DISMISSAL", KIND_RULE, ("dismissal_candidate",),
             ("dismissal",), "Hit the ball twice remains available as a dismissal",
             _t_return_hit_twice, _a_return_candidate, _f_return_none, _rule_special_dismissal),
    Operator("LEDGER_STATUS_EXTRA", "LEDGER", KIND_FACT, ("delivery_status",),
             ("ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA"),
             "a No ball adds one No-ball extra, a Wide adds one Wide extra",
             _t_ledger_status_extra, _a_ledger_status_extra, _noop, _rule_ledger_extra),
    Operator("MOVEMENT_COMPOSE", "LEDGER", KIND_FACT,
             ("completed_runs", "boundary_mode", "boundary_allowance", "crossed_at_throw",
              "award_run_in_progress", "wilful_deception", "dismissal"),
             ("movement",), "runs before the terminal event: completed runs, boundary allowance, awards",
             _t_movement, _a_movement, _f_movement, _rule_movement),
    Operator("RUN_CREDIT_ROUTE", "LEDGER", KIND_FACT, ("contact", "delivery_status"),
             ("ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.WIDE_EXTRA"),
             "credit movement to bat, byes, leg byes or wide extras by contact",
             _t_run_credit, _a_run_credit, _f_run_credit, _rule_bat_credit),
    Operator("PENALTY_AWARD", "LEDGER", KIND_FACT, ("penalty_runs_batting", "wilful_deception"),
             ("ledger.PENALTY",), "penalty runs awarded to the batting side",
             _t_penalty, _a_penalty, _noop, _rule_penalty_deception),
    Operator("COMPLETED_DISMISSAL_SUPPRESS", "LEDGER", KIND_FACT, ("dismissal", "delivery_status"),
             ("ledger.BATTER", "ledger.BYE", "ledger.LEG_BYE", "ledger.WIDE_EXTRA"),
             "a completed dismissal removes ordinary running from the ledger",
             _t_completed_dismissal_suppress, _a_completed_dismissal_suppress, _noop, _never_rule),
    Operator("DEAD_REBALL_ZERO", "LEDGER", KIND_FACT, ("delivery_status",), tuple(
        f"ledger.{key}" for key in LEDGER_ORDER),
             "a Dead ball records nothing",
             _t_dead_reball_zero, _a_dead_reball_zero, _noop, _rule_dead_zero),
    Operator("BOWLER_DEBIT", "RECORD", KIND_FACT,
             ("ledger.BATTER", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA"), ("bowler_runs",),
             "the bowling analysis debits batter runs and both extra types",
             _t_bowler_debit, _a_bowler_debit, _f_bowler_debit, _rule_bowler),
    Operator("COUNTS_IN_OVER", "RECORD", KIND_FACT, ("delivery_status", "forced_not_count",
                                                     "wilful_deception"), ("counts_in_over",),
             "only an ordinary legal delivery counts as one of the over",
             _t_counts, _a_counts, _f_counts, _rule_counts),
)

OPERATOR_BY_ID = {operator.op_id: operator for operator in OPERATORS}
OPERATOR_ORDER = tuple(operator.op_id for operator in OPERATORS)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run_pipeline(facts: dict, *, ablate: str | None = None) -> PipelineResult:
    """Run the staged derivation; optionally ablate exactly one operator."""

    if ablate is not None and ablate not in OPERATOR_BY_ID:
        raise KeyError(f"unknown operator to ablate: {ablate}")

    draft = Draft()
    steps: list[StepRecord] = []
    fired: list[str] = []
    for operator in OPERATORS:
        before = sha256_text(canon(draft.snapshot()))
        is_fired = bool(operator.trigger(draft, facts))
        rule_key = operator.rule_key(draft, facts) if is_fired else None
        if is_fired:
            fired.append(operator.op_id)
            if operator.op_id == ablate:
                operator.fallback(draft, facts)
            else:
                operator.apply(draft, facts)
        after = sha256_text(canon(draft.snapshot()))
        steps.append(StepRecord(operator.op_id, operator.stage, is_fired, rule_key, before, after))

    unresolved: str | None = None
    record: dict | None = None
    flat: dict | None = None
    flat_sha: str | None = None
    if draft.status is None:
        unresolved = "delivery_status"
    elif draft.dismissal is None:
        unresolved = "dismissal"
    elif draft.counts_in_over is None:
        unresolved = "counts_in_over"
    elif draft.bowler_runs is None:
        unresolved = "bowler_runs"
    else:
        ledger = {key: int(draft.ledger.get(key, 0)) for key in LEDGER_ORDER}
        record = {
            "delivery_status": draft.status,
            "counts_in_over": bool(draft.counts_in_over),
            "dismissal": draft.dismissal,
            "total_runs": sum(ledger.values()),
            "batter_runs": ledger["BATTER"],
            "bowler_runs": int(draft.bowler_runs),
            "run_ledger": [
                {"account": account, "runs": value}
                for account, value in ledger.items()
                if value
            ] or [{"account": "NONE", "runs": 0}],
        }
        try:
            validate_record(record)
        except ValueError as exc:  # pragma: no cover - defensive
            unresolved = f"invalid_record:{exc}"
            record = None
    if record is not None:
        flat = flatten_record(record)
        flat_sha = sha256_text(canon(flat))
    return PipelineResult(
        record=record,
        flat=flat,
        flat_sha256=flat_sha,
        steps=tuple(steps),
        fired_ops=tuple(fired),
        unresolved=unresolved,
    )


def pipeline_equivalence(fact_sets: Iterable[dict]) -> dict[str, Any]:
    """Prove the staged pipeline equals the frozen solver on the given fact sets."""

    checked = 0
    mismatches: list[dict[str, Any]] = []
    for facts in fact_sets:
        checked += 1
        oracle_record = solve(facts)
        oracle_flat = flatten_record(oracle_record)
        result = run_pipeline(facts)
        if not result.resolved:
            mismatches.append({"facts": facts, "reason": f"unresolved:{result.unresolved}"})
            continue
        if canon(result.flat) != canon(oracle_flat):
            mismatches.append({
                "facts": facts,
                "pipeline": result.flat,
                "solver": oracle_flat,
            })
    return {
        "checked": checked,
        "mismatches": len(mismatches),
        "first_mismatches": mismatches[:5],
        "equal": not mismatches,
    }


# ---------------------------------------------------------------------------
# Derivation analysis (ablation-based necessity)
# ---------------------------------------------------------------------------
@dataclass
class DerivationAnalysis:
    facts_sha256: str
    record_sha256: str
    record: dict[str, Any]
    flat: dict[str, Any]
    steps: list[dict[str, Any]]
    operators: list[dict[str, Any]]
    necessary: list[str]
    presentation_only: list[str]
    not_on_path: list[str]
    derivation_depth_verified: int
    derivation_depth_content: int
    derivation_depth_structural: int
    rule_keys: list[str]
    necessary_rule_keys: list[str]
    unresolved: str | None
    operator_version: str = DERIVATION_OPERATOR_VERSION

    def witness(self) -> dict[str, Any]:
        return {
            "operator_version": self.operator_version,
            "facts_sha256": self.facts_sha256,
            "record_sha256": self.record_sha256,
            "record": self.record,
            "unresolved": self.unresolved,
            "derivation_depth_verified": self.derivation_depth_verified,
            "derivation_depth_content": self.derivation_depth_content,
            "derivation_depth_structural": self.derivation_depth_structural,
            "necessary_operators": self.necessary,
            "presentation_only_operators": self.presentation_only,
            "not_on_path_operators": self.not_on_path,
            "rule_keys": self.rule_keys,
            "necessary_rule_keys": self.necessary_rule_keys,
            "steps": self.steps,
            "operators": self.operators,
        }


def analyse_derivation(facts: dict) -> DerivationAnalysis:
    """Replay the derivation and mechanically classify every operator."""

    base = run_pipeline(facts)
    if not base.resolved:
        raise UnresolvedDerivation(f"gold derivation unresolved: {base.unresolved}")
    gold_sha = base.flat_sha256
    operator_rows: list[dict[str, Any]] = []
    necessary: list[str] = []
    presentation: list[str] = []
    not_on_path: list[str] = []
    for step in base.steps:
        operator = OPERATOR_BY_ID[step.op_id]
        if not step.fired:
            not_on_path.append(step.op_id)
            operator_rows.append({
                "operator_id": step.op_id,
                "stage": step.stage,
                "fired": False,
                "verdict": NOT_ON_PATH,
                "necessity_kind": operator.necessity_kind,
                "rule_key": None,
                "reads": list(operator.reads),
                "writes": list(operator.writes),
                "description": operator.description,
                "ablation": None,
            })
            continue
        ablated = run_pipeline(facts, ablate=step.op_id)
        if not ablated.resolved:
            verdict = NECESSARY
            ablation = {
                "outcome": ABLATION_UNRESOLVED,
                "unresolved_field": ablated.unresolved,
                "ablated_record_sha256": None,
            }
        elif ablated.flat_sha256 != gold_sha:
            verdict = NECESSARY
            changed = [
                field
                for field in sorted(base.flat)
                if ablated.flat.get(field) != base.flat.get(field)
            ]
            ablation = {
                "outcome": "RECORD_CHANGED",
                "ablated_record_sha256": ablated.flat_sha256,
                "changed_fields": sorted(changed),
            }
        else:
            verdict = PRESENTATION_ONLY
            ablation = {
                "outcome": "RECORD_UNCHANGED",
                "ablated_record_sha256": ablated.flat_sha256,
                "changed_fields": [],
            }
        if verdict == NECESSARY:
            necessary.append(step.op_id)
        else:
            presentation.append(step.op_id)
        operator_rows.append({
            "operator_id": step.op_id,
            "stage": step.stage,
            "fired": True,
            "verdict": verdict,
            "necessity_kind": operator.necessity_kind,
            "rule_key": step.rule_key,
            "reads": list(operator.reads),
            "writes": list(operator.writes),
            "description": operator.description,
            "ablation": ablation,
        })

    necessary_kinds = {
        row["operator_id"]: row["necessity_kind"]
        for row in operator_rows
        if row["verdict"] == NECESSARY
    }
    content_depth = sum(1 for kind in necessary_kinds.values() if kind != KIND_STRUCTURAL)
    structural_depth = sum(1 for kind in necessary_kinds.values() if kind == KIND_STRUCTURAL)
    rule_keys = sorted({row["rule_key"] for row in operator_rows if row["fired"] and row["rule_key"]})
    necessary_rule_keys = sorted({
        row["rule_key"]
        for row in operator_rows
        if row["fired"] and row["rule_key"] and row["verdict"] == NECESSARY
    })
    return DerivationAnalysis(
        facts_sha256=sha256_text(canon(facts)),
        record_sha256=gold_sha,
        record=base.record,
        flat=base.flat,
        steps=[step.as_dict() for step in base.steps],
        operators=operator_rows,
        necessary=necessary,
        presentation_only=presentation,
        not_on_path=not_on_path,
        derivation_depth_verified=len(necessary),
        derivation_depth_content=content_depth,
        derivation_depth_structural=structural_depth,
        rule_keys=rule_keys,
        necessary_rule_keys=necessary_rule_keys,
        unresolved=None,
    )


# ---------------------------------------------------------------------------
# Countermodel scan over facts (pivotal-fact proof for the evidence set)
# ---------------------------------------------------------------------------
def fact_pivot_scan(facts: dict, domains: dict[str, list], *, gold_sha256: str) -> dict[str, Any]:
    """For every fact, search all alternative legal values for a countermodel.

    A fact is *pivotal* iff some single-value change alters the record (or makes it
    unresolvable).  Pivotal facts must be cited in the minimum evidence set;
    non-pivotal facts are context only.
    """

    rows: list[dict[str, Any]] = []
    pivotal: list[str] = []
    context: list[str] = []
    for field_name in sorted(facts):
        current = facts[field_name]
        alternatives = [value for value in domains.get(field_name, []) if value != current]
        if not alternatives:
            alternatives = _implicit_alternatives(current)
        witness: dict[str, Any] | None = None
        for value in alternatives:
            mutated = dict(facts)
            mutated[field_name] = value
            result = run_pipeline(mutated)
            if not result.resolved:
                witness = {
                    "field": field_name,
                    "from": current,
                    "to": value,
                    "outcome": ABLATION_UNRESOLVED,
                    "unresolved_field": result.unresolved,
                    "record_sha256": None,
                }
                break
            if result.flat_sha256 != gold_sha256:
                witness = {
                    "field": field_name,
                    "from": current,
                    "to": value,
                    "outcome": "RECORD_CHANGED",
                    "record_sha256": result.flat_sha256,
                }
                break
        row = {
            "field": field_name,
            "value": current,
            "alternatives_tested": len(alternatives),
            "pivotal": witness is not None,
            "countermodel": witness,
        }
        rows.append(row)
        (pivotal if witness is not None else context).append(field_name)
    return {
        "fields": rows,
        "pivotal_fields": pivotal,
        "context_fields": context,
        "pivotal_count": len(pivotal),
        "context_count": len(context),
        "gold_record_sha256": gold_sha256,
    }


def _implicit_alternatives(value: Any) -> list[Any]:
    if isinstance(value, bool):
        return [not value]
    if isinstance(value, int):
        return [value + 1, max(0, value - 1)]
    if isinstance(value, str):
        return []
    return []


__all__ = [
    "ABLATION_UNRESOLVED",
    "DISMISSAL_GATE_SET",
    "KIND_FACT",
    "KIND_RULE",
    "KIND_STRUCTURAL",
    "NECESSARY",
    "NOT_ON_PATH",
    "OPERATORS",
    "OPERATOR_BY_ID",
    "OPERATOR_ORDER",
    "PRESENTATION_ONLY",
    "DerivationAnalysis",
    "Draft",
    "Operator",
    "PipelineResult",
    "UnresolvedDerivation",
    "analyse_derivation",
    "digest",
    "fact_pivot_scan",
    "pipeline_equivalence",
    "run_pipeline",
]
