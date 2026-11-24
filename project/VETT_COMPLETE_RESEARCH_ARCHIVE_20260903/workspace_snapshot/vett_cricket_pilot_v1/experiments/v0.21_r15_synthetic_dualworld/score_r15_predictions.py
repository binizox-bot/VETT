#!/usr/bin/env python3
"""Score an R15 prediction after predictions have been frozen.

Prediction format: {"cells": {"table|row|column": value, ...}}
Only cell IDs in private_gold.json are scored. Extra IDs are hallucinations.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def normalize(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return int(value) if float(value).is_integer() else float(value)
    text = str(value).strip()
    try:
        number = float(text)
        return int(number) if number.is_integer() else number
    except ValueError:
        return text


def score(gold_path: Path, prediction_path: Path) -> dict:
    gold_payload = json.loads(gold_path.read_text())
    prediction_payload = json.loads(prediction_path.read_text())
    predictions = prediction_payload.get("cells", prediction_payload)
    if not isinstance(predictions, dict):
        raise ValueError("Prediction must be an object or contain an object named 'cells'")
    gold = {cell["cell_id"]: cell for cell in gold_payload["scored_cells"]}
    missing, wrong, correct = [], [], []
    component = defaultdict(lambda: {"correct": 0, "wrong": 0, "missing": 0})
    for cell_id, item in gold.items():
        if cell_id not in predictions or normalize(predictions[cell_id]) is None:
            missing.append(cell_id)
            component[item["component_id"]]["missing"] += 1
        elif normalize(predictions[cell_id]) == normalize(item["value"]):
            correct.append(cell_id)
            component[item["component_id"]]["correct"] += 1
        else:
            wrong.append({"cell_id": cell_id, "gold": item["value"], "prediction": predictions[cell_id]})
            component[item["component_id"]]["wrong"] += 1
    hallucinations = sorted(set(predictions) - set(gold))
    total = len(gold)
    resolved_components = sum(v["correct"] == 2 for v in component.values())
    return {
        "total_scored_cells": total,
        "correct_cells": len(correct),
        "wrong_cells": len(wrong),
        "missing_cells": len(missing),
        "cell_accuracy": len(correct) / total,
        "cell_error_rate": (len(wrong) + len(missing)) / total,
        "hallucinated_cell_ids": hallucinations,
        "hallucination_count": len(hallucinations),
        "fully_correct_components": resolved_components,
        "total_components": len(component),
        "component_accuracy": resolved_components / len(component),
        "wrong_details": wrong,
        "missing_cell_ids": missing,
        "component_breakdown": dict(component),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--prediction", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    result = score(Path(args.gold), Path(args.prediction))
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
