#!/usr/bin/env python3
"""Audit isolated probe prediction files before any gold-bearing scoring step."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind-inputs", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, required=True)
    parser.add_argument("--methods", nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    expected = {item["instance_id"] for item in load_jsonl(args.blind_inputs)}
    checks = []
    failures = []
    for method in args.methods:
        path = args.runs_dir / f"{method}.predictions.jsonl"
        if not path.exists():
            failures.append({"method": method, "code": "MISSING_FILE"})
            continue
        try:
            predictions = load_jsonl(path)
        except (json.JSONDecodeError, TypeError) as exc:
            failures.append({"method": method, "code": "INVALID_JSONL", "detail": str(exc)})
            continue
        observed = [item.get("instance_id") for item in predictions]
        method_failures = []
        if len(observed) != len(expected):
            method_failures.append(f"count={len(observed)}, expected={len(expected)}")
        if len(observed) != len(set(observed)):
            method_failures.append("duplicate_instance_id")
        if set(observed) != expected:
            method_failures.append(
                f"missing={sorted(expected - set(observed))}, extra={sorted(set(observed) - expected)}"
            )
        if any(item.get("method") != method for item in predictions):
            method_failures.append("method_label_mismatch")
        serialized = json.dumps(predictions, ensure_ascii=False, sort_keys=True)
        forbidden = [
            token
            for token in ("table_id", "row_id", "gold", "cell_provenance", "scored_cell_ids")
            if f'"{token}"' in serialized
        ]
        if forbidden:
            method_failures.append(f"forbidden_fields={forbidden}")
        malformed_tables = 0
        for item in predictions:
            tables = item.get("tables")
            if not isinstance(tables, list):
                malformed_tables += 1
                continue
            for table in tables:
                if (
                    not isinstance(table, dict)
                    or not isinstance(table.get("table_type"), str)
                    or table.get("innings") not in {None, "I1", "I2"}
                    or not isinstance(table.get("columns"), list)
                    or not isinstance(table.get("rows"), list)
                    or not all(isinstance(row, dict) for row in table.get("rows", []))
                ):
                    malformed_tables += 1
        if malformed_tables:
            method_failures.append(f"malformed_tables={malformed_tables}")
        check = {
            "method": method,
            "prediction_count": len(predictions),
            "instance_ids_exact": set(observed) == expected and len(observed) == len(expected),
            "forbidden_fields": forbidden,
            "malformed_tables": malformed_tables,
            "status": "PASS" if not method_failures else "FAIL",
        }
        checks.append(check)
        if method_failures:
            failures.append({"method": method, "code": "PREDICTION_AUDIT", "detail": method_failures})

    report = {
        "audit_version": "0.1",
        "expected_instances": len(expected),
        "methods_expected": len(args.methods),
        "methods_audited": len(checks),
        "status": "PASS" if not failures else "FAIL",
        "checks": checks,
        "failures": failures,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
