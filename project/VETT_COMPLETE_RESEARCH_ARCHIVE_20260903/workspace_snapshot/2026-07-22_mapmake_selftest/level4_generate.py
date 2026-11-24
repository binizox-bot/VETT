import copy
import json
import secrets
from pathlib import Path


rng = secrets.SystemRandom()
root = Path(__file__).resolve().parent

batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin", "Julian", "Cameron"]
bowlers = ["Frost", "Pike", "Stone", "Rowe", "Shaw"]
run_words = {0: "no run", 1: "one", 2: "two", 3: "three", 4: "FOUR", 6: "SIX"}


def score(events):
    result = {
        "summary": {
            "runs": 0,
            "wickets": 0,
            "legal_balls": 0,
            "wides": 0,
            "no_balls": 0,
            "byes": 0,
            "leg_byes": 0,
        },
        "batting": {
            name: {"runs": 0, "balls": 0, "out": False}
            for name in batters
        },
        "bowling": {
            name: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0}
            for name in bowlers
        },
        "fall_of_wickets": [],
        "partnerships": [],
    }

    partnership = None
    for event in events:
        if partnership is None:
            partnership = {
                "number": len(result["partnerships"]) + 1,
                "batter_1": event["pair"][0],
                "batter_2": event["pair"][1],
                "runs": 0,
                "extras": 0,
                "legal_balls": 0,
                "end_team_runs": None,
                "ended_by": None,
            }

        bat = event.get("bat", 0)
        wd = event.get("wide", 0)
        nb = event.get("no_ball", 0)
        byes = event.get("byes", 0)
        leg_byes = event.get("leg_byes", 0)
        extras = wd + nb + byes + leg_byes
        total = bat + extras

        result["summary"]["runs"] += total
        result["summary"]["legal_balls"] += event["legal"]
        result["summary"]["wides"] += wd
        result["summary"]["no_balls"] += nb
        result["summary"]["byes"] += byes
        result["summary"]["leg_byes"] += leg_byes

        result["batting"][event["batter"]]["runs"] += bat
        if event["legal"] or nb:
            result["batting"][event["batter"]]["balls"] += 1

        result["bowling"][event["bowler"]]["legal_balls"] += event["legal"]
        result["bowling"][event["bowler"]]["runs_conceded"] += bat + wd + nb

        partnership["runs"] += total
        partnership["extras"] += extras
        partnership["legal_balls"] += event["legal"]

        if event.get("wicket"):
            result["summary"]["wickets"] += 1
            result["batting"][event["batter"]]["out"] = True
            if event.get("bowler_credit", True):
                result["bowling"][event["bowler"]]["wickets"] += 1
            result["fall_of_wickets"].append({
                "batter": event["batter"],
                "team_runs": result["summary"]["runs"],
                "wicket_number": result["summary"]["wickets"],
            })
            partnership["end_team_runs"] = result["summary"]["runs"]
            partnership["ended_by"] = event["batter"]
            result["partnerships"].append(partnership)
            partnership = None

    if partnership is not None:
        partnership["end_team_runs"] = result["summary"]["runs"]
        result["partnerships"].append(partnership)
    return result


events = []
striker, non_striker = batters[0], batters[1]
next_batter = 2
wicket_positions = sorted(rng.sample(range(8, 57), 5))
wide_slots = {(over, rng.randrange(6)) for over in rng.sample(range(10), 6)}
no_ball_slots = {(over, rng.randrange(6)) for over in rng.sample(range(1, 9), 2)}

for over in range(10):
    bowler = bowlers[over % len(bowlers)]
    for ball_index in range(6):
        if (over, ball_index) in wide_slots:
            wide_value = rng.choice([1, 1, 2])
            events.append({
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "pair": [striker, non_striker],
                "legal": 0,
                "wide": wide_value,
                "initial_kind": "wide",
                "initial_value": wide_value,
            })

        if (over, ball_index) in no_ball_slots:
            bat_value = rng.choice([0, 1, 2, 4])
            events.append({
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "pair": [striker, non_striker],
                "legal": 0,
                "no_ball": 1,
                "bat": bat_value,
                "initial_kind": "no_ball",
                "initial_value": bat_value,
            })
            if bat_value % 2:
                striker, non_striker = non_striker, striker

        legal_position = over * 6 + ball_index + 1
        if legal_position in wicket_positions:
            events.append({
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "pair": [striker, non_striker],
                "legal": 1,
                "bat": 0,
                "wicket": 1,
                "bowler_credit": True,
                "initial_kind": "wicket",
                "initial_value": 0,
            })
            striker = batters[next_batter]
            next_batter += 1
        else:
            runs = rng.choice([0, 0, 1, 1, 2, 3, 4, 4, 6])
            events.append({
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "pair": [striker, non_striker],
                "legal": 1,
                "bat": runs,
                "initial_kind": "bat",
                "initial_value": runs,
            })
            if runs % 2:
                striker, non_striker = non_striker, striker
    striker, non_striker = non_striker, striker

# Add two initially reported non-bat extras.
ordinary = [
    event for event in events
    if event["legal"] and not event.get("wicket") and event.get("bat", 0) in (2, 3)
]
for event, extra_name in zip(rng.sample(ordinary, 2), ["byes", "leg_byes"]):
    value = event["bat"]
    event["bat"] = 0
    event[extra_name] = value
    event["initial_kind"] = extra_name
    event["initial_value"] = value

initial_events = copy.deepcopy(events)

# Four late changes: re-attribution, numerical reduction, correction of a
# correction, and bowler-credit removal for a run-out.
bat_candidates = [
    event for event in events
    if event["legal"] and not event.get("wicket") and event.get("bat", 0) in (2, 3, 4, 6)
]
attribution_event, reduction_event, nested_event = rng.sample(bat_candidates, 3)

attr_initial = attribution_event["bat"]
attribution_event["bat"] = 0
attribution_event["leg_byes"] = attr_initial

red_initial = reduction_event["bat"]
red_final = rng.choice([value for value in (1, 2, 3) if value != red_initial])
reduction_event["bat"] = red_final

nested_initial = nested_event["bat"]
nested_provisional = rng.choice([value for value in (1, 2, 3, 4) if value != nested_initial])
nested_final = rng.choice([value for value in (0, 1, 2, 3) if value != nested_provisional])
nested_event["bat"] = nested_final

wicket_events = [event for event in events if event.get("wicket")]
runout_event = rng.choice(wicket_events[1:-1])
runout_event["bowler_credit"] = False


def ordinal_scoring(target):
    candidates = [
        event for event in initial_events
        if event["over"] == target["over"]
        and event["initial_kind"] in ("bat", "byes", "leg_byes", "no_ball")
        and (event["initial_value"] > 0 or event["initial_kind"] == "no_ball")
    ]
    match = next(event for event in candidates if event["sequence"] == target["sequence"])
    return candidates.index(match) + 1


def word(number):
    return {
        1: "first", 2: "second", 3: "third", 4: "fourth",
        5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth",
    }[number]


lines = [
    "RULES",
    "- Wide: illegal, no ball faced, charged to bowler.",
    "- No-ball: illegal, one ball faced in this benchmark, charged to bowler; bat runs are additional.",
    "- Bye/leg-bye: legal and faced, but not charged to bowler.",
    "- A run-out is a team wicket but not a bowler wicket.",
    "- The latest final scorer ruling replaces the corresponding older report.",
    "",
    "OUTPUT",
    "Return summary, complete batting, complete bowling, fall of wickets, and every partnership.",
    "For each partnership give number, the two starting batters in transcript order, runs, extras, legal balls,",
    "end team score, and the batter ending it; use null for the unbroken partnership.",
    "",
    "TARGET-MATCH MULTI-SOURCE TRANSCRIPT",
]

initial_running = score(initial_events)
for over in range(1, 11):
    bowler = bowlers[(over - 1) % len(bowlers)]
    over_events = [event for event in initial_events if event["over"] == over]
    lines.append(f"Over {over}, {bowler}:")
    for event in over_events:
        kind = event["initial_kind"]
        batter = event["batter"]
        if kind == "wide":
            lines.append(f"  Then {bowler} sends down a wide worth {event['initial_value']}.")
        elif kind == "no_ball":
            lines.append(
                f"  Then a no-ball to {batter}: one no-ball extra plus "
                f"{event['initial_value']} from the bat."
            )
        elif kind == "wicket":
            lines.append(f"  Then {bowler} bowls {batter} for no run; initially credited to the bowler.")
        elif kind == "byes":
            lines.append(f"  Then {event['initial_value']} byes while {batter} faces.")
        elif kind == "leg_byes":
            lines.append(f"  Then {event['initial_value']} leg-byes while {batter} faces.")
        else:
            lines.append(f"  Then {bowler} to {batter}: {run_words[event['initial_value']]} bat runs.")

    # Feed duplication and a near-name historical distraction.
    scoring_bits = []
    for event in over_events:
        value = (
            event.get("bat", 0) + event.get("wide", 0) + event.get("no_ball", 0)
            + event.get("byes", 0) + event.get("leg_byes", 0)
        )
        if value:
            scoring_bits.append(str(value))
        elif event.get("wicket"):
            scoring_bits.append("W")
        else:
            scoring_bits.append("dot")
    lines.append(
        "  Syndicated recap of that same over, not additional play: "
        + ", ".join(scoring_bits) + "."
    )
    if over in (3, 7):
        lines.append(
            f"  Harbor youth match ticker, not this match: A. Holt {rng.randrange(30, 70)}, "
            f"Frost {rng.randrange(20, 45)} for 2."
        )

lines.extend([
    "",
    "LATE SCORER THREAD",
])

attr_ord = word(ordinal_scoring(attribution_event))
lines.append(
    f"Final item 1: in over {attribution_event['over']}, the {attr_ord} scoring event, "
    f"the one faced by {attribution_event['batter']}, stays worth {attr_initial}, "
    "but all of those runs are leg-byes rather than bat runs."
)

red_ord = word(ordinal_scoring(reduction_event))
lines.append(
    f"Final item 2: in over {reduction_event['over']}, reduce the {red_ord} scoring event "
    f"faced by {reduction_event['batter']} from {red_initial} bat runs to {red_final}."
)

nested_ord = word(ordinal_scoring(nested_event))
lines.append(
    f"Scorer draft: in over {nested_event['over']}, change the {nested_ord} scoring event "
    f"faced by {nested_event['batter']} from {nested_initial} to {nested_provisional} bat runs."
)
lines.append(
    f"Final reply to the draft: same event, but {nested_provisional} was a transcription slip. "
    f"The ratified value is {nested_final} bat runs."
)

wicket_number = wicket_events.index(
    next(event for event in wicket_events if event["sequence"] == runout_event["sequence"]
         and event["over"] == runout_event["over"])
) + 1
lines.append(
    f"Final dismissal item: the {word(wicket_number)} wicket, {runout_event['batter']} in "
    f"over {runout_event['over']}, remains a wicket at the same score and on the same legal ball, "
    f"but replay changes bowled to run-out. Remove it from {runout_event['bowler']}'s wicket tally."
)
lines.append(
    "A cached scorecard snapshot from before this thread may still circulate. It is obsolete; "
    "use the final items and do not add recap or youth-match figures."
)

case = "\n".join(lines)
gold = score(events)
(root / "level4_case.txt").write_text(case, encoding="utf-8")
(root / "level4_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
print(case)
