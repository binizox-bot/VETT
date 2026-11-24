from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .repair import DUPLICATE_OF


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _load_predictions(path: Path) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            instance_id = record.get("instance_id")
            predictions = record.get("predictions")
            if not isinstance(instance_id, str) or not isinstance(predictions, dict):
                raise ValueError(f"invalid prediction record at line {line_number}")
            if instance_id in records:
                raise ValueError(f"duplicate prediction instance: {instance_id}")
            records[instance_id] = {
                str(key): str(value) for key, value in predictions.items()
            }
    return records


def score_predictions(
    release_dir: Path,
    predictions_path: Path,
    instance_ids: list[str] | None = None,
) -> dict[str, Any]:
    summary = json.loads(
        (release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
    )
    expected_ids = instance_ids or summary["match_ids"]
    unknown_requested = sorted(set(expected_ids) - set(summary["match_ids"]))
    if unknown_requested:
        raise ValueError(f"unknown requested instances: {unknown_requested}")
    submitted = _load_predictions(predictions_path)
    unknown_instances = sorted(set(submitted) - set(expected_ids))

    overall = Counter()
    macro_accuracies: list[float] = []
    grouped_correct: dict[tuple[str, ...], list[bool]] = defaultdict(list)
    depth_counts: dict[str, Counter[str]] = defaultdict(Counter)
    type_counts: dict[str, Counter[str]] = defaultdict(Counter)
    targets_by_instance: dict[str, list[dict[str, Any]]] = {}
    for match_id in expected_ids:
        gold = json.loads(
            (release_dir / "private" / match_id / "private_gold.json").read_text(
                encoding="utf-8"
            )
        )
        targets = gold["targets"]
        targets_by_instance[match_id] = targets
        predictions = submitted.get(match_id, {})
        expected_target_ids = {target["target_id"] for target in targets}
        overall["extra"] += len(set(predictions) - expected_target_ids)
        match_correct = 0
        for target in targets:
            target_id = target["target_id"]
            prediction = predictions.get(target_id)
            is_missing = prediction is None
            is_correct = prediction == target["value"]
            overall["total"] += 1
            overall["missing"] += int(is_missing)
            overall["correct"] += int(is_correct)
            match_correct += int(is_correct)
            grouped_correct[(match_id, target["table_id"], target["row_id"])].append(
                is_correct
            )
            grouped_correct[(match_id, target["table_id"])].append(is_correct)
            grouped_correct[(match_id,)].append(is_correct)
            depth = target["difficulty"]
            depth_counts[depth]["total"] += 1
            depth_counts[depth]["correct"] += int(is_correct)
            table_type = target["table_type"]
            type_counts[table_type]["total"] += 1
            type_counts[table_type]["correct"] += int(is_correct)
        macro_accuracies.append(_ratio(match_correct, len(targets)))

    def exact(prefix_length: int) -> dict[str, Any]:
        groups = [values for key, values in grouped_correct.items() if len(key) == prefix_length]
        correct = sum(all(values) for values in groups)
        return {"correct": correct, "total": len(groups), "accuracy": _ratio(correct, len(groups))}

    duplicate_pairs = 0
    duplicate_equal = 0
    for duplicate_id, source_id in DUPLICATE_OF.items():
        if duplicate_id not in expected_ids or source_id not in expected_ids:
            continue
        source_predictions = submitted.get(source_id, {})
        duplicate_predictions = submitted.get(duplicate_id, {})
        for target in targets_by_instance[duplicate_id]:
            duplicate_target = target["target_id"]
            source_target = duplicate_target.replace(duplicate_id, source_id, 1)
            if source_target in source_predictions and duplicate_target in duplicate_predictions:
                duplicate_pairs += 1
                duplicate_equal += int(
                    source_predictions[source_target]
                    == duplicate_predictions[duplicate_target]
                )

    return {
        "dataset_version": summary["dataset_version"],
        "submitted_instances": len(submitted),
        "expected_instances": len(expected_ids),
        "unknown_instances": unknown_instances,
        "micro_cell_exact": {
            "correct": overall["correct"],
            "total": overall["total"],
            "accuracy": _ratio(overall["correct"], overall["total"]),
        },
        "macro_match_cell_accuracy": round(
            sum(macro_accuracies) / len(macro_accuracies), 6
        )
        if macro_accuracies
        else 0.0,
        "row_exact": exact(3),
        "table_exact": exact(2),
        "match_exact": exact(1),
        "missing_cells": overall["missing"],
        "extra_cells": overall["extra"],
        "by_revision_depth": {
            name: {
                "correct": count["correct"],
                "total": count["total"],
                "accuracy": _ratio(count["correct"], count["total"]),
            }
            for name, count in sorted(depth_counts.items())
        },
        "by_table_type": {
            name: {
                "correct": count["correct"],
                "total": count["total"],
                "accuracy": _ratio(count["correct"], count["total"]),
            }
            for name, count in sorted(type_counts.items())
        },
        "duplicate_consistency": {
            "equal": duplicate_equal,
            "paired_predictions": duplicate_pairs,
            "accuracy": _ratio(duplicate_equal, duplicate_pairs),
        },
    }


__all__ = ["score_predictions"]
