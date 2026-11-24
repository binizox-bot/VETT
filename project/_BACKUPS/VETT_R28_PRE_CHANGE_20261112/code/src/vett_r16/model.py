from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


JsonValue = str | int | float | bool | None


@dataclass(frozen=True)
class AuthorityPolicy:
    source_priority: dict[str, int]

    def rank(self, source: str) -> int:
        try:
            return self.source_priority[source]
        except KeyError as exc:
            raise ValueError(f"unknown source class: {source}") from exc


@dataclass(frozen=True)
class Claim:
    claim_id: str
    document_id: str
    span_id: str
    source: str
    observed_at: int
    innings: str | None
    field: str
    entity: str | None
    value: JsonValue
    status: str = "asserted"
    supersedes: tuple[str, ...] = field(default_factory=tuple)
    invalidates: tuple[str, ...] = field(default_factory=tuple)

    def matches(self, target: "Target") -> bool:
        return (
            self.innings == target.innings
            and self.field == target.field
            and self.entity == target.entity
        )

    def __post_init__(self) -> None:
        if not self.claim_id or not self.document_id or not self.span_id:
            raise ValueError("claim, document, and span IDs must be non-empty")
        if self.status not in {"asserted", "retraction"}:
            raise ValueError(f"unsupported claim status: {self.status}")
        if self.status == "asserted" and self.value is None:
            raise ValueError("asserted claims require a value")
        if self.status == "retraction" and not self.invalidates:
            raise ValueError("retractions must invalidate at least one claim")


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

