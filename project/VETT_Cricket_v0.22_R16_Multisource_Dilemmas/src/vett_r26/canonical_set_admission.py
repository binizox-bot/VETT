from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_canonical_set_admission(
    preflight_path: Path,
    replay_path: Path,
    blocked_config_path: Path,
    metric_addendum_path: Path,
    request_contract_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    preflight = _read(preflight_path)
    replay = _read(replay_path)
    config = _read(blocked_config_path)
    metric_addendum = _read(metric_addendum_path)
    request_contract = _read(request_contract_path)
    all_preflight_gates_pass = bool(preflight.get("gates")) and all(
        preflight["gates"].values()
    )
    gates = {
        "prospective_metric_contract_frozen": metric_addendum.get("status")
        == "PREREGISTERED_PROSPECTIVE_ONLY",
        "request_contract_uses_canonical_set": request_contract.get(
            "generation_contract", {}
        ).get("r26_evidence_set_protocol")
        == "canonical_set_v2",
        "blocked_config_uses_canonical_set": config.get("runs", [{}])[0].get(
            "r26_evidence_set_protocol"
        )
        == "canonical_set_v2",
        "external_execution_remains_blocked": config.get("execution_authorized")
        is False,
        "zero_request_preflight_ready": preflight.get("status")
        == "REQUEST_READY_BLOCKED_BY_AUTHORIZATION",
        "all_preflight_gates_pass": all_preflight_gates_pass,
        "canonical_duplicate_fault_injection_passes": preflight.get(
            "gates", {}
        ).get("canonical_duplicate_probe_passes_when_required")
        is True,
        "preflight_sent_no_provider_requests": preflight.get(
            "provider_requests_made"
        )
        == 0,
        "posthoc_replay_remains_non_official": replay.get("status")
        == "NON_OFFICIAL_POST_HOC_REPLAY"
        and replay.get("official_score") is False,
        "historical_invalid_status_preserved": replay.get(
            "source_official_status_preserved"
        )
        == "INVALID_OUTPUT",
        "prospective_request_is_new": replay.get("prospective_request_differs")
        is True,
        "set_semantic_score_is_duplicate_invariant": replay.get(
            "set_semantic_score_invariant_before_after_canonicalization"
        )
        is True,
        "replay_sent_no_provider_requests": replay.get("provider_requests_made")
        == 0,
        "dataset_unchanged": replay.get("dataset_bytes_changed") is False,
    }
    status = (
        "LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED"
        if all(gates.values())
        else "LOCAL_PROTOCOL_NOT_READY"
    )
    report = {
        "protocol_version": "VETT-R26.18-CANONICAL-SET-ADMISSION-1",
        "status": status,
        "gates": gates,
        "dataset_candidate": "r26_15_content_dependency_candidate_v3",
        "dataset_mutation_authorized": False,
        "external_execution_authorized": False,
        "provider_requests_made_by_r26_18": 0,
        "estimated_future_sentinel5_cost_cny_zero_cache": preflight.get(
            "estimated_cost_cny_zero_cache"
        ),
        "maximum_future_cost_cny": config.get(
            "max_estimated_total_cost_cny"
        ),
        "local_replay": {
            "source_status": replay.get("source_official_status_preserved"),
            "affected_questions": replay.get("output_conformance", {}).get(
                "affected_questions"
            ),
            "question_conformance_rate": replay.get(
                "output_conformance", {}
            ).get("question_conformance_rate"),
            "duplicate_groups": replay.get("output_conformance", {}).get(
                "duplicate_groups"
            ),
            "redundant_count": replay.get("output_conformance", {}).get(
                "redundant_count"
            ),
            "semantic_score_invariant": replay.get(
                "set_semantic_score_invariant_before_after_canonicalization"
            ),
        },
        "artifact_sha256": {
            "preflight": _sha256(preflight_path),
            "replay": _sha256(replay_path),
            "blocked_config": _sha256(blocked_config_path),
            "metric_addendum": _sha256(metric_addendum_path),
            "request_contract": _sha256(request_contract_path),
        },
        "decision": {
            "retain_r26_15_dataset_bytes": True,
            "retain_historical_r26_17_statuses": True,
            "adopt_canonical_set_v2_for_future_requests": all(gates.values()),
            "automatically_run_provider": False,
            "merge_with_old_protocol_runs": False,
            "next_action": (
                "Only after separate explicit cost authorization, create an authorized "
                "copy of the frozen five-match config. Otherwise stop: local protocol "
                "work is complete and no dataset hardening is justified by this replay."
            ),
        },
        "claim_boundary": (
            "Local admission validates attribution and reproducibility, not empirical "
            "difficulty. The future five-match run remains unexecuted and blocked."
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-canonical-set-admission")
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--blocked-config", type=Path, required=True)
    parser.add_argument("--metric-addendum", type=Path, required=True)
    parser.add_argument("--request-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_canonical_set_admission(
        args.preflight,
        args.replay,
        args.blocked_config,
        args.metric_addendum,
        args.request_contract,
        args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_canonical_set_admission"]
