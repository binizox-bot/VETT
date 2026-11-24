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

PROFILES = {
    "r6_broadcast": {
        "instance_id": "r6a_0001",
        "revision_per_innings": 6,
        "eligible_tail_buffer": 15,
        "correction_delay_events": 9,
        "review_delay_events": None,
        "stale_delay_events": 0,
        "replay_interval": 11,
    },
    "r7_live_blog": {
        "instance_id": "r7b_0001",
        "revision_per_innings": 12,
        "eligible_tail_buffer": 35,
        "correction_delay_events": 18,
        "review_delay_events": 8,
        "stale_delay_events": 6,
        "replay_interval": 3,
    },
    "r8_radio_nonperiodic": {
        "instance_id": "r8c_0001",
        "revision_per_innings": 30,
        "eligible_tail_buffer": 50,
        "correction_delay_events": [24, 44],
        "review_delay_events": [9, 18],
        "stale_delay_events": [9, 23],
        "replay_interval": None,
        "replay_fraction": 0.95,
        "selection_rule": "stratified_stable_hash_nonperiodic",
    },
}


def stable_int(*parts: str) -> int:
    return int.from_bytes(
        hashlib.sha256("\x1f".join(parts).encode("utf-8")).digest()[:8], "big"
    )


def ranged_delay(value: int | list[int] | None, event_id: str, salt: str) -> int | None:
    if value is None or isinstance(value, int):
        return value
    low, high = value
    return low + stable_int(event_id, salt) % (high - low + 1)


def canon(value: str) -> str:
    return value.replace("(c)(wk)", "").replace("(wk)", "").replace("(c)", "").strip()


def event_serial(event: dict[str, Any]) -> int:
    return int(re.search(r"(\d+)$", event["event_id"]).group(1))


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
        return lead + f"the wicket stands: {event['dismissal']['description']}."
    if event["extras_type"] == "bye":
        return lead + f"the bat is missed and the runners complete {event['extras_runs']} as byes."
    if event["extras_type"] == "leg_bye":
        return lead + f"it comes from the pad and they complete {event['extras_runs']} as leg-byes."
    runs = event["batter_runs"]
    if event["boundary_four"]:
        return lead + "driven cleanly into the rope for four."
    if event["boundary_six"] and runs == 6:
        return lead + "a full swing sends it over the boundary for six."
    if event["boundary_six"] and runs > 6:
        return lead + f"the strike clears the rope for six and an overthrow sequence leaves {runs} credited to the batter."
    if runs == 0:
        return lead + variant(
            "defended without a run.",
            "the field closes quickly and no run is taken.",
            "played back down the pitch for a dot ball.",
            "no scoring chance develops from the stroke.",
        )
    if runs == 1:
        return lead + "worked into the field for a single."
    if runs == 2:
        return lead + "they turn quickly and complete two."
    if runs == 3:
        return lead + "the placement beats the first chase and they run three."
    return lead + f"the running and overthrows leave {runs} to the batter."


def provisional_description(
    event: dict[str, Any], alternate: int, alternate_event: dict[str, Any] | None = None
) -> str:
    label = event["delivery_label"].split("x", 1)[0]
    production_cue = event_serial(event)
    state = alternate_event or event
    if state["extras_type"] == "wide":
        item = f"{state['extras_runs']} " + ("wide" if state["extras_runs"] == 1 else "wides")
    elif state["extras_type"] == "no_ball":
        item = f"{state['extras_runs']} " + ("no-ball" if state["extras_runs"] == 1 else "no-balls")
    elif state["extras_type"] == "bye":
        item = f"{state['extras_runs']} " + ("bye" if state["extras_runs"] == 1 else "byes")
    elif state["extras_type"] == "leg_bye":
        item = f"{state['extras_runs']} " + ("leg-bye" if state["extras_runs"] == 1 else "leg-byes")
    else:
        item = f"{state['batter_runs']} " + ("run" if state["batter_runs"] == 1 else "runs") + f" to {event['striker']}"
    return (
        f"At {label}, the first television ribbon carries {item} from {event['bowler']}'s delivery, "
        f"with {event['non_striker']} waiting at the other end; the scorer keeps that entry open "
        f"under production cue {production_cue} and records it as "
        f"{'advancing' if state['is_legal'] else 'not advancing'} the legal-ball sequence."
    )


def alternate_claim(
    event: dict[str, Any], event_counter: int, profile_name: str
) -> tuple[int, dict[str, Any]]:
    correct_value = event["extras_runs"] if event["extras_type"] else event["batter_runs"]
    alternate = correct_value + (1 if event_counter % 2 else -1)
    if alternate < 0:
        alternate = correct_value + 1
    state = {
        "is_legal": event["is_legal"],
        "batter_runs": event["batter_runs"],
        "boundary_four": event["boundary_four"],
        "boundary_six": event["boundary_six"],
        "extras_type": event["extras_type"],
        "extras_runs": event["extras_runs"],
    }
    if profile_name == "r6_broadcast" or event["dismissal"]:
        if event["extras_type"]:
            state["extras_runs"] = alternate
        else:
            state["batter_runs"] = alternate
            state["boundary_four"] = alternate == 4
            state["boundary_six"] = alternate in (6, 8)
        return alternate, state

    if event["is_legal"] and event["batter_runs"] > 0 and event_counter % 3 == 0:
        state.update({
            "is_legal": False, "batter_runs": 0, "boundary_four": False,
            "boundary_six": False, "extras_type": "wide", "extras_runs": 1,
        })
    elif event["is_legal"] and event["batter_runs"] > 0 and event_counter % 3 == 1:
        state.update({
            "batter_runs": 0, "boundary_four": False, "boundary_six": False,
            "extras_type": "leg_bye", "extras_runs": max(1, min(event["batter_runs"], 3)),
        })
    elif event["extras_type"]:
        state.update({
            "is_legal": True, "batter_runs": max(1, event["extras_runs"]),
            "boundary_four": False, "boundary_six": False,
            "extras_type": None, "extras_runs": 0,
        })
    else:
        state["batter_runs"] = alternate
        state["boundary_four"] = alternate == 4
        state["boundary_six"] = alternate in (6, 8)
    alternate_value = state["extras_runs"] if state["extras_type"] else state["batter_runs"]
    return alternate_value, state


def table_cell_id(table: dict[str, Any], row: dict[str, Any], column: str) -> str:
    return f"{table['table_id']}|{row['row_id']}|{column}"


def table_of(root: dict[str, Any], iid: str, table_type: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t.get("innings_id") == iid and t["table_type"] == table_type)


def build(
    root: dict[str, Any], ledger: dict[str, Any], profile_name: str = "r6_broadcast"
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    profile = PROFILES[profile_name]
    segments: list[dict[str, Any]] = []
    accepted_segment_by_event: dict[str, str] = {}
    event_by_id = {e["event_id"]: e for inn in ledger["innings"] for e in inn["events"]}
    replay_event_ids: list[str] = []
    revision_records: list[dict[str, Any]] = []
    pending_stale: list[dict[str, Any]] = []

    def add(kind: str, text: str, event_ids: list[str] | None = None) -> str:
        sid = f"s{len(segments)+1:04d}"
        segments.append({"segment_id": sid, "kind": kind, "text": text, "event_ids": event_ids or []})
        return sid

    def innings_ref(event: dict[str, Any]) -> str:
        return "first-innings" if event["innings_id"] == "I1" else "second-innings"

    metadata = root["match_metadata"]
    if profile_name == "r8_radio_nonperiodic":
        opening_tail = (
            "The radio producer keeps three feeds open: the live caller, a scorer telephone and a delayed replay monitor. "
            "Only the scorer's later ruling closes an entry when those feeds conflict."
        )
    elif profile_name == "r7_live_blog":
        opening_tail = "A live-blog editor pins the opening post while radio pictures settle on the bowler's-end view."
    else:
        opening_tail = "The director settles on the bowler's-end camera as the players take their places."
    opening_sid = add(
        "match_opening",
        f"Coverage opens from {metadata.get('Venue', 'the ground')}. {metadata.get('Toss', '')}. "
        f"The umpires are {metadata.get('Umpires', 'the appointed officials')}. "
        + opening_tail,
    )

    revision_ids: set[str] = set()
    for innings in ledger["innings"]:
        # Keep enough subsequent live play for every delayed correction. This
        # prevents artificial end-of-document cleanup notes.
        eligible_events = innings["events"][:-profile["eligible_tail_buffer"]]
        score_candidates = [e for e in eligible_events if e["batter_runs"] > 0 or e["extras_runs"] > 0]
        if profile_name == "r8_radio_nonperiodic":
            # One revision is selected from every temporal stratum by a stable
            # hash.  This keeps broad coverage without exposing a fixed cadence.
            for i in range(profile["revision_per_innings"]):
                start = i * len(score_candidates) // profile["revision_per_innings"]
                end = (i + 1) * len(score_candidates) // profile["revision_per_innings"]
                bucket = score_candidates[start:end]
                if not bucket:
                    raise ValueError("Too few scoring events for the R8 revision strata")
                selected = min(
                    bucket,
                    key=lambda event: stable_int(root["root_id"], event["event_id"], "revision"),
                )
                revision_ids.add(selected["event_id"])
        else:
            revision_ids.update(
                score_candidates[
                    round(i * (len(score_candidates) - 1) / (profile["revision_per_innings"] - 1))
                ]["event_id"]
                for i in range(profile["revision_per_innings"])
            )
    stale_ids = (
        {
            event_id for event_id in revision_ids
            if stable_int(root["root_id"], event_id, "stale") % 3 != 0
        }
        if profile_name == "r8_radio_nonperiodic" else set(sorted(revision_ids)[::2])
    )
    nonperiodic_replay_ids: set[str] = set()
    if profile_name == "r8_radio_nonperiodic":
        replay_candidates = [
            event for innings in ledger["innings"] for event in innings["events"]
            if event["event_id"] not in revision_ids
        ]
        wanted = round(len(replay_candidates) * profile["replay_fraction"])
        nonperiodic_replay_ids = {
            event["event_id"] for event in sorted(
                replay_candidates,
                key=lambda event: stable_int(root["root_id"], event["event_id"], "replay"),
            )[:wanted]
        }
    pending: list[dict[str, Any]] = []
    event_counter = 0
    replay_counter = 0

    for innings_pos, innings in enumerate(ledger["innings"], start=1):
        add(
            "innings_transition",
            f"The {innings_pos}{'st' if innings_pos == 1 else 'nd'} innings begins with {innings['team']} batting. "
            + (
                f"The radio desk opens a fresh scoring sheet while {innings['team']}'s openers are described walking out."
                if profile_name == "r8_radio_nonperiodic"
                else (
                    f"The live-blog opens a fresh innings thread as {innings['team']}'s opening pair walk out."
                    if profile_name == "r7_live_blog"
                    else f"The field settles as the live camera follows {innings['team']}'s opening pair to the middle."
                )
            ),
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
                alternate, alternate_event = alternate_claim(event, event_counter, profile_name)
                provisional_sid = add(
                    "provisional_graphic",
                    provisional_description(event, alternate, alternate_event),
                    [event["event_id"]],
                )
                pending.append({
                    "release_at": event_counter + ranged_delay(
                        profile["correction_delay_events"], event["event_id"], "correction"
                    ),
                    "review_at": (
                        None if profile["review_delay_events"] is None
                        else event_counter + ranged_delay(
                            profile["review_delay_events"], event["event_id"], "review"
                        )
                    ),
                    "review_segment": None,
                    "event": event,
                    "alternate": alternate,
                    "alternate_event": alternate_event,
                    "provisional_segment": provisional_sid,
                    "stale": event["event_id"] in stale_ids,
                })
            else:
                sid = add("live_delivery", event_description(event), [event["event_id"]])
                accepted_segment_by_event[event["event_id"]] = sid
                should_replay = (
                    event["event_id"] in nonperiodic_replay_ids
                    if profile_name == "r8_radio_nonperiodic"
                    else event_counter % profile["replay_interval"] == 0
                )
                if should_replay:
                    replay_counter += 1
                    replay_openers = (
                        ("The producer's delayed monitor silently returns to ",
                         "An analyst describes a replay of ",
                         "The scorer telephone asks for another listen to ")
                        if profile_name == "r8_radio_nonperiodic" else
                        ("The square-leg replay returns to ",
                         "A slow-motion cut revisits ",
                         "The live blog embeds another angle of ")
                    )
                    replay_sid = add(
                        "same_delivery_replay",
                        replay_openers[(replay_counter - 1) % len(replay_openers)]
                        + event_description(event, prefix="the same delivery, replay of "),
                        [event["event_id"]],
                    )
                    replay_event_ids.append(event["event_id"])

            for item in pending:
                if (
                    item["review_at"] is not None
                    and item["review_at"] <= event_counter
                    and item["review_segment"] is None
                ):
                    label = item["event"]["delivery_label"].split("x", 1)[0]
                    review_openers = (
                        "Two scorer feeds now disagree over",
                        "The live desk quietly reopens",
                        "A scorer query is attached to",
                    )
                    item["review_segment"] = add(
                        "scorer_review_pending",
                        f"{review_openers[int(label.split('.')[0]) % len(review_openers)]} "
                        f"the {innings_ref(item['event'])} {label} entry from {item['event']['bowler']} "
                        f"to {item['event']['striker']} under production cue "
                        f"{event_serial(item['event'])}; "
                        "the scorer withholds a ruling and the live sequence continues.",
                        [item["event"]["event_id"]],
                    )

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
                record = {
                    "event_id": item["event"]["event_id"],
                    "correct_value": item["event"]["extras_runs"] if item["event"]["extras_type"] else item["event"]["batter_runs"],
                    "alternate_value": item["alternate"],
                    "alternate_event": item["alternate_event"],
                    "provisional_segment": item["provisional_segment"],
                    "review_segment": item["review_segment"],
                    "correction_segment": correction_sid,
                    "stale_segment": None,
                }
                revision_records.append(record)
                if item["stale"] and profile["stale_delay_events"] == 0:
                    record["stale_segment"] = add(
                        "stale_highlight_graphic",
                        f"A highlight cut briefly restores the old ribbon with {item['alternate']} on the "
                        f"{innings_ref(item['event'])} {item['event']['delivery_label'].split('x',1)[0]} entry, "
                        "which the commentator identifies as the pre-correction picture.",
                        [item["event"]["event_id"]],
                    )
                elif item["stale"]:
                    pending_stale.append({
                        "release_at": event_counter + ranged_delay(
                            profile["stale_delay_events"], item["event"]["event_id"], "stale-delay"
                        ),
                        "item": item,
                        "record": record,
                    })

            stale_ready = [item for item in pending_stale if item["release_at"] <= event_counter]
            pending_stale = [item for item in pending_stale if item["release_at"] > event_counter]
            for stale in stale_ready:
                item = stale["item"]
                stale["record"]["stale_segment"] = add(
                    "stale_highlight_graphic",
                    f"A later highlight card again shows {item['alternate']} beside "
                    f"{innings_ref(item['event'])} {item['event']['delivery_label'].split('x',1)[0]}, "
                    f"the call from {item['event']['bowler']} to {item['event']['striker']} under production cue "
                    f"{event_serial(item['event'])}; "
                    "the live-blog flags that card as an archived, superseded version.",
                    [item["event"]["event_id"]],
                )

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
            "alternate_event": item["alternate_event"],
            "provisional_segment": item["provisional_segment"],
            "review_segment": item["review_segment"],
            "correction_segment": correction_sid,
            "stale_segment": stale_sid,
        })

    for stale in pending_stale:
        item = stale["item"]
        stale["record"]["stale_segment"] = add(
            "stale_highlight_graphic",
            f"The closing archive card repeats {item['alternate']} for "
            f"{innings_ref(item['event'])} {item['event']['delivery_label'].split('x',1)[0]}, "
            "and the presenter marks it as an obsolete graphic.",
            [item["event"]["event_id"]],
        )

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
                        if canon(e["striker"]) == name
                        or (int(row["B"]) == 0 and canon(e["non_striker"]) == name)
                        or (e["dismissal"] and canon(e["dismissal"]["batter"]) == name)
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
        "instance_id": profile["instance_id"],
        "instruction": "Reconstruct the complete scorecard tables from the supplied delivery commentary.",
        "document": {"document_id": "delivery_commentary", "text": document_text},
        "tables": public_tables,
        "output_rule": "Return every supplied table and fill every blank cell while preserving row keys and columns.",
    }
    private = {
        "instance_id": profile["instance_id"],
        "root_id": root["root_id"],
        "gold_tables": gold_tables,
        "scored_cell_ids": scored,
        "challenge_cell_ids": challenges,
    }
    evidence = {
        "instance_id": profile["instance_id"],
        "difficulty_profile": profile_name,
        "profile_parameters": profile,
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
    parser.add_argument("--profile", choices=sorted(PROFILES), default="r6_broadcast")
    args = parser.parse_args()
    root = json.loads(args.root.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    public, private, evidence = build(root, ledger, args.profile)
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
        "pending_reviews": sum(bool(x.get("review_segment")) for x in evidence["revision_records"]),
        "replays": len(evidence["replay_event_ids"]),
    }, indent=2))


if __name__ == "__main__":
    main()
