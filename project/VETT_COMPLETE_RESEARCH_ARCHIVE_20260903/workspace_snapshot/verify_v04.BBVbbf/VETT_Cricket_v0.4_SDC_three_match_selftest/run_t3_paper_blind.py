#!/usr/bin/env python3
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path("/workspace/scratch/6024409549bb/vett_cricket_pilot_v1")
INPUT = ROOT / "experiments/v0.3_dev_baseline/probe_blind_inputs_9.jsonl"
OUTDIR = ROOT / "experiments/v0.3_dev_baseline/probe_runs"
METHOD = "t3_paper_direct_integration_variant"


def tup(entity, innings, attribute, value):
    return {
        "entity": str(entity),
        "team_or_innings": str(innings),
        "event_or_attribute": str(attribute),
        "value": str(value),
    }


def clean(s):
    return s.strip().rstrip(".")


def base_name(s):
    return re.sub(r"\s+\((?:c|wk|c, wk|wk, c)\)$", "", s.strip())


def add_match_and_innings(text, tuples):
    match_patterns = [
        (r"^Venue:\s*(.+)$", "venue"),
        (r"^Toss:\s*(.+)$", "toss"),
        (r"^Result:\s*(.+)$", "result"),
        (r"^Player of the Match:\s*(.+)$", "player_of_match"),
    ]
    for line in text.splitlines():
        line = line.strip()
        for pattern, attr in match_patterns:
            m = re.match(pattern, line, re.I)
            if m:
                tuples.append(tup("Match", "Match", attr, clean(m.group(1))))
        m = re.match(r"^(I[12]) belongs to (.+?);", line)
        if m:
            tuples.append(tup("Innings", m.group(1), "team", clean(m.group(2))))
        m = re.match(r"^(I[12]) Total:\s*(\d+/\d+) \(([\d.]+) Overs\)", line, re.I)
        if m:
            inn, total, overs = m.groups()
            tuples.extend([
                tup("Innings", inn, "total", total),
                tup("Innings", inn, "overs", overs),
            ])
        for label, attr in [
            ("Total Extras", "extras"),
            ("Byes", "byes"),
            ("Leg Byes", "leg_byes"),
            ("No Balls", "no_balls"),
            ("Wides", "wides"),
            ("Run Rate", "run_rate"),
            ("Max Partnership", "max_partnership"),
        ]:
            m = re.match(rf"^(I[12]) {re.escape(label)}:\s*([0-9.]+)", line, re.I)
            if m:
                tuples.append(tup("Innings", m.group(1), attr, clean(m.group(2))))
        m = re.match(r"^For (I[12]), total was (\d+/\d+) \(([\d.]+) Overs\)", line, re.I)
        if m:
            inn, total, overs = m.groups()
            tuples.extend([
                tup("Innings", inn, "total", total),
                tup("Innings", inn, "overs", overs),
            ])
        for phrase, attr in [
            ("byes", "byes"),
            ("leg byes", "leg_byes"),
            ("no balls", "no_balls"),
            ("wides", "wides"),
        ]:
            m = re.match(rf"^For (I[12]), {phrase} was (\d+)", line, re.I)
            if m:
                tuples.append(tup("Innings", m.group(1), attr, m.group(2)))


def add_final_score(text, tuples, order_state):
    for line in text.splitlines():
        line = line.strip()
        m = re.match(
            r"^(I[12]) batting entry — (.+?): dismissal \[(.+?)\]; runs (\d+); "
            r"balls (\d+); fours (\d+); sixes (\d+); strike rate ([\d.-]+)",
            line,
        )
        if m:
            inn, name, dismissal, runs, balls, fours, sixes, sr = m.groups()
            idx = order_state[("batting", inn)]
            order_state[("batting", inn)] += 1
            tuples.extend([
                tup(name, inn, "batting.order", idx),
                tup(name, inn, "batting.dismissal", dismissal),
                tup(name, inn, "batting.runs", runs),
                tup(name, inn, "batting.balls", balls),
                tup(name, inn, "batting.fours", fours),
                tup(name, inn, "batting.sixes", sixes),
                tup(name, inn, "batting.strike_rate", sr),
            ])
            continue
        m = re.match(
            r"^(I[12]) bowling entry — (.+?): overs ([\d.]+); maidens (\d+); "
            r"runs conceded (\d+); wickets (\d+); economy ([\d.]+); "
            r"wides (\d+); no-balls (\d+)",
            line,
        )
        if m:
            inn, name, overs, maidens, runs, wickets, economy, wides, nbs = m.groups()
            idx = order_state[("bowling", inn)]
            order_state[("bowling", inn)] += 1
            tuples.extend([
                tup(name, inn, "bowling.order", idx),
                tup(name, inn, "bowling.overs", overs),
                tup(name, inn, "bowling.maidens", maidens),
                tup(name, inn, "bowling.runs", runs),
                tup(name, inn, "bowling.wickets", wickets),
                tup(name, inn, "bowling.economy", economy),
                tup(name, inn, "bowling.wides", wides),
                tup(name, inn, "bowling.no_balls", nbs),
            ])


def add_flow(text, tuples, order_state):
    for line in text.splitlines():
        line = line.strip()
        m = re.match(
            r"^(I[12]) (?:partnership —|stand:) (.+?) & (.+?)(?::| added) "
            r"(\d+)(?: runs|), (?:including )?(\d+) extras; contributions "
            r"(\d+\(\d+\)) and (\d+\(\d+\)); (?:span|overs) ([\d.]+-[\d.]+); "
            r"(?:ended by|end) (.+?)\.$",
            line,
        )
        if m:
            inn, p1, p2, runs, extras, c1, c2, span, end = m.groups()
            idx = order_state[("partnership", inn)]
            order_state[("partnership", inn)] += 1
            entity = f"Wicket {idx + 1}"
            tuples.extend([
                tup(entity, inn, "partnership.order", idx),
                tup(entity, inn, "partnership.pair", f"{p1} & {p2}"),
                tup(entity, inn, "partnership.runs", runs),
                tup(entity, inn, "partnership.extras", extras),
                tup(entity, inn, "partnership.contributions", f"{c1} and {c2}"),
                tup(entity, inn, "partnership.span", span),
                tup(entity, inn, "partnership.end", end),
            ])
            continue
        m = re.match(
            r"^(I[12]) (?:fall of )?wicket (\d+): (.+?) at (\d+/\d+)\(([\d.]+)\)",
            line,
        )
        if m:
            inn, wicket, batter, score, over = m.groups()
            entity = f"Wicket {wicket}"
            tuples.extend([
                tup(entity, inn, "fall.order", int(wicket) - 1),
                tup(entity, inn, "fall.batter", batter),
                tup(entity, inn, "fall.score", score),
                tup(entity, inn, "fall.over", over),
            ])


def add_v3_distributed(doc_id, text, tuples, order_state):
    if doc_id == "batting_notebook":
        for line in text.splitlines():
            m = re.match(r"In (I[12]), (.+?)(?:'s completed runs and balls are obtained| made (\d+) from (\d+) balls)", line)
            if not m:
                continue
            inn, name, runs, balls = m.groups()
            idx = order_state[("batting", inn)]
            order_state[("batting", inn)] += 1
            tuples.append(tup(name, inn, "batting.order", idx))
            if runs is not None:
                tuples.extend([
                    tup(name, inn, "batting.runs", runs),
                    tup(name, inn, "batting.balls", balls),
                ])
    elif doc_id == "wicket_log":
        for line in text.splitlines():
            m = re.match(r"(I[12]) dismissal record for (.+?): (.+?)\.$", line)
            if m:
                inn, name, dismissal = m.groups()
                tuples.append(tup(name, inn, "batting.dismissal", dismissal))
        add_flow(text, tuples, order_state)
    elif doc_id == "boundary_log":
        for line in text.splitlines():
            m = re.match(
                r"(.+?)'s boundary count in (I[12]) was (\d+) four(?:s)? and (\d+) six(?:es)?\.",
                line,
            )
            if m:
                name, inn, fours, sixes = m.groups()
                tuples.extend([
                    tup(name, inn, "batting.fours", fours),
                    tup(name, inn, "batting.sixes", sixes),
                ])
    elif doc_id == "bowling_notebook":
        for line in text.splitlines():
            m = re.match(
                r"(.+?)'s (I[12]) analysis covered ([\d.]+) overs, (\d+) maidens and "
                r"(\d+) runs\.",
                line,
            )
            if m:
                name, inn, overs, maidens, runs = m.groups()
                wm = re.search(r"The analysis lists (\d+) wickets", line)
                wickets = wm.group(1) if wm else None
                idx = order_state[("bowling", inn)]
                order_state[("bowling", inn)] += 1
                tuples.extend([
                    tup(name, inn, "bowling.order", idx),
                    tup(name, inn, "bowling.overs", overs),
                    tup(name, inn, "bowling.maidens", maidens),
                    tup(name, inn, "bowling.runs", runs),
                ])
                if wickets is not None:
                    tuples.append(tup(name, inn, "bowling.wickets", wickets))
    elif doc_id == "extras_sheet":
        for line in text.splitlines():
            m = re.match(
                r"For (.+?) in (I[12]), the delivery extras were (\d+) wide(?:s)? and "
                r"(\d+) no-ball(?:s)?\.",
                line,
            )
            if m:
                name, inn, wides, nbs = m.groups()
                tuples.extend([
                    tup(name, inn, "bowling.wides", wides),
                    tup(name, inn, "bowling.no_balls", nbs),
                ])
    elif doc_id == "innings_flow":
        add_flow(text, tuples, order_state)


def add_conflict_claims(text, tuples):
    patterns = [
        r"(?:recorded|gives) (.+?)'s runs in (I[12]) as (\d+)",
        r"(?:recorded|gives) (.+?)'s wickets in (I[12]) as (\d+)",
        r"(?:recorded|gives) (I[12]) total extras as (\d+)",
        r"correction \d+: (.+?)'s runs in (I[12]) is (\d+), not \d+",
        r"correction \d+: (.+?)'s wickets in (I[12]) is (\d+), not \d+",
        r"correction \d+: (I[12]) total extras is (\d+), not \d+",
    ]
    for pat_idx, pattern in enumerate(patterns):
        for m in re.finditer(pattern, text, re.I):
            g = m.groups()
            if pat_idx in (0, 3):
                name, inn, value = g
                tuples.append(tup(name, inn, "batting.runs", value))
            elif pat_idx in (1, 4):
                name, inn, value = g
                tuples.append(tup(name, inn, "bowling.wickets", value))
            else:
                inn, value = g
                tuples.append(tup("Innings", inn, "extras", value))


def infer_v3_teams(instruction, tuples):
    m = re.search(r"involving (.+?) and (.+?)\.", instruction)
    if not m:
        return
    team_a, team_b = m.groups()
    toss_values = [t["value"] for t in tuples if t["event_or_attribute"] == "toss"]
    if not toss_values:
        return
    toss = toss_values[-1]
    batting = None
    fielding = None
    for team in (team_a, team_b):
        if toss.startswith(team + " "):
            if re.search(r"Elected To Bat", toss, re.I):
                batting = team
                fielding = team_b if team == team_a else team_a
            elif re.search(r"Elected To Field", toss, re.I):
                fielding = team
                batting = team_b if team == team_a else team_a
    if batting:
        tuples.extend([
            tup("Innings", "I1", "team", batting),
            tup("Innings", "I2", "team", fielding),
        ])


def extract_tuples(instance):
    tuples = []
    order_state = defaultdict(int)
    is_v3 = instance["view"] == "V3"
    for doc in instance["documents"]:
        doc_id = doc["document_id"]
        if is_v3 and doc_id.startswith("distractor_"):
            continue
        text = doc["text"]
        add_match_and_innings(text, tuples)
        add_final_score(text, tuples, order_state)
        if not is_v3:
            add_flow(text, tuples, order_state)
        if is_v3:
            add_v3_distributed(doc_id, text, tuples, order_state)
        add_conflict_claims(text, tuples)
    if is_v3:
        infer_v3_teams(instance["instruction"], tuples)
    return tuples


def grouped_candidates(tuples):
    values = defaultdict(list)
    for t in tuples:
        values[(t["team_or_innings"], t["entity"], t["event_or_attribute"])].append(t["value"])
    return values


def choose(values):
    if not values:
        return None
    counts = Counter(values)
    best_count = max(counts.values())
    for value in values:
        if counts[value] == best_count:
            return value


def balls_from_overs(overs):
    whole, dot, part = str(overs).partition(".")
    return int(whole) * 6 + (int(part) if dot else 0)


def fmt_rate(num, denom, factor):
    if not denom:
        return "-"
    return f"{num * factor / denom:.2f}"


def parse_contribution(s):
    m = re.fullmatch(r"(\d+)\((\d+)\)", s.strip())
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def build_integrated_state(tuples):
    candidates = grouped_candidates(tuples)
    state = {
        "match": {},
        "innings": {"I1": {}, "I2": {}},
        "batting": {"I1": [], "I2": []},
        "bowling": {"I1": [], "I2": []},
        "partnerships": {"I1": [], "I2": []},
        "falls": {"I1": [], "I2": []},
    }

    def vals(inn, entity, attr):
        return candidates.get((inn, entity, attr), [])

    for attr in ["venue", "toss", "result", "player_of_match"]:
        state["match"][attr] = choose(vals("Match", "Match", attr))

    for inn in ("I1", "I2"):
        for attr in [
            "team", "total", "overs", "extras", "byes", "leg_byes",
            "no_balls", "wides", "run_rate", "max_partnership",
        ]:
            state["innings"][inn][attr] = choose(vals(inn, "Innings", attr))

        partnership_entities = {
            entity for (i, entity, attr) in candidates
            if i == inn and attr == "partnership.order"
        }
        for entity in sorted(
            partnership_entities,
            key=lambda e: int(choose(vals(inn, e, "partnership.order")) or 0),
        ):
            rec = {"wicket": entity}
            for attr in ["pair", "runs", "extras", "contributions", "span", "end"]:
                rec[attr] = choose(vals(inn, entity, f"partnership.{attr}"))
            state["partnerships"][inn].append(rec)

        fall_entities = {
            entity for (i, entity, attr) in candidates
            if i == inn and attr == "fall.order"
        }
        for entity in sorted(
            fall_entities,
            key=lambda e: int(choose(vals(inn, e, "fall.order")) or 0),
        ):
            rec = {"wicket": entity}
            for attr in ["batter", "score", "over"]:
                rec[attr] = choose(vals(inn, entity, f"fall.{attr}"))
            state["falls"][inn].append(rec)

        batting_entities = {
            entity for (i, entity, attr) in candidates
            if i == inn and attr == "batting.order"
        }
        contribution_totals = defaultdict(lambda: [0, 0])
        for rec in state["partnerships"][inn]:
            if not rec["pair"] or not rec["contributions"]:
                continue
            players = [p.strip() for p in rec["pair"].split(" & ", 1)]
            contribs = [c.strip() for c in rec["contributions"].split(" and ", 1)]
            for player, contribution in zip(players, contribs):
                r, b = parse_contribution(contribution)
                contribution_totals[base_name(player)][0] += r
                contribution_totals[base_name(player)][1] += b

        for entity in sorted(
            batting_entities,
            key=lambda e: int(choose(vals(inn, e, "batting.order")) or 0),
        ):
            rec = {"batter": entity}
            for attr in ["dismissal", "runs", "balls", "fours", "sixes", "strike_rate"]:
                rec[attr] = choose(vals(inn, entity, f"batting.{attr}"))
                if rec[attr] is None and entity != base_name(entity):
                    rec[attr] = choose(vals(inn, base_name(entity), f"batting.{attr}"))
            derived = contribution_totals.get(base_name(entity))
            if derived is not None:
                druns, dballs = map(str, derived)
                run_candidates = vals(inn, entity, "batting.runs") + vals(
                    inn, base_name(entity), "batting.runs"
                )
                if len(set(run_candidates)) > 1 or rec["runs"] is None:
                    rec["runs"] = druns
                if rec["balls"] is None:
                    rec["balls"] = dballs
            if rec["runs"] is not None and rec["balls"] is not None:
                rec["strike_rate"] = fmt_rate(int(rec["runs"]), int(rec["balls"]), 100)
            state["batting"][inn].append(rec)

        dismissal_wickets = Counter()
        for rec in state["batting"][inn]:
            dismissal = rec.get("dismissal") or ""
            m = re.search(r"(?:^b |^lbw | b )(.+)$", dismissal)
            if m:
                dismissal_wickets[base_name(m.group(1))] += 1

        bowling_entities = {
            entity for (i, entity, attr) in candidates
            if i == inn and attr == "bowling.order"
        }
        for entity in sorted(
            bowling_entities,
            key=lambda e: int(choose(vals(inn, e, "bowling.order")) or 0),
        ):
            rec = {"bowler": entity}
            for attr in ["overs", "maidens", "runs", "wickets", "economy", "wides", "no_balls"]:
                rec[attr] = choose(vals(inn, entity, f"bowling.{attr}"))
            derived_wickets = str(dismissal_wickets[base_name(entity)])
            wicket_candidates = vals(inn, entity, "bowling.wickets")
            if len(set(wicket_candidates)) > 1 or rec["wickets"] is None:
                rec["wickets"] = derived_wickets
            if rec["overs"] is not None and rec["runs"] is not None:
                rec["economy"] = fmt_rate(
                    int(rec["runs"]), balls_from_overs(rec["overs"]), 6
                )
            state["bowling"][inn].append(rec)

        summary = state["innings"][inn]
        if all(summary.get(x) is not None for x in ["byes", "leg_byes", "no_balls", "wides"]):
            derived_extras = str(sum(int(summary[x]) for x in ["byes", "leg_byes", "no_balls", "wides"]))
            if len(set(vals(inn, "Innings", "extras"))) > 1 or summary["extras"] is None:
                summary["extras"] = derived_extras
        if summary.get("total") and summary.get("overs"):
            total_runs = int(summary["total"].split("/", 1)[0])
            summary["run_rate"] = fmt_rate(total_runs, balls_from_overs(summary["overs"]), 6)
        if state["partnerships"][inn]:
            summary["max_partnership"] = str(max(int(p["runs"]) for p in state["partnerships"][inn]))
    return state


def tables_from_state(state):
    tables = [{
        "table_type": "Match Summary",
        "innings": None,
        "columns": ["Field", "Value"],
        "rows": [
            {"Field": "Venue", "Value": state["match"]["venue"]},
            {"Field": "Toss", "Value": state["match"]["toss"]},
            {"Field": "Result", "Value": state["match"]["result"]},
            {"Field": "Player of the Match", "Value": state["match"]["player_of_match"]},
        ],
    }]
    for inn in ("I1", "I2"):
        s = state["innings"][inn]
        tables.append({
            "table_type": "Innings Summary",
            "innings": inn,
            "columns": ["Metric", "Value"],
            "rows": [
                {"Metric": "Team", "Value": s["team"]},
                {"Metric": "Total", "Value": s["total"]},
                {"Metric": "Overs", "Value": s["overs"]},
                {"Metric": "Extras", "Value": s["extras"]},
                {"Metric": "Byes", "Value": s["byes"]},
                {"Metric": "Leg Byes", "Value": s["leg_byes"]},
                {"Metric": "No Balls", "Value": s["no_balls"]},
                {"Metric": "Wides", "Value": s["wides"]},
                {"Metric": "Run Rate", "Value": s["run_rate"]},
                {"Metric": "Max Partnership", "Value": s["max_partnership"]},
            ],
        })
        tables.append({
            "table_type": "Batting",
            "innings": inn,
            "columns": ["Batter", "Dismissal", "Runs", "Balls", "4s", "6s", "Strike Rate"],
            "rows": [
                {
                    "Batter": r["batter"], "Dismissal": r["dismissal"],
                    "Runs": r["runs"], "Balls": r["balls"], "4s": r["fours"],
                    "6s": r["sixes"], "Strike Rate": r["strike_rate"],
                }
                for r in state["batting"][inn]
            ],
        })
        tables.append({
            "table_type": "Bowling",
            "innings": inn,
            "columns": ["Bowler", "Overs", "Maidens", "Runs", "Wickets", "Economy", "Wides", "No Balls"],
            "rows": [
                {
                    "Bowler": r["bowler"], "Overs": r["overs"], "Maidens": r["maidens"],
                    "Runs": r["runs"], "Wickets": r["wickets"], "Economy": r["economy"],
                    "Wides": r["wides"], "No Balls": r["no_balls"],
                }
                for r in state["bowling"][inn]
            ],
        })
        tables.append({
            "table_type": "Partnerships",
            "innings": inn,
            "columns": ["Wicket", "Pair", "Runs", "Extras", "Contributions", "Span", "End"],
            "rows": [
                {
                    "Wicket": r["wicket"], "Pair": r["pair"], "Runs": r["runs"],
                    "Extras": r["extras"], "Contributions": r["contributions"],
                    "Span": r["span"], "End": r["end"],
                }
                for r in state["partnerships"][inn]
            ],
        })
        tables.append({
            "table_type": "Fall of Wickets",
            "innings": inn,
            "columns": ["Wicket", "Batter", "Score", "Over"],
            "rows": [
                {
                    "Wicket": r["wicket"], "Batter": r["batter"],
                    "Score": r["score"], "Over": r["over"],
                }
                for r in state["falls"][inn]
            ],
        })
    return tables


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    raw_path = OUTDIR / f"{METHOD}.raw.jsonl"
    pred_path = OUTDIR / f"{METHOD}.predictions.jsonl"
    run_path = OUTDIR / f"{METHOD}.run.json"
    input_bytes = INPUT.read_bytes()
    instances = [json.loads(line) for line in input_bytes.splitlines() if line.strip()]
    raw_records = []
    predictions = []
    for instance in instances:
        tuples = extract_tuples(instance)
        integrated = build_integrated_state(tuples)
        tables = tables_from_state(integrated)
        raw_records.append({
            "instance_id": instance["instance_id"],
            "method": METHOD,
            "stage_1_paper_tuples": tuples,
            "stage_2_integrated_state": integrated,
            "stage_3_semantic_tables": tables,
        })
        predictions.append({
            "instance_id": instance["instance_id"],
            "method": METHOD,
            "tables": tables,
        })
    raw_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in raw_records)
    )
    pred_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in predictions)
    )
    run_record = {
        "method": METHOD,
        "model_role": "isolated_same_model_agent",
        "run_date": date.today().isoformat(),
        "input_path": str(INPUT),
        "input_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "instance_count": len(instances),
        "raw_record_count": len(raw_records),
        "prediction_count": len(predictions),
        "completed_instance_ids": [r["instance_id"] for r in predictions],
        "stage_counts": {
            "text_to_tuple": len(raw_records),
            "tuple_integration": len(raw_records),
            "tuple_to_table": len(raw_records),
        },
        "limitations": [
            "Paper-style tuples retain only entity, team_or_innings, event_or_attribute, and value; no source or version provenance is retained.",
            "The blocked generated-code T3 integration path was not used; this run is the direct-integration variant.",
            "Conflict resolution is limited to cricket consistency constraints available in the extracted tuples.",
            "No gold, annotations, validation data, generation code, canonical roots, or other method outputs were inspected.",
        ],
    }
    run_path.write_text(json.dumps(run_record, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
