"""Typed errors for the R28 pipeline.

Each error maps to one stable process exit code so that an unattended caller
(CI, scheduler, a human on the phone) can branch without parsing text.
"""

from __future__ import annotations


class PipelineError(RuntimeError):
    """Base class; ``exit_code`` is the process status the CLI must return."""

    exit_code = 1


class UsageError(PipelineError):
    exit_code = 2


class ConfigError(UsageError):
    exit_code = 2


class GateFailure(PipelineError):
    """A blocking gate returned FAIL and no repair path existed."""

    exit_code = 3


class FrozenViolation(PipelineError):
    """Frozen input drift: R26.15, protected paths, prereg, contract, protocol."""

    exit_code = 4


class BudgetStop(PipelineError):
    """Hard budget / call cap reached: ledger is flushed, pipeline stops."""

    exit_code = 5


class Escalated(PipelineError):
    """A gate still FAILed after the bounded repair rounds (max 2)."""

    exit_code = 6


class HumanGateRequired(PipelineError):
    """An action reserved for a human was attempted with allow_human_gate=False."""

    exit_code = 7


class LocalFirstViolation(PipelineError):
    """A whitelisted local task was routed anywhere but the local ruler."""

    exit_code = 4


class CloudForbidden(LocalFirstViolation):
    """No cloud/paid provider may be reached from this pipeline."""


class CloudUnavailable(PipelineError):
    """Cloud ruler is not configured; degrade honestly and continue."""


class StageError(PipelineError):
    exit_code = 3


__all__ = [
    "PipelineError",
    "UsageError",
    "ConfigError",
    "GateFailure",
    "FrozenViolation",
    "BudgetStop",
    "Escalated",
    "HumanGateRequired",
    "LocalFirstViolation",
    "CloudForbidden",
    "CloudUnavailable",
    "StageError",
]
