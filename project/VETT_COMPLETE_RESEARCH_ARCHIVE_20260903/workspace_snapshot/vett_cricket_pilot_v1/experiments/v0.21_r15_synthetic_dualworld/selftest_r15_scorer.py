#!/usr/bin/env python3
"""Deterministic scorer tests: blank, perfect, and mutation plus hallucination."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("r15_scorer", HERE / "score_r15_predictions.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def run_case(cells: dict) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        prediction = Path(directory) / "prediction.json"
        prediction.write_text(json.dumps({"cells": cells}))
        return MODULE.score(HERE / "private_gold.json", prediction)


gold_payload = json.loads((HERE / "private_gold.json").read_text())
gold = {c["cell_id"]: c["value"] for c in gold_payload["scored_cells"]}

blank = run_case({})
perfect = run_case(gold)
mutated = dict(gold)
first = next(iter(mutated))
mutated[first] += 1
mutated["invented|row|field"] = 999
mutation = run_case(mutated)

checks = {
    "blank_has_68_missing": blank["missing_cells"] == 68 and blank["correct_cells"] == 0,
    "perfect_has_68_correct": perfect["correct_cells"] == 68 and perfect["cell_accuracy"] == 1.0,
    "mutation_has_one_wrong": mutation["wrong_cells"] == 1 and mutation["missing_cells"] == 0,
    "mutation_has_one_hallucination": mutation["hallucination_count"] == 1,
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "R15_SCORER_SELFTEST.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["status"] == "PASS" else 1)
