"""Configuration for difficulty tiers, format settings, and generation parameters."""
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class DifficultyConfig:
    """Controls the difficulty gradient of generated commentaries."""

    tier_distribution: Dict[str, float] = field(default_factory=lambda: {
        "D0_explicit": 0.30,
        "D1_variant": 0.25,
        "D2_distributed": 0.25,
        "D3_rule_required": 0.15,
        "D4_implicit": 0.05,
    })

    numeric_form_weights: Dict[str, float] = field(default_factory=lambda: {
        "numeric": 0.40,
        "spelled": 0.30,
        "hybrid": 0.20,
        "descriptive": 0.10,
    })

    multi_hop_distance: Tuple[int, int] = (2, 5)
    min_template_distance: int = 3

    polish_enabled: bool = True
    polish_max_retries: int = 3


# Preset difficulty profiles
EASY_PROFILE = DifficultyConfig(
    tier_distribution={
        "D0_explicit": 0.70,
        "D1_variant": 0.20,
        "D2_distributed": 0.10,
        "D3_rule_required": 0.00,
        "D4_implicit": 0.00,
    },
    numeric_form_weights={"numeric": 0.70, "spelled": 0.15, "hybrid": 0.10, "descriptive": 0.05},
)

MEDIUM_PROFILE = DifficultyConfig(
    tier_distribution={
        "D0_explicit": 0.30,
        "D1_variant": 0.25,
        "D2_distributed": 0.25,
        "D3_rule_required": 0.15,
        "D4_implicit": 0.05,
    },
    numeric_form_weights={"numeric": 0.40, "spelled": 0.30, "hybrid": 0.20, "descriptive": 0.10},
)

HARD_PROFILE = DifficultyConfig(
    tier_distribution={
        "D0_explicit": 0.15,
        "D1_variant": 0.20,
        "D2_distributed": 0.30,
        "D3_rule_required": 0.25,
        "D4_implicit": 0.10,
    },
    numeric_form_weights={"numeric": 0.20, "spelled": 0.35, "hybrid": 0.25, "descriptive": 0.20},
)

PROFILES = {"easy": EASY_PROFILE, "medium": MEDIUM_PROFILE, "hard": HARD_PROFILE}


# ── Cricket rule constants ──
# Byes and leg-byes do NOT count against bowlers. Wides and no-balls DO.
NON_BOWLER_EXTRAS = ["byes", "leg_byes"]
BOWLER_EXTRAS = ["wides", "no_balls"]

# Match format detection
ODI_MAX_OVERS = 50.0
T20_MAX_OVERS = 20.0

# Story type classification thresholds
STORY_THRESHOLDS = {
    "blowout_margin_runs": 100,
    "blowout_margin_wickets": 7,
    "close_margin_runs": 20,
    "close_margin_wickets": 3,
    "big_partnership": 80,
    "early_collapse_fow": 3,  # wickets lost before score reaches X
    "early_collapse_score": 50,
}
