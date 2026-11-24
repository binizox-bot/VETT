"""Controlled v0.5 process diagnostics for T³, Map&Make and CoT.

These are reproducible representation/reasoning proxies, not author API runs.
The oracle follows the complete recursive rule and must recover the 397-field
gold exactly.  Baselines receive deliberately generous information where
possible, but do not receive the full recursive event-state mechanism.
"""

import json
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GRAPH = json.loads((ROOT / "v05_hidden_event_graph.json").read_text(encoding="utf-8"))
GOLD = json.loads((ROOT / "v05_gold.json").read_text(encoding="utf-8"))
SOURCES = ["Amber", "Blue", "Cedar", "Delta"]
SOURCE_CODE = {source: index for index, source in enumerate(SOURCES)}
BATTERS = list(GOLD["batting"])
BOWLERS = list(GOLD["bowling"])


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


def selected_event(event_record, claim):
    return {
        "slot": event_record["slot"],
        "over": event_record["over"],
        "passage": event_record["passage"],
        "batter": claim["batter"],
        "bowler": claim["bowler"],
        "source": claim["source"],
        "claim_id": claim["claim_id"],
        "outcome": deepcopy(claim["outcome"]),
    }


def claim_from_source(event_record, source):
    return next(claim for claim in event_record["claims"] if claim["source"] == source)


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
            batter: {"runs": 0, "balls": 0, "out": False}
            for batter in BATTERS
        },
        "bowling": {
            bowler: {"legal_balls": 0, "runs_conceded": 0, "wickets": 0}
            for bowler in BOWLERS
        },
        "fall_of_wickets": [],
        "partnerships": [],
        "event_audit": [],
    }


def update_aggregate(result, event):
    outcome = event["outcome"]
    batter = event["batter"]
    bowler = event["bowler"]
    total_runs = (
        outcome["bat"]
        + outcome["leg_byes"]
        + outcome["wides"]
        + outcome["no_balls"]
    )
    result["summary"]["runs"] += total_runs
    result["summary"]["wickets"] += int(outcome["wicket"])
    result["summary"]["legal_balls"] += int(outcome["legal"])
    result["summary"]["wides"] += outcome["wides"]
    result["summary"]["no_balls"] += outcome["no_balls"]
    result["summary"]["leg_byes"] += outcome["leg_byes"]
    result["batting"][batter]["runs"] += outcome["bat"]
    result["batting"][batter]["balls"] += int(outcome["legal"])
    result["batting"][batter]["out"] |= outcome["wicket"]
    result["bowling"][bowler]["legal_balls"] += int(outcome["legal"])
    result["bowling"][bowler]["runs_conceded"] += (
        outcome["bat"] + outcome["wides"] + outcome["no_balls"]
    )
    result["bowling"][bowler]["wickets"] += int(outcome["wicket"])
    return total_runs


def project_ordered(events):
    result = empty_projection()
    team_runs = 0
    wickets_used_for_rows = 0
    current_partnership = {
        "events": [],
        "runs": 0,
        "extras": 0,
        "legal_balls": 0,
    }

    for event in events:
        outcome = event["outcome"]
        event_runs = update_aggregate(result, event)
        team_runs += event_runs

        result["event_audit"].append({
            "accepted_source": event["source"],
            "accepted_claim_id": event["claim_id"],
            "outcome_type": outcome_type(outcome),
            "outcome_value": outcome_value(outcome),
        })

        current_partnership["events"].append(event)
        current_partnership["runs"] += event_runs
        current_partnership["extras"] += (
            outcome["leg_byes"] + outcome["wides"] + outcome["no_balls"]
        )
        current_partnership["legal_balls"] += int(outcome["legal"])

        if outcome["wicket"] and wickets_used_for_rows < 5:
            wickets_used_for_rows += 1
            result["fall_of_wickets"].append({
                "batter": event["batter"],
                "team_runs": team_runs,
                "wicket_number": wickets_used_for_rows,
            })
            add_partnership(
                result,
                current_partnership,
                team_runs,
                event["batter"],
            )
            current_partnership = {
                "events": [],
                "runs": 0,
                "extras": 0,
                "legal_balls": 0,
            }

    if current_partnership["events"] or len(result["partnerships"]) < 6:
        add_partnership(result, current_partnership, team_runs, None)
    return result


def add_partnership(result, segment, end_team_runs, ended_by):
    players = []
    for event in segment["events"]:
        if event["batter"] not in players:
            players.append(event["batter"])
    players = (players + ["UNKNOWN", "UNKNOWN"])[:2]
    result["partnerships"].append({
        "number": len(result["partnerships"]) + 1,
        "batter_1": players[0],
        "batter_2": players[1],
        "runs": segment["runs"],
        "extras": segment["extras"],
        "legal_balls": segment["legal_balls"],
        "end_team_runs": end_team_runs,
        "ended_by": ended_by,
    })


def aggregate_unordered(events):
    result = empty_projection()
    for event in events:
        update_aggregate(result, event)
    # A flat tuple multiset has neither accepted-claim provenance nor a
    # defensible canonical sequence for FOW and partnerships.
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


def score(prediction):
    gold_flat = flatten(GOLD)
    pred_flat = flatten(prediction)
    errors = [
        {
            "field": key,
            "gold": gold_value,
            "prediction": pred_flat.get(key, "<missing>"),
        }
        for key, gold_value in gold_flat.items()
        if pred_flat.get(key, "<missing>") != gold_value
    ]
    extra_fields = sorted(set(pred_flat) - set(gold_flat))
    by_table = {}
    for error in errors:
        table = error["field"].split(".", 1)[0]
        by_table[table] = by_table.get(table, 0) + 1
    return {
        "correct_fields": len(gold_flat) - len(errors),
        "total_fields": len(gold_flat),
        "field_accuracy": (len(gold_flat) - len(errors)) / len(gold_flat),
        "field_error_rate": len(errors) / len(gold_flat),
        "table_exact_match": not errors and not extra_fields,
        "extra_prediction_fields": len(extra_fields),
        "errors_by_table": by_table,
        "errors": errors,
    }


canonical = GRAPH["canonical_events"]


# Oracle: complete recursive state transition from the visible rule.
oracle_events = []
previous_source_code = 2
previous_outcome = {
    "bat": 0, "leg_byes": 0, "wides": 0, "no_balls": 0,
    "wicket": False, "legal": True,
}
for event_record in canonical:
    accepted_code = (
        previous_source_code
        + event_record["over"]
        + event_record["passage"]
        + event_record["nonce"]
        + state_value(previous_outcome)
    ) % 4
    claim = claim_from_source(event_record, SOURCES[accepted_code])
    oracle_events.append(selected_event(event_record, claim))
    previous_source_code = accepted_code
    previous_outcome = claim["outcome"]


# T³ strict flat facts.  Target and rehearsal claims are counted after chain,
# slot, source and claim ID have been discarded.
all_flat_events = []
seen_flat = set()
deduplicated_flat_events = []
for packet in GRAPH["arrival_packets"]:
    for claim in packet["claims"]:
        event = {
            "batter": claim["batter"],
            "bowler": claim["bowler"],
            "outcome": claim["outcome"],
        }
        all_flat_events.append(event)
        key = (
            event["batter"],
            event["bowler"],
            tuple(sorted(event["outcome"].items())),
        )
        if key not in seen_flat:
            seen_flat.add(key)
            deduplicated_flat_events.append(event)

t3_predictions = {
    "count_all_flat_claims": aggregate_unordered(all_flat_events),
    "deduplicate_identical_flat_claims": aggregate_unordered(
        deduplicated_flat_events
    ),
}


# Map&Make receives optimistic oracle grouping and canonical slot order, but no
# recursive state.  First/last refer to the claim display order inside a packet.
mapmake_predictions = {
    "first_claim_per_slot": project_ordered([
        selected_event(event_record, event_record["claims"][0])
        for event_record in canonical
    ]),
    "last_claim_per_slot": project_ordered([
        selected_event(event_record, event_record["claims"][-1])
        for event_record in canonical
    ]),
}
for source in SOURCES:
    mapmake_predictions[f"static_{source.lower()}"] = project_ordered([
        selected_event(event_record, claim_from_source(event_record, source))
        for event_record in canonical
    ])


# CoT process proxies preserve target scope, packet grouping and canonical
# order.  They test plausible one-pass shortcuts that stop short of the full
# recursive event-state calculation required by the case.
cot_event_variants = {}

# Reset the state at every slot: uses over, passage and nonce but loses the
# chain dependency.
reset_events = []
for event_record in canonical:
    code = (2 + event_record["over"] + event_record["passage"] + event_record["nonce"]) % 4
    reset_events.append(
        selected_event(event_record, claim_from_source(event_record, SOURCES[code]))
    )
cot_event_variants["nonrecursive_state_reset"] = reset_events

# Carry previous chosen source, but omit the previous accepted outcome value.
source_only_events = []
previous_code = 2
for event_record in canonical:
    code = (
        previous_code
        + event_record["over"]
        + event_record["passage"]
        + event_record["nonce"]
    ) % 4
    claim = claim_from_source(event_record, SOURCES[code])
    source_only_events.append(selected_event(event_record, claim))
    previous_code = code
cot_event_variants["recursive_source_only"] = source_only_events

# Local recency/corroboration shortcuts.
cot_event_variants["packet_first"] = [
    selected_event(event_record, event_record["claims"][0])
    for event_record in canonical
]
cot_event_variants["packet_last"] = [
    selected_event(event_record, event_record["claims"][-1])
    for event_record in canonical
]
for source in SOURCES:
    cot_event_variants[f"static_{source.lower()}"] = [
        selected_event(event_record, claim_from_source(event_record, source))
        for event_record in canonical
    ]

cot_predictions = {
    name: project_ordered(events)
    for name, events in cot_event_variants.items()
}


def evaluate_group(predictions):
    results = {}
    for name, prediction in predictions.items():
        (ROOT / f"{name}_prediction.json").write_text(
            json.dumps(prediction, indent=2),
            encoding="utf-8",
        )
        results[name] = score(prediction)
    best_variant = min(
        results,
        key=lambda name: results[name]["field_error_rate"],
    )
    return {
        "variants": results,
        "best_variant": best_variant,
        "best_field_error_rate": results[best_variant]["field_error_rate"],
    }


results = {
    "Oracle": {
        "complete_recursive_solver": score(project_ordered(oracle_events)),
    },
    "T3": evaluate_group(t3_predictions),
    "MapMake": evaluate_group(mapmake_predictions),
    "CoT": evaluate_group(cot_predictions),
}

(ROOT / "oracle_prediction.json").write_text(
    json.dumps(project_ordered(oracle_events), indent=2),
    encoding="utf-8",
)
(ROOT / "v05_selftest_results.json").write_text(
    json.dumps(results, indent=2),
    encoding="utf-8",
)

print(json.dumps({
    "Oracle": {
        "correct_fields": results["Oracle"]["complete_recursive_solver"]["correct_fields"],
        "total_fields": results["Oracle"]["complete_recursive_solver"]["total_fields"],
        "field_error_rate": results["Oracle"]["complete_recursive_solver"]["field_error_rate"],
    },
    **{
        method: {
            "best_variant": results[method]["best_variant"],
            "best_field_error_rate": results[method]["best_field_error_rate"],
            "variants": {
                name: {
                    "correct_fields": value["correct_fields"],
                    "total_fields": value["total_fields"],
                    "field_error_rate": value["field_error_rate"],
                }
                for name, value in results[method]["variants"].items()
            },
        }
        for method in ("T3", "MapMake", "CoT")
    },
}, indent=2))
