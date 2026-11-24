"""Human gate.

Endpoint changes, the publish decision and touching the frozen R26.15 candidate
are human-only actions.  With ``allow_human_gate=False`` (the default) the gate
raises ``HumanGateRequired`` (exit 7) *before* any write happens.

Writing inside R26.15 is refused unconditionally: R28 forbids it, so even
``allow_human_gate=True`` cannot unlock it.
"""

from __future__ import annotations

import pathlib
from typing import Any

from .errors import HumanGateRequired
from .events import append_jsonl


PROTECTED_ACTIONS = ("modify_endpoint", "publish_decision", "touch_r26_15")


class HumanGate:
    def __init__(self, *, allow: bool, run_dir: pathlib.Path,
                 r26_15_root: pathlib.Path | None = None,
                 ledger: pathlib.Path | None = None):
        self.allow = bool(allow)
        self.run_dir = pathlib.Path(run_dir)
        self.r26_root = pathlib.Path(r26_15_root) if r26_15_root else None
        self.ledger = ledger or (self.run_dir / "human_gate_ledger.jsonl")

    def _record(self, action: str, decision: str, evidence: dict[str, Any] | None) -> None:
        append_jsonl(self.ledger, {
            "schema": "vett-r28-pipeline-human-gate/v1",
            "action": action,
            "decision": decision,
            "allow_human_gate": self.allow,
            "evidence": evidence or {},
        })

    def require(self, action: str, *, reason: str,
                evidence: dict[str, Any] | None = None) -> dict[str, Any]:
        if action not in PROTECTED_ACTIONS:
            raise ValueError(f"unknown protected action {action!r}")
        payload = {"action": action, "reason": reason, "evidence": evidence or {}}
        if not self.allow:
            self._record(action, "refused", payload)
            raise HumanGateRequired(
                f"{action} requires a human gate; rerun with --allow-human-gate "
                f"and an explicit human decision (reason: {reason})"
            )
        self._record(action, "allowed", payload)
        return payload

    def guard_write(self, path: pathlib.Path | str) -> pathlib.Path:
        """Refuse any write inside the frozen R26.15 candidate."""
        target = pathlib.Path(path).resolve()
        if self.r26_root is not None:
            try:
                target.relative_to(self.r26_root.resolve())
            except ValueError:
                return target
            self._record("touch_r26_15", "refused", {"path": str(target)})
            raise HumanGateRequired(
                f"write to the frozen R26.15 candidate is forbidden in R28: {target}"
            )
        return target


__all__ = ["PROTECTED_ACTIONS", "HumanGate"]
