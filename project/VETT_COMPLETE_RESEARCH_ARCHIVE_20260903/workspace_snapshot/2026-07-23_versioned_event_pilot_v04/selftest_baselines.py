"""Strict lossy-representation self-tests for T³ and Map&Make.

These are process diagnostics, not executions of the authors' model/API
configurations. Each method is tested with two reasonable no-state policies,
and the better error rate is reported.
"""

import json
from pathlib import Path


root = Path(__file__).resolve().parent
graph = json.loads((root / "v04_hidden_event_graph.json").read_text(encoding="utf-8"))
gold = json.loads((root / "v04_gold.json").read_text(encoding="utf-8"))
canonical = json.loads((root / "v04_canonical_events.json").read_text(encoding="utf-8"))

batters = list(gold["batting"])
bowlers = list(gold["bowling"])


def empty_projection():
    return {
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


def aggregate_unordered(outcomes):
    """Aggregate flat or atomic event facts after order/identity was lost."""
    result = empty_projection()
    for item in outcomes:
        batter = item["batter"]
        bowler = item["bowler"]
        outcome = item["outcome"]
        bat = outcome["bat"]
        leg_byes = outcome["leg_byes"]
        wicket = outcome["wicket"]
        result["summary"]["runs"] += bat + leg_byes
        result["summary"]["wickets"] += int(wicket)
        result["summary"]["legal_balls"] += 1
        result["summary"]["leg_byes"] += leg_byes
        result["batting"][batter]["runs"] += bat
        result["batting"][batter]["balls"] += 1
        result["batting"][batter]["out"] |= wicket
        result["bowling"][bowler]["legal_balls"] += 1
        result["bowling"][bowler]["runs_conceded"] += bat
        result["bowling"][bowler]["wickets"] += int(wicket)
    # Flat tuples/independent atoms no longer contain an unambiguous canonical
    # event order, so FOW and partnership rows remain absent.
    return result


def event_fact(event_id, outcome):
    event = next(
        event for event in graph["canonical_events"]
        if event["event_id"] == event_id
    )
    return {
        "batter": event["batter"],
        "bowler": event["bowler"],
        "outcome": outcome,
    }


# T³ strict flat tuples: source, status, arrival order and event identity are
# discarded by the generalized (subject, relation, object/value) representation.
t3_count_all = []
for mention in graph["mentions"]:
    if mention["event_id"] is None:
        # Out-of-scope facts become indistinguishable after scope is discarded.
        t3_count_all.append({
            "batter": mention["batter"],
            "bowler": mention["bowler"],
            "outcome": mention["outcome"],
        })
    else:
        t3_count_all.append(event_fact(mention["event_id"], mention["outcome"]))

t3_deduplicated = []
seen = set()
for fact in t3_count_all:
    key = (
        fact["batter"],
        fact["bowler"],
        fact["outcome"]["bat"],
        fact["outcome"]["leg_byes"],
        fact["outcome"]["wicket"],
    )
    if key not in seen:
        seen.add(key)
        t3_deduplicated.append(fact)

t3_predictions = {
    "count_all": aggregate_unordered(t3_count_all),
    "deduplicate_identical": aggregate_unordered(t3_deduplicated),
}


# Map&Make no-state policies. Both receive oracle event alignment, making these
# optimistic diagnostics: one keeps the first proposition for each event; the
# other keeps the last proposition, which can be a stale replay.
mentions_by_event = {}
for mention in graph["mentions"]:
    if mention["event_id"] is not None:
        mentions_by_event.setdefault(mention["event_id"], []).append(mention)

mapmake_first = []
mapmake_last = []
for event in graph["canonical_events"]:
    event_mentions = mentions_by_event[event["event_id"]]
    first = min(event_mentions, key=lambda item: item["arrival_order"])
    last = max(event_mentions, key=lambda item: item["arrival_order"])
    mapmake_first.append(event_fact(event["event_id"], first["outcome"]))
    mapmake_last.append(event_fact(event["event_id"], last["outcome"]))

mapmake_predictions = {
    "first_proposition": aggregate_unordered(mapmake_first),
    "last_proposition": aggregate_unordered(mapmake_last),
}


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


def score(prediction):
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


results = {"T3": {}, "MapMake": {}}
for name, prediction in t3_predictions.items():
    (root / f"t3_{name}_prediction.json").write_text(
        json.dumps(prediction, indent=2),
        encoding="utf-8",
    )
    results["T3"][name] = score(prediction)

for name, prediction in mapmake_predictions.items():
    (root / f"mapmake_{name}_prediction.json").write_text(
        json.dumps(prediction, indent=2),
        encoding="utf-8",
    )
    results["MapMake"][name] = score(prediction)

for method in results:
    best_name = min(
        results[method],
        key=lambda name: results[method][name]["field_error_rate"],
    )
    results[method]["best_variant"] = best_name
    results[method]["best_field_error_rate"] = results[method][best_name][
        "field_error_rate"
    ]

(root / "v04_selftest_results.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    method: {
        "best_variant": results[method]["best_variant"],
        "best_field_error_rate": results[method]["best_field_error_rate"],
        "variants": {
            name: {
                "correct_fields": value["correct_fields"],
                "total_fields": value["total_fields"],
                "field_error_rate": value["field_error_rate"],
            }
            for name, value in results[method].items()
            if isinstance(value, dict)
        },
    }
    for method in ("T3", "MapMake")
}, indent=2))
