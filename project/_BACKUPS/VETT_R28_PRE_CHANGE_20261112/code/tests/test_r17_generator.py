import hashlib
import json
import unittest
from pathlib import Path

from vett_r16.generator import load_canonical_roots
from vett_r17.generator import REQUIRED_MECHANISMS, build_instance
from vett_r17.model import Claim, Target
from vett_r17.resolver import resolve_target


WORKSPACE = Path(__file__).resolve().parents[2]
ROOTS_PATH = (
    WORKSPACE
    / "VETT_COMPLETE_RESEARCH_ARCHIVE_20260903"
    / "workspace_snapshot"
    / "vett_cricket_pilot_v1"
    / "data"
    / "canonical_roots_217.jsonl"
)


def claim_from_dict(raw: dict) -> Claim:
    return Claim(
        claim_id=raw["claim_id"],
        document_id=raw["document_id"],
        span_id=raw["span_id"],
        docket_id=raw["docket_id"],
        observed_at=raw["observed_at"],
        innings=raw.get("innings"),
        field=raw["field"],
        entity=raw.get("entity"),
        value=raw.get("value"),
        status=raw.get("status", "asserted"),
        supersedes=tuple(raw.get("supersedes", [])),
        invalidates=tuple(raw.get("invalidates", [])),
        derived_from=tuple(raw.get("derived_from", [])),
    )


class R17GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = load_canonical_roots(ROOTS_PATH, {"match_0003"})[0]
        cls.instance = build_instance(cls.root, seed=17023)

    def test_public_contract_hides_machine_trust_policy_and_graph(self) -> None:
        public = self.instance.public
        public_text = json.dumps(public, ensure_ascii=False, sort_keys=True)

        self.assertEqual("VETT-Cricket-v0.23-R17-pilot", public["dataset_version"])
        self.assertEqual(16, len(public["target_schema"]))
        self.assertGreaterEqual(len(public["documents"]), 10)
        for forbidden in (
            "source_priority",
            "authority_policy",
            "trust_tier",
            "supersedes",
            "invalidates",
            "derived_from",
            "gold_value",
            "decisive_support",
        ):
            self.assertNotIn(forbidden, public_text)

    def test_public_document_order_is_not_chronological(self) -> None:
        times = [
            int(document["published_at"].removeprefix("T+").removesuffix("m"))
            for document in self.instance.public["documents"]
        ]

        self.assertNotEqual(times, sorted(times))
        self.assertNotEqual(max(times), times[-1])

    def test_every_private_edge_has_a_literal_hashed_public_witness(self) -> None:
        spans = {
            (document["document_id"], span["span_id"]): span["text"]
            for document in self.instance.public["documents"]
            for span in document["spans"]
        }
        edge_count = 0
        for raw in self.instance.evidence["claims"]:
            key = (raw["document_id"], raw["span_id"])
            self.assertIn(key, spans)
            self.assertEqual(
                hashlib.sha256(spans[key].encode("utf-8")).hexdigest(),
                raw["span_sha256"],
            )
            references = (
                raw.get("supersedes", [])
                + raw.get("invalidates", [])
                + raw.get("derived_from", [])
            )
            witnesses = raw.get("edge_witnesses", [])
            self.assertEqual(len(references), len(witnesses))
            for witness in witnesses:
                edge_count += 1
                self.assertIn(witness["referenced_claim_id"], references)
                self.assertIn(witness["token"], spans[key])
        self.assertGreater(edge_count, 50)

    def test_reference_resolver_recovers_every_direct_gold(self) -> None:
        claims = [claim_from_dict(raw) for raw in self.instance.evidence["claims"]]
        gold = {item["target_id"]: item for item in self.instance.gold["targets"]}

        for raw_target in self.instance.public["target_schema"]:
            if "allowed_rule" in raw_target:
                continue
            target = Target(
                raw_target["target_id"],
                raw_target.get("innings"),
                raw_target["field"],
                raw_target.get("entity"),
            )
            result = resolve_target(claims, target)
            self.assertEqual("resolved", result.status, target.target_id)
            self.assertEqual(gold[target.target_id]["value"], result.value)
            self.assertEqual(
                tuple(gold[target.target_id]["decisive_support"]),
                result.decisive_claim_ids,
            )

    def test_declares_all_r17_mechanisms_and_two_wrong_worlds(self) -> None:
        self.assertEqual(
            set(REQUIRED_MECHANISMS),
            set(self.instance.evidence["difficulty_mechanisms"]),
        )
        self.assertEqual({"A", "B"}, set(self.instance.evidence["alternate_worlds"]))

    def test_same_seed_is_byte_deterministic(self) -> None:
        second = build_instance(self.root, seed=17023)
        self.assertEqual(self.instance.to_json_bytes(), second.to_json_bytes())

    def test_public_identifiers_do_not_reveal_document_roles(self) -> None:
        forbidden_role_tokens = (
            "final",
            "draft",
            "amend",
            "wire",
            "web",
            "radio",
            "archive",
            "void",
            "review",
            "live",
            "p0",
            "am1",
            "fin",
        )
        identifiers = [
            document["document_id"] for document in self.instance.public["documents"]
        ] + [raw["docket_id"] for raw in self.instance.evidence["claims"]]
        for identifier in identifiers:
            lowered = identifier.lower()
            self.assertFalse(
                any(token in lowered for token in forbidden_role_tokens), identifier
            )

    def test_identifier_and_opening_fingerprints_vary_across_matches(self) -> None:
        other_root = load_canonical_roots(ROOTS_PATH, {"match_0007"})[0]
        other = build_instance(other_root, seed=17023)
        first_ids = {item["document_id"] for item in self.instance.public["documents"]}
        second_ids = {item["document_id"] for item in other.public["documents"]}
        self.assertTrue(first_ids.isdisjoint(second_ids))

        def openings(bundle) -> set[str]:
            return {
                " ".join(span["text"].lower().split()[:5])
                for document in bundle.public["documents"]
                for span in document["spans"]
            }

        first_openings = openings(self.instance)
        second_openings = openings(other)
        overlap = len(first_openings & second_openings) / min(
            len(first_openings), len(second_openings)
        )
        self.assertLess(overlap, 0.35)


if __name__ == "__main__":
    unittest.main()
