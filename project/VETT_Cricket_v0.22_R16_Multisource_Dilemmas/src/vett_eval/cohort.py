from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from vett_r26.evaluation import score_predictions
from vett_r26.protocol_analysis import materialize_semantic_predictions

from .calibration_analysis import build_pilot20_bootstrap
from .metric_contract import (
    CALIBRATION_STAGE_INSTANCE_COUNTS,
    evaluate_calibration_stage,
    load_metric_contract,
)
from .runner import _request_record, _request_sha256


CORE_GENERATION_FIELDS = (
    "model",
    "enable_thinking",
    "thinking_budget",
    "temperature",
    "top_p",
    "target_batch_size",
    "input_ablation",
    "r26_evidence_role_protocol",
    "r26_unknown_evidence_protocol",
    "response_format_mode",
)
TRANSPORT_VARIANCE_FIELDS = (
    "max_tokens",
    "r26_response_envelope_protocol",
    "timeout_seconds",
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path_value: str, manifest_path: Path) -> Path:
    path = Path(path_value)
    if path.exists() or path.is_absolute():
        return path.resolve()
    return (manifest_path.resolve().parent / path).resolve()


def _run_spec(config_path: Path, run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    config = _read(config_path)
    matches = [spec for spec in config.get("runs", []) if str(spec["run_id"]) == run_id]
    if len(matches) != 1:
        raise ValueError(f"{config_path} must contain exactly one run_id={run_id}")
    return config, matches[0]


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _verify_request_equivalence(
    release_dir: Path,
    historical_release_dir: Path,
    run_dir: Path,
    spec: dict[str, Any],
    instance_ids: set[str],
) -> dict[str, Any]:
    """Prove that historical responses saw byte-equivalent semantic requests."""
    checked: list[dict[str, Any]] = []
    errors: list[str] = []
    for instance_id in sorted(instance_ids):
        public_path = release_dir / "public" / instance_id / "public_instance.json"
        historical_public_path = (
            historical_release_dir / "public" / instance_id / "public_instance.json"
        )
        if not public_path.is_file():
            errors.append(f"missing_release_instance:{instance_id}")
            continue
        if not historical_public_path.is_file():
            errors.append(f"missing_historical_release_instance:{instance_id}")
            continue
        public = _read(public_path)
        historical_public = _read(historical_public_path)
        targets = list(public["decision_question_schema"])
        historical_targets = list(historical_public["decision_question_schema"])
        batch_size = int(spec.get("target_batch_size", 0)) or len(targets)
        batches = [
            targets[index : index + batch_size]
            for index in range(0, len(targets), batch_size)
        ]
        historical_batches = [
            historical_targets[index : index + batch_size]
            for index in range(0, len(historical_targets), batch_size)
        ]
        if len(historical_batches) != len(batches):
            errors.append(f"request_batch_count_mismatch:{instance_id}")
            continue
        for batch_index, target_batch in enumerate(batches):
            checkpoint_path = (
                run_dir / "checkpoints" / instance_id / f"batch_{batch_index:03d}.json"
            )
            if not checkpoint_path.is_file():
                errors.append(
                    f"missing_request_checkpoint:{instance_id}:batch_{batch_index:03d}"
                )
                continue
            checkpoint = _read(checkpoint_path)
            historical_hash = str(checkpoint.get("request_sha256", ""))
            if not historical_hash:
                errors.append(
                    f"missing_request_sha256:{instance_id}:batch_{batch_index:03d}"
                )
                continue
            candidate_request = _request_record(
                release_dir,
                public,
                target_batch,
                batch_index,
                "r26_decision",
                input_ablation=spec.get("input_ablation"),
                edge_ontology_version=spec.get(
                    "r26_edge_ontology_version", "explicit_v2"
                ),
                evidence_role_protocol=spec.get(
                    "r26_evidence_role_protocol", "explicit_redundant_v2"
                ),
                response_envelope_protocol=spec.get(
                    "r26_response_envelope_protocol", "explicit_instance_v1"
                ),
                unknown_evidence_protocol=spec.get(
                    "r26_unknown_evidence_protocol", "batch_invalid_v1"
                ),
            )
            historical_request = _request_record(
                historical_release_dir,
                historical_public,
                historical_batches[batch_index],
                batch_index,
                "r26_decision",
                input_ablation=spec.get("input_ablation"),
                edge_ontology_version=spec.get(
                    "r26_edge_ontology_version", "explicit_v2"
                ),
                evidence_role_protocol=spec.get(
                    "r26_evidence_role_protocol", "explicit_redundant_v2"
                ),
                response_envelope_protocol=spec.get(
                    "r26_response_envelope_protocol", "explicit_instance_v1"
                ),
                unknown_evidence_protocol=spec.get(
                    "r26_unknown_evidence_protocol", "batch_invalid_v1"
                ),
            )
            reconstructed_historical_hash = _request_sha256(
                historical_request, spec
            )
            historical_reconstruction_match = (
                reconstructed_historical_hash == historical_hash
            )
            candidate_request["release_dir"] = "<RELEASE_DIR>"
            historical_request["release_dir"] = "<RELEASE_DIR>"
            candidate_semantic_hash = _request_sha256(candidate_request, spec)
            historical_semantic_hash = _request_sha256(historical_request, spec)
            semantic_match = candidate_semantic_hash == historical_semantic_hash
            checked.append({
                "instance_id": instance_id,
                "batch_index": batch_index,
                "historical_request_sha256": historical_hash,
                "reconstructed_historical_request_sha256": (
                    reconstructed_historical_hash
                ),
                "historical_reconstruction_match": (
                    historical_reconstruction_match
                ),
                "candidate_semantic_request_sha256": candidate_semantic_hash,
                "historical_semantic_request_sha256": historical_semantic_hash,
                "semantic_match": semantic_match,
            })
            if not historical_reconstruction_match:
                errors.append(
                    f"historical_request_reconstruction_mismatch:"
                    f"{instance_id}:batch_{batch_index:03d}"
                )
            if not semantic_match:
                errors.append(
                    f"semantic_request_hash_mismatch:"
                    f"{instance_id}:batch_{batch_index:03d}"
                )
    return {
        "status": "PASS" if not errors and checked else "FAIL",
        "errors": errors,
        "verified_batches": len(checked),
        "checks": checked,
    }


def analyze_calibration_cohorts(manifest_path: Path) -> dict[str, Any]:
    """Combine compatible, already-run artifacts without making model requests."""
    manifest = _read(manifest_path)
    release_dir = _resolve(str(manifest["release_dir"]), manifest_path)
    contract_path = _resolve(str(manifest["metric_contract"]), manifest_path)
    output_root = _resolve(str(manifest["output_dir"]), manifest_path)
    contract = load_metric_contract(contract_path)
    output_root.mkdir(parents=True, exist_ok=True)
    cohort_reports: list[dict[str, Any]] = []

    for cohort in manifest.get("cohorts", []):
        cohort_id = str(cohort["cohort_id"])
        stage = str(cohort["calibration_stage"])
        if stage not in CALIBRATION_STAGE_INSTANCE_COUNTS:
            raise ValueError(f"unsupported cohort calibration stage: {stage}")
        expected_instances = CALIBRATION_STAGE_INSTANCE_COUNTS[stage]
        cohort_dir = output_root / cohort_id
        cohort_dir.mkdir(parents=True, exist_ok=True)
        expected_model = str(cohort["model"])
        allowed_evidence = set(map(str, cohort["allowed_evidence_role_protocols"]))
        allowed_envelopes = set(map(str, cohort["allowed_response_envelope_protocols"]))
        allowed_unknown_evidence = set(map(str, cohort.get(
            "allowed_unknown_evidence_protocols", ["batch_invalid_v1"]
        )))
        issues: list[str] = []
        missing_members: list[str] = []
        combined_rows: dict[str, dict[str, Any]] = {}
        core_fingerprints: dict[str, dict[str, Any]] = {}
        transport_profiles: list[dict[str, Any]] = []
        status_counts: Counter[str] = Counter()
        stopped_early = False
        total_cost = 0.0
        member_reports: list[dict[str, Any]] = []

        for member in cohort.get("members", []):
            run_id = str(member["run_id"])
            run_dir = _resolve(str(member["run_dir"]), manifest_path)
            source_config = _resolve(str(member["source_config"]), manifest_path)
            intended_ids = set(map(str, member["instance_ids"]))
            metadata_path = run_dir / "RUN_METADATA.json"
            if not metadata_path.is_file():
                missing_members.append(run_id)
                member_reports.append({
                    "run_id": run_id,
                    "status": "NOT_RUN",
                    "intended_instance_ids": sorted(intended_ids),
                })
                continue
            metadata = _read(metadata_path)
            config, spec = _run_spec(source_config, run_id)
            actual_model = str(metadata.get("model", spec.get("model")))
            if actual_model != expected_model:
                issues.append(f"model_mismatch:{run_id}:{actual_model}")
            evidence_protocol = str(metadata.get(
                "r26_evidence_role_protocol",
                spec.get("r26_evidence_role_protocol", "explicit_redundant_v2"),
            ))
            envelope_protocol = str(metadata.get(
                "r26_response_envelope_protocol",
                spec.get("r26_response_envelope_protocol", "explicit_instance_v1"),
            ))
            unknown_evidence_protocol = str(metadata.get(
                "r26_unknown_evidence_protocol",
                spec.get("r26_unknown_evidence_protocol", "batch_invalid_v1"),
            ))
            if evidence_protocol not in allowed_evidence:
                issues.append(f"evidence_protocol:{run_id}:{evidence_protocol}")
            if envelope_protocol not in allowed_envelopes:
                issues.append(f"response_envelope:{run_id}:{envelope_protocol}")
            if unknown_evidence_protocol not in allowed_unknown_evidence:
                issues.append(
                    f"unknown_evidence_protocol:{run_id}:{unknown_evidence_protocol}"
                )
            core = {
                field: spec.get(field)
                for field in CORE_GENERATION_FIELDS
                if field not in {
                    "model", "input_ablation", "r26_evidence_role_protocol",
                    "r26_unknown_evidence_protocol"
                }
            }
            core.update({
                "model": actual_model,
                "input_ablation": spec.get("input_ablation", "full_input"),
                "r26_evidence_role_protocol": evidence_protocol,
                "r26_unknown_evidence_protocol": unknown_evidence_protocol,
            })
            core_fingerprints[run_id] = core
            transport_profiles.append({
                "run_id": run_id,
                **{
                    field: (
                        envelope_protocol
                        if field == "r26_response_envelope_protocol"
                        else spec.get(field)
                    )
                    for field in TRANSPORT_VARIANCE_FIELDS
                },
            })
            protocol = materialize_semantic_predictions(release_dir, run_dir)
            request_equivalence = _verify_request_equivalence(
                release_dir,
                Path(str(metadata["release_dir"])).resolve(),
                run_dir,
                spec,
                intended_ids,
            )
            if request_equivalence["status"] != "PASS":
                issues.extend(
                    f"request_equivalence:{run_id}:{error}"
                    for error in request_equivalence["errors"]
                )
            actual_ids = set(map(str, protocol.get("scored_instance_ids", [])))
            if protocol.get("status") != "COMPLETE_SEMANTIC_COVERAGE":
                issues.append(f"protocol_status:{run_id}:{protocol.get('status')}")
            if actual_ids != intended_ids:
                issues.append(
                    f"instance_set:{run_id}:expected={sorted(intended_ids)}:actual={sorted(actual_ids)}"
                )
            for record in metadata.get("records", []):
                for batch in record.get("batches", []):
                    status_counts[str(batch.get("status", "UNKNOWN"))] += 1
            stopped_early = stopped_early or bool(metadata.get("stopped_early", False))
            total_cost += float(metadata.get("actual_cost_cny") or 0.0)
            semantic_path = Path(str(protocol["prediction_path"]))
            for line in semantic_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                instance_id = str(row["instance_id"])
                if instance_id in combined_rows:
                    issues.append(f"duplicate_instance:{instance_id}")
                combined_rows[instance_id] = row
            member_reports.append({
                "run_id": run_id,
                "status": protocol.get("status"),
                "instance_ids": sorted(actual_ids),
                "actual_cost_cny": metadata.get("actual_cost_cny"),
                "evidence_role_protocol": evidence_protocol,
                "response_envelope_protocol": envelope_protocol,
                "request_equivalence": request_equivalence,
            })

        distinct_core = {_canonical_hash(value) for value in core_fingerprints.values()}
        if len(distinct_core) > 1:
            issues.append("core_generation_settings_mismatch")
        if len(combined_rows) != expected_instances:
            issues.append(
                f"cohort_instance_count:{len(combined_rows)}/{expected_instances}"
            )
        combined_path = cohort_dir / "COHORT_PREDICTIONS.jsonl"
        combined_path.write_text(
            "".join(
                json.dumps(combined_rows[key], ensure_ascii=False, sort_keys=True) + "\n"
                for key in sorted(combined_rows)
            ),
            encoding="utf-8",
        )

        scores = None
        gate = None
        bootstrap = None
        if not issues and not missing_members:
            instance_ids = sorted(combined_rows)
            scores = score_predictions(
                release_dir, combined_path, instance_ids=instance_ids
            )
            if stage == "pilot20":
                bootstrap = build_pilot20_bootstrap(
                    release_dir, combined_path, instance_ids, contract
                )
            gate = evaluate_calibration_stage(
                contract,
                stage,
                protocol_status="COMPLETE_SEMANTIC_COVERAGE",
                planned_instances=expected_instances,
                scored_instances=len(instance_ids),
                batch_status_counts=dict(status_counts),
                stopped_early=stopped_early,
                scores=scores,
                bootstrap=bootstrap,
            )
        report = {
            "cohort_id": cohort_id,
            "status": (
                "INCOMPLETE_COHORT" if missing_members
                else "INCOMPATIBLE_COHORT" if issues
                else "COMPLETE_COHORT"
            ),
            "calibration_stage": stage,
            "expected_instances": expected_instances,
            "collected_instances": len(combined_rows),
            "missing_members": missing_members,
            "issues": issues,
            "model": expected_model,
            "member_reports": member_reports,
            "core_generation_fingerprints": {
                run_id: _canonical_hash(value)
                for run_id, value in sorted(core_fingerprints.items())
            },
            "transport_profiles": transport_profiles,
            "transport_variance_is_nonsemantic": bool(
                cohort.get("transport_variance_is_nonsemantic", False)
            ),
            "actual_cost_cny": round(total_cost, 6),
            "scores": scores,
            "frozen_metric_gate": gate,
            "bootstrap": bootstrap,
            "prediction_path": str(combined_path),
        }
        (cohort_dir / "COHORT_ANALYSIS.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        cohort_reports.append(report)

    result = {
        "protocol_version": "VETT-R26-CALIBRATION-COHORT-1",
        "manifest": str(manifest_path),
        "metric_contract_version": contract["contract_version"],
        "cohorts": cohort_reports,
    }
    (output_root / "COHORT_INDEX.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(prog="vett-eval-cohort")
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        analyze_calibration_cohorts(args.manifest),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()


__all__ = ["analyze_calibration_cohorts"]
