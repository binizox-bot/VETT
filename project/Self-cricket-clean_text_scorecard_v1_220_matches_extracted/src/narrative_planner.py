"""Narrative Planner v2: evidence aggregation + composite slots for natural prose."""
import random
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.parser import MatchData, InningsData, BatterData, BowlerData
from src.evidence_planner import EvidenceRequirementsMap, EvidenceRequirement
from src.story_classifier import classify_story, STORY_DESCRIPTORS
from src.config import DifficultyConfig
from src.difficulty_tiers import get_field_tier


# Category → default difficulty tier
CATEGORY_TIERS = {
    # No D1 categories — everything requires at least arithmetic or distributed reading
    "setting_opening": "D2",    # venue+toss: embedded in narrative opening
    "innings_start": "D2",      # openers: described, not listed
    "wicket_fall": "D2",        # FOW scores: embedded, not listed
    "partnership_build": "D2",  # partnership math: need arithmetic
    "anchor_batter": "D2",      # top scorer: distributed in prose
    "tail_wicket": "D2",        # late wickets: less prominent
    "innings_close": "D2",      # totals: qualitative, not repeated
    "bowling_summary": "D2",    # figures: embedded in flowing prose
    "extras_accounting": "D3",  # ★ CRITICAL: cricket rule + arithmetic
    "chase_start": "D2",        # target embedded, not headlined
    "chase_wicket": "D2",       # chase FOW: distributed
    "chase_partnership": "D2",  # chase partnership math
    "chase_anchor": "D2",       # chase top scorer: distributed
    "chase_close": "D2",        # result margin: narrative, not formulaic
    "match_result": "D2",       # result+POM: narrative, not formulaic
}


@dataclass
class CompositeSlot:
    """A narrative position that bundles related evidence items into one natural sentence."""
    phase: int
    order: int
    category: str  # "innings_open", "wicket_fall", "partnership", "extras_accounting", etc.
    tier: str = "D2"  # D1-D4 difficulty tier for this evidence
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NarrativePlan:
    match_id: str
    story_type: str
    phase_emphasis: List[float]
    format_type: str
    slots: List[CompositeSlot] = field(default_factory=list)


def plan_narrative(md: MatchData, erm,  # erm is optional (can be None)
                   config: DifficultyConfig, rng: random.Random) -> NarrativePlan:
    story_info = classify_story(md)
    plan = NarrativePlan(match_id=md.match_id, story_type=story_info["type"],
                         phase_emphasis=story_info["emphasis"], format_type=md.format_type)

    inns = md.innings
    v = _build_base_values(md, rng)
    phase_order = {p: 0 for p in range(1, 9)}

    def _add(phase, category, extra_vals=None):
        phase_order[phase] += 1
        sv = dict(v)
        if extra_vals:
            sv.update(extra_vals)
        tier = CATEGORY_TIERS.get(category, "D2")
        plan.slots.append(CompositeSlot(phase=phase, order=phase_order[phase],
                                        category=category, values=sv, tier=tier))

    # ═══ PHASE 1: Setting + Toss ═══
    _add(1, "setting_opening")

    # ═══ PHASE 2: First Innings - Early Overs ═══
    inn = inns[0] if inns else None
    if inn:
        # Opening pair
        openers = [b for b in inn.batters[:2]]
        opener_vals = {}
        for i, b in enumerate(openers):
            clean = _clean(b.name)
            opener_vals[f"opener{i+1}"] = clean
            opener_vals[f"opener{i+1}_runs"] = b.runs
            opener_vals[f"opener{i+1}_balls"] = b.balls
        _add(2, "innings_start", opener_vals)

        # Early wickets (FOW 1-3) with batter context
        for fow in inn.fow[:3]:
            batter = _find_batter_for_fow(inn, fow)
            bowler = _find_bowler_for_dismissal(inn, batter)
            fow_vals = {
                "batter": _clean(fow.batter), "runs": batter.runs if batter else 0,
                "balls": batter.balls if batter else 0, "fours": batter.fours if batter else 0,
                "bowler": _clean(bowler.name) if bowler else "a bowler",
                "fow_score": f"{fow.score}/{fow.wicket_num}",
                "wicket_num": _ordinal(fow.wicket_num),
            }
            _add(2, "wicket_fall", fow_vals)

    # ═══ PHASE 3: First Innings - Middle ═══
    if inn:
        # Key partnerships (runs >= 15)
        for pi, p in enumerate(inn.partnerships):
            if p.runs >= 15:
                parts = p.pair.split(" & ")
                prev_fow = inn.fow[pi-1] if pi > 0 and pi-1 < len(inn.fow) else None
                curr_fow = inn.fow[pi] if pi < len(inn.fow) else None
                part_vals = {
                    "batter1": parts[0] if len(parts) >= 1 else "",
                    "batter2": parts[1] if len(parts) >= 2 else "",
                    "runs1": _parse_contrib(p.striker), "runs2": _parse_contrib(p.non_striker),
                    "partnership_runs": p.runs,
                    "fow_before": f"{prev_fow.score}/{prev_fow.wicket_num}" if prev_fow else "",
                    "fow_after": f"{curr_fow.score}/{curr_fow.wicket_num}" if curr_fow else "",
                }
                _add(3, "partnership_build", part_vals)

        # Anchor batter (top scorer)
        scored = sorted([b for b in inn.batters if b.runs > 0], key=lambda b: b.runs, reverse=True)
        if scored and scored[0].runs >= 30:
            b = scored[0]
            _add(3, "anchor_batter", {
                "batter": _clean(b.name), "runs": b.runs, "balls": b.balls,
                "fours": b.fours, "sixes": b.sixes,
            })

        # Middle wickets (FOW 4-7)
        for fow in inn.fow[3:7]:
            batter = _find_batter_for_fow(inn, fow)
            bowler = _find_bowler_for_dismissal(inn, batter)
            _add(3, "wicket_fall", {
                "batter": _clean(fow.batter), "runs": batter.runs if batter else 0,
                "bowler": _clean(bowler.name) if bowler else "a bowler",
                "fow_score": f"{fow.score}/{fow.wicket_num}", "wicket_num": fow.wicket_num,
            })

    # ═══ PHASE 4: First Innings - Close ═══
    if inn:
        # Late wickets (FOW 8-10)
        for fow in inn.fow[7:]:
            batter = _find_batter_for_fow(inn, fow)
            _add(4, "tail_wicket", {
                "batter": _clean(fow.batter), "runs": batter.runs if batter else 0,
                "fow_score": f"{fow.score}/{fow.wicket_num}",
            })

        # Innings close
        _add(4, "innings_close", {
            "total_runs": inn.total_runs, "total_wickets": inn.total_wickets,
            "overs": inn.overs.replace(" Overs", "").strip(),
            "extras_total": inn.total_extras,
            "batting_runs": inn.batting_runs_sum,
        })

    # ═══ PHASE 5: Bowling Summary + Extras Accounting ═══
    if inn:
        # Best bowlers
        bwled = sorted([b for b in inn.bowlers if b.wickets >= 1],
                       key=lambda b: (b.wickets, -b.runs_conceded), reverse=True)
        bowl_vals = {}
        for rank, b in enumerate(bwled[:3]):
            bowl_vals[f"bowler{rank+1}"] = b.name
            bowl_vals[f"bowler{rank+1}_wkts"] = b.wickets
            bowl_vals[f"bowler{rank+1}_runs"] = b.runs_conceded
        _add(5, "bowling_summary", bowl_vals)

        # ★ EXTRAS ACCOUNTING (single composite sentence with ALL operands)
        _add(5, "extras_accounting", {
            "total_extras": inn.total_extras,
            "byes": inn.byes, "leg_byes": inn.leg_byes,
            "no_balls": inn.no_balls, "wides": inn.wides,
            "non_bowler_extras": inn.byes + inn.leg_byes,
            "bowling_runs_charged": inn.bowling_runs_charged,
            "batting_runs": inn.batting_runs_sum,
            "total_runs": inn.total_runs,
        })

    # ═══ PHASE 6-7: Second Innings (complete) ═══
    if len(inns) >= 2:
        inn2 = inns[1]
        target = inns[0].total_runs
        bowling_team_name = inns[0].name

        # Chase opening
        openers2 = [b for b in inn2.batters[:2]]
        _add(6, "chase_start", {
            "target": target, "opener1": _clean(openers2[0].name) if openers2 else "",
            "opener2": _clean(openers2[1].name) if len(openers2) > 1 else "",
            "bowling_team": bowling_team_name,
        })

        # ALL chase FOW entries
        for fow in inn2.fow:
            batter = _find_batter_for_fow(inn2, fow)
            bowler = _find_bowler_for_dismissal(inn2, batter)
            phase = 6 if fow.wicket_num <= 3 else 7
            _add(phase, "chase_wicket", {
                "batter": _clean(fow.batter), "runs": batter.runs if batter else 0,
                "bowler": _clean(bowler.name) if bowler else "a bowler",
                "fow_score": f"{fow.score}/{fow.wicket_num}", "target": target,
                "bowling_team": bowling_team_name,
            })

        # ALL chase partnerships
        for pi, p in enumerate(inn2.partnerships):
            if p.runs >= 10:
                parts = p.pair.split(" & ")
                prev_fow = inn2.fow[pi-1] if pi > 0 and pi-1 < len(inn2.fow) else None
                curr_fow = inn2.fow[pi] if pi < len(inn2.fow) else None
                _add(7, "chase_partnership", {
                    "batter1": parts[0] if len(parts) >= 1 else "",
                    "batter2": parts[1] if len(parts) >= 2 else "",
                    "runs1": _parse_contrib(p.striker), "runs2": _parse_contrib(p.non_striker),
                    "partnership_runs": p.runs,
                    "fow_before": f"{prev_fow.score}/{prev_fow.wicket_num}" if prev_fow else "",
                    "fow_after": f"{curr_fow.score}/{curr_fow.wicket_num}" if curr_fow else "",
                    "target": target,
                })

        # Chase anchor (top scorer in innings 2)
        scored2 = sorted([b for b in inn2.batters if b.runs > 0], key=lambda b: b.runs, reverse=True)
        if scored2 and scored2[0].runs >= 20:
            b = scored2[0]
            _add(7, "chase_anchor", {
                "batter": _clean(b.name), "runs": b.runs, "balls": b.balls,
                "fours": b.fours, "sixes": b.sixes, "target": target,
            })

        # Chase innings close + extras accounting
        _add(7, "chase_close", {
            "total_runs": inn2.total_runs, "total_wickets": inn2.total_wickets,
            "overs": inn2.overs.replace(" Overs", "").strip(),
            "extras_total": inn2.total_extras,
            "batting_runs": inn2.batting_runs_sum,
            "batting_team": inn2.name,
            "margin": md.result_margin, "target": target,
        })

        # Chase extras accounting
        _add(7, "extras_accounting", {
            "total_extras": inn2.total_extras,
            "byes": inn2.byes, "leg_byes": inn2.leg_byes,
            "no_balls": inn2.no_balls, "wides": inn2.wides,
            "non_bowler_extras": inn2.byes + inn2.leg_byes,
            "bowling_runs_charged": inn2.bowling_runs_charged,
            "batting_runs": inn2.batting_runs_sum,
            "total_runs": inn2.total_runs,
            "bowling_team": bowling_team_name,
        })

        # Also add bowling summary for defending team
        bwled2 = sorted([b for b in inn2.bowlers if b.wickets >= 1],
                        key=lambda b: (b.wickets, -b.runs_conceded), reverse=True)
        bowl2_vals = {"bowling_team": bowling_team_name}
        for rank, b in enumerate(bwled2[:3]):
            bowl2_vals[f"bowler{rank+1}"] = b.name
            bowl2_vals[f"bowler{rank+1}_wkts"] = b.wickets
            bowl2_vals[f"bowler{rank+1}_runs"] = b.runs_conceded
        _add(7, "bowling_summary", bowl2_vals)

        # ═══ PHASE 8: Result + POM ═══
        _add(8, "match_result", {
            "result": md.result, "margin": md.result_margin, "pom": md.player_of_match,
            "target": target,
        })

    plan.slots.sort(key=lambda s: (s.phase, s.order))
    return plan


def _build_base_values(md: MatchData, rng: random.Random) -> Dict[str, Any]:
    v = {}
    inns = md.innings
    inn1 = inns[0] if inns else None
    inn2 = inns[1] if len(inns) >= 2 else None

    v["venue"] = md.venue
    v["team1"] = inn1.name if inn1 else ""
    v["team2"] = inn2.name if inn2 else ""
    v["batting_team"] = inn1.name if inn1 else ""
    v["bowling_team"] = inn2.name if inn2 else ""
    v["toss_team"] = _extract_toss_team(md.toss)
    v["toss_decision"] = "bat" if "bat" in md.toss.lower() else "field"
    v["pom"] = md.player_of_match
    v["result"] = md.result
    v["margin"] = md.result_margin
    v["format"] = md.format_type

    # Narrative fillers
    v["outcome_hint"] = rng.choice([
        "would be tested before the result was settled",
        "proved more consequential than it first appeared",
    ])
    v["toss_reason"] = rng.choice([
        "the surface offered early help to the bowlers",
        "conditions looked good for chasing",
    ])
    v["chase_character"] = rng.choice(["controlled", "tested but never broken", "professional"])
    v["total_feeling"] = rng.choice([
        "defendable but not imposing", "probably short of par",
        "competitive without being match-winning",
    ])

    story = STORY_DESCRIPTORS.get(md.story_type, STORY_DESCRIPTORS["balanced"])
    for sk, sv in story.items():
        v[sk] = sv

    return v


def _clean(name: str) -> str:
    return re.sub(r'\s*\([^)]*\)', '', name).strip()


def _find_batter_for_fow(inn: InningsData, fow) -> Optional[BatterData]:
    clean = _clean(fow.batter)
    for b in inn.batters:
        if clean in _clean(b.name):
            return b
    return None


def _find_bowler_for_dismissal(inn: InningsData, batter: Optional[BatterData]) -> Optional[BowlerData]:
    """Find which bowler dismissed this batter (heuristic)."""
    if not batter:
        return None
    # Try to match dismissal text to bowler name
    for bw in inn.bowlers:
        if bw.name.split()[-1] in batter.dismissal:
            return bw
    return None  # don't fabricate attribution


def _parse_contrib(s: str) -> int:
    m = re.match(r"(\d+)", s)
    return int(m.group(1)) if m else 0


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13: return f"{n}th"
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    return f"{n}{suffixes.get(n % 10, 'th')}"


def _extract_toss_team(toss_str: str) -> str:
    m = re.match(r"(.+?)\s+won\s+the\s+[Tt]oss", toss_str)
    return m.group(1).strip() if m else ""
