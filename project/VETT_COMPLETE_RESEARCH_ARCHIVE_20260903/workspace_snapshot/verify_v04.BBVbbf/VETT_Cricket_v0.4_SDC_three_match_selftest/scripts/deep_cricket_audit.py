#!/usr/bin/env python3
"""Run cricket-domain invariants over canonical roots.

The audit is intentionally stricter than the construction validator. It checks
independent scorecard identities and reports failures without rewriting gold.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def legal_balls(overs: Any) -> int:
    text = str(overs)
    if "." not in text:
        return int(text) * 6
    whole, remainder = text.split(".", 1)
    return int(whole) * 6 + int(remainder)


def contribution(value: Any) -> tuple[int, int] | None:
    match = re.fullmatch(r"(\d+)\((\d+)\)", str(value).strip())
    return (int(match.group(1)), int(match.group(2))) if match else None


def total_parts(value: Any) -> tuple[int, int, str] | None:
    match = re.fullmatch(r"(\d+)/(\d+)\s*\((\d+(?:\.\d+)?)\s+Overs\)", str(value).strip(), re.I)
    return (int(match.group(1)), int(match.group(2)), match.group(3)) if match else None


def fow_parts(value: Any) -> tuple[int, int, str] | None:
    match = re.fullmatch(r"(\d+)/(\d+)\((\d+(?:\.\d+)?)\)", str(value).strip())
    return (int(match.group(1)), int(match.group(2)), match.group(3)) if match else None


def end_over(value: Any) -> str:
    text = str(value).strip()
    return text.rsplit("-", 1)[-1] if "-" in text else text


def credited_dismissal(dismissal: Any) -> bool:
    text = str(dismissal).strip().casefold()
    if not text or text in {"not out", "did not bat", "absent hurt", "retired hurt"}:
        return False
    non_bowler = ("run out", "retired out", "obstructing the field", "timed out")
    return not any(label in text for label in non_bowler)


def rounded_rate(numerator: int, denominator: int) -> str:
    value = Decimal(numerator) / Decimal(denominator)
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f")


def normalized_player(value: Any) -> str:
    text = str(value).strip().casefold()
    text = re.sub(r"\s*\((?:c|wk|c/wk|wk/c)\)\s*", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def table_map(root: dict[str, Any]) -> dict[tuple[str | None, str], dict[str, Any]]:
    return {(table.get("innings_id"), table["table_type"]): table for table in root["tables"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    roots = load_jsonl(args.roots)
    failures: list[dict[str, Any]] = []
    checks = Counter()
    passes = Counter()
    root_failures: dict[str, set[str]] = defaultdict(set)

    def check(code: str, condition: bool, root_id: str, innings_id: str, detail: str, severity: str) -> None:
        checks[(code, severity)] += 1
        if condition:
            passes[(code, severity)] += 1
        else:
            failures.append(
                {
                    "code": code,
                    "severity": severity,
                    "root_id": root_id,
                    "innings_id": innings_id,
                    "detail": detail,
                }
            )
            root_failures[root_id].add(code)

    for root in roots:
        if root["curation_status"] != "READY_FOR_GENERATED_VIEWS":
            continue
        root_id = root["root_id"]
        tables = table_map(root)
        for innings in root["innings"]:
            iid = innings["innings_id"]
            summary_table = tables[(iid, "Innings Summary")]
            summary = {row["Field"]: row["Value"] for row in summary_table["rows"]}
            batting = tables[(iid, "Batting")]["rows"]
            bowling = tables[(iid, "Bowling")]["rows"]
            partnerships = tables[(iid, "Partnerships")]["rows"]
            fow = tables[(iid, "Fall of Wickets")]["rows"]

            batting_names = [normalized_player(row.get("Batter", "")) for row in batting]
            bowling_names = [normalized_player(row.get("Bowler", "")) for row in bowling]
            check(
                "BATTING_NAME_UNIQUE",
                len(batting_names) == len(set(batting_names)),
                root_id,
                iid,
                f"duplicate_names={[name for name, count in Counter(batting_names).items() if count > 1]}",
                "blocking",
            )
            check(
                "BOWLING_NAME_UNIQUE",
                len(bowling_names) == len(set(bowling_names)),
                root_id,
                iid,
                f"duplicate_names={[name for name, count in Counter(bowling_names).items() if count > 1]}",
                "blocking",
            )

            parsed_total = total_parts(summary.get("Total"))
            check("TOTAL_PARSE", parsed_total is not None, root_id, iid, str(summary.get("Total")), "blocking")
            if parsed_total:
                total_runs, total_wickets, total_overs = parsed_total
                check(
                    "TOTAL_MATCHES_CANONICAL",
                    (total_runs, total_wickets, legal_balls(total_overs))
                    == (innings["runs"], innings["wickets"], innings["legal_balls"]),
                    root_id,
                    iid,
                    f"summary={parsed_total}, canonical={innings}",
                    "blocking",
                )
            else:
                total_runs, total_wickets, total_overs = innings["runs"], innings["wickets"], innings["overs"]

            components = [
                int(summary.get(field, 0) or 0)
                for field in ("Byes", "Leg Byes", "No Balls", "Wides", "Penalty")
            ]
            extras = int(summary.get("Total Extras", 0) or 0)
            check(
                "EXTRAS_COMPONENT_SUM",
                sum(components) == extras,
                root_id,
                iid,
                f"components={components}, total_extras={extras}",
                "blocking",
            )
            batting_runs = sum(int(row.get("R", 0) or 0) for row in batting)
            check(
                "BATTING_PLUS_EXTRAS",
                batting_runs + extras == total_runs,
                root_id,
                iid,
                f"batting={batting_runs}, extras={extras}, total={total_runs}",
                "blocking",
            )

            partnership_runs = [int(row.get("Runs", 0) or 0) for row in partnerships]
            check(
                "PARTNERSHIP_SUM",
                sum(partnership_runs) == total_runs,
                root_id,
                iid,
                f"partnerships={sum(partnership_runs)}, total={total_runs}",
                "blocking",
            )
            check(
                "MAX_PARTNERSHIP",
                max(partnership_runs, default=0) == int(summary.get("Max Partnership", 0) or 0),
                root_id,
                iid,
                f"max={max(partnership_runs, default=0)}, summary={summary.get('Max Partnership')}",
                "blocking",
            )

            for index, row in enumerate(partnerships, 1):
                striker = contribution(row.get("Striker"))
                non_striker = contribution(row.get("Non-striker"))
                if striker and non_striker:
                    expected = striker[0] + non_striker[0] + int(row.get("Extras", 0) or 0)
                    check(
                        "PARTNERSHIP_CONTRIBUTION_SUM",
                        expected == int(row.get("Runs", 0) or 0),
                        root_id,
                        iid,
                        f"row={index}, expected={expected}, runs={row.get('Runs')}",
                        "blocking",
                    )

            bowling_balls = sum(legal_balls(row.get("O", 0)) for row in bowling)
            check(
                "BOWLING_LEGAL_BALLS",
                bowling_balls == innings["legal_balls"],
                root_id,
                iid,
                f"bowling={bowling_balls}, innings={innings['legal_balls']}",
                "blocking",
            )
            bowler_runs = sum(int(row.get("R", 0) or 0) for row in bowling)
            non_bowler_extras = int(summary.get("Byes", 0) or 0) + int(summary.get("Leg Byes", 0) or 0)
            non_bowler_extras += int(summary.get("Penalty", 0) or 0)
            check(
                "BOWLING_RUN_RECONCILIATION",
                bowler_runs + non_bowler_extras == total_runs,
                root_id,
                iid,
                f"bowler_runs={bowler_runs}, non_bowler_extras={non_bowler_extras}, total={total_runs}",
                "blocking",
            )
            check(
                "BOWLER_WIDES_SUM",
                sum(int(row.get("Wd", 0) or 0) for row in bowling) == int(summary.get("Wides", 0) or 0),
                root_id,
                iid,
                "bowling wides versus innings wides",
                "blocking",
            )
            check(
                "BOWLER_NOBALLS_SUM",
                sum(int(row.get("Nb", 0) or 0) for row in bowling)
                == int(summary.get("No Balls", 0) or 0),
                root_id,
                iid,
                "bowling no-balls versus innings no-balls",
                "blocking",
            )
            credited = sum(credited_dismissal(row.get("Dismissal")) for row in batting)
            bowling_wickets = sum(int(row.get("W", 0) or 0) for row in bowling)
            check(
                "BOWLING_WICKET_CREDITS",
                bowling_wickets == credited,
                root_id,
                iid,
                f"bowling={bowling_wickets}, credited_dismissals={credited}",
                "blocking",
            )

            for row_index, row in enumerate(batting, 1):
                balls = int(row.get("B", 0) or 0)
                runs = int(row.get("R", 0) or 0)
                expected_sr = "-" if balls == 0 else rounded_rate(100 * runs, balls)
                check(
                    "STRIKE_RATE",
                    str(row.get("SR")) == expected_sr,
                    root_id,
                    iid,
                    f"row={row_index}, expected={expected_sr}, actual={row.get('SR')}",
                    "warning",
                )
            for row_index, row in enumerate(bowling, 1):
                balls = legal_balls(row.get("O", 0))
                expected_econ = rounded_rate(6 * int(row.get("R", 0) or 0), balls) if balls else "-"
                check(
                    "ECONOMY_RATE",
                    str(row.get("Econ")) == expected_econ,
                    root_id,
                    iid,
                    f"row={row_index}, expected={expected_econ}, actual={row.get('Econ')}",
                    "warning",
                )
            expected_rr = rounded_rate(6 * total_runs, innings["legal_balls"])
            check(
                "RUN_RATE",
                str(summary.get("Run Rate")) == expected_rr,
                root_id,
                iid,
                f"expected={expected_rr}, actual={summary.get('Run Rate')}",
                "warning",
            )

            parsed_fow = [fow_parts(row.get("At")) for row in fow]
            check(
                "FOW_PARSE",
                all(item is not None for item in parsed_fow),
                root_id,
                iid,
                f"rows={len(fow)}",
                "blocking",
            )
            if all(item is not None for item in parsed_fow):
                valid_fow = [item for item in parsed_fow if item is not None]
                scores = [item[0] for item in valid_fow]
                wickets = [item[1] for item in valid_fow]
                check(
                    "FOW_SEQUENCE",
                    wickets == list(range(1, len(wickets) + 1)),
                    root_id,
                    iid,
                    str(wickets),
                    "blocking",
                )
                check(
                    "FOW_MONOTONIC",
                    scores == sorted(scores) and all(score <= total_runs for score in scores),
                    root_id,
                    iid,
                    str(scores),
                    "blocking",
                )
                check(
                    "FOW_COUNT",
                    len(valid_fow) == total_wickets,
                    root_id,
                    iid,
                    f"fow={len(valid_fow)}, wickets={total_wickets}",
                    "blocking",
                )
                cumulative = 0
                for index, item in enumerate(valid_fow):
                    cumulative += partnership_runs[index]
                    check(
                        "FOW_PARTNERSHIP_CUMULATIVE",
                        cumulative == item[0],
                        root_id,
                        iid,
                        f"wicket={index + 1}, cumulative={cumulative}, fow={item[0]}",
                        "blocking",
                    )
                    check(
                        "FOW_OVER_MATCHES_PARTNERSHIP",
                        legal_balls(end_over(partnerships[index].get("Overs")))
                        == legal_balls(item[2]),
                        root_id,
                        iid,
                        f"wicket={index + 1}, partnership={partnerships[index].get('Overs')}, fow={item[2]}",
                        "blocking",
                    )
            last_end = str(partnerships[-1].get("End", "")).strip().casefold() if partnerships else ""
            unbroken_final_stand = not last_end or last_end == "not out"
            expected_partnership_rows = total_wickets + int(unbroken_final_stand)
            check(
                "PARTNERSHIP_ROW_COUNT",
                len(partnerships) == expected_partnership_rows,
                root_id,
                iid,
                f"rows={len(partnerships)}, expected={expected_partnership_rows}",
                "blocking",
            )

    blocking_failures = [item for item in failures if item["severity"] == "blocking"]
    warning_failures = [item for item in failures if item["severity"] == "warning"]
    report = {
        "audit_version": "0.1",
        "roots_total": len(roots),
        "ready_roots_audited": sum(root["curation_status"] == "READY_FOR_GENERATED_VIEWS" for root in roots),
        "checks_total": sum(checks.values()),
        "checks_passed": sum(passes.values()),
        "failures_total": len(failures),
        "blocking_failures": len(blocking_failures),
        "warning_failures": len(warning_failures),
        "roots_with_blocking_failures": sorted(
            {
                item["root_id"]
                for item in blocking_failures
            }
        ),
        "by_check": {
            f"{code}:{severity}": {
                "total": checks[(code, severity)],
                "passed": passes[(code, severity)],
                "failed": checks[(code, severity)] - passes[(code, severity)],
            }
            for code, severity in sorted(checks)
        },
        "failures": failures,
        "status": "PASS" if not blocking_failures else "FAIL",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in report if key not in {"by_check", "failures"}}, indent=2))


if __name__ == "__main__":
    main()
