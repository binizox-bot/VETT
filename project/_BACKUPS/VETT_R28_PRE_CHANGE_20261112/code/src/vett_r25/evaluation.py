from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .solver import flatten_record
from .spec import LEVELS


def _ratio(a: int, b: int) -> float:
    return round(a / b, 6) if b else 0.0


def _set_f1(predicted: set[str], gold: set[str]) -> tuple[int, int, int]:
    return len(predicted & gold), len(predicted - gold), len(gold - predicted)


def score_predictions(release_dir: Path, predictions_path: Path, *, instance_ids: list[str] | None = None) -> dict[str, Any]:
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in predictions_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        submitted[str(row["instance_id"])] = {
            str(item["question_id"]): item
            for item in row.get("decision_predictions", [])
            if "question_id" in item
        }
    selected = instance_ids or summary["match_ids"]
    field = Counter()
    cf_field = Counter()
    state = Counter()
    cf_state = Counter()
    evidence = Counter()
    record_exact = Counter()
    cf_exact = Counter()
    pair_exact = Counter()
    by_level: dict[str, Counter[str]] = {level: Counter() for level in LEVELS}
    exact_by_level: dict[str, Counter[str]] = {level: Counter() for level in LEVELS}
    brier_sum = 0.0

    for match_id in selected:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        predictions = submitted.get(match_id, {})
        for answer in gold["decision_answers"]:
            prediction = predictions.get(answer["question_id"], {})
            pred_record = prediction.get("decision_record", {})
            pred_cf = prediction.get("counterfactual_record", {})
            try:
                pred_flat = flatten_record(pred_record)
            except (KeyError, TypeError, ValueError):
                pred_flat = {}
            try:
                pred_cf_flat = flatten_record(pred_cf)
            except (KeyError, TypeError, ValueError):
                pred_cf_flat = {}
            gold_flat = answer["decision_record_flat"]
            gold_cf_flat = answer["counterfactual"]["decision_record_flat"]
            factual_correct = sum(pred_flat.get(key) == value for key, value in gold_flat.items())
            counterfactual_correct = sum(pred_cf_flat.get(key) == value for key, value in gold_cf_flat.items())
            field["correct"] += factual_correct
            field["total"] += len(gold_flat)
            cf_field["correct"] += counterfactual_correct
            cf_field["total"] += len(gold_cf_flat)
            bucket = by_level[answer["level"]]
            bucket["correct"] += factual_correct
            bucket["total"] += len(gold_flat)
            factual_exact = pred_flat == gold_flat
            counterfactual_exact = pred_cf_flat == gold_cf_flat
            record_exact["correct"] += int(factual_exact)
            record_exact["total"] += 1
            exact_by_level[answer["level"]]["correct"] += int(factual_exact)
            exact_by_level[answer["level"]]["total"] += 1
            cf_exact["correct"] += int(counterfactual_exact)
            cf_exact["total"] += 1
            pair_exact["correct"] += int(factual_exact and counterfactual_exact)
            pair_exact["total"] += 1

            for key, value in answer["state"].items():
                state["correct"] += int(prediction.get("state", {}).get(key) == value)
                state["total"] += 1
            for key, value in answer["counterfactual"]["state"].items():
                cf_state["correct"] += int(prediction.get("counterfactual_state", {}).get(key) == value)
                cf_state["total"] += 1
            tp, fp, fn = _set_f1(
                set(map(str, prediction.get("evidence_spans", []))),
                set(map(str, answer["minimum_evidence_spans"])),
            )
            evidence["tp"] += tp
            evidence["fp"] += fp
            evidence["fn"] += fn
            try:
                confidence = min(1.0, max(0.0, float(prediction.get("confidence", 0.0))))
            except (TypeError, ValueError):
                confidence = 0.0
            brier_sum += (confidence - float(factual_exact)) ** 2

    ev_precision = evidence["tp"] / (evidence["tp"] + evidence["fp"]) if evidence["tp"] + evidence["fp"] else 0.0
    ev_recall = evidence["tp"] / (evidence["tp"] + evidence["fn"]) if evidence["tp"] + evidence["fn"] else 0.0
    ev_f1 = 2 * ev_precision * ev_recall / (ev_precision + ev_recall) if ev_precision + ev_recall else 0.0
    per_level = {level: _ratio(by_level[level]["correct"], by_level[level]["total"]) for level in LEVELS}
    exact_per_level = {level: _ratio(exact_by_level[level]["correct"], exact_by_level[level]["total"]) for level in LEVELS}
    adjacent_gaps = {
        f"{LEVELS[index]}-{LEVELS[index + 1]}": round(
            exact_per_level[LEVELS[index]] - exact_per_level[LEVELS[index + 1]], 6
        )
        for index in range(len(LEVELS) - 1)
    }
    return {
        "instances": len(selected),
        "questions": record_exact["total"],
        "decision_field_macro_accuracy": _ratio(field["correct"], field["total"]),
        "decision_field_accuracy_by_level": per_level,
        "level_macro_accuracy": round(sum(per_level.values()) / len(LEVELS), 6),
        "full_record_exact_match": _ratio(record_exact["correct"], record_exact["total"]),
        "full_record_exact_by_level": exact_per_level,
        "full_record_exact_counts_by_level": {
            level: {
                "correct": exact_by_level[level]["correct"],
                "total": exact_by_level[level]["total"],
            }
            for level in LEVELS
        },
        "adjacent_level_exact_gaps": adjacent_gaps,
        "adjacent_level_gap_target": 0.08,
        "adjacent_level_gap_pass": all(gap >= 0.08 for gap in adjacent_gaps.values()),
        "factual_record_macro_accuracy": round(sum(exact_per_level.values()) / len(LEVELS), 6),
        "latent_state_accuracy": _ratio(state["correct"], state["total"]),
        "minimal_evidence_precision": round(ev_precision, 6),
        "minimal_evidence_recall": round(ev_recall, 6),
        "minimal_evidence_f1": round(ev_f1, 6),
        "counterfactual_field_accuracy": _ratio(cf_field["correct"], cf_field["total"]),
        "counterfactual_full_record_exact_match": _ratio(cf_exact["correct"], cf_exact["total"]),
        "counterfactual_state_accuracy": _ratio(cf_state["correct"], cf_state["total"]),
        "paired_factual_counterfactual_exact": _ratio(pair_exact["correct"], pair_exact["total"]),
        "confidence_brier_score": round(brier_sum / record_exact["total"], 6) if record_exact["total"] else 0.0,
    }


def write_oracle_predictions(release_dir: Path, output_path: Path, *, test_only: bool) -> dict[str, Any]:
    if not test_only:
        raise ValueError("oracle export requires test_only=True")
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    rows: list[str] = []
    for match_id in summary["match_ids"]:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        rows.append(json.dumps({
            "instance_id": match_id,
            "decision_predictions": [{
                "question_id": item["question_id"],
                "decision_record": item["decision_record"],
                "state": item["state"],
                "evidence_spans": item["minimum_evidence_spans"],
                "counterfactual_record": item["counterfactual"]["decision_record"],
                "counterfactual_state": item["counterfactual"]["state"],
                "explanation": "TEST_ONLY_ORACLE",
                "confidence": 1.0,
            } for item in gold["decision_answers"]],
        }, ensure_ascii=False, sort_keys=True))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return {"status": "COMPLETE", "instances": len(rows), "output": str(output_path), "test_only": True}


__all__ = ["score_predictions", "write_oracle_predictions"]
