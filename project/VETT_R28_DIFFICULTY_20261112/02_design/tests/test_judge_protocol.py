"""Offline unit tests for the frozen judge protocol (no network, no model, no GPU).

Run:
    cd VETT_R28_DIFFICULTY_20261112\\02_design
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN_ROOT = HERE.parent
sys.path.insert(0, str(DESIGN_ROOT / "scripts"))

import judge_protocol as jp  # noqa: E402

PROTOCOL_PATH = DESIGN_ROOT / "protocol.json"


def ok_record() -> dict:
    return {field: 0 for field in jp.RECORD_FIELDS}


SALT = "unit-test-salt-0123456789abcdef"


class AuthorityTests(unittest.TestCase):
    """The protocol must mirror the routing card, never invent capability."""

    def test_allow_set_is_exactly_four(self):
        allow = jp.allowed_local_tasks()
        self.assertEqual(allow, sorted([
            "T1_factor_visibility", "T2_naturalness", "S1_span_topic",
            "C1_cert_sentence_consistency"]))

    def test_deny_set_is_exactly_nine(self):
        deny = jp.denied_local_tasks()
        self.assertEqual(len(deny), 9)
        for task in ("D1_12_field_record_derivation", "D8_T3_adjudication", "R1_readability"):
            self.assertIn(task, deny)

    def test_allow_routes_carry_measured_agreement(self):
        for task in jp.allowed_local_tasks():
            route = jp.local_route_at_judge_time(task)
            self.assertEqual(route["verdict"], "ALLOW", task)
            measured = route["measured"]
            self.assertGreaterEqual(measured["agreement"], 0.85, task)
            self.assertGreaterEqual(measured["n"], 30, task)

    def test_missing_card_fails_safe(self):
        route = jp.local_route_at_judge_time("T1_factor_visibility", card={})
        self.assertEqual(route["verdict"], "DENY")
        self.assertEqual(route["reason_code"], "TASK_DENIED")

    def test_unknown_task_is_denied(self):
        route = jp.local_route_at_judge_time("T9_made_up_task")
        self.assertEqual(route["verdict"], "DENY")

    def test_unmeasured_matrix_is_denied(self):
        card = jp.load_routing_card()
        route = jp.local_route_at_judge_time("T1_factor_visibility", card=card, matrix={})
        self.assertEqual(route["verdict"], "DENY")
        self.assertEqual(route["reason_code"], "CAPABILITY_UNMEASURED")

    def test_r1_deny_evidence(self):
        route = jp.local_route_at_judge_time("R1_readability")
        self.assertEqual(route["verdict"], "DENY")
        self.assertEqual(route["reason_code"], "CAPABILITY_BELOW_THRESHOLD")
        self.assertEqual(route["fallback_used"], "flesch_reading_ease_band")
        self.assertLess(route["measured"]["agreement"], 0.85)

    def test_policy_denies_have_no_measurement(self):
        self.assertEqual(sorted(jp.POLICY_DENY_TASKS),
                         ["D5_contract_or_code_design", "D8_T3_adjudication"])


class LocalGateTests(unittest.TestCase):

    def test_allow_at_task_cap(self):
        for task, cap in (("T1_factor_visibility", 3000), ("S1_span_topic", 1000)):
            self.assertEqual(jp.assert_local_allowed(task, tokens=cap)["verdict"], "ALLOW")

    def test_over_task_cap_raises(self):
        with self.assertRaises(jp.InputCapExceeded):
            jp.assert_local_allowed("S1_span_topic", tokens=1001)

    def test_hard_ceiling_raises(self):
        with self.assertRaises(jp.InputCapExceeded):
            jp.assert_local_allowed("T1_factor_visibility", tokens=jp.HARD_INPUT_CAP_TOKENS + 1)

    def test_prompt_path_uses_conservative_estimator(self):
        text = "x" * (3 * (jp.HARD_INPUT_CAP_TOKENS + 1))
        self.assertGreater(jp.estimate_tokens(text), jp.HARD_INPUT_CAP_TOKENS)
        with self.assertRaises(jp.InputCapExceeded):
            jp.assert_local_allowed("T1_factor_visibility", prompt=text)

    def test_deny_tasks_raise(self):
        for task in jp.denied_local_tasks():
            with self.assertRaises(jp.ProtocolError):
                jp.assert_local_allowed(task, tokens=10)

    def test_r1_raises_specific_class(self):
        with self.assertRaises(jp.CapabilityBelowThreshold):
            jp.assert_local_allowed("R1_readability", tokens=10)


class CapabilityGateTests(unittest.TestCase):

    def test_n_below_minimum_is_denied(self):
        gate = jp.gate_capability(task="X", ruler="local", n=29, agreement=1.0)
        self.assertEqual(gate["verdict"], "DENY")
        self.assertEqual(gate["label"], "DESCRIPTIVE_ONLY")

    def test_unmeasured_is_denied(self):
        gate = jp.gate_capability(task="X", ruler="local", n=None, agreement=None)
        self.assertEqual(gate["verdict"], "DENY")

    def test_threshold_boundary(self):
        self.assertEqual(jp.gate_capability(task="X", ruler="local", n=30,
                                            agreement=0.85)["verdict"], "ALLOW")
        self.assertEqual(jp.gate_capability(task="X", ruler="local", n=30,
                                            agreement=0.8499)["verdict"], "DENY")

    def test_cloud_is_stricter(self):
        self.assertEqual(jp.gate_capability(task="T3_adjudication", ruler="cloud", n=30,
                                            agreement=0.89)["verdict"], "DENY")
        self.assertEqual(jp.gate_capability(task="T3_adjudication", ruler="cloud", n=30,
                                            agreement=0.91)["verdict"], "ALLOW")
        self.assertEqual(jp.gate_capability(task="T3_adjudication", ruler="cloud", n=12,
                                            agreement=0.99)["label"], "DESCRIPTIVE_ONLY")

    def test_matrix_deny_overrides(self):
        gate = jp.gate_capability(task="R1_readability", ruler="local", n=30,
                                  agreement=0.99, matrix_verdict="DENY")
        self.assertEqual(gate["verdict"], "DENY")


class CloudGateTests(unittest.TestCase):

    def test_planned_workload_fits_caps(self):
        workload = jp.workload_split()
        self.assertLessEqual(workload["cloud"]["calls_total"], jp.CLOUD_TOTAL_CALL_CAP)
        self.assertEqual(workload["cloud"]["calls_total"], 52)
        self.assertEqual(workload["local"]["calls_total"], 6400)

    def test_sampling_caps(self):
        jp.assert_cloud_allowed("T3_adjudication", 12)
        jp.assert_cloud_allowed("T1_cross_check", 24)
        jp.assert_cloud_allowed("T2_cross_check", 16)
        with self.assertRaises(jp.CloudBudgetExceeded):
            jp.assert_cloud_allowed("T1_cross_check", 25)
        with self.assertRaises(jp.CloudBudgetExceeded):
            jp.assert_cloud_allowed("T3_adjudication", 13)

    def test_total_cap(self):
        with self.assertRaises(jp.CloudBudgetExceeded):
            jp.assert_cloud_allowed("T1_cross_check", 24, used_calls=70)

    def test_paid_provider_refused(self):
        for provider in ("openai", "anthropic", "http://x", "gemini"):
            with self.assertRaises(jp.PaidProviderForbidden):
                jp.assert_cloud_allowed("T3_adjudication", 1, provider=provider)

    def test_unknown_cloud_task_refused(self):
        with self.assertRaises(jp.TaskDenied):
            jp.assert_cloud_allowed("T1_full_run", 1)


class BlindPacketTests(unittest.TestCase):

    def test_clean_item_is_stripped(self):
        item = {"passage": "Four runs were scored off the bat.",
                "instance_id": "match_0003", "scenario_family": "L3_NB_LBW",
                "level": 3, "difficulty_vector": {"x": 1}, "private_gold": {"a": 1}}
        packet = jp.build_blind_packet(item, "T1_factor_visibility", SALT)
        self.assertEqual(sorted(packet["payload"]), ["passage"])
        self.assertEqual(packet["contains_answer"], False)
        self.assertEqual(jp.audit_packet(packet), [])
        blob = jp.canonical_json(packet)
        for needle in ("match_0003", "L3_NB_LBW", "private_gold", "difficulty_vector"):
            self.assertNotIn(needle, blob)

    def test_forbidden_key_inside_payload(self):
        packet = {
            "schema_version": "vett-blind-packet/v1", "packet_id": "pkt_0123456789abcdef",
            "item_handle": "0123456789abcdef", "task": "T1_factor_visibility",
            "ruler": "local", "prompt_template_version": "v1", "token_estimate": 5,
            "contains_answer": False, "payload": {"passage": "x", "level": 2},
        }
        codes = {v["code"] for v in jp.audit_packet(packet)}
        self.assertIn("BP-WHITELIST", codes)
        self.assertIn("BP-FORBIDDEN-KEY", codes)

    def test_forbidden_content_patterns(self):
        cases = {
            "match id": "as in match_0021 the batter scored",
            "family": "family L5_RUNOUT_LATER_BOUNDARY says four",
            "level": "level L3 dossier",
            "difficulty": "this is harder, dose 2",
            "path": "see C:\\VETT\\dataset\\row.json",
            "r28 item id": "item r28q_0001 leaked",
            "r28 held-out id": "twin r28h_0005 leaked",
            "r28 family": "family rfam_83faedd9516b leaked",
            "r28 span id": "span r28fact_446afd688a87582ab949 leaked",
            "r28 rule id": "rule r28rule_e2e38c24dc261b9ef56b leaked",
            "r28 bind id": "binding r28bind_abc123 leaked",
            "r28 masked id": "masked cell r28masked_aa11 leaked",
        }
        for label, text in cases.items():
            item = {"passage": text, "instance_id": "i1"}
            with self.assertRaises(jp.BlindPacketViolation, msg=label):
                jp.build_blind_packet(item, "T1_factor_visibility", SALT)

    def test_r28_id_patterns_present(self):
        ids = {p["id"] for p in jp.BLIND_FORBIDDEN_PATTERNS}
        for expected in ("BP-R28-ID", "BP-R28-HELDOUT-ITEM", "BP-R28-FAMILY"):
            self.assertIn(expected, ids)

    def test_every_measured_r28_span_prefix_is_blocked(self):
        """PAMEND-004: a shape rule must catch every measured prefix, not a hand-listed few."""
        prefixes = ("r28authpolicy", "r28bind", "r28conflict", "r28fact", "r28masked",
                    "r28rev", "r28revpolicy", "r28rule", "r28scope", "r28shadow")
        for prefix in prefixes:
            sample = f"{prefix}_0123456789abcdef"
            item = {"span_text": f"the span {sample} says four", "instance_id": "i1"}
            with self.assertRaises(jp.BlindPacketViolation, msg=prefix):
                jp.build_blind_packet(item, "S1_span_topic", SALT)

    def test_r28_shape_rule_does_not_fire_on_prose(self):
        for text in ("Four runs were scored off the bat.",
                     "over 28 overs the chase ended",
                     "r28 is not an id here",
                     "verdict: no ball, 1 run"):
            packet = jp.build_blind_packet({"passage": text, "instance_id": "i2"},
                                           "T1_factor_visibility", SALT)
            self.assertEqual(jp.audit_packet(packet), [], text)

    def test_short_salt_refused(self):
        with self.assertRaises(jp.BlindPacketViolation):
            jp.build_blind_packet({"passage": "x", "instance_id": "i"}, "T1_factor_visibility", "short")

    def test_unknown_task_refused(self):
        with self.assertRaises(jp.BlindPacketViolation):
            jp.build_blind_packet({"passage": "x", "instance_id": "i"},
                                  "D1_12_field_record_derivation", SALT)

    def test_missing_field_refused(self):
        with self.assertRaises(jp.BlindPacketViolation):
            jp.build_blind_packet({"instance_id": "i"}, "T1_factor_visibility", SALT)

    def test_c1_requires_contains_answer(self):
        packet = jp.build_blind_packet({"sentence": "x", "record": ok_record(),
                                        "instance_id": "i"}, "C1_cert_sentence_consistency", SALT)
        self.assertTrue(packet["contains_answer"])
        tampered = dict(packet, contains_answer=False)
        codes = {v["code"] for v in jp.audit_packet(tampered)}
        self.assertIn("BP-CONTAINS-ANSWER", codes)

    def test_handle_stability_and_salt_sensitivity(self):
        a = jp.build_blind_packet({"passage": "x", "instance_id": "i"}, "T1_factor_visibility", SALT)
        b = jp.build_blind_packet({"passage": "x", "instance_id": "i"}, "T1_factor_visibility", SALT)
        c = jp.build_blind_packet({"passage": "x", "instance_id": "i"},
                                  "T1_factor_visibility", SALT + "different")
        self.assertEqual(a["item_handle"], b["item_handle"])
        self.assertNotEqual(a["item_handle"], c["item_handle"])
        self.assertRegex(a["item_handle"], r"^[0-9a-f]{16}$")


class CanonicalRecordTests(unittest.TestCase):

    def test_sorted_and_narrowed(self):
        record = {"total_runs": "4", "batter_runs": 4.0, **{f: 0 for f in jp.RECORD_FIELDS
                                                            if f not in ("total_runs", "batter_runs")}}
        canonical = jp.canonical_record(record)
        self.assertEqual(list(canonical), sorted(jp.RECORD_FIELDS))
        self.assertEqual(canonical["total_runs"], 4)
        self.assertIsInstance(canonical["batter_runs"], int)

    def test_extra_field_rejected(self):
        with self.assertRaises(jp.BlindPacketViolation):
            jp.canonical_record({**ok_record(), "gold": 1})

    def test_missing_field_rejected(self):
        with self.assertRaises(jp.BlindPacketViolation):
            jp.canonical_record({"batter_runs": 1})

    def test_boolean_rejected(self):
        record = ok_record()
        record["delivery_status"] = True
        with self.assertRaises(jp.BlindPacketViolation):
            jp.canonical_record(record)


class CacheTests(unittest.TestCase):
    PARAMS = {"temperature": 0.0, "seed": 20261112, "num_ctx": 8192, "num_predict": 128}

    def key(self, **overrides):
        params = dict(self.PARAMS, **{k: v for k, v in overrides.items()
                                      if k in self.PARAMS})
        return jp.cache_key(overrides.get("task", "T1_factor_visibility"),
                            overrides.get("text", "P"),
                            params,
                            overrides.get("template", "T1.factor_visibility.v1"),
                            overrides.get("digest", jp.MODEL_DIGEST))

    def test_deterministic(self):
        self.assertEqual(self.key(), self.key())

    def test_sensitive_to_every_field(self):
        base = self.key()
        self.assertNotEqual(base, self.key(text="P "))
        self.assertNotEqual(base, self.key(temperature=0.1))
        self.assertNotEqual(base, self.key(seed=7))
        self.assertNotEqual(base, self.key(num_ctx=4096))
        self.assertNotEqual(base, self.key(num_predict=96))
        self.assertNotEqual(base, self.key(template="T1.factor_visibility.v2"))
        self.assertNotEqual(base, self.key(digest="0" * 64))
        self.assertNotEqual(base, self.key(task="T2_naturalness"))

    def test_missing_params_rejected(self):
        with self.assertRaises(jp.ProtocolError):
            jp.cache_key("T1_factor_visibility", "P", {"temperature": 0.0}, "v1", jp.MODEL_DIGEST)

    def test_digest_required(self):
        with self.assertRaises(jp.ProtocolError):
            jp.cache_key("T1_factor_visibility", "P", self.PARAMS, "v1", "")

    def test_legacy_key_formula_and_divergence(self):
        v1 = jp.legacy_cache_key_v1("T1_factor_visibility", "PROMPT", "T1.factor_visibility.v1")
        self.assertEqual(v1, jp.legacy_cache_key_v1("T1_factor_visibility", "PROMPT",
                                                    "T1.factor_visibility.v1"))
        self.assertEqual(v1, jp.sha256_text("|".join([
            "vett-local-cache/v1", "T1.factor_visibility.v1", jp.MODEL_TAG,
            str(jp.TEMPERATURE), str(jp.SEED), str(jp.HARD_INPUT_CAP_TOKENS), "256", "PROMPT"])))
        v2 = jp.cache_key("T1_factor_visibility", "PROMPT", self.PARAMS,
                          "T1.factor_visibility.v1", jp.MODEL_DIGEST)
        self.assertNotEqual(v1, v2)


class ReplayTests(unittest.TestCase):

    ENTRY = {
        "task": "T1_factor_visibility", "input_sha256": "a" * 64,
        "prompt_template_version": "T1.factor_visibility.v1", "temperature": 0.0,
        "seed": 20261112, "model_tag": jp.MODEL_TAG,
        "raw_output": '{"supported": true, "evidence": "four runs"}',
        "parsed_output": {"supported": True, "evidence": "four runs"},
        "wall_clock": 0.2,
    }

    def parse(self, raw):
        return {"supported": '"supported": true' in raw, "evidence": "four runs"}, True, None

    def test_replay_is_recompute_not_regeneration(self):
        result = jp.replay_score(self.ENTRY, self.parse)
        self.assertFalse(result["regenerated_model_output"])
        self.assertTrue(result["parsed_matches_ledger"])

    def test_replay_digest_stable(self):
        a = jp.replay_score(self.ENTRY, self.parse)
        b = jp.replay_score(self.ENTRY, self.parse)
        self.assertEqual(a["replay_digest"], b["replay_digest"])

    def test_missing_raw_output_refused(self):
        broken = dict(self.ENTRY)
        broken["raw_output"] = ""
        with self.assertRaises(jp.ReplayUnavailable):
            jp.replay_score(broken, self.parse)

    def test_missing_ledger_field_refused(self):
        broken = dict(self.ENTRY)
        broken.pop("temperature")
        with self.assertRaises(jp.ReplayUnavailable):
            jp.assert_replayable(broken)

    def test_parser_compatibility_policy(self):
        v4 = jp.replay_parser_compatible({"task": "S1_span_topic",
                                          "prompt_template_version": "S1.span_topic.v4"})
        v2 = jp.replay_parser_compatible({"task": "S1_span_topic",
                                          "prompt_template_version": "S1.span_topic.v2"})
        self.assertEqual(v4["replay_status"], "COMPATIBLE")
        self.assertEqual(v2["replay_status"], "PARSER_INCOMPATIBLE_LEGACY")
        self.assertFalse(v2["parser_compatible"])


class BaselineGateTests(unittest.TestCase):

    def block(self, **overrides):
        block = {
            "informative_field_accuracy": 0.45, "record_exact": 0.10,
            "n_items": 320, "n_families": 320, "n_distinct_records": 320,
            "baselines": {
                "constant_prior": {"reference_rate": 0.5288888888888889,
                                   "same_set_rate": 0.55, "status": "MEASURED"},
                "question_text_tfidf_logreg": {"reference_rate": 0.5422222222222223,
                                               "same_set_rate": 0.50, "status": "MEASURED"},
                "anchor_mode": {"reference_rate": 0.7333333333333333,
                                "same_set_rate": 0.72, "status": "MEASURED"},
                "anchor_record_exact": {"reference_rate": 0.32, "same_set_rate": 0.30,
                                        "status": "MEASURED"},
            },
        }
        block.update(overrides)
        return block

    def test_complete_report_passes(self):
        self.assertEqual(jp.require_baseline_trio(self.block())["status"], "PASS")

    def test_missing_baseline_refused(self):
        block = self.block()
        block["baselines"] = {k: v for k, v in block["baselines"].items() if k != "anchor_mode"}
        with self.assertRaises(jp.BaselineTrioMissing):
            jp.require_baseline_trio(block)

    def test_single_baseline_refused(self):
        block = self.block()
        block["baselines"] = {"constant_prior": block["baselines"]["constant_prior"],
                             "anchor_record_exact": block["baselines"]["anchor_record_exact"]}
        with self.assertRaises(jp.BaselineTrioMissing):
            jp.require_baseline_trio(block)

    def test_above_anchor_fails(self):
        self.assertEqual(jp.require_baseline_trio(
            self.block(informative_field_accuracy=0.74))["status"], "FAIL")

    def test_unmeasured_same_set_is_untested(self):
        block = self.block()
        block["baselines"]["anchor_mode"] = {"reference_rate": 0.7333333333333333,
                                             "same_set_rate": None, "status": "UNTESTED"}
        self.assertEqual(jp.require_baseline_trio(block)["status"], "UNTESTED")

    def test_missing_en_fields_refused(self):
        block = self.block()
        block.pop("n_families")
        with self.assertRaises(jp.BaselineTrioMissing):
            jp.require_baseline_trio(block)

    def test_reference_values_match_the_frozen_baselines(self):
        baselines = jp.load_json(jp.BASELINES_PATH)["baselines"]
        self.assertEqual(baselines["constant_75_to_25"]["field_accuracy_informative"]["rate"],
                         jp.BASELINE_TRIO[0]["reference_rate"])
        self.assertEqual(baselines["tfidf_logreg_question_text_75_to_25"]
                         ["field_accuracy_informative"]["rate"], jp.BASELINE_TRIO[1]["reference_rate"])
        self.assertEqual(baselines["anchor_classifier_75_to_25"]["field_accuracy_informative"]["rate"],
                         jp.BASELINE_TRIO[2]["reference_rate"])
        self.assertEqual(baselines["anchor_classifier_75_to_25"]["record_exact"]["rate"],
                         jp.RECORD_EXACT_BASELINE["reference_rate"])


class EffectiveNTests(unittest.TestCase):

    def codes(self, block, comparison="r28"):
        return [v["code"] for v in jp.check_effective_n(block, comparison=comparison)["violations"]]

    def test_valid_block(self):
        block = {"n_items": 320, "n_families": 320, "n_distinct_records": 320,
                 "independent_units": 320, "pairing": "item"}
        self.assertTrue(jp.check_effective_n(block)["ok"])

    def test_twin_arms_do_not_add_n(self):
        block = {"n_items": 320, "n_families": 320, "n_distinct_records": 320,
                 "independent_units": 640, "pairing": "item"}
        self.assertIn("EN5", self.codes(block))

    def test_field_level_pseudo_n(self):
        block = {"n_items": 320, "n_families": 320, "n_distinct_records": 320,
                 "independent_units": 2880}
        self.assertIn("EN5", self.codes(block))

    def test_r2615_must_cluster_by_family(self):
        block = {"n_items": 100, "n_families": 100, "n_distinct_records": 16,
                 "bootstrap_unit": "item"}
        codes = self.codes(block, "r26_15")
        self.assertIn("EN1", codes)
        self.assertIn("EN3", codes)

    def test_cross_dataset_must_be_exploratory(self):
        self.assertIn("EN6", self.codes({"n_items": 320, "n_families": 320,
                                         "n_distinct_records": 320}, "cross"))

    def test_missing_triplet(self):
        self.assertEqual(self.codes({"n_items": 320}), ["EN2"])


class DegradedTests(unittest.TestCase):

    def event(self, **overrides):
        payload = {"task": "R1_readability", "reason_code": "CAPABILITY_BELOW_THRESHOLD",
                   "reason": "agreement 0.6667", "fallback_used": "flesch_reading_ease_band",
                   "affected_items": ["R1-1"], "scope": "local"}
        payload.update(overrides)
        return jp.make_degraded(**payload)

    def test_required_fields(self):
        event = self.event()
        for field in ("task", "reason_code", "fallback_used", "affected_items"):
            self.assertIn(field, event)
        self.assertEqual(jp.validate_degraded(event), [])

    def test_unknown_reason_code_rejected(self):
        with self.assertRaises(ValueError):
            self.event(reason_code="NOT_A_CODE")

    def test_empty_affected_items_rejected(self):
        with self.assertRaises(ValueError):
            self.event(affected_items=[])

    def test_missing_fallback_rejected(self):
        with self.assertRaises(ValueError):
            self.event(fallback_used="")

    def test_bad_scope_rejected(self):
        with self.assertRaises(ValueError):
            self.event(scope="nowhere")

    def test_legacy_event_normalised(self):
        legacy = {"schema_version": "vett-degraded-event/v1", "task": "R1_readability",
                  "status": "DEGRADED", "reason_code": "CAPABILITY_BELOW_THRESHOLD",
                  "reason": "below gate", "source": "t13",
                  "fallback": "flesch_reading_ease_band",
                  "timestamp_utc": "2026-11-12T00:00:00Z",
                  "evidence": {"input_sha256": "b" * 64}}
        upgraded = jp.normalize_degraded(legacy)
        self.assertEqual(upgraded["schema_version"], jp.DEGRADED_SCHEMA)
        self.assertEqual(upgraded["fallback_used"], "flesch_reading_ease_band")
        self.assertEqual(upgraded["affected_items"], ["b" * 64])
        self.assertEqual(jp.validate_degraded(upgraded), [])

    def test_legacy_without_fallback_refused(self):
        with self.assertRaises(ValueError):
            jp.normalize_degraded({"schema_version": "vett-degraded-event/v1",
                                   "task": "X", "reason_code": "TASK_DENIED"})

    def test_reason_code_union(self):
        self.assertEqual(len(jp.T18_REASON_CODES), 14)
        self.assertEqual(len(jp.JUDGE_REASON_CODES), 23)
        for code in jp.T18_REASON_CODES:
            self.assertIn(code, jp.JUDGE_REASON_CODES)


class ProtocolArtifactTests(unittest.TestCase):
    """protocol.json / PROTOCOL.md must agree with the code that produced them."""

    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))

    def test_rule_ids_match_code(self):
        json_ids = {r["id"] for r in self.protocol["rules"]}
        self.assertEqual(json_ids, set(jp.RULE_IDS))
        self.assertEqual(len(jp.RULE_IDS), len(set(jp.RULE_IDS)))

    def test_rule_shape(self):
        for rule in jp.RULES:
            self.assertIn(rule["level"], ("MUST", "MUST_NOT"), rule["id"])
            self.assertTrue(rule["section"], rule["id"])
            self.assertTrue(rule["text"], rule["id"])
            self.assertTrue(rule["enforces"], rule["id"])

    def test_task_rule_ids_exist(self):
        known = set(jp.RULE_IDS)
        for spec in list(jp.LOCAL_TASK_SPEC.values()) + list(jp.LOCAL_DENY_SPEC.values()):
            for rule_id in spec["rule_ids"]:
                self.assertIn(rule_id, known)

    def test_counts_and_verdicts(self):
        counts = self.protocol["rulers"]["local"]["counts"]
        self.assertEqual(counts, {"allow": 4, "deny": 9, "total": 13})
        for entry in self.protocol["rulers"]["local"]["allow"]:
            self.assertEqual(entry["verdict"], "ALLOW")
            self.assertGreaterEqual(entry["measured"]["agreement"], 0.85)
        for entry in self.protocol["rulers"]["local"]["deny"]:
            self.assertEqual(entry["verdict"], "DENY")
            self.assertTrue(entry["deny_reason"])

    def test_deny_evidence_classes(self):
        statuses = {e["task"]: e["evidence_status"] for e in self.protocol["rulers"]["local"]["deny"]}
        for task, status in statuses.items():
            self.assertEqual(status, "POLICY_NO_MEASUREMENT" if task in jp.POLICY_DENY_TASKS
                             else "MEASURED", task)

    def test_published_example_is_valid(self):
        self.assertEqual(jp.validate_degraded(self.protocol["degraded"]["example"]), [])

    def test_blind_section_matches_code(self):
        blind = self.protocol["blind_packet"]
        self.assertEqual(blind["payload_whitelist"],
                         {k: list(v) for k, v in jp.PAYLOAD_WHITELIST.items()})
        self.assertEqual(blind["forbidden_keys"], list(jp.BLIND_FORBIDDEN_KEYS))

    def test_bindings_are_present(self):
        for name in ("routing_card", "capability_matrix", "baselines", "preregistration",
                     "r28_contract"):
            self.assertEqual(len(self.protocol["bindings"][name]["sha256"]), 64, name)

    def test_verification_checklist_matches(self):
        ids = [c["id"] for c in self.protocol["verification"]["checklist"]]
        self.assertEqual(ids, [c["id"] for c in jp.VERIFICATION_CHECKLIST])
        self.assertEqual(len(ids), 22)


class ReadOnlyDatasetTests(unittest.TestCase):

    def test_r26_15_is_byte_identical_to_the_t1_freeze(self):
        aggregate = jp.r26_15_tree_aggregate()
        self.assertEqual(aggregate["file_count"], jp.R26_15_EXPECTED_FILES)
        self.assertEqual(aggregate["total_bytes"], jp.R26_15_EXPECTED_BYTES)
        self.assertEqual(aggregate["aggregate_sha256"], jp.R26_15_EXPECTED_AGGREGATE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
