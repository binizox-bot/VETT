import itertools
import json
import secrets
from pathlib import Path


rng = secrets.SystemRandom()
root = Path(__file__).resolve().parent

batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin"]
bowlers = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart", "Cross"]
run_words = {0: "dot", 1: "one bat run", 2: "two bat runs", 3: "three bat runs",
             4: "four bat runs", 6: "six bat runs", 8: "eight bat runs"}


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
        extras = event.get("leg_byes", 0)
        total = bat + extras
        result["summary"]["runs"] += total
        result["summary"]["legal_balls"] += 1
        result["summary"]["leg_byes"] += extras
        result["batting"][event["batter"]]["runs"] += bat
        result["batting"][event["batter"]]["balls"] += 1
        result["bowling"][event["bowler"]]["legal_balls"] += 1
        result["bowling"][event["bowler"]]["runs_conceded"] += bat
        partnership["runs"] += total
        partnership["extras"] += extras
        partnership["legal_balls"] += 1
        if event.get("wicket"):
            result["summary"]["wickets"] += 1
            result["batting"][event["batter"]]["out"] = True
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
wicket_positions = [10, 24, 36]
for legal_position in range(1, 43):
    over = (legal_position - 1) // 6 + 1
    bowler = bowlers[over - 1]
    if legal_position in wicket_positions:
        event = {
            "legal_position": legal_position,
            "over": over,
            "bowler": bowler,
            "batter": striker,
            "pair": [striker, non_striker],
            "bat": 0,
            "wicket": 1,
        }
        events.append(event)
        striker = batters[next_batter]
        next_batter += 1
    else:
        runs = rng.choice([0, 1, 2, 3, 4, 6])
        event = {
            "legal_position": legal_position,
            "over": over,
            "bowler": bowler,
            "batter": striker,
            "pair": [striker, non_striker],
            "bat": runs,
        }
        events.append(event)
        if runs % 2:
            striker, non_striker = non_striker, striker
    if legal_position % 6 == 0:
        striker, non_striker = non_striker, striker

eligible = [event for event in events if not event.get("wicket")]
ambiguous_events = sorted(rng.sample(eligible, 14), key=lambda event: event["legal_position"])
true_bits = [rng.randrange(2) for _ in ambiguous_events]

for index, (event, bit) in enumerate(zip(ambiguous_events, true_bits), 1):
    original = event["bat"]
    if index % 3 == 1:
        left = {"bat": original if original % 2 == 0 else 1, "leg_byes": 0}
        right = {"bat": left["bat"] + 2, "leg_byes": 0}
    elif index % 3 == 2:
        value = 4 if original % 2 == 0 else 3
        left = {"bat": value, "leg_byes": 0}
        right = {"bat": 0, "leg_byes": value}
    else:
        left = {"bat": 1, "leg_byes": 0}
        right = {"bat": 3, "leg_byes": 0}
    event["packet"] = f"P{index:02d}"
    event["left"] = left
    event["right"] = right
    chosen = right if bit else left
    event["bat"] = chosen["bat"]
    if chosen["leg_byes"]:
        event["leg_byes"] = chosen["leg_byes"]

# Build overlapping exact-count checks. They are added until the binary choice
# vector is uniquely determined; no direct per-packet answer is exposed.
candidates = list(itertools.product((0, 1), repeat=len(ambiguous_events)))
audits = []
attempts = 0
while len(candidates) > 1:
    attempts += 1
    subset = sorted(rng.sample(range(len(ambiguous_events)), rng.randrange(5, 10)))
    count = sum(true_bits[index] for index in subset)
    reduced = [
        candidate for candidate in candidates
        if sum(candidate[index] for index in subset) == count
    ]
    if len(reduced) < len(candidates):
        audits.append((subset, count))
        candidates = reduced
    if attempts > 500:
        raise RuntimeError("Could not obtain a unique audit system")

lines = [
    "RECOVERY RULES",
    "- Every packet below is one legal delivery and one ball faced.",
    "- Left and right readings always refer to the same delivery; exactly one is correct.",
    "- Wickets and uncorrupted deliveries are certain.",
    "- The official audit constraints jointly identify a unique set of right-hand readings.",
    "- Leg-byes count for the team and partnership but not batter or bowler.",
    "",
    "OUTPUT",
    "Return summary, all batting rows, all bowling rows, fall of wickets and all partnerships.",
    "",
    "CORRUPTED TARGET-MATCH LOG",
]

packet_lookup = {event["legal_position"]: event for event in ambiguous_events}
for over in range(1, 8):
    lines.append(f"Over {over}, {bowlers[over - 1]}:")
    for event in [event for event in events if event["over"] == over]:
        if event["legal_position"] in packet_lookup:
            left = event["left"]
            right = event["right"]
            def describe(reading):
                if reading["leg_byes"]:
                    return f"{reading['leg_byes']} leg-byes"
                return run_words[reading["bat"]]
            lines.append(
                f"  {event['packet']} to {event['batter']}: "
                f"LEFT={describe(left)} | RIGHT={describe(right)}."
            )
        elif event.get("wicket"):
            lines.append(
                f"  Certain: {event['bowler']} bowls {event['batter']} for no run; wicket stands."
            )
        else:
            lines.append(
                f"  Certain: {event['bowler']} to {event['batter']}, {run_words[event['bat']]}."
            )

lines.extend(["", "OFFICIAL OVERLAPPING AUDIT CHECKS"])
for number, (subset, count) in enumerate(audits, 1):
    packet_names = ", ".join(f"P{index + 1:02d}" for index in subset)
    lines.append(
        f"Audit {number}: among [{packet_names}], exactly {count} use the RIGHT reading."
    )
lines.append(
    "The audit system has exactly one solution. No packet outside these checks and no other match is relevant."
)

case = "\n".join(lines)
gold = score(events)
(root / "level5_case.txt").write_text(case, encoding="utf-8")
(root / "level5_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
print(case)
