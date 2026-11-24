#!/usr/bin/env python3
"""Score normalized VETT-Cricket prediction JSONL files."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def norm(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value).strip()).casefold()
    try:
        number = float(text)
        return str(int(number)) if number.is_integer() else f"{number:.6f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def flatten_tables(tables: list[dict[str, Any]]) -> dict[str, Any]:
    cells = {}
    for table in tables:
        table_id = table.get("table_id", "")
        columns = table.get("columns", [])
        for row_index, row in enumerate(table.get("rows", []), 1):
            row_id = row.get("row_id", f"r{row_index:03d}")
            for column in columns:
                if column in row:
                    cell_id = f"{table_id}.{row_id}.{re.sub(r'[^a-z0-9]+', '_', column.lower()).strip('_')}"
                    cells[cell_id] = row[column]
    return cells


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    dataset = {x["instance_id"]: x for x in load_jsonl(args.dataset)}
    predictions = {x["instance_id"]: x for x in load_jsonl(args.predictions)}
    per_instance = []
    groups = defaultdict(Counter)

    for iid, instance in dataset.items():
        scored = set(instance["gold"]["scored_cell_ids"])
        if not scored:
            continue
        gold_all = flatten_tables(instance["gold"]["tables"])
        gold_universe = set(gold_all)
        pred = predictions.get(iid)
        pred_all = flatten_tables(pred.get("tables", [])) if pred else {}
        correct = sum(cell_id in pred_all and norm(pred_all[cell_id]) == norm(gold_all[cell_id]) for cell_id in scored)
        missing = sum(cell_id not in pred_all for cell_id in scored)
        incorrect = len(scored) - correct - missing
        # Gold structural cells may be deliberately excluded from value scoring.
        # Predicting those cells is valid; only cells outside the gold table
        # universe count as hallucinations.
        hallucinated = sum(cell_id not in gold_universe for cell_id in pred_all)
        cell_accuracy = correct / len(scored)
        omission_rate = missing / len(scored)
        hallucination_rate = hallucinated / len(scored)
        table_exact = int(correct == len(scored) and hallucinated == 0)
        row = {
            "instance_id": iid,
            "view": instance["view"],
            "tier": instance["difficulty"]["tier"],
            "gold_cells": len(scored),
            "correct": correct,
            "incorrect": incorrect,
            "missing": missing,
            "hallucinated": hallucinated,
            "cell_accuracy": round(cell_accuracy, 6),
            "cell_error_rate": round(1 - cell_accuracy, 6),
            "omission_rate": round(omission_rate, 6),
            "hallucination_rate": round(hallucination_rate, 6),
            "table_exact": table_exact,
        }
        per_instance.append(row)
        for key in (f"view:{instance['view']}", f"tier:{instance['difficulty']['tier']}", "overall"):
            groups[key]["gold"] += len(scored)
            groups[key]["correct"] += correct
            groups[key]["missing"] += missing
            groups[key]["incorrect"] += incorrect
            groups[key]["hallucinated"] += hallucinated
            groups[key]["tables"] += 1
            groups[key]["table_exact"] += table_exact

    report = {
        "scored_instances": len(per_instance),
        "missing_prediction_instances": sum(row["instance_id"] not in predictions for row in per_instance),
        "groups": {},
        "per_instance": per_instance,
    }
    for key, c in sorted(groups.items()):
        report["groups"][key] = {
            **dict(c),
            "cell_accuracy": round(c["correct"] / c["gold"], 6) if c["gold"] else None,
            "cell_error_rate": round(1 - c["correct"] / c["gold"], 6) if c["gold"] else None,
            "omission_rate": round(c["missing"] / c["gold"], 6) if c["gold"] else None,
            "hallucination_rate": round(c["hallucinated"] / c["gold"], 6) if c["gold"] else None,
            "table_exact_rate": round(c["table_exact"] / c["tables"], 6) if c["tables"] else None,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["groups"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
