import copy
import json
import secrets
from pathlib import Path


rng = secrets.SystemRandom()
root = Path(__file__).resolve().parent

batters = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin"]
bowlers = ["Frost", "Pike", "Stone", "Rowe"]
run_words = {
    0: "nothing",
    1: "a single",
    2: "a pair",
    3: "three",
    4: "four",
    6: "six",
}

events = []
striker = batters[0]
non_striker = batters[1]
next_batter = 2
legal_index = 0
wicket_positions = sorted(rng.sample(range(5, 23), 2))
wide_positions = set(rng.sample(range(1, 24), 3))
no_ball_position = rng.choice([position for position in range(2, 22) if position not in wicket_positions])

for over in range(4):
    bowler = bowlers[over]
    ball = 1
    while ball <= 6:
        prospective_index = legal_index + 1
        if prospective_index in wide_positions:
            events.append({
                "label": f"{over}.{ball}",
                "bowler": bowler,
                "batter": striker,
                "legal": 0,
                "wide": 1,
                "initial": {"kind": "wide", "value": 1},
            })
            wide_positions.remove(prospective_index)

        if prospective_index == no_ball_position:
            events.append({
                "label": f"{over}.{ball}",
                "bowler": bowler,
                "batter": striker,
                "legal": 0,
                "no_ball": 1,
                "bat": 0,
                "initial": {"kind": "caught", "value": 0},
                "correction": "no_ball_void_wicket",
            })

        legal_index += 1
        if legal_index in wicket_positions:
            event = {
                "label": f"{over}.{ball}",
                "bowler": bowler,
                "batter": striker,
                "legal": 1,
                "bat": 0,
                "wicket": 1,
                "initial": {"kind": "wicket", "value": 0},
            }
            events.append(event)
            striker = batters[next_batter]
            next_batter += 1
        else:
            runs = rng.choice([0, 1, 2, 3, 4, 6])
            event = {
                "label": f"{over}.{ball}",
                "bowler": bowler,
                "batter": striker,
                "legal": 1,
                "bat": runs,
                "initial": {"kind": "bat", "value": runs},
            }
            events.append(event)
            if runs % 2 == 1:
                striker, non_striker = non_striker, striker
        ball += 1

    striker, non_striker = non_striker, striker

correctable_fours = [
    event for event in events
    if event.get("bat") == 4 and event["legal"] and not event.get("wicket")
]
while len(correctable_fours) < 2:
    candidate = rng.choice([
        event for event in events
        if event["legal"] and not event.get("wicket") and event.get("bat", 0) in (0, 2, 6)
    ])
    candidate["bat"] = 4
    candidate["initial"] = {"kind": "bat", "value": 4}
    correctable_fours = [
        event for event in events
        if event.get("bat") == 4 and event["legal"] and not event.get("wicket")
    ]

attribution_event, boundary_event = rng.sample(correctable_fours, 2)
attribution_event["bat"] = 0
attribution_event[rng.choice(["byes", "leg_byes"])] = 4
attribution_event["correction"] = "four_to_extras"

boundary_event["bat"] = 3
boundary_event["correction"] = "four_to_three"

initial_events = copy.deepcopy(events)


def score(source_events):
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

    for event in source_events:
        bat = event.get("bat", 0)
        wd = event.get("wide", 0)
        nb = event.get("no_ball", 0)
        byes = event.get("byes", 0)
        leg_byes = event.get("leg_byes", 0)
        total = bat + wd + nb + byes + leg_byes
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


gold = score(events)
initial_score = score(initial_events)

lines = [
    "SCORING CONVENTIONS",
    "- Wide: neither legal ball nor ball faced; charged to bowler.",
    "- No-ball: not legal; counts as ball faced in this task; charged to bowler.",
    "- Bye/leg-bye: legal and ball faced; not charged to bowler.",
    "- Only the later official correction replaces the matching delivery.",
    "",
    "TARGET",
    "Return final innings summary, complete batting and bowling rows, and fall of wickets.",
    "",
    "MULTI-FEED COMMENTARY",
]

for index, event in enumerate(initial_events):
    label = event["label"]
    bowler = event["bowler"]
    batter = event["batter"]
    initial = event["initial"]
    if initial["kind"] == "wide":
        text = f"{label} {bowler} strays beyond {batter}'s reach; wide called."
    elif initial["kind"] == "caught":
        text = f"{label} {bowler} has {batter} caught. The fielders celebrate, pending the front-foot check."
    elif initial["kind"] == "wicket":
        text = f"{label} {bowler} removes {batter}; a standing bowler-credited wicket with no run."
    else:
        text = f"{label} {bowler} to {batter}: {run_words[initial['value']]}."
    lines.append(text)

    if event.get("correction") == "no_ball_void_wicket":
        lines.append(
            f"Delayed replay on {label}: front foot over. Official signal is no-ball; "
            f"the catch of {batter} is void and no bat run was completed."
        )

    if event["legal"] and int(label.split(".")[1]) == 6:
        over_number = int(label.split(".")[0])
        bowler_score = initial_score["bowling"][bowler]
        lines.append(
            f"Radio over-recap for over {over_number}: {bowler} has now sent down another six legal balls. "
            "This is a summary of the deliveries just heard, not a new passage of play."
        )
        lines.append(
            f"Archive graphic, unrelated to today: {bowler} conceded "
            f"{bowler_score['runs_conceded'] + rng.choice([7, 11, 19])} in the previous fixture."
        )

lines.extend([
    "",
    "LATE OFFICIAL SCORER BULLETIN",
])

extra_kind = "leg-byes" if attribution_event.get("leg_byes") else "byes"
lines.append(
    f"At {attribution_event['label']}, the apparent four to {attribution_event['batter']} "
    f"off {attribution_event['bowler']} never touched the bat. Reassign all four as {extra_kind}. "
    "The team total for that delivery stays unchanged."
)
lines.append(
    f"At {boundary_event['label']}, revise the apparent four to {boundary_event['batter']} "
    "to three completed runs. This reduces both the batter and team total by one."
)
lines.append(
    "The bulletin is final. Earlier radio recaps and archive graphics do not override it."
)

commentary = "\n".join(lines)
(root / "blind_case_v2.txt").write_text(commentary, encoding="utf-8")
(root / "blind_gold_v2.json").write_text(json.dumps(gold, indent=2), encoding="utf-8")
print(commentary)
