import inspect
import unittest

from vett_r17.model import Claim, Target
from vett_r17.resolver import resolve_target


def claim(
    claim_id: str,
    value: int | None,
    *,
    innings: str = "I1",
    status: str = "asserted",
    supersedes: tuple[str, ...] = (),
    invalidates: tuple[str, ...] = (),
    derived_from: tuple[str, ...] = (),
) -> Claim:
    return Claim(
        claim_id=claim_id,
        document_id=f"doc_{claim_id}",
        span_id=f"doc_{claim_id}.s001",
        docket_id=f"DKT-{claim_id}",
        observed_at=len(claim_id),
        innings=innings,
        field="total_runs",
        entity=None,
        value=value,
        status=status,
        supersedes=supersedes,
        invalidates=invalidates,
        derived_from=derived_from,
    )


class R17ResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = Target("I1.total_runs", "I1", "total_runs")

    def test_api_has_no_authority_policy_parameter(self) -> None:
        self.assertEqual(["claims", "target"], list(inspect.signature(resolve_target).parameters))

    def test_correction_of_correction_leaves_only_final_value(self) -> None:
        claims = [
            claim("prelim", 163),
            claim("amendment_a", 164, supersedes=("prelim",)),
            claim("amendment_b", 165, supersedes=("amendment_a",)),
        ]

        result = resolve_target(claims, self.target)

        self.assertEqual("resolved", result.status)
        self.assertEqual(165, result.value)
        self.assertEqual(("amendment_b",), result.decisive_claim_ids)
        self.assertEqual({"prelim", "amendment_a"}, set(result.inactive_claim_ids))

    def test_staleness_cascades_through_multi_hop_copy_lineage(self) -> None:
        claims = [
            claim("prelim", 163),
            claim("wire", 163, derived_from=("prelim",)),
            claim("web", 163, derived_from=("wire",)),
            claim("final", 165, supersedes=("prelim",)),
        ]

        result = resolve_target(claims, self.target)

        self.assertEqual("resolved", result.status)
        self.assertEqual(165, result.value)
        self.assertEqual({"prelim", "wire", "web"}, set(result.inactive_claim_ids))

    def test_conflicting_active_values_fail_closed(self) -> None:
        result = resolve_target(
            [claim("left", 164), claim("right", 165)], self.target
        )

        self.assertEqual("ambiguous", result.status)
        self.assertIsNone(result.value)

    def test_reference_outside_exact_scope_is_rejected(self) -> None:
        claims = [
            claim("first", 164, innings="I1"),
            claim("second", 165, innings="I2", supersedes=("first",)),
        ]

        with self.assertRaisesRegex(ValueError, "outside its target scope"):
            resolve_target(claims, Target("I2.total_runs", "I2", "total_runs"))

    def test_lineage_cycle_is_rejected(self) -> None:
        claims = [
            claim("left", 164, derived_from=("right",)),
            claim("right", 164, derived_from=("left",)),
        ]

        with self.assertRaisesRegex(ValueError, "cycle"):
            resolve_target(claims, self.target)

    def test_retraction_removes_event_claim_without_source_ranking(self) -> None:
        claims = [
            claim("phantom", 166),
            claim(
                "withdrawal",
                None,
                status="retraction",
                invalidates=("phantom",),
            ),
            claim("settled", 165),
        ]

        result = resolve_target(claims, self.target)

        self.assertEqual("resolved", result.status)
        self.assertEqual(165, result.value)


if __name__ == "__main__":
    unittest.main()
