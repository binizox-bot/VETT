#!/usr/bin/env python3
"""Mechanical validation for the frozen GPT-5.5 diagnostic package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


METHODS = [
    "direct_no_cot",
    "direct_cot",
    "t3_paper_direct_integration_variant",
    "t3_provenance_enhanced",
    "mapmake_paper_style",
    "mapmake_scope_version_enhanced",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    failures = []
    freeze = json.loads((args.experiment_dir / "GPT55_PREDICTION_FREEZE.json").read_text())
    summary = json.loads((args.experiment_dir / "GPT55_R10_RESULTS.json").read_text())
    decomposition = json.loads((args.experiment_dir / "GPT55_R10_ERROR_DECOMPOSITION.json").read_text())
    blind = json.loads((args.experiment_dir / "blind" / "r10_blind.jsonl").read_text())
    contract = blind["output_contract"]["top_level"]["tables"]
    checks = {}

    for method in METHODS:
        prediction_path = args.experiment_dir / "runs_gpt55" / f"{method}.prediction.json"
        prediction = json.loads(prediction_path.read_text())
        observed_hash = sha256(prediction_path)
        hash_ok = observed_hash == freeze["prediction_sha256"][method]
        structure_ok = prediction.get("method") == method and len(prediction.get("tables", [])) == len(contract)
        if structure_ok:
            for got, expected in zip(prediction["tables"], contract, strict=True):
                structure_ok &= (
                    got.get("table_type") == expected.get("table_type")
                    and got.get("innings_id") == expected.get("innings_id")
                    and got.get("columns") == expected.get("columns")
                    and len(got.get("rows", [])) == len(expected.get("rows", []))
                )
                if not structure_ok:
                    break
                row_key = expected["columns"][0]
                structure_ok &= all(
                    got_row.get(row_key) == expected_row.get(row_key)
                    for got_row, expected_row in zip(got["rows"], expected["rows"], strict=True)
                )
        result = summary["methods"][method]
        arithmetic_ok = (
            result["correct"] + result["incorrect"] + result["missing"] == result["gold_cells"] == 336
        )
        core = decomposition["methods"][method]["scalar_core"]
        core_ok = core["correct"] + core["errors"] == core["gold"] == 232
        checks[method] = {
            "hash_ok": hash_ok,
            "structure_ok": bool(structure_ok),
            "score_arithmetic_ok": arithmetic_ok,
            "core_arithmetic_ok": core_ok,
            "prediction_sha256": observed_hash,
        }
        if not all((hash_ok, structure_ok, arithmetic_ok, core_ok)):
            failures.append(method)

    public_text = blind["documents"][0]["text"].casefold()
    unsupported_check = {
        "samuel_moore_occurrences": public_text.count("samuel moore"),
        "referee_occurrences": public_text.count("referee"),
    }
    if unsupported_check != {"samuel_moore_occurrences": 0, "referee_occurrences": 0}:
        failures.append("unsupported_gold_recheck_changed")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "freeze_stage": freeze["stage"],
        "methods": checks,
        "unsupported_gold_check": unsupported_check,
        "failures": failures,
    }
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": failures}, indent=2))
    raise SystemExit(0 if not failures else 1)


if __name__ == "__main__":
    main()
