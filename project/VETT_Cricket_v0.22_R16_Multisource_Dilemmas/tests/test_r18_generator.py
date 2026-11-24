import hashlib
import unittest
from collections import Counter
from pathlib import Path

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


class R18GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roots = load_canonical_roots(
            ROOTS_PATH,
            {"match_0003", "match_0007", "match_0009"},
        )
        cls.instances = [build_instance(root, seed=18031) for root in cls.roots]

    def test_decisive_targets_are_distributed_across_documents(self) -> None:
        for instance in self.instances:
            claims = {
                claim["claim_id"]: claim for claim in instance.evidence["claims"]
            }
            support_documents = [
                claims[target["decisive_support"][0]]["document_id"]
                for target in instance.gold["targets"]
                if target["decisive_support"]
            ]
            counts = Counter(support_documents)

            self.assertGreaterEqual(len(counts), 5)
            self.assertLessEqual(max(counts.values()) / len(support_documents), 0.25)
            documents = {
                document["document_id"]: document
                for document in instance.public["documents"]
            }
            self.assertTrue(
                all(len(documents[document_id]["spans"]) >= 3 for document_id in counts)
            )

    def test_old_public_metadata_shortcuts_are_absent(self) -> None:
        decisive_signatures = []
        for instance in self.instances:
            documents = {
                document["document_id"]: document
                for document in instance.public["documents"]
            }
            claims = {
                claim["claim_id"]: claim for claim in instance.evidence["claims"]
            }
            decisive_documents = {
                claims[target["decisive_support"][0]]["document_id"]
                for target in instance.gold["targets"]
                if target["decisive_support"]
            }
            signatures = {
                (documents[document_id]["genre"], documents[document_id]["published_at"])
                for document_id in decisive_documents
            }
            decisive_signatures.append(signatures)

            public_text = " ".join(
                document["genre"] + " " + document["text"]
                for document in instance.public["documents"]
            ).lower()
            self.assertNotIn("sealed scorer bulletin", public_text)
            self.assertNotIn("closes the ledger", public_text)
            self.assertFalse(
                any(
                    documents[document_id]["published_at"] == "T+32m"
                    for document_id in decisive_documents
                )
            )

        self.assertEqual(len(decisive_signatures), len({frozenset(x) for x in decisive_signatures}))

    def test_all_claim_hashes_follow_transformed_public_spans(self) -> None:
        for instance in self.instances:
            spans = {
                (document["document_id"], span["span_id"]): span["text"]
                for document in instance.public["documents"]
                for span in document["spans"]
            }
            for claim in instance.evidence["claims"]:
                text = spans[(claim["document_id"], claim["span_id"])]
                self.assertEqual(
                    hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    claim["span_sha256"],
                )

    def test_build_is_byte_deterministic(self) -> None:
        first = self.instances[0]
        second = build_instance(self.roots[0], seed=18031)

        self.assertEqual(first.to_json_bytes(), second.to_json_bytes())


if __name__ == "__main__":
    unittest.main()
