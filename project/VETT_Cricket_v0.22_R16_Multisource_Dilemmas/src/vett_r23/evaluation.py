from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .spec import LEVELS


def _ratio(a: int, b: int) -> float:
    return round(a / b, 6) if b else 0.0


def _prf(counts: Counter[str]) -> dict[str, Any]:
    precision = _ratio(counts["tp"], counts["tp"] + counts["fp"])
    recall = _ratio(counts["tp"], counts["tp"] + counts["fn"])
    f1 = round(2 * precision * recall / (precision + recall), 6) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, **dict(counts)}


def _edge(edge: dict[str, Any]) -> tuple[str, str, str]:
    return str(edge.get("from_span")), str(edge.get("relation")), str(edge.get("to_span"))


def _index(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {str(item["question_id"]): item for item in items if isinstance(item, dict) and "question_id" in item}


def score_predictions(
    release_dir: Path,
    predictions_path: Path,
    *,
    instance_ids: list[str] | None = None,
) -> dict[str, Any]:
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    submitted: dict[str, dict[str, Any]] = {}
    for line in predictions_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            submitted[item["instance_id"]] = {
                "knowledge": _index(item.get("knowledge_predictions", [])),
                "open": _index(item.get("open_qa_predictions", [])),
            }
    knowledge = Counter()
    knowledge_atoms = Counter()
    knowledge_decisive_spans = Counter()
    knowledge_misleading_spans = Counter()
    open_answer = Counter()
    open_atoms = Counter()
    decisive_spans = Counter()
    decisive_edges = Counter()
    provenance_spans = Counter()
    provenance_edges = Counter()
    explanation = Counter()
    by_level: dict[str, Counter[str]] = defaultdict(Counter)
    selected_ids = instance_ids or summary["match_ids"]
    unknown = sorted(set(selected_ids) - set(summary["match_ids"]))
    if unknown:
        raise ValueError(f"unknown R23 instance IDs: {unknown}")
    for match_id in selected_ids:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        pred = submitted.get(match_id, {"knowledge": {}, "open": {}})
        for answer in gold["knowledge_answers"]:
            item = pred["knowledge"].get(answer["question_id"])
            answer_ok = item is not None and str(item.get("answer_code")) == str(answer["answer_code"])
            pa = set(map(str, item.get("reasoning_atoms", []))) if item else set()
            ga = set(answer["required_atoms"])
            pds = set(map(str, item.get("decisive_spans", []))) if item else set()
            gds = set(answer.get("decisive_evidence_spans", []))
            pms = set(map(str, item.get("misleading_spans", []))) if item else set()
            gms = set(answer.get("misleading_evidence_spans", []))
            evidence_ok = pds == gds and pms == gms
            knowledge["total"] += 1
            knowledge["correct"] += int(answer_ok)
            knowledge["joint"] += int(answer_ok and pa == ga and evidence_ok)
            knowledge["missing"] += int(item is None)
            knowledge_atoms["tp"] += len(pa & ga)
            knowledge_atoms["fp"] += len(pa - ga)
            knowledge_atoms["fn"] += len(ga - pa)
            for counts, predicted, expected in (
                (knowledge_decisive_spans, pds, gds),
                (knowledge_misleading_spans, pms, gms),
            ):
                counts["tp"] += len(predicted & expected)
                counts["fp"] += len(predicted - expected)
                counts["fn"] += len(expected - predicted)
            bucket = by_level[answer["level"]]
            bucket["knowledge_total"] += 1
            bucket["knowledge_correct"] += int(answer_ok)
            bucket["knowledge_joint"] += int(answer_ok and pa == ga and evidence_ok)
            explanation["knowledge_total"] += 1
            explanation["knowledge_present"] += int(bool(item and str(item.get("explanation", "")).strip()))
        for answer in gold["open_qa_answers"]:
            item = pred["open"].get(answer["question_id"])
            answer_ok = item is not None and str(item.get("conclusion_value")) == str(answer["conclusion_value"])
            pa = set(map(str, item.get("reasoning_atoms", []))) if item else set()
            ga = set(answer["required_atoms"])
            pds = set(map(str, item.get("decisive_spans", []))) if item else set()
            gds = set(answer["decisive_evidence"]["spans"])
            pde = {_edge(edge) for edge in item.get("decisive_edges", []) if isinstance(edge, dict)} if item else set()
            gde = {_edge(edge) for edge in answer["decisive_evidence"]["edges"]}
            pps = set(map(str, item.get("provenance_spans", []))) if item else set()
            gps = set(answer["provenance_context"]["spans"])
            ppe = {_edge(edge) for edge in item.get("provenance_edges", []) if isinstance(edge, dict)} if item else set()
            gpe = {_edge(edge) for edge in answer["provenance_context"]["edges"]}
            open_answer["total"] += 1
            open_answer["correct"] += int(answer_ok)
            open_answer["joint"] += int(answer_ok and pa == ga and pds == gds and pde == gde)
            open_answer["missing"] += int(item is None)
            for counts, predicted, expected in (
                (open_atoms, pa, ga),
                (decisive_spans, pds, gds),
                (decisive_edges, pde, gde),
                (provenance_spans, pps, gps),
                (provenance_edges, ppe, gpe),
            ):
                counts["tp"] += len(predicted & expected)
                counts["fp"] += len(predicted - expected)
                counts["fn"] += len(expected - predicted)
            bucket = by_level[answer["level"]]
            bucket["open_total"] += 1
            bucket["open_correct"] += int(answer_ok)
            bucket["open_joint"] += int(answer_ok and pa == ga and pds == gds and pde == gde)
            explanation["open_total"] += 1
            explanation["open_present"] += int(bool(item and str(item.get("explanation", "")).strip()))
    return {
        "dataset_version": summary["dataset_version"],
        "instances": len(selected_ids),
        "submitted_instances": len(submitted),
        "knowledge_answer_exact": {"correct": knowledge["correct"], "total": knowledge["total"], "accuracy": _ratio(knowledge["correct"], knowledge["total"]), "missing": knowledge["missing"]},
        "knowledge_joint_exact": {"correct": knowledge["joint"], "total": knowledge["total"], "accuracy": _ratio(knowledge["joint"], knowledge["total"])},
        "knowledge_atom_micro": _prf(knowledge_atoms),
        "knowledge_decisive_span_micro": _prf(knowledge_decisive_spans),
        "knowledge_misleading_span_micro": _prf(knowledge_misleading_spans),
        "open_conclusion_exact": {"correct": open_answer["correct"], "total": open_answer["total"], "accuracy": _ratio(open_answer["correct"], open_answer["total"]), "missing": open_answer["missing"]},
        "open_grounded_joint_exact": {"correct": open_answer["joint"], "total": open_answer["total"], "accuracy": _ratio(open_answer["joint"], open_answer["total"])},
        "open_reasoning_atom_micro": _prf(open_atoms),
        "open_decisive_span_micro": _prf(decisive_spans),
        "open_decisive_edge_micro": _prf(decisive_edges),
        "open_provenance_span_micro": _prf(provenance_spans),
        "open_provenance_edge_micro": _prf(provenance_edges),
        "explanation_presence": {
            "knowledge": _ratio(explanation["knowledge_present"], explanation["knowledge_total"]),
            "open": _ratio(explanation["open_present"], explanation["open_total"]),
        },
        "by_level": {
            level: {
                "knowledge_accuracy": _ratio(by_level[level]["knowledge_correct"], by_level[level]["knowledge_total"]),
                "knowledge_joint_accuracy": _ratio(by_level[level]["knowledge_joint"], by_level[level]["knowledge_total"]),
                "open_conclusion_accuracy": _ratio(by_level[level]["open_correct"], by_level[level]["open_total"]),
                "open_joint_accuracy": _ratio(by_level[level]["open_joint"], by_level[level]["open_total"]),
            }
            for level in LEVELS
        },
    }


def write_oracle_predictions(
    release_dir: Path, output_path: Path, *, test_only: bool
) -> dict[str, Any]:
    if not test_only:
        raise ValueError("oracle export requires test_only=True")
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    records: list[str] = []
    for match_id in summary["match_ids"]:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        record = {
            "instance_id": match_id,
            "knowledge_predictions": [
                {
                    "question_id": item["question_id"],
                    "answer_code": item["answer_code"],
                    "reasoning_atoms": item["required_atoms"],
                    "decisive_spans": item.get("decisive_evidence_spans", []),
                    "misleading_spans": item.get("misleading_evidence_spans", []),
                    "explanation": "TEST_ONLY_ORACLE",
                    "confidence": 1.0,
                }
                for item in gold["knowledge_answers"]
            ],
            "open_qa_predictions": [
                {
                    "question_id": item["question_id"],
                    "conclusion_value": item["conclusion_value"],
                    "reasoning_atoms": item["required_atoms"],
                    "decisive_spans": item["decisive_evidence"]["spans"],
                    "decisive_edges": item["decisive_evidence"]["edges"],
                    "provenance_spans": item["provenance_context"]["spans"],
                    "provenance_edges": item["provenance_context"]["edges"],
                    "explanation": "TEST_ONLY_ORACLE",
                    "confidence": 1.0,
                }
                for item in gold["open_qa_answers"]
            ],
        }
        records.append(json.dumps(record, ensure_ascii=False, sort_keys=True))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(records) + "\n", encoding="utf-8")
    return {"status": "COMPLETE", "instances": len(records), "output": str(output_path), "test_only": True}


__all__ = ["score_predictions", "write_oracle_predictions"]
