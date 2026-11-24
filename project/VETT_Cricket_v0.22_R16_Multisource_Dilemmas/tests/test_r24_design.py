import unittest
from pathlib import Path

from vett_r24_design.validate import validate_blueprint


PROJECT = Path(__file__).resolve().parents[1]


class R24DesignTests(unittest.TestCase):
    def test_high_difficulty_blueprint_is_complete_and_balanced(self) -> None:
        result = validate_blueprint(PROJECT / "design" / "r24_high_difficulty_blueprint.json")
        self.assertEqual("PASS", result["status"], result["errors"])
        self.assertEqual(60, result["scenario_count"])
        self.assertEqual(12, result["cluster_count"])
        self.assertEqual({f"L{i}": 12 for i in range(1, 6)}, result["level_counts"])
        self.assertGreaterEqual(result["metric_count"], 9)


if __name__ == "__main__":
    unittest.main()
