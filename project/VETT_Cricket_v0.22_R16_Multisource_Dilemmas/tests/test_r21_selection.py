import json
import tempfile
import unittest
from pathlib import Path

from vett_r21.selection import select_pilot


PROJECT = Path(__file__).resolve().parents[1]
ROOTS = PROJECT / "repair_r20" / "canonical_roots_220_repaired.jsonl"
R20 = PROJECT / "dataset_r20_220"


class R21SelectionTests(unittest.TestCase):
    def test_selection_is_deterministic_diverse_and_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            first = select_pilot(ROOTS, R20, Path(temp_dir) / "first.json")
            second = select_pilot(ROOTS, R20, Path(temp_dir) / "second.json")
        self.assertEqual(first, second)
        self.assertEqual(20, first["count"])
        self.assertEqual(20, len(set(first["match_ids"])))
        self.assertTrue(first["independent_roots_only"])
        self.assertIn("match_0004", first["match_ids"])
        self.assertIn("match_0066", first["match_ids"])
        self.assertEqual(10, first["coverage"]["masked_vs_clean"]["masked"])
        self.assertEqual(10, first["coverage"]["masked_vs_clean"]["clean"])
        self.assertIn("AUTO_PASS_NEEDS_SUPPORT_AUDIT", first["coverage"]["original_actions"])
        self.assertIn("REPAIR_SCORECARD", first["coverage"]["original_actions"])
        self.assertIn("REVIEW_BALL_ACCOUNTING", first["coverage"]["original_actions"])
        self.assertIn("REWRITE_INPUT_CONSTRUCTION_LEAK", first["coverage"]["original_actions"])


if __name__ == "__main__":
    unittest.main()
