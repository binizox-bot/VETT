from __future__ import annotations

from .model import AuthorityPolicy, Claim, Resolution, Target


def resolve_target(
    claims: list[Claim], target: Target, policy: AuthorityPolicy
) -> Resolution:
    """Resolve one target using exact scope, explicit state edges, and authority."""

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

    known_ids = {claim.claim_id for claim in eligible}
    inactive: set[str] = set()
    for claim in eligible:
        referenced = set(claim.supersedes) | set(claim.invalidates)
        unknown = referenced - known_ids
        if unknown:
            raise ValueError(
                f"claim {claim.claim_id} references claims outside its target scope: "
                f"{sorted(unknown)}"
            )
        inactive.update(referenced)

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
            "all matching assertions were superseded or invalidated",
        )

    best_rank = min(policy.rank(claim.source) for claim in active)
    decisive = [claim for claim in active if policy.rank(claim.source) == best_rank]
    values = {claim.value for claim in decisive}
    decisive_ids = tuple(claim.claim_id for claim in decisive)

    if len(values) != 1:
        return Resolution(
            target.target_id,
            "ambiguous",
            None,
            decisive_ids,
            eligible_ids,
            inactive_ids,
            "top-authority active claims disagree without an explicit state edge",
        )

    return Resolution(
        target.target_id,
        "resolved",
        decisive[0].value,
        decisive_ids,
        eligible_ids,
        inactive_ids,
        f"selected authority rank {best_rank} after scope and state filtering",
    )
