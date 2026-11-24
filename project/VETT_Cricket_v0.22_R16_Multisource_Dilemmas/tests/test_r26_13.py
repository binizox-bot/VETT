from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from vett_eval.runner import run_config
from vett_eval.calibration_analysis import (
    anchor_standardized_match_block_bootstrap,
    question_field_accuracy_rows,
)
from vett_r26.auditor import audit_release
from vett_r26.answer_prior_audit import audit_answer_priors
from vett_r26.identifier_neutrality import PUBLIC_SPAN_ID, audit_identifier_neutrality
from vett_r26.input_form_analysis import analyze_input_forms
from vett_r26.language_surface_audit import audit_language_surface
from vett_r26.level_confound_audit import audit_level_surface_confound
from vett_r26.evaluation import score_predictions
from vett_r26.error_analysis import analyze_r26_errors
from vett_r26.identifiability_admission import build_identifiability_admission
from vett_r26.adjustment_authority import validate_adjustment_authority
from vett_r26.diagnostic_decision import decide_next_diagnostic
from vett_r26.metadata_shortcut_audit import audit_metadata_shortcuts
from vett_r26.measurement_admission import build_admission_report
from vett_r26.protocol_fault_matrix import audit_protocol_fault_matrix
from vett_r26.proof_audit import audit_proof_certificates, audit_proof_instance
from vett_r26.sentinel_preflight import compile_sentinel_preflight


ROOT = Path(__file__).resolve().parents[1]
R26_12 = ROOT / "r26_anchor_stability_candidate"
R26_13 = ROOT / "r26_measurement_validity_candidate"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class R2613MeasurementValidityTests(unittest.TestCase):
    def test_candidate_preserves_semantics_and_passes_new_static_gates(self) -> None:
        release = audit_release(R26_13)
        self.assertEqual("PASS", release["status"], release["errors"])
        self.assertEqual("PASS", release["metadata_shortcut_status"])
        self.assertEqual({"PASS": 20}, release["proof_only_variant_status_counts"])
        metadata = audit_metadata_shortcuts(R26_13)
        self.assertEqual("PASS", metadata["status"])
        self.assertLessEqual(
            metadata["baselines"]["span_identifier_morphology"]
            ["leave_one_match_out_macro_f1"],
            0.5,
        )
        proof = audit_proof_certificates(R26_13)
        self.assertEqual("PASS", proof["status"], proof["errors"][:10])
        self.assertEqual(100, proof["minimal_fact_reconstruction_passes"])
        self.assertEqual(100, proof["single_edge_deletion_passes"])
        self.assertEqual(100, proof["unique_registered_proof_passes"])
        self.assertEqual(100, proof["unique_public_surface_proof_passes"])

    def test_r26_12_identifier_leak_is_measured_not_hidden(self) -> None:
        report = audit_metadata_shortcuts(R26_12)
        self.assertEqual("FAIL", report["status"])
        self.assertEqual(
            1.0,
            report["baselines"]["span_identifier_morphology"]
            ["leave_one_match_out_macro_f1"],
        )
        self.assertGreater(report["role_bearing_public_span_ids"], 0)

    def test_every_public_span_id_has_the_same_role_neutral_shape(self) -> None:
        for path in (R26_13 / "public").glob("match_*/public_instance.json"):
            public = _read(path)
            ids = [
                str(span["span_id"])
                for document in public["documents"]
                for span in document["spans"]
            ]
            self.assertTrue(ids)
            self.assertTrue(all(PUBLIC_SPAN_ID.fullmatch(span_id) for span_id in ids))

    def test_neutrality_and_proof_mutations_fail_closed(self) -> None:
        match_id = "match_0021"
        public = _read(R26_13 / "public" / match_id / "public_instance.json")
        gold = _read(R26_13 / "private" / match_id / "private_gold.json")
        evidence = _read(R26_13 / "private" / match_id / "private_evidence.json")

        leaked = copy.deepcopy(public)
        leaked["documents"][0]["spans"][0]["span_id"] = "r25fact_leaked_role"
        neutrality = audit_identifier_neutrality(leaked, gold, evidence)
        self.assertEqual("FAIL", neutrality["status"])
        self.assertTrue(any("non_neutral_id_shape" in item for item in neutrality["errors"]))

        missing_edge_gold = copy.deepcopy(gold)
        missing_edge_gold["decision_answers"][0]["minimum_evidence_edges"].pop()
        missing_edge = audit_proof_instance(public, missing_edge_gold, evidence)
        self.assertEqual("FAIL", missing_edge["status"])

        duplicate_claims = copy.deepcopy(evidence)
        first_answer = gold["decision_answers"][0]
        qid = first_answer["question_id"]
        original = next(
            claim for claim in duplicate_claims["r25_evidence_claims"]
            if claim.get("question_id") == qid and claim.get("role") == "incident_fact"
        )
        duplicate_claims["r25_evidence_claims"].append(copy.deepcopy(original))
        duplicated = audit_proof_instance(public, gold, duplicate_claims)
        self.assertEqual("FAIL", duplicated["status"])

        surface_substitute = copy.deepcopy(public)
        decisive_id = str(gold["decision_answers"][0]["minimum_evidence_spans"][0])
        decisive_text = next(
            str(span["text"])
            for document in surface_substitute["documents"]
            for span in document["spans"]
            if str(span["span_id"]) == decisive_id
        )
        protected = set(map(str, gold["decision_answers"][0]["minimum_evidence_spans"]))
        protected.update(
            map(str, gold["decision_answers"][0]["rejected_evidence_spans"])
        )
        replacement = next(
            span
            for document in surface_substitute["documents"]
            for span in document["spans"]
            if str(span["span_id"]) not in protected
        )
        replacement["text"] = decisive_text
        substitute_audit = audit_proof_instance(
            surface_substitute, gold, evidence
        )
        self.assertEqual("FAIL", substitute_audit["status"])
        self.assertTrue(
            any(
                "unregistered_exact_surface_substitutes" in error
                for error in substitute_audit["errors"]
            )
        )

    def test_level_surface_confound_is_disclosed_and_matched(self) -> None:
        report = audit_level_surface_confound(R26_13)
        self.assertEqual(
            "CONFOUND_DETECTED_MATCHED_CONTROL_READY", report["status"]
        )
        self.assertGreater(
            report["question_only_baseline"]["leave_one_match_out_macro_f1"],
            0.5,
        )
        self.assertLess(
            report["question_prefix_without_intervention_baseline"]
            ["leave_one_match_out_macro_f1"],
            0.3,
        )
        self.assertTrue(all(report["matched_control_gates"].values()))
        self.assertTrue(
            all(
                count == 4
                for levels in report["anchor_level_cell_counts"].values()
                for count in levels.values()
            )
        )

        scores = score_predictions(
            R26_13,
            ROOT
            / "analysis/r26_13_measurement_validity/ORACLE_PREDICTIONS.jsonl",
        )
        matched = scores["cross_level_anchor_diagnostic"]
        self.assertEqual("COMPLETE_MATCHED_CONTROL", matched["status"])
        self.assertTrue(matched["anchor_level_cells_complete"])

        identifiability = build_identifiability_admission(
            ROOT / "analysis/r26_13_measurement_validity",
            ROOT / "analysis/r26_13_request_readiness",
        )
        self.assertEqual("STATIC_IDENTIFIABILITY_FAIL", identifiability["status"])
        self.assertFalse(
            identifiability["gates"][
                "question_only_factual_answer_shortcut_absent"
            ]
        )
        self.assertTrue(
            all(
                passed
                for name, passed in identifiability["gates"].items()
                if name != "question_only_factual_answer_shortcut_absent"
            )
        )

    def test_answer_prior_shortcut_blocks_external_calibration(self) -> None:
        report = audit_answer_priors(R26_13)
        self.assertEqual("FAIL_QUESTION_ONLY_ANSWER_SHORTCUT", report["status"])
        self.assertEqual(
            ["ledger.BYE", "ledger.LEG_BYE", "ledger.PENALTY"],
            report["constant_scored_fields"],
        )
        self.assertGreater(
            report["baselines"]["unconditional"]["field_accuracy"], 0.64
        )
        nearest = report["baselines"]["question_surface_nearest_neighbor"]
        self.assertGreater(nearest["question"]["field_accuracy"], 0.90)
        self.assertGreater(nearest["question"]["full_record_exact"], 0.70)
        self.assertLess(nearest["question_prefix"]["full_record_exact"], 0.10)
        self.assertEqual(1.0, report["anchor_level_exact_record_purity"])
        self.assertFalse(all(report["gates"].values()))

    def test_anchor_standardized_bootstrap_is_complete_and_reproducible(self) -> None:
        predictions = (
            ROOT
            / "analysis/r26_13_measurement_validity/ORACLE_PREDICTIONS.jsonl"
        )
        instance_ids = sorted(
            path.parent.name
            for path in (R26_13 / "private").glob("match_*/private_gold.json")
        )
        rows = question_field_accuracy_rows(R26_13, predictions, instance_ids)
        first = anchor_standardized_match_block_bootstrap(
            rows, resamples=250, seed=26222
        )
        repeated = anchor_standardized_match_block_bootstrap(
            rows, resamples=250, seed=26222
        )
        self.assertEqual(first, repeated)
        self.assertEqual(25, first["anchor_level_cells"])
        self.assertEqual(20, first["match_blocks"])
        self.assertEqual(250, first["resamples"])
        self.assertGreaterEqual(first["attempted_draws"], first["resamples"])
        self.assertEqual(
            {level: 1.0 for level in ("L1", "L2", "L3", "L4", "L5")},
            first["level_point_estimates"],
        )
        self.assertTrue(
            all(
                interval["point"] == 0.0
                and interval["lower_95"] == 0.0
                and interval["upper_95"] == 0.0
                for interval in first["adjacent_gap_intervals"].values()
            )
        )

    def test_runner_and_paired_analyzer_support_input_forms_without_provider_calls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            output = root / "runs"
            config_path.write_text(json.dumps({
                "release_dir": str(R26_13),
                "output_dir": str(output),
                "runs": [
                    {
                        "run_id": "oracle_uniform",
                        "adapter": "oracle",
                        "test_only": True,
                        "instance_ids": ["match_0021"],
                        "target_batch_size": 5,
                        "public_input_form": "uniform"
                    },
                    {
                        "run_id": "oracle_proof_only",
                        "adapter": "oracle",
                        "test_only": True,
                        "instance_ids": ["match_0021"],
                        "target_batch_size": 5,
                        "public_input_form": "proof_only"
                    }
                ]
            }), encoding="utf-8")
            run_config(config_path)
            report = analyze_input_forms(
                R26_13,
                [output / "oracle_uniform", output / "oracle_proof_only"],
            )
            self.assertEqual("PASS", report["status"], report["errors"])
            self.assertEqual(
                0.0,
                report["diagnostics"]["proof_only_minus_uniform"]
                ["decision_field_macro_accuracy"],
            )
            paired = report["diagnostics"]["proof_only_vs_uniform_paired"]
            self.assertEqual(1, paired["match_blocks"])
            self.assertEqual(
                0.0,
                paired["metrics"]["decision_field_macro_accuracy"]
                ["right_minus_left"],
            )
            for form in ("uniform", "proof_only"):
                metadata = _read(output / f"oracle_{form}" / "RUN_METADATA.json")
                self.assertEqual(form, metadata["public_input_form"])

            errors = analyze_r26_errors(R26_13, output / "oracle_uniform")
            self.assertEqual(5, errors["questions"])
            gold = _read(
                R26_13 / "private/match_0021/private_gold.json"
            )
            expected_anchors = {
                str(answer["cross_level_anchor_family"])
                for answer in gold["decision_answers"]
            }
            self.assertEqual(
                expected_anchors,
                set(errors["by_cross_level_anchor_and_level"]),
            )
            self.assertEqual(
                5,
                sum(
                    row["questions"]
                    for levels in errors["by_cross_level_anchor_and_level"].values()
                    for row in levels.values()
                ),
            )

            proof_metadata_path = output / "oracle_proof_only" / "RUN_METADATA.json"
            proof_metadata = _read(proof_metadata_path)
            proof_metadata["temperature"] = 0.2
            proof_metadata_path.write_text(
                json.dumps(proof_metadata), encoding="utf-8"
            )
            confounded = analyze_input_forms(
                R26_13,
                [output / "oracle_uniform", output / "oracle_proof_only"],
            )
            self.assertEqual("INCOMPLETE_OR_INVALID", confounded["status"])
            self.assertIn(
                "non_equivalent_run_except_input_form:proof_only",
                confounded["errors"],
            )

    def test_language_surface_gate_covers_naturalized_generated_prose(self) -> None:
        report = audit_language_surface(R26_13)
        self.assertEqual(
            "AUTOMATED_PASS_HUMAN_REVIEW_REQUIRED", report["status"]
        )
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(0, report["exact_generated_nonrule_text_duplicates"])
        self.assertTrue(
            all(
                count == 0
                for count in report["known_degenerate_frame_counts"].values()
            )
        )

    def test_streaming_preflight_report_does_not_claim_empirical_release(self) -> None:
        report = _read(
            ROOT
            / "analysis/r26_13_measurement_validity/STREAMING_EXPANSION_PREFLIGHT_220.json"
        )
        self.assertEqual("STATIC_PREFLIGHT_PASS", report["status"])
        self.assertEqual(220, report["r26_instances_passed"])
        self.assertEqual(1100, report["questions_audited"])
        self.assertFalse(report["full_candidate_materialized"])
        self.assertEqual(0, report["provider_requests_made"])
        self.assertTrue(
            report["static_gates"]["no_known_language_surface_degeneration"]
        )
        self.assertTrue(
            report["static_gates"]["five_by_five_anchor_level_cells_balanced"]
        )

    def test_admission_separates_static_pass_from_empirical_authorization(self) -> None:
        analysis = ROOT / "analysis/r26_13_measurement_validity"
        with tempfile.TemporaryDirectory() as directory:
            report = build_admission_report(R26_13, analysis, Path(directory))
        self.assertEqual("STATIC_ADMISSION_FAIL", report["status"])
        self.assertFalse(report["static_constructability_220"])
        self.assertTrue(report["static_gates"]["independent_rebuild_byte_identical"])
        self.assertFalse(
            report["static_gates"][
                "question_only_factual_answer_shortcut_absent"
            ]
        )
        self.assertFalse(report["empirical_difficulty_calibrated"])
        self.assertFalse(report["full_220_materialization_authorized"])
        self.assertIn(
            "R26_13_PILOT20_TWO_STRONG_MODEL_FAMILIES_NOT_RUN",
            report["blockers"],
        )
        self.assertIn("QUESTION_ONLY_FACTUAL_ANSWER_SHORTCUT", report["blockers"])

    def test_zero_request_preflight_and_fault_attribution_pass(self) -> None:
        preflight = compile_sentinel_preflight(
            ROOT / "eval_configs/r26_13_glm53_flash_uniform_sentinel5_blocked.json",
            ROOT / "design/r26_13_sentinel5_request_contract.json",
        )
        self.assertEqual("NOT_READY", preflight["status"])
        self.assertEqual(0, preflight["provider_requests_made"])
        self.assertGreaterEqual(preflight["minimum_oracle_output_headroom_ratio"], 1.25)
        self.assertTrue(
            preflight["gates"]["complete_anchor_by_level_latin_square"]
        )
        self.assertFalse(
            preflight["gates"]["no_question_only_factual_answer_shortcut"]
        )
        faults = audit_protocol_fault_matrix(R26_13)
        self.assertEqual("PASS", faults["status"])
        self.assertEqual(0, faults["provider_requests_made"])
        semantic = [
            case for case in faults["cases"]
            if case["expected_layer"] == "semantic"
        ]
        self.assertEqual(4, len(semantic))
        self.assertTrue(
            all(case["sensitivity_fingerprint_pass"] for case in semantic)
        )

    def test_diagnostic_escalation_policy_stops_or_proceeds_by_value(self) -> None:
        contract = _read(ROOT / "design/r26_13_diagnostic_escalation_contract.json")
        pending = decide_next_diagnostic(contract)
        self.assertEqual(
            "AWAIT_EXPLICIT_AUTHORIZATION_FOR_UNIFORM_SENTINEL5",
            pending["next_action"],
        )
        shortcut = decide_next_diagnostic(
            contract,
            static_readiness=audit_answer_priors(R26_13),
        )
        self.assertEqual(
            "STOP_AND_REPAIR_QUESTION_ONLY_ANSWER_SHORTCUT",
            shortcut["next_action"],
        )
        invalid = decide_next_diagnostic(
            contract,
            uniform={"officially_eligible": False, "eligibility_failures": ["truncated"]},
        )
        self.assertEqual("STOP_AND_REPAIR_PROTOCOL", invalid["next_action"])
        useful = decide_next_diagnostic(
            contract,
            uniform={
                "officially_eligible": True,
                "scores": {
                    "decision_field_macro_accuracy": 0.6,
                    "minimal_evidence_edge_f1": 0.7,
                    "factual_evidence_chain_joint_exact": 0.4,
                },
            },
        )
        self.assertEqual(
            "AUTHORIZE_PAIRED_PROOF_ONLY_SENTINEL5", useful["next_action"]
        )
        unnecessary = decide_next_diagnostic(
            contract,
            uniform={
                "officially_eligible": True,
                "scores": {
                    "decision_field_macro_accuracy": 0.8,
                    "minimal_evidence_edge_f1": 0.8,
                    "factual_evidence_chain_joint_exact": 0.8,
                },
            },
        )
        self.assertEqual(
            "STOP_PROOF_ONLY_HAS_NO_DECISION_VALUE", unnecessary["next_action"]
        )

        authority = validate_adjustment_authority(
            ROOT / "design/r26_13_adjustment_authority_addendum.json"
        )
        self.assertEqual("PASS", authority["status"], authority["errors"])
        self.assertFalse(authority["sentinel_content_mutation_permitted"])
        self.assertFalse(authority["one_family_promotion_permitted"])


if __name__ == "__main__":
    unittest.main()
