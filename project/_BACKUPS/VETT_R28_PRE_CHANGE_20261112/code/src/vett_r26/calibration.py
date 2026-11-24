from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .spec import LEVELS


PRIMARY_METRICS = (
    "factual_record_macro_accuracy",
    "decision_field_macro_accuracy",
    "minimal_evidence_f1",
    "counterfactual_full_record_exact_match",
    "paired_factual_counterfactual_exact",
    "latent_state_accuracy",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _question_map(analysis: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["instance_id"]), str(row["question_id"])): row
        for row in analysis["question_results"]
    }


def compare_pair(label: str, baseline_path: Path, candidate_path: Path) -> dict[str, Any]:
    baseline = _read(baseline_path)
    candidate = _read(candidate_path)
    old = _question_map(baseline)
    new = _question_map(candidate)
    if set(old) != set(new):
        raise ValueError(f"paired question IDs differ for {label}")
    transitions = {"wrong_to_correct": [], "correct_to_wrong": [], "unchanged": 0}
    for key in sorted(old):
        before = bool(old[key]["record_exact"])
        after = bool(new[key]["record_exact"])
        if before == after:
            transitions["unchanged"] += 1
            continue
        name = "wrong_to_correct" if after else "correct_to_wrong"
        transitions[name].append({
            "instance_id": key[0],
            "question_id": key[1],
            "level": new[key]["level"],
            "scenario_family": new[key]["scenario_family"],
        })
    old_scores, new_scores = baseline["scores"], candidate["scores"]
    metrics = {
        metric: {
            "baseline": old_scores[metric],
            "candidate": new_scores[metric],
            "delta": round(new_scores[metric] - old_scores[metric], 6),
        }
        for metric in PRIMARY_METRICS
    }
    levels = {
        level: {
            "baseline": old_scores["full_record_exact_by_level"][level],
            "candidate": new_scores["full_record_exact_by_level"][level],
            "delta": round(
                new_scores["full_record_exact_by_level"][level]
                - old_scores["full_record_exact_by_level"][level],
                6,
            ),
        }
        for level in LEVELS
    }
    return {
        "label": label,
        "baseline_run_id": baseline["run_id"],
        "candidate_run_id": candidate["run_id"],
        "model": candidate["model"],
        "metrics": metrics,
        "levels": levels,
        "factual_target_ceiling_pass": new_scores["factual_record_macro_accuracy"] <= 0.65,
        "factual_no_regression_pass": new_scores["factual_record_macro_accuracy"] <= old_scores["factual_record_macro_accuracy"],
        "evidence_no_regression_pass": new_scores["minimal_evidence_f1"] <= old_scores["minimal_evidence_f1"],
        "paired_no_regression_pass": new_scores["paired_factual_counterfactual_exact"] <= old_scores["paired_factual_counterfactual_exact"],
        "adjacent_level_gap_pass": bool(new_scores["adjacent_level_gap_pass"]),
        "transitions": transitions,
    }


def calibration_report(pairs: list[tuple[str, Path, Path]]) -> dict[str, Any]:
    comparisons = [compare_pair(label, baseline, candidate) for label, baseline, candidate in pairs]
    gates = {
        "all_models_below_65pct_factual": all(row["factual_target_ceiling_pass"] for row in comparisons),
        "no_model_factual_regression": all(row["factual_no_regression_pass"] for row in comparisons),
        "no_model_evidence_regression": all(row["evidence_no_regression_pass"] for row in comparisons),
        "no_model_paired_regression": all(row["paired_no_regression_pass"] for row in comparisons),
        "all_models_adjacent_gap_pass": all(row["adjacent_level_gap_pass"] for row in comparisons),
    }
    return {
        "status": "PASS" if all(gates.values()) else "REVISE",
        "gates": gates,
        "comparisons": comparisons,
        "decision": "READY_FOR_EXPANSION" if all(gates.values()) else "REVISE_BEFORE_EXPANSION",
        "limitations": [
            "Five matches provide only five questions per level; exact level rates move in 20-point steps.",
            "Paired single-run deltas include model sampling variance and require confirmation on a larger calibration panel.",
        ],
    }


def _markdown(report: dict[str, Any]) -> str:
    rows = []
    for item in report["comparisons"]:
        factual = item["metrics"]["factual_record_macro_accuracy"]
        evidence = item["metrics"]["minimal_evidence_f1"]
        paired = item["metrics"]["paired_factual_counterfactual_exact"]
        levels = "/".join(f"{item['levels'][level]['candidate']:.0%}" for level in LEVELS)
        rows.append(
            f"| {item['model']} | {factual['baseline']:.0%} → {factual['candidate']:.0%} | "
            f"{evidence['baseline']:.1%} → {evidence['candidate']:.1%} | "
            f"{paired['baseline']:.0%} → {paired['candidate']:.0%} | {levels} |"
        )
    gates = "\n".join(
        f"| {name} | {'PASS' if value else 'FAIL'} |" for name, value in report["gates"].items()
    )
    return f"""# R26 paired five-match sentinel

Status: **{report['status']}**

| Model | Factual exact | Evidence F1 | Paired exact | R26 L1/L2/L3/L4/L5 |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

| Gate | Result |
|---|---|
{gates}

Five questions per level imply 20-point resolution. This sentinel is a gate, not a final level-effect estimate.
"""


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-calibration")
    parser.add_argument("--pair", nargs=3, action="append", metavar=("LABEL", "BASELINE", "CANDIDATE"), required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    report = calibration_report([(label, Path(base), Path(candidate)) for label, base, candidate in args.pair])
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["calibration_report", "compare_pair"]
