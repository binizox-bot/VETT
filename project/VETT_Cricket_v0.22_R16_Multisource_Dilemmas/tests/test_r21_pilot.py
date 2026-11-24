import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r21.auditor import audit_instance
from vett_r21.evaluation import score_predictions
from vett_r21.generator import build_instance, resolve
from vett_r21.release import audit_release, build_release


PROJECT = Path(__file__).resolve().parents[1]
ROOTS = PROJECT / "repair_r20" / "canonical_roots_220_repaired.jsonl"
SELECTION = PROJECT / "r21_pilot" / "SELECTION.json"


def roots() -> dict[str, dict]:
    return {root["root_id"]: root for root in map(json.loads, ROOTS.read_text(encoding="utf-8").splitlines())}


def hashes(path: Path) -> dict[str, str]:
    return {item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest() for item in path.rglob("*") if item.is_file()}


class R21PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = roots()["match_0066"]
        cls.bundle = build_instance(cls.root)

    def test_oracle_resolves_every_value_and_instance_passes(self) -> None:
        expected = {target["target_id"]: target["value"] for target in self.bundle.gold["targets"]}
        self.assertEqual(expected, resolve(self.bundle.evidence))
        audit = audit_instance(self.bundle.public, self.bundle.gold, self.bundle.evidence)
        self.assertEqual("PASS", audit["status"], audit["errors"])

    def test_public_documents_hide_literal_coordinates(self) -> None:
        text = "\n".join(document["text"] for document in self.bundle.public["documents"])
        for target in self.bundle.public["target_schema"]:
            self.assertNotIn(target["target_id"], text)
            self.assertNotIn(target["table_id"], text)

    def test_build_is_deterministic_and_perfect_evidence_scores_one(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            selection = json.loads(SELECTION.read_text(encoding="utf-8"))
            selection["match_ids"] = ["match_0066", "match_0004"]
            selection["count"] = 2
            selection_path = base / "selection.json"
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            first = base / "first"
            second = base / "second"
            summary = build_release(ROOTS, selection_path, first)
            build_release(ROOTS, selection_path, second)
            self.assertEqual("PASS", summary["status"])
            self.assertEqual(hashes(first), hashes(second))
            self.assertEqual("PASS", audit_release(first)["status"])
            predictions = base / "predictions.jsonl"
            lines = []
            for match_id in selection["match_ids"]:
                gold = json.loads((first / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
                lines.append(json.dumps({
                    "instance_id": match_id,
                    "predictions": [
                        {
                            "target_id": target["target_id"],
                            "value": target["value"],
                            "evidence_spans": target["required_evidence_spans"],
                            "evidence_edges": target["required_edges"],
                        }
                        for target in gold["targets"]
                    ],
                }, ensure_ascii=False))
            predictions.write_text("\n".join(lines) + "\n", encoding="utf-8")
            scores = score_predictions(first, predictions)
            self.assertEqual(1.0, scores["answer_cell_exact"]["accuracy"])
            self.assertEqual(1.0, scores["evidence_span_micro"]["f1"])
            self.assertEqual(1.0, scores["evidence_edge_micro"]["f1"])
            self.assertEqual(1.0, scores["joint_target_exact"]["accuracy"])


if __name__ == "__main__":
    unittest.main()
