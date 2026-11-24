#!/usr/bin/env python3
"""Transform the admitted R8 instance into a lower-repetition R9 stress variant.

R9 keeps the same validated event ledger and gold tables. It removes most
shadow-feed recaps and replaces every compact official correction with two
nonadjacent authority fragments: one certifies event class/legal status and a
later fragment supplies the accepted magnitude. Neither fragment is sufficient
for scored events on its own.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def event_serial(event: dict[str, Any]) -> int:
    return int(re.search(r"(\d+)$", event["event_id"]).group(1))


def stable_int(*parts: str) -> int:
    return int.from_bytes(hashlib.sha256("\x1f".join(parts).encode()).digest()[:8], "big")


def innings_ref(event: dict[str, Any]) -> str:
    return "first innings" if event["innings_id"] == "I1" else "second innings"


def classification_text(event: dict[str, Any]) -> str:
    label = event["delivery_label"].split("x", 1)[0]
    cue = event_serial(event)
    if event["extras_type"]:
        category = {
            "wide": "a wide with no batter credit",
            "no_ball": "a no-ball with no batter credit",
            "bye": "byes after the bat was missed",
            "leg_bye": "leg-byes from pad contact",
        }[event["extras_type"]]
    else:
        category = "runs credited to the batter rather than to any extras account"
    legal = "legal-ball sequence advances" if event["is_legal"] else "legal-ball sequence does not advance"
    return (
        f"The scorer telephone partially closes {innings_ref(event)} production cue {cue}. For the "
        f"entry at {label}, {event['bowler']} to {event['striker']}, authority now classifies the call "
        f"as {category}, and confirms that the {legal}. The accepted numeral is still withheld."
    )


def magnitude_text(event: dict[str, Any]) -> str:
    cue = event_serial(event)
    amount = event["extras_runs"] if event["extras_type"] else event["batter_runs"]
    variants = (
        "the console accepts {amount} for the category certified earlier and voids every older numeral",
        "the earlier category now receives magnitude {amount}, superseding the open ribbon",
        "magnitude {amount} is attached to the prior telephone classification and the provisional number is retired",
        "the certified category is closed at {amount}, with the first numerical claim marked obsolete",
    )
    clause = variants[stable_int(event["event_id"], "magnitude-wording") % len(variants)].format(amount=amount)
    return (
        f"After further live play, the independent scoring console closes {innings_ref(event)} "
        f"production cue {cue}: {clause}."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--replay-keep-fraction", type=float, default=0.48)
    args = parser.parse_args()

    public = json.loads(args.public.read_text(encoding="utf-8"))
    private = json.loads(args.private.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    event_by_id = {
        event["event_id"]: event
        for innings in evidence["event_ledger"]["innings"]
        for event in innings["events"]
    }

    replay_segments = [s for s in evidence["segments"] if s["kind"] == "same_delivery_replay"]
    keep_count = round(len(replay_segments) * args.replay_keep_fraction)
    kept_replay_old_ids = {
        segment["segment_id"] for segment in sorted(
            replay_segments,
            key=lambda segment: stable_int(segment["event_ids"][0], segment["segment_id"], "r9-replay"),
        )[:keep_count]
    }

    correction_old_ids = {
        row["correction_segment"] for row in evidence["revision_records"]
    }
    stale_to_correction = {
        row["stale_segment"]: row["correction_segment"]
        for row in evidence["revision_records"] if row.get("stale_segment")
    }
    magnitude_position_by_correction: dict[str, float] = {}
    staged: list[dict[str, Any]] = []
    old_to_node_keys: dict[str, list[str]] = {}
    for pos, segment in enumerate(evidence["segments"]):
        old_id = segment["segment_id"]
        if segment["kind"] == "same_delivery_replay" and old_id not in kept_replay_old_ids:
            old_to_node_keys[old_id] = []
            continue
        if old_id in correction_old_ids:
            event = event_by_id[segment["event_ids"][0]]
            class_key = old_id + ".CLASS"
            magnitude_key = old_id + ".MAG"
            delay = 7 + stable_int(event["event_id"], "r9-split-delay") % 13
            staged.append({
                "node_key": class_key,
                "position": pos * 100,
                "kind": "authority_classification_fragment",
                "text": classification_text(event),
                "event_ids": [event["event_id"]],
            })
            staged.append({
                "node_key": magnitude_key,
                "position": (pos + delay) * 100 + 50 + event_serial(event) / 1000,
                "kind": "authority_magnitude_fragment",
                "text": magnitude_text(event),
                "event_ids": [event["event_id"]],
            })
            magnitude_position_by_correction[old_id] = (
                (pos + delay) * 100 + 50 + event_serial(event) / 1000
            )
            old_to_node_keys[old_id] = [class_key, magnitude_key]
            continue
        node_key = old_id + ".KEEP"
        text = segment["text"].replace("live-blog", "radio desk").replace(
            "first television ribbon", "first live scoring ribbon"
        )
        position = pos * 100
        if old_id in stale_to_correction:
            position = max(
                position,
                magnitude_position_by_correction[stale_to_correction[old_id]] + 1000,
            )
        staged.append({
            "node_key": node_key,
            "position": position,
            "kind": segment["kind"],
            "text": text,
            "event_ids": segment.get("event_ids", []),
        })
        old_to_node_keys[old_id] = [node_key]

    staged.sort(key=lambda node: (node["position"], node["node_key"]))
    # Guarantee an actual, not merely coordinate-based, separation between a
    # completed authority chain and any later stale return of the old graphic.
    for record in evidence["revision_records"]:
        if not record.get("stale_segment"):
            continue
        magnitude_key = record["correction_segment"] + ".MAG"
        stale_key = record["stale_segment"] + ".KEEP"
        magnitude_index = next(i for i, node in enumerate(staged) if node["node_key"] == magnitude_key)
        stale_index = next(i for i, node in enumerate(staged) if node["node_key"] == stale_key)
        if stale_index - magnitude_index < 10:
            stale_node = staged.pop(stale_index)
            magnitude_index = next(i for i, node in enumerate(staged) if node["node_key"] == magnitude_key)
            staged.insert(min(magnitude_index + 10, len(staged)), stale_node)
    node_to_sid = {node["node_key"]: f"s{pos:04d}" for pos, node in enumerate(staged, start=1)}
    old_to_sids = {
        old_id: [node_to_sid[key] for key in keys]
        for old_id, keys in old_to_node_keys.items()
    }

    parts: list[str] = []
    cursor = 0
    spans: dict[str, dict[str, int]] = {}
    new_segments = []
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
            "segment_id": sid,
            "kind": node["kind"],
            "text": node["text"],
            "event_ids": node["event_ids"],
            **spans[sid],
        })
    document_text = "".join(parts)

    new_records = []
    for record in evidence["revision_records"]:
        updated = copy.deepcopy(record)
        split_sids = old_to_sids[record["correction_segment"]]
        updated["provisional_segment"] = old_to_sids[record["provisional_segment"]][0]
        updated["review_segment"] = (
            old_to_sids[record["review_segment"]][0] if record.get("review_segment") else None
        )
        updated["classification_segment"] = split_sids[0]
        updated["magnitude_segment"] = split_sids[1]
        updated["resolution_segments"] = split_sids
        updated["correction_segment"] = split_sids[1]
        updated["stale_segment"] = (
            old_to_sids[record["stale_segment"]][0] if record.get("stale_segment") else None
        )
        new_records.append(updated)

    new_cells = []
    for cell in evidence["cells"]:
        updated = copy.deepcopy(cell)
        new_refs = []
        for ref in cell["evidence"]:
            for sid in old_to_sids.get(ref["segment_id"], []):
                new_refs.append({"segment_id": sid, **spans[sid]})
        updated["evidence"] = new_refs
        new_cells.append(updated)

    retained_replay_ids = [
        segment["event_ids"][0] for segment in replay_segments
        if segment["segment_id"] in kept_replay_old_ids
    ]
    public["instance_id"] = "r9d_0001"
    public["document"]["text"] = document_text
    private["instance_id"] = "r9d_0001"
    evidence.update({
        "instance_id": "r9d_0001",
        "difficulty_profile": "r9_split_authority",
        "profile_parameters": {
            "source_profile": "r8_radio_nonperiodic",
            "revision_chains": len(new_records),
            "authority_fragments_per_revision": 2,
            "split_delay_base_segments": [7, 19],
            "replay_keep_fraction_of_r8": args.replay_keep_fraction,
            "selection_rule": "stable_hash_nonperiodic",
        },
        "document_sha256": hashlib.sha256(document_text.encode()).hexdigest(),
        "segments": new_segments,
        "cells": new_cells,
        "revision_records": new_records,
        "replay_event_ids": retained_replay_ids,
    })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "r9_public.json").write_text(
        json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "r9_private_gold.json").write_text(
        json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "r9_private_evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "words": len(document_text.split()),
        "segments": len(new_segments),
        "revision_chains": len(new_records),
        "authority_fragments": len(new_records) * 2,
        "retained_replays": len(retained_replay_ids),
        "removed_replays": len(replay_segments) - len(retained_replay_ids),
    }, indent=2))


if __name__ == "__main__":
    main()
