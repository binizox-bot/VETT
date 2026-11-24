"""Neutral prose rendering: identities, fact clauses, documents, question, schema.

Everything here is a pure function of the question id and the frozen seed, so the
two arms share byte-identical question text, output schema and ruleset while the
dossier itself carries the (manipulated) presentation layer.

No text may mention a dose, a mechanism, a level, a family or a difficulty word,
and no label may encode the answer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .canonical import canon, digest, estimate_tokens

RULESET = {
    "ruleset_id": "R28-CRICKET-LAWS-2026",
    "title": "2026 Laws of Cricket, scoring extracts used by the match control",
    "effective_date": "2026-01-01",
}

FORBIDDEN_PUBLIC_MARKERS = (
    "correct answer",
    "gold answer",
    "gold record",
    "distractor",
    "misleading",
    "non-authoritative",
    "ignore this",
    "difficulty",
    "dose",
    "level",
    "hard",
    "shallow",
    "case-",
    "pkt-",
    "obs-",
    "variant",
)

_TOKEN_PREFIXES = ("review token RV", "dossier packet DP", "scorer leaf SF",
                   "register slip RS", "folio entry FE", "ledger cell LC")


def _hex(question_id: str, salt: str, length: int = 4) -> str:
    return digest(question_id, salt)[:length].upper()


def token(question_id: str, salt: str, prefix_index: int) -> str:
    prefix = _TOKEN_PREFIXES[prefix_index % len(_TOKEN_PREFIXES)]
    return f"{prefix}-{_hex(question_id, salt)}"


@dataclass(frozen=True)
class Identity:
    """Neutral identity chain from the question's target to the fact-bearing label."""

    head: str
    chain: tuple[str, ...]
    over_number: int
    venue: str

    @property
    def terminal(self) -> str:
        return self.chain[-1]

    @property
    def hops(self) -> int:
        return len(self.chain) - 1

    def labels(self) -> dict[str, Any]:
        return {
            "head": self.head,
            "chain": list(self.chain),
            "terminal": self.terminal,
            "hops": self.hops,
            "over_number": self.over_number,
            "venue": self.venue,
        }


def build_identity(question_id: str, *, d1_level: int, seed: int) -> Identity:
    """Build the identity chain; ``d1_level`` equals the number of hops."""

    over_number = 3 + int(digest(seed, question_id, "over")[:4], 16) % 44
    venues = ("the north ground", "the river ground", "the college ground",
              "the old racecourse ground", "the harbour ground")
    venue = venues[int(digest(question_id, "venue")[:4], 16) % len(venues)]
    head = token(question_id, "head", 0)
    mid = token(question_id, "mid", 1)
    terminal = token(question_id, "terminal", 2)
    if d1_level == 0:
        chain = (head,)
    elif d1_level == 1:
        chain = (head, terminal)
    elif d1_level == 2:
        chain = (head, mid, terminal)
    else:
        raise ValueError(f"unsupported D1 level: {d1_level}")
    return Identity(head=head, chain=chain, over_number=over_number, venue=venue)


# ---------------------------------------------------------------------------
# Fact clauses (one sentence fragment per fact field/value)
# ---------------------------------------------------------------------------
_BOOLEAN_CLAUSES: dict[str, tuple[str, str]] = {
    "no_ball_called": ("the bowler's-end umpire signalled No ball",
                       "no No-ball signal was given"),
    "wide_called": ("the striker's-end umpire signalled Wide",
                    "no Wide signal was given"),
    "early_dead_reball": ("Dead ball was called before the striker could play",
                          "no early Dead-ball interruption occurred"),
    "crossed_at_throw": ("the batters had crossed when the throw left the fielder",
                         "the batters had not crossed when the throw left the fielder"),
    "appeal_made": ("the fielding side appealed", "the fielding side did not appeal"),
    "appeal_in_time": ("the appeal came before the next run-up and before Time",
                       "the appeal came only after the next run-up or the call of Time"),
    "wicket_broken_by_delivery": ("the delivered ball broke the striker's wicket",
                                  "the delivered ball did not break the striker's wicket"),
    "lbw_pitch_valid": ("the pitching point met the LBW condition",
                        "the ball pitched outside the line of leg stump"),
    "lbw_impact_valid": ("the interception point met the applicable LBW condition",
                         "the interception point failed the applicable LBW condition"),
    "lbw_would_hit_wicket": ("the tracked path would have hit the wicket",
                             "the tracked path would have missed the wicket"),
    "wicket_fair": ("the wicket was put down fairly", "the wicket was not put down fairly"),
    "out_of_ground": ("the batter was out of ground", "the batter had made ground"),
    "dead_before_wicket": ("the ball was already dead when the wicket was broken",
                           "the ball was still in play when the wicket was broken"),
    "attempting_run": ("the striker was attempting a run", "the striker was not attempting a run"),
    "keeper_only": ("the wicket-keeper alone put down the wicket",
                    "another fielder took part in putting down the wicket"),
    "catch_complete": ("the fielder ultimately controlled both ball and movement",
                       "the fielder never controlled both ball and movement"),
    "ball_grounded_before_control": ("the ball touched the ground before control was complete",
                                     "the ball did not touch the ground before control was complete"),
    "boundary_contact_before_completion": (
        "the fielder touched the boundary before control was complete",
        "there was no boundary contact before control was complete",
    ),
    "wilful_deception": ("a fielder wilfully deceived a batter after the striker received the ball",
                         "no fielder wilfully deceived either batter after receipt"),
    "award_run_in_progress": ("the applicable award included the run in progress",
                              "no award included the run in progress"),
    "forced_not_count": ("the review sheet flags this delivery as not counting in the over",
                         "nothing on the review sheet removes this delivery from the over"),
}

_CONTACT_CLAUSES = {
    "BAT": "the ball touched the striker's bat",
    "PERSON": "the ball first touched the striker's person and not the bat",
    "NONE": "the ball touched neither bat nor person",
}

_BOUNDARY_CLAUSES = {
    "NORMAL": "the boundary came directly from the delivery and not from an overthrow",
    "OVERTHROW": "the boundary resulted from a fielder's throw at the wicket",
    "LATER_AFTER_WICKET": "the loose ball reached the boundary only after the wicket event",
    "NONE": "no boundary occurred",
}

_DISMISSAL_CLAUSES = {
    "BOWLED": "the wicket event was submitted as Bowled",
    "LBW": "the wicket event was submitted as LBW",
    "CAUGHT": "the wicket event was submitted as Caught",
    "RUN_OUT": "the wicket event was submitted as Run out",
    "STUMPED_OR_RUN_OUT": "the wicket event required a choice between Stumped and Run out",
    "OBSTRUCTING_FIELD": "the wicket event was submitted as Obstructing the field",
    "HIT_BALL_TWICE": "the wicket event was submitted as Hit the ball twice",
    "NONE": "no dismissal was submitted",
}


def fact_clause(field_name: str, value: Any) -> str:
    """Neutral cricket-native clause for one fact (no identifiers)."""

    if field_name in _BOOLEAN_CLAUSES:
        return _BOOLEAN_CLAUSES[field_name][0 if bool(value) else 1]
    if field_name == "contact":
        return _CONTACT_CLAUSES[str(value)]
    if field_name == "completed_runs":
        count = int(value)
        return f"{count} completed run{'s' if count != 1 else ''} preceded the terminal event"
    if field_name == "boundary_mode":
        return _BOUNDARY_CLAUSES[str(value)]
    if field_name == "boundary_allowance":
        return f"the agreed boundary allowance was {int(value)} runs"
    if field_name == "dismissal_candidate":
        return _DISMISSAL_CLAUSES[str(value)]
    if field_name == "penalty_runs_batting":
        return f"the batting side received {int(value)} separate penalty runs"
    raise KeyError(f"no R28 clause renderer for fact field {field_name}")


_FACT_FRAMES = (
    "The {source} records, for {subject}, that {clause}.",
    "Under {subject}, the {source} reports that {clause}.",
    "For {subject}, the {source} states that {clause}.",
    "Filed against {subject}, the {source} notes that {clause}.",
    "The {source} carries the entry that, for {subject}, {clause}.",
    "In the {source}, the line for {subject} reads that {clause}.",
)
_SHADOW_FRAMES = (
    "A separate incident note for {subject} records that {clause}.",
    "The review sheet for {subject} states that {clause}.",
    "A parallel entry headed {subject} notes that {clause}.",
    "The control file for {subject} reports that {clause}.",
)
_BINDING_FRAMES = (
    "The match-control index cross-references {source} as {target}.",
    "The scorer's routing note files {source} under {target}.",
    "The review register links {source} to {target}; the two phrases label one delivery.",
    "The pavilion concordance lists {source} and {target} as two headings for one delivery.",
    "In the scorer's filing trail, the entry called {source} continues under {target}.",
    "The innings register says that references to {source} resolve to {target}.",
)


def fact_span_text(subject: str, source: str, field_name: str, value: Any, *, question_id: str) -> str:
    index = int(digest(question_id, field_name, "fact-frame")[:4], 16) % len(_FACT_FRAMES)
    return _FACT_FRAMES[index].format(
        source=source, subject=subject, clause=fact_clause(field_name, value)
    )


def shadow_fact_text(subject: str, field_name: str, value: Any, *, question_id: str) -> str:
    index = int(digest(question_id, field_name, "shadow-frame")[:4], 16) % len(_SHADOW_FRAMES)
    return _SHADOW_FRAMES[index].format(subject=subject, clause=fact_clause(field_name, value))


def binding_text(source: str, target: str, *, question_id: str, hop: int) -> str:
    index = int(digest(question_id, hop, "binding-frame")[:4], 16) % len(_BINDING_FRAMES)
    return _BINDING_FRAMES[index].format(source=source, target=target)


def source_label(question_id: str, role: str) -> str:
    """Named source used by the controlling (signed) copy."""

    pairs = (
        ("signed on-field worksheet", "signed review sheet"),
        ("signed umpire worksheet", "signed match-control sheet"),
        ("signed field-observation sheet", "signed review folio"),
    )
    index = int(digest(question_id, role, "source-pair")[:4], 16) % len(pairs)
    return pairs[index][0]


def shadow_source_label(question_id: str, salt: str) -> str:
    pairs = (
        ("unsigned live-feed copy", "unsigned scorer-feed copy"),
        ("unsigned tabbed feed", "unsigned audio-log summary"),
        ("unsigned relay sheet", "unsigned standby copy"),
    )
    index = int(digest(question_id, salt, "shadow-source")[:4], 16) % len(pairs)
    return pairs[index][0]


def scope_text(identity: Identity, question_id: str) -> str:
    return (
        f"This dossier covers the single delivery filed as {identity.head} at "
        f"{identity.venue} in over {identity.over_number}. It carries the source copies, "
        "the law extracts and the review notes for that one delivery only."
    )


def question_text(identity: Identity) -> str:
    return (
        f"Resolve {identity.head}: one delivery in the dossier. Read the source copies, apply the "
        "law extracts that govern them, and return the normalized decision record, a confidence "
        "value and the smallest sufficient evidence set. Do not borrow an observation from a "
        "similar delivery, and do not use any figure that the controlling source does not support."
    )


def output_schema(config_output_contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "required_fields": list(config_output_contract["required_fields"]),
        "decision_record_fields": sorted(config_output_contract["decision_record_fields"]),
        "informative_fields": sorted(config_output_contract["informative_fields"]),
        "confidence": "scalar in [0,1]",
        "abstain": "not permitted; an unparseable or incomplete answer is scored wrong (ITT)",
    }


@dataclass
class Document:
    document_id: str
    title: str
    spans: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {"document_id": self.document_id, "title": self.title, "spans": self.spans}


def dossiers_tokens(documents: list[Document], question: str, schema: dict[str, Any],
                    chars_per_token: int = 4) -> int:
    text = question + canon(schema)
    for document in documents:
        text += document.title
        for span in document.spans:
            text += span["text"]
    return int(math.ceil(len(text) / chars_per_token))


def scan_public_text(documents: list[Document], question: str) -> list[str]:
    """Return forbidden markers found in public text (leak audit, HA11)."""

    blob = (question + "\n" + "\n".join(
        span["text"] for document in documents for span in document.spans
    )).lower()
    return [marker for marker in FORBIDDEN_PUBLIC_MARKERS if marker in blob]


__all__ = [
    "Document",
    "FORBIDDEN_PUBLIC_MARKERS",
    "Identity",
    "RULESET",
    "binding_text",
    "build_identity",
    "dossiers_tokens",
    "estimate_tokens",
    "fact_clause",
    "fact_span_text",
    "output_schema",
    "question_text",
    "scan_public_text",
    "scope_text",
    "shadow_fact_text",
    "shadow_source_label",
    "source_label",
    "token",
]
