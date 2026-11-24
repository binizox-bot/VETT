from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any


_NAME = re.compile(r"^[A-Z][A-Za-z'-]+(?: [A-Z][A-Za-z'-]+){1,2}$")


def digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _candidate_names(gold: dict[str, Any], column: str) -> list[str]:
    names: list[str] = []
    for target in gold.get("table_targets", []):
        if str(target.get("column", "")).casefold() != column.casefold():
            continue
        value = str(target.get("value", "")).strip()
        if _NAME.fullmatch(value) and value not in names:
            names.append(value)
    return names


def _match_summary(gold: dict[str, Any]) -> dict[str, str]:
    by_row: dict[str, dict[str, str]] = {}
    for target in gold.get("table_targets", []):
        if not str(target.get("table_id", "")).endswith(".match_summary"):
            continue
        by_row.setdefault(str(target.get("row_id")), {})[
            str(target.get("column"))
        ] = str(target.get("value", "")).strip()
    return {
        row["Field"]: row["Value"]
        for row in by_row.values()
        if row.get("Field") and row.get("Value")
    }


def _fixture_context(gold: dict[str, Any]) -> tuple[str, str]:
    summary = _match_summary(gold)
    venue = summary.get("Venue", "the match ground")
    toss = summary.get("Toss", "")
    result = summary.get("Result", "")
    toss_team = toss.split(" Won The Toss", 1)[0].strip() if " Won The Toss" in toss else ""
    winner = result.split(" Won by", 1)[0].strip() if " Won by" in result else ""
    if toss_team and winner and toss_team != winner:
        fixture = f"the {toss_team}-{winner} fixture"
    elif winner:
        fixture = f"the {winner} fixture at {venue}"
    elif toss_team:
        fixture = f"the {toss_team} fixture at {venue}"
    else:
        fixture = f"the fixture at {venue}"
    return venue, fixture


@dataclass(frozen=True)
class NaturalIdentity:
    batter: str
    bowler: str
    over_number: int
    minute: str
    target_description: str
    labels: tuple[str, ...]
    venue: str = ""
    fixture_label: str = ""


def natural_identity(
    match_id: str,
    question_id: str,
    gold: dict[str, Any],
    *,
    index: int,
    depth: int,
    fixture_context: bool = False,
) -> NaturalIdentity:
    batters = _candidate_names(gold, "Batter") or ["the striker", "the incoming batter"]
    bowlers = _candidate_names(gold, "Bowler") or ["the bowler", "the change bowler"]
    batter = batters[index % len(batters)]
    bowler = bowlers[(index * 3 + 1) % len(bowlers)]
    if fixture_context and bowler.split()[-1] == batter.split()[-1]:
        # A same-surname pairing can be real, but in a semi-synthetic identity
        # label ("Vale-Vale delivery") it reads like generator residue.  Select
        # the first deterministic alternative only for the R26.13 fixture-aware
        # renderer, preserving every historical release byte-for-byte.
        start = (index * 3 + 1) % len(bowlers)
        alternatives = [
            bowlers[(start + offset) % len(bowlers)]
            for offset in range(1, len(bowlers))
            if bowlers[(start + offset) % len(bowlers)].split()[-1]
            != batter.split()[-1]
        ]
        if alternatives:
            bowler = alternatives[0]
    over_number = 4 + int(digest(match_id, question_id, "over")[:4], 16) % 36
    hour = 11 + int(digest(question_id, "hour")[:2], 16) % 8
    minute_value = int(digest(question_id, "minute")[:2], 16) % 60
    minute = f"{hour:02d}:{minute_value:02d}"
    folio = 10 + int(digest(match_id, question_id, "folio")[:4], 16) % 90
    row = 1 + int(digest(match_id, question_id, "row")[:4], 16) % 24
    ledger_suffix = chr(ord("A") + int(digest(question_id, "ledger")[:2], 16) % 26)
    batter_short = batter.split()[-1] if " " in batter else batter
    bowler_short = bowler.split()[-1] if " " in bowler else bowler
    venue, fixture = _fixture_context(gold) if fixture_context else ("", "")
    target = (
        f"the scoring review involving {batter} in over {over_number} at {venue}"
        if fixture_context
        else f"the scoring review involving {batter} in over {over_number}"
    )
    if fixture_context:
        candidates = (
            f"the {batter_short}-{bowler_short} delivery in over {over_number} of {fixture}",
            f"the pavilion-end entry for the {batter_short}-{bowler_short} delivery in {fixture}",
            f"the {minute} signal review for {fixture}, filed under pavilion folio {folio}",
            f"the signed scorer sheet for {fixture} at folio {folio}, row {row}",
            f"pre-lock ledger cell {folio}/{row}-{ledger_suffix} in the scorebook for {fixture}",
        )
    else:
        candidates = (
            f"the {batter_short}-{bowler_short} delivery in over {over_number}",
            f"the pavilion-end entry for the {batter_short}-{bowler_short} delivery",
            f"the {minute} signal review filed under pavilion folio {folio}",
            f"the signed scorer sheet at folio {folio}, row {row}",
            f"pre-lock ledger cell {folio}/{row}-{ledger_suffix}",
        )
    if depth < 1 or depth > len(candidates):
        raise ValueError(f"unsupported semantic bridge depth: {depth}")
    return NaturalIdentity(
        batter=batter,
        bowler=bowler,
        over_number=over_number,
        minute=minute,
        target_description=target,
        labels=candidates[:depth],
        venue=venue,
        fixture_label=fixture,
    )


def counterfactual_blast_radius(answer: dict[str, Any]) -> tuple[int, tuple[str, ...]]:
    factual = answer["decision_record_flat"]
    counterfactual = answer["counterfactual"]["decision_record_flat"]
    changed = [f"record.{key}" for key, value in factual.items() if counterfactual.get(key) != value]
    for key, value in answer.get("state", {}).items():
        if answer["counterfactual"].get("state", {}).get(key) != value:
            changed.append(f"state.{key}")
    return len(changed), tuple(sorted(changed))


__all__ = ["NaturalIdentity", "counterfactual_blast_radius", "digest", "natural_identity"]
