#!/usr/bin/env python3
"""Score complete R5 fixed-schema table predictions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


KEY_COLUMNS = {
    "Match Summary": "Field", "Innings Summary": "Field", "Batting": "Batter",
    "Bowling": "Bowler", "Partnerships": "Partnership", "Fall of Wickets": "Wkt",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def norm(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def table_key(table: dict[str, Any]) -> tuple[str, str | None]:
    return table["table_type"], table.get("innings_id")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    gold_rows = load_jsonl(args.gold)
    predictions = {row["instance_id"]: row for row in load_jsonl(args.predictions)}
    totals = {"gold": 0, "correct": 0, "incorrect": 0, "missing": 0}
    challenge = {"gold": 0, "correct": 0, "incorrect": 0, "missing": 0}
    instance_exact = 0
    details = []

    for gold in gold_rows:
        pred = predictions.get(gold["instance_id"], {"tables": []})
        pred_tables = {table_key(table): table for table in pred.get("tables", [])}
        challenge_ids = {row["cell_id"] for row in gold["challenge_cells"]}
        instance_errors = 0
        instance_total = 0
        for table in gold["gold_tables"]:
            key_col = KEY_COLUMNS[table["table_type"]]
            pred_table = pred_tables.get(table_key(table), {"rows": []})
            pred_by_key: dict[str, list[dict[str, Any]]] = {}
            for pred_row_item in pred_table.get("rows", []):
                pred_by_key.setdefault(norm(pred_row_item.get(key_col)), []).append(pred_row_item)
            key_occurrences: dict[str, int] = {}
            for pos, gold_row in enumerate(table["rows"], start=1):
                normalized_key = norm(gold_row[key_col])
                occurrence = key_occurrences.get(normalized_key, 0)
                candidates = pred_by_key.get(normalized_key, [])
                pred_row = candidates[occurrence] if occurrence < len(candidates) else {}
                key_occurrences[normalized_key] = occurrence + 1
                row_id = f"r{pos:03d}"
                for column in table["columns"]:
                    if column == key_col or gold_row[column] is None or norm(gold_row[column]) == "":
                        continue
                    cid = f"{table['table_id']}|{row_id}|{column}"
                    instance_total += 1
                    totals["gold"] += 1
                    bucket = challenge if cid in challenge_ids else None
                    if bucket is not None:
                        bucket["gold"] += 1
                    observed = pred_row.get(column)
                    if observed is None or norm(observed) == "":
                        totals["missing"] += 1
                        instance_errors += 1
                        if bucket is not None:
                            bucket["missing"] += 1
                    elif norm(observed) == norm(gold_row[column]):
                        totals["correct"] += 1
                        if bucket is not None:
                            bucket["correct"] += 1
                    else:
                        totals["incorrect"] += 1
                        instance_errors += 1
                        if bucket is not None:
                            bucket["incorrect"] += 1
        if instance_errors == 0:
            instance_exact += 1
        details.append({
            "instance_id": gold["instance_id"],
            "cells": instance_total,
            "errors": instance_errors,
            "exact": instance_errors == 0,
        })

    def finish(bucket: dict[str, int]) -> dict[str, Any]:
        bucket = dict(bucket)
        bucket["accuracy"] = bucket["correct"] / bucket["gold"] if bucket["gold"] else 0.0
        bucket["error_rate"] = (bucket["incorrect"] + bucket["missing"]) / bucket["gold"] if bucket["gold"] else 0.0
        return bucket

    report = {
        "overall": finish(totals),
        "challenge": finish(challenge),
        "instance_exact_match": {"correct": instance_exact, "gold": len(gold_rows), "rate": instance_exact / len(gold_rows)},
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": report["overall"], "challenge": report["challenge"], "instance_exact": report["instance_exact_match"]}, indent=2))


if __name__ == "__main__":
    main()
