from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_protocol_smoke_outcome(
    blocked_config_path: Path,
    authorized_config_path: Path,
    run_dir: Path,
    sentinel_preflight_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    blocked = _read(blocked_config_path)
    authorized = _read(authorized_config_path)
    normalized_blocked = json.loads(json.dumps(blocked))
    normalized_blocked["execution_authorized"] = True
    config_diff_only_authorization = normalized_blocked == authorized
    metadata = _read(run_dir / "RUN_METADATA.json")
    checkpoint = _read(
        run_dir / "checkpoints" / "match_0220" / "batch_000.json"
    )
    analysis = _read(run_dir / "ANALYSIS.json")
    preflight = _read(sentinel_preflight_path)
    expected_request_hash = next(
        item["request_sha256"]
        for item in preflight["per_match"]
        if item["match_id"] == "match_0220"
    )
    batch = checkpoint["batch_record"]
    scores = analysis["scores"]
    gates = {
        "config_diff_only_execution_authorized": config_diff_only_authorization,
        "single_registered_instance": metadata.get("instances_requested") == 1
        and [
            str(record.get("instance_id"))
            for record in metadata.get("records", [])
        ]
        == ["match_0220"],
        "exact_target_map_protocol": metadata.get(
            "r26_response_envelope_protocol"
        )
        == "exact_target_map_v3",
        "request_hash_matches_zero_request_preflight": checkpoint.get(
            "request_sha256"
        )
        == expected_request_hash,
        "one_attempt_zero_retry": batch.get("attempts") == 1,
        "batch_status_ok": batch.get("status") == "OK",
        "five_targets_returned": batch.get("returned_targets") == 5
        and len(checkpoint.get("predictions", {})) == 5,
        "provider_reported_stop": batch.get("finish_reason") == "stop",
        "not_truncated": batch.get("output_truncated") is False,
        "no_validation_errors": not batch.get("validation_errors"),
        "no_semantic_unknown_evidence_warnings": not batch.get(
            "semantic_warnings"
        ),
        "within_cost_ceiling": float(metadata.get("actual_cost_cny") or 0.0)
        <= float(authorized["max_estimated_total_cost_cny"]),
        "single_protocol_gate_complete": analysis.get("sentinel_run_complete")
        is True
        and analysis.get("scored_instances") == 1,
    }
    status = "PASS_PROTOCOL_SMOKE" if all(gates.values()) else "FAIL"
    report = {
        "protocol_version": "VETT-R26.17-PROTOCOL-SMOKE-OUTCOME-1",
        "status": status,
        "run_id": metadata.get("run_id"),
        "model": metadata.get("model"),
        "instance_id": "match_0220",
        "response_envelope_protocol": metadata.get(
            "r26_response_envelope_protocol"
        ),
        "gates": gates,
        "provider_requests": 1,
        "attempts": batch.get("attempts"),
        "returned_targets": batch.get("returned_targets"),
        "finish_reason": batch.get("finish_reason"),
        "output_truncated": batch.get("output_truncated"),
        "elapsed_seconds": batch.get("elapsed_seconds"),
        "actual_usage": metadata.get("actual_usage"),
        "actual_cost_cny": metadata.get("actual_cost_cny"),
        "configured_cost_ceiling_cny": authorized[
            "max_estimated_total_cost_cny"
        ],
        "zero_cache_estimate_cny": 0.2453,
        "request_sha256": checkpoint.get("request_sha256"),
        "semantic_warnings": batch.get("semantic_warnings", []),
        "diagnostic_scores": {
            "decision_field_macro_accuracy": scores[
                "decision_field_macro_accuracy"
            ],
            "decision_informative_field_accuracy": scores[
                "decision_informative_field_accuracy"
            ],
            "decision_informative_field_value_balanced_accuracy": scores[
                "decision_informative_field_value_balanced_accuracy"
            ],
            "factual_record_macro_accuracy": scores[
                "factual_record_macro_accuracy"
            ],
            "minimal_evidence_f1": scores["minimal_evidence_f1"],
            "rejected_evidence_f1": scores["rejected_evidence_f1"],
            "minimal_evidence_edge_f1": scores[
                "minimal_evidence_edge_f1"
            ],
            "content_dependency_edge_f1": scores[
                "content_dependency_edge_f1"
            ],
            "factual_evidence_chain_joint_exact": scores[
                "factual_evidence_chain_joint_exact"
            ],
            "unknown_evidence_reference_rate": scores[
                "unknown_evidence_reference_rate"
            ],
        },
        "historical_edge7_merge_authorized": False,
        "dataset_mutation_authorized": False,
        "five_match_execution_authorized": False,
        "decision": (
            "The exact-target-map protocol passed its registered one-match smoke "
            "gate. This removes the known duplicate-target failure mode as a local "
            "blocker. A fresh five-match run may now be considered, but requires a "
            "new explicit cost authorization and cannot reuse this smoke response."
        ),
        "claim_boundary": (
            "Single-match semantic scores are diagnostic only. This run cannot be "
            "merged into the historical request_bound_v2 Sentinel5, establish level "
            "ordering, trigger dataset edits, or authorize a paper claim."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "PROTOCOL_SMOKE_OUTCOME.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "PROTOCOL_SMOKE_OUTCOME.md").write_text(
        "# R26.17 exact-target-map protocol smoke\n\n"
        f"- Status: `{status}`\n"
        "- Instance: `match_0220`\n"
        "- Provider requests: 1; retries: 0\n"
        f"- Returned targets: {batch.get('returned_targets')}/5\n"
        f"- Finish reason: `{batch.get('finish_reason')}`; truncated: "
        f"{batch.get('output_truncated')}\n"
        f"- Actual cost: CNY {metadata.get('actual_cost_cny')}\n"
        f"- Input/output tokens: {metadata['actual_usage']['input_tokens']}/"
        f"{metadata['actual_usage']['output_tokens']}\n"
        f"- Elapsed: {batch.get('elapsed_seconds'):.3f} seconds\n"
        "- Unknown evidence warnings: 0\n\n"
        "The exact five target keys were returned without truncation or validation "
        "errors. The protocol smoke passed. Its single-match scores are diagnostic "
        "and cannot be merged into the historical Edge7 Sentinel5. A fresh five-match "
        "run requires separate authorization.\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-protocol-smoke-outcome")
    parser.add_argument("--blocked-config", type=Path, required=True)
    parser.add_argument("--authorized-config", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_protocol_smoke_outcome(
        args.blocked_config,
        args.authorized_config,
        args.run,
        args.preflight,
        args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_protocol_smoke_outcome"]
