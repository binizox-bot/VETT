#!/usr/bin/env python3
"""Build R10: implicit revision links, relational magnitudes, and interval audits."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def stable_int(*parts: str) -> int:
    return int.from_bytes(hashlib.sha256("\x1f".join(parts).encode()).digest()[:8], "big")


def innings_ref(event: dict[str, Any]) -> str:
    return "first innings" if event["innings_id"] == "I1" else "second innings"


def outcome_class(event: dict[str, Any]) -> str:
    if event["extras_type"]:
        return {
            "wide": "a wide outside the legal-ball count with no batter credit",
            "no_ball": "a no-ball outside the legal-ball count with no batter credit",
            "bye": "legal-ball byes after the bat was missed",
            "leg_bye": "legal-ball leg-byes following pad contact",
        }[event["extras_type"]]
    return "a legal-ball scoring stroke credited to the batter with no extras component"


def link_phrase(event: dict[str, Any], include_marker: bool, occurrence_tag: str = "") -> str:
    over_number = int(event["delivery_label"].split(".", 1)[0]) + 1
    base = (
        f"the {innings_ref(event)} line from {event['bowler']} to {event['striker']}, "
        f"with {event['non_striker']} at the other end during over {over_number}, "
        f"after {event['wickets_after']} wickets had fallen"
    )
    if include_marker:
        base += f", whose delivery marker was {event['delivery_label'].split('x', 1)[0]}"
    if occurrence_tag:
        base += f", identified as {occurrence_tag} under that repeated marker"
    return base


def classification_text(event: dict[str, Any], include_marker: bool, occurrence_tag: str = "") -> str:
    return (
        f"At delivery {event['delivery_label'].split('x', 1)[0]}, the scorer reopens "
        f"{link_phrase(event, False, occurrence_tag)}; authority certifies it as {outcome_class(event)}, "
        "while its numerical component remains unresolved through the next passage of live play."
    )


def magnitude_text(
    event: dict[str, Any], alternate: int, correct: int, include_marker: bool, relational: bool,
    occurrence_tag: str = "",
) -> str:
    link = link_phrase(event, include_marker, occurrence_tag)
    variants = (
        "The independent console later returns to {link}: {claim}, and the earlier class ruling remains controlling.",
        "Much later, the scoring desk closes {link}; {claim}, under the category already certified.",
        "After another passage of play, officials settle {link}: {claim}, without reopening its event class.",
        "The delayed reconciliation finally reaches {link}; {claim}, while the prior classification stands.",
    )
    if relational:
        delta = correct - alternate
        if delta == 1:
            claim = "the accepted figure is one higher than the number on the first ribbon"
        elif delta == -1:
            claim = "the accepted figure is one lower than the number on the first ribbon"
        elif delta == 0:
            claim = "the numerical figure remains the one first shown even though its accounting class changed"
        else:
            claim = f"the accepted figure differs from the first ribbon by {abs(delta)}"
    else:
        claim = f"the accepted magnitude is {correct}"
    template = variants[stable_int(event["event_id"], "r10-magnitude-style") % len(variants)]
    return template.format(link=link, claim=claim)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-fraction-of-events", type=float, default=0.35)
    args = parser.parse_args()

    public = json.loads(args.public.read_text(encoding="utf-8"))
    private = json.loads(args.private.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    ledger = evidence["event_ledger"]
    event_by_id = {
        event["event_id"]: event for innings in ledger["innings"] for event in innings["events"]
    }
    segment_by_id = {segment["segment_id"]: segment for segment in evidence["segments"]}
    old_index = {segment["segment_id"]: pos for pos, segment in enumerate(evidence["segments"])}

    ordinal_words = {1: "the first call", 2: "the second call", 3: "the third call", 4: "the fourth call"}
    occurrence_tag_by_event: dict[str, str] = {}
    for innings in ledger["innings"]:
        totals: dict[str, int] = {}
        seen: dict[str, int] = {}
        for event in innings["events"]:
            label = event["delivery_label"].split("x", 1)[0]
            totals[label] = totals.get(label, 0) + 1
        for event in innings["events"]:
            label = event["delivery_label"].split("x", 1)[0]
            seen[label] = seen.get(label, 0) + 1
            if totals[label] > 1:
                occurrence_tag_by_event[event["event_id"]] = ordinal_words.get(
                    seen[label], f"call number {seen[label]}"
                )

    replay_segments = [s for s in evidence["segments"] if s["kind"] == "same_delivery_replay"]
    total_events = len(event_by_id)
    wanted_replays = min(len(replay_segments), round(total_events * args.replay_fraction_of_events))
    kept_replay_old_ids = {
        segment["segment_id"] for segment in sorted(
            replay_segments,
            key=lambda segment: stable_int(segment["event_ids"][0], "r10-replay"),
        )[:wanted_replays]
    }

    # Determine whether participant/state features identify exactly one still-open
    # revision at the time its numerical fragment arrives.
    def signature(event: dict[str, Any]) -> tuple[Any, ...]:
        return (
            event["innings_id"], event["bowler"], event["striker"], event["non_striker"],
            event["is_legal"], event["extras_type"] or "bat",
        )

    link_audit = []
    rewrite_by_sid: dict[str, str] = {}
    relational_event_ids: set[str] = set()
    for record in evidence["revision_records"]:
        event = event_by_id[record["event_id"]]
        magnitude_pos = old_index[record["magnitude_segment"]]
        active_candidates = []
        for other in evidence["revision_records"]:
            other_event = event_by_id[other["event_id"]]
            if (
                signature(other_event) == signature(event)
                and old_index[other["classification_segment"]] < magnitude_pos
                <= old_index[other["magnitude_segment"]]
            ):
                active_candidates.append(other["event_id"])
        include_marker = len(active_candidates) != 1
        relational = stable_int(event["event_id"], "r10-relational") % 10 < 8
        if relational:
            relational_event_ids.add(event["event_id"])
        occurrence_tag = occurrence_tag_by_event.get(event["event_id"], "")
        rewrite_by_sid[record["classification_segment"]] = classification_text(
            event, include_marker, occurrence_tag
        )
        rewrite_by_sid[record["magnitude_segment"]] = magnitude_text(
            event, record["alternate_value"], record["correct_value"], include_marker, relational,
            occurrence_tag,
        )
        link_audit.append({
            "event_id": event["event_id"],
            "active_candidate_count": len(active_candidates),
            "link_mode": "delivery_marker_fallback" if include_marker else "implicit_state_signature",
            "magnitude_mode": "relation_to_provisional" if relational else "direct_magnitude",
            "state_signature": list(signature(event)),
        })

    staged = []
    old_to_node_key: dict[str, str | None] = {}
    for pos, segment in enumerate(evidence["segments"]):
        old_sid = segment["segment_id"]
        if segment["kind"] == "same_delivery_replay" and old_sid not in kept_replay_old_ids:
            old_to_node_key[old_sid] = None
            continue
        key = old_sid + ".KEEP"
        text = rewrite_by_sid.get(old_sid, segment["text"])
        text = text.replace("production cue", "scoring reference").replace("live-blog", "radio desk")
        segment_occurrence_tag = (
            occurrence_tag_by_event.get(segment.get("event_ids", [None])[0], "")
            if segment.get("event_ids") else ""
        )
        open_line_phrase = (
            f"on {segment_occurrence_tag} under the repeated marker"
            if segment_occurrence_tag else "on the still-open scorer line"
        )
        text = re.sub(
            r"under scoring reference\s+\d+",
            open_line_phrase,
            text,
            flags=re.I,
        )
        staged.append({
            "node_key": key, "position": pos * 100, "kind": segment["kind"],
            "text": text, "event_ids": segment.get("event_ids", []),
        })
        old_to_node_key[old_sid] = key

    # Six non-overlapping five-over interval checks. They are redundant audit
    # statements, explicitly not new events, and create a conservation/dedup test.
    checkpoint_groups = []
    for innings in ledger["innings"]:
        events = innings["events"]
        for start_over in (0, 10, 20):
            group = [
                event for event in events
                if start_over <= int(event["delivery_label"].split(".", 1)[0]) < start_over + 5
            ]
            if not group:
                continue
            event_ids = [event["event_id"] for event in group]
            first_positions = [
                min(old_index[s["segment_id"]] for s in evidence["segments"] if event_id in s.get("event_ids", []))
                for event_id in event_ids
            ]
            runs = sum(event["batter_runs"] + event["extras_runs"] for event in group)
            wickets = sum(bool(event["dismissal"]) for event in group)
            checkpoint_id = f"{innings['innings_id']}.C{len(checkpoint_groups)+1:02d}"
            wicket_word = "wicket" if wickets == 1 else "wickets"
            text = (
                f"A separate ledger reconciliation for {innings_ref(group[0])}, overs {start_over + 1} "
                f"through {start_over + 5}, records a movement of {runs} runs and {wickets} {wicket_word} "
                "since the preceding audit boundary, and the desk explicitly treats this as a conservation "
                "check over calls already heard rather than additional play."
            )
            staged.append({
                "node_key": checkpoint_id, "position": max(first_positions) * 100 + 80,
                "kind": "interval_conservation_checkpoint", "text": text, "event_ids": event_ids,
            })
            checkpoint_groups.append({
                "checkpoint_id": checkpoint_id, "innings_id": innings["innings_id"],
                "over_range": [start_over, start_over + 4], "runs": runs,
                "wickets": wickets, "event_ids": event_ids,
            })

    staged.sort(key=lambda node: (node["position"], node["node_key"]))
    node_to_sid = {node["node_key"]: f"s{pos:04d}" for pos, node in enumerate(staged, start=1)}
    old_to_sid = {
        old_sid: (node_to_sid[key] if key is not None else None)
        for old_sid, key in old_to_node_key.items()
    }

    parts, cursor, spans, new_segments = [], 0, {}, []
    for node in staged:
        sid = node_to_sid[node["node_key"]]
        if parts:
            parts.append("\n\n")
            cursor += 2
        start = cursor
        parts.append(node["text"])
        cursor += len(node["text"])
        spans[sid] = {"start": start, "end": cursor}
        new_segments.append({
            "segment_id": sid, "kind": node["kind"], "text": node["text"],
            "event_ids": node["event_ids"], **spans[sid],
        })
    document_text = "".join(parts)

    new_records = []
    for record in evidence["revision_records"]:
        updated = copy.deepcopy(record)
        for field in (
            "provisional_segment", "review_segment", "classification_segment",
            "magnitude_segment", "correction_segment", "stale_segment",
        ):
            if updated.get(field):
                updated[field] = old_to_sid[updated[field]]
        updated["resolution_segments"] = [
            updated["classification_segment"], updated["magnitude_segment"]
        ]
        updated["magnitude_mode"] = (
            "relation_to_provisional" if record["event_id"] in relational_event_ids else "direct_magnitude"
        )
        new_records.append(updated)

    record_by_event = {record["event_id"]: record for record in new_records}
    new_cells = []
    for cell in evidence["cells"]:
        updated = copy.deepcopy(cell)
        mapped = []
        for ref in cell["evidence"]:
            sid = old_to_sid.get(ref["segment_id"])
            if sid:
                mapped.append({"segment_id": sid, **spans[sid]})
        for event_id in cell["event_ids"]:
            if event_id in relational_event_ids:
                provisional_sid = record_by_event[event_id]["provisional_segment"]
                if provisional_sid not in {ref["segment_id"] for ref in mapped}:
                    mapped.append({"segment_id": provisional_sid, **spans[provisional_sid]})
        updated["evidence"] = sorted(mapped, key=lambda ref: int(ref["segment_id"][1:]))
        new_cells.append(updated)

    retained_replay_ids = [
        segment["event_ids"][0] for segment in replay_segments
        if segment["segment_id"] in kept_replay_old_ids
    ]
    public["instance_id"] = "r10e_0001"
    public["document"]["text"] = document_text
    private["instance_id"] = "r10e_0001"
    evidence.update({
        "instance_id": "r10e_0001",
        "difficulty_profile": "r10_implicit_fourth_root",
        "profile_parameters": {
            "source_profile": "r9_split_authority",
            "replay_fraction_of_atomic_events": args.replay_fraction_of_events,
            "relational_magnitude_target": 0.80,
            "explicit_numeric_cues": 0,
            "interval_checkpoint_groups": len(checkpoint_groups),
        },
        "document_sha256": hashlib.sha256(document_text.encode()).hexdigest(),
        "segments": new_segments,
        "cells": new_cells,
        "revision_records": new_records,
        "replay_event_ids": retained_replay_ids,
        "checkpoint_event_groups": checkpoint_groups,
        "implicit_link_audit": link_audit,
    })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in (
        ("r10_public.json", public),
        ("r10_private_gold.json", private),
        ("r10_private_evidence.json", evidence),
    ):
        (args.output_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps({
        "words": len(document_text.split()), "segments": len(new_segments),
        "atomic_events": total_events, "retained_replays": len(retained_replay_ids),
        "relational_magnitudes": len(relational_event_ids),
        "implicit_unique_links": sum(x["link_mode"] == "implicit_state_signature" for x in link_audit),
        "marker_fallbacks": sum(x["link_mode"] == "delivery_marker_fallback" for x in link_audit),
        "checkpoint_groups": len(checkpoint_groups),
    }, indent=2))


if __name__ == "__main__":
    main()
