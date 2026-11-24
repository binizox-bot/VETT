from __future__ import annotations


VERSION = "VETT-Cricket-v0.30-R23-knowledge-open-reasoning"
EMBEDDED_VERSION = "VETT-Cricket-v0.31-R23.1-text-embedded-rule-reasoning"
BASE_VERSION = "VETT-Cricket-v0.29-R22-five-level-evidence"
DEFAULT_SEED = 23031
LEVELS = ("L1", "L2", "L3", "L4", "L5")

RULESET = {
    "authority": "Marylebone Cricket Club",
    "title": "Laws of Cricket 2017 Code, 4th Edition 2026",
    "effective_date": "2026-10-01",
    "source_url": "https://www.lords.org/getattachment/e8b12929-1e84-4927-af4e-2a5875b53589/Laws-of-Cricket-2017-Code-4th-Edition-(2026).pdf",
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
    "BASE_VERSION",
    "DEFAULT_SEED",
    "EMBEDDED_VERSION",
    "LEVELS",
    "OPEN_REASONING_ATOMS",
    "RELATION_ATOMS",
    "RULESET",
    "VERSION",
]
