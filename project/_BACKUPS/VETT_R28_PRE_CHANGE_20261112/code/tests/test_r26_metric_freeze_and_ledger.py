from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vett_eval.calibration_analysis import match_stratified_paired_bootstrap
from vett_eval.metric_contract import (
    evaluate_calibration_stage,
    load_metric_contract,
    validate_metric_contract,
)
from vett_eval.panel import analyze_r26_panel
from vett_eval.runner import _chat_response_diagnostics, _response_diagnostic_errors
from vett_eval.runner import estimate_config, run_config
from vett_r26.difficulty_ledger import AXES, LEVELS, build_ledger
from vett_r26.difficulty_stability import (
    audit_difficulty_stability,
    write_stability_audit,
)
from vett_r26.anchors import validate_anchor_design
from vett_r26.auditor import audit_instance as audit_r26_instance
from vett_r26.auditor import audit_release
from vett_r26.expansion_design import (
    audit_expansion_input_coverage,
    audit_expansion_plan,
    build_expansion_plan,
)
from vett_r26.release import build_anchor_stability_candidate
from vett_r25.auditor import audit_instance as audit_r25_instance
from vett_r25.generator import augment_instance as augment_r25_instance
from vett_r26.generator import augment_r25_instance as augment_r26_instance
from vett_r26.spec import CANDIDATE_VERSION
from vett_r26.admission import build_admission_report
from vett_r26.adjustment_registry import validate_adjustment_registry


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "r26_authority_binding_pilot"
METRIC_CONTRACT = ROOT / "design" / "r26_9_metric_contract.json"
FEATURE_CONTRACT = ROOT / "design" / "r26_9_difficulty_feature_contract.json"
STABILITY_CONTRACT = ROOT / "design" / "r26_12_difficulty_stability_contract.json"
LEDGER = ROOT / "analysis/r26_9_difficulty_ledger/PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl"
CANDIDATE_RELEASE = ROOT / "r26_anchor_stability_candidate"
CANDIDATE_LEDGER = ROOT / "analysis/r26_12_anchor_candidate_ledger/PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl"
R20_SUMMARY = ROOT / "dataset_r20_220/RELEASE_SUMMARY.json"


class R26MetricFreezeAndLedgerTests(unittest.TestCase):
    def test_frozen_metric_contract_validates_and_fails_closed_on_drift(self) -> None:
        contract = load_metric_contract(METRIC_CONTRACT)
        self.assertEqual(
            "decision_field_level_macro_accuracy",
            contract["primary_difficulty_metric"]["name"],
        )
        drifted = json.loads(json.dumps(contract))
        drifted["difficulty_curve"]["target_adjacent_drop"] = 0.07
        with self.assertRaisesRegex(ValueError, "must remain 0.08"):
            validate_metric_contract(drifted)

    def test_calibration_stages_enforce_protocol_and_scope(self) -> None:
        contract = load_metric_contract(METRIC_CONTRACT)
        protocol_gate = evaluate_calibration_stage(
            contract,
            "single_protocol_gate",
            protocol_status="COMPLETE_SEMANTIC_COVERAGE",
            planned_instances=1,
            scored_instances=1,
            batch_status_counts={"OK": 1},
            stopped_early=False,
            scores=None,
        )
        self.assertEqual("PASS", protocol_gate["status"])
        self.assertFalse(protocol_gate["difficulty_conclusion_permitted"])

        scores = {
            "decision_field_accuracy_by_level": {
                "L1": 0.80,
                "L2": 0.70,
                "L3": 0.60,
                "L4": 0.50,
                "L5": 0.40,
            },
            "decision_field_macro_accuracy": 0.60,
        }
        sentinel = evaluate_calibration_stage(
            contract,
            "sentinel5",
            protocol_status="COMPLETE_SEMANTIC_COVERAGE",
            planned_instances=5,
            scored_instances=5,
            batch_status_counts={"OK": 5},
            stopped_early=False,
            scores=scores,
        )
        self.assertEqual("PASS", sentinel["status"])
        self.assertTrue(all(sentinel["checks"].values()))
        self.assertTrue(sentinel["screen_only"])

        invalid = evaluate_calibration_stage(
            contract,
            "sentinel5",
            protocol_status="PARTIAL_SEMANTIC_COVERAGE",
            planned_instances=5,
            scored_instances=4,
            batch_status_counts={"OK": 4, "INVALID_OUTPUT": 1},
            stopped_early=True,
            scores=scores,
        )
        self.assertEqual("INELIGIBLE_PROTOCOL", invalid["status"])
        self.assertFalse(invalid["difficulty_conclusion_permitted"])

        wrong_single_size = evaluate_calibration_stage(
            contract,
            "single_protocol_gate",
            protocol_status="COMPLETE_SEMANTIC_COVERAGE",
            planned_instances=5,
            scored_instances=5,
            batch_status_counts={"OK": 5},
            stopped_early=False,
            scores=None,
        )
        self.assertEqual("INVALID_STAGE_SIZE", wrong_single_size["status"])
        self.assertFalse(wrong_single_size["difficulty_conclusion_permitted"])

        wrong_sentinel_size = evaluate_calibration_stage(
            contract,
            "sentinel5",
            protocol_status="COMPLETE_SEMANTIC_COVERAGE",
            planned_instances=1,
            scored_instances=1,
            batch_status_counts={"OK": 1},
            stopped_early=False,
            scores=scores,
        )
        self.assertEqual("INVALID_STAGE_SIZE", wrong_sentinel_size["status"])

    def test_panel_applies_frozen_single_match_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config_path.write_text(json.dumps({
                "metric_contract": str(METRIC_CONTRACT),
                "calibration_stage": "single_protocol_gate",
                "release_dir": str(RELEASE),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "oracle_protocol_gate",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }), encoding="utf-8")
            run_config(config_path)
            report = analyze_r26_panel(config_path)
            metadata = json.loads(
                (root / "runs/oracle_protocol_gate/RUN_METADATA.json").read_text(
                    encoding="utf-8"
                )
            )
            gate = report["models"][0]["frozen_metric_gate"]
            self.assertEqual("PASS", gate["status"])
            self.assertTrue(gate["officially_eligible"])
            self.assertFalse(gate["difficulty_conclusion_permitted"])
            provenance = metadata["experiment_provenance"]
            self.assertEqual("single_protocol_gate", provenance["calibration_stage"])
            self.assertEqual(64, len(provenance["config_sha256"]))
            self.assertEqual(64, len(provenance["metric_contract_sha256"]))

    def test_panel_fails_closed_when_calibration_stage_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config = {
                "release_dir": str(RELEASE),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "undeclared_stage",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            # Simulate analysis of a historical run whose request predates the
            # mandatory scientific-stage preflight.
            config["metric_contract"] = str(METRIC_CONTRACT)
            config_path.write_text(json.dumps(config), encoding="utf-8")
            report = analyze_r26_panel(config_path)
        gate = report["models"][0]["frozen_metric_gate"]
        self.assertEqual("MISSING_CALIBRATION_STAGE", gate["status"])
        self.assertFalse(gate["difficulty_conclusion_permitted"])
        self.assertFalse(report["all_scientific_gates_pass"])

    def test_paid_preflight_rejects_missing_or_wrong_scientific_stage_size(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config = {
                "metric_contract": str(METRIC_CONTRACT),
                "release_dir": str(RELEASE),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "unsafe_stage",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "lacks a supported calibration_stage"):
                estimate_config(config_path)
            config["calibration_stage"] = "sentinel5"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "require 5"):
                estimate_config(config_path)

    def test_json_closure_repair_is_visible_to_the_official_gate(self) -> None:
        diagnostics = _chat_response_diagnostics({
            "choices": [{"finish_reason": "stop", "message": {"content": "{}"}}],
            "vett_json_repair": {"appended_suffix": "]}"},
        })
        self.assertEqual("]}", diagnostics["json_repair_suffix"])
        self.assertIn(
            "JSON closure repair was required",
            _response_diagnostic_errors(diagnostics),
        )

    def test_pilot20_bootstrap_preserves_paired_match_blocks(self) -> None:
        contract = load_metric_contract(METRIC_CONTRACT)
        values = {"L1": 0.80, "L2": 0.70, "L3": 0.60, "L4": 0.50, "L5": 0.40}
        rows = [
            {"match_id": f"match_{index:04d}", "level": level, "accuracy": value}
            for index in range(20)
            for level, value in values.items()
        ]
        bootstrap = match_stratified_paired_bootstrap(
            rows, resamples=10000, seed=26091
        )
        self.assertEqual(20, bootstrap["match_blocks"])
        self.assertEqual(10000, bootstrap["resamples"])
        self.assertTrue(all(
            interval["lower_95"] > 0
            for interval in bootstrap["adjacent_gap_intervals"].values()
        ))
        result = evaluate_calibration_stage(
            contract,
            "pilot20",
            protocol_status="COMPLETE_SEMANTIC_COVERAGE",
            planned_instances=20,
            scored_instances=20,
            batch_status_counts={"OK": 20},
            stopped_early=False,
            scores={
                "decision_field_accuracy_by_level": values,
                "decision_field_macro_accuracy": 0.60,
            },
            bootstrap=bootstrap,
        )
        self.assertEqual("PASS", result["status"])
        self.assertTrue(all(result["checks"].values()))

    def test_private_difficulty_ledger_is_complete_and_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            report = build_ledger(
                RELEASE, first, FEATURE_CONTRACT, METRIC_CONTRACT
            )
            repeated = build_ledger(
                RELEASE, second, FEATURE_CONTRACT, METRIC_CONTRACT
            )
            self.assertEqual("PASS", report["status"], report["errors"])
            self.assertEqual(100, report["rows"])
            self.assertEqual(20, report["matches"])
            self.assertEqual({level: 20 for level in LEVELS}, report["level_counts"])
            self.assertEqual(25, report["scenario_family_count"])
            self.assertEqual(0, report["public_level_leaks"])
            self.assertEqual(0, report["exact_duplicate_rows"])
            self.assertEqual(0, report["difficulty_vector_reproduction_errors"])
            means = report["feature_summary_by_level"]["structural_load_index"]
            self.assertTrue(all(
                means[left]["mean"] < means[right]["mean"]
                for left, right in zip(LEVELS, LEVELS[1:])
            ))
            for axis in AXES:
                for level in LEVELS:
                    summary = report["feature_summary_by_level"][axis][level]
                    self.assertGreaterEqual(summary["min"], 0.0)
                    self.assertLessEqual(summary["max"], 1.0)
            self.assertTrue(report["raw_feature_crossovers"])
            self.assertEqual(report["ledger_sha256"], repeated["ledger_sha256"])
            for name in (
                "PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl",
                "PRIVATE_DIFFICULTY_FEATURE_LEDGER.csv",
                "DIFFICULTY_LEDGER_AUDIT.json",
                "DIFFICULTY_LEDGER_AUDIT.md",
            ):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

    def test_private_ledger_is_not_packaged_as_public_input(self) -> None:
        public_files = {path.name for path in (RELEASE / "public").rglob("*") if path.is_file()}
        self.assertNotIn("PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl", public_files)
        self.assertNotIn("PRIVATE_DIFFICULTY_FEATURE_LEDGER.csv", public_files)

    def test_pre220_stability_gate_finds_real_design_blockers_without_invalidating_pilot(self) -> None:
        report = audit_difficulty_stability(
            RELEASE, LEDGER, STABILITY_CONTRACT
        )
        self.assertEqual("EXPANSION_BLOCKED", report["status"])
        self.assertFalse(report["current_pilot_semantics_invalidated"])
        self.assertGreaterEqual(report["unique_difficulty_vector_ratio"], 0.70)
        self.assertEqual(1.0, report["single_level_scenario_family_share"])
        self.assertEqual(0, report["cross_level_anchor_families"])
        self.assertIn("transition_axis_dominance:L2-L3", report["errors"])
        self.assertIn("transition_axis_dominance:L3-L4", report["errors"])
        self.assertIn("transition_axis_dominance:L4-L5", report["errors"])
        self.assertIn("cross_level_anchor_families:0", report["errors"])

    def test_anchor_candidate_passes_static_semantic_and_pre220_stability_gates(self) -> None:
        self.assertEqual("PASS", validate_anchor_design()["status"])
        release_report = audit_release(CANDIDATE_RELEASE)
        self.assertEqual("PASS", release_report["status"], release_report["errors"])
        report = audit_difficulty_stability(
            CANDIDATE_RELEASE, CANDIDATE_LEDGER, STABILITY_CONTRACT
        )
        self.assertEqual("READY_FOR_220", report["status"], report["errors"])
        self.assertEqual(5, report["cross_level_anchor_families"])
        self.assertTrue(all(
            delta >= 0.01
            for transitions in report["anchor_transition_summary"].values()
            for delta in transitions.values()
        ))
        self.assertTrue(all(
            row["mean_structural_delta"] >= 0.08
            and row["maximum_dominant_axis_share"] <= 0.8
            for row in report["transition_summary"].values()
        ))

    def test_anchor_candidate_build_is_byte_manifest_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir) / "candidate"
            second = Path(second_dir) / "candidate"
            build_anchor_stability_candidate(ROOT / "r25_diagnostic_pilot", first)
            build_anchor_stability_candidate(ROOT / "r25_diagnostic_pilot", second)
            first_manifest = json.loads((first / "MANIFEST.json").read_text(encoding="utf-8"))
            second_manifest = json.loads((second / "MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(first_manifest, second_manifest)
            self.assertEqual(
                "VETT-Cricket-v0.36.12-R26.12-anchor-stability-candidate",
                first_manifest["dataset_version"],
            )

    def test_220_expansion_plan_is_balanced_private_and_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "first.json"
            second_path = root / "second.json"
            report = build_expansion_plan(R20_SUMMARY, first_path)
            repeated = build_expansion_plan(R20_SUMMARY, second_path)
            self.assertEqual("PASS", report["status"], report["errors"])
            self.assertEqual(report, repeated)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertEqual(220, report["matches"])
            self.assertEqual(1100, report["assignments"])
            self.assertEqual(44, report["blocks"])
            self.assertEqual({44}, set(report["anchor_level_counts"].values()))
            self.assertEqual({44}, set(report["scenario_family_counts"].values()))
            plan = json.loads(first_path.read_text(encoding="utf-8"))
            self.assertEqual(
                "PRIVATE_DESIGN_LEDGER_DO_NOT_EXPOSE_TO_MODEL", plan["privacy"]
            )
            plan["assignments"][0]["scenario_family"] = "INVALID_FAMILY"
            self.assertEqual("FAIL", audit_expansion_plan(plan)["status"])
            coverage = audit_expansion_input_coverage(
                first_path,
                ROOT / "r25_diagnostic_pilot",
                root / "coverage.json",
            )
            self.assertEqual("BLOCKED", coverage["status"])
            self.assertEqual(20, coverage["complete_matches"])
            self.assertEqual(200, coverage["incomplete_matches"])
            self.assertFalse(coverage["partial_generation_permitted"])

    def test_expansion_allocation_drives_one_end_to_end_semantic_bundle(self) -> None:
        plan = json.loads((
            ROOT / "analysis/r26_12_expansion_plan_220/PRIVATE_EXPANSION_ALLOCATION.json"
        ).read_text(encoding="utf-8"))
        match_id = "match_0003"
        assignment = {
            row["level"]: row["scenario_family"]
            for row in plan["assignments"]
            if row["match_id"] == match_id
        }
        base = ROOT / "dataset_r22_220"
        public = json.loads((
            base / "public" / match_id / "public_instance.json"
        ).read_text(encoding="utf-8"))
        gold = json.loads((
            base / "private" / match_id / "private_gold.json"
        ).read_text(encoding="utf-8"))
        evidence = json.loads((
            base / "private" / match_id / "private_evidence.json"
        ).read_text(encoding="utf-8"))
        r25 = augment_r25_instance(
            public,
            gold,
            evidence,
            variant_index=0,
            scenario_family_by_level=assignment,
        )
        self.assertEqual(
            "PASS",
            audit_r25_instance(r25.public, r25.gold, r25.evidence)["status"],
        )
        self.assertEqual(
            assignment,
            {
                answer["level"]: answer["scenario_family"]
                for answer in r25.gold["decision_answers"]
            },
        )
        r26 = augment_r26_instance(
            r25.public,
            r25.gold,
            r25.evidence,
            variant_index=0,
            dataset_version=CANDIDATE_VERSION,
            candidate_difficulty_design=True,
        )
        r26_audit = audit_r26_instance(
            r26.public,
            r26.gold,
            r26.evidence,
            base_public=r25.public,
            base_gold=r25.gold,
            expected_version=CANDIDATE_VERSION,
        )
        self.assertEqual("PASS", r26_audit["status"], r26_audit["errors"])

    def test_admission_report_separates_design_pass_from_full_release_blockers(self) -> None:
        kwargs = {
            "release_dir": CANDIDATE_RELEASE,
            "ledger_audit_path": ROOT / "analysis/r26_12_anchor_candidate_ledger/DIFFICULTY_LEDGER_AUDIT.json",
            "stability_audit_path": ROOT / "analysis/r26_12_anchor_candidate_stability/DIFFICULTY_STABILITY_AUDIT.json",
            "shortcut_audit_path": ROOT / "analysis/r26_12_anchor_candidate_shortcut.json",
            "expansion_plan_path": ROOT / "analysis/r26_12_expansion_plan_220/PRIVATE_EXPANSION_ALLOCATION.json",
            "expansion_input_audit_path": ROOT / "analysis/r26_12_expansion_plan_220/EXPANSION_INPUT_COVERAGE.json",
            "adjustment_registry_audit_path": ROOT / "analysis/r26_12_admission/ADJUSTMENT_REGISTRY_AUDIT.json",
            "oracle_predictions_path": ROOT / "analysis/r26_12_anchor_candidate_oracle.jsonl",
            "cohort_index_path": ROOT / "analysis/r26_12_glm53_sentinel5_cohort/COHORT_INDEX.json",
            "pending_eval_config_path": ROOT / "eval_configs/r26_12_glm53_request_bound_sentinel5_collection4.json",
        }
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            report = build_admission_report(output_dir=first, **kwargs)
            repeated = build_admission_report(output_dir=second, **kwargs)
            self.assertEqual("PASS", report["pre220_structural_design_gate"])
            self.assertEqual("BLOCKED", report["full_220_generation_input_readiness"])
            self.assertFalse(report["full_220_generation_authorized"])
            self.assertIn("INCOMPLETE_SENTINEL5", report["full_220_generation_blockers"])
            self.assertIn(
                "PILOT20_TWO_STRONG_MODEL_FAMILIES",
                report["full_220_generation_blockers"],
            )
            self.assertEqual(report, repeated)
            for name in ("R26_12_ADMISSION_REPORT.json", "R26_12_ADMISSION_REPORT.md"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

    def test_preregistered_adjustment_registry_forbids_single_match_tuning(self) -> None:
        report = validate_adjustment_registry(
            ROOT / "design/r26_12_preregistered_adjustment_registry.json"
        )
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(4, report["transition_actions"])
        self.assertFalse(report["single_match_activation_permitted"])

    def test_pre220_stability_report_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            write_stability_audit(RELEASE, LEDGER, STABILITY_CONTRACT, first)
            write_stability_audit(RELEASE, LEDGER, STABILITY_CONTRACT, second)
            for name in (
                "DIFFICULTY_STABILITY_AUDIT.json",
                "DIFFICULTY_STABILITY_AUDIT.md",
            ):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
