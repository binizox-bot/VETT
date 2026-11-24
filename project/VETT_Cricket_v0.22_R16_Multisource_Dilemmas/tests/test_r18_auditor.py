import copy
import hashlib
import unittest
from pathlib import Path

from vett_r18.auditor import audit_instance
from vett_r18.generator import build_instance, load_canonical_roots


WORKSPACE = Path(__file__).resolve().parents[2]
ROOTS_PATH = (
    WORKSPACE
    / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903"
    / "workspace_snapshot"
    / "vett_cricket_pilot_v1"
    / "data"
    / "canonical_roots_217.jsonl"
)


class R18AuditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = load_canonical_roots(ROOTS_PATH, {"match_0003"})[0]
        cls.instance = build_instance(root, seed=18031)

    def test_claim_value_not_grounded_in_public_span_fails(self) -> None:
        evidence = copy.deepcopy(self.instance.evidence)
        invalidated_ids = {
            referenced
            for claim in evidence["claims"]
            for referenced in claim.get("invalidates", [])
        }
        claim = next(
            item
            for item in evidence["claims"]
            if item["claim_id"] in invalidated_ids
            and item["field"] == "player_of_match"
        )
        claim["value"] = "Ghost Player"

        result = audit_instance(self.instance.public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("claim_text_semantic_grounding", failed)

    def test_clean_r18_instance_passes_all_gates(self) -> None:
        result = audit_instance(
            self.instance.public, self.instance.gold, self.instance.evidence
        )

        self.assertEqual("PASS", result["status"])
        gates = {gate["name"]: gate for gate in result["gates"]}
        self.assertTrue(gates["claim_text_semantic_grounding"]["passed"])
        self.assertTrue(gates["affirmative_edge_semantics"]["passed"])
        self.assertTrue(gates["decisive_support_distribution"]["passed"])

    def test_edge_token_inside_negated_quotation_fails(self) -> None:
        public = copy.deepcopy(self.instance.public)
        evidence = copy.deepcopy(self.instance.evidence)
        decisive_id = next(
            target["decisive_support"][0]
            for target in self.instance.gold["targets"]
            if target["target_id"] == "match.winner"
        )
        claim = next(item for item in evidence["claims"] if item["claim_id"] == decisive_id)
        token = claim["edge_witnesses"][0]["token"]
        document = next(
            item
            for item in public["documents"]
            if item["document_id"] == claim["document_id"]
        )
        span = next(
            item for item in document["spans"] if item["span_id"] == claim["span_id"]
        )
        old_text = span["text"]
        span["text"] = old_text.replace(
            token,
            f"rejects the quoted phrase '{token}' and does not alter that docket",
        )
        document["text"] = document["text"].replace(old_text, span["text"])
        new_hash = hashlib.sha256(span["text"].encode("utf-8")).hexdigest()
        for item in evidence["claims"]:
            if (
                item["document_id"] == claim["document_id"]
                and item["span_id"] == claim["span_id"]
            ):
                item["span_sha256"] = new_hash

        result = audit_instance(public, self.instance.gold, evidence)

        self.assertEqual("FAIL", result["status"])
        failed = {gate["name"] for gate in result["gates"] if not gate["passed"]}
        self.assertIn("affirmative_edge_semantics", failed)


if __name__ == "__main__":
    unittest.main()
