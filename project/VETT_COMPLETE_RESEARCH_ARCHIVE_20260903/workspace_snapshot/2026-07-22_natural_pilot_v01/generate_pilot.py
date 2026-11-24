import itertools
import json
import random
from pathlib import Path


rng = random.Random(20260722)
root = Path(__file__).resolve().parent

batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin", "Julian", "Cameron"]
bowlers = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart"]
run_words = {
    0: "dot", 1: "one bat run", 2: "two bat runs", 3: "three bat runs",
    4: "four bat runs", 6: "six bat runs", 8: "eight bat runs",
}


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
            player: {"runs": 0, "balls": 0, "out": False}
            for player in batters
        },
        "bowling": {
            player: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0}
            for player in bowlers
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
        leg_byes = event.get("leg_byes", 0)
        total = bat + leg_byes
        result["summary"]["runs"] += total
        result["summary"]["legal_balls"] += 1
        result["summary"]["leg_byes"] += leg_byes
        result["batting"][event["batter"]]["runs"] += bat
        result["batting"][event["batter"]]["balls"] += 1
        result["bowling"][event["bowler"]]["legal_balls"] += 1
        result["bowling"][event["bowler"]]["runs_conceded"] += bat
        partnership["runs"] += total
        partnership["extras"] += leg_byes
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
wicket_positions = [11, 25, 38, 55, 66]

for position in range(1, 73):
    over = (position - 1) // 6 + 1
    bowler = bowlers[(over - 1) % len(bowlers)]
    if position in wicket_positions:
        event = {
            "position": position,
            "over": over,
            "ball": (position - 1) % 6 + 1,
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
            "position": position,
            "over": over,
            "ball": (position - 1) % 6 + 1,
            "bowler": bowler,
            "batter": striker,
            "pair": [striker, non_striker],
            "bat": runs,
        }
        events.append(event)
        if runs % 2:
            striker, non_striker = non_striker, striker
    if position % 6 == 0:
        striker, non_striker = non_striker, striker

# Twenty OCR-conflicted packets. Both readings preserve parity, so the
# independently certain striker sequence remains valid.
ambiguous = sorted(
    rng.sample([event for event in events if not event.get("wicket")], 20),
    key=lambda event: event["position"],
)
true_bits = [rng.randrange(2) for _ in ambiguous]
for index, (event, bit) in enumerate(zip(ambiguous, true_bits), 1):
    original = event["bat"]
    if index % 3 == 1:
        left_bat = original if original % 2 == 0 else 1
        left = {"bat": left_bat, "leg_byes": 0}
        right = {"bat": left_bat + 2, "leg_byes": 0}
    elif index % 3 == 2:
        value = 4 if original % 2 == 0 else 3
        left = {"bat": value, "leg_byes": 0}
        right = {"bat": 0, "leg_byes": value}
    else:
        left = {"bat": 1, "leg_byes": 0}
        right = {"bat": 3, "leg_byes": 0}
    event["packet"] = f"clip-{chr(64 + index)}"
    event["left"] = left
    event["right"] = right
    chosen = right if bit else left
    event["bat"] = chosen["bat"]
    if chosen["leg_byes"]:
        event["leg_byes"] = chosen["leg_byes"]


def materialize(bits):
    output = []
    ambiguous_index = {event["position"]: index for index, event in enumerate(ambiguous)}
    for event in events:
        copy = {
            key: value for key, value in event.items()
            if key not in ("left", "right", "packet", "leg_byes", "bat")
        }
        if event["position"] in ambiguous_index:
            index = ambiguous_index[event["position"]]
            choice = event["right"] if bits[index] else event["left"]
            copy["bat"] = choice["bat"]
            if choice["leg_byes"]:
                copy["leg_byes"] = choice["leg_byes"]
        else:
            copy["bat"] = event.get("bat", 0)
            if event.get("leg_byes"):
                copy["leg_byes"] = event["leg_byes"]
        output.append(copy)
    return output


def checkpoint_features(candidate_events):
    features = {}
    running_team = 0
    running_leg_byes = 0
    running_batters = {player: 0 for player in batters}
    running_bowlers = {player: 0 for player in bowlers}
    for event in candidate_events:
        bat = event.get("bat", 0)
        leg_byes = event.get("leg_byes", 0)
        running_team += bat + leg_byes
        running_leg_byes += leg_byes
        running_batters[event["batter"]] += bat
        running_bowlers[event["bowler"]] += bat
        position = event["position"]
        over = event["over"]
        ball = event["ball"]
        # Natural camera freezes after selected balls and over endings.
        if ball in (3, 6):
            features[("team", over, ball)] = running_team
            features[("leg_byes", over, ball)] = running_leg_byes
            for player in batters:
                if running_batters[player]:
                    features[("batter", player, over, ball)] = running_batters[player]
            features[("bowler", event["bowler"], over, ball)] = running_bowlers[event["bowler"]]
    return features


true_features = checkpoint_features(events)
pool_keys = list(true_features)
rng.shuffle(pool_keys)

# Every checkpoint statistic is additive across deliveries. Precompute its
# all-LEFT value and each packet's RIGHT-minus-LEFT delta, then enumerate bit
# masks without repeatedly materializing full innings.
left_features = checkpoint_features(materialize([0] * len(ambiguous)))
feature_deltas = {key: [0] * len(ambiguous) for key in pool_keys}
for index in range(len(ambiguous)):
    bits = [0] * len(ambiguous)
    bits[index] = 1
    one_right = checkpoint_features(materialize(bits))
    for key in pool_keys:
        feature_deltas[key][index] = one_right.get(key, 0) - left_features.get(key, 0)


def feature_from_mask(key, mask):
    value = left_features.get(key, 0)
    deltas = feature_deltas[key]
    for index, delta in enumerate(deltas):
        if mask & (1 << index):
            value += delta
    return value


# Greedily retain natural checkpoint statements until exactly one assignment
# survives. Candidate generation uses only the public alternatives.
candidates = list(range(1 << len(ambiguous)))
selected_keys = []
for key in pool_keys:
    target = true_features[key]
    reduced = [
        mask for mask in candidates
        if feature_from_mask(key, mask) == target
    ]
    if len(reduced) < len(candidates):
        selected_keys.append(key)
        candidates = reduced
    if len(candidates) == 1:
        break

true_mask = sum(bit << index for index, bit in enumerate(true_bits))
if len(candidates) != 1 or candidates[0] != true_mask:
    raise RuntimeError("Natural checkpoint pool did not uniquely recover the true innings")


def describe_reading(reading):
    if reading["leg_byes"]:
        return f"{reading['leg_byes']} leg-byes"
    return run_words[reading["bat"]]


lines = [
    "SCORING RULES",
    "- Every listed item is one legal delivery and one ball faced.",
    "- Each OCR-conflicted clip has two readings of the same delivery; exactly one is correct.",
    "- Leg-byes count for team and partnership, but not batter or bowler.",
    "- Wickets and batter identities in the commentary are certain.",
    "- Official scorer checkpoints jointly make the final innings uniquely recoverable.",
    "",
    "OUTPUT",
    "Return final summary, all batting rows, all bowling rows, fall of wickets and all partnerships.",
    "",
    "COMMENTARY AND OCR CLIPS",
]

ambiguous_positions = {event["position"] for event in ambiguous}
for over in range(1, 13):
    bowler = bowlers[(over - 1) % len(bowlers)]
    lines.append(f"Over {over}, {bowler}:")
    for event in [event for event in events if event["over"] == over]:
        if event["position"] in ambiguous_positions:
            lines.append(
                f"  {event['packet']} at this point, faced by {event['batter']}: "
                f"feed one reads {describe_reading(event['left'])}; "
                f"feed two reads {describe_reading(event['right'])}."
            )
        elif event.get("wicket"):
            lines.append(
                f"  Next, {bowler} bowls {event['batter']} for no run; the wicket stands."
            )
        else:
            lines.append(
                f"  Next, {bowler} to {event['batter']}: {run_words[event['bat']]}."
            )

lines.extend(["", "OFFICIAL SCORER CHECKPOINTS"])
for number, key in enumerate(selected_keys, 1):
    value = true_features[key]
    kind = key[0]
    if kind == "team":
        _, over, ball = key
        text = (
            f"Checkpoint {number}: immediately after legal ball {ball} of over {over}, "
            f"the target-match team score was {value}."
        )
    elif kind == "leg_byes":
        _, over, ball = key
        text = (
            f"Checkpoint {number}: immediately after legal ball {ball} of over {over}, "
            f"the cumulative leg-bye count was {value}."
        )
    elif kind == "batter":
        _, player, over, ball = key
        text = (
            f"Checkpoint {number}: immediately after legal ball {ball} of over {over}, "
            f"{player}'s cumulative bat score was {value}."
        )
    else:
        _, player, over, ball = key
        text = (
            f"Checkpoint {number}: immediately after legal ball {ball} of over {over}, "
            f"{player} had conceded {value} chargeable runs in the innings."
        )
    lines.append(text)
lines.append(
    "These official checkpoints, taken together, admit exactly one reading of every conflicted clip."
)

case = "\n".join(lines)
gold = score(events)
manifest = {
    "seed": 20260722,
    "ambiguous_events": len(ambiguous),
    "checkpoint_count": len(selected_keys),
    "unique_solution_count": len(candidates),
    "selected_checkpoint_keys": selected_keys,
}
(root / "pilot_case.txt").write_text(case, encoding="utf-8")
(root / "pilot_gold.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
(root / "pilot_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(case)
