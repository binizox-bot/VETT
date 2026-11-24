import hashlib
import tempfile
import unittest
from pathlib import Path

from vett_r19.release import PILOT_MATCH_IDS, audit_release, build_release


WORKSPACE = Path(__file__).resolve().parents[2]
ROOTS_PATH = (
    WORKSPACE
    / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903"
    / "workspace_snapshot"
    / "vett_cricket_pilot_v1"
    / "data"
    / "canonical_roots_217.jsonl"
)


def directory_hashes(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


class R19ReleaseTests(unittest.TestCase):
    def test_latest_amendment_shortcuts_are_below_ten_percent(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            first_summary = build_release(
                ROOTS_PATH, first, PILOT_MATCH_IDS, seed=19041
            )
            second_summary = build_release(
                ROOTS_PATH, second, PILOT_MATCH_IDS, seed=19041
            )

            self.assertEqual("PASS", first_summary["status"])
            self.assertEqual(first_summary, second_summary)
            self.assertEqual(directory_hashes(first), directory_hashes(second))
            self.assertLessEqual(
                first_summary["public_shortcuts"]["latest_amendment"]["accuracy"],
                0.10,
            )
            self.assertLessEqual(
                first_summary["public_shortcuts"]["latest_amendment_per_target"][
                    "accuracy"
                ],
                0.10,
            )
            for rank in range(1, 17):
                self.assertLessEqual(
                    first_summary["public_shortcuts"][
                        f"amendment_rank_{rank:02d}"
                    ]["accuracy"],
                    0.10,
                )
            self.assertEqual(
                14,
                min(first_summary["decisive_support"]["document_counts"].values()),
            )
            self.assertLessEqual(
                first_summary["decisive_support"]["maximum_document_share"],
                0.10,
            )
            self.assertGreaterEqual(
                first_summary["cross_instance_language"]["normalized_unique_ratio"],
                0.70,
            )
            self.assertEqual("PASS", audit_release(first)["status"])


if __name__ == "__main__":
    unittest.main()
