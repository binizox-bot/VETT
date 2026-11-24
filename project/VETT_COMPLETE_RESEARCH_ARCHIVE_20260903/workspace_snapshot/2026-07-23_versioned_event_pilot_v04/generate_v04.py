"""Generate a versioned-event, multi-feed Text-to-Table stress test.

The canonical innings comes from the independently solved v0.3 event stream.
This generator renders it as a non-monotonic multi-source transcript containing
duplicates, provisional reports, final corrections, stale replays and
out-of-scope match snippets. Visible text contains no event IDs.
"""

import json
import random
from pathlib import Path


rng = random.Random(20260723)
root = Path(__file__).resolve().parent
source_root = root.parent / "2026-07-22_natural_pilot_v03"

integrated = json.loads(
    (source_root / "t3_stage2_integrated.json").read_text(encoding="utf-8")
)
events = integrated["events"]
gold = json.loads((source_root / "pilot_v03_gold.json").read_text(encoding="utf-8"))

batters = list(gold["batting"])
bowlers = list(gold["bowling"])
run_words = {
    0: "no run",
    1: "one bat run",
    2: "two bat runs",
    3: "three bat runs",
    4: "four bat runs",
    6: "six bat runs",
    8: "eight bat runs",
}
ordinal_words = {
    1: "first", 2: "second", 3: "third",
    4: "fourth", 5: "fifth", 6: "sixth",
}


def normalized_outcome(event):
    return {
        "bat": event.get("bat", 0),
        "leg_byes": event.get("leg_byes", 0),
        "wicket": bool(event.get("wicket")),
    }


def describe(outcome, batter, bowler):
    if outcome["wicket"]:
        return f"{bowler} has {batter} caught for no run"
    if outcome["leg_byes"]:
        return (
            f"{batter} faces {bowler}; {outcome['leg_byes']} leg-byes are signalled"
        )
    return f"{bowler} to {batter}: {run_words[outcome['bat']]}"


def corrupt_outcome(final, index):
    if final["wicket"]:
        return {"bat": 0, "leg_byes": 0, "wicket": False}
    if index % 4 == 0:
        return {"bat": 0, "leg_byes": 0, "wicket": True}
    if final["leg_byes"]:
        return {
            "bat": final["leg_byes"],
            "leg_byes": 0,
            "wicket": False,
        }
    value = final["bat"]
    if value >= 2:
        wrong = value - 2
    elif value == 1:
        wrong = 3
    else:
        wrong = 4
    return {"bat": wrong, "leg_byes": 0, "wicket": False}


for position, event in enumerate(events, 1):
    event["position"] = position
    event["event_id"] = f"e_{position:03d}"

wicket_positions = [
    event["position"] for event in events if event.get("wicket")
]
non_wickets = [
    event["position"] for event in events if not event.get("wicket")
]
revision_positions = set(wicket_positions)
revision_positions.update(rng.sample(non_wickets, 25))
duplicate_positions = set(rng.sample(range(1, len(events) + 1), 24))
stale_positions = set(rng.sample(sorted(revision_positions), 18))
scope_positions = rng.sample(range(1, len(events) + 1), 18)

mentions = []
visible_sections = []
arrival = 0


def add_mention(event, role, source, outcome, text, surface_event=None):
    global arrival
    arrival += 1
    identity_event = event if event is not None else surface_event
    mention = {
        "mention_id": f"m_{arrival:03d}",
        "event_id": event["event_id"] if event else None,
        "batter": identity_event["batter"],
        "bowler": identity_event["bowler"],
        "arrival_order": arrival,
        "role": role,
        "source": source,
        "outcome": outcome,
        "text": text,
    }
    mentions.append(mention)
    visible_sections.append(text)


visible_sections.extend([
    "SCORING RULES",
    "- Commentary packets are shown in arrival order, not necessarily event order.",
    "- Delayed replay and cached audio may repeat an event already heard.",
    "- A final scorer ruling replaces the referenced earlier passage.",
    "- A cached replay recorded before a ruling never overrides that ruling.",
    "- Youth and archive tickers are not part of the target match.",
    "- Leg-byes count for team and partnership but not batter or bowler.",
    "",
    "OUTPUT",
    "Return final summary, all batting rows, all bowling rows, fall of wickets and all partnerships.",
    "",
    "PRIMARY LIVE FEED",
])

for over in range(1, 13):
    over_events = [event for event in events if event["over"] == over]
    bowler = over_events[0]["bowler"]
    visible_sections.append(f"{bowler}'s {'opening' if over <= 6 else 'return'} spell, over {over}:")
    for passage, event in enumerate(over_events, 1):
        final = normalized_outcome(event)
        initial = (
            corrupt_outcome(final, event["position"])
            if event["position"] in revision_positions
            else final
        )
        event["initial_outcome"] = initial
        live_text = f"  Next passage: {describe(initial, event['batter'], event['bowler'])}."
        add_mention(event, "INITIAL", "live", initial, live_text)

        if event["position"] in duplicate_positions:
            replay_text = (
                f"  Delayed replay from this target innings, already heard: "
                f"{describe(initial, event['batter'], event['bowler'])}."
            )
            add_mention(event, "DUPLICATE", "delayed_replay", initial, replay_text)

    if over in (2, 4, 6, 8, 10, 12):
        distractor = events[scope_positions[(over // 2) - 1]]
        distractor_outcome = normalized_outcome(distractor)
        archive_text = (
            f"  Harbor youth ticker, a different match: "
            f"{describe(distractor_outcome, distractor['batter'], distractor['bowler'])}."
        )
        add_mention(
            None,
            "OUT_OF_SCOPE",
            "youth_ticker",
            distractor_outcome,
            archive_text,
            surface_event=distractor,
        )

visible_sections.extend(["", "FINAL SCORER RULINGS"])
for position in sorted(revision_positions, reverse=True):
    event = events[position - 1]
    final = normalized_outcome(event)
    passage = event["ball"]
    ruling_text = (
        f"Final ruling: in over {event['over']}, replace the "
        f"{ordinal_words[passage]} passage of {event['bowler']}'s spell. "
        f"The ratified event is: {describe(final, event['batter'], event['bowler'])}."
    )
    add_mention(event, "FINAL_REVISION", "official_scorer", final, ruling_text)

visible_sections.extend(["", "LATE CACHE AND ARCHIVE PACKETS"])
for position in sorted(stale_positions):
    event = events[position - 1]
    initial = event["initial_outcome"]
    stale_text = (
        f"Cached radio replay recorded before the final rulings: "
        f"{describe(initial, event['batter'], event['bowler'])}. "
        "This is stale audio."
    )
    add_mention(event, "STALE", "radio_cache", initial, stale_text)

for offset, position in enumerate(scope_positions[6:], 1):
    event = events[position - 1]
    outcome = normalized_outcome(event)
    scope_text = (
        f"Archive packet {offset}, previous fixture at this ground: "
        f"{describe(outcome, event['batter'], event['bowler'])}."
    )
    add_mention(
        None,
        "OUT_OF_SCOPE",
        "archive",
        outcome,
        scope_text,
        surface_event=event,
    )

visible_sections.extend([
    "",
    "The final scorer rulings are authoritative. Replays, cached audio, youth tickers,",
    "and archive packets do not create target-match events.",
])

hidden_graph = {
    "canonical_events": [
        {
            "event_id": event["event_id"],
            "over": event["over"],
            "passage": event["ball"],
            "bowler": event["bowler"],
            "batter": event["batter"],
            "final_outcome": normalized_outcome(event),
            "initial_outcome": event["initial_outcome"],
        }
        for event in events
    ],
    "mentions": mentions,
    "revision_positions": sorted(revision_positions),
    "duplicate_positions": sorted(duplicate_positions),
    "stale_positions": sorted(stale_positions),
    "scope_count": sum(m["role"] == "OUT_OF_SCOPE" for m in mentions),
    "final_state_is_unique": True,
}

(root / "v04_case.txt").write_text("\n".join(visible_sections), encoding="utf-8")
(root / "v04_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
(root / "v04_hidden_event_graph.json").write_text(
    json.dumps(hidden_graph, indent=2),
    encoding="utf-8",
)
(root / "v04_canonical_events.json").write_text(
    json.dumps(events, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    "canonical_events": len(events),
    "mentions": len(mentions),
    "revision_chains": len(revision_positions),
    "duplicates": len(duplicate_positions),
    "stale_replays": len(stale_positions),
    "out_of_scope_mentions": hidden_graph["scope_count"],
    "unique_final_state": True,
}, indent=2))
