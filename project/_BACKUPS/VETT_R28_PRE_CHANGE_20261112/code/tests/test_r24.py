import copy
import json
import unittest
from pathlib import Path

from vett_r24.auditor import audit_instance, audit_release
from vett_r24.evaluation import score_predictions
from vett_r24.generator import augment_instance
from vett_r24.knowledge import RULE_CARDS
from vett_r24.text_embedding import reconstruct_base_documents


PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT / "dataset_r22_220"
RELEASE = PROJECT / "dataset_r24_220"


def _base(match_id: str):
    return tuple(
        json.loads((BASE / folder / match_id / filename).read_text(encoding="utf-8"))
        for folder, filename in (
            ("public", "public_instance.json"),
            ("private", "private_gold.json"),
            ("private", "private_evidence.json"),
        )
    )


class R24Tests(unittest.TestCase):
    def test_rule_bank_and_deterministic_reversible_instance(self) -> None:
        self.assertEqual(60, len(RULE_CARDS))
        self.assertEqual({f"L{i}": 12 for i in range(1, 6)}, {
            level: sum(card["level"] == level for card in RULE_CARDS) for level in ("L1", "L2", "L3", "L4", "L5")
        })
        base = _base("match_0066")
        first = augment_instance(*base)
        second = augment_instance(*base)
        self.assertEqual(first.public, second.public)
        self.assertEqual("PASS", audit_instance(first.public, first.gold, first.evidence)["status"])
        self.assertEqual(base[0]["documents"], reconstruct_base_documents(first.public["documents"], first.evidence["r24_text_patches"]))

    def test_corruption_is_detected(self) -> None:
        bundle = augment_instance(*_base("match_0066"))
        damaged = copy.deepcopy(bundle.gold)
        damaged["table_targets"][0]["value"] = "CORRUPTED"
        result = audit_instance(bundle.public, damaged, bundle.evidence)
        self.assertEqual("FAIL", result["status"])
        self.assertTrue(any("table_targets_sha256" in error for error in result["errors"]))

    def test_full_release_and_oracle_score(self) -> None:
        audit = audit_release(RELEASE)
        self.assertEqual("PASS", audit["status"], audit["errors"])
        oracle = PROJECT / "tmp" / "r24_oracle_220.jsonl"
        score = score_predictions(RELEASE, oracle)
        self.assertEqual(1.0, score["fact_answer_macro_accuracy"])
        self.assertEqual(1.0, score["counterfactual_pair_consistency"])
        self.assertEqual(1.0, score["answer_reasoning_evidence_counterfactual_joint_exact"]["accuracy"])
        self.assertEqual(0.0, score["confidence_brier_score"])


if __name__ == "__main__":
    unittest.main()
