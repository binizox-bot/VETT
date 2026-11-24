import unittest
from collections import Counter
from pathlib import Path

from vett_r19.auditor import audit_instance
from vett_r19.generator import build_instance, load_canonical_roots


WORKSPACE = Path(__file__).resolve().parents[2]
ROOTS_PATH = (
    WORKSPACE
    / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903"
    / "workspace_snapshot"
    / "vett_cricket_pilot_v1"
    / "data"
    / "canonical_roots_217.jsonl"
)


class R19GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = load_canonical_roots(ROOTS_PATH, {"match_0003"})[0]
        cls.instance = build_instance(cls.root, seed=19041)

    def test_each_direct_target_has_its_own_decisive_document(self) -> None:
        claims = {
            claim["claim_id"]: claim for claim in self.instance.evidence["claims"]
        }
        support_documents = [
            claims[target["decisive_support"][0]]["document_id"]
            for target in self.instance.gold["targets"]
            if target["decisive_support"]
        ]
        counts = Counter(support_documents)

        self.assertEqual(14, len(counts))
        self.assertEqual({1}, set(counts.values()))
        documents = {
            document["document_id"]: document
            for document in self.instance.public["documents"]
        }
        self.assertTrue(
            all(len(documents[document_id]["spans"]) >= 3 for document_id in counts)
        )

    def test_clean_fragmented_instance_passes_stricter_audit(self) -> None:
        result = audit_instance(
            self.instance.public, self.instance.gold, self.instance.evidence
        )

        self.assertEqual("PASS", result["status"])
        gate = next(
            gate
            for gate in result["gates"]
            if gate["name"] == "single_target_decisive_distribution"
        )
        self.assertTrue(gate["passed"])
        self.assertLessEqual(gate["details"]["maximum_share"], 0.10)

    def test_build_is_byte_deterministic(self) -> None:
        second = build_instance(self.root, seed=19041)

        self.assertEqual(self.instance.to_json_bytes(), second.to_json_bytes())


if __name__ == "__main__":
    unittest.main()
