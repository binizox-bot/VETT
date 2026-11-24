"""
Multi-Tier Difficulty System for Cricket Text-to-Table Fields.

Four tiers designed so that a model must demonstrate progressively
deeper reasoning capability:

D1 (Easy)     - Direct extraction: value stated near its context
D2 (Medium)   - Arithmetic: operands present but require addition/subtraction
D3 (Hard)     - Cricket Rule: requires domain knowledge + distributed operands
D4 (Expert)   - Deep Inference: scattered evidence, qualitative hints, multi-step

Each scorecard field is assigned a tier.
"""
from collections import Counter

# ═══════════════════════════════════════════════════════════════════
# FIELD → TIER MAPPING
# ═══════════════════════════════════════════════════════════════════

FIELD_TIERS = {
    # ── Match Metadata ──
    "match_winner": "D1",
    "result": "D1",
    "toss_decision": "D1",
    "venue": "D1",
    "player_of_match": "D1",
    "umpires": "D4",        # almost never in commentary
    "referee": "D4",         # almost never in commentary

    # ── Innings Summary ──
    "innings_total_runs": "D1",
    "innings_total_wickets": "D1",
    "innings_overs": "D1",
    "innings_run_rate": "D3",    # need to compute from runs/overs

    # ── Extras (the hardest area) ──
    "extras_total": "D2",        # stated, but breakdown requires arithmetic
    "extras_byes": "D3",         # mentioned but must know cricket rule
    "extras_leg_byes": "D3",     # mentioned but must know cricket rule
    "extras_no_balls": "D2",     # stated in extras breakdown
    "extras_wides": "D2",        # stated in extras breakdown
    "extras_breakdown_sum": "D2", # B+LB+NB+W = total: arithmetic

    # ── Batting ──
    "batter_runs_top3": "D1",       # top 3 batters: explicit
    "batter_runs_mid": "D2",        # middle batters: mentioned, need to find
    "batter_runs_tail": "D3",       # tail: scattered in narrative
    "batter_balls": "D3",           # balls faced: sometimes stated, sometimes inferred
    "batter_fours": "D3",           # boundaries: sparsely mentioned
    "batter_sixes": "D3",
    "batter_sr": "D4",              # strike rate: almost never stated, must compute
    "batting_runs_sum": "D2",       # sum of all batter runs: stated in extras context
    "batting_runs_plus_extras": "D2", # B+E=T: arithmetic verification

    # ── Bowling ──
    "bowler_wickets_top2": "D1",   # best bowlers: explicit figures
    "bowler_runs_top2": "D1",
    "bowler_wickets_others": "D3", # other bowlers: scattered mentions
    "bowler_runs_others": "D3",
    "bowler_overs": "D4",          # per-bowler overs: almost never stated
    "bowler_maidens": "D4",
    "bowler_econ": "D4",           # economy: qualitative only
    "bowling_runs_sum": "D2",      # sum of bowler runs: stated in extras context
    "bowling_runs_charged": "D3",  # total - B - LB: cricket rule required
    "bowling_wickets_sum": "D2",   # bowler wickets sum verification

    # ── Partnerships ──
    "partnership_runs_major": "D1",   # big stands: explicitly stated
    "partnership_runs_minor": "D2",   # small stands: mentioned in passing
    "partnership_contribution": "D3", # who scored what within partnership
    "partnership_extras": "D3",

    # ── Fall of Wickets ──
    "fow_score_early": "D1",      # first 3 wickets: stated at fall
    "fow_score_mid": "D2",        # middle wickets: mixed in narrative
    "fow_score_late": "D2",       # late wickets: tail-end mentions
    "fow_chain_verification": "D2", # partnership accumulation check

    # ── Match Result ──
    "result_margin_runs": "D1",     # "won by X runs"
    "result_margin_wickets": "D1",  # "won by X wickets"
    "chase_logic": "D3",            # target, achieved, wickets: cricket rule
    "chase_pressure": "D3",         # FOW + asking rate synthesis
}

# ═══════════════════════════════════════════════════════════════════
# TIER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

TIER_DEFINITIONS = {
    "D1": {
        "name": "Direct Extraction",
        "description": "Value is explicitly stated in commentary near its natural context",
        "operand_strategy": "explicit_near",
        "example": '"Ethan Drake top-scored with 49 from 62 balls" — both runs and balls directly stated',
        "model_task": "Locate and extract the value from the relevant sentence",
        "target_accuracy": ">95% for strong models",
    },
    "D2": {
        "name": "Arithmetic Verification",
        "description": "Operands are present in the same section of commentary, but the target value requires addition or subtraction to compute",
        "operand_strategy": "same_section_arithmetic",
        "example": '"The 21 extras broke down into 2 byes, 3 leg-byes, 1 no-ball and 15 wides" — model must compute 2+3+1+15=21',
        "model_task": "Identify all operands in a passage and perform arithmetic",
        "target_accuracy": ">85% for strong models",
    },
    "D3": {
        "name": "Cricket Rule Application",
        "description": "Operands are distributed across different paragraphs AND a cricket rule must be applied to reach the target value",
        "operand_strategy": "distributed_with_rule",
        "example": 'Byes (2) and leg-byes (3) mentioned in extras paragraph; total (144) in innings close. Model must know: bowling_runs = total - byes - leg_byes = 139',
        "model_task": "Gather operands from multiple locations, apply domain-specific cricket rule, perform arithmetic",
        "target_accuracy": ">70% for strong models",
    },
    "D4": {
        "name": "Expert Inference",
        "description": "Evidence is scattered across the entire commentary, some operands are only qualitatively described, and multiple inference steps are required",
        "operand_strategy": "deeply_distributed_qualitative",
        "example": 'Economy rate: bowler runs mentioned in paragraph 3, overs mentioned as innings total in paragraph 1, per-bowler overs must be inferred from "bowled a tight spell" descriptions',
        "model_task": "Synthesize qualitative and quantitative evidence from across the full text, apply multiple cricket rules, infer missing intermediate values",
        "target_accuracy": ">50% for strong models (diagnostic field)",
    },
}

# ═══════════════════════════════════════════════════════════════════
# TIER DISTRIBUTION CONFIG (per match)
# ═══════════════════════════════════════════════════════════════════

# How evidence is embedded per tier
EMBEDDING_STRATEGIES = {
    "D1": {
        "sentence_position": "dedicated",     # gets its own clear sentence
        "name_proximity": "adjacent",          # number right next to player name
        "form_variation": False,               # always numeric, never spelled
        "paragraph_distribution": 1,           # all in same paragraph
    },
    "D2": {
        "sentence_position": "embedded",       # embedded in a longer sentence
        "name_proximity": "same_section",      # in same section but not adjacent
        "form_variation": True,                # sometimes spelled-out
        "paragraph_distribution": 1,           # all operands in same paragraph
    },
    "D3": {
        "sentence_position": "distributed",    # scattered across the narrative
        "name_proximity": "different_sections", # may be far apart
        "form_variation": True,                # varied forms (numeric + spelled)
        "paragraph_distribution": 2,           # operands in 2+ different paragraphs
        "rule_hint": False,                    # cricket rule NOT explained in text
    },
    "D4": {
        "sentence_position": "hidden",         # deeply embedded, never highlighted
        "name_proximity": "far",               # may be very far from context
        "form_variation": True,
        "paragraph_distribution": 3,           # operands in 3+ different paragraphs
        "rule_hint": False,                    # no hints
        "qualitative_only": True,              # some values only qualitative
    },
}


def get_field_tier(field_name: str) -> str:
    """Look up the difficulty tier for a scorecard field."""
    # Try exact match first
    if field_name in FIELD_TIERS:
        return FIELD_TIERS[field_name]
    # Try partial match
    for key, tier in FIELD_TIERS.items():
        if key in field_name or field_name in key:
            return tier
    return "D2"  # default medium


def get_tier_info(tier: str) -> dict:
    """Get full tier definition."""
    return TIER_DEFINITIONS.get(tier, TIER_DEFINITIONS["D2"])


def get_embedding_strategy(tier: str) -> dict:
    """Get evidence embedding strategy for a tier."""
    return EMBEDDING_STRATEGIES.get(tier, EMBEDDING_STRATEGIES["D2"])


def tier_summary() -> dict:
    """Count fields per tier."""
    counts = Counter(FIELD_TIERS.values())
    return dict(counts)
