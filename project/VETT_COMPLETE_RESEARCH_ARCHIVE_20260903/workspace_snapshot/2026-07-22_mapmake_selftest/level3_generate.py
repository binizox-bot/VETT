import copy
import json
import secrets
from pathlib import Path


rng = secrets.SystemRandom()
root = Path(__file__).resolve().parent

batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin", "Julian"]
bowlers = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart"]
run_words = {0: "no run", 1: "one run", 2: "two runs", 3: "three runs", 4: "FOUR", 6: "SIX"}


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
    }
    for event in events:
        bat = event.get("bat", 0)
        wd = event.get("wide", 0)
        nb = event.get("no_ball", 0)
        byes = event.get("byes", 0)
        leg_byes = event.get("leg_byes", 0)
        result["summary"]["runs"] += bat + wd + nb + byes + leg_byes
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

        if event.get("wicket"):
            result["summary"]["wickets"] += 1
            result["batting"][event["batter"]]["out"] = True
            result["bowling"][event["bowler"]]["wickets"] += 1
            result["fall_of_wickets"].append({
                "batter": event["batter"],
                "team_runs": result["summary"]["runs"],
                "wicket_number": result["summary"]["wickets"],
            })
    return result


events = []
striker, non_striker = batters[0], batters[1]
next_batter = 2
wicket_legal_positions = sorted(rng.sample(range(7, 35), 3))
wide_slots = {(over, rng.randrange(0, 6)) for over in rng.sample(range(6), 3)}
no_ball_slot = (rng.randrange(1, 5), rng.randrange(0, 6))

for over in range(6):
    bowler = bowlers[over]
    for ball_index in range(6):
        if (over, ball_index) in wide_slots:
            events.append({
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "legal": 0,
                "wide": 1,
                "initial_kind": "wide",
                "initial_value": 1,
            })

        if (over, ball_index) == no_ball_slot:
            events.append({
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "legal": 0,
                "no_ball": 1,
                "bat": 0,
                "initial_kind": "pending_catch",
                "initial_value": 0,
                "void_catch": True,
            })

        legal_position = over * 6 + ball_index + 1
        is_wicket = legal_position in wicket_legal_positions
        if is_wicket:
            event = {
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "legal": 1,
                "bat": 0,
                "wicket": 1,
                "initial_kind": "wicket",
                "initial_value": 0,
            }
            events.append(event)
            striker = batters[next_batter]
            next_batter += 1
        else:
            runs = rng.choice([0, 1, 2, 3, 4, 4, 6])
            event = {
                "over": over + 1,
                "sequence": len([e for e in events if e["over"] == over + 1]) + 1,
                "bowler": bowler,
                "batter": striker,
                "legal": 1,
                "bat": runs,
                "initial_kind": "bat",
                "initial_value": runs,
            }
            events.append(event)
            if runs % 2:
                striker, non_striker = non_striker, striker
    striker, non_striker = non_striker, striker

# Choose three ordinary scoring events and turn their initial reports into
# progressively harder official corrections. The visible text identifies them
# only by over, bowler, batter and ordinal scoring shot within that over.
candidates = [
    event for event in events
    if event["legal"] and not event.get("wicket") and event.get("bat", 0) in (2, 3, 4, 6)
]
while len(candidates) < 3:
    candidate = rng.choice([
        event for event in events
        if event["legal"] and not event.get("wicket")
    ])
    candidate["bat"] = 4
    candidate["initial_value"] = 4
    candidates = [
        event for event in events
        if event["legal"] and not event.get("wicket") and event.get("bat", 0) in (2, 3, 4, 6)
    ]

attribution_event, reduction_event, nested_event = rng.sample(candidates, 3)
initial_events = copy.deepcopy(events)

attribution_initial = attribution_event["bat"]
attribution_event["bat"] = 0
attribution_kind = rng.choice(["byes", "leg_byes"])
attribution_event[attribution_kind] = attribution_initial
attribution_event["correction_kind"] = "attribution"

reduction_initial = reduction_event["bat"]
reduction_final = rng.choice([value for value in (1, 2, 3) if value != reduction_initial])
reduction_event["bat"] = reduction_final
reduction_event["correction_kind"] = "reduction"

nested_initial = nested_event["bat"]
nested_provisional = rng.choice([value for value in (1, 2, 3, 4) if value != nested_initial])
nested_final = rng.choice([value for value in (0, 1, 2, 3) if value != nested_provisional])
nested_event["bat"] = nested_final
nested_event["correction_kind"] = "nested"


def scoring_ordinal(target, source):
    same_over = [
        event for event in source
        if event["over"] == target["over"]
        and event["initial_kind"] == "bat"
        and event["initial_value"] > 0
    ]
    return same_over.index(next(event for event in same_over if event["sequence"] == target["sequence"])) + 1


def ordinal_word(number):
    return {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}.get(
        number, f"number-{number}"
    )


lines = [
    "SCORING CONVENTIONS",
    "- Wide: not a legal ball and not a ball faced; charged to the bowler.",
    "- No-ball: not a legal ball, but counts as a ball faced here; charged to the bowler.",
    "- Bye and leg-bye: legal ball and ball faced; not charged to the bowler.",
    "- A later official decision replaces the earlier report of the same passage.",
    "",
    "TARGET",
    "Produce the final innings summary, every batting row, every bowling row, and the fall of wickets.",
    "",
    "MERGED LIVE TRANSCRIPT",
]

for over in range(1, 7):
    over_events = [event for event in initial_events if event["over"] == over]
    lines.append(f"Over {over}, {bowlers[over - 1]} operating:")
    for event in over_events:
        batter = event["batter"]
        bowler = event["bowler"]
        kind = event["initial_kind"]
        if kind == "wide":
            lines.append(f"  Next one: {bowler} misses the strip outside {batter}; wide.")
        elif kind == "pending_catch":
            lines.append(
                f"  Next one: {batter} is caught from {bowler}, but the replay desk is checking the front foot."
            )
            lines.append(
                "  Replay desk: overstep confirmed. No-ball, catch void, and no bat run was completed."
            )
        elif kind == "wicket":
            lines.append(f"  Next one: {bowler} bowls {batter}; no run and the wicket stands.")
        else:
            lines.append(f"  Next one: {bowler} to {batter}, {run_words[event['initial_value']]}.")

    # Natural duplicate feed: exact over summary plus one non-target historical distractor.
    scoring = [
        event for event in over_events
        if event["initial_kind"] == "bat" and event["initial_value"] > 0
    ]
    recap = ", ".join(
        f"{event['batter']} {event['initial_value']}"
        for event in scoring
    ) or "no bat runs"
    lines.append(
        f"  End-of-over radio recap (repeat, not new play): the scoring shots just heard were {recap}."
    )
    lines.append(
        f"  Archive ticker, previous match only: {bowlers[over - 1]} had figures "
        f"{rng.randrange(18, 45)} for {rng.randrange(0, 4)}."
    )

lines.extend(["", "SCORER MESSAGES ARRIVING AFTER THE SIXTH OVER"])

attr_ord = ordinal_word(scoring_ordinal(attribution_event, initial_events))
extra_label = "byes" if attribution_kind == "byes" else "leg-byes"
lines.append(
    f"Official correction A: in over {attribution_event['over']}, the {attr_ord} scoring shot "
    f"by {attribution_event['batter']} from {attribution_event['bowler']} did not touch the bat. "
    f"Keep its value at {attribution_initial}, but record all of it as {extra_label}."
)

red_ord = ordinal_word(scoring_ordinal(reduction_event, initial_events))
lines.append(
    f"Official correction B: in over {reduction_event['over']}, the {red_ord} scoring shot "
    f"by {reduction_event['batter']} from {reduction_event['bowler']} was first called "
    f"{reduction_initial}; video shows only {reduction_final} completed. Replace the old value."
)

nested_ord = ordinal_word(scoring_ordinal(nested_event, initial_events))
lines.append(
    f"Provisional correction C: in over {nested_event['over']}, the {nested_ord} scoring shot "
    f"by {nested_event['batter']} from {nested_event['bowler']} may be reduced from "
    f"{nested_initial} to {nested_provisional} bat runs."
)
lines.append(
    f"Final correction to C: the same {nested_ord} scoring shot in over {nested_event['over']} "
    f"has now been checked frame by frame. Ignore the provisional value of {nested_provisional}; "
    f"the final value is {nested_final} bat runs."
)

# A stale replay is deliberately placed after the final correction. Its wording
# explicitly marks it as an old recording, so the gold remains uniquely recoverable.
lines.append(
    f"Delayed audio replay, recorded before the corrections: the commentator again says "
    f"{nested_event['batter']}'s shot was worth {nested_initial}. This is stale audio, not a new ruling."
)
lines.append(
    "The three official items above are final. Radio recaps, archive tickers, provisional wording, "
    "and delayed audio do not create deliveries or override final rulings."
)

case = "\n".join(lines)
gold = score(events)
(root / "level3_case.txt").write_text(case, encoding="utf-8")
(root / "level3_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
print(case)
