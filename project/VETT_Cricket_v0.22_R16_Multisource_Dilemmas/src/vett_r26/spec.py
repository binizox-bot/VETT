from __future__ import annotations

from vett_r25.spec import PILOT_MATCH_IDS, RULESET


VERSION = "VETT-Cricket-v0.36.7-R26.7-authority-binding-pilot"
CANDIDATE_VERSION = "VETT-Cricket-v0.36.12-R26.12-anchor-stability-candidate"
MEASUREMENT_VALIDITY_VERSION = (
    "VETT-Cricket-v0.36.13-R26.13-measurement-validity-candidate"
)
ANSWER_BLIND_VERSION = (
    "VETT-Cricket-v0.36.14-R26.14-answer-blind-shadow"
)
CONTENT_DEPENDENCY_VERSION = (
    "VETT-Cricket-v0.36.15-R26.15-content-dependency-shadow"
)
DIFFICULTY_DESIGN_REVISION = (
    "R26.12-OBSERVED-AUTHORITY-RULE-AND-SOURCE-ORDER-ANCHORS"
)
MEASUREMENT_DESIGN_REVISION = (
    "R26.13-ROLE-NEUTRAL-IDS-CAUSAL-PROOFS-AND-NATURALIZED-SOURCE-PROSE"
)
ANSWER_BLIND_DESIGN_REVISION = (
    "R26.14-DOSSIER-BOUND-COUNTERFACTUAL-INSTRUCTION-AND-PRIOR-AWARE-METRICS"
)
CONTENT_DEPENDENCY_DESIGN_REVISION = (
    "R26.15-INTERVENTION-TO-AFFECTED-RULE-CONTENT-DEPENDENCY-GRAPH"
)
BASE_VERSION = "VETT-Cricket-v0.35-R25.2-diagnostic-pilot"
DEFAULT_SEED = 26041
LEVELS = ("L1", "L2", "L3", "L4", "L5")
POSITION_FORMS = ("head", "middle", "tail")
EVIDENCE_RELATIONS = (
    "identifies",
    "resolves_to",
    "governed_by",
    "authorizes",
    "rejects",
    "supports_decision",
    "governs_decision",
)
CONTENT_DEPENDENCY_RELATIONS = EVIDENCE_RELATIONS + ("conditions_rule",)

# Number of necessary natural-language identity links from the query description to
# the terminal label used by the incident observations.
# Identity length alone did not control empirical difficulty. R26.2 restores the
# interpretable 1--5 schedule and adds source-authority conflicts independently.
SEMANTIC_BRIDGE_DEPTH = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}

STRONG_PANEL_BANDS = {
    "L1": (0.76, 0.84),
    "L2": (0.62, 0.68),
    "L3": (0.48, 0.54),
    "L4": (0.32, 0.40),
    "L5": (0.16, 0.24),
}

FORBIDDEN_PUBLIC_MARKERS = (
    "correct answer",
    "gold answer",
    "distractor",
    "misleading",
    "non-authoritative",
    "ignore this",
    "case-",
    "obs-",
    "pkt-",
)

POSITION_BANDS = {
    "head": (0.0, 0.30),
    "middle": (0.30, 0.70),
    "tail": (0.70, 1.0),
}

__all__ = [
    "ANSWER_BLIND_DESIGN_REVISION",
    "ANSWER_BLIND_VERSION",
    "BASE_VERSION",
    "CANDIDATE_VERSION",
    "CONTENT_DEPENDENCY_DESIGN_REVISION",
    "CONTENT_DEPENDENCY_RELATIONS",
    "CONTENT_DEPENDENCY_VERSION",
    "DEFAULT_SEED",
    "DIFFICULTY_DESIGN_REVISION",
    "FORBIDDEN_PUBLIC_MARKERS",
    "EVIDENCE_RELATIONS",
    "LEVELS",
    "MEASUREMENT_DESIGN_REVISION",
    "MEASUREMENT_VALIDITY_VERSION",
    "PILOT_MATCH_IDS",
    "POSITION_BANDS",
    "POSITION_FORMS",
    "RULESET",
    "SEMANTIC_BRIDGE_DEPTH",
    "STRONG_PANEL_BANDS",
    "VERSION",
]
