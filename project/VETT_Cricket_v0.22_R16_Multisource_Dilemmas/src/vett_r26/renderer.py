from __future__ import annotations

from typing import Any

from vett_r25.scenarios import RULE_TEXT

from .scenario_kernel import NaturalIdentity, digest


_SOURCE_ALIAS_PAIRS = (
    ("north-pavilion worksheet", "river-end worksheet"),
    ("blue-tab scorer copy", "amber-tab scorer copy"),
    ("oak-folder entry", "ash-folder entry"),
    ("members-end review leaf", "nursery-end review leaf"),
    ("upper-desk register note", "lower-desk register note"),
    ("green-jacket folio", "maroon-jacket folio"),
    ("clock-room copy", "signal-room copy"),
    ("west-cabinet sheet", "east-cabinet sheet"),
    ("square-leg file note", "pavilion file note"),
    ("bound ledger extract", "loose-leaf ledger extract"),
)


def source_aliases(question_id: str) -> tuple[str, str]:
    pair = _SOURCE_ALIAS_PAIRS[
        int(digest(question_id, "source-alias-pair")[:8], 16) % len(_SOURCE_ALIAS_PAIRS)
    ]
    if int(digest(question_id, "source-alias-order")[:8], 16) % 2:
        return pair[1], pair[0]
    return pair


def fact_clause(field: str, value: Any) -> str:
    boolean = {
        "no_ball_called": ("the bowler's-end umpire signalled No ball", "no No-ball signal was made"),
        "wide_called": ("the striker's-end umpire signalled Wide", "no Wide signal was made"),
        "early_dead_reball": (
            "Dead ball was called before the striker had an opportunity to play",
            "there was no early Dead-ball interruption",
        ),
        "crossed_at_throw": (
            "the batters had crossed when the throw left the fielder",
            "the batters had not crossed when the throw left the fielder",
        ),
        "appeal_made": ("the fielding side appealed", "the fielding side did not appeal"),
        "appeal_in_time": (
            "the appeal came before the next run-up and before Time was called",
            "the appeal came only after the next run-up or the call of Time",
        ),
        "wicket_broken_by_delivery": (
            "the delivered ball broke the striker's wicket",
            "the delivered ball did not break the striker's wicket",
        ),
        "lbw_pitch_valid": (
            "the pitching point met the LBW condition",
            "the ball pitched outside the line of leg stump",
        ),
        "lbw_impact_valid": (
            "the interception point met the applicable LBW condition",
            "the interception point failed the applicable LBW condition",
        ),
        "lbw_would_hit_wicket": (
            "the tracked path would have hit the wicket",
            "the tracked path would have missed the wicket",
        ),
        "wicket_fair": ("the wicket was put down fairly", "the wicket was not put down fairly"),
        "out_of_ground": ("the batter was out of ground", "the batter had made ground"),
        "dead_before_wicket": (
            "the ball was already dead when the wicket was broken",
            "the ball was still in play when the wicket was broken",
        ),
        "attempting_run": (
            "the striker was attempting a run",
            "the striker was not attempting a run",
        ),
        "keeper_only": (
            "the wicket-keeper alone put down the wicket",
            "another fielder took part in putting down the wicket",
        ),
        "catch_complete": (
            "the fielder ultimately controlled both ball and movement",
            "the fielder never controlled both ball and movement",
        ),
        "ball_grounded_before_control": (
            "the ball touched the ground before control was complete",
            "the ball did not touch the ground before control was complete",
        ),
        "boundary_contact_before_completion": (
            "the fielder touched the boundary before control was complete",
            "there was no boundary contact before control was complete",
        ),
        "wilful_deception": (
            "a fielder wilfully deceived a batter after the striker received the ball",
            "no fielder wilfully deceived either batter after receipt",
        ),
        "award_run_in_progress": (
            "the applicable award included the run in progress",
            "no award included the run in progress",
        ),
    }
    if field in boolean:
        return boolean[field][0 if bool(value) else 1]
    if field == "contact":
        return {
            "BAT": "the ball touched the striker's bat",
            "PERSON": "the ball first touched the striker's person and not the bat",
            "NONE": "the ball touched neither bat nor person",
        }[str(value)]
    if field == "completed_runs":
        return f"{int(value)} completed run{'s' if int(value) != 1 else ''} preceded the terminal event"
    if field == "boundary_mode":
        return {
            "NORMAL": "the boundary came directly from the delivery and not from an overthrow",
            "OVERTHROW": "the boundary resulted from a fielder's throw at the wicket",
            "LATER_AFTER_WICKET": "the loose ball reached the boundary only after the wicket event",
            "NONE": "no boundary occurred",
        }[str(value)]
    if field == "boundary_allowance":
        return f"the agreed boundary allowance was {int(value)} runs"
    if field == "dismissal_candidate":
        return {
            "BOWLED": "the wicket event was submitted as Bowled",
            "LBW": "the wicket event was submitted as LBW",
            "CAUGHT": "the wicket event was submitted as Caught",
            "RUN_OUT": "the wicket event was submitted as Run out",
            "STUMPED_OR_RUN_OUT": "the wicket event required a choice between Stumped and Run out",
            "NONE": "no dismissal was submitted",
        }[str(value)]
    if field == "penalty_runs_batting":
        return f"the batting side received {int(value)} separate penalty runs"
    raise KeyError(f"no R26 renderer for fact field {field}")


def bridge_text(
    source: str,
    target: str,
    *,
    hop: int,
    identity: NaturalIdentity,
    authority_contract: str | None = None,
    naturalized_v2: bool = False,
) -> str:
    frames = (
        "The match-control index cross-references {source} as {target}.",
        "In the commentary reconciliation, {source} is the same delivery as {target}.",
        "The scorer's routing note files {source} under {target}.",
        "The review register links {source} to {target}; the two phrases are not separate incidents.",
        "The pre-lock index carries {source} forward as {target}.",
        "The pavilion concordance lists {source} and {target} as two headings for one delivery.",
        "A margin entry in the reconciliation directs {source} to the record headed {target}.",
        "The officials' cross-reference pairs {source} with {target} for the same ball.",
        "In the scorer's filing trail, the entry called {source} continues under {target}.",
        "The innings register says that references to {source} resolve to {target}.",
        "The review clerk indexed {source} against {target}, treating both as one incident.",
        "The delivery concordance maps the wording {source} to the filing label {target}.",
    )
    frame_index = int(digest(identity.target_description, source, target, hop, "bridge-frame")[:8], 16)
    selected = frames[frame_index % len(frames)]
    if naturalized_v2:
        if selected == frames[6]:
            selected = 'A margin entry in the reconciliation links "{source}" to the record headed "{target}".'
        elif selected == frames[11]:
            selected = 'The delivery concordance maps the wording "{source}" to the filing label "{target}".'
    text = selected.format(source=source, target=target)
    if authority_contract:
        text += " " + authority_contract
    return text


def authority_contract(active_source: str, *, key: str = "") -> str:
    accepted_source, rejected_source = source_aliases(key)
    if active_source == "HIGHEST_REVISION":
        frames = (
            "The {accepted} is signed revision 9 and controls the {rejected}, signed revision 2, for this observation.",
            "Where these copies disagree, the {accepted} carries signed revision 9 and controls the {rejected} at signed revision 2.",
            "Revision metadata assigns 9 to the {accepted}, which controls the {rejected} marked revision 2.",
            "The {accepted} is the greatest signed revision, number 9, and controls the {rejected}, number 2.",
            "For this delivery, signed revision 9 is the {accepted}; it controls the {rejected}, which is signed revision 2.",
        )
    elif active_source == "LAST_PRE_LOCK":
        frames = (
            "The {accepted} was signed at 18:22 and controls; the {rejected} was filed at 18:29, after the 18:25 review lock.",
            "For the 18:25 lock, the {accepted} is the last signed pre-lock entry at 18:22 and controls the 18:29 {rejected}.",
            "Timing metadata places the {accepted} at 18:22, so it controls; the {rejected} at 18:29 belongs to the next cycle after the 18:25 lock.",
            "The {accepted}, signed at 18:22, controls this cycle rather than the {rejected}, filed after the 18:25 lock at 18:29.",
            "At the 18:25 cut-off the {accepted} is the latest signed entry, timestamped 18:22, and controls the later {rejected}.",
        )
    else:
        frames = (
            "For this incident, the {accepted} is the signed on-field observation and controls the {rejected}, an unsigned scorer-feed copy.",
            "The source register identifies the {accepted} as the signed field observation; it controls the unsigned {rejected} for this delivery.",
            "Here the {accepted} carries the on-field signature and controls the {rejected}, which came from the unsigned live feed.",
            "For this ball, the signed on-field source is the {accepted}; it controls the contradictory unsigned {rejected}.",
            "Source priority maps the {accepted} to the signed field observation, which controls the inconsistent unsigned {rejected}.",
        )
    frame = frames[int(digest(active_source, key, "authority-contract")[:8], 16) % len(frames)]
    return frame.format(accepted=accepted_source, rejected=rejected_source)


def authority_policy_text(subject: str, active_source: str, *, question_id: str) -> str:
    frames = (
        "The incident-specific source protocol for {subject} states: {contract}",
        "A source-priority note attached to {subject} provides: {contract}",
        "For {subject}, the review clerk recorded this controlling-source instruction: {contract}",
        "The match file places the following source rule beside {subject}: {contract}",
        "The reconciliation cover sheet for {subject} specifies: {contract}",
        "An authority note indexed to {subject} reads: {contract}",
        "The scorers' source register assigns this rule to {subject}: {contract}",
        "Beside {subject}, the signed review index gives the following priority rule: {contract}",
    )
    contract = authority_contract(active_source, key=question_id)
    index = int(digest(question_id, subject, "authority-policy-frame")[:8], 16) % len(frames)
    return frames[index].format(subject=subject, contract=contract)


def conflict_text(
    subject: str,
    field: str,
    value: Any,
    *,
    active_source: str,
    question_id: str,
    naturalized_v2: bool = False,
) -> str:
    _, rejected_source = source_aliases(question_id)
    return _source_fact_text(
        rejected_source,
        subject,
        fact_clause(field, value),
        question_id=question_id,
        field=field,
        naturalized_v2=naturalized_v2,
    )


def _source_fact_text(
    source: str,
    subject: str,
    clause: str,
    *,
    question_id: str,
    field: str,
    naturalized_v2: bool = False,
) -> str:
    frames = (
        "The {source} for {subject} records that {clause}.",
        "Under {subject}, the {source} reports that {clause}.",
        "The entry in the {source} says of {subject} that {clause}.",
        "For {subject}, the {source} contains the statement that {clause}.",
        "The {source} describes {subject} as an incident where {clause}.",
        "Filed against {subject}, the {source} states that {clause}.",
        "The account headed {source} notes for {subject} that {clause}.",
        "In the {source}, the line for {subject} reads that {clause}.",
    )
    index = int(digest(question_id, field, source, "neutral-source-fact-frame")[:8], 16) % len(frames)
    if naturalized_v2:
        frames = (
            "According to the {source}, the record for {subject} states that {clause}.",
            "Under {subject}, the {source} reports that {clause}.",
            "The {source} records that, for {subject}, {clause}.",
            "For {subject}, the {source} contains the statement that {clause}.",
            "The {source} records {subject} as an incident in which {clause}.",
            "Filed against {subject}, the {source} states that {clause}.",
            "On the {source}, the record for {subject} states that {clause}.",
            "In the {source}, the line for {subject} reads that {clause}.",
        )
    return frames[index].format(source=source, subject=subject, clause=clause)


def fact_text(
    subject: str,
    field: str,
    value: Any,
    *,
    question_id: str,
    shadow: bool = False,
    active_source: str = "DIRECT_OBSERVATION",
    naturalized_v2: bool = False,
) -> str:
    if not shadow:
        accepted_source, _ = source_aliases(question_id)
        return _source_fact_text(
            accepted_source,
            subject,
            fact_clause(field, value),
            question_id=question_id,
            field=field,
            naturalized_v2=naturalized_v2,
        )
    frames = (
        "The umpire signal sheet for {subject} records that {clause}.",
        "In the ball-by-ball reconciliation for {subject}, the scorer notes that {clause}.",
        "The review-room audio log for {subject} confirms that {clause}.",
        "The signed delivery worksheet for {subject} states that {clause}.",
        "The innings-control note attached to {subject} records that {clause}.",
        "A delivery annotation indexed to {subject} reports that {clause}.",
        "The working scorer sheet describes {subject} as an incident where {clause}.",
        "An auxiliary review note for {subject} says that {clause}.",
    )
    offset = 2 if shadow else 0
    frame = frames[(int(digest(question_id, field, "shadow" if shadow else "fact")[:4], 16) + offset) % len(frames)]
    return frame.format(subject=subject, clause=fact_clause(field, value))


def rule_text(rule_key: str, *, match_id: str) -> str:
    frames = (
        "The scorer's 2026 law notebook gives this instruction: {rule}",
        "For this match, the officials' law digest reproduces the following 2026 provision: {rule}",
        "The match-control rules sheet states: {rule}",
        "A 2026 law extract in the scorers' folder provides: {rule}",
        "The officials' match copy of the Laws notes: {rule}",
        "The rules reference used for this innings reads: {rule}",
    )
    return frames[int(digest(match_id, rule_key, "rule-frame")[:4], 16) % len(frames)].format(
        rule=RULE_TEXT[rule_key]
    )


def question_text(identity: NaturalIdentity, intervention_field: str, intervention_value: Any) -> str:
    return (
        f"Resolve {identity.target_description}. The dossier contains all recorded calls, contacts, running, "
        "boundaries, penalties, appeals and wicket events needed for this incident. Do not borrow an observation "
        "from a similar delivery. Return the normalized decision record, requested latent state and smallest "
        "sufficient evidence set. Then change only the active observation so that "
        f"{fact_clause(intervention_field, intervention_value)}; preserve every other resolved fact and source "
        "selection, and recompute the counterfactual record and state."
    )


__all__ = [
    "authority_contract", "authority_policy_text", "bridge_text", "conflict_text",
    "fact_clause", "fact_text", "question_text", "rule_text", "source_aliases",
]
