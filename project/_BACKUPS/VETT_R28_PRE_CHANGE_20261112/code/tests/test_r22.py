import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from vett_r22.auditor import audit_instance
from vett_r22.evaluation import score_predictions
from vett_r22.generator import build_instance, resolve_probe
from vett_r22.release import audit_release, build_release
from vett_r22.spec import LEVELS, LEVEL_CONTRACTS, TARGET_FAMILIES


PROJECT = Path(__file__).resolve().parents[1]
ROOTS = PROJECT / "repair_r20" / "canonical_roots_220_repaired.jsonl"


def roots() -> dict[str, dict]:
    return {
        item["root_id"]: item
        for item in map(json.loads, ROOTS.read_text(encoding="utf-8").splitlines())
    }


def hashes(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in path.rglob("*") if item.is_file()
    }


class R22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = build_instance(roots()["match_0066"])

    def test_complete_matrix_and_no_difficulty_regression(self) -> None:
        probes = self.bundle.gold["probes"]
        self.assertEqual(25, len(probes))
        self.assertEqual(
            {(level, family) for level in LEVELS for family in TARGET_FAMILIES},
            {(probe["level"], probe["target_family"]) for probe in probes},
        )
        for probe in probes:
            complexity = probe["complexity"]
            baseline = probe["r21_baseline"]
            contract = LEVEL_CONTRACTS[probe["level"]]
            self.assertGreaterEqual(complexity["decisive_spans"], baseline["required_spans"])
            self.assertGreaterEqual(complexity["decisive_edges"], baseline["required_edges"])
            self.assertGreaterEqual(complexity["depth"], baseline["depth"])
            self.assertGreaterEqual(complexity["decisive_spans"], contract.min_decisive_spans)
            self.assertGreaterEqual(complexity["candidate_values"], contract.min_candidate_values)

    def test_oracle_and_counterfactual_audit_pass(self) -> None:
        audit = audit_instance(self.bundle.public, self.bundle.gold, self.bundle.evidence)
        self.assertEqual("PASS", audit["status"], audit["errors"])
        self.assertGreater(audit["summary"]["counterfactual_checks"], 200)
        for probe in self.bundle.gold["probes"]:
            claims = [claim for claim in self.bundle.evidence["probe_claims"] if claim["probe_id"] == probe["probe_id"]]
            self.assertEqual(probe["value"], resolve_probe(probe, claims))

    def test_release_is_deterministic_and_perfect_submission_scores_one(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            first, second = base / "first", base / "second"
            ids = ["match_0066", "match_0004"]
            summary = build_release(ROOTS, first, match_ids=ids, development_ids=ids)
            build_release(ROOTS, second, match_ids=ids, development_ids=ids)
            self.assertEqual("PASS", summary["status"])
            self.assertEqual(hashes(first), hashes(second))
            self.assertEqual("PASS", audit_release(first)["status"])
            lines = []
            for match_id in ids:
                gold = json.loads((first / "private" / match_id / "private_gold.json").read_text(encoding="utf-8"))
                lines.append(json.dumps({
                    "instance_id": match_id,
                    "table_predictions": [
                        {"target_id": target["target_id"], "value": target["value"]}
                        for target in gold["table_targets"]
                    ],
                    "probe_predictions": [
                        {
                            "probe_id": probe["probe_id"],
                            "value": probe["value"],
                            "decisive_spans": probe["decisive_evidence"]["spans"],
                            "decisive_edges": probe["decisive_evidence"]["edges"],
                            "provenance_spans": probe["provenance_context"]["spans"],
                            "provenance_edges": probe["provenance_context"]["edges"],
                            "confidence": 1.0,
                        }
                        for probe in gold["probes"]
                    ],
                }, ensure_ascii=False))
            predictions = base / "predictions.jsonl"
            predictions.write_text("\n".join(lines) + "\n", encoding="utf-8")
            score = score_predictions(first, predictions)
            self.assertEqual(1.0, score["table_cell_exact"]["accuracy"])
            self.assertEqual(1.0, score["fam"])
            self.assertEqual(1.0, score["asp_exact"]["accuracy"])
            self.assertEqual(1.0, score["decisive_span_micro"]["f1"])
            self.assertEqual(0.0, score["brier"])


if __name__ == "__main__":
    unittest.main()
