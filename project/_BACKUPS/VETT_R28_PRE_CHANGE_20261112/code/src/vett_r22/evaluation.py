from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .spec import LEVELS, TARGET_FAMILIES


def _ratio(a: int | float, b: int | float) -> float:
    return round(a / b, 6) if b else 0.0


def _edge(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (str(edge.get("from_span")), str(edge.get("relation")), str(edge.get("to_span")))


def _prf(counts: Counter[str]) -> dict[str, Any]:
    precision = _ratio(counts["tp"], counts["tp"] + counts["fp"])
    recall = _ratio(counts["tp"], counts["tp"] + counts["fn"])
    f1 = _ratio(2 * precision * recall, precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, **dict(counts)}


def _items(value: Any, id_key: str) -> dict[str, dict[str, Any]]:
    if isinstance(value, dict):
        value = [dict(item, **{id_key: key}) if isinstance(item, dict) else {id_key: key, "value": item} for key, item in value.items()]
    if not isinstance(value, list):
        return {}
    return {str(item[id_key]): item for item in value if isinstance(item, dict) and id_key in item}


def _load(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        instance_id = item.get("instance_id")
        if not isinstance(instance_id, str) or instance_id in result:
            raise ValueError(f"invalid or duplicate instance at line {number}")
        result[instance_id] = {
            "table": _items(item.get("table_predictions", []), "target_id"),
            "probe": _items(item.get("probe_predictions", []), "probe_id"),
        }
    return result


def score_predictions(
    release_dir: Path,
    predictions_path: Path,
    instance_ids: list[str] | None = None,
) -> dict[str, Any]:
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    submitted = _load(predictions_path)
    table = Counter()
    probe_answer = Counter()
    decisive_span = Counter()
    decisive_edge = Counter()
    provenance_span = Counter()
    provenance_edge = Counter()
    asp = Counter()
    matrix: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    confidence_sum = 0.0
    confidence_count = 0
    selected_ids = instance_ids if instance_ids is not None else summary["match_ids"]
    for match_id in selected_ids:
        gold = json.loads((release_dir / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
        prediction = submitted.get(match_id, {"table": {}, "probe": {}})
        for target in gold["table_targets"]:
            table["total"] += 1
            item = prediction["table"].get(target["target_id"])
            correct = item is not None and str(item.get("value", "")) == str(target["value"])
            table["correct"] += int(correct)
            table["missing"] += int(item is None)
        for target in gold["probes"]:
            item = prediction["probe"].get(target["probe_id"])
            answer_ok = item is not None and str(item.get("value", "")) == str(target["value"])
            probe_answer["total"] += 1
            probe_answer["correct"] += int(answer_ok)
            probe_answer["missing"] += int(item is None)
            bucket = matrix[(target["level"], target["target_family"])]
            bucket["total"] += 1
            bucket["correct"] += int(answer_ok)
            predicted_ds = set(map(str, item.get("decisive_spans", []))) if item else set()
            predicted_de = {_edge(edge) for edge in item.get("decisive_edges", []) if isinstance(edge, dict)} if item else set()
            predicted_ps = set(map(str, item.get("provenance_spans", []))) if item else set()
            predicted_pe = {_edge(edge) for edge in item.get("provenance_edges", []) if isinstance(edge, dict)} if item else set()
            gold_ds = set(target["decisive_evidence"]["spans"])
            gold_de = {_edge(edge) for edge in target["decisive_evidence"]["edges"]}
            gold_ps = set(target["provenance_context"]["spans"])
            gold_pe = {_edge(edge) for edge in target["provenance_context"]["edges"]}
            for counts, predicted_set, gold_set in (
                (decisive_span, predicted_ds, gold_ds),
                (decisive_edge, predicted_de, gold_de),
                (provenance_span, predicted_ps, gold_ps),
                (provenance_edge, predicted_pe, gold_pe),
            ):
                counts["tp"] += len(predicted_set & gold_set)
                counts["fp"] += len(predicted_set - gold_set)
                counts["fn"] += len(gold_set - predicted_set)
            proof_exact = predicted_ds == gold_ds and predicted_de == gold_de
            asp["total"] += 1
            asp["correct"] += int(answer_ok and proof_exact)
            bucket["asp_correct"] += int(answer_ok and proof_exact)
            if item is not None and isinstance(item.get("confidence"), (int, float)):
                confidence = min(1.0, max(0.0, float(item["confidence"])))
                confidence_sum += (confidence - float(answer_ok)) ** 2
                confidence_count += 1

    matrix_report = {
        f"{level}|{family}": {
            "correct": matrix[(level, family)]["correct"],
            "total": matrix[(level, family)]["total"],
            "accuracy": _ratio(matrix[(level, family)]["correct"], matrix[(level, family)]["total"]),
            "asp_correct": matrix[(level, family)]["asp_correct"],
            "asp_accuracy": _ratio(matrix[(level, family)]["asp_correct"], matrix[(level, family)]["total"]),
        }
        for level in LEVELS for family in TARGET_FAMILIES
    }
    level_fam = {
        level: round(sum(matrix_report[f"{level}|{family}"]["accuracy"] for family in TARGET_FAMILIES) / len(TARGET_FAMILIES), 6)
        for level in LEVELS
    }
    level_asp = {
        level: round(sum(matrix_report[f"{level}|{family}"]["asp_accuracy"] for family in TARGET_FAMILIES) / len(TARGET_FAMILIES), 6)
        for level in LEVELS
    }
    family_fam = {
        family: round(sum(matrix_report[f"{level}|{family}"]["accuracy"] for level in LEVELS) / len(LEVELS), 6)
        for family in TARGET_FAMILIES
    }
    family_asp = {
        family: round(sum(matrix_report[f"{level}|{family}"]["asp_accuracy"] for level in LEVELS) / len(LEVELS), 6)
        for family in TARGET_FAMILIES
    }
    adjacent_level_gaps = {
        f"{LEVELS[index]}->{LEVELS[index + 1]}": round(level_fam[LEVELS[index]] - level_fam[LEVELS[index + 1]], 6)
        for index in range(len(LEVELS) - 1)
    }
    fam = round(sum(level_fam.values()) / len(LEVELS), 6)
    return {
        "dataset_version": summary["dataset_version"],
        "expected_instances": len(selected_ids),
        "submitted_instances": len(submitted),
        "table_cell_exact": {"correct": table["correct"], "total": table["total"], "accuracy": _ratio(table["correct"], table["total"])},
        "probe_answer_exact": {"correct": probe_answer["correct"], "total": probe_answer["total"], "accuracy": _ratio(probe_answer["correct"], probe_answer["total"])},
        "fact_answer_matrix": matrix_report,
        "level_fam": level_fam,
        "level_asp": level_asp,
        "family_fam": family_fam,
        "family_asp": family_asp,
        "adjacent_level_gaps": adjacent_level_gaps,
        "minimum_adjacent_level_gap": min(adjacent_level_gaps.values()),
        "adjacent_gap_target": 0.08,
        "adjacent_gap_pass": all(gap >= 0.08 for gap in adjacent_level_gaps.values()),
        "fam": fam,
        "asp_exact": {"correct": asp["correct"], "total": asp["total"], "accuracy": _ratio(asp["correct"], asp["total"])},
        "decisive_span_micro": _prf(decisive_span),
        "decisive_edge_micro": _prf(decisive_edge),
        "provenance_span_micro": _prf(provenance_span),
        "provenance_edge_micro": _prf(provenance_edge),
        "brier": round(confidence_sum / confidence_count, 6) if confidence_count else None,
        "confidence_items": confidence_count,
        "missing_table_targets": table["missing"],
        "missing_probes": probe_answer["missing"],
    }


__all__ = ["score_predictions"]
