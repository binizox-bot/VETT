from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vett_eval.runner import (
    _R26_ITEM_SCHEMA,
    _evidence_relations_by_target,
    _normalize_response,
    _public_span_ids,
    _request_record,
)
from vett_r26.content_dependency import audit_content_dependency_feasibility
from vett_r26.content_dependency_audit import audit_content_dependency_release
from vett_r26.content_dependency_release import (
    verify_content_dependency_determinism,
)
from vett_r26.evaluation import score_predictions
from vett_r26.structural_shortcut_audit import audit_structural_shortcuts


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "r26_14_answer_blind_candidate_v2"
CANDIDATE = ROOT / "r26_15_content_dependency_candidate_v3"
ANALYSIS = ROOT / "analysis/r26_15_content_dependency"
CONTRACT = ROOT / "design/r26_15_content_dependency_contract.json"
STRUCTURAL_CONTRACT = (
    ROOT / "design/r26_14_structural_shortcut_audit_contract.json"
)


class R2615ContentDependencyTests(unittest.TestCase):
    def test_frozen_dependency_design_is_feasible(self) -> None:
        report = audit_content_dependency_feasibility(PARENT, CONTRACT)
        self.assertEqual("FEASIBLE", report["status"])
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(324, report["proposed_content_dependency_edges"])
        self.assertTrue(
            report["gates"][
                "every_question_links_its_counterfactual_changed_field"
            ]
        )
        self.assertEqual(38, report["maximum_augmented_edges_per_question"])
        self.assertEqual(
            0.0,
            report["topology_information_gain"][
                "old_role_template_content_dependency_edge_recall"
            ],
        )

    def test_candidate_is_a_narrow_graph_only_extension(self) -> None:
        report = audit_content_dependency_release(
            PARENT, CANDIDATE, CONTRACT
        )
        self.assertEqual("PASS", report["status"], report["errors"][:10])
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(0, report["public_document_changes"])
        self.assertEqual(0, report["public_question_changes"])
        self.assertEqual(0, report["semantic_field_changes"])
        self.assertEqual(0, report["span_membership_changes"])
        self.assertEqual(0, report["inherited_edge_changes"])
        self.assertEqual(324, report["content_dependency_edges"])
        self.assertEqual(100, report["intervention_linked_questions"])

    def test_role_template_no_longer_reconstructs_the_complete_graph(self) -> None:
        report = audit_structural_shortcuts(CANDIDATE, STRUCTURAL_CONTRACT)
        self.assertEqual("PASS", report["status"])
        role_oracle = report["role_oracle_topology_reconstructability"]
        self.assertEqual(0.0, role_oracle["edge_exact"])
        self.assertEqual(0.93896, role_oracle["edge_f1"])
        self.assertLessEqual(
            report["question_only_topology_prior"][
                "typed_relation_count_signature_exact"
            ],
            0.10,
        )

    def test_oracle_and_edge_mutation_expose_content_linking(self) -> None:
        oracle_path = ANALYSIS / "ORACLE_PREDICTIONS_V3.jsonl"
        score = score_predictions(CANDIDATE, oracle_path)
        self.assertEqual(1.0, score["minimal_evidence_edge_f1"])
        self.assertEqual(1.0, score["conditional_edge_link_f1"])
        self.assertEqual(
            1.0,
            score["minimal_evidence_edge_f1_by_relation_group"][
                "content_dependency"
            ],
        )
        rows = [
            json.loads(line)
            for line in oracle_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        first = rows[0]["decision_predictions"][0]
        index = next(
            index
            for index, edge in enumerate(first["evidence_edges"])
            if edge["relation"] == "conditions_rule"
        )
        first["evidence_edges"].pop(index)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing_content_edge.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True)
                    for row in rows
                )
                + "\n",
                encoding="utf-8",
            )
            mutated = score_predictions(CANDIDATE, path)
        self.assertEqual(1.0, mutated["decision_field_macro_accuracy"])
        self.assertEqual(1.0, mutated["gold_edge_endpoint_recovery_rate"])
        self.assertLess(mutated["conditional_edge_link_f1"], 1.0)
        self.assertLess(
            mutated["minimal_evidence_edge_f1_by_relation_group"][
                "content_dependency"
            ],
            1.0,
        )
        self.assertLess(mutated["factual_evidence_chain_joint_exact"], 1.0)

    def test_build_is_byte_deterministic_and_runner_accepts_new_relation(self) -> None:
        report = verify_content_dependency_determinism(
            PARENT, CANDIDATE, CONTRACT
        )
        self.assertEqual("PASS", report["status"])
        self.assertEqual(0, report["byte_mismatch_count"])
        self.assertTrue(report["manifest_byte_identical"])
        relations = _R26_ITEM_SCHEMA["properties"]["evidence_edges"]["items"][
            "properties"
        ]["relation"]["enum"]
        self.assertIn("conditions_rule", relations)
        self.assertEqual(
            48,
            _R26_ITEM_SCHEMA["properties"]["evidence_edges"]["maxItems"],
        )

    def test_runner_relation_vocabulary_is_release_scoped(self) -> None:
        old_summary = json.loads(
            (PARENT / "RELEASE_SUMMARY.json").read_text(encoding="utf-8")
        )
        match_id = str(old_summary["match_ids"][0])
        old_public = json.loads(
            (PARENT / "public" / match_id / "public_instance.json").read_text(
                encoding="utf-8"
            )
        )
        new_public = json.loads(
            (CANDIDATE / "public" / match_id / "public_instance.json").read_text(
                encoding="utf-8"
            )
        )
        old_question = old_public["decision_question_schema"][0]
        new_question = new_public["decision_question_schema"][0]
        old_request = _request_record(
            PARENT, old_public, [old_question], 0, "r26_decision"
        )
        new_request = _request_record(
            CANDIDATE, new_public, [new_question], 0, "r26_decision"
        )
        def relation_enum(request: dict) -> list[str]:
            return request["response_schema"]["properties"][
                "decision_predictions"
            ]["items"]["properties"]["evidence_edges"]["items"][
                "properties"
            ]["relation"]["enum"]

        self.assertNotIn("conditions_rule", relation_enum(old_request))
        self.assertIn("conditions_rule", relation_enum(new_request))
        self.assertIn("conditions_rule", new_request["user_prompt"])

        new_gold = json.loads(
            (CANDIDATE / "private" / match_id / "private_gold.json").read_text(
                encoding="utf-8"
            )
        )["decision_answers"][0]
        response = {
            "instance_id": match_id,
            "decision_predictions": [{
                "question_id": new_gold["question_id"],
                "decision_record": new_gold["decision_record"],
                "state": new_gold["state"],
                "evidence_spans": new_gold["minimum_evidence_spans"],
                "rejected_evidence_spans": new_gold[
                    "rejected_evidence_spans"
                ],
                "evidence_edges": new_gold["minimum_evidence_edges"],
                "counterfactual_record": new_gold["counterfactual"][
                    "decision_record"
                ],
                "counterfactual_state": new_gold["counterfactual"]["state"],
                "explanation": "oracle protocol check",
                "confidence": 1.0,
            }],
        }
        normalized, errors = _normalize_response(
            response,
            match_id,
            {str(new_gold["question_id"])},
            "r26_decision",
            evidence_span_ids=_public_span_ids(new_public),
            evidence_relations_by_target=_evidence_relations_by_target(
                [new_question]
            ),
        )
        self.assertFalse(errors)
        self.assertIn(str(new_gold["question_id"]), normalized)

        _, legacy_errors = _normalize_response(
            response,
            match_id,
            {str(new_gold["question_id"])},
            "r26_decision",
            evidence_span_ids=_public_span_ids(new_public),
            evidence_relations_by_target=_evidence_relations_by_target(
                [old_question]
            ),
        )
        self.assertTrue(
            any("evidence edge" in error and "invalid" in error for error in legacy_errors)
        )

    def test_full_cohort_content_dependency_preflight_passes(self) -> None:
        report = json.loads(
            (
                ANALYSIS
                / "STREAMING_EXPANSION_PREFLIGHT_220_V3.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual("STATIC_PREFLIGHT_PASS", report["status"])
        self.assertTrue(all(report["static_gates"].values()))
        self.assertEqual(3564, report["content_dependency_edges"])
        self.assertEqual(
            1100,
            report["content_dependency_intervention_linked_questions"],
        )
        self.assertEqual(0, report["provider_requests_made"])

    def test_static_admission_is_fingerprinted_and_empirically_blocked(self) -> None:
        report = json.loads(
            (ANALYSIS / "STATIC_ADMISSION_V3.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            "STATIC_CANDIDATE_PASS_EMPIRICAL_BLOCKED", report["status"]
        )
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(0, report["provider_requests_made"])
        self.assertEqual(0.0, report["pilot"]["role_template_edge_exact"])
        self.assertEqual(324, report["pilot"]["content_dependency_edges"])
        self.assertEqual(3564, report["full_cohort"]["content_dependency_edges"])
        self.assertEqual(
            report["input_fingerprints"]["candidate_manifest"]["sha256"],
            report["pilot"]["manifest_sha256"],
        )
        boundary = report["next_empirical_boundary"]
        self.assertFalse(boundary["execution_authorized"])
        self.assertEqual(0, boundary["provider_requests_made"])
        self.assertEqual(5, boundary["matches"])
        self.assertEqual(25, boundary["questions"])
        self.assertLess(boundary["estimated_zero_cache_cost_cny"], 1.0)
        self.assertGreater(
            boundary["minimum_oracle_output_headroom_ratio"], 1.5
        )


if __name__ == "__main__":
    unittest.main()
