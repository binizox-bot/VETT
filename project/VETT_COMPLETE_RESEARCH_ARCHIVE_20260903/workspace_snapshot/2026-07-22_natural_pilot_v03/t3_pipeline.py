"""T³ (Text-Tuple-Table) self-test on the natural v0.3 pilot.

The script does not read pilot_v03_gold.json. It implements the three official
high-level stages:

1. Text-to-Tuple: parse event and reconciliation tuples from the case.
2. Information Integration: generate/execute numerical consolidation logic.
3. Tuple-to-Table: project integrated event tuples into the required tables.
"""

import json
import re
from pathlib import Path

import numpy as np


root = Path(__file__).resolve().parent
case_path = root / "pilot_v03_case.txt"
case_text = case_path.read_text(encoding="utf-8")

word_to_run = {
    "dot": 0,
    "one bat run": 1,
    "two bat runs": 2,
    "three bat runs": 3,
    "four bat runs": 4,
    "six bat runs": 6,
    "eight bat runs": 8,
}


def parse_reading(text):
    text = text.strip().rstrip(".")
    leg_bye_match = re.fullmatch(r"(\d+) leg-byes", text)
    if leg_bye_match:
        return {"bat": 0, "leg_byes": int(leg_bye_match.group(1))}
    if text not in word_to_run:
        raise ValueError(f"Unknown scoring reading: {text}")
    return {"bat": word_to_run[text], "leg_byes": 0}


def parse_number_list(text):
    return [int(value.strip()) for value in text.split(",")]


def parse_player_list(text):
    return [value.strip() for value in text.split(",")]


def parse_segments(text):
    return [
        (int(over), 1 if half == "first" else 2)
        for over, half in re.findall(r"over (\d+) (first|second) half", text)
    ]


def parse_deliveries(text):
    return [
        (int(over), int(ball))
        for over, ball in re.findall(r"(\d+)\.(\d+)", text)
    ]


def parse_reconciliation(line):
    prefix = re.match(r"Reconciliation (\d+): (.*)", line)
    if not prefix:
        raise ValueError(f"Malformed reconciliation: {line}")
    number = int(prefix.group(1))
    body = prefix.group(2)

    match = re.fullmatch(
        r"the combined team runs produced in overs \[([0-9, ]+)\] were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "team_overs",
            "overs": parse_number_list(match.group(1)),
            "value": int(match.group(2)),
        }

    match = re.fullmatch(
        r"across overs \[([0-9, ]+)\], the combined chargeable runs conceded "
        r"by \[([A-Za-z, ]+)\] were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "bowler_overs",
            "overs": parse_number_list(match.group(1)),
            "players": parse_player_list(match.group(2)),
            "value": int(match.group(3)),
        }

    match = re.fullmatch(
        r"across \[(.*)\], the combined team runs were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "team_segments",
            "segments": parse_segments(match.group(1)),
            "value": int(match.group(2)),
        }

    match = re.fullmatch(
        r"in marked cells \[([0-9., ]+)\], the combined bat runs of "
        r"\[([A-Za-z, ]+)\] were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "batter_marked",
            "deliveries": parse_deliveries(match.group(1)),
            "players": parse_player_list(match.group(2)),
            "value": int(match.group(3)),
        }

    match = re.fullmatch(
        r"the marked delivery cells \[([0-9., ]+)\] contained "
        r"(\d+) combined team runs\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "team_marked",
            "deliveries": parse_deliveries(match.group(1)),
            "value": int(match.group(2)),
        }

    match = re.fullmatch(
        r"across \[(.*)\], the combined bat runs of "
        r"\[([A-Za-z, ]+)\] were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "batter_segments",
            "segments": parse_segments(match.group(1)),
            "players": parse_player_list(match.group(2)),
            "value": int(match.group(3)),
        }

    match = re.fullmatch(
        r"across overs \[([0-9, ]+)\], the combined bat runs of "
        r"\[([A-Za-z, ]+)\] were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "batter_overs",
            "overs": parse_number_list(match.group(1)),
            "players": parse_player_list(match.group(2)),
            "value": int(match.group(3)),
        }

    match = re.fullmatch(
        r"the combined leg-byes recorded in overs \[([0-9, ]+)\] were (\d+)\.",
        body,
    )
    if match:
        return {
            "number": number,
            "kind": "leg_byes_overs",
            "overs": parse_number_list(match.group(1)),
            "value": int(match.group(2)),
        }

    raise ValueError(f"Unsupported reconciliation wording: {body}")


def text_to_tuples(text):
    events = []
    reconciliations = []
    bowlers = []
    current_over = None
    current_bowler = None
    ball = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        over_match = re.fullmatch(r"Over (\d+), ([A-Za-z]+):", line)
        if over_match:
            current_over = int(over_match.group(1))
            current_bowler = over_match.group(2)
            if current_bowler not in bowlers:
                bowlers.append(current_bowler)
            ball = 0
            continue

        clip_match = re.fullmatch(
            r"(clip-\d+) at this point, faced by ([A-Za-z]+): "
            r"feed one reads (.*); feed two reads (.*)\.",
            line,
        )
        if clip_match:
            ball += 1
            events.append({
                "over": current_over,
                "ball": ball,
                "bowler": current_bowler,
                "batter": clip_match.group(2),
                "clip": clip_match.group(1),
                "feed_one": parse_reading(clip_match.group(3)),
                "feed_two": parse_reading(clip_match.group(4)),
                "wicket": False,
            })
            continue

        wicket_match = re.fullmatch(
            r"Next, ([A-Za-z]+) bowls ([A-Za-z]+) for no run; "
            r"the wicket stands\.",
            line,
        )
        if wicket_match:
            ball += 1
            events.append({
                "over": current_over,
                "ball": ball,
                "bowler": wicket_match.group(1),
                "batter": wicket_match.group(2),
                "bat": 0,
                "leg_byes": 0,
                "wicket": True,
            })
            continue

        certain_match = re.fullmatch(
            r"Next, ([A-Za-z]+) to ([A-Za-z]+): (.*)\.",
            line,
        )
        if certain_match:
            ball += 1
            reading = parse_reading(certain_match.group(3))
            events.append({
                "over": current_over,
                "ball": ball,
                "bowler": certain_match.group(1),
                "batter": certain_match.group(2),
                **reading,
                "wicket": False,
            })
            continue

        if line.startswith("Reconciliation "):
            reconciliations.append(parse_reconciliation(line))

    if len(events) != 72:
        raise ValueError(f"Expected 72 event tuples, extracted {len(events)}")
    if len(reconciliations) != 24:
        raise ValueError(
            f"Expected 24 reconciliation tuples, extracted {len(reconciliations)}"
        )
    return {"events": events, "reconciliations": reconciliations, "bowlers": bowlers}


def contribution(event, outcome, constraint):
    kind = constraint["kind"]
    over = event["over"]
    delivery = (event["over"], event["ball"])
    segment = (event["over"], 1 if event["ball"] <= 3 else 2)
    bat = outcome["bat"]
    leg_byes = outcome["leg_byes"]

    if kind == "team_overs":
        return bat + leg_byes if over in constraint["overs"] else 0
    if kind == "bowler_overs":
        return (
            bat
            if over in constraint["overs"] and event["bowler"] in constraint["players"]
            else 0
        )
    if kind == "team_segments":
        return bat + leg_byes if segment in map(tuple, constraint["segments"]) else 0
    if kind == "batter_marked":
        return (
            bat
            if delivery in map(tuple, constraint["deliveries"])
            and event["batter"] in constraint["players"]
            else 0
        )
    if kind == "team_marked":
        return (
            bat + leg_byes
            if delivery in map(tuple, constraint["deliveries"])
            else 0
        )
    if kind == "batter_segments":
        return (
            bat
            if segment in map(tuple, constraint["segments"])
            and event["batter"] in constraint["players"]
            else 0
        )
    if kind == "batter_overs":
        return (
            bat
            if over in constraint["overs"] and event["batter"] in constraint["players"]
            else 0
        )
    if kind == "leg_byes_overs":
        return leg_byes if over in constraint["overs"] else 0
    raise ValueError(kind)


def integrate_tuples(tuple_data):
    events = tuple_data["events"]
    constraints = tuple_data["reconciliations"]
    clips = [event for event in events if "clip" in event]

    matrix = []
    targets = []
    for constraint in constraints:
        base = 0
        row = []
        for event in events:
            if "clip" in event:
                first = contribution(event, event["feed_one"], constraint)
                second = contribution(event, event["feed_two"], constraint)
                base += first
                row.append(second - first)
            else:
                base += contribution(
                    event,
                    {"bat": event["bat"], "leg_byes": event["leg_byes"]},
                    constraint,
                )
        matrix.append(row)
        targets.append(constraint["value"] - base)

    matrix = np.asarray(matrix, dtype=float)
    targets = np.asarray(targets, dtype=float)
    if np.linalg.matrix_rank(matrix) != len(clips):
        raise ValueError("Integration matrix is not full rank")

    raw_solution = np.linalg.solve(matrix, targets)
    choices = np.rint(raw_solution).astype(int)
    if not np.all((choices == 0) | (choices == 1)):
        raise ValueError(f"Non-binary integrated solution: {raw_solution}")
    if not np.allclose(matrix @ choices, targets):
        raise ValueError("Integrated solution fails reconciliation equations")

    integrated_events = []
    clip_choices = {}
    clip_index = 0
    for event in events:
        integrated = {
            key: value
            for key, value in event.items()
            if key not in ("feed_one", "feed_two", "clip")
        }
        if "clip" in event:
            choice = int(choices[clip_index])
            outcome = event["feed_two"] if choice else event["feed_one"]
            integrated.update(outcome)
            clip_choices[event["clip"]] = "feed_two" if choice else "feed_one"
            clip_index += 1
        integrated_events.append(integrated)

    return {
        "events": integrated_events,
        "clip_choices": clip_choices,
        "matrix_rank": int(np.linalg.matrix_rank(matrix)),
        "max_residual": float(np.max(np.abs(matrix @ choices - targets))),
    }


def tuples_to_table(integrated, bowler_order):
    events = integrated["events"]
    batting_order = []
    for event in events:
        if event["batter"] not in batting_order:
            batting_order.append(event["batter"])

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
            for player in batting_order
        },
        "bowling": {
            player: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0}
            for player in bowler_order
        },
        "fall_of_wickets": [],
        "partnerships": [],
    }

    active = batting_order[:2]
    next_batter_index = 2
    partnership = None

    for event in events:
        if event["batter"] not in active:
            raise ValueError(
                f"Tuple sequence has inactive batter {event['batter']} at "
                f"{event['over']}.{event['ball']}"
            )
        other = next(player for player in active if player != event["batter"])
        if partnership is None:
            partnership = {
                "number": len(result["partnerships"]) + 1,
                "batter_1": event["batter"],
                "batter_2": other,
                "runs": 0,
                "extras": 0,
                "legal_balls": 0,
                "end_team_runs": None,
                "ended_by": None,
            }

        bat = event["bat"]
        leg_byes = event["leg_byes"]
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

        if event["wicket"]:
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

            active.remove(event["batter"])
            if next_batter_index >= len(batting_order):
                raise ValueError("No next batter available")
            active.append(batting_order[next_batter_index])
            next_batter_index += 1

    if partnership is not None:
        partnership["end_team_runs"] = result["summary"]["runs"]
        result["partnerships"].append(partnership)
    return result


tuple_data = text_to_tuples(case_text)
(root / "t3_stage1_tuples.json").write_text(
    json.dumps(tuple_data, indent=2),
    encoding="utf-8",
)

integrated = integrate_tuples(tuple_data)
(root / "t3_stage2_integrated.json").write_text(
    json.dumps(integrated, indent=2),
    encoding="utf-8",
)

prediction = tuples_to_table(integrated, tuple_data["bowlers"])
(root / "t3_prediction.json").write_text(
    json.dumps(prediction, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    "event_tuples": len(tuple_data["events"]),
    "reconciliation_tuples": len(tuple_data["reconciliations"]),
    "matrix_rank": integrated["matrix_rank"],
    "max_residual": integrated["max_residual"],
    "clip_choices": integrated["clip_choices"],
}, indent=2))
