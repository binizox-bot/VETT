from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .solver import intervene, solve


@dataclass(frozen=True)
class ScenarioTemplate:
    family_id: str
    level: str
    facts: dict[str, Any]
    visible_fields: tuple[str, ...]
    intervention_field: str
    intervention_value: Any
    rule_keys: tuple[str, ...]
    alias_hops: int
    temporal_joins: int
    rule_operators: int
    scope_decisions: int
    isomorphic_distractors: int

    def records(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        factual = solve(self.facts)
        changed, counterfactual = intervene(
            self.facts, self.intervention_field, self.intervention_value
        )
        return factual, changed, counterfactual


def _t(
    family_id: str,
    level: str,
    facts: dict[str, Any],
    visible_fields: tuple[str, ...],
    intervention_field: str,
    intervention_value: Any,
    rule_keys: tuple[str, ...],
    structure: tuple[int, int, int, int, int],
) -> ScenarioTemplate:
    return ScenarioTemplate(
        family_id, level, facts, visible_fields, intervention_field,
        intervention_value, rule_keys, *structure
    )


RULE_TEXT = {
    "NB_PRECEDENCE": "Law 21.12: a No-ball call overrides a Wide call at any time.",
    "NB_COUNT": "Law 21.16: a No ball does not count as one of the over.",
    "NB_SCORE": "Laws 21.14-21.15: a No-ball call adds one No-ball extra; completed runs and boundary allowances are added and classified by contact.",
    "WIDE_COUNT": "Law 22.8: a Wide does not count as one of the over.",
    "WIDE_SCORE": "Laws 22.6-22.7: a Wide adds one run, and completed runs or a boundary allowance from that delivery are recorded as Wides.",
    "WIDE_CONTACT": "Law 22.3.1: revoke a Wide call if the delivered ball contacts the striker's bat or person before contacting a fielder.",
    "LEGAL_COUNT": "Laws 17.3 and 20.7: an ordinary legal delivery counts as one valid ball unless a stated exception directs otherwise.",
    "EARLY_DEAD": "Law 20.7.1.1: when the delivered ball becomes dead before the striker had an opportunity to play it, it does not count in the over; the supported reball event records no delivery score.",
    "BOUNDARY_NORMAL": "Laws 19.6-19.7: use the agreed boundary allowance; absent a different agreement, a grounded boundary is four and a qualifying bat-struck ball first grounded beyond is six.",
    "BAT_CREDIT": "Law 21.15 and the scoring laws: runs from a ball struck by the bat are credited to the striker, apart from separately recorded penalty awards.",
    "BOWLER_DEBIT": "The bowling analysis debits batter runs and No-ball or Wide extras to the bowler, but not Byes, Leg byes or five-run penalties.",
    "NB_DISMISSAL_GATE": "Law 21.17: after No ball, dismissal is unavailable except under Hit the ball twice, Obstructing the field or Run out.",
    "BOWLED_TEST": "Law 32.1: Bowled requires a non-No-ball delivered ball to break the striker's wicket, including after first touching that striker's bat or person.",
    "LBW_TEST": "Law 36.1: LBW requires a non-No-ball delivery, a qualifying pitching and impact path, and a ball that would have hit the wicket.",
    "WIDE_DISMISSAL_GATE": "Law 22.9: after Wide, dismissal remains possible only under Hit wicket, Obstructing the field, Run out or Stumped.",
    "STUMPED_TEST": "Law 39.1: Stumped requires a non-No-ball delivery, a striker out of ground and not attempting a run, and the wicket fairly put down by the wicket-keeper without another fielder's intervention.",
    "NB_KEEPER_RUNOUT_EXCEPTION": "Law 38.2.2.2: after No ball, a striker out of ground but not attempting a run is not Run out when the wicket-keeper alone puts down the wicket.",
    "RUNOUT_TEST": "Laws 38.1-38.2: Run out requires the ball in play, a batter out of ground and that ground's wicket fairly put down, subject to the stated exceptions.",
    "APPEAL": "Laws 31.1 and 31.3: an umpire may not give a batter out without a fielding-side appeal made within the applicable window.",
    "CAUGHT_CONTROL": "Laws 33.1-33.3: Caught requires bat contact, no prior grounding, and a fair catch completed with control of both ball and movement; boundary grounding before completion prevents it.",
    "DEAD_SEQUENCE": "Laws 20.1 and 20.6: after the ball becomes dead, a later broken wicket or later boundary contact cannot create a dismissal or boundary score for that delivery.",
    "OVERTHROW": "Law 19.8: for an overthrow boundary, add the boundary allowance, runs completed at the instant of the throw, and the run in progress if the batters had already crossed then.",
    "DECEPTION": "Law 41.5: wilful deception after the striker receives the ball makes it dead, prevents dismissal, makes the ball not count, awards five Penalty runs and retains completed plus current running.",
    "SOURCE_ORDER": "Where the live worksheet and signed review sheet conflict on an observation, use the signed sheet with the later revision number for that observation; other fields keep their recorded values.",
}


SCENARIOS = (
    # L1: direct locator, one governing operation.
    _t("L1_NB_DOT", "L1",
       {"no_ball_called": True, "contact": "NONE", "completed_runs": 0},
       ("no_ball_called", "contact", "completed_runs"), "no_ball_called", False,
       ("NB_COUNT", "NB_SCORE", "BOWLER_DEBIT"), (0, 0, 1, 0, 0)),
    _t("L1_WIDE_DOT", "L1",
       {"wide_called": True, "contact": "NONE", "completed_runs": 0},
       ("wide_called", "contact", "completed_runs"), "wide_called", False,
       ("WIDE_COUNT", "WIDE_SCORE", "BOWLER_DEBIT"), (0, 0, 1, 0, 0)),
    _t("L1_LEGAL_FOUR", "L1",
       {"contact": "BAT", "boundary_mode": "NORMAL", "boundary_allowance": 4},
       ("contact", "boundary_mode", "boundary_allowance"), "boundary_allowance", 6,
       ("LEGAL_COUNT", "BOUNDARY_NORMAL", "BAT_CREDIT", "BOWLER_DEBIT"), (0, 0, 1, 0, 0)),
    _t("L1_EARLY_DEAD", "L1",
       {"early_dead_reball": True, "contact": "NONE", "completed_runs": 0},
       ("early_dead_reball", "contact", "completed_runs"), "early_dead_reball", False,
       ("EARLY_DEAD", "LEGAL_COUNT"), (0, 0, 1, 0, 0)),
    _t("L1_LEGAL_BOWLED", "L1",
       {"no_ball_called": False, "contact": "BAT", "dismissal_candidate": "BOWLED", "wicket_broken_by_delivery": True, "appeal_made": True, "appeal_in_time": True},
       ("no_ball_called", "contact", "dismissal_candidate", "wicket_broken_by_delivery", "appeal_made", "appeal_in_time"), "no_ball_called", True,
       ("APPEAL", "BOWLED_TEST", "NB_DISMISSAL_GATE", "LEGAL_COUNT"), (0, 0, 1, 0, 0)),

    # L2: alias hop plus precedence or exception gate.
    _t("L2_NB_OVER_WIDE", "L2",
       {"no_ball_called": True, "wide_called": True, "contact": "BAT", "completed_runs": 1},
       ("no_ball_called", "wide_called", "contact", "completed_runs"), "no_ball_called", False,
       ("NB_PRECEDENCE", "NB_COUNT", "NB_SCORE", "WIDE_CONTACT", "BAT_CREDIT", "BOWLER_DEBIT"), (1, 0, 3, 0, 1)),
    _t("L2_WIDE_BOUNDARY", "L2",
       {"wide_called": True, "contact": "NONE", "boundary_mode": "NORMAL", "boundary_allowance": 4},
       ("wide_called", "contact", "boundary_mode", "boundary_allowance"), "contact", "BAT",
       ("WIDE_CONTACT", "WIDE_COUNT", "WIDE_SCORE", "BAT_CREDIT", "BOWLER_DEBIT"), (1, 0, 2, 0, 1)),
    _t("L2_NB_BAT_FOUR", "L2",
       {"no_ball_called": False, "contact": "BAT", "boundary_mode": "NORMAL", "boundary_allowance": 4},
       ("no_ball_called", "contact", "boundary_mode", "boundary_allowance"), "no_ball_called", True,
       ("NB_COUNT", "NB_SCORE", "BOUNDARY_NORMAL", "BAT_CREDIT", "BOWLER_DEBIT"), (1, 0, 2, 0, 1)),
    _t("L2_NB_BOWLED", "L2",
       {"no_ball_called": False, "contact": "BAT", "dismissal_candidate": "BOWLED", "wicket_broken_by_delivery": True, "appeal_made": True, "appeal_in_time": True},
       ("no_ball_called", "contact", "dismissal_candidate", "wicket_broken_by_delivery", "appeal_made", "appeal_in_time"), "no_ball_called", True,
       ("NB_COUNT", "NB_SCORE", "NB_DISMISSAL_GATE", "APPEAL"), (1, 0, 2, 0, 1)),
    _t("L2_WIDE_STUMP", "L2",
       {"wide_called": True, "contact": "NONE", "dismissal_candidate": "STUMPED_OR_RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "attempting_run": False, "keeper_only": True},
       ("wide_called", "contact", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "attempting_run", "keeper_only"), "attempting_run", True,
       ("WIDE_DISMISSAL_GATE", "STUMPED_TEST", "RUNOUT_TEST", "APPEAL", "WIDE_SCORE"), (1, 0, 2, 0, 1)),

    # L3: temporal join and at least two dependent operators.
    _t("L3_NB_LBW", "L3",
       {"no_ball_called": False, "contact": "PERSON", "dismissal_candidate": "LBW", "lbw_pitch_valid": True, "lbw_impact_valid": True, "lbw_would_hit_wicket": True, "appeal_made": True, "appeal_in_time": True},
       ("no_ball_called", "contact", "dismissal_candidate", "lbw_pitch_valid", "lbw_impact_valid", "lbw_would_hit_wicket", "appeal_made", "appeal_in_time"), "no_ball_called", True,
       ("LBW_TEST", "NB_DISMISSAL_GATE", "NB_COUNT", "NB_SCORE", "APPEAL", "BOWLER_DEBIT"), (1, 1, 2, 0, 1)),
    _t("L3_CATCH_BOUNDARY", "L3",
       {"contact": "BAT", "dismissal_candidate": "CAUGHT", "appeal_made": True, "appeal_in_time": True, "catch_complete": True, "ball_grounded_before_control": False, "boundary_contact_before_completion": False, "boundary_mode": "NORMAL", "boundary_allowance": 4},
       ("contact", "dismissal_candidate", "appeal_made", "appeal_in_time", "catch_complete", "ball_grounded_before_control", "boundary_contact_before_completion", "boundary_mode", "boundary_allowance"), "boundary_contact_before_completion", True,
       ("CAUGHT_CONTROL", "BOUNDARY_NORMAL", "BAT_CREDIT", "APPEAL", "BOWLER_DEBIT"), (1, 1, 2, 0, 1)),
    _t("L3_DEAD_BEFORE_RUNOUT", "L3",
       {"contact": "BAT", "completed_runs": 1, "dismissal_candidate": "RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "dead_before_wicket": False, "boundary_mode": "LATER_AFTER_WICKET", "boundary_allowance": 4},
       ("contact", "completed_runs", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "dead_before_wicket", "boundary_mode", "boundary_allowance"), "dead_before_wicket", True,
       ("DEAD_SEQUENCE", "RUNOUT_TEST", "APPEAL", "BOUNDARY_NORMAL", "BAT_CREDIT"), (1, 1, 3, 0, 1)),
    _t("L3_OVERTHROW_CROSS", "L3",
       {"contact": "BAT", "completed_runs": 2, "crossed_at_throw": True, "boundary_mode": "OVERTHROW", "boundary_allowance": 4},
       ("contact", "completed_runs", "crossed_at_throw", "boundary_mode", "boundary_allowance"), "crossed_at_throw", False,
       ("OVERTHROW", "BAT_CREDIT", "BOWLER_DEBIT", "LEGAL_COUNT"), (1, 1, 3, 0, 1)),
    _t("L3_NB_KEEPER_EXCEPTION", "L3",
       {"no_ball_called": False, "contact": "NONE", "dismissal_candidate": "STUMPED_OR_RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "attempting_run": False, "keeper_only": True},
       ("no_ball_called", "contact", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "attempting_run", "keeper_only"), "no_ball_called", True,
       ("NB_DISMISSAL_GATE", "NB_KEEPER_RUNOUT_EXCEPTION", "RUNOUT_TEST", "APPEAL", "NB_SCORE"), (1, 1, 3, 0, 1)),

    # L4: same cricket operators, plus a version/scope decision in the dossier.
    _t("L4_REVIEW_NB_OVER_WIDE", "L4",
       {"no_ball_called": True, "wide_called": True, "contact": "BAT", "completed_runs": 1},
       ("no_ball_called", "wide_called", "contact", "completed_runs"), "no_ball_called", False,
       ("NB_PRECEDENCE", "NB_COUNT", "NB_SCORE", "WIDE_CONTACT", "BAT_CREDIT", "BOWLER_DEBIT"), (2, 1, 4, 1, 2)),
    _t("L4_REVIEW_CATCH_CONTROL", "L4",
       {"contact": "BAT", "dismissal_candidate": "CAUGHT", "appeal_made": True, "appeal_in_time": True, "catch_complete": True, "ball_grounded_before_control": False, "boundary_contact_before_completion": False, "boundary_mode": "NORMAL", "boundary_allowance": 4},
       ("contact", "dismissal_candidate", "appeal_made", "appeal_in_time", "catch_complete", "ball_grounded_before_control", "boundary_contact_before_completion", "boundary_mode", "boundary_allowance"), "boundary_contact_before_completion", True,
       ("CAUGHT_CONTROL", "BOUNDARY_NORMAL", "BAT_CREDIT", "APPEAL"), (2, 1, 3, 1, 2)),
    _t("L4_REVIEW_OVERTHROW", "L4",
       {"contact": "BAT", "completed_runs": 2, "crossed_at_throw": True, "boundary_mode": "OVERTHROW", "boundary_allowance": 4},
       ("contact", "completed_runs", "crossed_at_throw", "boundary_mode", "boundary_allowance"), "completed_runs", 1,
       ("OVERTHROW", "BAT_CREDIT", "BOWLER_DEBIT"), (2, 1, 3, 1, 2)),
    _t("L4_REVIEW_DEAD_SEQUENCE", "L4",
       {"contact": "BAT", "completed_runs": 1, "dismissal_candidate": "RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "dead_before_wicket": False, "boundary_mode": "LATER_AFTER_WICKET", "boundary_allowance": 4},
       ("contact", "completed_runs", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "dead_before_wicket", "boundary_mode", "boundary_allowance"), "dead_before_wicket", True,
       ("DEAD_SEQUENCE", "RUNOUT_TEST", "BOUNDARY_NORMAL", "APPEAL"), (2, 1, 3, 1, 2)),
    _t("L4_REVIEW_WIDE_STUMP", "L4",
       {"wide_called": True, "contact": "NONE", "dismissal_candidate": "STUMPED_OR_RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "attempting_run": False, "keeper_only": True},
       ("wide_called", "contact", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "attempting_run", "keeper_only"), "keeper_only", False,
       ("WIDE_DISMISSAL_GATE", "STUMPED_TEST", "RUNOUT_TEST", "APPEAL"), (2, 1, 3, 1, 2)),

    # L5: multi-operator ledgers with an isomorphic shadow case.
    _t("L5_NB_OVERTHROW", "L5",
       {"no_ball_called": True, "contact": "BAT", "completed_runs": 1, "crossed_at_throw": True, "boundary_mode": "OVERTHROW", "boundary_allowance": 4},
       ("no_ball_called", "contact", "completed_runs", "crossed_at_throw", "boundary_mode", "boundary_allowance"), "crossed_at_throw", False,
       ("NB_COUNT", "NB_SCORE", "OVERTHROW", "BAT_CREDIT", "BOWLER_DEBIT"), (2, 2, 4, 1, 3)),
    _t("L5_NB_DECEPTION", "L5",
       {"no_ball_called": True, "contact": "BAT", "completed_runs": 1, "wilful_deception": False, "dismissal_candidate": "RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True},
       ("no_ball_called", "contact", "completed_runs", "wilful_deception", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground"), "wilful_deception", True,
       ("NB_COUNT", "NB_SCORE", "DECEPTION", "RUNOUT_TEST", "BAT_CREDIT", "BOWLER_DEBIT"), (2, 2, 4, 1, 3)),
    _t("L5_NB_WIDE_CONTACT_OVERTHROW", "L5",
       {"no_ball_called": True, "wide_called": True, "contact": "BAT", "completed_runs": 2, "crossed_at_throw": True, "boundary_mode": "OVERTHROW", "boundary_allowance": 4},
       ("no_ball_called", "wide_called", "contact", "completed_runs", "crossed_at_throw", "boundary_mode", "boundary_allowance"), "contact", "NONE",
       ("NB_PRECEDENCE", "NB_COUNT", "NB_SCORE", "OVERTHROW", "BAT_CREDIT", "BOWLER_DEBIT"), (2, 2, 4, 1, 3)),
    _t("L5_RUNOUT_LATER_BOUNDARY", "L5",
       {"contact": "BAT", "completed_runs": 1, "dismissal_candidate": "RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "dead_before_wicket": False, "boundary_mode": "LATER_AFTER_WICKET", "boundary_allowance": 4},
       ("contact", "completed_runs", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "dead_before_wicket", "boundary_mode", "boundary_allowance"), "wicket_fair", False,
       ("RUNOUT_TEST", "DEAD_SEQUENCE", "BOUNDARY_NORMAL", "BAT_CREDIT", "APPEAL", "BOWLER_DEBIT"), (2, 2, 4, 1, 3)),
    _t("L5_WIDE_STUMP_REVIEW", "L5",
       {"wide_called": True, "contact": "NONE", "dismissal_candidate": "STUMPED_OR_RUN_OUT", "appeal_made": True, "appeal_in_time": True, "wicket_fair": True, "out_of_ground": True, "attempting_run": False, "keeper_only": True},
       ("wide_called", "contact", "dismissal_candidate", "appeal_made", "appeal_in_time", "wicket_fair", "out_of_ground", "attempting_run", "keeper_only"), "out_of_ground", False,
       ("WIDE_COUNT", "WIDE_SCORE", "WIDE_DISMISSAL_GATE", "STUMPED_TEST", "APPEAL"), (2, 2, 4, 1, 3)),
)


SCENARIOS_BY_LEVEL = {
    level: tuple(item for item in SCENARIOS if item.level == level)
    for level in ("L1", "L2", "L3", "L4", "L5")
}

if any(len(items) != 5 for items in SCENARIOS_BY_LEVEL.values()):
    raise RuntimeError("R25 requires five scenario families per level")

for scenario in SCENARIOS:
    factual, _, counterfactual = scenario.records()
    if factual == counterfactual:
        raise RuntimeError(f"counterfactual does not change output: {scenario.family_id}")
    unknown = set(scenario.rule_keys) - set(RULE_TEXT)
    if unknown:
        raise RuntimeError(f"unknown rule keys for {scenario.family_id}: {unknown}")


__all__ = ["RULE_TEXT", "SCENARIOS", "SCENARIOS_BY_LEVEL", "ScenarioTemplate"]
