from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from vett_r23.evaluation import score_predictions as _score_r23

from .spec import LEVELS


def _ratio(a: int, b: int) -> float:
    return round(a / b, 6) if b else 0.0


def score_predictions(release_dir: Path, predictions_path: Path, *, instance_ids: list[str] | None = None) -> dict[str, Any]:
    result = _score_r23(release_dir, predictions_path, instance_ids=instance_ids)
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    submitted: dict[str, dict[str, dict[str, Any]]] = {}
    for line in predictions_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            submitted[row["instance_id"]] = {str(item["question_id"]): item for item in row.get("knowledge_predictions", []) if "question_id" in item}
    selected = instance_ids or summary["match_ids"]
    by_level: dict[str, Counter[str]] = {level: Counter() for level in LEVELS}
    counterfactual = Counter()
    scope = Counter()
    joint = Counter()
    brier_sum = 0.0
    for match_id in selected:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        predictions = submitted.get(match_id, {})
        for answer in gold["knowledge_answers"]:
            item = predictions.get(answer["question_id"])
            answer_ok = item is not None and str(item.get("answer_code")) == str(answer["answer_code"])
            cf_ok = item is not None and str(item.get("counterfactual_answer_code")) == str(answer["counterfactual_answer_code"])
            predicted_roles = {str(span): "decisive" for span in (item.get("decisive_spans", []) if item else [])}
            predicted_roles.update({str(span): "misleading" for span in (item.get("misleading_spans", []) if item else [])})
            gold_roles = {str(span): "decisive" for span in answer["decisive_evidence_spans"]}
            gold_roles.update({str(span): "misleading" for span in answer["misleading_evidence_spans"]})
            scope_correct = sum(predicted_roles.get(span) == role for span, role in gold_roles.items())
            scope["correct"] += scope_correct
            scope["total"] += len(gold_roles)
            atoms_ok = item is not None and set(map(str, item.get("reasoning_atoms", []))) == set(answer["required_atoms"])
            spans_ok = item is not None and set(map(str, item.get("decisive_spans", []))) == set(answer["decisive_evidence_spans"]) and set(map(str, item.get("misleading_spans", []))) == set(answer["misleading_evidence_spans"])
            joint["correct"] += int(answer_ok and cf_ok and atoms_ok and spans_ok)
            joint["total"] += 1
            counterfactual["correct"] += int(cf_ok)
            counterfactual["pair_correct"] += int(answer_ok and cf_ok)
            counterfactual["total"] += 1
            bucket = by_level[answer["level"]]
            bucket["correct"] += int(answer_ok)
            bucket["total"] += 1
            try:
                confidence = min(1.0, max(0.0, float(item.get("confidence", 0.0)))) if item else 0.0
            except (TypeError, ValueError):
                confidence = 0.0
            brier_sum += (confidence - float(answer_ok)) ** 2
    level_accuracy = {level: _ratio(by_level[level]["correct"], by_level[level]["total"]) for level in LEVELS}
    result.update({
        "fact_answer_macro_accuracy": round(sum(level_accuracy.values()) / len(LEVELS), 6),
        "fact_answer_accuracy_by_level": level_accuracy,
        "scope_assignment_accuracy": _ratio(scope["correct"], scope["total"]),
        "counterfactual_answer_accuracy": _ratio(counterfactual["correct"], counterfactual["total"]),
        "counterfactual_pair_consistency": _ratio(counterfactual["pair_correct"], counterfactual["total"]),
        "answer_reasoning_evidence_counterfactual_joint_exact": {"correct": joint["correct"], "total": joint["total"], "accuracy": _ratio(joint["correct"], joint["total"])},
        "confidence_brier_score": round(brier_sum / joint["total"], 6) if joint["total"] else 0.0,
    })
    return result


def write_oracle_predictions(release_dir: Path, output_path: Path, *, test_only: bool) -> dict[str, Any]:
    if not test_only:
        raise ValueError("oracle export requires test_only=True")
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    records: list[str] = []
    for match_id in summary["match_ids"]:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        record = {
            "instance_id": match_id,
            "knowledge_predictions": [{
                "question_id": item["question_id"], "answer_code": item["answer_code"],
                "reasoning_atoms": item["required_atoms"], "decisive_spans": item["decisive_evidence_spans"],
                "misleading_spans": item["misleading_evidence_spans"],
                "counterfactual_answer_code": item["counterfactual_answer_code"],
                "explanation": "TEST_ONLY_ORACLE", "confidence": 1.0,
            } for item in gold["knowledge_answers"]],
            "open_qa_predictions": [{
                "question_id": item["question_id"], "conclusion_value": item["conclusion_value"],
                "reasoning_atoms": item["required_atoms"], "decisive_spans": item["decisive_evidence"]["spans"],
                "decisive_edges": item["decisive_evidence"]["edges"], "provenance_spans": item["provenance_context"]["spans"],
                "provenance_edges": item["provenance_context"]["edges"], "explanation": "TEST_ONLY_ORACLE", "confidence": 1.0,
            } for item in gold["open_qa_answers"]],
        }
        records.append(json.dumps(record, ensure_ascii=False, sort_keys=True))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(records) + "\n", encoding="utf-8")
    return {"status": "COMPLETE", "instances": len(records), "output": str(output_path), "test_only": True}


__all__ = ["score_predictions", "write_oracle_predictions"]
