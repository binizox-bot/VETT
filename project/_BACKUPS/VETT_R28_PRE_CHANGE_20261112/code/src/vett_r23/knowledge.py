from __future__ import annotations

from typing import Any

from .spec import RULESET


def _card(
    rule_id: str,
    level: str,
    law_reference: str,
    source_pages: str,
    question: str,
    answer_code: str,
    answer_choices: list[str],
    required_atoms: list[str],
    distractor_atoms: list[str],
    embedded_fragments: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "level": level,
        "law_reference": law_reference,
        "source_pages": source_pages,
        "source_url": RULESET["source_url"],
        "question": question,
        "answer_code": answer_code,
        "answer_choices": answer_choices,
        "required_atoms": required_atoms,
        "reasoning_atom_choices": required_atoms + distractor_atoms,
        "embedded_fragments": embedded_fragments,
    }


RULE_CARDS = (
    _card(
        "no_ball_over_count",
        "L1",
        "Law 21.16",
        "pp. 74-75",
        "In the MCC 2026 Laws, does a called No ball count as one of the balls in the over?",
        "DOES_NOT_COUNT",
        ["COUNTS", "DOES_NOT_COUNT", "COUNTS_ONLY_IF_NO_RUN"],
        ["NO_BALL_IS_NOT_A_VALID_BALL_OF_THE_OVER"],
        ["NO_BALL_ALWAYS_ENDS_PLAY", "NO_BALL_COUNTS_IF_STRUCK"],
        [{"role": "decisive", "text": "The scorers' over audit says that a delivery called No ball is excluded from the six valid balls, even when play continues and runs result."}],
    ),
    _card(
        "wide_over_count",
        "L1",
        "Law 22.8",
        "pp. 76-77",
        "In the MCC 2026 Laws, does a called Wide count as one of the balls in the over?",
        "DOES_NOT_COUNT",
        ["COUNTS", "DOES_NOT_COUNT", "COUNTS_AFTER_A_RUN"],
        ["WIDE_IS_NOT_A_VALID_BALL_OF_THE_OVER"],
        ["WIDE_IMMEDIATELY_MAKES_BALL_DEAD", "WIDE_COUNTS_IF_NOT_RUN"],
        [{"role": "decisive", "text": "The technical scorer retained the same ball number after a Wide because that call did not supply a valid ball of the over."}],
    ),
    _card(
        "no_ball_overrides_wide",
        "L2",
        "Laws 21.12 and 22.3.2",
        "pp. 74-76",
        "A delivery appears to satisfy both No ball and Wide conditions. Which call governs under the MCC 2026 Laws?",
        "NO_BALL_OVERRIDES_WIDE",
        ["BOTH_CALLS_STAND", "WIDE_OVERRIDES_NO_BALL", "NO_BALL_OVERRIDES_WIDE"],
        ["NO_BALL_HAS_PRECEDENCE", "WIDE_CALL_IS_REVOKED"],
        ["BOTH_PENALTIES_ARE_ADDED", "EARLIER_SIGNAL_HAS_PRECEDENCE"],
        [
            {"role": "decisive", "text": "A laws-desk note records that the delivery first appeared wide of the striker and was signalled Wide."},
            {"role": "decisive", "text": "The subsequent No ball call took precedence, so the earlier Wide signal was revoked rather than accumulated."},
        ],
    ),
    _card(
        "no_ball_penalty",
        "L2",
        "Law 21.14",
        "pp. 74-75",
        "What immediate penalty follows a called No ball, before adding other completed runs or boundary allowances?",
        "ONE_RUN_PLUS_OTHER_RUNS",
        ["ONE_RUN_PLUS_OTHER_RUNS", "FIVE_RUNS_ONLY", "NO_AUTOMATIC_RUN"],
        ["ONE_RUN_PENALTY", "PENALTY_ADDED_TO_OTHER_SCORING"],
        ["PENALTY_REPLACES_ALL_OTHER_RUNS", "PENALTY_DEPENDS_ON_DISMISSAL"],
        [
            {"role": "decisive", "text": "The scoring review begins a called No ball with a one-run penalty."},
            {"role": "decisive", "text": "Its remaining entry is then added from completed runs or a boundary allowance; the automatic run does not replace that scoring."},
        ],
    ),
    _card(
        "no_ball_dismissal_exceptions",
        "L3",
        "Law 21.17",
        "pp. 74-75",
        "Which answer lists all dismissal modes that may still apply after No ball has been called?",
        "HIT_BALL_TWICE|OBSTRUCTING_FIELD|RUN_OUT",
        [
            "HIT_BALL_TWICE|OBSTRUCTING_FIELD|RUN_OUT",
            "BOWLED|RUN_OUT|STUMPED",
            "HIT_WICKET|OBSTRUCTING_FIELD|STUMPED",
        ],
        ["NO_BALL_LIMITS_DISMISSAL_SET", "RUN_OUT_REMAINS_AVAILABLE"],
        ["BOWLED_REMAINS_AVAILABLE", "STUMPED_REMAINS_AVAILABLE"],
        [
            {"role": "decisive", "text": "After the No ball call, the review struck out Bowled, Caught, LBW, Stumped and Hit wicket as possible dismissals for that delivery."},
            {"role": "decisive", "text": "The surviving dismissal routes in the case note were Run out, Obstructing the field and Hit the ball twice."},
        ],
    ),
    _card(
        "wide_dismissal_exceptions",
        "L3",
        "Law 22.9",
        "pp. 76-77",
        "Which answer lists all dismissal modes that may still apply after Wide has been called?",
        "HIT_WICKET|OBSTRUCTING_FIELD|RUN_OUT|STUMPED",
        [
            "HIT_WICKET|OBSTRUCTING_FIELD|RUN_OUT|STUMPED",
            "BOWLED|CAUGHT|LBW|RUN_OUT",
            "HIT_BALL_TWICE|OBSTRUCTING_FIELD|RUN_OUT",
        ],
        ["WIDE_LIMITS_DISMISSAL_SET", "STUMPED_REMAINS_AVAILABLE"],
        ["BOWLED_REMAINS_AVAILABLE", "CAUGHT_REMAINS_AVAILABLE"],
        [
            {"role": "decisive", "text": "Once Wide was confirmed, the review rejected Bowled, Caught, LBW and Hit the ball twice for that delivery."},
            {"role": "decisive", "text": "It retained Hit wicket, Obstructing the field, Run out and Stumped as the applicable dismissal routes."},
        ],
    ),
    _card(
        "no_ball_bat_boundary_four",
        "L4",
        "Laws 21.14-21.15",
        "pp. 74-75",
        "A No ball is struck by the bat and reaches the boundary for four, with no other penalty. How is the delivery recorded?",
        "TOTAL_5|BATTER_4|NO_BALL_EXTRA_1",
        [
            "TOTAL_5|BATTER_4|NO_BALL_EXTRA_1",
            "TOTAL_4|BATTER_4|NO_BALL_EXTRA_0",
            "TOTAL_5|BATTER_0|NO_BALL_EXTRA_5",
        ],
        ["ADD_NO_BALL_PENALTY", "CREDIT_BAT_BOUNDARY_TO_STRIKER"],
        ["CREDIT_ALL_RUNS_AS_NO_BALL_EXTRAS", "IGNORE_BOUNDARY_ALLOWANCE"],
        [
            {"role": "misleading", "text": "A broadcast margin note treated the struck No ball boundary as four runs in total and assigned no separate No ball extra."},
            {"role": "decisive", "text": "The authorised scoring correction credited four boundary runs to the striker and added the one-run No ball penalty, producing five from the delivery."},
        ],
    ),
    _card(
        "wide_boundary_scoring",
        "L4",
        "Laws 22.6-22.7",
        "pp. 76-77",
        "An untouched Wide reaches the boundary, with no other penalty. How is the five-run total classified?",
        "TOTAL_5|ALL_WIDES|BOWLER_DEBIT_5",
        [
            "TOTAL_5|ALL_WIDES|BOWLER_DEBIT_5",
            "TOTAL_5|BYE_4|WIDE_1",
            "TOTAL_4|ALL_WIDES|BOWLER_DEBIT_4",
        ],
        ["WIDE_PENALTY_PLUS_BOUNDARY", "ALL_RESULTING_RUNS_ARE_WIDES", "DEBIT_BOWLER"],
        ["BOUNDARY_IS_BYES", "ONLY_ONE_RUN_DEBITED_TO_BOWLER"],
        [
            {"role": "misleading", "text": "The first commentary return split the untouched Wide boundary into one Wide and four Byes."},
            {"role": "decisive", "text": "The scoring desk rejected that split: all five were recorded as Wides and all five were charged against the bowler."},
        ],
    ),
    _card(
        "deliberate_short_run",
        "L5",
        "Law 18.5.2",
        "pp. 52-53",
        "An umpire judges that a batter deliberately ran short. Ignoring unrelated penalties, what scoring consequence follows?",
        "DISALLOW_BATTING_RUNS|FIELDING_PENALTY_5",
        [
            "DISALLOW_BATTING_RUNS|FIELDING_PENALTY_5",
            "REMOVE_ONE_RUN_ONLY|NO_PENALTY",
            "ALLOW_COMPLETED_RUNS|BATTING_PENALTY_5",
        ],
        ["DISALLOW_ALL_BATTING_RUNS", "AWARD_FIVE_TO_FIELDING_SIDE"],
        ["DISALLOW_ONLY_SHORT_RUN", "AWARD_FIVE_TO_BATTING_SIDE"],
        [
            {"role": "misleading", "text": "A commentator argued that only the visibly short run should be removed and that no further consequence followed."},
            {"role": "decisive", "text": "The umpire's final finding was deliberate short running, so the special deliberate-short procedure—not ordinary accidental short-run treatment—governs the ledger."},
        ],
    ),
    _card(
        "leg_bye_no_attempt",
        "L5",
        "Laws 23.2.1 and 23.3",
        "pp. 76-78",
        "The ball hits the striker, who neither attempts a shot nor tries to avoid being hit. Can completed runs be awarded as Leg byes?",
        "NO_LEG_BYES|DISALLOW_BATTING_RUNS",
        [
            "NO_LEG_BYES|DISALLOW_BATTING_RUNS",
            "LEG_BYES_ALLOWED|COUNT_ALL_RUNS",
            "BYE_RUNS_ALLOWED|COUNT_BOUNDARY_ONLY",
        ],
        ["SHOT_OR_AVOIDANCE_REQUIRED", "LEG_BYE_CONDITIONS_FAIL", "DISALLOW_BATTING_RUNS"],
        ["CONTACT_AUTOMATICALLY_CREATES_LEG_BYES", "RUNNING_OVERRIDES_LEG_BYE_CONDITION"],
        [
            {"role": "misleading", "text": "The live note labelled the completed running as Leg byes merely because the ball had touched the striker."},
            {"role": "decisive", "text": "Replay review established that the striker neither attempted a shot nor tried to avoid being hit; the provisional Leg-bye label therefore remained subject to the Law 23 eligibility test."},
        ],
    ),
)

RULE_CARDS_BY_ID = {card["rule_id"]: card for card in RULE_CARDS}


__all__ = ["RULE_CARDS", "RULE_CARDS_BY_ID"]
