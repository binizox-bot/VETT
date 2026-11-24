from __future__ import annotations

VERSION = "VETT-Cricket-v0.35-R25.2-diagnostic-pilot"
BASE_VERSION = "VETT-Cricket-v0.29-R22-five-level-evidence"
DEFAULT_SEED = 25033
LEVELS = ("L1", "L2", "L3", "L4", "L5")

PILOT_MATCH_IDS = (
    "match_0003", "match_0004", "match_0021", "match_0042", "match_0058",
    "match_0066", "match_0067", "match_0072", "match_0074", "match_0095",
    "match_0099", "match_0104", "match_0153", "match_0162", "match_0163",
    "match_0166", "match_0199", "match_0201", "match_0218", "match_0220",
)

RULESET = {
    "authority": "Marylebone Cricket Club",
    "title": "Laws of Cricket 2017 Code, 4th Edition 2026",
    "effective_date": "2026-10-01",
    "source_url": "https://www.lords.org/getattachment/e8b12929-1e84-4927-af4e-2a5875b53589/Laws-of-Cricket-2017-Code-4th-Edition-(2026).pdf",
    "source_sha256": "38ce30020b31cc997c4b05f90dcb3dbc6782336690606b7eda511245f2be8a87",
}

FORBIDDEN_ROLE_WORDS = (
    "misleading", "non-authoritative", "non authoritative", "correct answer",
    "controlling adjudication", "ignore this", "distractor",
)

DECISION_FIELDS = (
    "delivery_status", "counts_in_over", "dismissal", "total_runs",
    "batter_runs", "bowler_runs", "run_ledger",
)

__all__ = [
    "BASE_VERSION", "DECISION_FIELDS", "DEFAULT_SEED", "FORBIDDEN_ROLE_WORDS",
    "LEVELS", "PILOT_MATCH_IDS", "RULESET", "VERSION",
]
