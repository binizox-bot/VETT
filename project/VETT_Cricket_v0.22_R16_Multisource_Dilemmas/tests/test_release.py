import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r16.release import audit_release, build_release


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


class ReleaseTests(unittest.TestCase):
    def test_two_match_release_is_complete_and_reproducible(self) -> None:
        selected = ["match_0003", "match_0007"]
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)

            first_summary = build_release(ROOTS_PATH, first, selected, seed=16022)
            second_summary = build_release(ROOTS_PATH, second, selected, seed=16022)

            self.assertEqual("PASS", first_summary["status"])
            self.assertEqual(2, first_summary["instances"])
            self.assertEqual(first_summary, second_summary)
            self.assertEqual(directory_hashes(first), directory_hashes(second))

            for match_id in selected:
                self.assertTrue((first / "public" / match_id / "public_instance.json").is_file())
                self.assertTrue((first / "private" / match_id / "private_gold.json").is_file())
                self.assertTrue((first / "private" / match_id / "private_evidence.json").is_file())
                audit_path = first / "audit" / f"{match_id}.audit.json"
                self.assertEqual("PASS", json.loads(audit_path.read_text(encoding="utf-8"))["status"])

            self.assertTrue((first / "MANIFEST.json").is_file())
            self.assertTrue((first / "RELEASE_REPORT.md").is_file())
            self.assertEqual("PASS", audit_release(first)["status"])

            public_path = first / "public" / selected[0] / "public_instance.json"
            public_path.write_bytes(public_path.read_bytes() + b" ")
            tampered = audit_release(first)
            self.assertEqual("FAIL", tampered["status"])
            self.assertEqual("FAIL", tampered["manifest_status"])
            self.assertTrue(tampered["manifest_errors"])


if __name__ == "__main__":
    unittest.main()
