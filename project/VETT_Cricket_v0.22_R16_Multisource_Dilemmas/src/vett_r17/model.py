from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


JsonValue = str | int | float | bool | None


@dataclass(frozen=True)
class Claim:
    claim_id: str
    document_id: str
    span_id: str
    docket_id: str
    observed_at: int
    innings: str | None
    field: str
    entity: str | None
    value: JsonValue
    status: str = "asserted"
    supersedes: tuple[str, ...] = field(default_factory=tuple)
    invalidates: tuple[str, ...] = field(default_factory=tuple)
    derived_from: tuple[str, ...] = field(default_factory=tuple)

    def matches(self, target: "Target") -> bool:
        return (
            self.innings == target.innings
            and self.field == target.field
            and self.entity == target.entity
        )

    @property
    def references(self) -> tuple[str, ...]:
        return self.supersedes + self.invalidates + self.derived_from

    def __post_init__(self) -> None:
        if not all((self.claim_id, self.document_id, self.span_id, self.docket_id)):
            raise ValueError("claim, document, span, and docket IDs must be non-empty")
        if self.status not in {"asserted", "retraction"}:
            raise ValueError(f"unsupported claim status: {self.status}")
        if self.status == "asserted" and self.value is None:
            raise ValueError("asserted claims require a value")
        if self.status == "retraction" and not self.invalidates:
            raise ValueError("retractions must invalidate at least one claim")
        if self.status == "retraction" and self.value is not None:
            raise ValueError("retractions cannot assert a value")
        if len(set(self.references)) != len(self.references):
            raise ValueError(f"claim {self.claim_id} contains duplicate graph references")


@dataclass(frozen=True)
class Target:
    target_id: str
    innings: str | None
    field: str
    entity: str | None = None


@dataclass(frozen=True)
class Resolution:
    target_id: str
    status: str
    value: JsonValue
    decisive_claim_ids: tuple[str, ...]
    eligible_claim_ids: tuple[str, ...]
    inactive_claim_ids: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "status": self.status,
            "value": self.value,
            "decisive_claim_ids": list(self.decisive_claim_ids),
            "eligible_claim_ids": list(self.eligible_claim_ids),
            "inactive_claim_ids": list(self.inactive_claim_ids),
            "reason": self.reason,
        }
