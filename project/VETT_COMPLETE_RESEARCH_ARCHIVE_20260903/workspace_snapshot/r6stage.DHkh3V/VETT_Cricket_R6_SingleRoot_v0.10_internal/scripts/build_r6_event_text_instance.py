#!/usr/bin/env python3
"""Build one event-level R6 text-to-table instance from a validated ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


KEY_COLUMNS = {
    "Match Summary": "Field", "Innings Summary": "Field", "Batting": "Batter",
    "Bowling": "Bowler", "Partnerships": "Partnership", "Fall of Wickets": "Wkt",
}


def canon(value: str) -> str:
    return value.replace("(c)(wk)", "").replace("(wk)", "").replace("(c)", "").strip()


def event_description(event: dict[str, Any], prefix: str = "") -> str:
    label = event["delivery_label"].split("x", 1)[0]
    striker = event["striker"]
    bowler = event["bowler"]
    event_number = int(re.search(r"(\d+)$", event["event_id"]).group(1))

    def variant(*options: str) -> str:
        return options[event_number % len(options)]

    # Keep the outcome in the same sentence as its delivery identity. Besides
    # sounding more like a live log, this prevents reusable outcome fragments
    # from becoming position-independent shortcuts.
    lead = f"{prefix}{label}: {bowler} to {striker}; "
    if not event["is_legal"]:
        if event["extras_type"] == "wide":
            return lead + variant(
                "the line drifts beyond reach and the umpire calls a wide, so another ball is required.",
                "it passes outside the hitting arc for a wide and does not consume a legal ball.",
                "the wide signal follows immediately, leaving the bowler to repeat the delivery.",
            )
        if event["extras_type"] == "no_ball":
            return lead + variant(
                "the front-foot signal goes up for a no-ball, so it does not enter the legal-ball count.",
                "the umpire extends an arm for no-ball and the over remains at the same legal delivery.",
                "a no-ball is called at the crease, adding one without advancing the six-ball sequence.",
            )
    if event["dismissal"]:
        return lead + f"The wicket stands: {event['dismissal']['description']}."
    if event["extras_type"] == "bye":
        return lead + f"The bat is missed and the runners complete {event['extras_runs']} as byes."
    if event["extras_type"] == "leg_bye":
        return lead + f"It comes from the pad and they complete {event['extras_runs']} as leg-byes."
    runs = event["batter_runs"]
    if event["boundary_four"]:
        return lead + "Driven cleanly into the rope for four."
    if event["boundary_six"] and runs == 6:
        return lead + "A full swing sends it over the boundary for six."
    if event["boundary_six"] and runs > 6:
        return lead + f"The strike clears the rope for six and an overthrow sequence leaves {runs} credited to the batter."
    if runs == 0:
        return lead + variant(
            "defended without a run.",
            "the field closes quickly and no run is taken.",
            "played back down the pitch for a dot ball.",
            "no scoring chance develops from the stroke.",
        )
    if runs == 1:
        return lead + "Worked into the field for a single."
    if runs == 2:
        return lead + "They turn quickly and complete two."
    if runs == 3:
        return lead + "The placement beats the first chase and they run three."
    return lead + f"The running and overthrows leave {runs} to the batter."


def provisional_description(event: dict[str, Any], alternate: int) -> str:
    label = event["delivery_label"].split("x", 1)[0]
    if event["extras_type"]:
        item = f"{alternate} extras"
    else:
        item = f"{alternate} runs to {event['striker']}"
    return (
        f"At {label}, the first television ribbon carries {item} from {event['bowler']}'s delivery, "
        "but the scorer keeps that entry open while the next pictures are checked."
    )


def table_cell_id(table: dict[str, Any], row: dict[str, Any], column: str) -> str:
    return f"{table['table_id']}|{row['row_id']}|{column}"


def table_of(root: dict[str, Any], iid: str, table_type: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t.get("innings_id") == iid and t["table_type"] == table_type)


def build(root: dict[str, Any], ledger: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    accepted_segment_by_event: dict[str, str] = {}
    event_by_id = {e["event_id"]: e for inn in ledger["innings"] for e in inn["events"]}
    replay_event_ids: list[str] = []
    revision_records: list[dict[str, Any]] = []

    def add(kind: str, text: str, event_ids: list[str] | None = None) -> str:
        sid = f"s{len(segments)+1:04d}"
        segments.append({"segment_id": sid, "kind": kind, "text": text, "event_ids": event_ids or []})
        return sid

    metadata = root["match_metadata"]
    opening_sid = add(
        "match_opening",
        f"Coverage opens from {metadata.get('Venue', 'the ground')}. {metadata.get('Toss', '')}. "
        f"The umpires are {metadata.get('Umpires', 'the appointed officials')}. "
        "The director settles on the bowler's-end camera as the players take their places.",
    )

    revision_ids: set[str] = set()
    for innings in ledger["innings"]:
        # Keep enough subsequent live play for every delayed correction. This
        # prevents artificial end-of-document cleanup notes.
        eligible_events = innings["events"][:-15]
        score_candidates = [e for e in eligible_events if e["batter_runs"] > 0 or e["extras_runs"] > 0]
        revision_ids.update(
            score_candidates[round(i * (len(score_candidates) - 1) / 5)]["event_id"]
            for i in range(6)
        )
    stale_ids = set(sorted(revision_ids)[::2])
    pending: list[dict[str, Any]] = []
    event_counter = 0

    for innings_pos, innings in enumerate(ledger["innings"], start=1):
        add(
            "innings_transition",
            f"The {innings_pos}{'st' if innings_pos == 1 else 'nd'} innings begins with {innings['team']} batting. "
            f"The field settles as the live camera follows {innings['team']}'s opening pair to the middle.",
        )
        current_over = None
        for event in innings["events"]:
            event_counter += 1
            over = event["delivery_label"].split(".", 1)[0]
            if over != current_over:
                current_over = over
                add(
                    "over_transition",
                    f"Over {int(over) + 1} starts with {event['bowler']} taking the ball; "
                    "the field is still being adjusted behind the live call.",
                )

            if event["event_id"] in revision_ids:
                correct_value = event["extras_runs"] if event["extras_type"] else event["batter_runs"]
                alternate = correct_value + (1 if event_counter % 2 else -1)
                if alternate < 0:
                    alternate = correct_value + 1
                provisional_sid = add("provisional_graphic", provisional_description(event, alternate), [event["event_id"]])
                pending.append({
                    "release_at": event_counter + 9,
                    "event": event,
                    "alternate": alternate,
                    "provisional_segment": provisional_sid,
                    "stale": event["event_id"] in stale_ids,
                })
            else:
                sid = add("live_delivery", event_description(event), [event["event_id"]])
                accepted_segment_by_event[event["event_id"]] = sid
                if event_counter % 11 == 0:
                    replay_sid = add(
                        "same_delivery_replay",
                        "The director immediately returns from square leg to "
                        + event_description(event, prefix="the same delivery, replay of "),
                        [event["event_id"]],
                    )
                    replay_event_ids.append(event["event_id"])

            ready = [item for item in pending if item["release_at"] <= event_counter]
            pending = [item for item in pending if item["release_at"] > event_counter]
            for item in ready:
                correction_sid = add(
                    "delayed_scorer_correction",
                    "The scorer now returns to the earlier open entry: "
                    + event_description(item["event"], prefix="official correction for "),
                    [item["event"]["event_id"]],
                )
                accepted_segment_by_event[item["event"]["event_id"]] = correction_sid
                stale_sid = None
                if item["stale"]:
                    stale_sid = add(
                        "stale_highlight_graphic",
                        f"A highlight cut briefly restores the old ribbon with {item['alternate']} on the "
                        f"{item['event']['innings_id']} {item['event']['delivery_label'].split('x',1)[0]} entry, "
                        "which the commentator identifies as the pre-correction picture.",
                        [item["event"]["event_id"]],
                    )
                revision_records.append({
                    "event_id": item["event"]["event_id"],
                    "correct_value": item["event"]["extras_runs"] if item["event"]["extras_type"] else item["event"]["batter_runs"],
                    "alternate_value": item["alternate"],
                    "provisional_segment": item["provisional_segment"],
                    "correction_segment": correction_sid,
                    "stale_segment": stale_sid,
                })

    for item in pending:
        correction_sid = add(
            "delayed_scorer_correction",
            "Before the broadcast closes, the scorer resolves an earlier open entry: "
            + event_description(item["event"], prefix="official correction for "),
            [item["event"]["event_id"]],
        )
        accepted_segment_by_event[item["event"]["event_id"]] = correction_sid
        stale_sid = None
        if item["stale"]:
            stale_sid = add(
                "stale_highlight_graphic",
                f"The closing montage reuses the old {item['alternate']} ribbon for {item['event']['delivery_label'].split('x',1)[0]}, which the presenter labels as superseded.",
                [item["event"]["event_id"]],
            )
        revision_records.append({
            "event_id": item["event"]["event_id"],
            "correct_value": item["event"]["extras_runs"] if item["event"]["extras_type"] else item["event"]["batter_runs"],
            "alternate_value": item["alternate"],
            "provisional_segment": item["provisional_segment"],
            "correction_segment": correction_sid,
            "stale_segment": stale_sid,
        })

    closing_sid = add(
        "match_close",
        f"The official result is {metadata.get('Result', '')}. "
        f"The player-of-the-match award goes to {metadata.get('Player of the Match', '')}. "
        "The final interviews begin as the ground staff move in behind the presentation area.",
    )

    # Compose document and retain private character spans.
    parts, cursor, spans = [], 0, {}
    for segment in segments:
        if parts:
            parts.append("\n\n")
            cursor += 2
        start = cursor
        parts.append(segment["text"])
        cursor += len(segment["text"])
        spans[segment["segment_id"]] = {"start": start, "end": cursor}
    document_text = "".join(parts)

    # Event dependencies for every output cell.
    inning_events = {inn["innings_id"]: inn["events"] for inn in ledger["innings"]}
    wicket_events = {iid: [e for e in events if e["dismissal"]] for iid, events in inning_events.items()}
    dependency_map: dict[str, list[str]] = {}
    operation_map: dict[str, str] = {}
    scored, challenges = [], []
    public_tables, gold_tables = [], []

    for table in root["tables"]:
        key = KEY_COLUMNS[table["table_type"]]
        iid = table.get("innings_id")
        public_rows, gold_rows = [], []
        for row_pos, row in enumerate(table["rows"]):
            public_rows.append({col: (row[col] if col == key else None) for col in table["columns"]})
            gold_rows.append({col: row[col] for col in table["columns"]})
            for column in table["columns"]:
                if column == key or row[column] is None or str(row[column]).strip() == "":
                    continue
                cid = table_cell_id(table, row, column)
                deps: list[str] = []
                operation = "direct_metadata"
                if table["table_type"] == "Match Summary":
                    deps = []
                elif table["table_type"] == "Innings Summary":
                    events = inning_events[iid]
                    field = row["Field"]
                    if field in ("Byes", "Leg Byes", "No Balls", "Wides"):
                        wanted = {"Byes": "bye", "Leg Byes": "leg_bye", "No Balls": "no_ball", "Wides": "wide"}[field]
                        # The complete innings feed supplies closed-world evidence,
                        # including a defensible zero when the category never occurs.
                        deps = [e["event_id"] for e in events]
                        operation = "sum_extra_class"
                    elif field == "Max Partnership":
                        deps = [e["event_id"] for e in events]
                        operation = "group_sum_then_max"
                    else:
                        deps = [e["event_id"] for e in events]
                        operation = "innings_state_aggregate"
                elif table["table_type"] == "Batting":
                    name = canon(row["Batter"])
                    deps = [
                        e["event_id"] for e in inning_events[iid]
                        if canon(e["striker"]) == name or (e["dismissal"] and canon(e["dismissal"]["batter"]) == name)
                    ]
                    operation = {
                        "Dismissal": "final_dismissal_state", "R": "sum_batter_runs", "B": "count_legal_faced",
                        "4s": "count_fours", "6s": "count_sixes", "SR": "ratio_runs_balls",
                    }[column]
                elif table["table_type"] == "Bowling":
                    name = row["Bowler"]
                    deps = [e["event_id"] for e in inning_events[iid] if e["bowler"] == name]
                    operation = {
                        "O": "count_legal_balls", "M": "group_over_zero_conceded", "R": "sum_bowler_conceded",
                        "W": "count_credited_wickets", "Econ": "ratio_runs_overs", "Wd": "sum_wides", "Nb": "sum_no_balls",
                    }[column]
                elif table["table_type"] == "Partnerships":
                    pid = f"{iid}.P{row_pos+1:02d}"
                    deps = [e["event_id"] for e in inning_events[iid] if e["partnership_id"] == pid]
                    operation = {
                        "Runs": "sum_partnership_runs", "Extras": "sum_partnership_extras",
                        "Striker": "player_component", "Non-striker": "player_component", "Overs": "event_boundary",
                        "End": "terminal_dismissal_state",
                    }[column]
                elif table["table_type"] == "Fall of Wickets":
                    deps = [wicket_events[iid][row_pos]["event_id"]]
                    operation = "cumulative_wicket_state"
                dependency_map[cid] = deps
                operation_map[cid] = operation
                scored.append(cid)
                if operation != "direct_metadata":
                    challenges.append(cid)
        public_tables.append({
            "table_type": table["table_type"], "innings_id": iid,
            "columns": table["columns"], "rows": public_rows,
        })
        gold_tables.append({
            "table_id": table["table_id"], "table_type": table["table_type"], "innings_id": iid,
            "columns": table["columns"], "rows": gold_rows,
        })

    segment_by_id = {s["segment_id"]: s for s in segments}
    cell_evidence = []
    for table in root["tables"]:
        key = KEY_COLUMNS[table["table_type"]]
        for row in table["rows"]:
            for column in table["columns"]:
                cid = table_cell_id(table, row, column)
                if cid not in dependency_map:
                    continue
                if operation_map[cid] == "direct_metadata":
                    sid = closing_sid if row[key] in ("Result", "Player of the Match") else opening_sid
                    refs = [sid]
                else:
                    refs = sorted({accepted_segment_by_event[eid] for eid in dependency_map[cid] if eid in accepted_segment_by_event})
                cell_evidence.append({
                    "cell_id": cid,
                    "gold": row[column],
                    "operation": operation_map[cid],
                    "event_ids": dependency_map[cid],
                    "evidence": [
                        {"segment_id": sid, **spans[sid]}
                        for sid in refs
                    ],
                })

    public = {
        "instance_id": "r6a_0001",
        "instruction": "Reconstruct the complete scorecard tables from the supplied delivery commentary.",
        "document": {"document_id": "delivery_commentary", "text": document_text},
        "tables": public_tables,
        "output_rule": "Return every supplied table and fill every blank cell while preserving row keys and columns.",
    }
    private = {
        "instance_id": "r6a_0001",
        "root_id": root["root_id"],
        "gold_tables": gold_tables,
        "scored_cell_ids": scored,
        "challenge_cell_ids": challenges,
    }
    evidence = {
        "instance_id": "r6a_0001",
        "document_sha256": hashlib.sha256(document_text.encode()).hexdigest(),
        "segments": [{**s, **spans[s["segment_id"]]} for s in segments],
        "cells": cell_evidence,
        "revision_records": revision_records,
        "replay_event_ids": replay_event_ids,
        "event_ledger": ledger,
    }
    return public, private, evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = json.loads(args.root.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    public, private, evidence = build(root, ledger)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "r6_single_public.json").write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "r6_single_private_gold.json").write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "r6_single_private_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "words": len(public["document"]["text"].split()),
        "segments": len(evidence["segments"]),
        "scored_cells": len(private["scored_cell_ids"]),
        "challenge_cells": len(private["challenge_cell_ids"]),
        "revisions": len(evidence["revision_records"]),
        "replays": len(evidence["replay_event_ids"]),
    }, indent=2))


if __name__ == "__main__":
    main()
