from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from vett_r26.protocol_analysis import materialize_semantic_predictions

from .calibration_analysis import build_pilot20_bootstrap
from .metric_contract import evaluate_calibration_stage, load_metric_contract


LEVELS = ("L1", "L2", "L3", "L4", "L5")


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _adjacent_gaps(level_values: dict[str, float]) -> dict[str, float]:
    return {
        f"{left}-{right}": round(
            float(level_values.get(left, 0.0)) - float(level_values.get(right, 0.0)),
            6,
        )
        for left, right in zip(LEVELS, LEVELS[1:])
    }


def analyze_r26_panel(config_path: Path) -> dict[str, Any]:
    """Create a protocol-aware multi-model comparison without making API calls."""
    config = json.loads(config_path.read_text(encoding="utf-8"))
    release_dir = Path(config["release_dir"])
    output_root = Path(config["output_dir"])
    metric_contract = None
    metric_contract_path = config.get("metric_contract")
    if metric_contract_path:
        candidate = Path(str(metric_contract_path))
        if not candidate.is_file():
            candidate = config_path.parent / candidate
        metric_contract = load_metric_contract(candidate)
    entries: list[dict[str, Any]] = []
    for spec in config.get("runs", []):
        run_id = str(spec["run_id"])
        run_dir = output_root / run_id
        metadata_path = run_dir / "RUN_METADATA.json"
        if not metadata_path.is_file():
            entries.append({
                "run_id": run_id,
                "model": spec.get("model"),
                "status": "NOT_RUN",
                "planned_instances": len(spec.get("instance_ids", [])),
            })
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        protocol = materialize_semantic_predictions(release_dir, run_dir)
        batches = [
            batch
            for record in metadata.get("records", [])
            for batch in record.get("batches", [])
        ]
        status_counts = Counter(str(batch.get("status", "UNKNOWN")) for batch in batches)
        failure_classes = Counter(
            str(item.get("failure_class", "UNKNOWN"))
            for item in protocol.get("rejected", [])
        )
        planned_instances = int(
            metadata.get("instances_requested", metadata.get("instances", 0))
        )
        scored_instances = int(protocol.get("scored_instances", 0))
        scores = protocol.get("scores")
        configured_max_tokens = int(spec.get("max_tokens", 0) or 0)
        output_token_counts = [
            int(batch.get("usage", {}).get("output_tokens", 0))
            for batch in batches
            if int(batch.get("usage", {}).get("output_tokens", 0)) > 0
        ]
        actual_output_headroom = (
            min(configured_max_tokens / value for value in output_token_counts)
            if configured_max_tokens and output_token_counts
            else None
        )
        required_headroom = float(spec.get("min_output_headroom_ratio", 1.2))
        entry: dict[str, Any] = {
            "run_id": run_id,
            "model": metadata.get("model", spec.get("model")),
            "status": protocol["status"],
            "r26_evidence_role_protocol": metadata.get(
                "r26_evidence_role_protocol", "explicit_redundant_v2"
            ),
            "r26_response_envelope_protocol": metadata.get(
                "r26_response_envelope_protocol", "explicit_instance_v1"
            ),
            "r26_unknown_evidence_protocol": metadata.get(
                "r26_unknown_evidence_protocol", "batch_invalid_v1"
            ),
            "planned_instances": planned_instances,
            "attempted_instances": len(metadata.get("records", [])),
            "scored_instances": scored_instances,
            "planned_semantic_coverage": round(
                scored_instances / planned_instances, 6
            ) if planned_instances else 0.0,
            "batch_status_counts": dict(sorted(status_counts.items())),
            "failure_class_counts": dict(sorted(failure_classes.items())),
            "stopped_early": bool(metadata.get("stopped_early", False)),
            "actual_usage": metadata.get("actual_usage", {}),
            "actual_cost_cny": metadata.get("actual_cost_cny"),
            "minimum_actual_output_headroom_ratio": (
                round(actual_output_headroom, 6)
                if actual_output_headroom is not None else None
            ),
            "actual_output_headroom_status": (
                "PASS" if actual_output_headroom is not None
                and actual_output_headroom >= required_headroom
                else "LOW" if actual_output_headroom is not None
                else "UNAVAILABLE"
            ),
        }
        if scored_instances:
            entry["actual_cost_cny_per_scoreable_instance"] = round(
                float(metadata.get("actual_cost_cny") or 0.0) / scored_instances, 6
            )
        scored_questions = int(scores.get("questions", 0)) if scores else 0
        if scored_questions:
            entry["actual_cost_cny_per_scoreable_question"] = round(
                float(metadata.get("actual_cost_cny") or 0.0) / scored_questions, 6
            )
        diagnostic_scores = protocol.get("diagnostic_factual_scores")
        if diagnostic_scores is not None:
            entry["diagnostic_factual_only"] = {
                "non_official": True,
                "scored_instances": protocol.get(
                    "diagnostic_factual_scored_instances", 0
                ),
                "coverage": protocol.get("diagnostic_factual_coverage", 0.0),
                "factual_record_macro_accuracy": diagnostic_scores[
                    "factual_record_macro_accuracy"
                ],
                "decision_field_macro_accuracy": diagnostic_scores[
                    "decision_field_macro_accuracy"
                ],
                "decision_field_accuracy_by_level": diagnostic_scores[
                    "decision_field_accuracy_by_level"
                ],
                "counterfactual_field_accuracy": diagnostic_scores[
                    "counterfactual_field_accuracy"
                ],
                "paired_factual_counterfactual_exact": diagnostic_scores[
                    "paired_factual_counterfactual_exact"
                ],
                "warning": (
                    "Diagnostic factual metrics are excluded from official model counts, "
                    "difficulty gates and paper result tables."
                ),
            }
        if scores is not None:
            level_values = {
                level: float(scores["decision_field_accuracy_by_level"].get(level, 0.0))
                for level in LEVELS
            }
            gaps = _adjacent_gaps(level_values)
            entry.update({
                "factual_record_macro_accuracy": scores[
                    "factual_record_macro_accuracy"
                ],
                "decision_field_macro_accuracy": scores[
                    "decision_field_macro_accuracy"
                ],
                "minimal_evidence_f1": scores["minimal_evidence_f1"],
                "rejected_evidence_f1": scores["rejected_evidence_f1"],
                "minimal_evidence_edge_f1": scores[
                    "minimal_evidence_edge_f1"
                ],
                "evidence_chain_joint_exact": scores[
                    "evidence_chain_joint_exact"
                ],
                "factual_evidence_chain_joint_exact": scores[
                    "factual_evidence_chain_joint_exact"
                ],
                "decision_field_accuracy_by_level": level_values,
                "adjacent_field_accuracy_gaps": gaps,
                "cross_level_anchor_diagnostic": scores.get(
                    "cross_level_anchor_diagnostic"
                ),
            })
        calibration_stage = spec.get(
            "calibration_stage", config.get("calibration_stage")
        )
        if metric_contract is not None and calibration_stage == "sentinel5_collection":
            entry["frozen_metric_gate"] = {
                "contract_version": metric_contract["contract_version"],
                "stage": calibration_stage,
                "status": "COLLECTION_ONLY",
                "officially_eligible": False,
                "difficulty_conclusion_permitted": False,
                "decision": (
                    "Artifacts may be collected for a named Sentinel5 cohort, but "
                    "only a complete five-match cohort may be scientifically evaluated."
                ),
            }
        elif metric_contract is not None and not calibration_stage:
            entry["frozen_metric_gate"] = {
                "contract_version": metric_contract["contract_version"],
                "status": "MISSING_CALIBRATION_STAGE",
                "officially_eligible": False,
                "difficulty_conclusion_permitted": False,
                "decision": (
                    "The run may be protocol-scoreable, but no scientific stage was "
                    "declared; difficulty conclusions are forbidden."
                ),
            }
        elif metric_contract is not None and calibration_stage:
            bootstrap = None
            if (
                calibration_stage == "pilot20"
                and protocol["status"] == "COMPLETE_SEMANTIC_COVERAGE"
                and planned_instances == scored_instances == 20
            ):
                bootstrap = build_pilot20_bootstrap(
                    release_dir,
                    Path(protocol["prediction_path"]),
                    list(map(str, protocol["scored_instance_ids"])),
                    metric_contract,
                )
            entry["frozen_metric_gate"] = evaluate_calibration_stage(
                metric_contract,
                str(calibration_stage),
                protocol_status=str(protocol["status"]),
                planned_instances=planned_instances,
                scored_instances=scored_instances,
                batch_status_counts=dict(status_counts),
                stopped_early=bool(metadata.get("stopped_early", False)),
                scores=scores,
                bootstrap=bootstrap,
            )
        entries.append(entry)

    total_costs = [
        entry.get("actual_cost_cny")
        for entry in entries
        if entry.get("actual_cost_cny") is not None
    ]
    report = {
        "protocol_version": "VETT-R26-PANEL-2",
        "config": str(config_path),
        "release_dir": str(release_dir),
        "metric_contract_version": (
            metric_contract["contract_version"] if metric_contract else None
        ),
        "models": entries,
        "models_planned": len(entries),
        "models_scoreable": sum(entry.get("scored_instances", 0) > 0 for entry in entries),
        "all_scientific_gates_pass": bool(entries) and all(
            entry.get("frozen_metric_gate", {}).get("status") == "PASS"
            for entry in entries
        ),
        "actual_cost_cny": round(sum(float(cost) for cost in total_costs), 6),
        "warning": (
            "Protocol-invalid or truncated runs are excluded from semantic model scores; "
            "they are reported as availability/protocol failures, not factual errors."
        ),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    _write_json(output_root / "PANEL_ANALYSIS.json", report)

    rows = []
    for entry in entries:
        diagnostic = entry.get("diagnostic_factual_only")
        diagnostic_text = (
            f"{diagnostic['decision_field_macro_accuracy']:.2%} (non-official)"
            if diagnostic is not None
            and entry.get("scored_instances", 0) == 0
            else "—"
        )
        if "factual_record_macro_accuracy" not in entry:
            rows.append(
                f"| {entry['model']} | {entry['status']} | "
                f"{entry.get('scored_instances', 0)}/{entry.get('planned_instances', 0)} | "
                f"— | {diagnostic_text} | — | — | — |"
            )
            continue
        rows.append(
            f"| {entry['model']} | {entry['status']} | "
            f"{entry['scored_instances']}/{entry['planned_instances']} | "
            f"{entry['factual_record_macro_accuracy']:.2%} | "
            f"{diagnostic_text} | "
            f"{entry['minimal_evidence_f1']:.2%} | "
            f"{entry['minimal_evidence_edge_f1']:.2%} | "
            f"{entry['factual_evidence_chain_joint_exact']:.2%} |"
        )
    (output_root / "PANEL_ANALYSIS.md").write_text(
        "# R26 protocol-aware evaluation panel\n\n"
        "| Model | Protocol status | Scoreable matches | Official factual record macro | Diagnostic field accuracy | Positive span F1 | Edge F1 | Fact+chain exact |\n"
        "|---|---|---:|---:|---:|---:|---:|---:|\n"
        + "\n".join(rows)
        + f"\n\n- Total recorded cost (CNY): {report['actual_cost_cny']}\n"
        + f"- All declared scientific gates pass: {report['all_scientific_gates_pass']}\n"
        + "- Protocol-invalid and truncated runs are not converted into factual zero scores.\n"
        + "- Diagnostic factual values are non-official and are never used for difficulty gates.\n",
        encoding="utf-8",
    )
    return report


__all__ = ["analyze_r26_panel"]
