#!/usr/bin/env python3
"""Audit whether canonical scorecards can be reversed into legal delivery ledgers."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


def canon(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("(c)(wk)", "").replace("(wk)", "").replace("(c)", "")).strip()


def bowler_of(dismissal: str) -> str | None:
    lower = dismissal.lower().strip()
    if not lower or lower == "not out" or lower.startswith("run out"):
        return None
    if " b " in dismissal:
        return dismissal.rsplit(" b ", 1)[1].strip()
    if lower.startswith("b "):
        return dismissal[2:].strip()
    if lower.startswith("lbw "):
        return dismissal[4:].strip()
    raise ValueError(dismissal)


def ball_index(value: str) -> int:
    over, ball = value.split(".")
    return int(over) * 6 + int(ball)


def table_of(root: dict[str, Any], iid: str, table_type: str) -> dict[str, Any]:
    return next(t for t in root["tables"] if t.get("innings_id") == iid and t["table_type"] == table_type)


def audit_root(root: dict[str, Any], source_action: str) -> dict[str, Any]:
    reasons: set[str] = set()
    if source_action != "AUTO_PASS_NEEDS_SUPPORT_AUDIT":
        reasons.add("source_not_auto_pass")
    if len(root["innings"]) != 2:
        reasons.add("not_two_innings")
    innings_details = []
    for innings in root["innings"]:
        iid = innings["innings_id"]
        local: set[str] = set()
        bowling = table_of(root, iid, "Bowling")
        if len([r["Bowler"] for r in bowling["rows"]]) != len({r["Bowler"] for r in bowling["rows"]}):
            local.add("duplicate_bowling_row_key")
        bowler_balls = []
        for row in bowling["rows"]:
            value = str(row["O"])
            if "." in value:
                overs, balls = value.split(".", 1)
                bowler_balls.append(int(overs) * 6 + int(balls))
            else:
                bowler_balls.append(int(value) * 6)
        if sum(bowler_balls) != innings["legal_balls"]:
            local.add("bowler_ball_total")
        expected_partials = 1 if innings["legal_balls"] % 6 else 0
        observed_partials = sum(balls % 6 != 0 for balls in bowler_balls)
        if observed_partials != expected_partials:
            local.add("partial_spell_count_mismatch")
        spell_overs = {r["Bowler"]: math.ceil(balls / 6) for r, balls in zip(bowling["rows"], bowler_balls)}
        batting = table_of(root, iid, "Batting")
        batting_names = [canon(r["Batter"]) for r in batting["rows"]]
        if len(batting_names) != len(set(batting_names)):
            local.add("duplicate_batting_row_key")
        batting_by_name = {canon(r["Batter"]): r for r in batting["rows"]}
        fixed: dict[int, str] = {}
        for row in table_of(root, iid, "Fall of Wickets")["rows"]:
            match = re.search(r"\((\d+)\.(\d+)\)", row["At"])
            if not match:
                local.add("bad_fow_notation")
                continue
            batter = batting_by_name.get(canon(row["Batter"]))
            if not batter:
                local.add("fow_batter_mapping")
                continue
            try:
                bowler = bowler_of(batter["Dismissal"])
            except ValueError:
                local.add("dismissal_owner_parse")
                continue
            if bowler:
                over = int(match.group(1))
                if over in fixed and fixed[over] != bowler:
                    local.add("two_bowlers_own_wickets_in_one_over")
                fixed[over] = bowler
        for over in range(max(0, innings["legal_balls"] // 6 - 1)):
            if fixed.get(over) is not None and fixed.get(over) == fixed.get(over + 1):
                local.add("same_bowler_required_in_consecutive_overs")
        for bowler, count in spell_overs.items():
            if sum(owner == bowler for owner in fixed.values()) > count:
                local.add("wicket_overs_exceed_spell")

        partnerships = table_of(root, iid, "Partnerships")
        if not partnerships["rows"]:
            local.add("no_partnership_rows")
        covered: list[int] = []
        for row in partnerships["rows"]:
            m1 = re.fullmatch(r"(-?\d+)\((\d+)\)", str(row["Striker"]))
            m2 = re.fullmatch(r"(-?\d+)\((\d+)\)", str(row["Non-striker"]))
            if not m1 or not m2:
                local.add("partnership_component_parse")
                continue
            if int(m1.group(1)) + int(m2.group(1)) + int(row["Extras"]) != int(row["Runs"]):
                local.add("partnership_run_components")
            try:
                start, end = row["Overs"].split("-")
                start_i, end_i = ball_index(start), ball_index(end)
            except Exception:
                local.add("partnership_over_parse")
                continue
            if end_i - start_i + 1 != int(m1.group(2)) + int(m2.group(2)):
                local.add("partnership_ball_components")
            covered.extend(range(start_i, end_i + 1))
        if covered != list(range(1, innings["legal_balls"] + 1)):
            local.add("partnership_ball_coverage")
        reasons.update(local)
        innings_details.append({"innings_id": iid, "reasons": sorted(local)})
    return {
        "root_id": root["root_id"],
        "strict_event_reversible": not reasons,
        "reasons": sorted(reasons),
        "innings": innings_details,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--audit-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    actions = {row["match_id"]: row["recommended_action"] for row in csv.DictReader(args.audit_csv.open(encoding="utf-8"))}
    roots = [json.loads(line) for line in args.canonical.read_text(encoding="utf-8").splitlines() if line.strip()]
    details = [audit_root(root, actions.get(root["root_id"], "MISSING")) for root in roots]
    reason_counts = Counter(reason for row in details for reason in row["reasons"])
    strict = [row["root_id"] for row in details if row["strict_event_reversible"]]
    auto_pass = [row for row in details if "source_not_auto_pass" not in row["reasons"]]
    report = {
        "audit_version": "R6-event-feasibility-0.1",
        "canonical_roots": len(roots),
        "source_auto_pass_roots": len(auto_pass),
        "strict_event_reversible_roots": len(strict),
        "strict_root_ids": strict,
        "reason_counts": dict(reason_counts.most_common()),
        "decision": "DO_NOT_REVERSE_SYNTHESIZE_DELIVERIES_FROM_CURRENT_SCORECARDS" if not strict else "REVIEW_STRICT_ROOTS",
        "recommended_route": "Forward-generate a disclosed delivery ledger, derive the scorecard from it, and use the 220 roots only for names, match styles and distributional calibration.",
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("canonical_roots", "source_auto_pass_roots", "strict_event_reversible_roots", "decision")}, indent=2))


if __name__ == "__main__":
    main()
