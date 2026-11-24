from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def aggregate_runs(run_dirs: list[Path], output_dir: Path) -> dict[str, Any]:
    if len(run_dirs) < 2:
        raise ValueError("at least two run directories are required")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"aggregate output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_items = [
        json.loads((run_dir / "RUN_METADATA.json").read_text(encoding="utf-8"))
        for run_dir in run_dirs
    ]
    task_types = {item.get("task_type") for item in metadata_items}
    models = {item.get("model") for item in metadata_items}
    releases = {item.get("release_dir") for item in metadata_items}
    if len(task_types) != 1 or len(models) != 1 or len(releases) != 1:
        raise ValueError("source runs must use the same task type, model, and release")

    ordered_ids: list[str] = []
    predictions: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    record_sources: dict[str, str] = {}
    excluded_failures: list[dict[str, Any]] = []
    for run_dir, metadata in zip(run_dirs, metadata_items):
        for record in metadata.get("records", []):
            instance_id = record["instance_id"]
            if instance_id not in ordered_ids:
                ordered_ids.append(instance_id)
            previous = records.get(instance_id)
            if previous is not None:
                for batch in previous.get("batches", []):
                    if batch.get("status") == "ERROR":
                        excluded_failures.append(
                            {
                                "instance_id": instance_id,
                                "source_run": record_sources[instance_id],
                                "error": batch.get("error"),
                                "elapsed_seconds": batch.get("elapsed_seconds"),
                            }
                        )
            records[instance_id] = record
            record_sources[instance_id] = str(run_dir.resolve())
        for prediction in _jsonl(run_dir / "predictions.jsonl"):
            predictions[prediction["instance_id"]] = prediction

    prediction_path = output_dir / "predictions.jsonl"
    prediction_path.write_text(
        "".join(
            json.dumps(predictions[instance_id], ensure_ascii=False, sort_keys=True) + "\n"
            for instance_id in ordered_ids
        ),
        encoding="utf-8",
    )
    ordered_records = [records[instance_id] for instance_id in ordered_ids]
    usage = {
        key: sum(
            int(batch.get("usage", {}).get(key, 0))
            for record in ordered_records
            for batch in record.get("batches", [])
        )
        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "total_tokens")
    }
    costs = [
        float(batch["actual_cost_cny"])
        for record in ordered_records
        for batch in record.get("batches", [])
        if batch.get("actual_cost_cny") is not None
    ]
    first = metadata_items[0]
    metadata = {
        "protocol_version": "VETT-EVAL-AGGREGATE-1",
        "run_id": output_dir.name,
        "adapter": first.get("adapter"),
        "model": first.get("model"),
        "release_dir": first.get("release_dir"),
        "instances": len(ordered_ids),
        "task_type": first.get("task_type"),
        "test_only": False,
        "source_runs": [str(path.resolve()) for path in run_dirs],
        "records": ordered_records,
        "actual_usage": usage,
        "actual_cost_cny": round(sum(costs), 6),
        "excluded_failed_attempts": excluded_failures,
    }
    (output_dir / "RUN_METADATA.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "status": "COMPLETE",
        "run_dir": str(output_dir),
        "instances": len(ordered_ids),
        "excluded_failed_attempts": len(excluded_failures),
    }


__all__ = ["aggregate_runs"]
