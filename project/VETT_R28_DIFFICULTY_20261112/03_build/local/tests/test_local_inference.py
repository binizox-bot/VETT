"""Offline unit tests for the local-inference service (no GPU calls required).

Run from ``03_build/local``::

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

LOCAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LOCAL_ROOT))

from local_inference import api, config, corpus, degrade, ledger, matrix, policy, service, tasks  # noqa: E402


class TestLedger(unittest.TestCase):
    def test_required_fields_recorded(self) -> None:
        entry = ledger.build_entry(
            task="T1_factor_visibility",
            template_version="T1.factor_visibility.v1",
            prompt="hello",
            raw_output='{"supported": true}',
            parsed_output={"supported": True},
            parsed_ok=True,
            wall_clock=0.1,
            call={"prompt_eval_count": 1, "eval_count": 1, "context_length": 8192,
                  "_num_predict": 128},
            service_info={"digest": "x", "quantization_level": "Q4_K_M"},
        )
        self.assertEqual(ledger.missing_fields(entry), [])
        for field in ledger.REQUIRED_FIELDS:
            self.assertIn(field, entry)
        self.assertEqual(entry["temperature"], 0.0)
        self.assertEqual(entry["seed"], config.SEED)
        self.assertEqual(entry["cost_cny"], 0.0)
        self.assertTrue(ledger.is_usable(entry))

    def test_empty_raw_is_unusable(self) -> None:
        entry = ledger.build_entry(
            task="T1_factor_visibility", template_version="v", prompt="p",
            raw_output="", parsed_output={"error": "x"}, parsed_ok=False, wall_clock=0.0,
        )
        self.assertTrue(ledger.is_complete(entry))
        self.assertFalse(ledger.is_usable(entry))


class TestCapsAndDeny(unittest.TestCase):
    def test_input_cap_enforced(self) -> None:
        spec = tasks.TASK_SPECS["T1_factor_visibility"]
        with self.assertRaises(service.InputCapExceeded):
            policy.enforce_input_cap("T1_factor_visibility", "x" * (spec.input_cap_tokens * 3 + 3))

    def test_hard_8k_ceiling_enforced(self) -> None:
        with self.assertRaises(service.InputCapExceeded) as ctx:
            policy.enforce_input_cap("T1_factor_visibility", "x" * (config.NUM_CTX * 3 + 30))
        self.assertEqual(ctx.exception.cap, config.NUM_CTX)

    def test_static_deny_routes_raise(self) -> None:
        for task_id in policy.DENY_ROUTES:
            with self.assertRaises(service.TaskDenied):
                policy.assert_allowed(task_id, "x")

    def test_unknown_task_denied(self) -> None:
        with self.assertRaises(service.TaskDenied):
            policy.assert_allowed("not_a_task", "x")


class TestSampleConstruction(unittest.TestCase):
    def test_full_sample_counts_and_determinism(self) -> None:
        for task_id, size in config.DEFAULT_SAMPLE_SIZES.items():
            spec = tasks.TASK_SPECS[task_id]
            first = spec.build_samples(size, config.DEFAULT_SEED)
            second = spec.build_samples(size, config.DEFAULT_SEED)
            self.assertGreaterEqual(len(first), 30, task_id)
            self.assertEqual([s["sample_id"] for s in first],
                             [s["sample_id"] for s in second], task_id)

    def test_s1_truth_is_single_field_topic(self) -> None:
        for sample in corpus.build_s1_samples(16, config.DEFAULT_SEED):
            self.assertEqual(corpus.mechanical_topic(sample["span_text"]), sample["truth"])
            self.assertIn(sample["truth"], corpus.TOPIC_LABELS)

    def test_t1_groups_balanced(self) -> None:
        samples = corpus.build_t1_samples(30, config.DEFAULT_SEED)
        groups = {}
        for sample in samples:
            groups[sample["group"]] = groups.get(sample["group"], 0) + 1
        self.assertEqual(len(groups), 3)
        self.assertTrue(all(count == 10 for count in groups.values()), groups)

    def test_c1_truth_construction(self) -> None:
        samples = corpus.build_c1_samples(30, config.DEFAULT_SEED)
        self.assertEqual(len({s["sample_id"] for s in samples}), 30)
        self.assertEqual(len({(json.dumps(s["record"], sort_keys=True), s["sentence"]) for s in samples}), 30)
        self.assertEqual(len({s["group"] for s in samples}), 2)
        for sample in samples:
            record_value = sample["record"][sample["field"]]
            rendered = json.dumps(record_value, ensure_ascii=False)
            if sample["truth_consistent"]:
                self.assertIn(rendered, sample["sentence"])
            else:
                self.assertNotIn(rendered, sample["sentence"])

    def test_t2_corruption_changes_text(self) -> None:
        for sample in corpus.build_t2_samples(8, config.DEFAULT_SEED):
            self.assertNotEqual(sample["natural_text"], sample["degraded_text"])
            self.assertGreater(len(sample["degraded_text"].split()), 10)


class TestPromptsAndParsers(unittest.TestCase):
    def test_prompts_within_caps(self) -> None:
        for task_id, size in config.DEFAULT_SAMPLE_SIZES.items():
            spec = tasks.TASK_SPECS[task_id]
            for sample in spec.build_samples(size, config.DEFAULT_SEED):
                prompt = tasks.build_prompt(task_id, sample)
                self.assertLessEqual(service.estimate_tokens(prompt), spec.input_cap_tokens, task_id)

    def test_t1_parser(self) -> None:
        parsed, ok, err = tasks.t1_parse('{"supported": true, "evidence": "x"}')
        self.assertTrue(ok)
        self.assertIsNone(err)
        self.assertTrue(parsed["supported"])
        parsed, ok, _ = tasks.t1_parse("no json here")
        self.assertFalse(ok)

    def test_s1_parser_rejects_unknown_label(self) -> None:
        _, ok, _ = tasks.s1_parse('{"topic": "PROVENANCE"}')
        self.assertFalse(ok)
        _, ok, _ = tasks.s1_parse('{"topic": "RUNS"}')
        self.assertTrue(ok)

    def test_c1_parser(self) -> None:
        parsed, ok, _ = tasks.c1_parse('{"consistent": false, "field": "total_runs"}')
        self.assertTrue(ok)
        self.assertFalse(parsed["consistent"])


class TestArtifacts(unittest.TestCase):
    @unittest.skipUnless(config.MATRIX_PATH.exists(), "capability_matrix.json missing")
    def test_matrix_digest_stable(self) -> None:
        data = json.loads(config.MATRIX_PATH.read_text(encoding="utf-8"))
        self.assertEqual(matrix._digest(data["tasks"]), data["summary_digest"])

    @unittest.skipUnless(config.ROUTING_CARD_PATH.exists() and config.MATRIX_PATH.exists(),
                         "routing artifacts missing")
    def test_routing_card_matches_code(self) -> None:
        data = json.loads(config.MATRIX_PATH.read_text(encoding="utf-8"))
        card = json.loads(config.ROUTING_CARD_PATH.read_text(encoding="utf-8"))
        rebuilt = policy.build_routing_card(data)
        card.pop("generated_at", None)
        rebuilt.pop("generated_at", None)
        self.assertEqual(json.dumps(card, sort_keys=True), json.dumps(rebuilt, sort_keys=True))

    @unittest.skipUnless(config.MATRIX_PATH.exists(), "capability_matrix.json missing")
    def test_allow_tasks_meet_gate(self) -> None:
        data = json.loads(config.MATRIX_PATH.read_text(encoding="utf-8"))
        for task_id, metrics in data["tasks"].items():
            if metrics["verdict"] == "ALLOW":
                self.assertGreaterEqual(metrics["agreement"], config.GATE_THRESHOLD, task_id)
                self.assertGreaterEqual(metrics["n_complete"], 30, task_id)

    @unittest.skipUnless(config.COST_LEDGER_PATH.exists(), "cost_ledger.jsonl missing")
    def test_ledger_file_complete(self) -> None:
        report = ledger.validate_file()
        self.assertTrue(report["ok"], report["problems"][:5])
        self.assertGreater(report["lines"], 0)


class TestDegradationSelfTest(unittest.TestCase):
    def test_selftest_passes(self) -> None:
        from local_inference import verify

        result = verify.run_selftest()
        self.assertTrue(result["ok"], [c for c in result["cases"] if not c["ok"]])
        self.assertIn("CAPABILITY_BELOW_THRESHOLD", result["event_reason_codes"])
        self.assertIn("SERVICE_UNAVAILABLE", result["event_reason_codes"])
        self.assertIn("PARSE_FAILURE", result["event_reason_codes"])
        self.assertTrue(result["sandbox_ledger"]["ok"])


if __name__ == "__main__":
    unittest.main()
