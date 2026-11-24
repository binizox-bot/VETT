from __future__ import annotations

from dataclasses import dataclass


VERSION = "VETT-Cricket-v0.29-R22-five-level-evidence"
DEFAULT_SEED = 22029

LEVELS = ("L1", "L2", "L3", "L4", "L5")
TARGET_FAMILIES = (
    "cell_value",
    "entity_scope",
    "event_state",
    "derived_indicator",
    "consistency_provenance",
)

ALLOWED_RELATIONS = {
    "supersedes",
    "retracts",
    "copies_from",
    "qualifies",
    "computed_from",
}

DUPLICATE_MAP = {
    "match_0038": "match_0037",
    "match_0119": "match_0118",
    "match_0200": "match_0197",
}


@dataclass(frozen=True)
class LevelContract:
    level: str
    min_decisive_spans: int
    max_decisive_spans: int
    min_decisive_edges: int
    max_decisive_edges: int
    min_depth: int
    max_depth: int
    min_candidate_values: int
    calibration_point: float


LEVEL_CONTRACTS = {
    "L1": LevelContract("L1", 2, 3, 1, 2, 1, 2, 2, 0.88),
    "L2": LevelContract("L2", 3, 5, 2, 4, 2, 3, 3, 0.77),
    "L3": LevelContract("L3", 4, 7, 3, 6, 3, 4, 3, 0.65),
    "L4": LevelContract("L4", 6, 10, 5, 9, 3, 5, 4, 0.52),
    "L5": LevelContract("L5", 9, 14, 8, 13, 4, 6, 5, 0.35),
}

# A lower level may only select an R21 target whose existing graph is no harder
# than the R22 contract. Higher levels dominate every R21 mechanism directly.
COMPATIBLE_R21_MECHANISMS = {
    "L1": {"one_step", "scoped"},
    "L2": {"one_step", "scoped", "two_step", "retract_replace"},
    "L3": {"one_step", "scoped", "two_step", "retract_replace", "copy_trap"},
    "L4": {"one_step", "scoped", "two_step", "retract_replace", "copy_trap"},
    "L5": {"one_step", "scoped", "two_step", "retract_replace", "copy_trap"},
}

# Exact construction targets. Provenance-only stale copies are additional and do
# not count as decisive proof.
DECISIVE_SHAPES = {
    "L1": (2, 1),
    "L2": (3, 2),
    "L3": (4, 3),
    "L4": (7, 6),
    "L5": (11, 10),
}

PROVENANCE_SHAPES = {
    "L1": (0, 0),
    "L2": (0, 0),
    "L3": (2, 2),
    "L4": (1, 1),
    "L5": (3, 3),
}


def expected_probe_count(match_count: int) -> int:
    return match_count * len(LEVELS) * len(TARGET_FAMILIES)


__all__ = [
    "ALLOWED_RELATIONS",
    "COMPATIBLE_R21_MECHANISMS",
    "DECISIVE_SHAPES",
    "DEFAULT_SEED",
    "DUPLICATE_MAP",
    "LEVELS",
    "LEVEL_CONTRACTS",
    "PROVENANCE_SHAPES",
    "TARGET_FAMILIES",
    "VERSION",
    "LevelContract",
    "expected_probe_count",
]
