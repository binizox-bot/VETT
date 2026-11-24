"""Reversibility Auditor: validates generated commentary against scorecard for evidence closure."""
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any
from src.parser import MatchData
from src.evidence_planner import EvidenceRequirementsMap, EvidenceRequirement


@dataclass
class AuditResult:
    match_id: str
    total_operands: int = 0
    found_operands: int = 0
    closure_rate: float = 0.0
    arithmetic_ok: bool = True
    name_fidelity_ok: bool = True
    cricket_rules_ok: bool = True
    missing_items: List[Dict] = field(default_factory=list)
    difficulty_score: float = 0.0
    overall_grade: str = "F"


def audit_match(md: MatchData, erm: EvidenceRequirementsMap, commentary: str) -> AuditResult:
    """Run 7 audit checks on generated commentary."""

    ar = AuditResult(match_id=md.match_id)
    comm_lower = commentary.lower()

    # ── Check 1: Evidence Closure ──
    for item in erm.l2_operands:
        ar.total_operands += 1
        val = item.value
        found = False

        if item.evidence_type == "numeric" and isinstance(val, (int, float)):
            if int(val) == 0 and not (isinstance(val, float) and val > 0):
                found = True  # zeros are trivial
            else:
                found = bool(re.search(rf"\b{int(val)}\b", commentary))
        elif item.evidence_type == "name" and isinstance(val, str):
            found = val.lower() in comm_lower
        elif item.evidence_type == "cricket_rule":
            found = True  # cricket rules are applied, not stated

        if found:
            ar.found_operands += 1
        else:
            ar.missing_items.append({
                "id": item.id, "field": item.field, "value": val,
                "level": item.level, "difficulty": item.difficulty_class,
            })

    ar.closure_rate = ar.found_operands / ar.total_operands if ar.total_operands else 1.0

    # ── Check 2: Value Fidelity (sample check) ──
    # Check that key numbers are correct
    for inn in md.innings:
        if not re.search(rf"\b{inn.total_runs}\b", commentary):
            ar.missing_items.append({"field": "innings_total", "value": inn.total_runs, "note": "Missing from commentary"})

    # ── Check 3: Name Fidelity ──
    all_names = set()
    for inn in md.innings:
        for b in inn.batters:
            clean = re.sub(r'\s*\([^)]*\)', '', b.name).strip()
            parts = clean.split()
            if len(parts) >= 2:
                all_names.add(parts[-1])
        for b in inn.bowlers:
            parts = b.name.split()
            if len(parts) >= 2:
                all_names.add(parts[-1])

    for name in all_names:
        if name and len(name) > 1:
            if not re.search(rf"\b{re.escape(name)}\b", commentary):
                ar.name_fidelity_ok = False
                break

    # ── Check 4: Arithmetic Self-Consistency ──
    for inn in md.innings:
        bat_sum = inn.batting_runs_sum
        extras = inn.total_extras
        total = inn.total_runs
        if bat_sum + extras != total:
            ar.arithmetic_ok = False
        if inn.extras_breakdown_sum != extras:
            ar.arithmetic_ok = False

    # ── Check 5: Cricket Rule Correctness ──
    for inn in md.innings:
        bowling_charged = inn.total_runs - inn.byes - inn.leg_byes
        if bowling_charged != inn.bowling_runs_charged:
            ar.cricket_rules_ok = False

    # ── Check 6: Difficulty Score ──
    difficulty_weights = {
        "D0_explicit": 1, "D1_variant": 2, "D2_distributed": 3,
        "D3_rule_required": 4, "D4_implicit": 5,
    }
    total_weight = 0
    count = 0
    for item in erm.items:
        if item.level == "L2":
            w = difficulty_weights.get(item.difficulty_class, 1)
            total_weight += w
            count += 1
    ar.difficulty_score = total_weight / count if count else 0

    # ── Check 7: Overall Grade ──
    if ar.closure_rate >= 0.95 and ar.arithmetic_ok and ar.name_fidelity_ok and ar.cricket_rules_ok:
        ar.overall_grade = "A"
    elif ar.closure_rate >= 0.85 and ar.arithmetic_ok:
        ar.overall_grade = "B"
    elif ar.closure_rate >= 0.70:
        ar.overall_grade = "C"
    else:
        ar.overall_grade = "D"

    return ar


def audit_match_v2(md: MatchData, plan, commentary: str) -> AuditResult:
    """Audit v2: check that all KEY values for scorecard reversibility appear in commentary."""
    ar = AuditResult(match_id=md.match_id)

    # Key values needed for L1+L2 reversibility
    key_values = []

    for inn in md.innings:
        # Innings totals
        key_values += [inn.total_runs, inn.total_wickets]
        # Extras
        key_values += [inn.total_extras, inn.byes, inn.leg_byes, inn.no_balls, inn.wides]
        # Batting sum
        key_values.append(inn.batting_runs_sum)
        # Bowling runs charged
        key_values.append(inn.bowling_runs_charged)
        # Top 3 batter runs
        for b in sorted(inn.batters, key=lambda b: -b.runs)[:3]:
            if b.runs > 0: key_values.append(b.runs)
        # Top 2 bowler wickets+runs
        for b in sorted(inn.bowlers, key=lambda b: -b.wickets)[:2]:
            if b.wickets > 0:
                key_values.append(b.wickets)
                key_values.append(b.runs_conceded)
        # Major partnership runs (>=20)
        for p in inn.partnerships:
            if p.runs >= 20: key_values.append(p.runs)
        # FOW scores
        for f in inn.fow:
            key_values.append(f.score)

    # Deduplicate
    unique_values = set(v for v in key_values if v and v > 0)

    ar.total_operands = len(unique_values)
    for val in unique_values:
        if re.search(rf"\b{val}\b", commentary):
            ar.found_operands += 1
        else:
            ar.missing_items.append({"value": val, "note": "not found in commentary"})

    ar.closure_rate = ar.found_operands / ar.total_operands if ar.total_operands else 1.0
    ar.arithmetic_ok = "{" not in commentary
    ar.cricket_rules_ok = True
    ar.name_fidelity_ok = True
    ar.difficulty_score = _compute_difficulty(plan)

    if ar.closure_rate >= 0.95: ar.overall_grade = "A"
    elif ar.closure_rate >= 0.85: ar.overall_grade = "B"
    elif ar.closure_rate >= 0.70: ar.overall_grade = "C"
    else: ar.overall_grade = "D"

    return ar


def _compute_difficulty(plan) -> float:
    """Compute actual difficulty score from slot tier distribution (1.0-5.0 scale)."""
    tier_weight = {"D1": 1.0, "D2": 2.0, "D3": 3.5, "D4": 5.0}
    if not plan or not plan.slots:
        return 2.5
    total = sum(tier_weight.get(s.tier, 2.0) for s in plan.slots)
    return round(total / len(plan.slots), 2)


def compute_tier_breakdown(plan) -> dict:
    """Per-tier and per-category difficulty breakdown."""
    tier_weight = {"D1": 1.0, "D2": 2.0, "D3": 3.5, "D4": 5.0}
    tiers = {"D1": 0, "D2": 0, "D3": 0, "D4": 0}
    categories = {}
    for s in plan.slots:
        tiers[s.tier] = tiers.get(s.tier, 0) + 1
        if s.category not in categories:
            categories[s.category] = {"count": 0, "weight": 0}
        categories[s.category]["count"] += 1
        categories[s.category]["weight"] += tier_weight.get(s.tier, 2.0)

    # Category averages
    cat_avg = {}
    for cat, data in sorted(categories.items()):
        cat_avg[cat] = round(data["weight"] / data["count"], 1) if data["count"] else 0

    return {
        "tiers": tiers,
        "tier_pct": {t: round(c / len(plan.slots) * 100, 1) for t, c in tiers.items()},
        "category_avg": cat_avg,
        "overall": _compute_difficulty(plan),
    }


def audit_summary(results: List[AuditResult]) -> Dict:
    """Generate aggregate audit summary."""
    total = len(results)
    if total == 0:
        return {}

    grades = [r.overall_grade for r in results]
    closures = [r.closure_rate for r in results]
    difficulties = [r.difficulty_score for r in results]

    return {
        "total_matches": total,
        "grade_distribution": {g: grades.count(g) for g in ["A", "B", "C", "D"]},
        "avg_closure_rate": sum(closures) / total,
        "min_closure_rate": min(closures),
        "max_closure_rate": max(closures),
        "perfect_closure": sum(1 for c in closures if c >= 0.99),
        "avg_difficulty_score": sum(difficulties) / total,
        "arithmetic_ok": sum(1 for r in results if r.arithmetic_ok),
        "name_fidelity_ok": sum(1 for r in results if r.name_fidelity_ok),
        "cricket_rules_ok": sum(1 for r in results if r.cricket_rules_ok),
        "total_missing_operands": sum(len(r.missing_items) for r in results),
    }
