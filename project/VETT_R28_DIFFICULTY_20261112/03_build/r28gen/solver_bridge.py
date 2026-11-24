"""Read-only bridge to the frozen deterministic solver.

The R28 oracle is the already frozen ``vett_r25.solver`` (a single-ball rules
lookup).  We import it instead of reimplementing it so that every gold record is
produced by the same code the R26.15 baseline used; the module digest is pinned
and re-verified at build time, and ``sys.dont_write_bytecode`` keeps the protected
tree byte-identical (no new ``__pycache__`` entries either).
"""

from __future__ import annotations

import sys

from .canonical import sha256_file, sha256_text, canon
from .constants import SRC

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vett_r25.scenarios import RULE_TEXT  # noqa: E402
from vett_r25.solver import (  # noqa: E402
    LEDGER_ORDER as SOLVER_LEDGER_ORDER,
    flatten_record,
    solve,
    trace_state,
    validate_record,
)

SOLVER_PATH = SRC / "vett_r25" / "solver.py"
SCENARIOS_PATH = SRC / "vett_r25" / "scenarios.py"

# Pinned digests of the frozen reference implementation (t1 baseline).
PINNED_SOLVER_SHA256 = "4fcd8a10fe5cb7c8de422c2357ebefc13fe82d3e69020cfcada955b4a5fe3362"
PINNED_SCENARIOS_SHA256 = "d695252cb5a0c4b0183fbdd4764d1b52177187b50c7483b690e5b9e413b5b45a"


class SolverDrift(RuntimeError):
    """Raised when the frozen solver bytes no longer match the pinned digest."""


def solver_provenance(*, strict: bool = True) -> dict[str, object]:
    """Return the digest record for the frozen solver, optionally enforcing it."""

    solver_sha = sha256_file(SOLVER_PATH)
    scenarios_sha = sha256_file(SCENARIOS_PATH)
    record = {
        "module": "vett_r25.solver",
        "path": "src/vett_r25/solver.py",
        "sha256": solver_sha,
        "pinned_sha256": PINNED_SOLVER_SHA256,
        "scenarios_path": "src/vett_r25/scenarios.py",
        "scenarios_sha256": scenarios_sha,
        "pinned_scenarios_sha256": PINNED_SCENARIOS_SHA256,
        "matches_pinned": solver_sha == PINNED_SOLVER_SHA256 and scenarios_sha == PINNED_SCENARIOS_SHA256,
    }
    if strict and not record["matches_pinned"]:
        raise SolverDrift(
            "frozen solver drifted: "
            f"solver={solver_sha} (pinned {PINNED_SOLVER_SHA256}), "
            f"scenarios={scenarios_sha} (pinned {PINNED_SCENARIOS_SHA256})"
        )
    return record


def solve_flat(facts: dict) -> tuple[dict, dict, str]:
    """Solve one fact set; return ``(record, flat_record, flat_record_sha256)``."""

    record = solve(facts)
    flat = flatten_record(record)
    return record, flat, sha256_text(canon(flat))


def flat_of(record: dict) -> dict:
    return flatten_record(record)


def rule_text(rule_key: str) -> str:
    return RULE_TEXT[rule_key]


def solver_rule_keys() -> tuple[str, ...]:
    return tuple(sorted(RULE_TEXT))


def trace_state_safe(facts: dict, record: dict, active_source: str) -> dict:
    """Latent state for the gold file (never part of the 12-field record)."""

    try:
        return trace_state(facts, record, active_source)
    except Exception as exc:  # noqa: BLE001 - state is diagnostic only
        return {"error": f"{type(exc).__name__}: {exc}", "active_source": active_source}


__all__ = [
    "PINNED_SCENARIOS_SHA256",
    "PINNED_SOLVER_SHA256",
    "RULE_TEXT",
    "SOLVER_LEDGER_ORDER",
    "SolverDrift",
    "flat_of",
    "rule_text",
    "solve",
    "solve_flat",
    "solver_provenance",
    "solver_rule_keys",
    "trace_state_safe",
    "validate_record",
]
