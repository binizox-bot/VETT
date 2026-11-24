from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any


VERSION = "VETT-Cricket-v0.28-R21-evidence-chain-pilot"

ORDINALS = (
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth",
    "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth",
    "nineteenth", "twentieth",
)

TABLE_NAMES = {
    "Match Summary": ("match register", "fixture summary", "match-level ledger"),
    "Innings Summary": ("innings summary", "innings control block", "innings ledger"),
    "Batting": ("batting card", "batters' register", "dismissal-and-scoring card"),
    "Bowling": ("bowling analysis", "bowlers' register", "spell analysis"),
    "Fall of Wickets": ("wicket-fall list", "dismissal sequence", "fall register"),
    "Partnerships": ("partnership list", "stand register", "pairing ledger"),
}

COLUMN_NAMES = {
    "Field": ("label", "field heading", "item name"),
    "Value": ("recorded content", "corresponding entry", "filed value"),
    "Batter": ("batter identity", "listed player", "name entry"),
    "Dismissal": ("dismissal wording", "departure entry", "method of dismissal"),
    "R": ("runs credited", "run entry", "runs column"),
    "B": ("deliveries faced", "ball count", "balls column"),
    "4s": ("boundary-fours count", "fours entry", "number of fours"),
    "6s": ("sixes count", "six-hitting entry", "number of sixes"),
    "SR": ("strike-rate entry", "scoring-rate figure", "strike rate"),
    "Bowler": ("bowler identity", "listed bowler", "name entry"),
    "O": ("overs figure", "overs entry", "spell length"),
    "M": ("maiden-over count", "maidens entry", "maiden figure"),
    "W": ("wickets credited", "wicket tally", "wickets column"),
    "Econ": ("economy figure", "runs-per-over entry", "economy rate"),
    "0s": ("dot-ball count", "scoreless-delivery tally", "dots entry"),
    "Wd": ("wide count", "wides charged", "wide-ball entry"),
    "Nb": ("no-ball count", "no-balls charged", "no-ball entry"),
    "Wkt": ("wicket number", "dismissal ordinal", "fall number"),
    "Score": ("score at the fall", "fall score", "score entry"),
    "At": ("over marker", "point of fall", "over entry"),
    "Player": ("departing player", "player entry", "dismissed batter"),
    "Partnership": ("partner pairing", "partnership pair", "two-player entry"),
    "Runs": ("stand size", "partnership total", "runs added"),
    "Extras": ("extras contribution", "stand extras", "extras entry"),
    "Overs": ("stand interval", "partnership overs", "over range"),
    "Striker": ("first partner contribution", "striker-side entry", "lead contribution"),
    "Non-Striker": ("second partner contribution", "non-striker entry", "other contribution"),
    "Non-striker": ("second partner contribution", "non-striker entry", "other contribution"),
    "End": ("ending event", "stand-ending dismissal", "closing event"),
}

GENRES = (
    "venue notebook", "broadcast handover", "scorer correspondence",
    "competition registry", "technical review page", "officials' worksheet",
    "archive reconciliation note", "production desk extract",
    "match-control memorandum", "statistics liaison page",
)

FILLERS = (
    "The folio number identifies a sheet, not the authority of its cricket entries.",
    "Receipt order differs from event order because several pages arrived in one bundle.",
    "Initials in the margin confirm handling only and do not validate adjacent figures.",
    "A copied entry inherits the status of the source docket from which it was taken.",
    "Only an explicit relation changes the standing of a claim for the named location.",
    "Pagination was assigned after the records were reconciled.",
    "The transmission checksum concerns document handling rather than match state.",
    "Unmentioned rows and columns are unaffected by a location-specific revision.",
)


@dataclass(frozen=True)
class Bundle:
    public: dict[str, Any]
    gold: dict[str, Any]
    evidence: dict[str, Any]


def _digest(*parts: object) -> str:
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _quote(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _innings_phrase(innings_id: str | None, variant: int) -> str:
    choices = {
        None: ("match-level", "whole-match", "fixture-level"),
        "I1": ("opening-innings", "first-innings", "initial-innings"),
        "I2": ("chase-innings", "second-innings", "reply-innings"),
        "I3": ("third-innings", "return-innings", "later-innings"),
    }
    values = choices.get(innings_id, (f"{innings_id}-innings",))
    return values[variant % len(values)]


def _locator(
    cell: dict[str, Any], table: dict[str, Any], row_number: int, style: int
) -> str:
    ordinal = ORDINALS[row_number - 1] if row_number <= len(ORDINALS) else f"number-{row_number}"
    table_name = TABLE_NAMES[table["table_type"]][style % len(TABLE_NAMES[table["table_type"]])]
    column_names = COLUMN_NAMES.get(cell["column"], (cell["column"].lower(),))
    column_name = column_names[(style // 3) % len(column_names)]
    innings = _innings_phrase(table.get("innings_id"), style // 7)
    variants = (
        f"the {column_name} on the {ordinal} line of the {innings} {table_name}",
        f"the {ordinal} listed row's {column_name} in the {innings} {table_name}",
        f"the {innings} {table_name}, {ordinal} row, specifically its {column_name}",
        f"the {column_name} attached to row {ordinal} in the {innings} {table_name}",
    )
    return variants[style % len(variants)]


def _base_text(docket: str, locator: str, value: str, style: int) -> str:
    variants = (
        f"Slip {docket} initially entered {_quote(value)} for {locator}.",
        f"For {locator}, the provisional docket {docket} carried {_quote(value)}.",
        f"The early register item {docket} associated {locator} with {_quote(value)}.",
        f"Docket {docket} supplied the first circulated value, {_quote(value)}, for {locator}.",
        f"The value shown by {docket} at {locator} was {_quote(value)}.",
        f"At {locator}, item {docket} recorded {_quote(value)} before reconciliation.",
    )
    return variants[style % len(variants)]


def _supersede_text(
    docket: str, parent: str, locator: str, value: str, style: int, scoped: bool
) -> str:
    scope = " That change applies only to this location." if scoped else ""
    variants = (
        f"Revision {docket} supersedes {parent} for {locator}; use {_quote(value)}.{scope}",
        f"Replace {parent} with {docket} at {locator}, where the reconciled entry is {_quote(value)}.{scope}",
        f"For {locator}, {docket} displaces {parent} and records {_quote(value)}.{scope}",
        f"The desk issued {docket} against {parent}: {locator} now carries {_quote(value)}.{scope}",
        f"Docket {parent} is no longer operative at {locator}; its successor {docket} gives {_quote(value)}.{scope}",
        f"A location-specific amendment, {docket}, overrides {parent} and sets {locator} to {_quote(value)}.{scope}",
        f"Use the {_quote(value)} entry in {docket}, which supersedes {parent} for {locator}.{scope}",
        f"Reconciliation moved {locator} from {parent} to {docket}; the replacement is {_quote(value)}.{scope}",
    )
    return variants[style % len(variants)]


def _copy_text(
    docket: str, parent: str, locator: str, value: str, style: int
) -> str:
    variants = (
        f"Docket {docket} repeats {_quote(value)} for {locator}, copied from {parent} without independent checking.",
        f"The {_quote(value)} entry at {locator} in {docket} is a direct copy of {parent}.",
        f"For {locator}, page {docket} transcribed {parent}'s {_quote(value)} and adds no separate verification.",
        f"Item {docket} inherited {_quote(value)} at {locator} from source docket {parent}.",
    )
    return variants[style % len(variants)]


def _retract_text(docket: str, parent: str, locator: str, style: int) -> str:
    variants = (
        f"Withdrawal {docket} retracts {parent} for {locator}; its value must not be carried forward.",
        f"For {locator}, notice {docket} cancels docket {parent} without supplying a replacement value.",
        f"Docket {parent} was withdrawn at {locator} by notice {docket}.",
        f"The review note {docket} invalidates {parent} only for {locator}.",
    )
    return variants[style % len(variants)]


def _replacement_text(docket: str, locator: str, value: str, style: int) -> str:
    variants = (
        f"After the withdrawal, independent entry {docket} records {_quote(value)} for {locator}.",
        f"The active standalone entry for {locator} is {docket}, carrying {_quote(value)}.",
        f"A separately verified docket, {docket}, supplies {_quote(value)} at {locator}.",
        f"Following cancellation of the earlier item, {docket} enters {_quote(value)} for {locator}.",
    )
    return variants[style % len(variants)]


def _alternatives(cells: list[dict[str, Any]], tables: dict[str, Any]) -> dict[str, list[str]]:
    grouped: dict[tuple[str, str], list[str]] = {}
    for cell in cells:
        table = tables[cell["table_id"]]
        grouped.setdefault((table["table_type"], cell["column"]), []).append(str(cell["value"]))
    result: dict[str, list[str]] = {}
    for cell in cells:
        table = tables[cell["table_id"]]
        value = str(cell["value"])
        peers = list(dict.fromkeys(
            item for item in grouped[(table["table_type"], cell["column"])] if item != value
        ))
        if not peers:
            peers = [str(int(value) + 1)] if value.lstrip("-").isdigit() else [f"provisional {value}"]
        result[cell["cell_id"]] = peers
    return result


def build_instance(root: dict[str, Any], seed: int = 21031) -> Bundle:
    match_id = root["root_id"]
    tables = {table["table_id"]: table for table in root["tables"]}
    row_numbers = {
        (table["table_id"], row["row_id"]): index
        for table in root["tables"]
        for index, row in enumerate(table["rows"], 1)
    }
    cells = sorted(
        (
            cell for cell in root["cells"]
            if cell.get("gold_status") == "R20_VERIFIED_SOURCE"
        ),
        key=lambda cell: cell["cell_id"],
    )
    alternatives = _alternatives(cells, tables)
    claims: list[dict[str, Any]] = []
    span_items: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []

    def add_claim(
        target_id: str,
        relation: str,
        value: str | None,
        text: str,
        parent_claim: str | None,
        parent_docket: str | None,
        ordinal: int,
    ) -> dict[str, Any]:
        token = _digest(seed, match_id, target_id, relation, ordinal)
        claim = {
            "claim_id": f"claim_{token[:16]}",
            "target_id": target_id,
            "docket": f"N{token[16:26].upper()}",
            "relation": relation,
            "value": value,
            "parent_claim_id": parent_claim,
            "parent_docket": parent_docket,
            "span_id": f"span_{token[26:44]}",
        }
        # Text is built after the deterministic docket is known.
        claim["text_builder"] = text
        claims.append(claim)
        return claim

    mechanisms = ("one_step", "two_step", "copy_trap", "retract_replace", "scoped")
    for cell in cells:
        table = tables[cell["table_id"]]
        token = _digest(seed, match_id, cell["cell_id"], "mechanism")
        style = int(token[:8], 16)
        mechanism = mechanisms[style % len(mechanisms)]
        locator = _locator(cell, table, row_numbers[(cell["table_id"], cell["row_id"])], style)
        wrongs = alternatives[cell["cell_id"]]
        target_claims: list[dict[str, Any]] = []
        required_claims: list[dict[str, Any]] = []
        required_edges: list[dict[str, str]] = []

        base = add_claim(cell["cell_id"], "asserts", wrongs[0], "base", None, None, 0)
        base["text"] = _base_text(base["docket"], locator, wrongs[0], style)
        target_claims.append(base)
        required_claims.append(base)

        if mechanism == "two_step":
            middle_value = wrongs[1 % len(wrongs)]
            middle = add_claim(cell["cell_id"], "supersedes", middle_value, "supersede", base["claim_id"], base["docket"], 1)
            middle["text"] = _supersede_text(middle["docket"], base["docket"], locator, middle_value, style + 1, False)
            target_claims.append(middle)
            required_claims.append(middle)
            required_edges.append({"from_claim": middle["claim_id"], "relation": "supersedes", "to_claim": base["claim_id"]})
            parent = middle
        else:
            parent = base

        if mechanism == "copy_trap":
            for copy_index in range(2):
                copy_claim = add_claim(cell["cell_id"], "copies_from", wrongs[0], "copy", base["claim_id"], base["docket"], copy_index + 1)
                copy_claim["text"] = _copy_text(copy_claim["docket"], base["docket"], locator, wrongs[0], style + copy_index)
                target_claims.append(copy_claim)
                required_claims.append(copy_claim)
                required_edges.append({"from_claim": copy_claim["claim_id"], "relation": "copies_from", "to_claim": base["claim_id"]})

        if mechanism == "retract_replace":
            retraction = add_claim(cell["cell_id"], "retracts", None, "retract", base["claim_id"], base["docket"], 1)
            retraction["text"] = _retract_text(retraction["docket"], base["docket"], locator, style)
            replacement = add_claim(cell["cell_id"], "asserts", str(cell["value"]), "replacement", None, None, 2)
            replacement["text"] = _replacement_text(replacement["docket"], locator, str(cell["value"]), style)
            target_claims.extend((retraction, replacement))
            required_claims.extend((retraction, replacement))
            required_edges.append({"from_claim": retraction["claim_id"], "relation": "retracts", "to_claim": base["claim_id"]})
            decisive = replacement
        else:
            terminal_ordinal = 3 if mechanism == "copy_trap" else 2 if mechanism == "two_step" else 1
            terminal = add_claim(cell["cell_id"], "supersedes", str(cell["value"]), "supersede", parent["claim_id"], parent["docket"], terminal_ordinal)
            terminal["text"] = _supersede_text(terminal["docket"], parent["docket"], locator, str(cell["value"]), style + 2, mechanism == "scoped")
            target_claims.append(terminal)
            required_claims.append(terminal)
            required_edges.append({"from_claim": terminal["claim_id"], "relation": "supersedes", "to_claim": parent["claim_id"]})
            decisive = terminal

        for claim in target_claims:
            claim.pop("text_builder", None)
            claim["span_sha256"] = _hash(claim["text"])
            span_items.append({"span_id": claim["span_id"], "text": claim["text"], "claim_id": claim["claim_id"]})
        claim_to_span = {claim["claim_id"]: claim["span_id"] for claim in target_claims}
        targets.append(
            {
                "target_id": cell["cell_id"],
                "table_id": cell["table_id"],
                "table_type": table["table_type"],
                "innings_id": table.get("innings_id"),
                "row_id": cell["row_id"],
                "column": cell["column"],
                "value": str(cell["value"]),
                "mechanism": mechanism,
                "decisive_claim_id": decisive["claim_id"],
                "required_evidence_spans": [claim["span_id"] for claim in required_claims],
                "required_edges": [
                    {
                        "from_span": claim_to_span[edge["from_claim"]],
                        "relation": edge["relation"],
                        "to_span": claim_to_span[edge["to_claim"]],
                    }
                    for edge in required_edges
                ],
            }
        )

    rng = random.Random(f"R21|{seed}|{match_id}")
    rng.shuffle(span_items)
    documents: list[dict[str, Any]] = []
    claim_locations: dict[str, str] = {}
    cursor = 0
    document_index = 0
    while cursor < len(span_items):
        size = rng.randint(20, 46)
        chunk = span_items[cursor : cursor + size]
        cursor += len(chunk)
        token = _digest(seed, match_id, "document", document_index)
        document_id = f"folio_{token[:14]}"
        spans = []
        for item in chunk:
            spans.append({"span_id": item["span_id"], "text": item["text"]})
            claim_locations[item["claim_id"]] = document_id
        for filler_index in range(1 + int(token[14:16], 16) % 3):
            spans.append({
                "span_id": f"{document_id}.routing{filler_index + 1}",
                "text": FILLERS[int(_digest(token, filler_index)[:8], 16) % len(FILLERS)],
            })
        documents.append({
            "document_id": document_id,
            "genre": GENRES[int(token[16:20], 16) % len(GENRES)],
            "spans": spans,
            "text": "\n".join(span["text"] for span in spans),
        })
        document_index += 1
    rng.shuffle(documents)
    for claim in claims:
        claim["document_id"] = claim_locations[claim["claim_id"]]

    target_columns: dict[tuple[str, str], list[str]] = {}
    for target in targets:
        target_columns.setdefault((target["table_id"], target["row_id"]), []).append(target["column"])
    layouts = [
        {
            "table_id": table["table_id"],
            "table_type": table["table_type"],
            "innings_id": table.get("innings_id"),
            "columns": table["columns"],
            "rows": [
                {"row_id": row["row_id"], "score_columns": sorted(target_columns.get((table["table_id"], row["row_id"]), []))}
                for row in table["rows"]
            ],
        }
        for table in root["tables"]
    ]
    public = {
        "dataset_version": VERSION,
        "instance_id": match_id,
        "task": (
            "Reconstruct every requested exact-string cell and cite the evidence graph. "
            "Row words such as first or eighth refer to row order in the public layout. "
            "An explicit supersession invalidates its predecessor for that semantic location; "
            "a retraction cancels its target; a copied claim inherits the status of its source. "
            "Document order, genre and frequency are not authority signals."
        ),
        "output_contract": {
            "per_target": ["target_id", "value", "evidence_spans", "evidence_edges"],
            "edge_fields": ["from_span", "relation", "to_span"],
        },
        "table_layouts": layouts,
        "target_schema": [
            {key: target[key] for key in ("target_id", "table_id", "table_type", "innings_id", "row_id", "column")}
            for target in targets
        ],
        "documents": documents,
    }
    gold = {
        "dataset_version": VERSION,
        "instance_id": match_id,
        "targets": targets,
        "masked_source_conflict_cell_ids": [
            cell["cell_id"] for cell in root["cells"]
            if cell.get("gold_status") == "R20_UNSCORED_SOURCE_CONFLICT"
        ],
    }
    evidence = {
        "dataset_version": VERSION,
        "instance_id": match_id,
        "policy": "typed_claim_graph_with_copy_inheritance",
        "claims": claims,
    }
    return Bundle(public=public, gold=gold, evidence=evidence)


def resolve(evidence: dict[str, Any]) -> dict[str, str]:
    by_target: dict[str, list[dict[str, Any]]] = {}
    for claim in evidence["claims"]:
        by_target.setdefault(claim["target_id"], []).append(claim)
    result: dict[str, str] = {}
    for target_id, claims in by_target.items():
        invalid: set[str] = set()
        for claim in claims:
            if claim["relation"] in {"supersedes", "retracts"} and claim["parent_claim_id"]:
                invalid.add(claim["parent_claim_id"])
        changed = True
        while changed:
            changed = False
            for claim in claims:
                if claim["relation"] == "copies_from" and claim["parent_claim_id"] in invalid and claim["claim_id"] not in invalid:
                    invalid.add(claim["claim_id"])
                    changed = True
        active = [
            claim for claim in claims
            if claim["value"] is not None
            and claim["relation"] != "copies_from"
            and claim["claim_id"] not in invalid
        ]
        if len(active) != 1:
            raise ValueError(f"{target_id}: expected one active claim, found {len(active)}")
        result[target_id] = str(active[0]["value"])
    return result


__all__ = ["Bundle", "VERSION", "build_instance", "resolve"]
