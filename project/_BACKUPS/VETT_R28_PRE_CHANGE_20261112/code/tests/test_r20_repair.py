import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r20.repair import DUPLICATE_OF, audit_repair_release, build_repair_release


WORKSPACE = Path(__file__).resolve().parents[2]
ARCHIVE = WORKSPACE / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903" / "workspace_snapshot"
ROOTS = ARCHIVE / "vett_cricket_pilot_v1" / "data" / "canonical_roots_217.jsonl"
RAW = WORKSPACE / "Self-cricket-clean_text_scorecard_v1_220_matches_extracted"
AUDIT = ARCHIVE / "cricket_220_audit_v1" / "results" / "per_match_audit.csv"
DETAILS = ARCHIVE / "cricket_220_audit_v1" / "results" / "check_details.csv"


def hashes(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in path.rglob("*")
        if item.is_file()
    }


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class R20RepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "repair"
        cls.summary = build_repair_release(ROOTS, RAW, AUDIT, DETAILS, cls.output)
        cls.roots = load_jsonl(cls.output / "canonical_roots_220_repaired.jsonl")
        cls.sources = load_jsonl(cls.output / "source_documents_220_repaired.jsonl")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_all_220_match_ids_are_present(self) -> None:
        expected = [f"match_{index:04d}" for index in range(1, 221)]
        self.assertEqual(expected, [root["root_id"] for root in self.roots])
        self.assertEqual(expected, [source["match_id"] for source in self.sources])
        self.assertEqual(217, self.summary["independent_roots"])
        self.assertEqual(3, self.summary["duplicate_controls"])

    def test_duplicate_controls_are_explicit(self) -> None:
        by_id = {root["root_id"]: root for root in self.roots}
        for duplicate_id, original_id in DUPLICATE_OF.items():
            self.assertEqual(original_id, by_id[duplicate_id]["r20_duplicate_of"])
            self.assertFalse(by_id[duplicate_id]["r20_repair"]["independent_root"])

    def test_failed_checks_mask_cells_without_guessing_values(self) -> None:
        for root in self.roots:
            for failure in root["r20_repair"]["source_failure_records"]:
                self.assertTrue(
                    any(
                        failure["check"] in cell["r20_conflict_checks"]
                        for cell in root["cells"]
                    ),
                    (root["root_id"], failure),
                )
            self.assertGreater(root["r20_repair"]["scored_verified_cells"], 0)

    def test_construction_leak_commentaries_are_sanitized(self) -> None:
        by_id = {source["match_id"]: source for source in self.sources}
        affected = (
            "match_0014",
            "match_0107",
            "match_0115",
            "match_0123",
            "match_0129",
            "match_0130",
            "match_0138",
            "match_0162",
            "match_0163",
            "match_0164",
        )
        for match_id in affected:
            self.assertTrue(by_id[match_id]["sanitization_edits"])
            lowered = by_id[match_id]["commentary"].lower()
            self.assertNotIn("scorecard fingerprint", lowered)
            self.assertNotIn("source game", lowered)
            self.assertNotIn("reconstructed scorecard", lowered)
            self.assertNotIn("reconstructed match", lowered)
            self.assertNotIn("rebuilt scorecard", lowered)

    def test_release_audit_passes(self) -> None:
        self.assertEqual("PASS", audit_repair_release(self.output)["status"])

    def test_build_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as second_dir:
            second = Path(second_dir) / "repair"
            second_summary = build_repair_release(ROOTS, RAW, AUDIT, DETAILS, second)
            self.assertEqual(self.summary, second_summary)
            self.assertEqual(hashes(self.output), hashes(second))


if __name__ == "__main__":
    unittest.main()
