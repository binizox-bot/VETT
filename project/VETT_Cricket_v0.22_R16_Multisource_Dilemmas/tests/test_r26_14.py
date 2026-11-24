from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vett_r26.answer_blind_admission import build_answer_blind_admission
from vett_r26.answer_blind_drift_audit import audit_answer_blind_drift
from vett_r26.answer_prior_audit import audit_answer_priors
from vett_r26.adversarial_static_audit import (
    adversarial_question_baselines,
    audit_adversarial_static_shortcuts,
    load_question_rows,
)
from vett_r26.auditor import audit_release
from vett_r26.diagnostic_decision import decide_next_diagnostic
from vett_r26.evaluation import score_predictions
from vett_r26.level_confound_audit import audit_level_surface_confound
from vett_r26.protocol_fault_matrix import audit_protocol_fault_matrix
from vett_r26.sentinel_preflight import compile_sentinel_preflight
from vett_r26.structural_shortcut_audit import (
    audit_structural_shortcuts,
    collect_structural_rows,
    summarize_structural_rows,
)


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "r26_measurement_validity_candidate"
CANDIDATE = ROOT / "r26_14_answer_blind_candidate_v2"
ANALYSIS = ROOT / "analysis/r26_14_answer_blind"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class R2614AnswerBlindCandidateTests(unittest.TestCase):
    def test_integrated_release_and_narrow_drift_pass(self) -> None:
        release = audit_release(CANDIDATE)
        self.assertEqual("PASS", release["status"], release["errors"][:10])
        self.assertEqual("PASS", release["answer_prior_shortcut_status"])
        drift = audit_answer_blind_drift(PARENT, CANDIDATE)
        self.assertEqual("PASS", drift["status"], drift["errors"])
        self.assertTrue(all(drift["gates"].values()))
        self.assertEqual(100, drift["questions_changed"])
        self.assertEqual(100, drift["public_span_texts_changed"])
        self.assertEqual(0, drift["gold_semantic_fields_changed"])
        self.assertEqual(0, drift["proof_edges_changed"])
        self.assertEqual(0, drift["unregistered_public_text_changes"])

    def test_question_only_answer_shortcut_is_below_frozen_ceilings(self) -> None:
        report = audit_answer_priors(CANDIDATE)
        self.assertEqual("PASS", report["status"])
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(100, report["dossier_bound_intervention_questions"])
        self.assertEqual(0, report["question_interventions_parseable"])
        nearest = report["baselines"]["question_surface_nearest_neighbor"]
        self.assertLessEqual(
            nearest["public_question_payload"]["informative_field_accuracy"],
            0.50,
        )
        self.assertLessEqual(nearest["question"]["full_record_exact"], 0.10)
        self.assertLessEqual(
            report["question_payload_field_advantage_over_unconditional"], 0.05
        )
        self.assertIn("do not infer model difficulty", report["required_action"])

        adversarial = audit_adversarial_static_shortcuts(CANDIDATE)
        self.assertEqual(
            "PASS_WITH_DISCLOSED_COMPONENT_LOCATOR", adversarial["status"]
        )
        self.assertTrue(all(adversarial["factual_shortcut_gates"].values()))
        self.assertLessEqual(
            adversarial["question_only_baselines"]["equal_prior_word_nb"]
            ["informative_field_accuracy"],
            0.50,
        )
        self.assertLessEqual(
            adversarial["question_only_baselines"]
            ["scenario_family_held_out_1nn"]["informative_field_accuracy"],
            0.50,
        )
        pilot_field_signal = adversarial["field_signal_diagnostics"][
            "equal_prior_word_nb"
        ]
        self.assertEqual(
            "ledger.NO_BALL_EXTRA",
            pilot_field_signal["highest_informative_field"],
        )
        self.assertEqual(
            0.582237,
            pilot_field_signal[
                "highest_informative_field_value_balanced_accuracy"
            ],
        )
        self.assertEqual(
            ["ledger.NO_BALL_EXTRA"],
            pilot_field_signal[
                "informative_fields_above_55pct_value_balanced_accuracy"
            ],
        )
        locator = adversarial["counterfactual_instruction_locator"]
        self.assertEqual([5], locator["marker_candidates_per_match"])
        self.assertEqual(0.33, locator["top1_query_plus_marker_locator_accuracy"])
        self.assertLess(locator["mean_marker_only_decisive_span_recall"], 0.07)

        leaked_rows = load_question_rows(CANDIDATE)
        for row in leaked_rows:
            row["payload"] = json.dumps(row["record"], sort_keys=True)
        leaked = adversarial_question_baselines(leaked_rows)
        self.assertEqual("FAIL", leaked["status"])
        self.assertFalse(all(leaked["gates"].values()))
        self.assertGreater(
            leaked["baselines"]["equal_prior_word_nb"]
            ["informative_field_accuracy"],
            0.90,
        )

    def test_oracle_scores_all_prior_aware_companion_metrics(self) -> None:
        scores = score_predictions(
            CANDIDATE, ANALYSIS / "ORACLE_PREDICTIONS.jsonl"
        )
        for metric in (
            "decision_field_macro_accuracy",
            "decision_informative_field_accuracy",
            "decision_informative_field_value_balanced_accuracy",
            "decision_field_skill_over_unconditional_prior",
            "decision_informative_field_skill_over_unconditional_prior",
            "full_record_exact_match",
            "factual_evidence_chain_joint_exact",
            "gold_edge_endpoint_recovery_rate",
            "predicted_edge_gold_endpoint_share",
            "conditional_edge_link_precision_given_gold_nodes",
            "conditional_edge_link_recall_given_recovered_endpoints",
            "conditional_edge_link_f1",
        ):
            self.assertEqual(1.0, scores[metric], metric)
        self.assertEqual(
            ["ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"],
            scores["answer_prior_reference"][
                "constant_fields_excluded_from_informative_metrics"
            ],
        )
        rows = [
            json.loads(line)
            for line in (ANALYSIS / "ORACLE_PREDICTIONS.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        rows[0]["decision_predictions"][0]["evidence_edges"].pop()
        with tempfile.TemporaryDirectory() as directory:
            mutated_path = Path(directory) / "missing_edge.jsonl"
            mutated_path.write_text(
                "\n".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True)
                    for row in rows
                )
                + "\n",
                encoding="utf-8",
            )
            mutated = score_predictions(CANDIDATE, mutated_path)
        self.assertEqual(1.0, mutated["gold_edge_endpoint_recovery_rate"])
        self.assertLess(mutated["conditional_edge_link_f1"], 1.0)
        self.assertLess(mutated["minimal_evidence_edge_f1"], 1.0)

    def test_level_surface_is_neutralized_but_matched_reporting_remains(self) -> None:
        report = audit_level_surface_confound(CANDIDATE)
        self.assertEqual(
            "CONFOUND_DETECTED_MATCHED_CONTROL_READY", report["status"]
        )
        self.assertLess(
            report["question_only_baseline"]["leave_one_match_out_macro_f1"],
            0.30,
        )
        self.assertLess(
            report["intervention_only_baseline"][
                "leave_one_match_out_macro_f1"
            ],
            0.30,
        )
        self.assertEqual(100, report["dossier_bound_intervention_questions"])
        self.assertTrue(all(report["matched_control_gates"].values()))

        shortcut = _read(ANALYSIS / "SEMANTIC_SHORTCUT_AUDIT.json")
        self.assertEqual("PASS", shortcut["status"])
        self.assertTrue(all(shortcut["gates"].values()))
        self.assertLess(
            shortcut["literal_query_top_k_evidence_recall"], 0.25
        )
        review = _read(
            ANALYSIS
            / "language_surface/ASSISTANT_STRATIFIED_LANGUAGE_REVIEW.json"
        )
        self.assertEqual("PASS_WITH_DISCLOSED_LIMITATIONS", review["status"])
        self.assertEqual(
            0, review["review_counts"]["blocking_language_defects"]
        )
        self.assertEqual("NOT_RUN", review["independent_human_review_status"])

    def test_structural_shortcuts_are_bounded_and_mutation_sensitive(self) -> None:
        contract_path = ROOT / "design/r26_14_structural_shortcut_audit_contract.json"
        report = audit_structural_shortcuts(CANDIDATE, contract_path)
        self.assertEqual("PASS", report["status"])
        self.assertTrue(all(report["gates"].values()))
        retrieval = report["bm25_question_to_evidence"]
        self.assertEqual(1.0, retrieval["top1_positive_rate"])
        self.assertEqual(
            {"semantic_bridge": 100}, retrieval["top1_role_counts"]
        )
        self.assertLess(
            retrieval[
                "non_entry_positive_recall_at_gold_k_after_removing_marker_and_semantic_bridge_spans"
            ],
            0.08,
        )
        self.assertLess(
            retrieval["mean_reciprocal_rank_first_non_entry_positive"],
            0.10,
        )
        topology = report["question_only_topology_prior"]
        self.assertEqual(0.06, topology["typed_relation_count_signature_exact"])
        self.assertEqual(0.08, topology["typed_edge_cardinality_exact"])
        self.assertLess(
            report["public_numeric_level_confound"][
                "leave_one_match_out_macro_f1"
            ],
            0.30,
        )

        summary = _read(CANDIDATE / "RELEASE_SUMMARY.json")
        rows = []
        for match_id in summary["match_ids"]:
            rows.extend(
                collect_structural_rows(
                    _read(CANDIDATE / "public" / match_id / "public_instance.json"),
                    _read(CANDIDATE / "private" / match_id / "private_gold.json"),
                    _read(
                        CANDIDATE
                        / "private"
                        / match_id
                        / "private_evidence.json"
                    ),
                )
            )
        for row in rows:
            row["query_tokens"] = [row["topology_signature"]]
        leaked = summarize_structural_rows(rows, _read(contract_path))
        self.assertEqual("FAIL", leaked["status"])
        self.assertEqual(
            1.0,
            leaked["question_only_topology_prior"][
                "typed_relation_count_signature_exact"
            ],
        )

    def test_full_cohort_streaming_preflight_passes_without_materialization(self) -> None:
        report = _read(ANALYSIS / "STREAMING_EXPANSION_PREFLIGHT_220.json")
        self.assertEqual("STATIC_PREFLIGHT_PASS", report["status"])
        self.assertEqual(220, report["matches_planned"])
        self.assertEqual(1100, report["questions_audited"])
        self.assertEqual(0, report["unapproved_exact_question_duplicates"])
        self.assertEqual(1, report["approved_duplicate_control_questions"])
        self.assertEqual(0, report["cross_match_public_span_id_collisions"])
        self.assertTrue(
            all(
                report["full_cohort_answer_prior_diagnostic"]["gates"].values()
            )
        )
        self.assertEqual(
            1100,
            report["full_cohort_answer_prior_diagnostic"][
                "dossier_bound_intervention_questions"
            ],
        )
        self.assertEqual(
            0,
            report["full_cohort_answer_prior_diagnostic"][
                "explicit_question_interventions"
            ],
        )
        adversarial = report[
            "full_cohort_adversarial_question_only_diagnostic"
        ]
        self.assertEqual("PASS", adversarial["status"])
        self.assertTrue(all(adversarial["gates"].values()))
        self.assertLessEqual(
            adversarial["baselines"]["equal_prior_word_nb"]
            ["informative_field_accuracy"],
            0.50,
        )
        full_field_signal = adversarial["field_signal_diagnostics"][
            "equal_prior_word_nb"
        ]
        self.assertEqual(
            "ledger.NO_BALL_EXTRA",
            full_field_signal["highest_informative_field"],
        )
        self.assertEqual(
            0.517943,
            full_field_signal[
                "highest_informative_field_value_balanced_accuracy"
            ],
        )
        self.assertEqual(
            [],
            full_field_signal[
                "informative_fields_above_55pct_value_balanced_accuracy"
            ],
        )
        locator = report["full_cohort_counterfactual_locator_diagnostic"]
        self.assertEqual(1100, locator["marker_spans"])
        self.assertEqual(0.340909, locator["top1_query_plus_marker_locator_accuracy"])
        self.assertLess(locator["mean_marker_only_decisive_span_recall"], 0.07)
        structural = report["full_cohort_structural_shortcut_diagnostic"]
        self.assertEqual("PASS", structural["status"])
        self.assertTrue(all(structural["gates"].values()))
        retrieval = structural["bm25_question_to_evidence"]
        self.assertEqual(
            {"semantic_bridge": 1100}, retrieval["top1_role_counts"]
        )
        self.assertLess(
            retrieval[
                "non_entry_positive_recall_at_gold_k_after_removing_marker_and_semantic_bridge_spans"
            ],
            0.06,
        )
        self.assertEqual(
            0.039091,
            structural["question_only_topology_prior"][
                "typed_relation_count_signature_exact"
            ],
        )
        self.assertLess(
            structural["public_numeric_level_confound"][
                "leave_one_match_out_macro_f1"
            ],
            0.30,
        )
        self.assertFalse(report["full_candidate_materialized"])
        self.assertEqual(0, report["provider_requests_made"])

    def test_fault_matrix_and_zero_request_sentinel_are_fail_closed(self) -> None:
        faults = audit_protocol_fault_matrix(CANDIDATE)
        self.assertEqual("PASS", faults["status"])
        self.assertEqual(12, len(faults["cases"]))
        self.assertEqual(
            {"protocol": 6, "semantic": 4, "transport_or_envelope": 2},
            faults["case_counts_by_expected_layer"],
        )
        preflight = compile_sentinel_preflight(
            ROOT / "eval_configs/r26_14_glm53_flash_uniform_sentinel5_blocked.json",
            ROOT / "design/r26_14_sentinel5_request_contract.json",
        )
        self.assertEqual(
            "REQUEST_READY_BLOCKED_BY_AUTHORIZATION", preflight["status"]
        )
        self.assertTrue(all(preflight["gates"].values()))
        self.assertFalse(preflight["execution_authorized"])
        self.assertEqual(0, preflight["provider_requests_made"])
        self.assertLessEqual(preflight["estimated_cost_cny_zero_cache"], 1.2)
        self.assertGreaterEqual(
            preflight["minimum_oracle_output_headroom_ratio"], 1.25
        )

    def test_static_admission_passes_without_claiming_empirical_difficulty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = build_answer_blind_admission(
                CANDIDATE,
                ANALYSIS,
                ROOT / "design/r26_14_metric_validity_addendum.json",
                Path(directory) / "STATIC_ADMISSION.json",
            )
        self.assertEqual(
            "STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED", report["status"]
        )
        self.assertTrue(report["static_candidate_admitted"])
        self.assertFalse(report["empirical_difficulty_calibrated"])
        self.assertFalse(report["full_220_materialization_authorized"])
        self.assertFalse(report["official_release_authorized"])
        self.assertTrue(all(report["static_gates"].values()))
        self.assertIn(
            "STRONG_MODEL_65PCT_AND_ADJACENT_8PPT_TARGETS_UNCALIBRATED",
            report["blockers"],
        )

        contract = _read(ROOT / "design/r26_14_diagnostic_escalation_contract.json")
        action = decide_next_diagnostic(
            contract, static_readiness=audit_answer_priors(CANDIDATE)
        )
        self.assertEqual(
            "AWAIT_EXPLICIT_AUTHORIZATION_FOR_UNIFORM_SENTINEL5",
            action["next_action"],
        )


if __name__ == "__main__":
    unittest.main()
