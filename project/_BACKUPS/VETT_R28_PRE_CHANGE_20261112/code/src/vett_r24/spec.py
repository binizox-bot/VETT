from __future__ import annotations

VERSION = "VETT-Cricket-v0.32-R24-high-difficulty-rule-reasoning"
BASE_VERSION = "VETT-Cricket-v0.29-R22-five-level-evidence"
DEFAULT_SEED = 24032
LEVELS = ("L1", "L2", "L3", "L4", "L5")

RULESET = {
    "authority": "Marylebone Cricket Club",
    "title": "Laws of Cricket 2017 Code, 4th Edition 2026",
    "effective_date": "2026-10-01",
    "source_url": "https://www.lords.org/getattachment/e8b12929-1e84-4927-af4e-2a5875b53589/Laws-of-Cricket-2017-Code-4th-Edition-(2026).pdf",
    "source_sha256": "38ce30020b31cc997c4b05f90dcb3dbc6782336690606b7eda511245f2be8a87",
}

EVIDENCE_PROFILE = {
    "L1": {"decisive": 1, "misleading": 0, "reasoning_components_min": 1},
    "L2": {"decisive": 2, "misleading": 0, "reasoning_components_min": 2},
    "L3": {"decisive": 2, "misleading": 1, "reasoning_components_min": 2},
    "L4": {"decisive": 3, "misleading": 1, "reasoning_components_min": 3},
    "L5": {"decisive": 3, "misleading": 2, "reasoning_components_min": 3},
}

MUTATION_BUDGET = {
    "replace_unreferenced_routing_spans_max": 7,
    "insert_rule_spans_max": 9,
    "touch_base_spans_percent_max": 1.2,
}

OPEN_REASONING_ATOMS = (
    "FOLLOWS_SUPERSEDES",
    "APPLIES_RETRACTION",
    "INHERITS_COPY_STATUS",
    "APPLIES_SCOPE_QUALIFIER",
    "EXECUTES_PUBLIC_COMPUTATION",
    "SEPARATES_DECISIVE_FROM_PROVENANCE",
    "REJECTS_DOCUMENT_ORDER_AUTHORITY",
    "REJECTS_FREQUENCY_AUTHORITY",
)

RELATION_ATOMS = {
    "supersedes": "FOLLOWS_SUPERSEDES",
    "retracts": "APPLIES_RETRACTION",
    "copies_from": "INHERITS_COPY_STATUS",
    "qualifies": "APPLIES_SCOPE_QUALIFIER",
    "computed_from": "EXECUTES_PUBLIC_COMPUTATION",
}

__all__ = [
    "BASE_VERSION", "DEFAULT_SEED", "EVIDENCE_PROFILE", "LEVELS", "MUTATION_BUDGET",
    "OPEN_REASONING_ATOMS", "RELATION_ATOMS", "RULESET", "VERSION",
]
