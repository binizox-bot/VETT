import copy
import hashlib
import unittest
from pathlib import Path

from vett_r17.auditor import audit_instance
from vett_r17.generator import build_instance, load_canonical_roots


WORKSPACE = Path(__file__).resolve().parents[2]
ROOTS_PATH = (
    WORKSPACE
    / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903"
    / "workspace_snapshot"
    / "vett_cricket_pilot_v1"
    / "data"
    / "canonical_roots_217.jsonl"
)


class R17AuditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = load_canonical_roots(ROOTS_PATH, {"match_0003"})[0]
        cls.instance = build_instance(root, seed=17023)

    def test_clean_instance_passes_all_adversarial_gates(self) -> None:
        result = audit_instance(
            self.instance.public, self.instance.gold, self.instance.evidence
        )

        self.assertEqual("PASS", result["status"])
        self.assertEqual(14, result["summary"]["direct_targets"])
        self.assertEqual(2, result["summary"]["derived_targets"])
        self.assertEqual(14, len(result["counterfactuals"]))
        self.assertGreaterEqual(len(result["edge_ablations"]), 90)
        self.assertTrue(all(item["passed"] for item in result["edge_ablations"]))
        gates = {gate["name"]: gate for gate in result["gates"]}
        for required in (
            "public_policy_hidden",
            "opaque_identifiers",
            "edge_witness_visibility",
            "alternate_world_cricket_coherence",
            "unique_graph_resolution",
            "graph_edge_necessity",
            "decisive_span_counterfactual",
            "shortcut_resistance",
        ):
            self.assertTrue(gates[required]["passed"], required)
        for baseline in ("first_mention", "last_array_mention", "latest_timestamp", "majority_vote"):
            self.assertLessEqual(result["baselines"][baseline]["accuracy"], 0.25)

    def test_missing_literal_edge_witness_fails_even_when_hashes_are_updated(self) -> None:
        public = copy.deepcopy(self.instance.public)
        evidence = copy.deepcopy(self.instance.evidence)
        decisive_id = next(
            item["decisive_support"][0]
            for item in self.instance.gold["targets"]
            if item["target_id"] == "I1.total_runs"
        )
        claim = next(raw for raw in evidence["claims"] if raw["claim_id"] == decisive_id)
        token = claim["edge_witnesses"][0]["token"]
        document = next(
            item
            for item in public["documents"]
            if item["document_id"] == claim["document_id"]
        )
        span = next(item for item in document["spans"] if item["span_id"] == claim["span_id"])
        span["text"] = span["text"].replace(token, "revises an earlier docket")
        document["text"] = "\n".join(
            f"[{item['span_id']}] {item['text']}" for item in document["spans"]
        )
        new_hash = hashlib.sha256(span["text"].encode("utf-8")).hexdigest()
        for raw in evidence["claims"]:
            if raw["document_id"] == claim["document_id"] and raw["span_id"] == span["span_id"]:
                raw["span_sha256"] = new_hash

        result = audit_instance(public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("edge_witness_visibility", failed)

    def test_removed_final_amendment_edge_fails_unique_resolution(self) -> None:
        evidence = copy.deepcopy(self.instance.evidence)
        decisive_id = next(
            item["decisive_support"][0]
            for item in self.instance.gold["targets"]
            if item["target_id"] == "I1.total_runs"
        )
        claim = next(raw for raw in evidence["claims"] if raw["claim_id"] == decisive_id)
        claim["supersedes"] = []
        claim["edge_witnesses"] = []

        result = audit_instance(self.instance.public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("unique_graph_resolution", failed)

    def test_corrupt_alternate_world_fails_cricket_coherence(self) -> None:
        evidence = copy.deepcopy(self.instance.evidence)
        claim = next(
            raw
            for raw in evidence["claims"]
            if raw["innings"] == "I2"
            and raw["field"] == "total_extras"
            and raw["derived_from"]
        )
        claim["value"] += 1

        result = audit_instance(self.instance.public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("alternate_world_cricket_coherence", failed)

    def test_public_machine_policy_leak_fails(self) -> None:
        public = copy.deepcopy(self.instance.public)
        public["source_priority"] = {"sealed": 0}

        result = audit_instance(public, self.instance.gold, self.instance.evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("public_policy_hidden", failed)

    def test_role_bearing_identifier_fails_even_when_references_match(self) -> None:
        public = copy.deepcopy(self.instance.public)
        evidence = copy.deepcopy(self.instance.evidence)
        document = public["documents"][0]
        old_id = document["document_id"]
        document["document_id"] = "doc_final"
        for raw in evidence["claims"]:
            if raw["document_id"] == old_id:
                raw["document_id"] = "doc_final"

        result = audit_instance(public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("opaque_identifiers", failed)


if __name__ == "__main__":
    unittest.main()
