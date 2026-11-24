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


def _manifest_errors(release_dir: Path) -> list[str]:
    manifest = _read(release_dir / "MANIFEST.json")
    errors: list[str] = []
    entries = manifest.get("files", [])
    if manifest.get("file_count_excluding_manifest") != len(entries):
        errors.append("manifest_file_count_mismatch")
    for entry in entries:
        relative = Path(str(entry["path"]))
        path = release_dir / relative
        if not path.is_file():
            errors.append(f"missing:{relative.as_posix()}")
            continue
        if path.stat().st_size != int(entry["bytes"]):
            errors.append(f"bytes:{relative.as_posix()}")
        if _sha256(path) != str(entry["sha256"]):
            errors.append(f"sha256:{relative.as_posix()}")
    return errors


def build_protocol_citation_admission(
    release_dir: Path,
    prereg_path: Path,
    metric_addendum_path: Path,
    citation_audit_path: Path,
    replay_path: Path,
    preflight_path: Path,
    blocked_config_path: Path,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Admit local protocol plumbing without claiming empirical model validity."""
    prereg = _read(prereg_path)
    metric = _read(metric_addendum_path)
    citation = _read(citation_audit_path)
    replay = _read(replay_path)
    preflight = _read(preflight_path)
    config = _read(blocked_config_path)
    summary = _read(release_dir / "RELEASE_SUMMARY.json")
    manifest_errors = _manifest_errors(release_dir)

    gates = {
        "release_static_status_pass": summary.get("status") == "PASS",
        "release_empirical_status_still_not_run": summary.get(
            "empirical_calibration", {}
        ).get("status")
        == "NOT_RUN",
        "release_manifest_bytes_unchanged": not manifest_errors,
        "unknown_evidence_policy_preregistered": (
            prereg.get("frozen_before_implementation") is True
            and prereg.get("scope", {}).get("new_unknown_evidence_protocol")
            == "semantic_false_positive_v2"
            and prereg.get("external_request_authorization") is False
        ),
        "unknown_evidence_metric_frozen_pre_edge7": (
            metric.get("status") == "FROZEN_BEFORE_ANY_EDGE7_PROVIDER_RESULT"
            and metric.get("primary_metrics_unchanged") is True
            and metric.get("provider_requests_made") == 0
        ),
        "citation_stability_audit_pass": (
            citation.get("status") == "PASS_KEEP_DATASET_BYTES"
            and all(citation.get("gates", {}).values())
            and citation.get("counts", {}).get("substitution_collisions") == 0
        ),
        "counterfactual_replay_is_nonofficial": (
            replay.get("status") == "COUNTERFACTUAL_POLICY_DIAGNOSTIC_ONLY"
            and replay.get("official_score") is False
            and replay.get("source_official_status") == "INVALID_OUTPUT"
            and replay.get("source_status_unchanged") is True
        ),
        "edge7_preflight_ready_but_blocked": (
            preflight.get("status") == "REQUEST_READY_BLOCKED_BY_AUTHORIZATION"
            and preflight.get("execution_authorized") is False
            and preflight.get("provider_requests_made") == 0
            and all(preflight.get("gates", {}).values())
        ),
        "edge7_semantic_protocol_bound": (
            preflight.get("r26_unknown_evidence_protocol")
            == "semantic_false_positive_v2"
            and preflight.get("instances") == 5
            and preflight.get("questions") == 25
        ),
        "provider_execution_config_blocked": (
            config.get("require_explicit_execution_authorization") is True
            and config.get("execution_authorized") is False
            and len(config.get("runs", [])) == 1
            and config["runs"][0].get("max_retries") == 0
        ),
        "no_provider_requests_in_r26_16_local_work": (
            metric.get("provider_requests_made") == 0
            and preflight.get("provider_requests_made") == 0
        ),
    }
    local_pass = all(gates.values())
    report = {
        "protocol_version": "VETT-R26.16-PROTOCOL-CITATION-ADMISSION-1",
        "dataset_version": summary.get("dataset_version"),
        "status": (
            "LOCAL_PROTOCOL_AND_CITATION_PASS_EMPIRICAL_EDGE7_BLOCKED"
            if local_pass
            else "LOCAL_PROTOCOL_AND_CITATION_FAIL"
        ),
        "gates": gates,
        "manifest_errors": manifest_errors,
        "dataset_bytes_changed_by_r26_16": False,
        "dataset_mutation_decision": (
            "KEEP_R26_15_DATASET_BYTES"
            if gates["citation_stability_audit_pass"]
            else "BLOCK_AND_INVESTIGATE"
        ),
        "provider_requests_made": 0,
        "external_execution_authorized": False,
        "empirical_edge7_run_completed": False,
        "paper_level_difficulty_claim_authorized": False,
        "next_permitted_action": (
            "request_new_explicit_authorization_for_exact_edge7_sentinel5_only"
            if local_pass
            else "repair_failed_local_gate_before_any_provider_request"
        ),
        "key_evidence": {
            "matches": summary.get("instances"),
            "questions": summary.get("decision_questions"),
            "public_spans_audited": citation.get("counts", {}).get(
                "public_spans"
            ),
            "gold_cited_unique_spans": citation.get("counts", {}).get(
                "gold_cited_unique_spans"
            ),
            "single_hex_substitutions_tested": citation.get("counts", {}).get(
                "substitutions_tested"
            ),
            "single_hex_substitution_collisions": citation.get("counts", {}).get(
                "substitution_collisions"
            ),
            "minimum_gold_to_other_public_hamming": citation.get(
                "minimum_gold_to_other_public_hamming_across_matches"
            ),
            "counterfactual_unknown_question_rate": replay.get(
                "counterfactual_scores", {}
            ).get("unknown_evidence_question_rate"),
            "sentinel5_estimated_cost_cny_zero_cache": preflight.get(
                "estimated_cost_cny_zero_cache"
            ),
            "sentinel5_context_utilization_upper_bound": preflight.get(
                "maximum_context_utilization_upper_bound"
            ),
            "sentinel5_minimum_oracle_output_headroom_ratio": preflight.get(
                "minimum_oracle_output_headroom_ratio"
            ),
        },
        "input_sha256": {
            "release_manifest": _sha256(release_dir / "MANIFEST.json"),
            "preregistration": _sha256(prereg_path),
            "metric_addendum": _sha256(metric_addendum_path),
            "citation_audit": _sha256(citation_audit_path),
            "counterfactual_replay": _sha256(replay_path),
            "sentinel5_preflight": _sha256(preflight_path),
            "blocked_config": _sha256(blocked_config_path),
        },
        "claim_boundary": (
            "This admission establishes local integrity, scoring attribution, citation "
            "stability, and request readiness only. It provides no new model result, no "
            "empirical five-level calibration, and no authorization to spend money."
        ),
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-r26-protocol-citation-admission")
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--metric-addendum", type=Path, required=True)
    parser.add_argument("--citation-audit", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--blocked-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build_protocol_citation_admission(
        args.release,
        args.prereg,
        args.metric_addendum,
        args.citation_audit,
        args.replay,
        args.preflight,
        args.blocked_config,
        args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = ["build_protocol_citation_admission"]
