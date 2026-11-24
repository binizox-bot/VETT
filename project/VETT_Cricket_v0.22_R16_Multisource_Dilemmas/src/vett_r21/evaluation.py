from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _ratio(a: int, b: int) -> float:
    return round(a / b, 6) if b else 0.0


def _prf(counts: Counter[str]) -> dict[str, Any]:
    precision = _ratio(counts["tp"], counts["tp"] + counts["fp"])
    recall = _ratio(counts["tp"], counts["tp"] + counts["fn"])
    f1 = round(2 * precision * recall / (precision + recall), 6) if precision + recall else 0.0
    return {
        "true_positive": counts["tp"],
        "false_positive": counts["fp"],
        "false_negative": counts["fn"],
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _edge_tuple(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (str(edge.get("from_span")), str(edge.get("relation")), str(edge.get("to_span")))


def _load(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        instance_id = record.get("instance_id")
        if not isinstance(instance_id, str) or instance_id in result:
            raise ValueError(f"invalid or duplicate instance at line {line_number}")
        items = record.get("predictions", [])
        if isinstance(items, dict):
            items = [dict(value, target_id=key) if isinstance(value, dict) else {"target_id": key, "value": value} for key, value in items.items()]
        if not isinstance(items, list):
            raise ValueError(f"predictions is not a list at line {line_number}")
        normalized: dict[str, dict[str, Any]] = {}
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("target_id"), str):
                continue
            normalized[item["target_id"]] = {
                "value": str(item.get("value", "")),
                "evidence_spans": [str(value) for value in item.get("evidence_spans", [])],
                "evidence_edges": [
                    {
                        "from_span": str(edge.get("from_span")),
                        "relation": str(edge.get("relation")),
                        "to_span": str(edge.get("to_span")),
                    }
                    for edge in item.get("evidence_edges", [])
                    if isinstance(edge, dict)
                ],
            }
        result[instance_id] = normalized
    return result


def score_predictions(
    release_dir: Path,
    predictions_path: Path,
    instance_ids: list[str] | None = None,
) -> dict[str, Any]:
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    expected_ids = instance_ids or summary["match_ids"]
    submitted = _load(predictions_path)
    answer = Counter()
    span_counts = Counter()
    edge_counts = Counter()
    by_mechanism: dict[str, Counter[str]] = defaultdict(Counter)
    group_answer: dict[tuple[str, ...], list[bool]] = defaultdict(list)
    group_joint: dict[tuple[str, ...], list[bool]] = defaultdict(list)
    categories = Counter()
    for match_id in expected_ids:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        predicted = submitted.get(match_id, {})
        expected_target_ids = {target["target_id"] for target in gold["targets"]}
        answer["extra"] += len(set(predicted) - expected_target_ids)
        for target in gold["targets"]:
            target_id = target["target_id"]
            item = predicted.get(target_id)
            answer["total"] += 1
            if item is None:
                answer["missing"] += 1
                value_correct = False
                predicted_spans: set[str] = set()
                predicted_edges: set[tuple[str, str, str]] = set()
                categories["MISSING_TARGET"] += 1
            else:
                value_correct = item["value"] == target["value"]
                predicted_spans = set(item["evidence_spans"])
                predicted_edges = {_edge_tuple(edge) for edge in item["evidence_edges"]}
            answer["correct"] += int(value_correct)
            gold_spans = set(target["required_evidence_spans"])
            gold_edges = {_edge_tuple(edge) for edge in target["required_edges"]}
            span_counts["tp"] += len(predicted_spans & gold_spans)
            span_counts["fp"] += len(predicted_spans - gold_spans)
            span_counts["fn"] += len(gold_spans - predicted_spans)
            edge_counts["tp"] += len(predicted_edges & gold_edges)
            edge_counts["fp"] += len(predicted_edges - gold_edges)
            edge_counts["fn"] += len(gold_edges - predicted_edges)
            span_exact = predicted_spans == gold_spans
            edge_exact = predicted_edges == gold_edges
            joint = value_correct and span_exact and edge_exact
            if item is not None:
                if value_correct and span_exact and edge_exact:
                    categories["FULLY_CORRECT"] += 1
                elif value_correct:
                    categories["ANSWER_RIGHT_EVIDENCE_WRONG"] += 1
                elif span_exact and edge_exact:
                    categories["ANSWER_WRONG_EVIDENCE_RIGHT"] += 1
                else:
                    categories["ANSWER_AND_EVIDENCE_WRONG"] += 1
            mechanism = target["mechanism"]
            by_mechanism[mechanism]["total"] += 1
            by_mechanism[mechanism]["answer_correct"] += int(value_correct)
            by_mechanism[mechanism]["span_exact"] += int(span_exact)
            by_mechanism[mechanism]["edge_exact"] += int(edge_exact)
            by_mechanism[mechanism]["joint_correct"] += int(joint)
            for key in (
                (match_id, target["table_id"], target["row_id"]),
                (match_id, target["table_id"]),
                (match_id,),
            ):
                group_answer[key].append(value_correct)
                group_joint[key].append(joint)

    def exact(groups: dict[tuple[str, ...], list[bool]], size: int) -> dict[str, Any]:
        selected = [values for key, values in groups.items() if len(key) == size]
        correct = sum(all(values) for values in selected)
        return {"correct": correct, "total": len(selected), "accuracy": _ratio(correct, len(selected))}

    return {
        "dataset_version": summary["dataset_version"],
        "expected_instances": len(expected_ids),
        "submitted_instances": len(submitted),
        "answer_cell_exact": {"correct": answer["correct"], "total": answer["total"], "accuracy": _ratio(answer["correct"], answer["total"])},
        "evidence_span_micro": _prf(span_counts),
        "evidence_edge_micro": _prf(edge_counts),
        "evidence_error_counts": {
            "missing_spans": span_counts["fn"],
            "extra_spans": span_counts["fp"],
            "missing_edges": edge_counts["fn"],
            "extra_edges": edge_counts["fp"],
        },
        "joint_target_exact": {"correct": categories["FULLY_CORRECT"], "total": answer["total"], "accuracy": _ratio(categories["FULLY_CORRECT"], answer["total"])},
        "answer_row_exact": exact(group_answer, 3),
        "answer_table_exact": exact(group_answer, 2),
        "answer_match_exact": exact(group_answer, 1),
        "joint_row_exact": exact(group_joint, 3),
        "joint_table_exact": exact(group_joint, 2),
        "joint_match_exact": exact(group_joint, 1),
        "missing_targets": answer["missing"],
        "extra_targets": answer["extra"],
        "outcome_categories": dict(sorted(categories.items())),
        "by_mechanism": {
            mechanism: {
                "total": counts["total"],
                "answer_accuracy": _ratio(counts["answer_correct"], counts["total"]),
                "span_set_exact": _ratio(counts["span_exact"], counts["total"]),
                "edge_set_exact": _ratio(counts["edge_exact"], counts["total"]),
                "joint_accuracy": _ratio(counts["joint_correct"], counts["total"]),
            }
            for mechanism, counts in sorted(by_mechanism.items())
        },
    }


__all__ = ["score_predictions"]
