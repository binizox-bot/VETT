import copy
import hashlib
import unittest
from pathlib import Path

from vett_r16.auditor import audit_instance
from vett_r16.generator import build_instance, load_canonical_roots


WORKSPACE = Path(__file__).resolve().parents[2]
ROOTS_PATH = (
    WORKSPACE
    / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903"
    / "workspace_snapshot"
    / "vett_cricket_pilot_v1"
    / "data"
    / "canonical_roots_217.jsonl"
)


class AuditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = load_canonical_roots(ROOTS_PATH, {"match_0003"})[0]
        cls.instance = build_instance(root, seed=16022)

    def test_clean_instance_passes_all_machine_gates(self) -> None:
        result = audit_instance(
            self.instance.public, self.instance.gold, self.instance.evidence
        )

        self.assertEqual("PASS", result["status"])
        self.assertTrue(all(gate["passed"] for gate in result["gates"]))
        self.assertEqual(14, result["summary"]["direct_targets"])
        self.assertEqual(2, result["summary"]["derived_targets"])
        self.assertEqual(14, len(result["counterfactuals"]))
        self.assertTrue(
            all(item["removed_span_ids"] for item in result["counterfactuals"])
        )
        self.assertIn(
            "document_naturalness_proxy",
            {gate["name"] for gate in result["gates"]},
        )
        self.assertIn(
            "alternate_world_cricket_coherence",
            {gate["name"] for gate in result["gates"]},
        )
        for name in ("first_mention", "last_mention", "majority_vote"):
            self.assertLessEqual(result["baselines"][name]["accuracy"], 0.25)

    def test_changed_public_span_fails_hash_gate(self) -> None:
        public = copy.deepcopy(self.instance.public)
        public["documents"][0]["spans"][0]["text"] += " altered"

        result = audit_instance(public, self.instance.gold, self.instance.evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("span_integrity", failed)

    def test_deleted_decisive_claim_fails_resolution_gate(self) -> None:
        evidence = copy.deepcopy(self.instance.evidence)
        decisive = self.instance.gold["targets"][0]["decisive_support"][0]
        evidence["claims"] = [
            claim for claim in evidence["claims"] if claim["claim_id"] != decisive
        ]

        result = audit_instance(self.instance.public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("unique_gold_resolution", failed)

    def test_public_gold_marker_fails_leakage_gate(self) -> None:
        public = copy.deepcopy(self.instance.public)
        public["debug"] = {"gold_value": 164}

        result = audit_instance(public, self.instance.gold, self.instance.evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("public_private_separation", failed)

    def test_repeated_machine_template_fails_language_proxy_gate(self) -> None:
        public = copy.deepcopy(self.instance.public)
        evidence = copy.deepcopy(self.instance.evidence)
        repeated = (
            "Automated update repeats the same template for every field while the "
            "underlying semantic claims remain otherwise unchanged."
        )
        for document in public["documents"]:
            for span in document["spans"]:
                span["text"] = repeated
            document["text"] = "\n".join(
                f"[{span['span_id']}] {span['text']}" for span in document["spans"]
            )
        repeated_hash = hashlib.sha256(repeated.encode("utf-8")).hexdigest()
        for claim in evidence["claims"]:
            claim["span_sha256"] = repeated_hash

        result = audit_instance(public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("document_naturalness_proxy", failed)

    def test_incoherent_distractor_extras_fail_cricket_gate(self) -> None:
        evidence = copy.deepcopy(self.instance.evidence)
        mutated = next(
            claim
            for claim in evidence["claims"]
            if claim["document_id"] == "doc_03"
            and claim["innings"] == "I1"
            and claim["field"] == "total_extras"
        )
        mutated["value"] += 1

        result = audit_instance(self.instance.public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("alternate_world_cricket_coherence", failed)


if __name__ == "__main__":
    unittest.main()
