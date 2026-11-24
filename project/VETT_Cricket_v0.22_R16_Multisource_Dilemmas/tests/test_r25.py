from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vett_r25.auditor import audit_instance, audit_release
from vett_r25.evaluation import score_predictions, write_oracle_predictions
from vett_r25.error_analysis import analyze_errors
from vett_r25.generator import augment_instance, reconstruct_base_documents
from vett_r25.scenarios import SCENARIOS
from vett_r25.shortcut_audit import audit_r24
from vett_r25.solver import solve
from vett_r25.spec import FORBIDDEN_ROLE_WORDS, LEVELS
from vett_eval.analysis import analyze_r25_run
from vett_eval.runner import estimate_config, run_config


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class R25Tests(unittest.TestCase):
    def test_scenario_solver_and_counterfactual_invariants(self) -> None:
        self.assertEqual(25, len(SCENARIOS))
        self.assertEqual(set(LEVELS), {item.level for item in SCENARIOS})
        for scenario in SCENARIOS:
            factual, changed, counterfactual = scenario.records()
            self.assertNotEqual(factual, counterfactual)
            self.assertEqual(factual, solve(scenario.facts))
            self.assertEqual(counterfactual, solve(changed))
            self.assertEqual(factual["total_runs"], sum(row["runs"] for row in factual["run_ledger"]))
            self.assertEqual(counterfactual["total_runs"], sum(row["runs"] for row in counterfactual["run_ledger"]))

    def test_overthrow_math_includes_crossed_run(self) -> None:
        record = solve({
            "contact": "BAT",
            "completed_runs": 2,
            "crossed_at_throw": True,
            "boundary_mode": "OVERTHROW",
            "boundary_allowance": 4,
        })
        self.assertEqual(7, record["total_runs"])
        self.assertEqual(7, record["batter_runs"])

    def test_law_condition_gates_are_explicit(self) -> None:
        base = {
            "no_ball_called": False,
            "contact": "PERSON",
            "dismissal_candidate": "LBW",
            "appeal_made": True,
            "appeal_in_time": True,
            "lbw_pitch_valid": True,
            "lbw_impact_valid": True,
            "lbw_would_hit_wicket": True,
        }
        self.assertEqual("LBW", solve(base)["dismissal"])
        for field in ("lbw_pitch_valid", "lbw_impact_valid", "lbw_would_hit_wicket"):
            changed = dict(base)
            changed[field] = False
            self.assertEqual("NONE", solve(changed)["dismissal"], field)
        no_ball = dict(base)
        no_ball["no_ball_called"] = True
        self.assertEqual("NONE", solve(no_ball)["dismissal"])

        deception = solve({"contact": "BAT", "wilful_deception": True, "completed_runs": 1})
        self.assertFalse(deception["counts_in_over"])
        self.assertEqual(7, deception["total_runs"])

        grounded_catch = solve({
            "contact": "BAT",
            "dismissal_candidate": "CAUGHT",
            "appeal_made": True,
            "appeal_in_time": True,
            "catch_complete": True,
            "ball_grounded_before_control": True,
        })
        self.assertEqual("NONE", grounded_catch["dismissal"])

    def test_instance_is_reversible_and_has_no_role_words(self) -> None:
        match_id = "match_0066"
        base = ROOT / "dataset_r22_220"
        public = _read(base / "public" / match_id / "public_instance.json")
        gold = _read(base / "private" / match_id / "private_gold.json")
        evidence = _read(base / "private" / match_id / "private_evidence.json")
        bundle = augment_instance(public, gold, evidence, variant_index=5)
        result = audit_instance(bundle.public, bundle.gold, bundle.evidence)
        self.assertEqual("PASS", result["status"], result["errors"])
        for answer in bundle.gold["decision_answers"]:
            decisive = set(answer["minimum_evidence_spans"])
            witnesses = answer["evidence_necessity"]
            self.assertEqual(decisive, {item["span_id"] for item in witnesses})
            for witness in witnesses:
                self.assertTrue(witness["removal_result"].startswith("UNRESOLVED_"))
        self.assertEqual(public["documents"], reconstruct_base_documents(bundle.public["documents"], bundle.evidence["r25_text_patches"]))
        inserted_ids = {item["inserted_span_id"] for item in bundle.evidence["r25_text_patches"]}
        inserted_text = [
            span["text"]
            for document in bundle.public["documents"]
            for span in document["spans"]
            if span["span_id"] in inserted_ids
        ]
        self.assertTrue(all(word not in text.lower() for text in inserted_text for word in FORBIDDEN_ROLE_WORDS))

    def test_built_pilot_static_audit_and_oracle(self) -> None:
        release = ROOT / "r25_diagnostic_pilot"
        audit = audit_release(release)
        self.assertEqual("PASS", audit["status"], audit["errors"])
        self.assertEqual(100, audit["decision_questions"])
        self.assertLessEqual(audit["shortcut_baselines"]["most_common_field_macro_accuracy"], 0.45)
        self.assertLessEqual(audit["shortcut_baselines"]["most_common_record_accuracy"], 0.20)
        with tempfile.TemporaryDirectory() as directory:
            oracle = Path(directory) / "oracle.jsonl"
            write_oracle_predictions(release, oracle, test_only=True)
            score = score_predictions(release, oracle)
        self.assertEqual(1.0, score["decision_field_macro_accuracy"])
        self.assertEqual(1.0, score["full_record_exact_match"])
        self.assertEqual(1.0, score["factual_record_macro_accuracy"])
        self.assertEqual(1.0, score["minimal_evidence_f1"])
        self.assertEqual(1.0, score["counterfactual_field_accuracy"])
        self.assertEqual(1.0, score["paired_factual_counterfactual_exact"])

    def test_final_calibration_is_auditable_and_not_promoted(self) -> None:
        release = ROOT / "r25_diagnostic_pilot"
        report = _read(release / "CALIBRATION_REPORT.json")
        self.assertEqual("PILOT_DELIVERABLE_NOT_PROMOTED", report["status"])
        self.assertTrue(report["gates"]["question_only_record_macro_le_20pct"])
        self.assertTrue(report["gates"]["table_record_macro_le_65pct"])
        self.assertTrue(report["gates"]["table_field_strictly_decreasing_by_level"])
        self.assertFalse(report["gates"]["all_adjacent_exact_gaps_ge_8pct"])
        self.assertFalse(report["gates"]["two_model_families_tested"])
        self.assertFalse(report["promotion_decision"]["promote"])
        self.assertEqual(0.0, report["scores"]["question_only_factual_record_macro"])
        self.assertEqual(0.32, report["scores"]["table_factual_record_macro"])
        self.assertEqual(0.6, report["scores"]["isolated_factual_record_macro"])
        self.assertEqual("PASS", audit_release(release)["status"])

    def test_final_error_taxonomy_is_reproducible(self) -> None:
        run = (
            ROOT / "eval_runs" / "r25_2_siliconflow_flash_calibration5"
            / "glm53_flash_r25_2_calibration5"
        )
        report = analyze_errors(ROOT / "r25_diagnostic_pilot", run)
        self.assertEqual(25, report["questions"])
        self.assertEqual(17, report["error_taxonomy_question_counts"]["FACTUAL_RECORD_WRONG"])
        self.assertEqual(9, report["error_taxonomy_question_counts"]["CROSS_INCIDENT_CITATION"])
        self.assertEqual(4, report["error_taxonomy_question_counts"]["FACTUAL_LEDGER_INVARIANT_FAILURE"])

    def test_r24_failure_baseline_is_reproducible(self) -> None:
        report = audit_r24(ROOT / "dataset_r24_220")
        self.assertEqual(1.0, report["constant_counterfactual_accuracy"])
        self.assertEqual(1.0, report["evidence_role_cue_classifier"]["f1"])
        self.assertEqual(1.0, report["questions_with_semantically_labeled_options_rate"])

    def test_unified_runner_supports_r25_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            output = root / "runs"
            config.write_text(json.dumps({
                "release_dir": str(ROOT / "r25_diagnostic_pilot"),
                "output_dir": str(output),
                "runs": [{
                    "run_id": "r25_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "input_ablation": "question_only",
                }],
            }), encoding="utf-8")
            estimate = estimate_config(config)
            self.assertEqual("r25_decision", estimate["task_type"])
            self.assertLess(estimate["runs"][0]["estimated_input_tokens"], 10000)
            run_config(config)
            report = analyze_r25_run(ROOT / "r25_diagnostic_pilot", output / "r25_oracle")
        self.assertEqual(1.0, report["scores"]["decision_field_macro_accuracy"])
        self.assertEqual(1.0, report["scores"]["paired_factual_counterfactual_exact"])


if __name__ == "__main__":
    unittest.main()
