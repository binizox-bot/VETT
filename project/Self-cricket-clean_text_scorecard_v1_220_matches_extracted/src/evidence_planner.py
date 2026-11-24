"""Evidence Requirements Map: guarantees every L2 operand is tracked before generation."""
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from src.parser import MatchData, InningsData
from src.config import DifficultyConfig, NON_BOWLER_EXTRAS


@dataclass
class EvidenceRequirement:
    """A single evidence item that must appear in the commentary."""
    id: str
    field: str
    value: Any
    level: str  # L1, L2, L3
    evidence_type: str  # numeric, name, relationship, cricket_rule
    operand_of: List[str] = field(default_factory=list)
    difficulty_class: str = "D0_explicit"  # D0-D4
    linguistic_form: str = "numeric"
    placement_phase: int = 0  # which narrative phase (1-8)
    innings_ref: int = 0  # 1 or 2, 0 for match-level
    is_critical: bool = False

    # For batter/bowler references
    player_name: Optional[str] = None
    related_name: Optional[str] = None


@dataclass
class EvidenceRequirementsMap:
    """Complete map of all evidence needed for full reversibility."""
    match_id: str
    items: List[EvidenceRequirement] = field(default_factory=list)

    # Grouped for easy access
    by_phase: Dict[int, List[EvidenceRequirement]] = field(default_factory=dict)
    by_level: Dict[str, List[EvidenceRequirement]] = field(default_factory=dict)
    by_difficulty: Dict[str, List[EvidenceRequirement]] = field(default_factory=dict)
    l2_operands: List[EvidenceRequirement] = field(default_factory=list)


def build_evidence_map(md: MatchData, config: DifficultyConfig, rng: random.Random) -> EvidenceRequirementsMap:
    """Build complete evidence requirements map for a match."""
    erm = EvidenceRequirementsMap(match_id=md.match_id)
    counter = [0]

    def _add(**kwargs):
        counter[0] += 1
        eid = f"ev_{counter[0]:04d}"
        item = EvidenceRequirement(id=eid, **kwargs)

        # Assign difficulty class
        if item.level == "L1" or item.evidence_type == "name":
            item.difficulty_class = "D0_explicit"
        elif item.level == "L3":
            item.difficulty_class = "D4_implicit"
        else:
            item.difficulty_class = _assign_difficulty(config, rng)

        # Assign linguistic form
        if item.evidence_type == "numeric":
            from src.number_formatter import pick_form
            item.linguistic_form = pick_form(config.numeric_form_weights, rng)
        elif item.evidence_type == "name":
            item.linguistic_form = "full_name"

        erm.items.append(item)
        if item.level == "L2":
            erm.l2_operands.append(item)
        return item

    # ── L1: Match metadata ──
    _add(field="venue", value=md.venue, level="L1", evidence_type="name", placement_phase=1)
    _add(field="toss_decision", value=md.toss, level="L1", evidence_type="name", placement_phase=1)
    _add(field="result", value=md.result, level="L1", evidence_type="name", placement_phase=8)
    _add(field="player_of_match", value=md.player_of_match, level="L1", evidence_type="name", placement_phase=8)

    # ── Per-innings evidence ──
    for i, inn in enumerate(md.innings):
        pfx_base = 2 if i == 0 else 6  # first innings phases 2-5, second 6-8
        pfx_label = f"inn{i+1}"

        # L1: Innings total
        _add(field=f"{pfx_label}_total_runs", value=inn.total_runs, level="L1",
             evidence_type="numeric", placement_phase=pfx_base + 2,
             innings_ref=i+1, is_critical=True,
             operand_of=[f"{pfx_label}_bat_plus_extras", f"{pfx_label}_bowling_reconciliation"])

        _add(field=f"{pfx_label}_total_wickets", value=inn.total_wickets, level="L1",
             evidence_type="numeric", placement_phase=pfx_base + 2,
             innings_ref=i+1, operand_of=[f"{pfx_label}_wicket_sum"])

        _add(field=f"{pfx_label}_overs", value=inn.overs, level="L1",
             evidence_type="numeric", placement_phase=pfx_base + 2,
             innings_ref=i+1, operand_of=[f"{pfx_label}_run_rate"])

        # L1: Top 3 batters with runs
        batters_scored = sorted(
            [b for b in inn.batters if b.runs > 0],
            key=lambda b: b.runs, reverse=True
        )
        for rank, b in enumerate(batters_scored[:3]):
            clean = _clean_name(b.name)
            _add(field=f"{pfx_label}_batter_{clean}_runs", value=b.runs, level="L1",
                 evidence_type="numeric", placement_phase=pfx_base + (rank % 2),
                 innings_ref=i+1, player_name=clean,
                 operand_of=[f"{pfx_label}_batting_sum", f"{pfx_label}_player_contrib_{clean}"])

        # L1: Best 2 bowlers
        bowlers_sorted = sorted(
            [b for b in inn.bowlers if b.wickets >= 1],
            key=lambda b: (b.wickets, -b.runs_conceded), reverse=True
        )
        for rank, b in enumerate(bowlers_sorted[:2]):
            clean = _clean_name(b.name)
            _add(field=f"{pfx_label}_bowler_{clean}_figures", value=f"{b.wickets}/{b.runs_conceded}",
                 level="L1", evidence_type="numeric", placement_phase=pfx_base + 3,
                 innings_ref=i+1, player_name=clean,
                 operand_of=[f"{pfx_label}_bowling_sum"])

        # L1: Max partnership
        if inn.partnerships:
            max_part = max(inn.partnerships, key=lambda p: p.runs)
            _add(field=f"{pfx_label}_max_partnership", value=max_part.runs, level="L1",
                 evidence_type="numeric", placement_phase=pfx_base + 1,
                 innings_ref=i+1,
                 operand_of=[f"{pfx_label}_fow_chain"])

        # L2: Extras breakdown (critical gap in original)
        extras_phase = pfx_base + 3  # bowling summary phase
        _add(field=f"{pfx_label}_total_extras", value=inn.total_extras, level="L2",
             evidence_type="numeric", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_bat_plus_extras", f"{pfx_label}_extras_breakdown"],
             is_critical=True)
        _add(field=f"{pfx_label}_byes", value=inn.byes, level="L2",
             evidence_type="numeric", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_extras_breakdown", f"{pfx_label}_bowling_reconciliation"],
             is_critical=True)
        _add(field=f"{pfx_label}_leg_byes", value=inn.leg_byes, level="L2",
             evidence_type="numeric", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_extras_breakdown", f"{pfx_label}_bowling_reconciliation"],
             is_critical=True)
        _add(field=f"{pfx_label}_no_balls", value=inn.no_balls, level="L2",
             evidence_type="numeric", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_extras_breakdown"],
             is_critical=True)
        _add(field=f"{pfx_label}_wides", value=inn.wides, level="L2",
             evidence_type="numeric", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_extras_breakdown"],
             is_critical=True)

        # L2: Batting runs sum
        _add(field=f"{pfx_label}_batting_runs_sum", value=inn.batting_runs_sum, level="L2",
             evidence_type="numeric", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_bat_plus_extras"])

        # L2: Bowling runs charged to bowlers (cricket rule: total - byes - lb)
        _add(field=f"{pfx_label}_bowling_runs_charged", value=inn.bowling_runs_charged, level="L2",
             evidence_type="cricket_rule", placement_phase=extras_phase,
             innings_ref=i+1, operand_of=[f"{pfx_label}_bowling_reconciliation"])

        # L2: FOW scores (distributed across phases)
        for fow in inn.fow:
            fow_phase = pfx_base + min(fow.wicket_num // 3, 2)  # spread early/mid/late
            _add(field=f"{pfx_label}_fow_{fow.wicket_num}", value=fow.score, level="L2",
                 evidence_type="numeric", placement_phase=fow_phase,
                 innings_ref=i+1, player_name=_clean_name(fow.batter),
                 operand_of=[f"{pfx_label}_fow_chain"])

        # L2: Partnership runs
        for pi, p in enumerate(inn.partnerships):
            if p.runs >= 15:  # significant partnerships
                part_phase = pfx_base + min(pi // 3, 2)
                _add(field=f"{pfx_label}_partnership_{pi+1}", value=p.runs, level="L2",
                     evidence_type="numeric", placement_phase=part_phase,
                     innings_ref=i+1, operand_of=[f"{pfx_label}_fow_chain"])

        # L2: Player partnership contribution tracking
        for name, contrib in inn.player_contributions.items():
            if contrib >= 20:
                _add(field=f"{pfx_label}_player_contrib_{name}", value=contrib, level="L2",
                     evidence_type="numeric", placement_phase=pfx_base + 1,
                     innings_ref=i+1, player_name=name,
                     operand_of=[f"{pfx_label}_player_contrib_sum"])

    # ── Group by phase, level, difficulty ──
    for item in erm.items:
        ph = item.placement_phase
        if ph not in erm.by_phase:
            erm.by_phase[ph] = []
        erm.by_phase[ph].append(item)

        lv = item.level
        if lv not in erm.by_level:
            erm.by_level[lv] = []
        erm.by_level[lv].append(item)

        dc = item.difficulty_class
        if dc not in erm.by_difficulty:
            erm.by_difficulty[dc] = []
        erm.by_difficulty[dc].append(item)

    return erm


def _assign_difficulty(config: DifficultyConfig, rng: random.Random) -> str:
    tiers = list(config.tier_distribution.items())
    total = sum(w for _, w in tiers)
    r = rng.uniform(0, total)
    cumulative = 0
    for tier, weight in tiers:
        cumulative += weight
        if r <= cumulative:
            return tier
    return tiers[-1][0]


def _clean_name(name: str) -> str:
    """Remove role markers from player name."""
    import re
    return re.sub(r'\s*\([^)]*\)', '', name).strip()
