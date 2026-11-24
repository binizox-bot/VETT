#!/usr/bin/env python3
"""Strict scorer for VETT dataset/scoring v1 frozen batch.

Predictions JSONL rows must contain sample_id, model, and either raw_output or
parsed. Key aliases are an explicit allow-list from the private gold file.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def parse_json_output(value):
    if isinstance(value, dict):
        return value, None
    if value is None:
        return None, "empty_output"
    text = str(value).strip()
    if not text:
        return None, "empty_output"
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
    except Exception as exc:
        return None, f"invalid_json:{type(exc).__name__}"
    if isinstance(obj, dict) and isinstance(obj.get("fields"), dict):
        obj = obj["fields"]
    if not isinstance(obj, dict):
        return None, "json_not_object"
    return obj, None


def normalize_fields(obj, alias_map):
    normalized = {}
    used = {}
    problems = []
    for canonical, aliases in alias_map.items():
        present = [(key, obj[key]) for key in aliases if key in obj]
        if not present:
            problems.append(f"missing:{canonical}")
            continue
        values = {json.dumps(value, sort_keys=True) for _, value in present}
        if len(values) != 1:
            problems.append(f"conflicting_aliases:{canonical}")
            continue
        used[canonical] = [key for key, _ in present]
        normalized[canonical] = present[0][1]
    return normalized, used, problems


def int_equal(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return False
    try:
        return int(left) == int(right)
    except Exception:
        return left == right


def score_one(raw_or_parsed, gold_row):
    parsed, parse_error = parse_json_output(raw_or_parsed)
    if parse_error:
        return {
            "executable": False,
            "error": parse_error,
            "normalized": {},
            "field_scores": {},
            "correct_fields": 0,
            "total_fields": len(gold_row["field_order"]),
            "task_correct": False,
        }
    normalized, used, problems = normalize_fields(parsed, gold_row["legal_key_aliases"])
    field_scores = {}
    for field in gold_row["field_order"]:
        pred = normalized.get(field)
        gold = gold_row["gold"][field]
        field_scores[field] = {
            "gold": gold,
            "pred": pred,
            "ok": field in normalized and int_equal(pred, gold),
            "source_keys": used.get(field, []),
        }
    executable = not problems
    correct_fields = sum(1 for item in field_scores.values() if item["ok"])
    return {
        "executable": executable,
        "error": ";".join(problems) if problems else None,
        "normalized": normalized,
        "field_scores": field_scores,
        "correct_fields": correct_fields,
        "total_fields": len(field_scores),
        "task_correct": executable and correct_fields == len(field_scores),
    }


def load_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def score_file(predictions_path, gold_path, output_path):
    gold_rows = load_jsonl(gold_path)
    gold_by_id = {row["sample_id"]: row for row in gold_rows}
    predictions = load_jsonl(predictions_path)
    out = []
    for row in predictions:
        sample_id = row.get("sample_id")
        if sample_id not in gold_by_id:
            out.append({
                "sample_id": sample_id,
                "model": row.get("model"),
                "executable": False,
                "error": "unknown_sample_id",
                "task_correct": False,
            })
            continue
        value = row.get("parsed") if isinstance(row.get("parsed"), dict) else row.get("raw_output")
        scored = score_one(value, gold_by_id[sample_id])
        out.append({"sample_id": sample_id, "model": row.get("model"), **scored})
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in out), encoding="utf-8")
    return out


def self_test():
    gold = {
        "sample_id": "vett-dev-v1-0002-c10",
        "field_order": [
            "Evan Clarke_wickets",
            "Evan Clarke_runs",
            "Connor Reed_wickets",
            "Connor Reed_runs",
            "innings_total_wickets",
        ],
        "gold": {
            "Evan Clarke_wickets": 3,
            "Evan Clarke_runs": 28,
            "Connor Reed_wickets": 2,
            "Connor Reed_runs": 28,
            "innings_total_wickets": 8,
        },
        "legal_key_aliases": {
            "Evan Clarke_wickets": ["Evan Clarke_wickets", "Evan_Clarke_wickets"],
            "Evan Clarke_runs": ["Evan Clarke_runs", "Evan_Clarke_runs"],
            "Connor Reed_wickets": ["Connor Reed_wickets", "Connor_Reed_wickets"],
            "Connor Reed_runs": ["Connor Reed_runs", "Connor_Reed_runs"],
            "innings_total_wickets": ["innings_total_wickets"],
        },
    }
    tests = [
        ("correct", {"Evan Clarke_wickets": 3, "Evan Clarke_runs": 28, "Connor Reed_wickets": 2, "Connor Reed_runs": 28, "innings_total_wickets": 8}, True, True),
        ("people_swapped", {"Evan Clarke_wickets": 2, "Evan Clarke_runs": 28, "Connor Reed_wickets": 3, "Connor Reed_runs": 28, "innings_total_wickets": 8}, True, False),
        ("one_side_only", {"Evan Clarke_wickets": 3, "Evan Clarke_runs": 28, "Connor Reed_wickets": 1, "Connor Reed_runs": 28, "innings_total_wickets": 8}, True, False),
        ("wrong_transfer", {"Evan Clarke_wickets": 5, "Evan Clarke_runs": 28, "Connor Reed_wickets": 0, "Connor Reed_runs": 28, "innings_total_wickets": 8}, True, False),
        ("empty", "", False, False),
        ("legal_key_alias", {"Evan_Clarke_wickets": 3, "Evan_Clarke_runs": 28, "Connor_Reed_wickets": 2, "Connor_Reed_runs": 28, "innings_total_wickets": 8}, True, True),
    ]
    results = []
    for name, value, expected_exec, expected_correct in tests:
        actual = score_one(value, gold)
        passed = actual["executable"] == expected_exec and actual["task_correct"] == expected_correct
        results.append({
            "name": name,
            "expected_executable": expected_exec,
            "expected_task_correct": expected_correct,
            "actual_executable": actual["executable"],
            "actual_task_correct": actual["task_correct"],
            "passed": passed,
        })
    return {"passed": all(row["passed"] for row in results), "tests": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions")
    parser.add_argument("--gold")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result["passed"] else 1)
    if not (args.predictions and args.gold and args.out):
        parser.error("--predictions, --gold and --out are required unless --self-test is used")
    rows = score_file(args.predictions, args.gold, args.out)
    print(json.dumps({"rows": len(rows), "correct": sum(1 for row in rows if row.get("task_correct")), "executable": sum(1 for row in rows if row.get("executable"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
