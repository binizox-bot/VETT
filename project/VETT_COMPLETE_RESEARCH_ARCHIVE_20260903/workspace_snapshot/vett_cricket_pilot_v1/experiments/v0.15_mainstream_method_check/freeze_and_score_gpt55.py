#!/usr/bin/env python3
"""Freeze six blind GPT-5.5 predictions, score them, and build a summary.

The script refuses to overwrite an existing freeze file. Run it only after all
six isolated evaluators have completed and JSON validation has passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
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


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    run_dir = args.experiment_dir / "runs_gpt55"
    score_dir = args.experiment_dir / "scores_gpt55"
    freeze_path = args.experiment_dir / "GPT55_PREDICTION_FREEZE.json"
    if freeze_path.exists():
        raise SystemExit(f"Refusing to overwrite existing freeze: {freeze_path}")

    prediction_paths = {m: run_dir / f"{m}.prediction.json" for m in METHODS}
    missing = [str(path) for path in prediction_paths.values() if not path.exists()]
    if missing:
        raise SystemExit("Missing predictions:\n" + "\n".join(missing))

    for method, path in prediction_paths.items():
        parsed = json.loads(path.read_text(encoding="utf-8"))
        if parsed.get("method") != method or not isinstance(parsed.get("tables"), list):
            raise SystemExit(f"Invalid prediction contract: {path}")

    freeze = {
        "stage": "after blind generation and JSON validation; before gold scoring",
        "model": "GPT-5.5",
        "prediction_sha256": {method: sha256(path) for method, path in prediction_paths.items()},
    }
    freeze_path.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    scorer = args.experiment_dir / "score_r10_predictions.py"
    score_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for method, prediction in prediction_paths.items():
        output = score_dir / f"{method}.score.json"
        subprocess.run(
            [
                sys.executable,
                str(scorer),
                "--gold",
                str(args.gold),
                "--evidence",
                str(args.evidence),
                "--prediction",
                str(prediction),
                "--output",
                str(output),
            ],
            check=True,
        )
        report = json.loads(output.read_text(encoding="utf-8"))
        overall = report["overall"]
        results[method] = {
            "prediction_sha256": freeze["prediction_sha256"][method],
            "gold_cells": overall["gold"],
            "correct": overall.get("correct", 0),
            "incorrect": overall.get("incorrect", 0),
            "missing": overall.get("missing", 0),
            "hallucinated": overall.get("hallucinated", 0),
            "cell_accuracy": overall["cell_accuracy"],
            "cell_error_rate": overall["cell_error_rate"],
            "omission_rate": overall["omission_rate"],
            "hallucination_rate": round(overall.get("hallucinated", 0) / overall["gold"], 6),
            "row_exact_rate": report["row_exact"]["rate"],
            "table_exact_rate": report["table_exact"]["rate"],
            "instance_exact": report["instance_exact"],
        }

    summary = {
        "experiment_id": "v0.15-r10-gpt55-blind",
        "model": "GPT-5.5",
        "instances": 1,
        "scored_cells_per_method": 336,
        "methods": results,
        "interpretation_limits": [
            "One root and one backbone are a diagnostic, not a population leaderboard.",
            "T3 paper condition uses the direct-integration variant, not generated-code integration.",
            "R10 supplies a fixed schema, so Map&Make latent-schema discovery is not measured.",
            "The same constructor family produced the benchmark; independent human recoverability remains required.",
        ],
    }
    summary_json = args.experiment_dir / "GPT55_R10_RESULTS.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# R10 isolated GPT-5.5 blind diagnostic",
        "",
        "| Method | Correct | Wrong | Missing | Hallucinated | Cell error | Omission | Row exact | Table exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method in METHODS:
        r = results[method]
        lines.append(
            f"| {method} | {r['correct']}/336 | {r['incorrect']} | {r['missing']} | "
            f"{r['hallucinated']} | {pct(r['cell_error_rate'])} | {pct(r['omission_rate'])} | "
            f"{pct(r['row_exact_rate'])} | {pct(r['table_exact_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "This is a one-root, one-backbone construction diagnostic. It cannot establish population performance or a market-wide ranking.",
            "",
        ]
    )
    (args.experiment_dir / "GPT55_R10_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
