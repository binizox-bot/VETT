"""Offline unit + integration tests for the R28 closed-loop pipeline.

Run::

    cd VETT_R28_DIFFICULTY_20261112/05_pipeline
    python -m unittest discover -s tests -v

Every test is offline (0 network, 0 paid API).  Real-model calls are exercised
only through the fault-injection path (``--fault local``), which proves the
degradation branch without loading the 7B model.
"""

from __future__ import annotations

import copy
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

PIPE_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PIPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPE_ROOT))

from vett_r28.pipeline import cache as cache_mod  # noqa: E402
from vett_r28.pipeline import config as config_mod  # noqa: E402
from vett_r28.pipeline import gates as gates_mod  # noqa: E402
from vett_r28.pipeline import repairs as repairs_mod  # noqa: E402
from vett_r28.pipeline import routes  # noqa: E402
from vett_r28.pipeline.budget import BudgetLedger  # noqa: E402
from vett_r28.pipeline.cache import ContentAddressedCache, cache_key  # noqa: E402
from vett_r28.pipeline.context import PipelineContext  # noqa: E402
from vett_r28.pipeline.degrade import DegradationManager  # noqa: E402
from vett_r28.pipeline.errors import (BudgetStop, CloudForbidden, CloudUnavailable,  # noqa: E402
                                      Escalated, FrozenViolation, HumanGateRequired,
                                      LocalFirstViolation)
from vett_r28.pipeline.human import HumanGate  # noqa: E402
from vett_r28.pipeline.runner import run, run_gate  # noqa: E402
from vett_r28.pipeline.stages import ALL_STAGES  # noqa: E402

CONFIG_PATH = PIPE_ROOT / "r28.toml"
TEST_RUN_ROOT = "runs/_test"


def load_config():
    config = config_mod.load(CONFIG_PATH)
    config.data["pipeline"]["run_root"] = TEST_RUN_ROOT
    return config


def make_context(config, run_dir: pathlib.Path, *, dry_run=True, fault=None) -> PipelineContext:
    run_dir.mkdir(parents=True, exist_ok=True)
    return PipelineContext(
        config=config,
        run_dir=run_dir,
        dry_run=dry_run,
        resume=False,
        fault=fault,
        allow_human_gate=False,
        run_id="unit",
        cache=ContentAddressedCache(run_dir / "cache"),
        budget=BudgetLedger(run_dir, config.budget_settings()),
        degrade=DegradationManager(run_dir),
        human=HumanGate(allow=False, run_dir=run_dir, r26_15_root=config.r26_15_root()),
        gate_ledger=run_dir / "gate_ledger.jsonl",
    )


class PipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="vett_r28_pipeline_test_"))
        self.config = load_config()
        self.run_root = self.config.run_root()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.addCleanup(shutil.rmtree, self.run_root, True)

    # -- config ---------------------------------------------------------
    def test_config_loads_validates_and_is_deterministic(self):
        problems = self.config.validate()
        self.assertEqual(problems, [])
        self.assertEqual(self.config.digest(), self.config.digest())
        self.assertTrue((PIPE_ROOT / "r28.toml").is_file())
        budget = self.config.budget_settings()
        self.assertFalse(budget["cloud_enabled"])
        self.assertLessEqual(budget["cloud_calls_hard_cap"], 80)

    def test_config_rejects_unsafe_settings(self):
        cfg = load_config()
        cfg.data["budget"]["cloud_enabled"] = True
        cfg.data["run"]["repair_rounds"] = 5
        cfg.data["annotation"]["tasks"] = ["R1_readability"]
        problems = cfg.validate()
        joined = " | ".join(problems)
        self.assertIn("cloud_enabled", joined)
        self.assertIn("repair_rounds", joined)
        self.assertIn("R1_readability", joined)

    # -- cache ----------------------------------------------------------
    def test_cache_key_matches_frozen_protocol(self):
        sys.path.insert(0, str(self.config.path("judge_protocol_scripts")))
        import judge_protocol  # type: ignore

        params = {"temperature": 0.0, "seed": 20261112, "num_ctx": 8192,
                  "num_predict": 256}
        ours = cache_key(task="T1_factor_visibility", input_text="passage text",
                         params=params, prompt_template_version="T1.factor_visibility.v1",
                         model_digest="a" * 64)
        theirs = judge_protocol.cache_key("T1_factor_visibility", "passage text",
                                          params, "T1.factor_visibility.v1", "a" * 64)
        self.assertEqual(ours, theirs)

    def test_cache_roundtrip_and_quarantine(self):
        root = self.tmp / "cache"
        cache = ContentAddressedCache(root)
        record = {
            "task": "S1_span_topic",
            "input_text": "span text",
            "params": {"temperature": 0.0, "seed": 1, "num_ctx": 8192, "num_predict": 16},
            "prompt_template_version": "S1.span_topic.v4",
            "model_digest": "b" * 64,
            "model_tag": "test",
            "tokens": {"in": 3, "out": 2},
            "result": {"status": "OK", "annotation": {"topic": "delivery"}},
        }
        key = cache.put(record)
        self.assertEqual(cache.get(key)["result"]["annotation"]["topic"], "delivery")
        self.assertEqual(cache.stats()["hits"], 1)
        # corrupt the stored basis -> quarantine, never a false hit
        path = cache.object_path(key)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["input_text"] = "different"
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.assertIsNone(cache.get(key))
        self.assertGreaterEqual(cache.stats()["quarantined"], 1)

    # -- budget ---------------------------------------------------------
    def test_budget_breaker_stops_and_writes_stop_file(self):
        ledger = BudgetLedger(self.tmp / "run", {
            "hard_cap_cny": 0.000001, "soft_cap_cny": 0.000001,
            "cloud_calls_hard_cap": 80,
            "local_cost_cny_per_1k_tokens": 10.0,
            "cloud_cost_cny_per_1k_tokens": 10.0,
        })
        with self.assertRaises(BudgetStop):
            ledger.record(stage="annotate", task="T1_factor_visibility", route="local",
                          model_tag="test", cache_hit=False, tokens_in=1000, tokens_out=100)
        self.assertTrue((self.tmp / "run" / "BUDGET_STOP.json").is_file())
        self.assertTrue((self.tmp / "run" / "cost_ledger.jsonl").is_file())
        totals = ledger.totals()
        self.assertTrue(totals["stopped"])

    # -- routing / human ------------------------------------------------
    def test_cache_tampered_result_is_quarantined(self):
        cache = ContentAddressedCache(self.tmp / "cache_tamper")
        record = {
            "task": "C1_cert_sentence_consistency",
            "input_text": "sentence + record",
            "params": {"temperature": 0.0, "seed": 1, "num_ctx": 8192, "num_predict": 16},
            "prompt_template_version": "C1.cert_sentence_consistency.v1",
            "model_digest": "c" * 64,
            "model_tag": "test",
            "tokens": {"in": 3, "out": 2},
            "result": {"status": "OK", "annotation": {"consistent": True}},
        }
        key = cache.put(record)
        path = cache.object_path(key)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["result"]["annotation"]["consistent"] = False  # tamper, keep basis/digest
        path.write_text(json.dumps(payload), encoding="utf-8")
        self.assertIsNone(cache.get(key))
        self.assertGreaterEqual(cache.stats()["quarantined"], 1)
        self.assertTrue(path.with_suffix(path.suffix + ".quarantine").is_file())

    def test_routing_card_tamper_fails_pipeline(self):
        # ALLOW must come from the frozen card: removing T1 from ALLOW must FAIL.
        card = json.loads((PIPE_ROOT.parent / "03_build" / "local" / "routing_card.json")
                          .read_text(encoding="utf-8"))
        card["tasks"]["T1_factor_visibility"]["verdict"] = "DENY"
        tampered = self.tmp / "routing_card_tampered.json"
        tampered.write_text(json.dumps(card), encoding="utf-8")
        config = load_config()
        config.data["paths"]["routing_card"] = str(tampered)
        result = run(config=config, stage="annotate", dry_run=True, run_id="tampered",
                     verbose=False)
        self.assertEqual(result.exit_code, 4)
        self.assertEqual(result.status, "FROZEN_VIOLATION")
        rows = [json.loads(line) for line in
                (result.run_dir / "gate_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
        routing = [row for row in rows if row["gate"] == "G_ROUTING_CARD"]
        self.assertTrue(routing)
        self.assertEqual(routing[-1]["verdict"], "FAIL")

    def test_family_unit_summary(self):
        result = run(config=load_config(), stage="generate", dry_run=True,
                     run_id="family_unit", verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        manifest = json.loads((result.run_dir / "dataset_manifest.json").read_text(encoding="utf-8"))
        unit = manifest["summary"]["family_unit"]
        self.assertTrue(unit["one_question_per_family"])
        self.assertTrue(unit["one_record_per_question"])
        self.assertEqual(unit["max_questions_per_family"], 1)
        self.assertTrue(unit["family_bootstrap_eligible"])

    def test_replay_recomputes_metrics_without_model_calls(self):
        from vett_r28.pipeline.replay import replay

        ledger = self.tmp / "ledger.jsonl"
        entries = [
            {"task": "T1_factor_visibility", "input_sha256": "a" * 64,
             "prompt_template_version": "T1.factor_visibility.v1",
             "raw_output": '{"supported": true, "evidence": "x"}',
             "parsed_output": {"supported": True, "evidence": "x"}},
            {"task": "T1_factor_visibility", "input_sha256": "b" * 64,
             "prompt_template_version": "T1.factor_visibility.v1",
             "raw_output": '{"supported": true, "evidence": "y"}',
             "parsed_output": {"supported": True, "evidence": "y"}},
        ]
        ledger.write_text("\n".join(json.dumps(row) for row in entries) + "\n", encoding="utf-8")
        annotations = self.tmp / "annotations.json"
        annotations.write_text(json.dumps({
            "records": [
                {"task": "T1_factor_visibility", "prompt_sha256": "a" * 64,
                 "status": "OK", "annotation": {"supported": True, "evidence": "x"},
                 "mechanical": {"truth": True}},
                {"task": "T1_factor_visibility", "prompt_sha256": "b" * 64,
                 "status": "OK", "annotation": {"supported": True, "evidence": "y"},
                 "mechanical": {"truth": True}},
            ]
        }), encoding="utf-8")
        judge = self.tmp / "judge.json"
        judge.write_text(json.dumps({"tasks": {"T1_factor_visibility": {
            "n": 2, "ok": 2, "degraded": 0, "comparable_total": 2,
            "comparable_ok": 2, "comparable_degraded": 0, "agreement_rate": 1.0}}}),
            encoding="utf-8")
        report = replay(
            ledger_paths=[ledger],
            local_root=PIPE_ROOT.parent / "03_build" / "local",
            annotations_paths=[annotations],
            judge_path=judge,
            nondeterminism_path=None,
            expect_t1=1.0,
        )
        self.assertTrue(report["all_identical"])
        self.assertEqual(report["reparse_mismatched"], 0)
        self.assertEqual(report["annotations_mismatched"], 0)
        self.assertFalse(report["regenerated_model_output"])
        self.assertEqual(report["model_calls_during_replay"], 0)
        self.assertEqual(report["recomputed_metrics"]["T1_factor_visibility"]["agreement_rate"], 1.0)

    def test_local_first_assertions(self):
        routes.assert_local_first("T1_factor_visibility", "local")
        with self.assertRaises(LocalFirstViolation):
            routes.assert_local_first("T1_factor_visibility", "cloud")
        with self.assertRaises(CloudForbidden):
            routes.CloudRuler(enabled=False).check("T1_factor_visibility")
        with self.assertRaises(CloudUnavailable):
            routes.CloudRuler(enabled=False).check("T3_adjudication")
        with self.assertRaises(CloudForbidden):
            routes.assert_no_paid_provider("openai")
        routes.assert_no_paid_provider("local")
        self.assertTrue(routes.assert_local_endpoint("http://127.0.0.1:11434"))
        with self.assertRaises(LocalFirstViolation):
            routes.assert_local_endpoint("http://example.com:11434")

    def test_human_gate_blocks_publish_and_r26_15_writes(self):
        gate = HumanGate(allow=False, run_dir=self.tmp / "run",
                         r26_15_root=self.config.r26_15_root())
        with self.assertRaises(HumanGateRequired):
            gate.require("publish_decision", reason="test")
        with self.assertRaises(HumanGateRequired):
            gate.require("modify_endpoint", reason="test")
        allowed = HumanGate(allow=True, run_dir=self.tmp / "run",
                            r26_15_root=self.config.r26_15_root())
        allowed.require("publish_decision", reason="test")
        allowed.require("modify_endpoint", reason="test")
        with self.assertRaises(HumanGateRequired):
            allowed.guard_write(self.config.r26_15_root() / "MANIFEST.json")
        allowed.guard_write(self.tmp / "safe.json")

    def test_endpoint_modification_config_needs_human_gate(self):
        config = load_config()
        config.data.setdefault("run", {})["modify_endpoint"] = True
        result = run(config=config, stage="bootstrap", dry_run=True, run_id="endpoint",
                     verbose=False)
        self.assertEqual(result.exit_code, 7)
        self.assertEqual(result.status, "HUMAN_GATE_REQUIRED")

    # -- registry / gate loop -------------------------------------------
    def test_registry_is_complete_and_valid(self):
        self.assertEqual(gates_mod.validate_registry(repairs_mod.repair_ids()), [])
        snapshot = gates_mod.registry_snapshot()
        self.assertGreaterEqual(snapshot["gate_count"], 15)
        for stage in ALL_STAGES:
            self.assertIn(stage, gates_mod.STAGE_GATES)
            self.assertTrue(gates_mod.STAGE_GATES[stage])
        for gate_id, spec in gates_mod.REGISTRY.items():
            if spec.repair_id:
                self.assertIn(spec.repair_id, repairs_mod.REPAIRS)

    def test_gate_loop_is_bounded_and_escalates(self):
        ctx = make_context(self.config, self.tmp / "escalation")
        attempts = {"count": 0}
        repairs = {"count": 0}

        def failing_gate(context):
            attempts["count"] += 1
            return {"verdict": "FAIL", "evidence": {"attempt": attempts["count"]}}

        def noop_repair(context):
            repairs["count"] += 1
            return {"ok": False, "action": "noop"}

        gate_id = "G_TEST_BOUNDED"
        repair_id = "repair_test_bounded"
        gates_mod.REGISTRY[gate_id] = gates_mod.GateSpec(
            gate_id=gate_id, stage="judge", description="test", blocking=True,
            repair_id=repair_id, exit_code=3, fn=failing_gate)
        repairs_mod.REPAIRS[repair_id] = repairs_mod.RepairSpec(
            repair_id=repair_id, gate_id=gate_id, description="test", fn=noop_repair)
        try:
            with self.assertRaises(Escalated):
                run_gate(ctx, gate_id)
        finally:
            gates_mod.REGISTRY.pop(gate_id, None)
            repairs_mod.REPAIRS.pop(repair_id, None)
        self.assertEqual(attempts["count"], 3)  # initial + exactly 2 repairs
        self.assertEqual(repairs["count"], 2)
        self.assertTrue((ctx.run_dir / "ESCALATED.json").is_file())
        verdicts = [entry["verdict"] for entry in ctx.gate_results if entry["gate"] == gate_id]
        self.assertEqual(verdicts, ["FAIL", "FAIL", "FAIL", "ESCALATED"])

    def test_nonblocking_degraded_gate_continues(self):
        ctx = make_context(self.config, self.tmp / "degraded_gate")
        gate_id = "G_TEST_DEGRADED"
        gates_mod.REGISTRY[gate_id] = gates_mod.GateSpec(
            gate_id=gate_id, stage="annotate", description="test", blocking=False,
            repair_id=None, exit_code=3,
            fn=lambda context: {"verdict": "DEGRADED", "evidence": {"coverage": 0.0}})
        try:
            result = run_gate(ctx, gate_id)
        finally:
            gates_mod.REGISTRY.pop(gate_id, None)
        self.assertEqual(result["verdict"], "DEGRADED")
        self.assertFalse((ctx.run_dir / "ESCALATED.json").exists())

    def test_frozen_gate_aborts_with_exit_4(self):
        ctx = make_context(self.config, self.tmp / "frozen_gate")
        gate_id = "G_TEST_FROZEN"
        gates_mod.REGISTRY[gate_id] = gates_mod.GateSpec(
            gate_id=gate_id, stage="bootstrap", description="test", blocking=True,
            repair_id=None, exit_code=4,
            fn=lambda context: {"verdict": "FAIL", "evidence": {"drift": True}})
        try:
            with self.assertRaises(FrozenViolation):
                run_gate(ctx, gate_id)
        finally:
            gates_mod.REGISTRY.pop(gate_id, None)
        self.assertEqual(ctx.gate_results[-1]["verdict"], "FAIL")

    # -- end-to-end -----------------------------------------------------
    def test_dry_run_green_and_cache_replay_identical(self):
        first = run(config=load_config(), stage="all", dry_run=True, run_id="e2e",
                    verbose=False)
        self.assertEqual(first.exit_code, 0, first.error)
        self.assertEqual(first.status, "OK")
        hashes_path = first.run_dir / "ARTIFACT_HASHES.json"
        first_hashes = hashes_path.read_text(encoding="utf-8")
        first_manifest = json.loads((first.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(first_manifest["cache"]["hits"], 0)
        self.assertGreater(first_manifest["cache"]["misses"], 0)

        second = run(config=load_config(), stage="all", dry_run=True, run_id="e2e",
                     verbose=False)
        self.assertEqual(second.exit_code, 0, second.error)
        second_hashes = hashes_path.read_text(encoding="utf-8")
        self.assertEqual(first_hashes, second_hashes)
        manifest = json.loads((second.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["cache"]["hits"], manifest["budget"]["calls"])
        self.assertEqual(manifest["cache"]["misses"], 0)
        replay = json.loads((second.run_dir / "REPLAY_CHECK.json").read_text(encoding="utf-8"))
        self.assertTrue(replay["identical"])
        self.assertTrue(replay["previous_present"])
        judged = json.loads((second.run_dir / "judge.json").read_text(encoding="utf-8"))
        self.assertEqual(judged["endpoints"]["paired_accuracy_drop"]["status"], "NOT_RUN")
        self.assertFalse(judged["endpoints"]["paired_accuracy_drop"]["claim"])

    def test_dry_run_report_has_all_sections_and_no_endpoint_claim(self):
        result = run(config=load_config(), stage="all", dry_run=True, run_id="report",
                     verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        text = (result.run_dir / "REPORT.md").read_text(encoding="utf-8")
        for section in ("## 1. 概览", "## 2. 冻结输入与零漂移", "## 3. 数据集",
                        "## 4. 标注", "## 5. 判分", "## 6. 端点状态",
                        "## 7. 门与修复", "## 8. 预算", "## 9. 降级",
                        "## 10. 复现", "## 11. 产物哈希"):
            self.assertIn(section, text)
        self.assertIn("NOT_RUN", text)
        self.assertIn("R26.15", text)
        self.assertNotIn("vs 0.25", text)

    def test_dry_run_touches_nothing_outside_run_dir(self):
        result = run(config=load_config(), stage="all", dry_run=True, run_id="confined",
                     verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        self.assertTrue(str(result.run_dir).startswith(str(PIPE_ROOT)))
        self.assertNotIn("r26_15_content_dependency_candidate_v3", str(result.run_dir))
        # The frozen candidate is still byte-identical (bootstrap gates already check
        # this, we assert the count/bytes contract again here).
        build = PIPE_ROOT.parent / "03_build"
        if str(build) not in sys.path:
            sys.path.insert(0, str(build))
        from r28gen.verify import verify_r26_15_against_backup  # type: ignore

        verify = verify_r26_15_against_backup()
        self.assertTrue(verify["ok"])
        self.assertEqual(verify["file_count"], 165)
        self.assertEqual(verify["total_bytes"], 93346177)

    def test_fault_local_degrades_and_chain_continues(self):
        result = run(config=load_config(), stage="all", dry_run=False, run_id="live_degraded",
                     fault="local", limit_instances=1, sample_instances=1, verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        manifest = json.loads((result.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(manifest["degradation"]["count"], 3)
        self.assertIn("LOCAL_SERVICE_UNAVAILABLE", manifest["degradation"]["by_reason_code"])
        annotations = json.loads((result.run_dir / "annotations.json").read_text(encoding="utf-8"))
        self.assertEqual(annotations["mode"], "mechanical_only")
        self.assertEqual(annotations["metrics"]["coverage"], 0.0)

    def test_resume_skips_completed_stages(self):
        first = run(config=load_config(), stage="all", dry_run=True, run_id="resume",
                    verbose=False)
        self.assertEqual(first.exit_code, 0, first.error)
        second = run(config=load_config(), stage="all", dry_run=True, run_id="resume",
                     resume=True, verbose=False)
        self.assertEqual(second.exit_code, 0, second.error)
        manifest = json.loads((second.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["resumed_stages"], list(ALL_STAGES))
        self.assertEqual(manifest["budget"]["calls"], 0)

    def test_publish_requires_human_gate(self):
        result = run(config=load_config(), stage="publish", dry_run=True, run_id="publish",
                     verbose=False)
        self.assertEqual(result.exit_code, 7)
        self.assertEqual(result.status, "HUMAN_GATE_REQUIRED")
        self.assertFalse((result.run_dir / "PUBLISH_READINESS.json").exists())

    def test_publish_with_allow_writes_packet_only(self):
        result = run(config=load_config(), stage="publish", dry_run=True, run_id="publish_ok",
                     allow_human_gate=True, verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        payload = json.loads((result.run_dir / "PUBLISH_READINESS.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "AWAITING_HUMAN_SIGNATURE")

    def test_budget_stop_halts_pipeline(self):
        config = load_config()
        config.data["budget"]["hard_cap_cny"] = 0.000001
        config.data["budget"]["soft_cap_cny"] = 0.0
        config.data["budget"]["local_cost_cny_per_1k_tokens"] = 10.0
        result = run(config=config, stage="all", dry_run=True, run_id="budget",
                     verbose=False)
        self.assertEqual(result.exit_code, 5)
        self.assertEqual(result.status, "BUDGET_STOP")
        self.assertTrue((result.run_dir / "BUDGET_STOP.json").is_file())

    def test_disk_fault_falls_back_and_continues(self):
        result = run(config=load_config(), stage="all", dry_run=True, run_id="disk",
                     fault="disk", verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        manifest = json.loads((result.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNotNone(manifest["fallback_dir"])
        self.assertIn("DISK_UNAVAILABLE", manifest["degradation"]["by_reason_code"])
        shutil.rmtree(pathlib.Path(manifest["fallback_dir"]), ignore_errors=True)

    def test_single_stage_runs_prerequisites(self):
        result = run(config=load_config(), stage="report", dry_run=True, run_id="single",
                     verbose=False)
        self.assertEqual(result.exit_code, 0, result.error)
        manifest = json.loads((result.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([stage["status"] for stage in manifest["stage_results"].values()],
                         ["done"] * len(ALL_STAGES))


if __name__ == "__main__":
    unittest.main(verbosity=2)
