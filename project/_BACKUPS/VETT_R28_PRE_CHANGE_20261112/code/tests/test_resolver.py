import unittest

from vett_r16.model import AuthorityPolicy, Claim, Target
from vett_r16.resolver import resolve_target


class ResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = AuthorityPolicy(
            source_priority={
                "official_scorer": 0,
                "broadcast": 1,
                "reporter": 2,
                "syndication": 3,
            }
        )

    def test_higher_authority_beats_first_last_and_majority(self) -> None:
        target = Target("I1.total", innings="I1", field="total_runs")
        claims = [
            Claim("c1", "d1", "s1", "reporter", 10, "I1", "total_runs", None, 164),
            Claim("c2", "d2", "s2", "syndication", 20, "I1", "total_runs", None, 163),
            Claim("c3", "d3", "s3", "syndication", 30, "I1", "total_runs", None, 163),
            Claim("c4", "d4", "s4", "official_scorer", 40, "I1", "total_runs", None, 164),
            Claim("c5", "d5", "s5", "reporter", 50, "I1", "total_runs", None, 165),
        ]

        resolution = resolve_target(claims, target, self.policy)

        self.assertEqual("resolved", resolution.status)
        self.assertEqual(164, resolution.value)
        self.assertEqual(("c4",), resolution.decisive_claim_ids)

    def test_scope_filter_prevents_cross_innings_collision(self) -> None:
        target = Target("I2.extras", innings="I2", field="total_extras")
        claims = [
            Claim("i1", "d1", "s1", "official_scorer", 10, "I1", "total_extras", None, 12),
            Claim("i2", "d2", "s2", "broadcast", 20, "I2", "total_extras", None, 7),
        ]

        resolution = resolve_target(claims, target, self.policy)

        self.assertEqual("resolved", resolution.status)
        self.assertEqual(7, resolution.value)
        self.assertEqual(("i2",), resolution.decisive_claim_ids)

    def test_explicit_supersession_replaces_same_source_value(self) -> None:
        target = Target("I1.wides", innings="I1", field="wides")
        claims = [
            Claim("old", "d1", "s1", "official_scorer", 10, "I1", "wides", None, 8),
            Claim(
                "new",
                "d1",
                "s2",
                "official_scorer",
                20,
                "I1",
                "wides",
                None,
                9,
                supersedes=("old",),
            ),
        ]

        resolution = resolve_target(claims, target, self.policy)

        self.assertEqual("resolved", resolution.status)
        self.assertEqual(9, resolution.value)
        self.assertEqual(("new",), resolution.decisive_claim_ids)

    def test_retraction_invalidates_phantom_event(self) -> None:
        target = Target("I2.wickets", innings="I2", field="wickets")
        claims = [
            Claim("phantom", "d1", "s1", "broadcast", 10, "I2", "wickets", None, 7),
            Claim(
                "retract",
                "d2",
                "s2",
                "broadcast",
                20,
                "I2",
                "wickets",
                None,
                None,
                status="retraction",
                invalidates=("phantom",),
            ),
            Claim("official", "d3", "s3", "official_scorer", 30, "I2", "wickets", None, 6),
        ]

        resolution = resolve_target(claims, target, self.policy)

        self.assertEqual("resolved", resolution.status)
        self.assertEqual(6, resolution.value)
        self.assertIn("phantom", resolution.inactive_claim_ids)

    def test_equal_authority_conflict_without_edge_fails_closed(self) -> None:
        target = Target("I1.total", innings="I1", field="total_runs")
        claims = [
            Claim("a", "d1", "s1", "official_scorer", 10, "I1", "total_runs", None, 164),
            Claim("b", "d2", "s2", "official_scorer", 20, "I1", "total_runs", None, 165),
        ]

        resolution = resolve_target(claims, target, self.policy)

        self.assertEqual("ambiguous", resolution.status)
        self.assertIsNone(resolution.value)
        self.assertEqual(("a", "b"), resolution.decisive_claim_ids)


if __name__ == "__main__":
    unittest.main()
