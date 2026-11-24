from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from vett_r26.content_causality_audit import audit_content_causality
from vett_r26.content_causality_admission import (
    build_content_causality_admission,
)
from vett_r26.content_metric_sensitivity import audit_content_metric_sensitivity
from vett_r26.evaluation import score_predictions


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "r26_15_content_dependency_candidate_v3"
CONTRACT = ROOT / "design/r26_15_content_causality_audit_contract.json"
METRIC_CONTRACT = ROOT / "design/r26_15_content_metric_addendum.json"
ANALYSIS = ROOT / "analysis/r26_15_content_causality"


class R2615CausalMetricTests(unittest.TestCase):
    def test_independent_causal_reconstruction_and_masking_probe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = audit_content_causality(
                CANDIDATE, CONTRACT, Path(directory)
            )
        self.assertEqual("PASS_WITH_MEASUREMENT_WARNINGS", report["status"])
        self.assertTrue(all(report["gates"].values()), report["errors"][:10])
        self.assertEqual(324, report["counts"]["actual_content_edges"])
        self.assertEqual(
            324, report["counts"]["independently_reconstructed_content_edges"]
        )
        self.assertEqual(324, report["counts"]["public_semantic_anchor_edges"])
        self.assertEqual(25, report["counts"]["scenario_families"])
        self.assertEqual(
            3.0,
            report["opportunity"]["maximum_to_minimum_level_mean_ratio"],
        )
        omission = report["masking_probe"]["omit_content_edges"]
        self.assertEqual(0.93896, omission["overall_edge_f1"])
        self.assertEqual(0.0, omission["content_edge_f1"])
        self.assertEqual(0.0, omission["factual_chain_exact"])
        self.assertTrue(
            report["audit_implementation"][
                "forbidden_candidate_derivation_import_absent"
            ]
        )
        stored = json.loads(
            (ANALYSIS / "CAUSALITY_AND_MASKING_AUDIT.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(stored, report)

    def test_content_metrics_expose_opportunity_and_balanced_aggregations(self) -> None:
        score = score_predictions(
            CANDIDATE, ANALYSIS / "ORACLE_PREDICTIONS.jsonl"
        )
        self.assertTrue(score["content_dependency_metric_applicable"])
        for key in (
            "content_dependency_edge_f1",
            "content_dependency_edge_question_macro_f1",
            "content_dependency_edge_field_macro_f1",
            "content_dependency_edge_scenario_macro_f1",
        ):
            self.assertEqual(1.0, score[key])
        opportunity = score["content_dependency_gold_opportunity"]["by_level"]
        self.assertEqual(3.8, opportunity["L1"]["mean_gold_edges_per_question"])
        self.assertEqual(4.8, opportunity["L2"]["mean_gold_edges_per_question"])
        self.assertEqual(1.6, opportunity["L5"]["mean_gold_edges_per_question"])

        omitted = score_predictions(
            CANDIDATE, ANALYSIS / "OMIT_CONTENT_EDGES_PREDICTIONS.jsonl"
        )
        self.assertGreater(omitted["minimal_evidence_edge_f1"], 0.9)
        self.assertEqual(0.0, omitted["content_dependency_edge_f1"])
        self.assertEqual(
            0.0, omitted["content_dependency_edge_question_macro_f1"]
        )
        self.assertEqual(0.0, omitted["content_dependency_edge_field_macro_f1"])
        self.assertEqual(
            0.0, omitted["content_dependency_edge_scenario_macro_f1"]
        )

    def test_corrupted_responsibility_registry_is_rejected(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        corrupted = copy.deepcopy(contract)
        corrupted["rule_output_responsibilities"]["BOWLER_DEBIT"] = [
            "dismissal"
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "corrupted_contract.json"
            path.write_text(
                json.dumps(corrupted, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            report = audit_content_causality(CANDIDATE, path, root / "artifacts")
        self.assertEqual("FAIL", report["status"])
        self.assertFalse(report["gates"]["content_edge_count_exact"])
        self.assertFalse(report["gates"]["all_content_edge_sets_exact"])
        self.assertTrue(report["errors"])

    def test_corrupted_public_rule_clause_is_rejected(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        corrupted = copy.deepcopy(contract)
        corrupted["canonical_public_rule_clauses"]["NB_COUNT"] = (
            "THIS CLAUSE IS NOT PRESENT IN THE PUBLIC RULE SPAN"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "corrupted_public_clause.json"
            path.write_text(
                json.dumps(corrupted, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            report = audit_content_causality(CANDIDATE, path, root / "artifacts")
        self.assertEqual("FAIL", report["status"])
        self.assertFalse(
            report["gates"][
                "all_target_spans_contain_frozen_public_rule_clause"
            ]
        )
        self.assertTrue(
            any("public rule clause mismatch" in error for error in report["errors"])
        )

    def test_metric_mutations_separate_content_graph_from_factual_scores(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = audit_content_metric_sensitivity(
                CANDIDATE, METRIC_CONTRACT, Path(directory)
            )
        self.assertEqual("PASS", report["status"])
        self.assertTrue(all(report["gates"].values()))
        scores = report["scores"]
        self.assertEqual(
            0.93896,
            scores["remove_all_content_edges"]["minimal_evidence_edge_f1"],
        )
        self.assertEqual(
            0.0,
            scores["change_all_content_relations"][
                "content_dependency_edge_f1"
            ],
        )
        self.assertEqual(
            1.0,
            scores["add_one_false_content_edge"][
                "content_dependency_edge_recall"
            ],
        )
        self.assertLess(
            scores["add_one_false_content_edge"][
                "content_dependency_edge_precision"
            ],
            1.0,
        )

    def test_full_220_plan_is_causally_certified_without_materialization(self) -> None:
        report = json.loads(
            (ANALYSIS / "STREAMING_CAUSAL_PREFLIGHT_220.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("STATIC_PREFLIGHT_PASS", report["status"])
        self.assertTrue(all(report["static_gates"].values()))
        self.assertEqual(220, report["content_causality_instances_passed"])
        self.assertEqual(1100, report["content_causality_exact_questions"])
        self.assertEqual(3564, report["content_causality_expected_edges"])
        self.assertEqual(3564, report["content_causality_public_semantic_edges"])
        self.assertEqual(
            1.6,
            report["content_dependency_gold_opportunity"]["by_level"]["L5"]
            ["mean_gold_edges_per_question"],
        )
        self.assertEqual(0, report["provider_requests_made"])

    def test_additive_admission_preserves_candidate_and_blocks_empirical_claims(self) -> None:
        report = build_content_causality_admission(
            CANDIDATE,
            ROOT / "analysis/r26_15_content_dependency/STATIC_ADMISSION_V3.json",
            ANALYSIS / "CAUSALITY_AND_MASKING_AUDIT.json",
            ROOT
            / "analysis/r26_15_content_metric_sensitivity/METRIC_SENSITIVITY.json",
            ANALYSIS / "STREAMING_CAUSAL_PREFLIGHT_220.json",
            CONTRACT,
            METRIC_CONTRACT,
        )
        self.assertEqual(
            "STATIC_CAUSAL_MEASUREMENT_PASS_EMPIRICAL_BLOCKED",
            report["status"],
        )
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(
            "NO_R26_16_DATASET_MUTATION",
            report["data_change_decision"]["decision"],
        )
        self.assertEqual(3564, report["full_cohort"]["public_semantic_anchor_edges"])
        self.assertFalse(report["next_empirical_boundary"]["execution_authorized"])
        self.assertEqual(0, report["provider_requests_made"])


if __name__ == "__main__":
    unittest.main()
