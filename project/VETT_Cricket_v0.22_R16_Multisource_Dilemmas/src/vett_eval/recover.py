from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .runner import (
    DECISION_TASKS,
    KNOWLEDGE_TASKS,
    _cost_cny,
    _extract_chat_text,
    _evidence_relations_by_target,
    _normalize_response,
    _parse_json_with_closure_repair,
    _public_span_ids,
    _request_record,
    _request_sha256,
    _task_type,
    _usage_summary,
    _write_json,
)


def recover_chat_raw(
    config_path: Path,
    *,
    run_id: str,
    instance_id: str,
    batch_index: int = 0,
) -> dict[str, Any]:
    """Validate a saved chat response and promote it to a resumable checkpoint.

    This function never contacts the provider.  It is intended for narrowly
    repairable JSON suffix truncation and refuses recovery unless the normal
    schema/target-ID validation path reports zero errors.
    """
    config = json.loads(config_path.read_text(encoding="utf-8"))
    specs = [spec for spec in config.get("runs", []) if spec.get("run_id") == run_id]
    if len(specs) != 1:
        raise ValueError(f"expected exactly one run spec for {run_id}, found {len(specs)}")
    spec = specs[0]
    if spec.get("adapter") != "openai_chat_completions":
        raise ValueError("raw recovery only supports openai_chat_completions")

    release_dir = Path(config["release_dir"])
    output_root = Path(config["output_dir"])
    run_dir = output_root / run_id
    summary = json.loads((release_dir / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))
    task_type = _task_type(summary)
    public = json.loads(
        (release_dir / "public" / instance_id / "public_instance.json").read_text(encoding="utf-8")
    )
    targets = (
        public["decision_question_schema"]
        if task_type in DECISION_TASKS
        else public["knowledge_question_schema"]
        if task_type in KNOWLEDGE_TASKS
        else public["probe_schema"]
        if task_type == "r22"
        else public["target_schema"]
    )
    batch_size = int(spec.get("target_batch_size", 0)) or len(targets)
    batches = [targets[index : index + batch_size] for index in range(0, len(targets), batch_size)]
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError(f"batch index {batch_index} is outside 0..{len(batches) - 1}")
    target_batch = batches[batch_index]
    request_record = _request_record(
        release_dir,
        public,
        target_batch,
        batch_index,
        task_type,
        input_ablation=spec.get("input_ablation"),
    )

    raw_path = run_dir / "raw" / instance_id / f"batch_{batch_index:03d}.json"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    output_text = _extract_chat_text(raw)
    parsed, suffix = _parse_json_with_closure_repair(output_text)
    if not suffix:
        raise ValueError("saved response does not require closure repair")
    allowed = set(request_record["target_ids"])
    normalized, validation_errors = _normalize_response(
        parsed,
        instance_id,
        allowed,
        task_type,
        evidence_span_ids=(
            _public_span_ids(public) if task_type == "r26_decision" else None
        ),
        evidence_relations_by_target=(
            _evidence_relations_by_target(target_batch)
            if task_type == "r26_decision"
            else None
        ),
    )
    if validation_errors or set(normalized) != allowed:
        raise ValueError(f"recovered response failed validation: {validation_errors}")

    original_parse_error = raw.pop("vett_parse_error", None)
    raw["vett_json_repair"] = {
        "strategy": "append_missing_closing_delimiters",
        "appended_suffix": suffix,
        "original_characters": len(output_text),
        "trimmed_characters": len(output_text.rstrip()),
        "original_parse_error": original_parse_error,
        "validated_target_ids": sorted(allowed),
    }
    usage = _usage_summary(raw)
    batch_record = {
        "batch_index": batch_index,
        "requested_targets": len(target_batch),
        "returned_targets": len(normalized),
        "attempts": 1,
        "status": "OK",
        "validation_errors": [],
        "elapsed_seconds": 0.0,
        "usage": usage,
        "actual_cost_cny": _cost_cny(usage, spec),
        "resumed_from_checkpoint": False,
        "recovered_from_saved_raw": True,
        "json_repair_suffix": suffix,
    }
    checkpoint_path = run_dir / "checkpoints" / instance_id / f"batch_{batch_index:03d}.json"
    _write_json(raw_path, raw)
    _write_json(
        checkpoint_path,
        {
            "protocol_version": "VETT-EVAL-CHECKPOINT-1",
            "request_sha256": _request_sha256(request_record, spec),
            "predictions": normalized,
            "batch_record": batch_record,
        },
    )
    return {
        "status": "RECOVERED",
        "run_id": run_id,
        "instance_id": instance_id,
        "batch_index": batch_index,
        "appended_suffix": suffix,
        "validated_targets": len(normalized),
        "checkpoint": str(checkpoint_path),
        "provider_requests": 0,
    }


__all__ = ["recover_chat_raw"]
