"""Generate a recursive-source, shuffled-evidence Text-to-Table stress test.

The target innings contains 72 canonical events.  Each event is reported by
four mutually conflicting sources.  The accepted source is determined by a
stateful audit rule: resolving one slot changes the state needed to resolve the
next slot.  Evidence packets are shown out of order, and rehearsal packets from
a counterfactual chain share the same players and venue.

The visible rule uniquely determines the final event sequence.  The hidden
graph and gold tables are written only for verification and scoring.
"""

import json
import random
from pathlib import Path


RNG = random.Random(20260723)
ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT.parent / "2026-07-22_natural_pilot_v03"
SOURCES = ["Amber", "Blue", "Cedar", "Delta"]
SOURCE_CODE = {source: index for index, source in enumerate(SOURCES)}
BATTERS = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin", "Julian", "Cameron"]
BOWLERS = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart"]


def canonical_outcome(event):
    return {
        "bat": int(event.get("bat", 0)),
        "leg_byes": int(event.get("leg_byes", 0)),
        "wides": 0,
        "no_balls": 0,
        "wicket": bool(event.get("wicket")),
        "legal": True,
    }


def outcome_type(outcome):
    if outcome["wicket"]:
        return "WICKET"
    if outcome["wides"]:
        return "WIDE"
    if outcome["no_balls"]:
        return "NO_BALL"
    if outcome["leg_byes"]:
        return "LEG_BYE"
    if outcome["bat"]:
        return "BAT_RUNS"
    return "DOT"


def outcome_value(outcome):
    kind = outcome_type(outcome)
    if kind == "WICKET":
        return "CAUGHT_0"
    if kind == "WIDE":
        return f"WIDE_{outcome['wides']}"
    if kind == "NO_BALL":
        return f"NO_BALL_{outcome['no_balls']}"
    if kind == "LEG_BYE":
        return f"LEG_BYE_{outcome['leg_byes']}"
    if kind == "BAT_RUNS":
        return f"BAT_{outcome['bat']}"
    return "DOT_0"


def state_value(outcome):
    return (
        outcome["bat"]
        + outcome["leg_byes"]
        + 2 * outcome["wides"]
        + 3 * outcome["no_balls"]
        + 2 * int(outcome["wicket"])
    )


def describe(outcome, batter, bowler):
    kind = outcome_type(outcome)
    if kind == "WICKET":
        return f"{bowler} has {batter} caught, no run"
    if kind == "WIDE":
        return f"{bowler} sends {outcome['wides']} wides past {batter}"
    if kind == "NO_BALL":
        return f"{bowler} oversteps to {batter}; {outcome['no_balls']} no-ball"
    if kind == "LEG_BYE":
        return f"{batter} faces {bowler}; {outcome['leg_byes']} leg-byes"
    if kind == "BAT_RUNS":
        return f"{bowler} to {batter}; {outcome['bat']} bat runs"
    return f"{bowler} to {batter}; dot ball"


def make_wrong_outcomes(correct, slot):
    correct_kind = outcome_type(correct)
    templates = {
        "DOT": {
            "bat": 0, "leg_byes": 0, "wides": 0, "no_balls": 0,
            "wicket": False, "legal": True,
        },
        "BAT_RUNS": {
            "bat": [1, 2, 3, 4, 6][slot % 5],
            "leg_byes": 0, "wides": 0, "no_balls": 0,
            "wicket": False, "legal": True,
        },
        "LEG_BYE": {
            "bat": 0, "leg_byes": 2 if slot % 2 else 4,
            "wides": 0, "no_balls": 0, "wicket": False, "legal": True,
        },
        "WICKET": {
            "bat": 0, "leg_byes": 0, "wides": 0, "no_balls": 0,
            "wicket": True, "legal": True,
        },
        "WIDE": {
            "bat": 0, "leg_byes": 0, "wides": 1 + (slot % 2),
            "no_balls": 0, "wicket": False, "legal": False,
        },
        "NO_BALL": {
            "bat": 0, "leg_byes": 0, "wides": 0,
            "no_balls": 1, "wicket": False, "legal": False,
        },
    }
    kinds = [kind for kind in templates if kind != correct_kind]
    RNG.shuffle(kinds)
    wrong = []
    for kind in kinds:
        candidate = dict(templates[kind])
        if outcome_value(candidate) != outcome_value(correct):
            wrong.append(candidate)
        if len(wrong) == 3:
            break
    if len(wrong) != 3:
        raise ValueError("Could not create three distinct wrong outcomes")
    return wrong


def claim_record(slot, source, outcome, batter, bowler, chain):
    source_letter = source[0]
    claim_id = f"{chain}-{source_letter}-{slot:03d}"
    return {
        "source": source,
        "claim_id": claim_id,
        "batter": batter,
        "bowler": bowler,
        "outcome": outcome,
        "outcome_type": outcome_type(outcome),
        "outcome_value": outcome_value(outcome),
        "text": (
            f"{source} claim {claim_id}: "
            f"{describe(outcome, batter, bowler)}."
        ),
    }


integrated = json.loads(
    (SOURCE_ROOT / "t3_stage2_integrated.json").read_text(encoding="utf-8")
)
events = [dict(event) for event in integrated["events"]]
if len(events) != 72:
    raise ValueError(f"Expected 72 source events, found {len(events)}")

# The hidden accepted-source sequence is exactly balanced, but its order is
# random.  Per-slot nonces make this sequence satisfy the visible recursive
# rule, so the gold remains uniquely recoverable from the case.
desired_source_codes = [code for code in range(4) for _ in range(18)]
RNG.shuffle(desired_source_codes)

packets = []
hidden_events = []
previous_source_code = 2  # Genesis state: Cedar.
previous_outcome = {
    "bat": 0, "leg_byes": 0, "wides": 0, "no_balls": 0,
    "wicket": False, "legal": True,
}

for slot, (event, desired_code) in enumerate(zip(events, desired_source_codes), 1):
    over = int(event["over"])
    passage = int(event["ball"])
    correct = canonical_outcome(event)
    nonce = (
        desired_code
        - previous_source_code
        - over
        - passage
        - state_value(previous_outcome)
    ) % 4

    wrong_outcomes = make_wrong_outcomes(correct, slot)
    claims = []
    wrong_index = 0
    for source in SOURCES:
        source_code = SOURCE_CODE[source]
        if source_code == desired_code:
            outcome = correct
        else:
            outcome = wrong_outcomes[wrong_index]
            wrong_index += 1
        claims.append(
            claim_record(
                slot,
                source,
                outcome,
                event["batter"],
                event["bowler"],
                "H7",
            )
        )
    RNG.shuffle(claims)
    packet = {
        "slot": slot,
        "over": over,
        "passage": passage,
        "chain": "HARBOR-7",
        "nonce": nonce,
        "claims": claims,
    }
    packets.append(packet)
    hidden_events.append({
        "slot": slot,
        "over": over,
        "passage": passage,
        "batter": event["batter"],
        "bowler": event["bowler"],
        "nonce": nonce,
        "previous_source_code": previous_source_code,
        "previous_state_value": state_value(previous_outcome),
        "accepted_source": SOURCES[desired_code],
        "accepted_claim_id": next(
            claim["claim_id"]
            for claim in claims
            if claim["source"] == SOURCES[desired_code]
        ),
        "final_outcome": correct,
        "claims": claims,
    })
    previous_source_code = desired_code
    previous_outcome = correct


# Counterfactual rehearsal packets use the same venue, players, slots and source
# vocabulary.  Their chain identifier is the only reliable scope distinction.
shadow_packets = []
for shadow_number, event in enumerate(RNG.sample(events, 12), 1):
    slot = int(event["over"] - 1) * 6 + int(event["ball"])
    claims = []
    for source_index, source in enumerate(SOURCES):
        outcome = make_wrong_outcomes(canonical_outcome(event), slot + source_index)[0]
        claims.append(
            claim_record(
                slot,
                source,
                outcome,
                event["batter"],
                event["bowler"],
                "H7R",
            )
        )
    RNG.shuffle(claims)
    shadow_packets.append({
        "slot": slot,
        "over": int(event["over"]),
        "passage": int(event["ball"]),
        "chain": "HARBOR-7R",
        "nonce": RNG.randrange(4),
        "claims": claims,
        "shadow_number": shadow_number,
    })

arrival_packets = [
    *[{"role": "TARGET", **packet} for packet in packets],
    *[{"role": "SHADOW", **packet} for packet in shadow_packets],
]
RNG.shuffle(arrival_packets)

visible = [
    "EASTGATE OVAL MULTI-FEED AUDIT — HARBOR CITY",
    "",
    "TASK",
    "Recover the target innings and return:",
    "1. innings summary;",
    "2. every batting row;",
    "3. every bowling row;",
    "4. fall of wickets;",
    "5. every partnership;",
    "6. a 72-row accepted-claim audit table with accepted_source,",
    "   accepted_claim_id, outcome_type and outcome_value.",
    "",
    "SCOPE AND AUDIT RULE",
    "- The toss seal identifies HARBOR-7 as the target chain.",
    "- HARBOR-7R is a scorer rehearsal, not part of the target innings.",
    "- Packets are in arrival order. Reconstruct slot order by over and passage.",
    "- Source codes are Amber=0, Blue=1, Cedar=2 and Delta=3.",
    "- Before slot 1, previous source code is 2 and previous accepted outcome",
    "  has state value 0.",
    "- For each HARBOR-7 slot in chronological order, calculate:",
    "    accepted code = (previous accepted source code + over + passage",
    "                     + packet nonce + previous accepted state value) mod 4.",
    "- State value = bat runs + leg-byes + 2*wides + 3*no-balls",
    "                + 2 if the accepted event is a wicket.",
    "- Accept only the claim from the calculated source, then use that accepted",
    "  source and accepted outcome as the previous state for the next slot.",
    "- Wides and no-balls add to team and bowler totals but are not legal balls.",
    "- Leg-byes add to team and partnership totals but not batter or bowler runs.",
    "",
    "ARRIVAL-ORDER EVIDENCE PACKETS",
]

for arrival, packet in enumerate(arrival_packets, 1):
    visible.append(
        f"Packet {arrival:03d} | chain {packet['chain']} | "
        f"slot O{packet['over']:02d}.P{packet['passage']} | nonce {packet['nonce']}"
    )
    for claim in packet["claims"]:
        visible.append(f"  {claim['text']}")

visible.extend([
    "",
    "END OF EVIDENCE",
    "Do not average claims. Exactly one claim is accepted at every target slot.",
])


def project_gold(canonical_events, hidden):
    # Reuse the already validated aggregate gold and attach the provenance table.
    aggregate = json.loads(
        (SOURCE_ROOT / "pilot_v03_gold.json").read_text(encoding="utf-8")
    )
    aggregate["event_audit"] = [
        {
            "accepted_source": item["accepted_source"],
            "accepted_claim_id": item["accepted_claim_id"],
            "outcome_type": outcome_type(item["final_outcome"]),
            "outcome_value": outcome_value(item["final_outcome"]),
        }
        for item in hidden
    ]
    return aggregate


gold = project_gold(events, hidden_events)
hidden_graph = {
    "target_chain": "HARBOR-7",
    "source_codes": SOURCE_CODE,
    "genesis_previous_source_code": 2,
    "genesis_previous_state_value": 0,
    "canonical_events": hidden_events,
    "arrival_packets": arrival_packets,
    "accepted_source_distribution": {
        source: sum(item["accepted_source"] == source for item in hidden_events)
        for source in SOURCES
    },
    "unique_final_state": True,
}

ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "v05_case.txt").write_text("\n".join(visible), encoding="utf-8")
(ROOT / "v05_gold.json").write_text(
    json.dumps(gold, indent=2),
    encoding="utf-8",
)
(ROOT / "v05_hidden_event_graph.json").write_text(
    json.dumps(hidden_graph, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    "target_events": len(hidden_events),
    "target_claims": len(hidden_events) * 4,
    "shadow_packets": len(shadow_packets),
    "visible_packets": len(arrival_packets),
    "accepted_source_distribution": hidden_graph["accepted_source_distribution"],
    "gold_fields": 397,
    "unique_final_state": True,
}, indent=2))
