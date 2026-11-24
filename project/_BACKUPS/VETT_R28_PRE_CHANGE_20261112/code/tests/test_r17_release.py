import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r17.release import audit_release, build_release


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


class R17ReleaseTests(unittest.TestCase):
    def test_two_match_release_is_complete_reproducible_and_tamper_evident(self) -> None:
        selected = ["match_0003", "match_0007"]
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            first_summary = build_release(ROOTS_PATH, first, selected, seed=17023)
            second_summary = build_release(ROOTS_PATH, second, selected, seed=17023)

            self.assertEqual("PASS", first_summary["status"])
            self.assertEqual(2, first_summary["instances"])
            self.assertFalse(first_summary["public_authority_ranking"])
            self.assertGreaterEqual(first_summary["edge_ablations"], 180)
            self.assertEqual(
                "PASS", first_summary["cross_instance_language"]["status"]
            )
            self.assertGreaterEqual(
                first_summary["cross_instance_language"]["unique_five_word_opening_ratio"],
                0.70,
            )
            self.assertLessEqual(
                first_summary["cross_instance_language"]["maximum_five_word_opening_ratio"],
                0.08,
            )
            self.assertEqual(first_summary, second_summary)
            self.assertEqual(directory_hashes(first), directory_hashes(second))
            for baseline in (
                "first_mention",
                "last_array_mention",
                "latest_timestamp",
                "majority_vote",
            ):
                self.assertLessEqual(first_summary["baselines"][baseline]["accuracy"], 0.25)

            for match_id in selected:
                public_path = first / "public" / match_id / "public_instance.json"
                self.assertTrue(public_path.is_file())
                public_text = public_path.read_text(encoding="utf-8")
                self.assertNotIn("source_priority", public_text)
                audit = json.loads(
                    (first / "audit" / f"{match_id}.audit.json").read_text(encoding="utf-8")
                )
                self.assertEqual("PASS", audit["status"])

            self.assertEqual("PASS", audit_release(first)["status"])
            report_path = first / "RELEASE_REPORT.md"
            report_path.write_bytes(report_path.read_bytes() + b" ")
            tampered = audit_release(first)
            self.assertEqual("FAIL", tampered["status"])
            self.assertEqual("FAIL", tampered["manifest_status"])


if __name__ == "__main__":
    unittest.main()
