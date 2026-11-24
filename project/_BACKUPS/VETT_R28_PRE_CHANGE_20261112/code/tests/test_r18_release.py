import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r18.release import PILOT_MATCH_IDS, audit_release, build_release


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


class R18ReleaseTests(unittest.TestCase):
    def test_release_blocks_known_shortcuts_and_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            first_summary = build_release(
                ROOTS_PATH, first, PILOT_MATCH_IDS, seed=18031
            )
            second_summary = build_release(
                ROOTS_PATH, second, PILOT_MATCH_IDS, seed=18031
            )

            self.assertEqual("PASS", first_summary["status"])
            self.assertEqual(first_summary, second_summary)
            self.assertEqual(directory_hashes(first), directory_hashes(second))
            self.assertGreaterEqual(
                first_summary["cross_instance_language"]["normalized_unique_ratio"],
                0.70,
            )
            self.assertLessEqual(
                first_summary["cross_instance_language"]["normalized_maximum_ratio"],
                0.08,
            )
            for shortcut in first_summary["public_shortcuts"].values():
                self.assertLessEqual(shortcut["accuracy"], 0.25)
            self.assertIn("single_span_amendment", first_summary["public_shortcuts"])
            self.assertIn("amendment_template_family", first_summary["public_shortcuts"])
            self.assertLessEqual(
                first_summary["decisive_support"]["maximum_document_share"],
                0.25,
            )
            self.assertEqual("PASS", audit_release(first)["status"])

            manifest_path = first / "MANIFEST.json"
            original_manifest = manifest_path.read_bytes()
            manifest = json.loads(original_manifest.decode("utf-8"))
            manifest["file_count_excluding_manifest"] += 1
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self.assertEqual("FAIL", audit_release(first)["manifest_status"])
            manifest_path.write_bytes(original_manifest)

            report_path = first / "RELEASE_REPORT.md"
            report_path.write_bytes(report_path.read_bytes() + b" ")
            tampered = audit_release(first)
            self.assertEqual("FAIL", tampered["status"])
            self.assertEqual("FAIL", tampered["manifest_status"])


if __name__ == "__main__":
    unittest.main()
