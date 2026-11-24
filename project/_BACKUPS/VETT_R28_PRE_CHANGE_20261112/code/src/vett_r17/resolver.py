from __future__ import annotations

from .model import Claim, Resolution, Target


def _reject_cycles(claims_by_id: dict[str, Claim]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(claim_id: str) -> None:
        if claim_id in visiting:
            raise ValueError(f"claim graph contains a cycle at {claim_id}")
        if claim_id in visited:
            return
        visiting.add(claim_id)
        for referenced_id in claims_by_id[claim_id].references:
            visit(referenced_id)
        visiting.remove(claim_id)
        visited.add(claim_id)

    for claim_id in sorted(claims_by_id):
        visit(claim_id)


def resolve_target(claims: list[Claim], target: Target) -> Resolution:
    """Resolve by explicit state edges and copy ancestry, never source ranking."""

    eligible = sorted(
        (claim for claim in claims if claim.matches(target)),
        key=lambda claim: (claim.observed_at, claim.claim_id),
    )
    eligible_ids = tuple(claim.claim_id for claim in eligible)
    if not eligible:
        return Resolution(
            target.target_id,
            "unresolved",
            None,
            (),
            (),
            (),
            "no claims match the target scope",
        )

    claims_by_id = {claim.claim_id: claim for claim in eligible}
    if len(claims_by_id) != len(eligible):
        raise ValueError("duplicate claim IDs within target scope")
    known_ids = set(claims_by_id)
    for claim in eligible:
        unknown = set(claim.references) - known_ids
        if unknown:
            raise ValueError(
                f"claim {claim.claim_id} references claims outside its target scope: "
                f"{sorted(unknown)}"
            )
    _reject_cycles(claims_by_id)

    inactive: set[str] = set()
    for claim in eligible:
        inactive.update(claim.supersedes)
        inactive.update(claim.invalidates)

    changed = True
    while changed:
        changed = False
        for claim in eligible:
            if claim.claim_id in inactive or not claim.derived_from:
                continue
            if any(parent_id in inactive for parent_id in claim.derived_from):
                inactive.add(claim.claim_id)
                changed = True

    active = [
        claim
        for claim in eligible
        if claim.status == "asserted" and claim.claim_id not in inactive
    ]
    inactive_ids = tuple(sorted(inactive))
    if not active:
        return Resolution(
            target.target_id,
            "unresolved",
            None,
            (),
            eligible_ids,
            inactive_ids,
            "all matching assertions were amended, withdrawn, or stale by lineage",
        )

    values = {claim.value for claim in active}
    decisive_ids = tuple(claim.claim_id for claim in active)
    if len(values) != 1:
        return Resolution(
            target.target_id,
            "ambiguous",
            None,
            decisive_ids,
            eligible_ids,
            inactive_ids,
            "active claims disagree without a public state edge",
        )

    return Resolution(
        target.target_id,
        "resolved",
        active[0].value,
        decisive_ids,
        eligible_ids,
        inactive_ids,
        "all conflicting claims were explicitly amended, withdrawn, or stale by lineage",
    )
