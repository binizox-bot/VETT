import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from vett_eval.analysis import (
    analyze_r20_run,
    analyze_r21_run,
    analyze_r23_knowledge_run,
    analyze_r26_run,
)
from vett_eval.cohort import _verify_request_equivalence, analyze_calibration_cohorts
from vett_eval.panel import analyze_r26_panel
from vett_eval.runner import (
    PORTABLE_ARTIFACT_PATH_LIMIT,
    R25_DECISION_SCHEMA,
    R26_DECISION_SCHEMA,
    _bounded_response_schema,
    _load_env_file,
    _normalize_response,
    _parse_json_with_closure_repair,
    _recorded_actual_cost_cny,
    _task_type,
    _validate_artifact_path_budget,
    estimate_config,
    run_config,
)
from vett_r24.evaluation import score_predictions as score_r24_predictions
from vett_r26.protocol_analysis import (
    _failure_class,
    _output_conformance_summary,
    materialize_semantic_predictions,
)


PROJECT = Path(__file__).resolve().parents[1]
RELEASE = PROJECT / "dataset_r20_220"
R21_RELEASE = PROJECT / "r21_pilot"
R23_RELEASE = PROJECT / "r23_1_text_embedded_pilot"
R24_RELEASE = PROJECT / "dataset_r24_220"
R26_RELEASE = PROJECT / "r26_authority_binding_pilot"


class EvalFrameworkTests(unittest.TestCase):
    def test_output_conformance_is_separate_from_semantic_scoreability(self) -> None:
        summary = _output_conformance_summary({
            "r26_evidence_set_protocol": "canonical_set_v2",
            "records": [{
                "instance_id": "match_x",
                "batches": [{
                    "requested_targets": 5,
                    "conformance_warnings": [{
                        "warning_type": "DUPLICATE_EVIDENCE_CANONICALIZED",
                        "question_id": "q1",
                        "evidence_field": "evidence_edges",
                        "duplicate_groups": 2,
                        "redundant_count": 4,
                        "maximum_multiplicity": 3,
                    }],
                }],
            }],
        })
        self.assertEqual("FAIL_CANONICALIZED", summary["status"])
        self.assertFalse(summary["semantic_scoreability_affected"])
        self.assertEqual(0.8, summary["question_conformance_rate"])
        self.assertEqual(1, summary["affected_questions"])
        self.assertEqual(2, summary["duplicate_groups"])
        self.assertEqual(4, summary["redundant_count"])
        self.assertEqual(3, summary["maximum_multiplicity"])

        strict = _output_conformance_summary({
            "records": [{
                "instance_id": "match_old",
                "batches": [{
                    "batch_index": 0,
                    "requested_targets": 5,
                    "validation_errors": [
                        "prediction 1 repeats evidence edges"
                    ],
                }],
            }],
        })
        self.assertEqual("FAIL_HARD_STRICT", strict["status"])
        self.assertTrue(strict["semantic_scoreability_affected"])
        self.assertIsNone(strict["question_conformance_rate"])

    def test_declared_task_type_prevents_future_version_misrouting(self) -> None:
        self.assertEqual(
            "r26_decision",
            _task_type({
                "dataset_version": "VETT-Cricket-v9-R26.99-future",
                "evaluation_task_type": "r26_decision",
            }),
        )
        with self.assertRaisesRegex(ValueError, "unsupported declared"):
            _task_type({
                "dataset_version": "VETT-Cricket-v9-R26.99-future",
                "evaluation_task_type": "unknown_task",
            })

    def test_cohort_request_equivalence_rejects_semantic_input_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_id = "oracle_equivalence"
            spec = {
                "run_id": run_id,
                "adapter": "oracle",
                "model": "private-oracle",
                "test_only": True,
                "instance_ids": ["match_0067"],
                "target_batch_size": 5,
                "r26_evidence_role_protocol": "edge_derived_v3",
                "r26_response_envelope_protocol": "request_bound_v2",
                "response_format_mode": "json_schema",
            }
            config_path = root / "run.json"
            output_dir = root / "runs"
            config_path.write_text(json.dumps({
                "release_dir": str(R26_RELEASE),
                "output_dir": str(output_dir),
                "runs": [spec],
            }), encoding="utf-8")
            run_config(config_path)
            candidate = root / "candidate"
            public_dir = candidate / "public" / "match_0067"
            public_dir.mkdir(parents=True)
            public = json.loads((
                R26_RELEASE / "public/match_0067/public_instance.json"
            ).read_text(encoding="utf-8"))
            public["task"] += " altered"
            (public_dir / "public_instance.json").write_text(
                json.dumps(public), encoding="utf-8"
            )
            report = _verify_request_equivalence(
                candidate,
                R26_RELEASE,
                output_dir / run_id,
                spec,
                {"match_0067"},
            )
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any(
            "semantic_request_hash_mismatch" in error
            for error in report["errors"]
        ))

    def test_calibration_cohort_reuses_compatible_incremental_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = {
                "adapter": "oracle",
                "model": "private-oracle",
                "test_only": True,
                "target_batch_size": 5,
                "r26_evidence_role_protocol": "edge_derived_v3",
                "temperature": 0.1,
                "top_p": 0.95,
                "enable_thinking": False,
                "response_format_mode": "json_schema",
            }
            configs = []
            definitions = (
                (
                    "part_a",
                    ["match_0066", "match_0067"],
                    "explicit_instance_v1",
                ),
                (
                    "part_b",
                    ["match_0021", "match_0162", "match_0220"],
                    "request_bound_v2",
                ),
            )
            members = []
            for run_id, instance_ids, envelope in definitions:
                config_path = root / f"{run_id}.json"
                output_dir = root / f"runs_{run_id}"
                config_path.write_text(json.dumps({
                    "release_dir": str(R26_RELEASE),
                    "output_dir": str(output_dir),
                    "runs": [{
                        **common,
                        "run_id": run_id,
                        "instance_ids": instance_ids,
                        "r26_response_envelope_protocol": envelope,
                    }],
                }), encoding="utf-8")
                run_config(config_path)
                configs.append(config_path)
                members.append({
                    "run_id": run_id,
                    "run_dir": str(output_dir / run_id),
                    "source_config": str(config_path),
                    "instance_ids": instance_ids,
                })
            manifest = root / "cohort.json"
            manifest.write_text(json.dumps({
                "release_dir": str(R26_RELEASE),
                "metric_contract": str(
                    PROJECT / "design/r26_9_metric_contract.json"
                ),
                "output_dir": str(root / "cohort_output"),
                "cohorts": [{
                    "cohort_id": "oracle_sentinel5",
                    "calibration_stage": "sentinel5",
                    "model": "private-oracle",
                    "allowed_evidence_role_protocols": ["edge_derived_v3"],
                    "allowed_response_envelope_protocols": [
                        "explicit_instance_v1", "request_bound_v2"
                    ],
                    "transport_variance_is_nonsemantic": True,
                    "members": members,
                }],
            }), encoding="utf-8")
            report = analyze_calibration_cohorts(manifest)
        cohort = report["cohorts"][0]
        self.assertEqual("COMPLETE_COHORT", cohort["status"])
        self.assertEqual(5, cohort["collected_instances"])
        self.assertEqual([], cohort["issues"])
        self.assertEqual(1, len(set(cohort["core_generation_fingerprints"].values())))
        self.assertEqual(1.0, cohort["scores"]["decision_field_macro_accuracy"])
        # Perfect oracle scores intentionally fail a difficulty-separation screen;
        # this proves collection completeness and scientific conclusions are distinct.
        self.assertEqual("FAIL", cohort["frozen_metric_gate"]["status"])

    def test_recorded_actual_cost_ignores_unpriced_failures(self) -> None:
        records = [{"batches": [
            {"actual_cost_cny": 0.10054},
            {"actual_cost_cny": None},
            {"actual_cost_cny": 0.096234},
        ]}]
        self.assertEqual(0.196774, _recorded_actual_cost_cny(records))

    def test_artifact_path_budget_fails_before_provider_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / ("x" * PORTABLE_ARTIFACT_PATH_LIMIT)
            with self.assertRaisesRegex(RuntimeError, "Shorten output_dir or run_id"):
                _validate_artifact_path_budget(output, "run", ["match_0066"])

    def test_provider_failures_are_not_semantic_model_errors(self) -> None:
        self.assertEqual(
            "ACCOUNT_BALANCE",
            _failure_class({"status": "ERROR", "error": "Chat Completions HTTP 402: balance is insufficient"}),
        )
        self.assertEqual("RATE_LIMIT", _failure_class({"status": "ERROR", "error": "HTTP 429"}))
        self.assertEqual("TIMEOUT", _failure_class({"status": "ERROR", "error": "request timed out"}))
        self.assertEqual("SCHEMA_OR_PROTOCOL", _failure_class({"status": "INVALID"}))
        self.assertEqual(
            "OUTPUT_TRUNCATED",
            _failure_class({"status": "INVALID_OUTPUT", "finish_reason": "length"}),
        )

    def test_decision_explanation_has_output_budget(self) -> None:
        item = R25_DECISION_SCHEMA["properties"]["decision_predictions"]["items"]
        self.assertEqual(480, item["properties"]["explanation"]["maxLength"])

    def test_r26_schema_bounds_repetition_and_batch_cardinality(self) -> None:
        schema = _bounded_response_schema(R26_DECISION_SCHEMA, "r26_decision", 5)
        predictions = schema["properties"]["decision_predictions"]
        self.assertEqual(5, predictions["minItems"])
        self.assertEqual(5, predictions["maxItems"])
        item = predictions["items"]
        self.assertEqual(32, item["properties"]["evidence_spans"]["maxItems"])
        self.assertTrue(item["properties"]["evidence_spans"]["uniqueItems"])
        self.assertEqual(8, item["properties"]["rejected_evidence_spans"]["maxItems"])
        self.assertTrue(item["properties"]["rejected_evidence_spans"]["uniqueItems"])
        self.assertEqual(48, item["properties"]["evidence_edges"]["maxItems"])
        self.assertTrue(item["properties"]["evidence_edges"]["uniqueItems"])

    def test_r26_schema_accepts_neutral_ids_without_weakening_legacy_ids(self) -> None:
        item = R26_DECISION_SCHEMA["properties"]["decision_predictions"]["items"]
        span_pattern = item["properties"]["evidence_spans"]["items"]["pattern"]
        edge = item["properties"]["evidence_edges"]["items"]["properties"]
        import re

        self.assertIsNotNone(re.fullmatch(span_pattern, "s_0123456789abcdef01234567"))
        self.assertIsNotNone(re.fullmatch(span_pattern, "r25fact_legacy"))
        self.assertIsNone(re.fullmatch(span_pattern, "fact_answer_leak"))
        self.assertIsNotNone(
            re.fullmatch(edge["source_id"]["pattern"], "s_0123456789abcdef01234567")
        )
        self.assertIsNotNone(
            re.fullmatch(edge["target_id"]["pattern"], "decision:r25q_abc123")
        )

    def test_r26_normalization_rejects_repeated_evidence(self) -> None:
        record = {
            "delivery_status": "LEGAL",
            "counts_in_over": True,
            "dismissal": "NONE",
            "total_runs": 0,
            "batter_runs": 0,
            "bowler_runs": 0,
            "run_ledger": [{"account": "NONE", "runs": 0}],
        }
        state = {
            "active_source": "DIRECT_OBSERVATION",
            "initial_call_set": "NONE",
            "observed_contact": "NONE",
            "effective_delivery_status": "LEGAL",
            "movement_runs_before_boundary_allowance": 0,
            "boundary_allowance": 0,
            "pre_wicket_ball_state": "NOT_APPLICABLE",
        }
        edge = {"source_id": "s", "relation": "supports_decision", "target_id": "decision:q"}
        _, errors = _normalize_response(
            {
                "instance_id": "m",
                "decision_predictions": [{
                    "question_id": "q",
                    "decision_record": record,
                    "state": state,
                    "evidence_spans": ["s", "s"],
                    "rejected_evidence_spans": ["r", "r"],
                    "evidence_edges": [edge, edge],
                    "counterfactual_record": record,
                    "counterfactual_state": state,
                    "explanation": "x",
                    "confidence": 0.5,
                }],
            },
            "m",
            {"q"},
            "r26_decision",
        )
        self.assertTrue(any("repeats evidence span IDs" in error for error in errors))
        self.assertTrue(any("repeats rejected evidence span IDs" in error for error in errors))
        self.assertTrue(any("repeats evidence edges" in error for error in errors))

    def test_r26_canonical_set_scores_exact_duplicates_but_records_conformance(self) -> None:
        record = {
            "delivery_status": "LEGAL",
            "counts_in_over": True,
            "dismissal": "NONE",
            "total_runs": 0,
            "batter_runs": 0,
            "bowler_runs": 0,
            "run_ledger": [{"account": "NONE", "runs": 0}],
        }
        state = {
            "active_source": "DIRECT_OBSERVATION",
            "initial_call_set": "NONE",
            "observed_contact": "NONE",
            "effective_delivery_status": "LEGAL",
            "movement_runs_before_boundary_allowance": 0,
            "boundary_allowance": 0,
            "pre_wicket_ball_state": "NOT_APPLICABLE",
        }
        question_id = "r25q_test"
        span_id = "s_0123456789abcdef01234567"
        edge = {
            "source_id": span_id,
            "relation": "supports_decision",
            "target_id": f"decision:{question_id}",
        }
        response = {
            "decision_predictions": {
                question_id: {
                    "decision_record": record,
                    "state": state,
                    "evidence_spans": [span_id, span_id],
                    "evidence_edges": [edge, edge, edge],
                    "counterfactual_record": record,
                    "counterfactual_state": state,
                    "explanation": "x",
                    "confidence": 0.5,
                }
            }
        }
        warnings: list[dict] = []
        normalized, errors = _normalize_response(
            response,
            "match_test",
            {question_id},
            "r26_decision",
            evidence_span_ids={span_id},
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="exact_target_map_v3",
            unknown_evidence_protocol="semantic_false_positive_v2",
            evidence_relations_by_target={question_id: {"supports_decision"}},
            evidence_set_protocol="canonical_set_v2",
            conformance_warnings=warnings,
        )
        self.assertEqual([], errors)
        self.assertEqual([span_id], normalized[question_id]["evidence_spans"])
        self.assertEqual([edge], normalized[question_id]["evidence_edges"])
        self.assertEqual(2, len(warnings))
        self.assertEqual(3, sum(item["redundant_count"] for item in warnings))
        self.assertTrue(all(
            item["warning_type"] == "DUPLICATE_EVIDENCE_CANONICALIZED"
            for item in warnings
        ))

        over_limit = copy.deepcopy(response)
        over_limit["decision_predictions"][question_id]["evidence_edges"] = [
            edge for _ in range(49)
        ]
        _, over_limit_errors = _normalize_response(
            over_limit,
            "match_test",
            {question_id},
            "r26_decision",
            evidence_span_ids={span_id},
            evidence_role_protocol="edge_derived_v3",
            response_envelope_protocol="exact_target_map_v3",
            unknown_evidence_protocol="semantic_false_positive_v2",
            evidence_relations_by_target={question_id: {"supports_decision"}},
            evidence_set_protocol="canonical_set_v2",
        )
        self.assertTrue(any("too many evidence edges" in error for error in over_limit_errors))

    def test_r26_normalization_rejects_unknown_evidence_ids_and_edge_mismatch(self) -> None:
        record = {
            "delivery_status": "LEGAL", "counts_in_over": True,
            "dismissal": "NONE", "total_runs": 0, "batter_runs": 0,
            "bowler_runs": 0, "run_ledger": [{"account": "NONE", "runs": 0}],
        }
        state = {
            "active_source": "DIRECT_OBSERVATION", "initial_call_set": "NONE",
            "observed_contact": "NONE", "effective_delivery_status": "LEGAL",
            "movement_runs_before_boundary_allowance": 0, "boundary_allowance": 0,
            "pre_wicket_ball_state": "NOT_APPLICABLE",
        }
        _, errors = _normalize_response(
            {
                "instance_id": "m",
                "decision_predictions": [{
                    "question_id": "r25q_test",
                    "decision_record": record,
                    "state": state,
                    "evidence_spans": ["r25fact_good", "state"],
                    "rejected_evidence_spans": ["r25shadow_good"],
                    "evidence_edges": [{
                        "source_id": "r25fact_good",
                        "relation": "supports_decision",
                        "target_id": "decision:r25q_test",
                    }],
                    "counterfactual_record": record,
                    "counterfactual_state": state,
                    "explanation": "x",
                    "confidence": 0.5,
                }],
            },
            "m",
            {"r25q_test"},
            "r26_decision",
            evidence_span_ids={"r25fact_good", "r25shadow_good"},
        )
        self.assertTrue(any("unknown evidence span IDs: state" in error for error in errors))
        self.assertTrue(any("do not match rejects edges" in error for error in errors))

    def test_real_glm_rejected_array_corruption_fixture_is_fully_detected(self) -> None:
        fixture = json.loads(
            (PROJECT / "tests" / "fixtures" / "r26_glm53_rejected_array_corruption.json")
            .read_text(encoding="utf-8")
        )
        record = {
            "delivery_status": "LEGAL", "counts_in_over": True,
            "dismissal": "NONE", "total_runs": 0, "batter_runs": 0,
            "bowler_runs": 0, "run_ledger": [{"account": "NONE", "runs": 0}],
        }
        state = {
            "active_source": "DIRECT_OBSERVATION", "initial_call_set": "NONE",
            "observed_contact": "NONE", "effective_delivery_status": "LEGAL",
            "movement_runs_before_boundary_allowance": 0, "boundary_allowance": 0,
            "pre_wicket_ball_state": "LIVE",
        }
        question_id = fixture["source_question_id"]
        _, errors = _normalize_response(
            {
                "instance_id": "match_0066",
                "decision_predictions": [{
                    "question_id": question_id,
                    "decision_record": record,
                    "state": state,
                    "evidence_spans": ["r25fact_good"],
                    "rejected_evidence_spans": fixture["rejected_evidence_spans"],
                    "evidence_edges": [{
                        "source_id": "r25fact_good",
                        "relation": "supports_decision",
                        "target_id": f"decision:{question_id}",
                    }],
                    "counterfactual_record": record,
                    "counterfactual_state": state,
                    "explanation": "x",
                    "confidence": 0.5,
                }],
            },
            "match_0066",
            {question_id},
            "r26_decision",
            evidence_span_ids={"r25fact_good", "r25shadow_good"},
        )
        for fragment in fixture["expected_error_fragments"]:
            self.assertTrue(any(fragment in error for error in errors), fragment)

    def test_json_closure_repair_is_narrow_and_auditable(self) -> None:
        parsed, suffix = _parse_json_with_closure_repair(
            '{"decision_predictions":[{"question_id":"q"}]' + " " * 50
        )
        self.assertEqual({"decision_predictions": [{"question_id": "q"}]}, parsed)
        self.assertEqual("}", suffix)
        with self.assertRaises(json.JSONDecodeError):
            _parse_json_with_closure_repair('{"decision_predictions":["unterminated')
        with self.assertRaises(json.JSONDecodeError):
            _parse_json_with_closure_repair('{"a":{"b":{"c":1')

    def test_r24_knowledge_oracle_runner_includes_counterfactual(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R24_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "r24_knowledge_oracle", "adapter": "oracle",
                    "model": "private-oracle", "test_only": True,
                    "instance_ids": ["match_0066"], "target_batch_size": 5,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            predictions = temp / "runs" / "r24_knowledge_oracle" / "predictions.jsonl"
            score = score_r24_predictions(R24_RELEASE, predictions, instance_ids=["match_0066"])
            self.assertEqual(1.0, score["fact_answer_macro_accuracy"])
            self.assertEqual(1.0, score["counterfactual_pair_consistency"])

    def test_r23_knowledge_oracle_runner_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R23_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [
                    {
                        "run_id": "r23_knowledge_oracle",
                        "adapter": "oracle",
                        "model": "private-oracle",
                        "test_only": True,
                        "instance_ids": ["match_0066"],
                        "target_batch_size": 5,
                    }
                ],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            analysis = analyze_r23_knowledge_run(
                R23_RELEASE, temp / "runs" / "r23_knowledge_oracle"
            )
            self.assertEqual(1.0, analysis["scores"]["knowledge_answer_exact"]["accuracy"])
            self.assertEqual(1.0, analysis["scores"]["knowledge_joint_exact"]["accuracy"])
            self.assertEqual(1.0, analysis["scores"]["knowledge_decisive_span_micro"]["f1"])

    def test_normalization_flags_missing_requested_target(self) -> None:
        normalized, errors = _normalize_response(
            {
                "instance_id": "m",
                "predictions": [{"target_id": "a", "value": "1"}],
            },
            "m",
            {"a", "b"},
            "r20",
        )
        self.assertEqual({"a": "1"}, normalized)
        self.assertTrue(any("missing 1 requested target" in error for error in errors))

    def test_estimate_and_cost_ceiling_block_before_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R21_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [
                    {
                        "run_id": "budget_block",
                        "adapter": "oracle",
                        "model": "private-oracle",
                        "test_only": True,
                        "instance_ids": ["match_0066"],
                        "target_batch_size": 100,
                        "thinking_budget": 8192,
                        "pricing_cny_per_million": {
                            "input": 0.8,
                            "cached_input": 0.23,
                            "output": 2.8,
                        },
                        "max_estimated_cost_cny": 0,
                    }
                ],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            estimate = estimate_config(config_path)
            self.assertGreater(
                estimate["runs"][0]["estimated_cost_cny_zero_cache"], 0
            )
            with self.assertRaisesRegex(RuntimeError, "above configured ceiling"):
                run_config(config_path)

    def test_execution_authorization_gate_blocks_before_env_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "blocked.json"
            config.write_text(json.dumps({
                "require_explicit_execution_authorization": True,
                "execution_authorized": False,
                "env_file": "definitely_missing.env",
            }), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "provider execution is not authorized"):
                run_config(config)

    def test_resume_reuses_request_hashed_batch_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R21_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [
                    {
                        "run_id": "resume_oracle",
                        "adapter": "oracle",
                        "model": "private-oracle",
                        "test_only": True,
                        "resume": True,
                        "instance_ids": ["match_0066"],
                        "target_batch_size": 100,
                    }
                ],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            run_config(config_path)
            metadata = json.loads(
                (temp / "runs" / "resume_oracle" / "RUN_METADATA.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(
                all(
                    batch["resumed_from_checkpoint"]
                    for batch in metadata["records"][0]["batches"]
                )
            )

    def test_resume_retries_invalid_checkpoint_instead_of_reusing_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R21_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "resume_invalid",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "resume": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 100,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            checkpoint_path = next((temp / "runs" / "resume_invalid" / "checkpoints").rglob("*.json"))
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["predictions"] = {}
            checkpoint["batch_record"]["status"] = "INVALID_OUTPUT"
            checkpoint["batch_record"]["returned_targets"] = 0
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            run_config(config_path)
            metadata = json.loads(
                (temp / "runs" / "resume_invalid" / "RUN_METADATA.json").read_text(encoding="utf-8")
            )
            batch = metadata["records"][0]["batches"][0]
            self.assertEqual("OK", batch["status"])
            self.assertFalse(batch["resumed_from_checkpoint"])

    def test_strict_resume_reuses_terminal_failure_without_resubmission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "reuse_terminal",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "resume": True,
                    "reuse_terminal_failures": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            checkpoint_path = next(
                (temp / "runs" / "reuse_terminal" / "checkpoints").rglob("*.json")
            )
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["predictions"] = {}
            checkpoint["batch_record"]["status"] = "INVALID_OUTPUT"
            checkpoint["batch_record"]["returned_targets"] = 0
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            run_config(config_path)
            metadata = json.loads(
                (temp / "runs" / "reuse_terminal" / "RUN_METADATA.json").read_text(
                    encoding="utf-8"
                )
            )
            batch = metadata["records"][0]["batches"][0]
            self.assertEqual("INVALID_OUTPUT", batch["status"])
            self.assertTrue(batch["resumed_from_checkpoint"])
            self.assertTrue(batch["terminal_failure_reused"])

    def test_protocol_failure_stops_remaining_sentinel_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "fail_fast",
                    "adapter": "command",
                    "command": [sys.executable, "-c", "print('{}')"],
                    "model": "invalid-local-stub",
                    "instance_ids": ["match_0066", "match_0067"],
                    "target_batch_size": 5,
                    "max_retries": 0,
                    "stop_run_on_batch_failure": True,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            metadata = json.loads(
                (temp / "runs" / "fail_fast" / "RUN_METADATA.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(metadata["stopped_early"])
            self.assertEqual(1, metadata["instances"])
            self.assertEqual(2, metadata["instances_requested"])
            self.assertEqual(
                "INVALID_OUTPUT", metadata["records"][0]["batches"][0]["status"]
            )

    def test_r26_panel_scores_only_protocol_complete_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "panel_oracle",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                    "max_retries": 0,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            panel = analyze_r26_panel(config_path)
            self.assertEqual(1, panel["models_scoreable"])
            model = panel["models"][0]
            self.assertEqual(1, model["scored_instances"])
            self.assertEqual(1.0, model["factual_record_macro_accuracy"])
            self.assertTrue((temp / "runs" / "PANEL_ANALYSIS.json").is_file())
            self.assertTrue((temp / "runs" / "PANEL_ANALYSIS.md").is_file())

    def test_direct_r26_analysis_excludes_protocol_failed_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "direct_analysis_protocol_filter",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066", "match_0067"],
                    "target_batch_size": 5,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            run_dir = temp / "runs" / "direct_analysis_protocol_filter"
            checkpoint_path = run_dir / "checkpoints/match_0067/batch_000.json"
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["batch_record"]["status"] = "INVALID_OUTPUT"
            checkpoint["batch_record"]["validation_errors"] = [
                "prediction 0 uses unknown evidence span IDs: r26:s_deadbeef"
            ]
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            metadata_path = run_dir / "RUN_METADATA.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["records"][1]["batches"][0] = checkpoint["batch_record"]
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

            report = analyze_r26_run(R26_RELEASE, run_dir)

            self.assertEqual("PARTIAL_SEMANTIC_COVERAGE", report["protocol_evaluation"]["status"])
            self.assertEqual(["match_0066"], report["protocol_evaluation"]["scored_instance_ids"])
            self.assertEqual(1, report["scores"]["instances"])
            self.assertEqual(5, report["scores"]["questions"])
            self.assertEqual(2, report["planned_instances"])
            self.assertEqual(2, report["attempted_instances"])
            self.assertEqual(1, report["scored_instances"])
            self.assertEqual(0.5, report["planned_semantic_coverage"])
            self.assertFalse(report["sentinel_run_complete"])
            self.assertIn(
                "INCOMPLETE — subset metrics only",
                (run_dir / "ANALYSIS.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                {"match_0066"},
                {row["instance_id"] for row in report["question_results"]},
            )

    def test_evidence_only_failure_has_non_official_factual_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "evidence_only_invalid",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            run_dir = temp / "runs" / "evidence_only_invalid"
            checkpoint_path = next((run_dir / "checkpoints").rglob("*.json"))
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["batch_record"]["status"] = "INVALID_OUTPUT"
            checkpoint["batch_record"]["validation_errors"] = [
                "prediction 2 repeats rejected evidence span IDs"
            ]
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            metadata_path = run_dir / "RUN_METADATA.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["records"][0]["batches"][0] = checkpoint["batch_record"]
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            (run_dir / "predictions.jsonl").write_text(
                json.dumps({"instance_id": "match_0066", "decision_predictions": []}) + "\n",
                encoding="utf-8",
            )

            report = materialize_semantic_predictions(R26_RELEASE, run_dir)
            self.assertEqual("NO_SCOREABLE_INSTANCES", report["status"])
            self.assertEqual(0, report["scored_instances"])
            self.assertIsNone(report["scores"])
            self.assertEqual(1, report["diagnostic_factual_scored_instances"])
            diagnostic = report["diagnostic_factual_scores"]
            self.assertEqual(1.0, diagnostic["factual_record_macro_accuracy"])
            self.assertEqual(1.0, diagnostic["decision_field_macro_accuracy"])
            self.assertNotIn("minimal_evidence_f1", diagnostic)
            self.assertTrue(report["diagnostic_factual_recoveries"][0]["valid_for"].endswith("ONLY"))

    def test_ok_checkpoint_is_authoritative_when_summary_predictions_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "checkpoint_authority",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            run_dir = temp / "runs" / "checkpoint_authority"
            (run_dir / "predictions.jsonl").write_text(
                json.dumps({"instance_id": "match_0066", "decision_predictions": []}) + "\n",
                encoding="utf-8",
            )

            report = materialize_semantic_predictions(R26_RELEASE, run_dir)
            self.assertEqual("COMPLETE_SEMANTIC_COVERAGE", report["status"])
            self.assertEqual(1, report["scored_instances"])
            self.assertEqual(1.0, report["scores"]["factual_record_macro_accuracy"])
            self.assertEqual(1.0, report["scores"]["evidence_chain_joint_exact"])

    def test_factual_protocol_failure_is_not_diagnostically_recovered(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R26_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [{
                    "run_id": "factual_invalid",
                    "adapter": "oracle",
                    "model": "private-oracle",
                    "test_only": True,
                    "instance_ids": ["match_0066"],
                    "target_batch_size": 5,
                }],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            run_dir = temp / "runs" / "factual_invalid"
            checkpoint_path = next((run_dir / "checkpoints").rglob("*.json"))
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["batch_record"]["status"] = "INVALID_OUTPUT"
            checkpoint["batch_record"]["validation_errors"] = [
                "prediction 2 has invalid decision records"
            ]
            checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
            metadata_path = run_dir / "RUN_METADATA.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["records"][0]["batches"][0] = checkpoint["batch_record"]
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            (run_dir / "predictions.jsonl").write_text(
                json.dumps({"instance_id": "match_0066", "decision_predictions": []}) + "\n",
                encoding="utf-8",
            )

            report = materialize_semantic_predictions(R26_RELEASE, run_dir)
            self.assertEqual(0, report["diagnostic_factual_scored_instances"])
            self.assertIsNone(report["diagnostic_factual_scores"])

    def test_env_file_loads_without_overwriting_existing_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / "test.env"
            env_path.write_text(
                "# private values\nVETT_TEST_NEW=loaded\nVETT_TEST_EXISTING=file\n",
                encoding="utf-8",
            )
            os.environ["VETT_TEST_EXISTING"] = "process"
            os.environ.pop("VETT_TEST_NEW", None)
            try:
                _load_env_file(env_path)
                self.assertEqual("loaded", os.environ["VETT_TEST_NEW"])
                self.assertEqual("process", os.environ["VETT_TEST_EXISTING"])
            finally:
                os.environ.pop("VETT_TEST_NEW", None)
                os.environ.pop("VETT_TEST_EXISTING", None)

    def test_r21_oracle_preserves_values_spans_and_edges(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(R21_RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [
                    {
                        "run_id": "r21_oracle",
                        "adapter": "oracle",
                        "model": "private-oracle",
                        "test_only": True,
                        "instance_ids": ["match_0066"],
                        "target_batch_size": 57,
                    }
                ],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            analysis = analyze_r21_run(
                R21_RELEASE, temp / "runs" / "r21_oracle"
            )
            self.assertEqual(1.0, analysis["scores"]["answer_cell_exact"]["accuracy"])
            self.assertEqual(1.0, analysis["scores"]["evidence_span_micro"]["f1"])
            self.assertEqual(1.0, analysis["scores"]["evidence_edge_micro"]["f1"])
            self.assertEqual(1.0, analysis["scores"]["joint_target_exact"]["accuracy"])

    def test_oracle_smoke_run_and_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [
                    {
                        "run_id": "oracle_smoke",
                        "adapter": "oracle",
                        "model": "private-oracle",
                        "test_only": True,
                        "instance_ids": ["match_0001", "match_0002"],
                        "target_batch_size": 73,
                    }
                ],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = run_config(config_path)
            self.assertEqual("COMPLETE", result["status"])
            run_dir = temp / "runs" / "oracle_smoke"
            analysis = analyze_r20_run(RELEASE, run_dir)
            self.assertEqual(1.0, analysis["scores"]["micro_cell_exact"]["accuracy"])
            self.assertEqual(
                analysis["scores"]["micro_cell_exact"]["total"],
                analysis["error_categories"]["CORRECT"],
            )
            self.assertTrue(analysis["test_only"])

    def test_error_taxonomy_detects_stale_missing_and_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            config = {
                "release_dir": str(RELEASE),
                "output_dir": str(temp / "runs"),
                "runs": [
                    {
                        "run_id": "mutated",
                        "adapter": "oracle",
                        "model": "private-oracle",
                        "test_only": True,
                        "instance_ids": ["match_0001"],
                    }
                ],
            }
            config_path = temp / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run_config(config_path)
            run_dir = temp / "runs" / "mutated"
            prediction_path = run_dir / "predictions.jsonl"
            record = json.loads(prediction_path.read_text(encoding="utf-8"))
            evidence = json.loads(
                (
                    RELEASE
                    / "private"
                    / "match_0001"
                    / "private_evidence.json"
                ).read_text(encoding="utf-8")
            )
            stale_claim = next(claim for claim in evidence["claims"] if not claim["terminal"])
            record["predictions"][stale_claim["target_id"]] = stale_claim["value"]
            removed_id = next(
                target_id
                for target_id in record["predictions"]
                if target_id != stale_claim["target_id"]
            )
            record["predictions"].pop(removed_id)
            unsupported_id = next(
                target_id
                for target_id in record["predictions"]
                if target_id not in {stale_claim["target_id"], removed_id}
            )
            record["predictions"][unsupported_id] = "not-present-anywhere-value"
            prediction_path.write_text(
                json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            analysis = analyze_r20_run(RELEASE, run_dir)
            self.assertGreaterEqual(analysis["error_categories"]["STALE_REVISION"], 1)
            self.assertGreaterEqual(analysis["error_categories"]["MISSING_CELL"], 1)
            self.assertGreaterEqual(analysis["error_categories"]["UNSUPPORTED_VALUE"], 1)


if __name__ == "__main__":
    unittest.main()
