from __future__ import annotations

import json
import copy
import re
import sys
import tempfile
import unittest
from pathlib import Path

from vett_eval.analysis import analyze_r26_run
from vett_eval.runner import (
    R26_EDGE_DERIVED_ONTOLOGY,
    R26_EVIDENCE_GRAPH_ONTOLOGY,
    _evidence_grounding_warnings,
    _evidence_relations_by_target,
    _normalize_response,
    _request_record,
    estimate_config,
    run_config,
)
from vett_r26.auditor import audit_instance, audit_release
from vett_r26.citation_stability_audit import audit_citation_stability
from vett_r26.evaluation import score_predictions, write_oracle_predictions
from vett_r26.error_analysis import analyze_r26_errors
from vett_r26.edge7_subset_diagnostic import build_edge7_subset_diagnostic
from vett_r26.exact_target_map_audit import audit_exact_target_map
from vett_r26.generator import augment_r25_instance, reconstruct_r25_documents
from vett_r26.mutations import audit_position_variants, make_position_variant
from vett_r26.protocol_citation_admission import build_protocol_citation_admission
from vett_r26.protocol_smoke_outcome import build_protocol_smoke_outcome
from vett_r26.scenario_kernel import natural_identity
from vett_r26.renderer import source_aliases
from vett_r26.sentinel_preflight import (
    _oracle_response as preflight_oracle_response,
    compile_sentinel_preflight,
)
from vett_r26.shortcut_audit import audit_shortcuts
from vett_r26.spec import EVIDENCE_RELATIONS, LEVELS, POSITION_FORMS, SEMANTIC_BRIDGE_DEPTH, VERSION


ROOT = Path(__file__).resolve().parents[1]
CURRENT_RELEASE = ROOT / "r26_authority_binding_pilot"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class R26Tests(unittest.TestCase):
    def test_natural_identity_is_deterministic_and_level_scaled(self) -> None:
        gold = _read(ROOT / "r25_diagnostic_pilot/private/match_0066/private_gold.json")
        first = natural_identity("match_0066", "q", gold, index=2, depth=5)
        second = natural_identity("match_0066", "q", gold, index=2, depth=5)
        self.assertEqual(first, second)
        self.assertEqual(5, len(first.labels))
        self.assertNotIn("CASE-", str(first))
        self.assertNotIn("OBS-", str(first))

    def test_single_instance_preserves_r25_semantics_and_reconstructs(self) -> None:
        match_id = "match_0066"
        base = ROOT / "r25_diagnostic_pilot"
        public = _read(base / "public" / match_id / "public_instance.json")
        gold = _read(base / "private" / match_id / "private_gold.json")
        evidence = _read(base / "private" / match_id / "private_evidence.json")
        bundle = augment_r25_instance(public, gold, evidence, variant_index=5)
        report = audit_instance(
            bundle.public,
            bundle.gold,
            bundle.evidence,
            base_public=public,
            base_gold=gold,
        )
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(public["documents"], reconstruct_r25_documents(
            bundle.public["documents"], bundle.evidence["r26_text_patches"]
        ))
        self.assertTrue(all("level" not in item for item in bundle.public["decision_question_schema"]))
        for old, new in zip(gold["decision_answers"], bundle.gold["decision_answers"]):
            self.assertEqual(old["decision_record"], new["decision_record"])
            self.assertEqual(old["counterfactual"], new["counterfactual"])
            self.assertLessEqual(set(old["minimum_evidence_spans"]), set(new["minimum_evidence_spans"]))
            self.assertEqual(SEMANTIC_BRIDGE_DEPTH[new["level"]], new["semantic_bridge_depth"])
            self.assertTrue(new["minimum_evidence_edges"])
            self.assertTrue(new["rejected_evidence_spans"])
            self.assertFalse(set(new["rejected_evidence_spans"]) & set(new["minimum_evidence_spans"]))
            self.assertTrue(all(
                edge["relation"] in EVIDENCE_RELATIONS
                for edge in new["minimum_evidence_edges"]
            ))
            decisive = set(new["minimum_evidence_spans"])
            conflicts = set(new["distractor_spans"]) - set(old.get("distractor_spans", []))
            self.assertFalse(conflicts & decisive)
        for question in bundle.public["decision_question_schema"]:
            self.assertEqual(
                f"decision:{question['question_id']}",
                question["r26_public_contract"]["decision_node"],
            )

    def test_cyclic_evidence_graph_is_rejected(self) -> None:
        match_id = "match_0066"
        base = ROOT / "r25_diagnostic_pilot"
        public = _read(base / "public" / match_id / "public_instance.json")
        gold = _read(base / "private" / match_id / "private_gold.json")
        evidence = _read(base / "private" / match_id / "private_evidence.json")
        bundle = augment_r25_instance(public, gold, evidence, variant_index=5)
        answer = bundle.gold["decision_answers"][0]
        edge = next(
            item for item in answer["minimum_evidence_edges"]
            if item["relation"] == "supports_decision"
        )
        edge["target_id"] = answer["question_id"]
        report = audit_instance(
            bundle.public,
            bundle.gold,
            bundle.evidence,
            base_public=public,
            base_gold=gold,
        )
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("cyclic" in error for error in report["errors"]))

    def test_neutral_source_alias_binding_is_audited(self) -> None:
        match_id = "match_0066"
        base = ROOT / "r25_diagnostic_pilot"
        public = _read(base / "public" / match_id / "public_instance.json")
        gold = _read(base / "private" / match_id / "private_gold.json")
        evidence = _read(base / "private" / match_id / "private_evidence.json")
        bundle = augment_r25_instance(public, gold, evidence, variant_index=5)
        answer = bundle.gold["decision_answers"][0]
        qid = answer["question_id"]
        accepted_alias, rejected_alias = source_aliases(qid)
        fact_id = next(
            claim["inserted_span_id"]
            for claim in bundle.evidence["r25_evidence_claims"]
            if claim.get("question_id") == qid and claim.get("role") == "incident_fact"
        )
        for document in bundle.public["documents"]:
            for span in document["spans"]:
                if span["span_id"] == fact_id:
                    span["text"] = span["text"].replace(accepted_alias, rejected_alias)
        report = audit_instance(
            bundle.public,
            bundle.gold,
            bundle.evidence,
            base_public=public,
            base_gold=gold,
        )
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any(
            "accepted fact lacks controlling source alias" in error
            for error in report["errors"]
        ))

    def test_position_variants_preserve_semantics(self) -> None:
        match_id = "match_0066"
        release = CURRENT_RELEASE
        public = _read(release / "public" / match_id / "public_instance.json")
        gold = _read(release / "private" / match_id / "private_gold.json")
        variants = {form: make_position_variant(public, gold, form) for form in POSITION_FORMS}
        report = audit_position_variants(public, gold, variants)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertLessEqual(report["forms"]["head"]["mean_relative_position"], 0.30)
        self.assertGreaterEqual(report["forms"]["tail"]["mean_relative_position"], 0.70)

    def test_built_pilot_static_audit_and_oracle(self) -> None:
        release = CURRENT_RELEASE
        report = audit_release(release)
        self.assertEqual("PASS", report["status"], report["errors"])
        self.assertEqual(20, report["passed_instances"])
        self.assertEqual(100, report["decision_questions"])
        self.assertEqual(0, report["public_level_leaks"])
        means = report["mean_necessary_evidence_by_level"]
        self.assertTrue(all(means[LEVELS[index]] < means[LEVELS[index + 1]] for index in range(4)))
        with tempfile.TemporaryDirectory() as directory:
            predictions = Path(directory) / "oracle.jsonl"
            write_oracle_predictions(release, predictions, test_only=True)
            score = score_predictions(release, predictions)
            rows = [json.loads(line) for line in predictions.read_text(encoding="utf-8").splitlines()]

            wrong_positive_rows = copy.deepcopy(rows)
            first_positive = wrong_positive_rows[0]["decision_predictions"][0]
            first_positive["evidence_spans"].append(first_positive["rejected_evidence_spans"][0])
            wrong_positive = Path(directory) / "wrong_positive_span.jsonl"
            wrong_positive.write_text(
                "\n".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True)
                    for row in wrong_positive_rows
                ) + "\n",
                encoding="utf-8",
            )
            wrong_positive_score = score_predictions(release, wrong_positive)

            wrong_rejected_rows = copy.deepcopy(rows)
            wrong_rejected_rows[0]["decision_predictions"][0]["rejected_evidence_spans"] = []
            wrong_rejected = Path(directory) / "wrong_rejected_span.jsonl"
            wrong_rejected.write_text(
                "\n".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True)
                    for row in wrong_rejected_rows
                ) + "\n",
                encoding="utf-8",
            )
            wrong_rejected_score = score_predictions(release, wrong_rejected)

            wrong_edge_rows = copy.deepcopy(rows)
            wrong_edge = next(
                edge for edge in wrong_edge_rows[0]["decision_predictions"][0]["evidence_edges"]
                if edge["relation"] != "rejects"
            )
            wrong_edge["relation"] = "rejects"
            corrupted = Path(directory) / "wrong_edge.jsonl"
            corrupted.write_text(
                "\n".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True)
                    for row in wrong_edge_rows
                ) + "\n",
                encoding="utf-8",
            )
            wrong_edge_score = score_predictions(release, corrupted)
        self.assertEqual(1.0, score["factual_record_macro_accuracy"])
        self.assertEqual(1.0, score["minimal_evidence_f1"])
        self.assertEqual(1.0, score["rejected_evidence_f1"])
        self.assertEqual(1.0, score["minimal_evidence_edge_f1"])
        self.assertEqual(1.0, score["evidence_chain_joint_exact"])
        self.assertEqual(1.0, score["factual_evidence_chain_joint_exact"])

        self.assertLess(wrong_positive_score["minimal_evidence_f1"], 1.0)
        self.assertEqual(1.0, wrong_positive_score["rejected_evidence_f1"])
        self.assertEqual(1.0, wrong_positive_score["minimal_evidence_edge_f1"])
        self.assertEqual(0.99, wrong_positive_score["evidence_chain_joint_exact"])

        self.assertEqual(1.0, wrong_rejected_score["minimal_evidence_f1"])
        self.assertLess(wrong_rejected_score["rejected_evidence_f1"], 1.0)
        self.assertEqual(1.0, wrong_rejected_score["minimal_evidence_edge_f1"])
        self.assertEqual(0.99, wrong_rejected_score["evidence_chain_joint_exact"])

        self.assertEqual(1.0, wrong_edge_score["minimal_evidence_f1"])
        self.assertEqual(1.0, wrong_edge_score["rejected_evidence_f1"])
        self.assertLess(wrong_edge_score["minimal_evidence_edge_f1"], 1.0)
        self.assertEqual(0.99, wrong_edge_score["evidence_chain_joint_exact"])
        self.assertEqual(1.0, score["paired_factual_counterfactual_exact"])

    def test_built_pilot_has_no_declared_static_shortcut(self) -> None:
        report = audit_shortcuts(CURRENT_RELEASE)
        self.assertEqual("PASS", report["status"], report["gates"])
        recall = report["literal_query_top_k_evidence_recall_by_level"]
        self.assertTrue(all(recall[level] < 0.45 for level in ("L3", "L4", "L5")))
        self.assertLess(recall["L5"], recall["L3"])
        self.assertLess(
            report["top_20pct_document_necessary_doc_recall_by_level"]["L5"],
            0.70,
        )
        self.assertGreater(
            report["mean_necessary_document_fraction_by_level"]["L5"],
            0.20,
        )
        self.assertTrue(all(
            share <= 0.30
            for share in report["generated_surface_max_skeleton_share_by_role"].values()
        ))
        self.assertLessEqual(
            report["authority_style_only_baseline"]["leave_one_match_out_macro_f1"],
            0.60,
        )

    def test_unified_runner_recognizes_r26_as_decision_task(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(CURRENT_RELEASE),
                "output_dir": str(Path(directory) / "runs"),
                "runs": [{
                    "run_id": "r26_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }), encoding="utf-8")
            estimate = estimate_config(config)
            result = run_config(config)
            prediction_row = json.loads(
                (Path(directory) / "runs/r26_oracle/predictions.jsonl").read_text(encoding="utf-8").splitlines()[0]
            )
        self.assertEqual("r26_decision", estimate["task_type"])
        self.assertEqual("COMPLETE", result["status"])
        self.assertTrue(all(item["evidence_edges"] for item in prediction_row["decision_predictions"]))
        self.assertTrue(all(item["rejected_evidence_spans"] for item in prediction_row["decision_predictions"]))
        self.assertEqual(VERSION, _read(CURRENT_RELEASE / "RELEASE_SUMMARY.json")["dataset_version"])

    def test_r26_runner_exposes_explicit_edge_ontology(self) -> None:
        public = _read(CURRENT_RELEASE / "public/match_0066/public_instance.json")
        target = public["decision_question_schema"][:1]
        explicit = _request_record(
            CURRENT_RELEASE, public, target, 0, "r26_decision"
        )
        implicit = _request_record(
            CURRENT_RELEASE, public, target, 0, "r26_decision",
            edge_ontology_version="implicit_v1",
        )
        self.assertIn(
            json.dumps(R26_EVIDENCE_GRAPH_ONTOLOGY, ensure_ascii=False, separators=(",", ":")),
            explicit["user_prompt"],
        )
        self.assertEqual("R26-C3-EDGE-3-ROLE-SPLIT", explicit["evaluation_contract_version"])
        self.assertNotIn("evidence_graph_ontology", implicit["user_prompt"])
        self.assertEqual("R26-C3-EDGE-1-IMPLICIT", implicit["evaluation_contract_version"])

    def test_edge_derived_protocol_has_one_rejection_source_of_truth(self) -> None:
        public = _read(CURRENT_RELEASE / "public/match_0066/public_instance.json")
        target = public["decision_question_schema"][:1]
        request = _request_record(
            CURRENT_RELEASE,
            public,
            target,
            0,
            "r26_decision",
            evidence_role_protocol="edge_derived_v3",
        )
        item = request["response_schema"]["properties"]["decision_predictions"]["items"]
        self.assertNotIn("rejected_evidence_spans", item["properties"])
        self.assertNotIn("rejected_evidence_spans", item["required"])
        self.assertEqual(
            "R26-C3-EDGE-4-DERIVED-REJECTION",
            request["evaluation_contract_version"],
        )
        self.assertIn(
            json.dumps(
                R26_EDGE_DERIVED_ONTOLOGY,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            request["user_prompt"],
        )
        self.assertIn(
            "do not output rejected_evidence_spans",
            request["user_prompt"].lower(),
        )
        self.assertNotIn(
            "same-incident conflicting fact spans that must be explicitly rejected",
            request["user_prompt"],
        )

    def test_edge_derived_protocol_scores_missing_reject_edge_instead_of_invalidating_batch(self) -> None:
        fixture = _read(
            ROOT / "tests/fixtures/r26_gate3_cross_incident_binding_failure.json"
        )
        public = _read(CURRENT_RELEASE / "public/match_0066/public_instance.json")
        public_span_ids = {
            span["span_id"]
            for document in public["documents"]
            for span in document["spans"]
        }
        item = {
            "question_id": fixture["question_id"],
            **copy.deepcopy(fixture["prediction"]),
        }
        item.pop("rejected_evidence_spans")
        normalized, errors = _normalize_response(
            {
                "instance_id": "match_0066",
                "decision_predictions": [item],
            },
            "match_0066",
            {fixture["question_id"]},
            "r26_decision",
            evidence_span_ids=public_span_ids,
            evidence_role_protocol="edge_derived_v3",
        )
        self.assertEqual([], errors)
        failed_question = normalized[fixture["question_id"]]
        self.assertEqual([], failed_question["rejected_evidence_spans"])
        # The protocol derives what the model actually proved; it does not insert
        # the private gold span or otherwise repair the semantic error.
        self.assertNotIn(
            fixture["gold_rejected_evidence_spans"][0],
            failed_question["rejected_evidence_spans"],
        )

    def test_edge_derived_protocol_runs_end_to_end_without_private_repair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(CURRENT_RELEASE),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "edge_derived_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                }],
            }), encoding="utf-8")
            run_config(config)
            run_dir = root / "runs/edge_derived_oracle"
            metadata = _read(run_dir / "RUN_METADATA.json")
            checkpoint = _read(run_dir / "checkpoints/match_0066/batch_000.json")
            predictions = run_dir / "predictions.jsonl"
            score = score_predictions(
                CURRENT_RELEASE, predictions, instance_ids=["match_0066"]
            )
        self.assertEqual("edge_derived_v3", metadata["r26_evidence_role_protocol"])
        self.assertEqual("OK", checkpoint["batch_record"]["status"])
        self.assertEqual(
            "R26-C3-EDGE-4-DERIVED-REJECTION",
            checkpoint["batch_record"]["evaluation_contract_version"],
        )
        for prediction in checkpoint["predictions"].values():
            derived = sorted(
                edge["target_id"]
                for edge in prediction["evidence_edges"]
                if edge["relation"] == "rejects"
            )
            self.assertEqual(derived, prediction["rejected_evidence_spans"])
        self.assertEqual(1.0, score["rejected_evidence_f1"])
        self.assertEqual(1.0, score["minimal_evidence_edge_f1"])

    def test_request_bound_protocol_removes_only_redundant_response_identity(self) -> None:
        public = _read(CURRENT_RELEASE / "public/match_0066/public_instance.json")
        target = public["decision_question_schema"][:1]
        request = _request_record(
            CURRENT_RELEASE,
            public,
            target,
            0,
            "r26_decision",
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="request_bound_v2",
        )
        schema = request["response_schema"]
        payload = json.loads(request["user_prompt"][request["user_prompt"].index("{"):])
        self.assertNotIn("instance_id", schema["properties"])
        self.assertNotIn("instance_id", schema["required"])
        self.assertEqual(1, schema["properties"]["decision_predictions"]["minItems"])
        self.assertEqual(1, schema["properties"]["decision_predictions"]["maxItems"])
        self.assertEqual(
            [target[0]["question_id"]],
            schema["properties"]["decision_predictions"]["items"]["properties"][
                "question_id"
            ]["enum"],
        )
        # Request identity remains present in the signed request; only the model's
        # redundant response copy is removed.
        self.assertEqual("match_0066", request["instance_id"])
        self.assertEqual("match_0066", payload["instance_id"])
        self.assertEqual("request_bound_v2", request["response_envelope_protocol"])
        self.assertEqual(
            "R26-C3-EDGE-6-EXACT-SPAN-ID-COPY",
            request["evaluation_contract_version"],
        )
        self.assertIn("do not output a top-level instance_id", request["user_prompt"].lower())

    def test_role_neutral_span_ids_are_copied_without_release_prefix(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        public = _read(release / "public/match_0066/public_instance.json")
        target = public["decision_question_schema"][:1]
        request = _request_record(
            release,
            public,
            target,
            0,
            "r26_decision",
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="request_bound_v2",
        )
        prompt = request["system_prompt"] + request["user_prompt"]
        self.assertNotIn("span_id beginning r25 or r26", prompt)
        self.assertIn("copied byte-for-byte", prompt)
        self.assertIn("s_<24 lowercase hexadecimal characters>", prompt)
        self.assertIn("never transform it into r25:s_..., r26:s_...", prompt)
        item = request["response_schema"]["properties"]["decision_predictions"]["items"]
        span_pattern = item["properties"]["evidence_spans"]["items"]["pattern"]
        node_pattern = item["properties"]["evidence_edges"]["items"]["properties"][
            "source_id"
        ]["pattern"]
        sample_span = public["documents"][0]["spans"][0]["span_id"]
        question_id = target[0]["question_id"]
        self.assertIsNotNone(re.fullmatch(span_pattern, sample_span))
        self.assertIsNone(re.fullmatch(span_pattern, f"r26:{sample_span}"))
        self.assertIsNotNone(re.fullmatch(node_pattern, sample_span))
        self.assertIsNotNone(re.fullmatch(node_pattern, question_id))
        self.assertIsNotNone(re.fullmatch(node_pattern, f"decision:{question_id}"))
        self.assertIsNone(re.fullmatch(node_pattern, f"r26:{sample_span}"))
        self.assertEqual(
            "R26-C3-EDGE-6-EXACT-SPAN-ID-COPY",
            request["evaluation_contract_version"],
        )

    def test_unknown_evidence_is_preregistered_semantic_false_positive(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        public = _read(release / "public/match_0066/public_instance.json")
        gold = _read(release / "private/match_0066/private_gold.json")
        target_schema = public["decision_question_schema"]
        public_ids = {
            span["span_id"]
            for document in public["documents"]
            for span in document["spans"]
        }
        items = []
        for answer in gold["decision_answers"]:
            items.append({
                "question_id": answer["question_id"],
                "decision_record": answer["decision_record"],
                "state": answer["state"],
                "evidence_spans": list(answer["minimum_evidence_spans"]),
                "evidence_edges": copy.deepcopy(answer["minimum_evidence_edges"]),
                "counterfactual_record": answer["counterfactual"]["decision_record"],
                "counterfactual_state": answer["counterfactual"]["state"],
                "explanation": "test",
                "confidence": 0.5,
            })
        old_id = items[2]["evidence_spans"][1]
        unknown_id = "s_ffffffffffffffffffffffff"
        self.assertNotIn(unknown_id, public_ids)
        items[2]["evidence_spans"][1] = unknown_id
        for edge in items[2]["evidence_edges"]:
            if edge["source_id"] == old_id:
                edge["source_id"] = unknown_id
            if edge["target_id"] == old_id:
                edge["target_id"] = unknown_id
        response = {"decision_predictions": items}
        common = {
            "instance_id": "match_0066",
            "allowed": {item["question_id"] for item in target_schema},
            "task_type": "r26_decision",
            "evidence_span_ids": public_ids,
            "evidence_role_protocol": "edge_derived_v3",
            "response_envelope_protocol": "request_bound_v2",
            "evidence_relations_by_target": _evidence_relations_by_target(
                target_schema
            ),
        }
        _, legacy_errors = _normalize_response(response, **common)
        normalized, semantic_errors = _normalize_response(
            response,
            unknown_evidence_protocol="semantic_false_positive_v2",
            **common,
        )
        warnings = _evidence_grounding_warnings(normalized, public_ids)
        self.assertTrue(any("unknown evidence span IDs" in value for value in legacy_errors))
        self.assertEqual([], semantic_errors)
        self.assertEqual(1, len(warnings))
        self.assertEqual([unknown_id], warnings[0]["unknown_positive_span_ids"])
        self.assertTrue(warnings[0]["unknown_edges"])

        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            path = run_dir / "predictions.jsonl"
            path.write_text(json.dumps({
                "instance_id": "match_0066",
                "decision_predictions": [
                    {"question_id": qid, **value}
                    for qid, value in normalized.items()
                ],
            }) + "\n", encoding="utf-8")
            scores = score_predictions(
                release, path, instance_ids=["match_0066"]
            )
            (run_dir / "RUN_METADATA.json").write_text(json.dumps({
                "run_id": "semantic_unknown_test",
                "model": "local-fixture",
                "records": [{"instance_id": "match_0066", "batches": []}],
                "experiment_provenance": {
                    "calibration_stage": "single_protocol_gate"
                },
            }), encoding="utf-8")
            errors = analyze_r26_errors(release, run_dir)
        self.assertEqual(1.0, scores["factual_record_macro_accuracy"])
        self.assertEqual(1, scores["unknown_evidence_span_count"])
        self.assertEqual(1, scores["questions_with_unknown_evidence"])
        self.assertGreaterEqual(scores["unknown_evidence_edge_count"], 1)
        self.assertLess(scores["minimal_evidence_f1"], 1.0)
        self.assertLess(scores["minimal_evidence_edge_f1"], 1.0)
        diagnostic = next(
            row
            for row in errors["question_diagnostics"]
            if row["question_id"] == items[2]["question_id"]
        )
        self.assertIn(
            "UNKNOWN_EVIDENCE_SPAN_HALLUCINATION", diagnostic["labels"]
        )
        self.assertIn(
            "UNKNOWN_EVIDENCE_EDGE_HALLUCINATION", diagnostic["labels"]
        )
        self.assertEqual([unknown_id], diagnostic["unknown_positive_span_ids"])

        malformed = copy.deepcopy(response)
        malformed["decision_predictions"][2]["evidence_spans"][1] = "not-a-span"
        _, malformed_errors = _normalize_response(
            malformed,
            unknown_evidence_protocol="semantic_false_positive_v2",
            **common,
        )
        self.assertTrue(any(
            "malformed unknown evidence span IDs" in value
            for value in malformed_errors
        ))

        foreign_node = copy.deepcopy(response)
        foreign_node["decision_predictions"][2]["evidence_edges"][0][
            "source_id"
        ] = "r25q_foreign"
        _, foreign_errors = _normalize_response(
            foreign_node,
            unknown_evidence_protocol="semantic_false_positive_v2",
            **common,
        )
        self.assertTrue(any(
            "unknown evidence edge node IDs" in value
            for value in foreign_errors
        ))

    def test_edge7_runner_keeps_unknown_evidence_as_warning(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stub = root / "semantic_unknown_stub.py"
            stub.write_text(
                """import json, sys
r=json.load(sys.stdin)
p=json.loads(r['user_prompt'][r['user_prompt'].index('{'):])
s=p['documents'][0]['spans'][0]['span_id']
u='s_ffffffffffffffffffffffff'
items=[]
for i,q in enumerate(p['requested_questions']):
 qid=q['question_id']; x=u if i==2 else s
 rec={'delivery_status':'LEGAL','counts_in_over':True,'dismissal':'NONE','total_runs':0,'batter_runs':0,'bowler_runs':0,'run_ledger':[{'account':'NONE','runs':0}]}
 state={'active_source':'DIRECT_OBSERVATION','initial_call_set':'NONE','observed_contact':'NONE','effective_delivery_status':'LEGAL','movement_runs_before_boundary_allowance':0,'boundary_allowance':0,'pre_wicket_ball_state':'NOT_APPLICABLE'}
 items.append({'question_id':qid,'decision_record':rec,'state':state,'evidence_spans':[x],'evidence_edges':[{'source_id':qid,'relation':'identifies','target_id':x}],'counterfactual_record':rec,'counterfactual_state':state,'explanation':'test','confidence':0.5})
print(json.dumps({'decision_predictions':items}))
""",
                encoding="utf-8",
            )
            config = root / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(release),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "edge7_warning",
                    "adapter": "command",
                    "command": [sys.executable, str(stub)],
                    "model": "local-stub",
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                    "r26_response_envelope_protocol": "request_bound_v2",
                    "r26_unknown_evidence_protocol": "semantic_false_positive_v2"
                }],
            }), encoding="utf-8")
            result = run_config(config)
            run_dir = root / "runs/edge7_warning"
            metadata = _read(run_dir / "RUN_METADATA.json")
            checkpoint = _read(
                run_dir / "checkpoints/match_0066/batch_000.json"
            )
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual("OK", checkpoint["batch_record"]["status"])
        self.assertEqual([], checkpoint["batch_record"]["validation_errors"])
        self.assertEqual(1, len(checkpoint["batch_record"]["semantic_warnings"]))
        self.assertEqual(
            "R26-C3-EDGE-7-SEMANTIC-UNKNOWN-EVIDENCE",
            checkpoint["batch_record"]["evaluation_contract_version"],
        )
        self.assertEqual(
            "semantic_false_positive_v2",
            metadata["r26_unknown_evidence_protocol"],
        )

    def test_citation_stability_audit_preserves_dataset_difficulty(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        contract = ROOT / "design/r26_16_citation_stability_audit_contract.json"
        with tempfile.TemporaryDirectory() as directory:
            report = audit_citation_stability(
                release, contract, Path(directory)
            )
        self.assertEqual("PASS_KEEP_DATASET_BYTES", report["status"])
        self.assertTrue(all(report["gates"].values()), report["errors"][:5])
        self.assertEqual(20, report["counts"]["matches"])
        self.assertEqual(0, report["counts"]["substitution_collisions"])
        self.assertGreaterEqual(
            report["minimum_gold_to_other_public_hamming_across_matches"], 3
        )

    def test_edge7_sentinel_is_locally_ready_and_execution_blocked(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        config = (
            ROOT
            / "eval_configs/r26_16_glm53_flash_uniform_sentinel5_edge7_blocked.json"
        )
        contract = ROOT / "design/r26_16_sentinel5_request_contract.json"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            isolated_config = _read(config)
            isolated_config["output_dir"] = str(root / "fresh-output")
            isolated_config_path = root / "blocked-config.json"
            isolated_config_path.write_text(
                json.dumps(isolated_config, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            preflight_path = root / "preflight.json"
            preflight = compile_sentinel_preflight(
                isolated_config_path, contract, preflight_path
            )
            admission = build_protocol_citation_admission(
                release,
                ROOT / "design/r26_16_unknown_evidence_preregistration.json",
                ROOT / "design/r26_16_unknown_evidence_metric_addendum.json",
                ROOT
                / "analysis/r26_16_citation_stability/CITATION_STABILITY_AUDIT.json",
                ROOT
                / "analysis/r26_16_unknown_evidence_replay/COUNTERFACTUAL_EDGE7_REPLAY.json",
                preflight_path,
                isolated_config_path,
            )
        self.assertEqual(
            "REQUEST_READY_BLOCKED_BY_AUTHORIZATION", preflight["status"]
        )
        self.assertEqual(0, preflight["provider_requests_made"])
        self.assertFalse(preflight["execution_authorized"])
        self.assertTrue(all(preflight["gates"].values()))
        self.assertTrue(all(
            item["semantic_unknown_evidence_probe_passed"]
            for item in preflight["per_match"]
        ))
        self.assertEqual(
            "LOCAL_PROTOCOL_AND_CITATION_PASS_EMPIRICAL_EDGE7_BLOCKED",
            admission["status"],
        )
        self.assertEqual("KEEP_R26_15_DATASET_BYTES", admission["dataset_mutation_decision"])
        self.assertFalse(admission["paper_level_difficulty_claim_authorized"])

    def test_request_bound_protocol_accepts_absent_identity_but_rejects_conflict(self) -> None:
        fixture = _read(
            ROOT / "tests/fixtures/r26_gate3_cross_incident_binding_failure.json"
        )
        public = _read(CURRENT_RELEASE / "public/match_0066/public_instance.json")
        public_span_ids = {
            span["span_id"]
            for document in public["documents"]
            for span in document["spans"]
        }
        item = {"question_id": fixture["question_id"], **copy.deepcopy(fixture["prediction"])}
        item.pop("rejected_evidence_spans")
        response = {"decision_predictions": [item]}
        normalized, errors = _normalize_response(
            response,
            "match_0066",
            {fixture["question_id"]},
            "r26_decision",
            evidence_span_ids=public_span_ids,
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="request_bound_v2",
        )
        self.assertEqual([], errors)
        self.assertEqual({fixture["question_id"]}, set(normalized))

        response["instance_id"] = "match_0220"
        _, conflict_errors = _normalize_response(
            response,
            "match_0066",
            {fixture["question_id"]},
            "r26_decision",
            evidence_span_ids=public_span_ids,
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="request_bound_v2",
        )
        self.assertIn("response instance_id mismatch", conflict_errors)

    def test_request_bound_protocol_runs_end_to_end_and_restores_output_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(CURRENT_RELEASE),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "request_bound_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                    "r26_response_envelope_protocol": "request_bound_v2",
                }],
            }), encoding="utf-8")
            run_config(config)
            run_dir = root / "runs/request_bound_oracle"
            metadata = _read(run_dir / "RUN_METADATA.json")
            checkpoint = _read(run_dir / "checkpoints/match_0066/batch_000.json")
            output_row = json.loads(
                (run_dir / "predictions.jsonl").read_text(encoding="utf-8").splitlines()[0]
            )
        self.assertEqual("request_bound_v2", metadata["r26_response_envelope_protocol"])
        self.assertEqual("OK", checkpoint["batch_record"]["status"])
        self.assertEqual(
            "R26-C3-EDGE-6-EXACT-SPAN-ID-COPY",
            checkpoint["batch_record"]["evaluation_contract_version"],
        )
        self.assertEqual("request_bound_v2", checkpoint["batch_record"]["response_envelope_protocol"])
        self.assertEqual("match_0066", output_row["instance_id"])
        self.assertEqual(5, len(output_row["decision_predictions"]))

    def test_exact_target_map_protocol_makes_target_coverage_structural(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        public = _read(release / "public/match_0066/public_instance.json")
        targets = public["decision_question_schema"]
        target_ids = [item["question_id"] for item in targets]
        request = _request_record(
            release,
            public,
            targets,
            0,
            "r26_decision",
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="exact_target_map_v3",
            unknown_evidence_protocol="semantic_false_positive_v2",
        )
        schema = request["response_schema"]
        predictions = schema["properties"]["decision_predictions"]
        self.assertEqual("object", predictions["type"])
        self.assertEqual(target_ids, predictions["required"])
        self.assertEqual(set(target_ids), set(predictions["properties"]))
        self.assertFalse(predictions["additionalProperties"])
        self.assertTrue(all(
            "question_id" not in item["properties"]
            and "question_id" not in item["required"]
            for item in predictions["properties"].values()
        ))
        self.assertEqual(
            "R26-C3-EDGE-8-EXACT-TARGET-MAP",
            request["evaluation_contract_version"],
        )
        self.assertIn(
            "property names are the exact requested question IDs",
            request["user_prompt"],
        )

        # The failure shape observed in match_0220 is no longer an accepted
        # envelope: a repeated-ID array cannot satisfy the target-keyed object.
        _, array_errors = _normalize_response(
            {"decision_predictions": [
                {"question_id": target_ids[0]} for _ in target_ids
            ]},
            "match_0066",
            set(target_ids),
            "r26_decision",
            response_envelope_protocol="exact_target_map_v3",
        )
        self.assertEqual(
            ["decision_predictions must be an exact target-keyed object"],
            array_errors,
        )

    def test_exact_target_map_protocol_runs_oracle_end_to_end(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(release),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "exact_target_map_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                    "r26_response_envelope_protocol": "exact_target_map_v3",
                    "r26_unknown_evidence_protocol": "semantic_false_positive_v2",
                }],
            }), encoding="utf-8")
            result = run_config(config)
            run_dir = root / "runs/exact_target_map_oracle"
            metadata = _read(run_dir / "RUN_METADATA.json")
            checkpoint = _read(
                run_dir / "checkpoints/match_0066/batch_000.json"
            )
            output_row = json.loads(
                (run_dir / "predictions.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()[0]
            )
        self.assertEqual("COMPLETE", result["status"])
        self.assertEqual(
            "exact_target_map_v3", metadata["r26_response_envelope_protocol"]
        )
        self.assertEqual("OK", checkpoint["batch_record"]["status"])
        self.assertEqual(
            "R26-C3-EDGE-8-EXACT-TARGET-MAP",
            checkpoint["batch_record"]["evaluation_contract_version"],
        )
        self.assertEqual(5, checkpoint["batch_record"]["returned_targets"])
        self.assertEqual("match_0066", output_row["instance_id"])
        self.assertEqual(5, len(output_row["decision_predictions"]))

    def test_canonical_set_protocol_is_prospective_and_oracle_clean(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        public = _read(release / "public/match_0066/public_instance.json")
        with self.assertRaisesRegex(ValueError, "canonical_set_v2 requires"):
            _request_record(
                release,
                public,
                public["decision_question_schema"],
                0,
                "r26_decision",
                evidence_role_protocol="edge_derived_v3",
                response_envelope_protocol="request_bound_v2",
                unknown_evidence_protocol="semantic_false_positive_v2",
                evidence_set_protocol="canonical_set_v2",
            )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(release),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "canonical_set_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                    "r26_response_envelope_protocol": "exact_target_map_v3",
                    "r26_unknown_evidence_protocol": "semantic_false_positive_v2",
                    "r26_evidence_set_protocol": "canonical_set_v2",
                }],
            }), encoding="utf-8")
            run_config(config)
            run_dir = root / "runs/canonical_set_oracle"
            metadata = _read(run_dir / "RUN_METADATA.json")
            checkpoint = _read(
                run_dir / "checkpoints/match_0066/batch_000.json"
            )
        self.assertEqual("canonical_set_v2", metadata["r26_evidence_set_protocol"])
        self.assertEqual("OK", checkpoint["batch_record"]["status"])
        self.assertEqual("PASS", checkpoint["batch_record"]["conformance_status"])
        self.assertEqual([], checkpoint["batch_record"]["conformance_warnings"])
        self.assertEqual(
            "R26-C3-EDGE-9-CANONICAL-SET-CONFORMANCE",
            checkpoint["batch_record"]["evaluation_contract_version"],
        )

    def test_canonical_set_sentinel_preflight_injects_duplicate_faults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compile_sentinel_preflight(
                ROOT
                / "eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json",
                ROOT / "design/r26_18_canonical_set_request_contract.json",
                Path(directory) / "preflight.json",
            )
        self.assertEqual(
            "VETT-R26-SENTINEL5-ZERO-REQUEST-PREFLIGHT-4",
            report["protocol_version"],
        )
        self.assertEqual(
            "REQUEST_READY_BLOCKED_BY_AUTHORIZATION", report["status"]
        )
        self.assertEqual("canonical_set_v2", report["r26_evidence_set_protocol"])
        self.assertTrue(
            report["gates"][
                "canonical_duplicate_probe_passes_when_required"
            ]
        )
        self.assertTrue(all(
            item["canonical_duplicate_probe_passed"]
            for item in report["per_match"]
        ))
        self.assertEqual(0, report["provider_requests_made"])

    def test_canonical_set_pilot20_preflight_freezes_full_matched_panel(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = compile_sentinel_preflight(
                ROOT
                / "eval_configs/r26_18_glm53_canonical_set_pilot20_blocked.json",
                ROOT
                / "design/r26_18_canonical_set_pilot20_request_contract.json",
                Path(directory) / "pilot20_preflight.json",
            )
        self.assertEqual(
            "REQUEST_READY_BLOCKED_BY_AUTHORIZATION", report["status"]
        )
        self.assertEqual(20, report["instances"])
        self.assertEqual(100, report["questions"])
        self.assertEqual(4, report["matched_anchor_design"]["required_count_per_cell"])
        self.assertTrue(report["gates"]["complete_anchor_by_level_latin_square"])
        self.assertTrue(report["gates"]["one_batch_per_match"])
        self.assertTrue(report["gates"]["estimated_cost_within_contract"])
        self.assertEqual(0, report["provider_requests_made"])

    def test_canonical_set_runner_scores_duplicates_and_reports_nonconformance(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        gold = _read(release / "private/match_0066/private_gold.json")
        response = preflight_oracle_response(gold, "exact_target_map_v3")
        first_question = next(iter(response["decision_predictions"]))
        first = response["decision_predictions"][first_question]
        first["evidence_spans"].append(first["evidence_spans"][0])
        first["evidence_edges"].append(copy.deepcopy(first["evidence_edges"][0]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            response_path = root / "response.json"
            response_path.write_text(json.dumps(response), encoding="utf-8")
            emitter = root / "emit.py"
            emitter.write_text(
                "import pathlib,sys\nprint(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))\n",
                encoding="utf-8",
            )
            config = root / "config.json"
            config.write_text(json.dumps({
                "release_dir": str(release),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "canonical_command",
                    "adapter": "command",
                    "command": [sys.executable, str(emitter), str(response_path)],
                    "model": "duplicate-fixture",
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "max_retries": 0,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                    "r26_response_envelope_protocol": "exact_target_map_v3",
                    "r26_unknown_evidence_protocol": "semantic_false_positive_v2",
                    "r26_evidence_set_protocol": "canonical_set_v2",
                }],
            }), encoding="utf-8")
            run_config(config)
            run_dir = root / "runs/canonical_command"
            checkpoint = _read(
                run_dir / "checkpoints/match_0066/batch_000.json"
            )
            report = analyze_r26_run(release, run_dir)
        batch = checkpoint["batch_record"]
        self.assertEqual("OK", batch["status"])
        self.assertEqual("FAIL_CANONICALIZED", batch["conformance_status"])
        self.assertEqual(2, len(batch["conformance_warnings"]))
        self.assertTrue(report["sentinel_run_complete"])
        self.assertEqual(
            "FAIL_CANONICALIZED",
            report["protocol_evaluation"]["output_conformance"]["status"],
        )
        self.assertEqual(0.8, report["scores"]["output_conformance_question_rate"])
        self.assertEqual(1.0, report["scores"]["factual_record_macro_accuracy"])
        self.assertEqual(
            0.8,
            report["scores"][
                "factual_evidence_chain_conformant_joint_exact"
            ],
        )

    def test_exact_target_map_fault_attribution_is_complete(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        report = audit_exact_target_map(release, "match_0220")
        self.assertEqual("PASS_LOCAL_ONLY", report["status"])
        self.assertTrue(all(report["schema_gates"].values()))
        self.assertEqual(7, len(report["fault_cases"]))
        self.assertTrue(all(case["passed"] for case in report["fault_cases"]))
        self.assertEqual(0, report["provider_requests_made"])
        self.assertFalse(report["dataset_bytes_changed"])

    def test_incomplete_edge7_subset_cannot_authorize_dataset_edits(self) -> None:
        release = ROOT / "r26_15_content_dependency_candidate_v3"
        cohort_dir = ROOT / "analysis/r26_16_edge7_sentinel5_cohort"
        with tempfile.TemporaryDirectory() as directory:
            report = build_edge7_subset_diagnostic(
                release,
                cohort_dir / "COHORT_ANALYSIS.json",
                cohort_dir / "COHORT_PREDICTIONS.jsonl",
                Path(directory),
                ROOT
                / "analysis/r26_9_difficulty_ledger/PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl",
            )
        self.assertEqual(
            "DIAGNOSTIC_ONLY_INCOMPLETE_COHORT", report["status"]
        )
        self.assertFalse(report["dataset_mutation_authorized"])
        self.assertEqual("REJECT", report["decision"]["global_hardening"])
        self.assertEqual(
            "BLOCKED_INCOMPLETE_SENTINEL5",
            report["decision"]["dataset_edit_now"],
        )
        self.assertAlmostEqual(
            0.716667,
            report["primary_interpretation"][
                "frozen_12_field_macro_accuracy"
            ],
        )
        self.assertAlmostEqual(10.42, report["l2_to_l3_inversion"]["inversion_points"])

    def test_exact_target_map_real_smoke_is_protocol_only(self) -> None:
        run_dir = (
            ROOT
            / "eval_runs/r26_17_glm53_match0220_exact_map_smoke/"
            "r26_17_glm53_match0220_exact_map_smoke"
        )
        with tempfile.TemporaryDirectory() as directory:
            report = build_protocol_smoke_outcome(
                ROOT
                / "eval_configs/r26_17_glm53_flash_match0220_exact_target_map_smoke_blocked.json",
                ROOT
                / "eval_configs/r26_17_glm53_flash_match0220_exact_target_map_smoke_authorized.json",
                run_dir,
                ROOT
                / "analysis/r26_17_exact_target_map/ZERO_REQUEST_PREFLIGHT.json",
                Path(directory),
            )
        self.assertEqual("PASS_PROTOCOL_SMOKE", report["status"])
        self.assertTrue(all(report["gates"].values()))
        self.assertEqual(1, report["provider_requests"])
        self.assertEqual(5, report["returned_targets"])
        self.assertFalse(report["historical_edge7_merge_authorized"])
        self.assertFalse(report["dataset_mutation_authorized"])
        self.assertFalse(report["five_match_execution_authorized"])

    def test_request_bound_protocol_rejects_unsupported_combinations(self) -> None:
        public = _read(CURRENT_RELEASE / "public/match_0066/public_instance.json")
        with self.assertRaisesRegex(ValueError, "requires task_type=r26_decision"):
            _request_record(
                CURRENT_RELEASE,
                public,
                public["decision_question_schema"][:1],
                0,
                "r26_decision",
                response_envelope_protocol="request_bound_v2",
            )

    def test_r26_error_analysis_separates_clean_oracle_from_difficulty_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.json"
            config.write_text(json.dumps({
                "calibration_stage": "single_protocol_gate",
                "release_dir": str(CURRENT_RELEASE),
                "output_dir": str(root / "runs"),
                "runs": [{
                    "run_id": "error_analysis_oracle",
                    "adapter": "oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "r26_evidence_role_protocol": "edge_derived_v3",
                    "r26_response_envelope_protocol": "request_bound_v2",
                }],
            }), encoding="utf-8")
            run_config(config)
            report = analyze_r26_errors(
                CURRENT_RELEASE,
                root / "runs/error_analysis_oracle",
                ROOT / "analysis/r26_9_difficulty_ledger/PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl",
            )
        self.assertEqual({}, report["error_taxonomy_question_counts"])
        self.assertEqual(5, report["questions"])
        self.assertEqual("single_protocol_gate", report["calibration_stage"])
        self.assertFalse(report["may_trigger_dataset_changes"])
        self.assertTrue(all(
            row["factual_field_accuracy"] == 1.0
            and row["factual_record_exact"] == 1.0
            for row in report["by_level"].values()
        ))

    def test_r26_4_archived_release_keeps_legacy_edge_protocol(self) -> None:
        release = ROOT / "r26_long_context_pilot_evaluated_r26_4_partial"
        summary = _read(release / "RELEASE_SUMMARY.json")
        from vett_eval.runner import _task_type
        self.assertEqual("r26_edge_decision", _task_type(summary))


if __name__ == "__main__":
    unittest.main()
