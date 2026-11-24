"""Stratified targeted enumeration of the reachable decision-record space.

The contract forbids random sampling of fact domains (20,000 random draws yield
only 156 distinct records and 74% dismissal=NONE).  Instead we enumerate, per
``(delivery_status, dismissal)`` route, a running/boundary/penalty grid, solve
every fact set with the frozen solver, and keep **distinct 12-field records**.
Records are then grouped into the 67 contract strata
``(delivery_status, dismissal, BYE/LEG_BYE/PENALTY non-zero mask)``.

Two grids are enumerated:

``canonical``
    The grid frozen by the t4 contract probe (``02_contract/scripts/
    probe_record_space.py``).  Re-enumerating it here is a cross-check: an
    independent implementation must reproduce the contract's per-layer
    ``reachable_cap`` and the global lower bound of 761 distinct records.
``extended``
    A wider grid (more completed-run values, an extra boundary allowance and
    explicit per-fact ``forced_not_count``).  It can only add records, and is
    used as headroom for held-out selection and for the safety margin.

Selection always prefers ``canonical`` records (sorted by record sha256) and only
falls back to ``extended`` headroom when a layer's canonical records are used up.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from .canonical import canon, sha256_text
from .constants import LEDGER_FIELDS, MASK_FIELDS
from .solver_bridge import solve_flat

# ---------------------------------------------------------------------------
# Fact grid (frozen in the build config; cricket-legal values only)
# ---------------------------------------------------------------------------
FACT_GRID: dict[str, list[Any]] = {
    "no_ball_called": [False, True],
    "wide_called": [False, True],
    "early_dead_reball": [False, True],
    "contact": ["NONE", "BAT", "PERSON"],
    "completed_runs": [0, 1, 2, 3, 4, 5, 6],
    "crossed_at_throw": [False, True],
    "boundary_mode": ["NONE", "NORMAL", "OVERTHROW", "LATER_AFTER_WICKET"],
    "boundary_allowance": [0, 1, 4, 6],
    "dismissal_candidate": [
        "NONE", "BOWLED", "LBW", "CAUGHT", "RUN_OUT", "STUMPED_OR_RUN_OUT",
    ],
    "appeal_made": [False, True],
    "appeal_in_time": [False, True],
    "wicket_fair": [False, True],
    "wicket_broken_by_delivery": [False, True],
    "lbw_pitch_valid": [False, True],
    "lbw_impact_valid": [False, True],
    "lbw_would_hit_wicket": [False, True],
    "out_of_ground": [False, True],
    "dead_before_wicket": [False, True],
    "attempting_run": [False, True],
    "keeper_only": [False, True],
    "catch_complete": [False, True],
    "ball_grounded_before_control": [False, True],
    "boundary_contact_before_completion": [False, True],
    "wilful_deception": [False, True],
    "penalty_runs_batting": [0, 1, 2, 3, 4, 5],
    "award_run_in_progress": [False, True],
    "forced_not_count": [False, True],
}

# (boundary_mode, boundary_allowance, crossed_at_throw) triples per profile.
_BOUNDARY_CANONICAL: tuple[tuple[str, int, bool], ...] = (
    ("NONE", 0, False),
    ("NORMAL", 4, False),
    ("NORMAL", 6, False),
    ("OVERTHROW", 4, False),
    ("OVERTHROW", 4, True),
    ("OVERTHROW", 6, False),
    ("OVERTHROW", 6, True),
    ("LATER_AFTER_WICKET", 4, False),
    ("LATER_AFTER_WICKET", 6, False),
)
_BOUNDARY_EXTENDED: tuple[tuple[str, int, bool], ...] = _BOUNDARY_CANONICAL + (
    ("NORMAL", 1, False),
    ("OVERTHROW", 1, False),
    ("LATER_AFTER_WICKET", 1, False),
)

PROFILES: dict[str, dict[str, Any]] = {
    "canonical": {
        "completed_runs": (0, 1, 2, 3),
        "boundary": _BOUNDARY_CANONICAL,
        "penalties": (0, 5),
        "forced_not_count": (False,),
        "wilful_all_routes": True,
    },
    "extended": {
        "completed_runs": (0, 1, 2, 3, 4, 5, 6),
        "boundary": _BOUNDARY_EXTENDED,
        "penalties": (0, 1, 2, 3, 4, 5),
        "forced_not_count": (False, True),
        "wilful_all_routes": False,
    },
}


def status_facts(status: str) -> dict[str, Any]:
    """Minimal fact skeleton that drives the solver to ``status``."""

    if status == "LEGAL":
        return {}
    if status == "NO_BALL":
        return {"no_ball_called": True}
    if status == "WIDE":
        return {"wide_called": True, "contact": "NONE"}
    if status == "DEAD_REBALL":
        return {"early_dead_reball": True}
    raise KeyError(status)


def dismissal_facts(dismissal: str) -> dict[str, Any]:
    """Fact skeleton for the dismissal route (gates at their passing values)."""

    gates = {"appeal_made": True, "appeal_in_time": True, "wicket_fair": True}
    if dismissal == "NONE":
        return {"dismissal_candidate": "NONE", **gates}
    if dismissal == "BOWLED":
        return {"dismissal_candidate": "BOWLED", "wicket_broken_by_delivery": True, **gates}
    if dismissal == "LBW":
        return {
            "dismissal_candidate": "LBW",
            "lbw_pitch_valid": True,
            "lbw_impact_valid": True,
            "lbw_would_hit_wicket": True,
            **gates,
        }
    if dismissal == "CAUGHT":
        return {
            "dismissal_candidate": "CAUGHT",
            "contact": "BAT",
            "catch_complete": True,
            "ball_grounded_before_control": False,
            "boundary_contact_before_completion": False,
            **gates,
        }
    if dismissal == "RUN_OUT":
        return {"dismissal_candidate": "RUN_OUT", "out_of_ground": True, **gates}
    if dismissal == "STUMPED":
        return {
            "dismissal_candidate": "STUMPED_OR_RUN_OUT",
            "out_of_ground": True,
            "keeper_only": True,
            "attempting_run": False,
            **gates,
        }
    if dismissal == "OBSTRUCTING_FIELD":
        return {"dismissal_candidate": "OBSTRUCTING_FIELD", "appeal_made": True}
    if dismissal == "HIT_BALL_TWICE":
        return {"dismissal_candidate": "HIT_BALL_TWICE", "appeal_made": True}
    raise KeyError(dismissal)


# (status, dismissal) routes worth enumerating: routes that collapse structurally
# to a NONE dismissal (BOWLED/LBW/CAUGHT under a non-legal delivery) are skipped
# because they add no record shape the NONE route does not already produce.
ROUTE_PAIRS: tuple[tuple[str, str], ...] = (
    ("LEGAL", "NONE"),
    ("LEGAL", "RUN_OUT"),
    ("LEGAL", "OBSTRUCTING_FIELD"),
    ("LEGAL", "HIT_BALL_TWICE"),
    ("LEGAL", "BOWLED"),
    ("LEGAL", "LBW"),
    ("LEGAL", "CAUGHT"),
    ("LEGAL", "STUMPED"),
    ("NO_BALL", "NONE"),
    ("NO_BALL", "RUN_OUT"),
    ("NO_BALL", "OBSTRUCTING_FIELD"),
    ("NO_BALL", "HIT_BALL_TWICE"),
    ("NO_BALL", "STUMPED"),
    ("WIDE", "NONE"),
    ("WIDE", "RUN_OUT"),
    ("WIDE", "OBSTRUCTING_FIELD"),
    ("WIDE", "HIT_BALL_TWICE"),
    ("WIDE", "STUMPED"),
    ("DEAD_REBALL", "NONE"),
)


def _contacts_for(status: str, route: dict[str, Any]) -> tuple[str, ...]:
    if "contact" in route:
        return (str(route["contact"]),)
    if status == "WIDE":
        return ("NONE",)
    return ("NONE", "BAT", "PERSON")


def layer_mask(flat: dict[str, Any]) -> str:
    return "".join("1" if int(flat.get(field, 0)) != 0 else "0" for field in MASK_FIELDS)


def layer_key(flat: dict[str, Any]) -> tuple[str, str, str]:
    return (str(flat["delivery_status"]), str(flat["dismissal"]), layer_mask(flat))


def iter_route_facts(status: str, dismissal: str, profile: str = "extended") -> Iterator[dict[str, Any]]:
    """Deterministic enumeration of fact sets for one (status, dismissal) route."""

    spec = PROFILES[profile]
    route = {**status_facts(status), **dismissal_facts(dismissal)}
    if route.get("early_dead_reball") and dismissal != "NONE":
        return
    contacts = _contacts_for(status, route)
    for contact in contacts:
        for completed in spec["completed_runs"]:
            for mode, allowance, crossed in spec["boundary"]:
                for award in (False, True):
                    for penalty in spec["penalties"]:
                        for forced in spec["forced_not_count"]:
                            wilful_options = (
                                (False, True)
                                if (dismissal == "NONE" or spec["wilful_all_routes"])
                                else (False,)
                            )
                            for wilful in wilful_options:
                                facts: dict[str, Any] = dict(route)
                                facts.setdefault("contact", contact)
                                facts["completed_runs"] = completed
                                facts["boundary_mode"] = mode
                                facts["boundary_allowance"] = allowance
                                facts["crossed_at_throw"] = crossed if mode == "OVERTHROW" else False
                                facts["award_run_in_progress"] = award
                                facts["penalty_runs_batting"] = penalty
                                facts["wilful_deception"] = wilful
                                if profile == "extended":
                                    facts["forced_not_count"] = forced
                                facts.setdefault("appeal_made", True)
                                facts.setdefault("appeal_in_time", True)
                                facts.setdefault("wicket_fair", True)
                                yield facts


def required_combination_facts() -> list[dict[str, Any]]:
    """The five fact combinations the R26.15 data never contained (contract 7.2).

    The numeric parameters are chosen so that the five records are pairwise
    distinct (HA1 requires 320/320 distinct records, so no two required
    combinations may land on the same record).
    """

    gates = {"appeal_made": True, "appeal_in_time": True, "wicket_fair": True}
    base = {
        "contact": "BAT",
        "completed_runs": 0,
        "boundary_mode": "NONE",
        "boundary_allowance": 0,
        "crossed_at_throw": False,
        "award_run_in_progress": False,
        "penalty_runs_batting": 0,
        "wilful_deception": False,
        "forced_not_count": False,
    }
    return [
        {
            "name": "appeal_made_false_with_lbw",
            "facts": {
                **base,
                "dismissal_candidate": "LBW",
                "appeal_made": False,
                "appeal_in_time": True,
                "wicket_fair": True,
                "lbw_pitch_valid": True,
                "lbw_impact_valid": True,
                "lbw_would_hit_wicket": True,
                "completed_runs": 2,
            },
        },
        {
            "name": "appeal_in_time_false_with_caught",
            "facts": {
                **base,
                "dismissal_candidate": "CAUGHT",
                "appeal_made": True,
                "appeal_in_time": False,
                "wicket_fair": True,
                "catch_complete": True,
                "ball_grounded_before_control": False,
                "boundary_contact_before_completion": False,
                "completed_runs": 3,
            },
        },
        {
            "name": "contact_person_with_wide_called",
            "facts": {
                **base,
                "wide_called": True,
                "contact": "PERSON",
                "dismissal_candidate": "NONE",
                **gates,
                "completed_runs": 2,
            },
        },
        {
            "name": "dead_before_wicket_with_run_out",
            "facts": {
                **base,
                "dismissal_candidate": "RUN_OUT",
                **gates,
                "dead_before_wicket": True,
                "out_of_ground": True,
                "contact": "NONE",
                "completed_runs": 2,
            },
        },
        {
            "name": "penalty_five_with_overthrow",
            "facts": {
                **base,
                "dismissal_candidate": "NONE",
                **gates,
                "contact": "BAT",
                "completed_runs": 1,
                "boundary_mode": "OVERTHROW",
                "boundary_allowance": 4,
                "crossed_at_throw": True,
                "penalty_runs_batting": 5,
            },
        },
    ]


@dataclass(frozen=True)
class Candidate:
    """One reachable distinct record with a representative fact set."""

    record_sha256: str
    facts_sha256: str
    facts: dict[str, Any]
    flat: dict[str, Any]
    status: str
    dismissal: str
    mask: str
    profile: str = "extended"

    @property
    def layer(self) -> tuple[str, str, str]:
        return (self.status, self.dismissal, self.mask)

    def summary(self) -> dict[str, Any]:
        return {
            "record_sha256": self.record_sha256,
            "facts_sha256": self.facts_sha256,
            "record": self.flat,
            "profile": self.profile,
        }


def make_candidate(facts: dict[str, Any], *, profile: str = "extended") -> Candidate:
    _, flat, record_sha = solve_flat(facts)
    status, dismissal, mask = layer_key(flat)
    return Candidate(
        record_sha256=record_sha,
        facts_sha256=sha256_text(canon(facts)),
        facts=dict(facts),
        flat=dict(flat),
        status=status,
        dismissal=dismissal,
        mask=mask,
        profile=profile,
    )


def enumerate_layers(profile: str = "canonical") -> dict[tuple[str, str, str], list[Candidate]]:
    """Enumerate all routes for one profile; return per-layer distinct records."""

    best: dict[str, Candidate] = {}
    for status, dismissal in ROUTE_PAIRS:
        for facts in iter_route_facts(status, dismissal, profile):
            try:
                candidate = make_candidate(facts, profile=profile)
            except Exception:  # noqa: BLE001 - structurally impossible combinations
                continue
            previous = best.get(candidate.record_sha256)
            if previous is None or candidate.facts_sha256 < previous.facts_sha256:
                best[candidate.record_sha256] = candidate
    layers: dict[tuple[str, str, str], list[Candidate]] = {}
    for candidate in best.values():
        layers.setdefault(candidate.layer, []).append(candidate)
    for bucket in layers.values():
        bucket.sort(key=lambda item: item.record_sha256)
    return dict(sorted(layers.items()))


def enumerate_combined() -> dict[tuple[str, str, str], list[Candidate]]:
    """Canonical records first (sorted by sha), then extra extended headroom."""

    combined: dict[tuple[str, str, str], list[Candidate]] = {}
    canonical = enumerate_layers("canonical")
    extended = enumerate_layers("extended")
    for layer in sorted(set(canonical) | set(extended)):
        seen = {candidate.record_sha256 for candidate in canonical.get(layer, [])}
        bucket = list(canonical.get(layer, []))
        for candidate in extended.get(layer, []):
            if candidate.record_sha256 not in seen:
                bucket.append(candidate)
                seen.add(candidate.record_sha256)
        combined[layer] = bucket
    return combined


def required_candidates() -> list[dict[str, Any]]:
    """Resolve the five never-coexisting combinations into reachable records."""

    rows: list[dict[str, Any]] = []
    for item in required_combination_facts():
        candidate = make_candidate(item["facts"], profile="required")
        rows.append({
            "combination": item["name"],
            "facts": item["facts"],
            "facts_sha256": candidate.facts_sha256,
            "record": candidate.flat,
            "record_sha256": candidate.record_sha256,
            "layer": {
                "delivery_status": candidate.status,
                "dismissal": candidate.dismissal,
                "mask": candidate.mask,
            },
        })
    return rows


def reachable_summary(layers: dict[tuple[str, str, str], list[Candidate]]) -> dict[str, Any]:
    total = sum(len(bucket) for bucket in layers.values())
    by_status: dict[str, int] = {}
    by_dismissal: dict[str, int] = {}
    ledger_nonzero = {field: 0 for field in LEDGER_FIELDS}
    all_records: list[dict[str, Any]] = []
    for bucket in layers.values():
        for candidate in bucket:
            by_status[candidate.status] = by_status.get(candidate.status, 0) + 1
            by_dismissal[candidate.dismissal] = by_dismissal.get(candidate.dismissal, 0) + 1
            all_records.append(candidate.flat)
            for field in LEDGER_FIELDS:
                if int(candidate.flat.get(field, 0)) != 0:
                    ledger_nonzero[field] += 1
    constant_fields: list[dict[str, Any]] = []
    if all_records:
        for field in sorted(all_records[0]):
            values = {record.get(field) for record in all_records}
            if len(values) == 1:
                constant_fields.append({"field": field, "value": next(iter(values))})
    return {
        "distinct_records": total,
        "strata": len(layers),
        "by_status": dict(sorted(by_status.items())),
        "by_dismissal": dict(sorted(by_dismissal.items())),
        "ledger_nonzero_records": ledger_nonzero,
        "constant_fields_in_reachable_space": constant_fields,
        "route_pairs": [f"{status}/{dismissal}" for status, dismissal in ROUTE_PAIRS],
    }


__all__ = [
    "Candidate",
    "FACT_GRID",
    "PROFILES",
    "ROUTE_PAIRS",
    "dismissal_facts",
    "enumerate_combined",
    "enumerate_layers",
    "iter_route_facts",
    "layer_key",
    "layer_mask",
    "make_candidate",
    "reachable_summary",
    "required_candidates",
    "required_combination_facts",
    "status_facts",
]
