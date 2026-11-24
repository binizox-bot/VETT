#!/usr/bin/env python3
"""Summarize the rule-screened R6 roots after ledger synthesis and validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen-dir", type=Path, required=True)
    parser.add_argument("--source-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.source_audit.read_text(encoding="utf-8"))
    statuses = []
    for line in (args.screen_dir / "status.tsv").read_text(encoding="utf-8").splitlines():
        root_id, exit_code = line.split()
        validation_path = args.screen_dir / f"{root_id}.validation.json"
        if validation_path.exists():
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
            status = "PASS" if validation["status"] == "PASS" else "LEDGER_VALIDATION_FAIL"
            failures = [failure for detail in validation["details"] for failure in detail["failures"]]
            statuses.append({
                "root_id": root_id,
                "synthesis_exit_code": int(exit_code),
                "status": status,
                "round_trip_checks": validation["checks"],
                "round_trip_failures": validation["failure_count"],
                "failures": failures,
            })
        else:
            stderr_path = args.screen_dir / f"{root_id}.stderr.txt"
            tail = stderr_path.read_text(encoding="utf-8").strip().splitlines()[-1]
            statuses.append({
                "root_id": root_id,
                "synthesis_exit_code": int(exit_code),
                "status": "NO_FEASIBLE_LEDGER",
                "reason": tail,
            })

    passed = [row["root_id"] for row in statuses if row["status"] == "PASS"]
    report = {
        "screen_version": "R6.0-maiden-aware",
        "canonical_roots": source["canonical_roots"],
        "source_auto_pass_roots": source["source_auto_pass_roots"],
        "rule_screen_candidates": source["strict_event_reversible_roots"],
        "solver_screened_roots": len(statuses),
        "full_round_trip_pass_roots": len(passed),
        "full_round_trip_pass_ids": passed,
        "selected_root": "match_0031",
        "selection_note": "match_0031 is the first full-pass strict candidate; match_0032 shares the same match metadata and is retained only as a near-duplicate backup.",
        "rejected_engineering_probe": {
            "root_id": "match_0096",
            "reason": "Upstream cells are marked BLOCKED_BY_CONFLICT; it is not admitted as a paper gold instance.",
        },
        "roots": statuses,
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rule_screen_candidates": report["rule_screen_candidates"],
        "full_round_trip_pass_roots": report["full_round_trip_pass_roots"],
        "full_round_trip_pass_ids": report["full_round_trip_pass_ids"],
        "selected_root": report["selected_root"],
    }, indent=2))


if __name__ == "__main__":
    main()
