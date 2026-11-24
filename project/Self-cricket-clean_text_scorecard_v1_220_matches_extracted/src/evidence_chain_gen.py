"""Evidence Chain Generator: produces standardized Gen4 evidence_chain.md from the NarrativePlan."""
from src.parser import MatchData
from src.evidence_planner import EvidenceRequirementsMap
from src.narrative_planner import NarrativePlan, CompositeSlot


def generate_evidence_chain_v2(md: MatchData, plan: NarrativePlan) -> str:
    """Generate evidence chain from composite slots."""
    lines = []
    lines.append("| Level | Field / Target | Reasoning Type | Required Operands | Evidence Location |")
    lines.append("| --- | --- | --- | --- | --- |")

    inns = md.innings

    # L1: Direct extraction
    l1_items = [
        ("Match result", md.result, "direct_extraction", ""),
        ("Player of the Match", md.player_of_match, "direct_extraction", ""),
        ("Toss decision", md.toss, "direct_extraction", ""),
        ("Venue", md.venue, "direct_extraction", ""),
    ]
    for i, inn in enumerate(inns):
        pfx = f"Innings {i+1}"
        l1_items.append((f"{pfx} total", f"{inn.total_runs}/{inn.total_wickets} ({inn.overs})", "direct_extraction", ""))
        scored = sorted([b for b in inn.batters if b.runs > 0], key=lambda b: b.runs, reverse=True)
        for rank, b in enumerate(scored[:3]):
            l1_items.append((f"{pfx} top batter {rank+1}", f"{b.name} {b.runs}", "direct_extraction", ""))
        bowled = sorted([b for b in inn.bowlers if b.wickets >= 1], key=lambda b: (b.wickets, -b.runs_conceded), reverse=True)
        for rank, b in enumerate(bowled[:2]):
            l1_items.append((f"{pfx} best bowler {rank+1}", f"{b.name} {b.wickets}/{b.runs_conceded}", "direct_extraction", ""))
        if inn.partnerships:
            mp = max(inn.partnerships, key=lambda p: p.runs)
            l1_items.append((f"{pfx} max partnership", f"{mp.pair} {mp.runs}", "direct_extraction", ""))

    for field, target, rtype, operands in l1_items:
        lines.append(f"| L1 | {field} | {rtype} | {operands} | Phases 1-8 |")

    # L2: Arithmetic + cricket rule
    for i, inn in enumerate(inns):
        pfx = f"Innings {i+1}"
        lines.append(f"| L2 | {pfx} total validation | arithmetic | bat={inn.batting_runs_sum} + extras={inn.total_extras} = {inn.total_runs} | Phase 4-5 |")
        lines.append(f"| L2 | {pfx} extras breakdown | arithmetic | byes={inn.byes} + lb={inn.leg_byes} + nb={inn.no_balls} + wides={inn.wides} = {inn.total_extras} | Phase 5 |")
        lines.append(f"| L2 | {pfx} bowling reconciliation | cricket_rule | {inn.total_runs} - {inn.byes}(b) - {inn.leg_byes}(lb) = {inn.bowling_runs_charged} (charged to bowlers) | Phase 5 |")
        lines.append(f"| L2 | {pfx} wicket sum | multi_hop | bowl_w={inn.bowling_wickets_sum}, total_w={inn.total_wickets} | Phases 2-5 |")
        fow_chain = " → ".join(str(f.score) for f in inn.fow)
        lines.append(f"| L2 | {pfx} FOW chain | multi_hop | {fow_chain} | Phases 2-4 |")

    if md.result_type == "runs" and len(inns) >= 2:
        lines.append(f"| L2 | Result margin | arithmetic | {inns[0].total_runs} - {inns[1].total_runs} = {md.result_margin} | Phase 7-8 |")
    elif md.result_type == "wickets" and len(inns) >= 2:
        lines.append(f"| L2 | Result margin (chase) | cricket_rule | target={inns[0].total_runs}, chased with {10 - inns[1].total_wickets} wickets left | Phase 7-8 |")

    # L3: Narrative synthesis
    l3_items = [
        ("Match narrative inference", "phase synthesis", "Toss → innings structure → partnerships → chase evolution → result"),
        ("POM justification", "cross-phase reading", f"{md.player_of_match} — performance evaluated across both innings"),
        ("Hidden evidence design", "distributed operands", "Batting scores, bowling figures, and extras distributed across narrative phases rather than listed"),
        ("Cricket rule inference", "rule application", "Byes and leg-byes excluded from bowling runs; partnership accumulation; chase margin logic"),
        ("Numerical reasoning requirement", "multi-hop arithmetic", "Batting sum, extras sum, FOW chain, and bowling reconciliation all require addition/subtraction across distributed operands"),
    ]
    for field, rtype, operands in l3_items:
        lines.append(f"| L3 | {field} | {rtype} | {operands} | Phases 1-8 |")

    return "\n".join(lines) + "\n"


def generate_evidence_chain(md: MatchData, erm: EvidenceRequirementsMap,
                            plan: NarrativePlan) -> str:
    """Generate a complete evidence_chain.md in Gen4 standardized format."""
    lines = []
    lines.append("| Level | Field / Target | Reasoning Type | Required Operands | Evidence Location |")
    lines.append("| --- | --- | --- | --- | --- |")

    inns = md.innings

    # ── L1: Direct Extraction (~15 items) ──
    l1_items = [
        ("Match winner", md.result, "direct_extraction", "", "Phase 8"),
        ("Player of the Match", md.player_of_match, "direct_extraction", "", "Phase 8"),
        ("Toss decision", md.toss, "direct_extraction", "", "Phase 1"),
        ("Venue", md.venue, "direct_extraction", "", "Phase 1"),
    ]

    for i, inn in enumerate(inns):
        pfx = f"Innings {i+1}"
        l1_items.append((f"{pfx} total", f"{inn.total_runs}/{inn.total_wickets} ({inn.overs})",
                         "direct_extraction", "", f"Phase {2+i*4}"))
        batters = sorted([b for b in inn.batters if b.runs > 0], key=lambda b: b.runs, reverse=True)
        for rank, b in enumerate(batters[:3]):
            l1_items.append((f"{pfx} top batter {rank+1}", f"{b.name} {b.runs}",
                             "direct_extraction", "", f"Phase {2+i*4}"))
        bowlers = sorted([b for b in inn.bowlers if b.wickets >= 1], key=lambda b: (b.wickets, -b.runs_conceded), reverse=True)
        for rank, b in enumerate(bowlers[:2]):
            l1_items.append((f"{pfx} best bowler {rank+1}", f"{b.name} {b.wickets}/{b.runs_conceded}",
                             "direct_extraction", "", f"Phase {2+i*4}"))
        if inn.partnerships:
            mp = max(inn.partnerships, key=lambda p: p.runs)
            l1_items.append((f"{pfx} max partnership", f"{mp.pair} {mp.runs}",
                             "direct_extraction", "", f"Phase {2+i*4}"))

    for field, target, rtype, operands, location in l1_items:
        lines.append(f"| L1 | {field} | {rtype} | {operands} | {location} |")

    # ── L2: Arithmetic + Cricket Rule (~20 items) ──
    for i, inn in enumerate(inns):
        pfx = f"Innings {i+1}"

        # Total validation
        lines.append(f"| L2 | {pfx} total validation | arithmetic | batting_runs={inn.batting_runs_sum}, extras={inn.total_extras}, total={inn.total_runs} | Phases {2+i*4}-{3+i*4} |")

        # Bowling reconciliation
        lines.append(f"| L2 | {pfx} bowling reconciliation | cricket_rule | total={inn.total_runs}, byes={inn.byes}, leg_byes={inn.leg_byes}, charged={inn.bowling_runs_charged} | Phase {3+i*4} |")

        # Extras breakdown
        lines.append(f"| L2 | {pfx} extras breakdown | arithmetic | byes={inn.byes}, lb={inn.leg_byes}, nb={inn.no_balls}, wides={inn.wides}, total={inn.total_extras} | Phase {3+i*4} |")

        # Wicket sum
        lines.append(f"| L2 | {pfx} wicket sum | multi_hop | bowl_w={inn.bowling_wickets_sum}, total_w={inn.total_wickets} | Phases {2+i*4}-{3+i*4} |")

        # FOW chain
        fow_scores = [str(f.score) for f in inn.fow]
        lines.append(f"| L2 | {pfx} FOW chain | multi_hop | {' → '.join(fow_scores)} | Phases {2+i*4}-{4+i*4} |")

        # Overs validation
        lines.append(f"| L2 | {pfx} overs validation | arithmetic | bowl_overs={inn.bowling_overs_sum:.1f}, stated={inn.overs} | Phase {3+i*4} |")

        # Player contribution tracking for top players
        for name, contrib in sorted(inn.player_contributions.items(), key=lambda x: -x[1])[:3]:
            if contrib >= 20:
                lines.append(f"| L2 | {name} contribution tracking | multi_hop | sum of partnership contributions = {contrib} | Phases {2+i*4}-{4+i*4} |")

    # Result margin
    if md.result_margin and md.result_type != "abandoned":
        lines.append(f"| L2 | Result margin validation | cricket_rule | margin={md.result_margin}, type={md.result_type} | Phase 8 |")

    # ── L3: Narrative Synthesis (~12 items) ──
    l3_items = [
        ("Match narrative inference", "phase synthesis",
         "Toss → innings structure → chase evolution → result", "Phases 1-8"),
        ("Innings structure inference", "partnership + FOW reading",
         "How partnerships shaped the innings arc", "Phases 2-4"),
        ("Chase interpretation", "contextual reading",
         "Why the chase succeeded/failed through FOW timing and partnership context", "Phases 6-8"),
        ("POM justification", "cross-phase reading",
         f"{md.player_of_match} — contribution analyzed across both innings phases", "Phases 5, 8"),
        ("Bowling pressure inference", "economy + wickets synthesis",
         "Bowling impact through combined figures and timing of wickets", "Phase 5"),
        ("Chase pressure inference", "FOW + asking rate synthesis",
         "How pressure accumulated through wickets and required rate", "Phases 6-7"),
        ("Hidden evidence design", "inferential reading",
         "Core fields embedded through match phases and pressure shifts", "Phases 1-8"),
        ("Text-table synchronization", "commentary-scorecard verification",
         "All commentary-named facts match scorecard table values", "Phases 1-8"),
        ("Scorecard-fingerprint reduction", "anti-reidentification",
         "Original match identity obscured through systematic numeric redesign", "All phases"),
        ("Secondary anonymization safety", "cross-field redesign",
         "Teams, venue, players, totals, partnerships, FOW, and textual anchors rekeyed", "All phases"),
        ("Lower-order contribution inference", "late FOW + tail resistance",
         "How lower order affected final total", "Phases 4, 7"),
        (f"Format awareness ({md.format_type})", "format-specific reading",
         f"Match interpreted with {md.format_type}-specific tempo and phase emphasis", "Phases 1-8"),
    ]

    for field, rtype, operands, location in l3_items:
        lines.append(f"| L3 | {field} | {rtype} | {operands} | {location} |")

    return "\n".join(lines) + "\n"
