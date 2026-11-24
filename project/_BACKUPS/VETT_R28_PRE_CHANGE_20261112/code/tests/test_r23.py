import json
import tempfile
import unittest
from pathlib import Path

from vett_r23.auditor import audit_release
from vett_r23.evaluation import score_predictions, write_oracle_predictions
from vett_r23.release import build_release


PROJECT = Path(__file__).resolve().parents[1]
BASE_RELEASE = PROJECT / "r22_pilot"


class R23Tests(unittest.TestCase):
    def test_text_embedded_release_is_reversible_and_oracle_scored(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = Path(temp_dir) / "embedded"
            summary = build_release(
                BASE_RELEASE,
                release,
                match_ids=["match_0066", "match_0004"],
                embed_rule_text=True,
            )
            self.assertEqual("PASS", summary["status"])
            self.assertEqual(18, summary["embedded_rule_spans"])
            self.assertEqual(10, summary["replaced_routing_spans"])
            self.assertEqual(8, summary["inserted_rule_spans"])
            self.assertEqual("PASS", audit_release(release)["status"])
            predictions = Path(temp_dir) / "oracle.jsonl"
            write_oracle_predictions(release, predictions, test_only=True)
            score = score_predictions(release, predictions)
            self.assertEqual(1.0, score["knowledge_joint_exact"]["accuracy"])
            self.assertEqual(1.0, score["knowledge_decisive_span_micro"]["f1"])
            self.assertEqual(1.0, score["knowledge_misleading_span_micro"]["f1"])
            replay = Path(temp_dir) / "embedded_replay"
            build_release(
                BASE_RELEASE,
                replay,
                match_ids=["match_0066", "match_0004"],
                embed_rule_text=True,
            )
            for match_id in ("match_0066", "match_0004"):
                for relative in ("public_instance.json",):
                    self.assertEqual(
                        (release / "public" / match_id / relative).read_bytes(),
                        (replay / "public" / match_id / relative).read_bytes(),
                    )
                for relative in ("private_gold.json", "private_evidence.json"):
                    self.assertEqual(
                        (release / "private" / match_id / relative).read_bytes(),
                        (replay / "private" / match_id / relative).read_bytes(),
                    )

    def test_release_audit_and_oracle_score(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            release = Path(temp_dir) / "release"
            ids = ["match_0066", "match_0004"]
            summary = build_release(BASE_RELEASE, release, match_ids=ids)
            self.assertEqual("PASS", summary["status"])
            self.assertEqual(10, summary["knowledge_questions"])
            self.assertEqual(10, summary["open_questions"])
            self.assertEqual("PASS", audit_release(release)["status"])
            records = []
            for match_id in ids:
                gold = json.loads(
                    (release / "private" / match_id / "private_gold.json").read_text(encoding="utf-8")
                )
                records.append(
                    {
                        "instance_id": match_id,
                        "knowledge_predictions": [
                            {
                                "question_id": item["question_id"],
                                "answer_code": item["answer_code"],
                                "reasoning_atoms": item["required_atoms"],
                                "explanation": "Oracle explanation.",
                                "confidence": 1.0,
                            }
                            for item in gold["knowledge_answers"]
                        ],
                        "open_qa_predictions": [
                            {
                                "question_id": item["question_id"],
                                "conclusion_value": item["conclusion_value"],
                                "reasoning_atoms": item["required_atoms"],
                                "decisive_spans": item["decisive_evidence"]["spans"],
                                "decisive_edges": item["decisive_evidence"]["edges"],
                                "provenance_spans": item["provenance_context"]["spans"],
                                "provenance_edges": item["provenance_context"]["edges"],
                                "explanation": "Oracle open explanation.",
                                "confidence": 1.0,
                            }
                            for item in gold["open_qa_answers"]
                        ],
                    }
                )
            predictions = Path(temp_dir) / "predictions.jsonl"
            predictions.write_text(
                "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in records),
                encoding="utf-8",
            )
            score = score_predictions(release, predictions)
            self.assertEqual(1.0, score["knowledge_answer_exact"]["accuracy"])
            self.assertEqual(1.0, score["knowledge_joint_exact"]["accuracy"])
            self.assertEqual(1.0, score["open_conclusion_exact"]["accuracy"])
            self.assertEqual(1.0, score["open_grounded_joint_exact"]["accuracy"])
            self.assertEqual(1.0, score["open_reasoning_atom_micro"]["f1"])


if __name__ == "__main__":
    unittest.main()
