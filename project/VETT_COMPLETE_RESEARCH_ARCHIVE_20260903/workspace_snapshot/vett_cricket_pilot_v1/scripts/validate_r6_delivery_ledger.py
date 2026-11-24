#!/usr/bin/env python3
"""Aggregate an R6 delivery ledger and compare it with the canonical scorecard."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


def canon(value: str) -> str:
    return value.replace("(c)(wk)", "").replace("(wk)", "").replace("(c)", "").strip()


def table_of(root: dict[str, Any], iid: str, table_type: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t.get("innings_id") == iid and t["table_type"] == table_type)


def overs(balls: int) -> str:
    if balls % 6:
        return f"{balls // 6}.{balls % 6}"
    return str(balls // 6)


def rate(numerator: int, denominator_balls: int) -> str:
    if denominator_balls == 0:
        return "-"
    value = Decimal(numerator * 100) / Decimal(denominator_balls)
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")


def econ(runs: int, balls: int) -> str:
    if balls == 0:
        return "-"
    value = Decimal(runs * 6) / Decimal(balls)
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")


def validate_innings(root: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    iid = ledger["innings_id"]
    events = ledger["events"]
    failures = []
    checks = 0

    def check(name: str, observed: Any, expected: Any) -> None:
        nonlocal checks
        checks += 1
        if str(observed) != str(expected):
            failures.append({"check": name, "observed": observed, "expected": expected})

    legal = [e for e in events if e["is_legal"]]
    total = sum(e["batter_runs"] + e["extras_runs"] for e in events)
    wickets = [e for e in legal if e["dismissal"]]
    summary = {row["Field"]: row["Value"] for row in table_of(root, iid, "Innings Summary")["rows"]}
    check("legal_balls", len(legal), next(x["legal_balls"] for x in root["innings"] if x["innings_id"] == iid))
    check("team_runs", total, next(x["runs"] for x in root["innings"] if x["innings_id"] == iid))
    check("team_wickets", len(wickets), next(x["wickets"] for x in root["innings"] if x["innings_id"] == iid))
    extras = Counter()
    for event in events:
        if event["extras_type"]:
            extras[event["extras_type"]] += event["extras_runs"]
    for category, field in (("bye", "Byes"), ("leg_bye", "Leg Byes"), ("no_ball", "No Balls"), ("wide", "Wides")):
        check(f"extras.{category}", extras[category], summary[field])
    check("extras.total", sum(extras.values()), summary["Total Extras"])
    check("run_rate", econ(total, len(legal)), summary["Run Rate"])

    # Batting aggregation.
    batting = table_of(root, iid, "Batting")
    batter_stats: dict[str, Counter] = defaultdict(Counter)
    dismissal_by_batter = {}
    participants = set()
    for event in events:
        striker = canon(event["striker"])
        participants.add(striker)
        participants.add(canon(event["non_striker"]))
        if event["is_legal"]:
            batter_stats[striker]["B"] += 1
        batter_stats[striker]["R"] += event["batter_runs"]
        batter_stats[striker]["4s"] += int(event["boundary_four"])
        batter_stats[striker]["6s"] += int(event["boundary_six"])
        if event["dismissal"]:
            dismissal_by_batter[canon(event["dismissal"]["batter"])] = event["dismissal"]["description"]
    for row in batting["rows"]:
        name = canon(row["Batter"])
        stats = batter_stats[name]
        for field in ("R", "B", "4s", "6s"):
            check(f"batting.{name}.{field}", stats[field], row[field])
        check(f"batting.{name}.SR", rate(stats["R"], stats["B"]), row["SR"])
        expected_dismissal = row["Dismissal"]
        if expected_dismissal:
            observed_dismissal = dismissal_by_batter.get(name, "not out" if name in participants else "")
            check(f"batting.{name}.Dismissal", observed_dismissal, expected_dismissal)

    # Bowling aggregation and maidens.
    bowling = table_of(root, iid, "Bowling")
    bowler_stats: dict[str, Counter] = defaultdict(Counter)
    over_runs: dict[tuple[str, int], int] = defaultdict(int)
    for event in events:
        bowler = event["bowler"]
        over = int(event["delivery_label"].split(".")[0])
        if event["is_legal"]:
            bowler_stats[bowler]["balls"] += 1
        conceded = event["batter_runs"]
        if event["extras_type"] in ("wide", "no_ball"):
            conceded += event["extras_runs"]
        bowler_stats[bowler]["R"] += conceded
        over_runs[(bowler, over)] += conceded
        if event["extras_type"] == "wide":
            bowler_stats[bowler]["Wd"] += event["extras_runs"]
        if event["extras_type"] == "no_ball":
            bowler_stats[bowler]["Nb"] += event["extras_runs"]
        if event["dismissal"] and event["dismissal"]["credited_bowler"]:
            bowler_stats[event["dismissal"]["credited_bowler"]]["W"] += 1
    for row in bowling["rows"]:
        name = row["Bowler"]
        stats = bowler_stats[name]
        maidens = sum(runs == 0 for (bowler, _), runs in over_runs.items() if bowler == name)
        observed = {
            "O": overs(stats["balls"]), "M": maidens, "R": stats["R"], "W": stats["W"],
            "Econ": econ(stats["R"], stats["balls"]), "Wd": stats["Wd"], "Nb": stats["Nb"],
        }
        for field, value in observed.items():
            check(f"bowling.{name}.{field}", value, row[field])

    # Partnership aggregation.
    source_partnerships = table_of(root, iid, "Partnerships")
    events_by_pid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_pid[event["partnership_id"]].append(event)
    partnership_runs = []
    for pos, row in enumerate(source_partnerships["rows"], start=1):
        pid = f"{iid}.P{pos:02d}"
        pevents = events_by_pid[pid]
        runs = sum(e["batter_runs"] + e["extras_runs"] for e in pevents)
        extra_runs = sum(e["extras_runs"] for e in pevents)
        partnership_runs.append(runs)
        check(f"partnership.{pid}.Runs", runs, row["Runs"])
        check(f"partnership.{pid}.Extras", extra_runs, row["Extras"])
        legal_p = [e for e in pevents if e["is_legal"]]
        start, end = row["Overs"].split("-")
        check(f"partnership.{pid}.start", legal_p[0]["delivery_label"], start)
        check(f"partnership.{pid}.end", legal_p[-1]["delivery_label"], end)
        first, second = [canon(x) for x in row["Partnership"].split(" & ", 1)]
        for player, field in ((first, "Striker"), (second, "Non-striker")):
            runs_p = sum(e["batter_runs"] for e in legal_p if canon(e["striker"]) == player)
            balls_p = sum(1 for e in legal_p if canon(e["striker"]) == player)
            check(f"partnership.{pid}.{field}", f"{runs_p}({balls_p})", row[field])
    check("max_partnership", max(partnership_runs), summary["Max Partnership"])

    # Fall of wickets.
    fow = table_of(root, iid, "Fall of Wickets")
    for row, event in zip(fow["rows"], wickets):
        check(f"fow.{row['Wkt']}.Batter", canon(event["dismissal"]["batter"]), canon(row["Batter"]))
        observed_at = f"{event['team_score_after']}/{event['wickets_after']}({event['delivery_label']})"
        check(f"fow.{row['Wkt']}.At", observed_at, row["At"])

    return {"innings_id": iid, "checks": checks, "failures": failures}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    root = next(
        json.loads(line) for line in args.canonical.read_text(encoding="utf-8").splitlines()
        if line.strip() and json.loads(line)["root_id"] == ledger["root_id"]
    )
    details = [validate_innings(root, innings) for innings in ledger["innings"]]
    failures = [failure for row in details for failure in row["failures"]]
    report = {
        "root_id": ledger["root_id"],
        "status": "PASS" if not failures else "FAIL",
        "checks": sum(row["checks"] for row in details),
        "failure_count": len(failures),
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("root_id", "status", "checks", "failure_count")}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
