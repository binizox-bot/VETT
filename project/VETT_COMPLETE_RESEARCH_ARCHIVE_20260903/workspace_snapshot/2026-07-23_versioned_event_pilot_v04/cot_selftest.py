"""Controlled direct/CoT process checks on the v0.4 visible text.

This is not an API reproduction of a sampled LLM.  It operationalizes a
paper-style CoT upper bound: reason over the stated scope/source rules and
apply every authoritative final ruling before projecting the tables.

Both predictions are constructed from v04_case.txt.  The gold file is opened
only after the prediction files have been written.
"""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "v04_case.txt"

RUN_VALUES = {
    "no": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "six": 6,
    "eight": 8,
}
ORDINAL_VALUES = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
}
BATTER_ORDER = ["Aaron", "Connor", "Dylan", "Ethan", "Gavin", "Julian", "Cameron"]
BOWLER_ORDER = ["Frost", "Pike", "Stone", "Rowe", "Shaw", "Hart"]


def parse_description(description):
    description = description.rstrip(".")

    match = re.fullmatch(
        r"([A-Z][a-z]+) has ([A-Z][a-z]+) caught for no run",
        description,
    )
    if match:
        bowler, batter = match.groups()
        return {
            "batter": batter,
            "bowler": bowler,
            "bat": 0,
            "leg_byes": 0,
            "wicket": True,
        }

    match = re.fullmatch(
        r"([A-Z][a-z]+) faces ([A-Z][a-z]+); (\d+) leg-byes are signalled",
        description,
    )
    if match:
        batter, bowler, leg_byes = match.groups()
        return {
            "batter": batter,
            "bowler": bowler,
            "bat": 0,
            "leg_byes": int(leg_byes),
            "wicket": False,
        }

    match = re.fullmatch(
        r"([A-Z][a-z]+) to ([A-Z][a-z]+): "
        r"(no|one|two|three|four|six|eight) (?:bat run|bat runs|run)",
        description,
    )
    if match:
        bowler, batter, run_word = match.groups()
        return {
            "batter": batter,
            "bowler": bowler,
            "bat": RUN_VALUES[run_word],
            "leg_byes": 0,
            "wicket": False,
        }

    raise ValueError(f"Unparsed event description: {description!r}")


def recover_primary_events(case_text):
    primary_text = case_text.split("PRIMARY LIVE FEED", 1)[1].split(
        "FINAL SCORER RULINGS", 1
    )[0]
    events = []
    current_over = None
    passage = 0
    for line in primary_text.splitlines():
        heading = re.fullmatch(
            r"([A-Z][a-z]+)'s (?:opening|return) spell, over (\d+):",
            line.strip(),
        )
        if heading:
            current_over = int(heading.group(2))
            passage = 0
            continue
        if line.strip().startswith("Next passage:"):
            passage += 1
            description = line.strip().removeprefix("Next passage: ").rstrip(".")
            event = parse_description(description)
            event["over"] = current_over
            event["passage"] = passage
            events.append(event)

    if len(events) != 72:
        raise ValueError(f"Expected 72 primary events, recovered {len(events)}")
    return events


def apply_final_rulings(events, case_text):
    final_text = case_text.split("FINAL SCORER RULINGS", 1)[1].split(
        "LATE CACHE AND ARCHIVE PACKETS", 1
    )[0]
    indexed = {(event["over"], event["passage"]): event for event in events}
    applied = []
    pattern = re.compile(
        r"Final ruling: in over (\d+), replace the "
        r"(first|second|third|fourth|fifth|sixth) passage of "
        r"([A-Z][a-z]+)'s spell\. The ratified event is: (.+)\."
    )
    for line in final_text.splitlines():
        match = pattern.fullmatch(line.strip())
        if not match:
            continue
        over_word, ordinal_word, named_bowler, description = match.groups()
        key = (int(over_word), ORDINAL_VALUES[ordinal_word])
        replacement = parse_description(description)
        if replacement["bowler"] != named_bowler:
            raise ValueError(f"Bowler mismatch in ruling {line!r}")
        replacement["over"], replacement["passage"] = key
        indexed[key] = replacement
        applied.append(key)

    if len(applied) != 30 or len(set(applied)) != 30:
        raise ValueError(f"Expected 30 unique rulings, recovered {len(set(applied))}")
    return [indexed[(over, passage)] for over in range(1, 13) for passage in range(1, 7)]


def project(events):
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
            batter: {"runs": 0, "balls": 0, "out": False}
            for batter in BATTER_ORDER
        },
        "bowling": {
            bowler: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0}
            for bowler in BOWLER_ORDER
        },
        "fall_of_wickets": [],
        "partnerships": [],
    }

    partnership = None
    seen_batters = []
    partnership_pairs = []
    segment_batters = []
    for event in events:
        if event["batter"] not in segment_batters:
            segment_batters.append(event["batter"])
        if event["wicket"]:
            partnership_pairs.append(segment_batters)
            segment_batters = []
    if segment_batters:
        partnership_pairs.append(segment_batters)
    if any(len(pair) != 2 for pair in partnership_pairs):
        raise ValueError(f"Invalid partnership pairs: {partnership_pairs!r}")
    team_runs = 0
    wicket_number = 0

    for event in events:
        batter = event["batter"]
        bowler = event["bowler"]
        bat = event["bat"]
        leg_byes = event["leg_byes"]
        wicket = event["wicket"]
        event_runs = bat + leg_byes

        if batter not in seen_batters:
            seen_batters.append(batter)

        if partnership is None:
            pair = partnership_pairs[wicket_number]
            partnership = {
                "number": wicket_number + 1,
                "batter_1": pair[0],
                "batter_2": pair[1],
                "runs": 0,
                "extras": 0,
                "legal_balls": 0,
                "end_team_runs": None,
                "ended_by": None,
            }

        team_runs += event_runs
        result["summary"]["runs"] += event_runs
        result["summary"]["wickets"] += int(wicket)
        result["summary"]["legal_balls"] += 1
        result["summary"]["leg_byes"] += leg_byes

        result["batting"][batter]["runs"] += bat
        result["batting"][batter]["balls"] += 1
        result["batting"][batter]["out"] |= wicket

        result["bowling"][bowler]["legal_balls"] += 1
        result["bowling"][bowler]["runs_conceded"] += bat
        result["bowling"][bowler]["wickets"] += int(wicket)

        partnership["runs"] += event_runs
        partnership["extras"] += leg_byes
        partnership["legal_balls"] += 1

        if wicket:
            wicket_number += 1
            result["fall_of_wickets"].append({
                "batter": batter,
                "team_runs": team_runs,
                "wicket_number": wicket_number,
            })
            partnership["end_team_runs"] = team_runs
            partnership["ended_by"] = batter
            result["partnerships"].append(partnership)
            partnership = None

    if partnership is not None:
        partnership["end_team_runs"] = team_runs
        result["partnerships"].append(partnership)
    return result


def flatten(value, prefix=""):
    output = {}
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            output.update(flatten(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}.{index}" if prefix else str(index)
            output.update(flatten(child, child_prefix))
    else:
        output[prefix] = value
    return output


def score(prediction, gold):
    gold_flat = flatten(gold)
    pred_flat = flatten(prediction)
    keys = sorted(set(gold_flat) | set(pred_flat))
    errors = [
        {
            "field": key,
            "gold": gold_flat.get(key, "<missing>"),
            "prediction": pred_flat.get(key, "<missing>"),
        }
        for key in keys
        if gold_flat.get(key) != pred_flat.get(key)
    ]
    return {
        "correct_fields": len(keys) - len(errors),
        "total_fields": len(keys),
        "field_accuracy": (len(keys) - len(errors)) / len(keys),
        "field_error_rate": len(errors) / len(keys),
        "table_exact_match": not errors,
        "errors": errors,
    }


case_text = CASE_PATH.read_text(encoding="utf-8")
primary_events = recover_primary_events(case_text)
cot_events = apply_final_rulings([dict(event) for event in primary_events], case_text)

predictions = {
    "paper_cot_structured_upper_bound": project(cot_events),
}

# Persist predictions before opening the gold file.
for name, prediction in predictions.items():
    (ROOT / f"{name}_prediction.json").write_text(
        json.dumps(prediction, indent=2),
        encoding="utf-8",
    )

(ROOT / "cot_recovered_events.json").write_text(
    json.dumps(cot_events, indent=2),
    encoding="utf-8",
)

gold = json.loads((ROOT / "v04_gold.json").read_text(encoding="utf-8"))
results = {name: score(prediction, gold) for name, prediction in predictions.items()}
(ROOT / "cot_selftest_results.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    name: {
        "correct_fields": result["correct_fields"],
        "total_fields": result["total_fields"],
        "field_error_rate": result["field_error_rate"],
        "table_exact_match": result["table_exact_match"],
    }
    for name, result in results.items()
}, indent=2))
