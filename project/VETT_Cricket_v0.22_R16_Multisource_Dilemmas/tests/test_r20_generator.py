import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r20.auditor import audit_instance
from vett_r20.evaluation import score_predictions
from vett_r20.generator import build_instance, resolve_from_evidence
from vett_r20.release import audit_release, build_release


PROJECT = Path(__file__).resolve().parents[1]
ROOTS = PROJECT / "repair_r20" / "canonical_roots_220_repaired.jsonl"


def load_roots() -> dict[str, dict]:
    return {
        root["root_id"]: root
        for root in (
            json.loads(line)
            for line in ROOTS.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def hashes(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in path.rglob("*")
        if item.is_file()
    }


class R20GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.roots = load_roots()
        cls.root = cls.roots["match_0001"]
        cls.bundle = build_instance(cls.root)

    def test_all_verified_cells_and_only_verified_cells_are_targets(self) -> None:
        expected = {
            cell["cell_id"]: str(cell["value"])
            for cell in self.root["cells"]
            if cell["gold_status"] == "R20_VERIFIED_SOURCE"
        }
        actual = {
            target["target_id"]: target["value"]
            for target in self.bundle.gold["targets"]
        }
        self.assertEqual(expected, actual)

    def test_oracle_recovers_every_direct_cell(self) -> None:
        expected = {
            target["target_id"]: target["value"]
            for target in self.bundle.gold["targets"]
        }
        self.assertEqual(expected, resolve_from_evidence(self.bundle.evidence))

    def test_instance_is_long_and_passes_all_gates(self) -> None:
        audit = audit_instance(
            self.bundle.public, self.bundle.gold, self.bundle.evidence
        )
        self.assertEqual("PASS", audit["status"], audit["errors"])
        self.assertGreater(audit["summary"]["words"], 5000)
        self.assertEqual({1, 2, 3}, set(audit["summary"]["revision_depths"]))

    def test_same_seed_is_deterministic(self) -> None:
        self.assertEqual(self.bundle, build_instance(self.root))

    def test_two_match_release_is_reproducible_and_auditable(self) -> None:
        selected = ["match_0001", "match_0162"]
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir) / "release"
            second = Path(second_dir) / "release"
            summary = build_release(ROOTS, first, selected_ids=selected)
            build_release(ROOTS, second, selected_ids=selected)
            self.assertEqual("PASS", summary["status"])
            self.assertEqual(hashes(first), hashes(second))
            self.assertEqual("PASS", audit_release(first)["status"])
            predictions = Path(first_dir) / "predictions.jsonl"
            records = []
            for match_id in selected:
                gold = json.loads(
                    (first / "private" / match_id / "private_gold.json").read_text(
                        encoding="utf-8"
                    )
                )
                records.append(
                    json.dumps(
                        {
                            "instance_id": match_id,
                            "predictions": {
                                target["target_id"]: target["value"]
                                for target in gold["targets"]
                            },
                        },
                        ensure_ascii=False,
                    )
                )
            predictions.write_text("\n".join(records) + "\n", encoding="utf-8")
            scores = score_predictions(first, predictions)
            self.assertEqual(1.0, scores["micro_cell_exact"]["accuracy"])
            self.assertEqual(1.0, scores["row_exact"]["accuracy"])
            self.assertEqual(1.0, scores["table_exact"]["accuracy"])
            self.assertEqual(1.0, scores["match_exact"]["accuracy"])


if __name__ == "__main__":
    unittest.main()
