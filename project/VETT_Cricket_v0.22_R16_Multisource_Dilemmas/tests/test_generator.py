import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

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


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = load_canonical_roots(ROOTS_PATH, {"match_0003"})[0]

    def test_builds_separated_public_gold_and_evidence_artifacts(self) -> None:
        instance = build_instance(self.root, seed=16022)

        self.assertEqual("match_0003", instance.public["instance_id"])
        self.assertGreaterEqual(len(instance.public["documents"]), 6)
        self.assertEqual(16, len(instance.public["target_schema"]))
        self.assertEqual(16, len(instance.gold["targets"]))
        self.assertNotIn("claims", instance.public)
        self.assertIn("claims", instance.evidence)

        public_text = json.dumps(instance.public, ensure_ascii=False)
        for forbidden in ("gold_value", "decisive_support", "canonical_source_coordinate"):
            self.assertNotIn(forbidden, public_text)

    def test_gold_comes_from_canonical_root(self) -> None:
        instance = build_instance(self.root, seed=16022)
        gold = {target["target_id"]: target["value"] for target in instance.gold["targets"]}

        self.assertEqual(164, gold["I1.total_runs"])
        self.assertEqual(8, gold["I1.wickets"])
        self.assertEqual(165, gold["I2.total_runs"])
        self.assertEqual(6, gold["I2.wickets"])
        self.assertEqual("Ridgehaven", gold["match.winner"])
        self.assertEqual("Evan Clarke", gold["match.player_of_match"])

    def test_every_claim_references_a_real_hashed_public_span(self) -> None:
        instance = build_instance(self.root, seed=16022)
        spans = {
            (document["document_id"], span["span_id"]): span["text"]
            for document in instance.public["documents"]
            for span in document["spans"]
        }

        for claim in instance.evidence["claims"]:
            key = (claim["document_id"], claim["span_id"])
            self.assertIn(key, spans)
            expected = hashlib.sha256(spans[key].encode("utf-8")).hexdigest()
            self.assertEqual(expected, claim["span_sha256"])

    def test_instance_declares_every_required_difficulty_mechanism(self) -> None:
        instance = build_instance(self.root, seed=16022)
        required = {
            "stale_preliminary",
            "narrow_scope_correction",
            "syndicated_duplicate",
            "cross_innings_collision",
            "partial_correction",
            "invalidated_event",
            "position_trap",
            "derived_cricket_constraint",
        }

        self.assertEqual(required, set(instance.evidence["difficulty_mechanisms"]))

    def test_same_seed_is_byte_deterministic(self) -> None:
        first = build_instance(self.root, seed=16022)
        second = build_instance(self.root, seed=16022)

        self.assertEqual(first.to_json_bytes(), second.to_json_bytes())

    def test_public_language_avoids_template_artifacts(self) -> None:
        instance = build_instance(self.root, seed=16022)
        span_texts = [
            span["text"]
            for document in instance.public["documents"]
            for span in document["spans"]
        ]
        combined = " ".join(span_texts).lower()
        for artifact_pattern in (
            r"\bmatch match winner\b",
            r"\binnings innings total\b",
            r"\b1 no-balls\b",
            r"\b1 wides\b",
            r"\b1 byes\b",
            r"\b1 leg-byes\b",
            r"\bother fields are unchanged\b",
        ):
            self.assertIsNone(re.search(artifact_pattern, combined))

        prefixes = Counter(" ".join(text.lower().split()[:4]) for text in span_texts)
        most_common_prefix = prefixes.most_common(1)[0][1]
        self.assertLessEqual(most_common_prefix / len(span_texts), 0.15)
        self.assertGreaterEqual(
            sum(len(text) for text in span_texts) / len(span_texts), 55
        )


if __name__ == "__main__":
    unittest.main()
