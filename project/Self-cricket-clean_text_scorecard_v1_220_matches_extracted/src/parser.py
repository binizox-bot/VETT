"""Extended scorecard parser with derived computations and MatchData dataclass."""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path


@dataclass
class BatterData:
    name: str
    dismissal: str
    runs: int
    balls: int
    fours: int
    sixes: float  # can be "-" for DNB
    is_not_out: bool = False
    is_captain: bool = False
    is_wk: bool = False


@dataclass
class BowlerData:
    name: str
    overs: float
    maidens: int
    runs_conceded: int
    wickets: int
    econ: float
    wides: int
    noballs: int


@dataclass
class PartnershipData:
    pair: str
    runs: int
    extras: int
    striker: str
    non_striker: str
    overs: str
    end: str


@dataclass
class FOWData:
    wicket_num: int
    batter: str
    score: int
    at: str


@dataclass
class InningsData:
    name: str
    total_runs: int
    total_wickets: int
    overs: str
    byes: int = 0
    leg_byes: int = 0
    no_balls: int = 0
    wides: int = 0
    total_extras: int = 0
    run_rate: float = 0.0
    max_partnership: int = 0
    batters: List[BatterData] = field(default_factory=list)
    bowlers: List[BowlerData] = field(default_factory=list)
    partnerships: List[PartnershipData] = field(default_factory=list)
    fow: List[FOWData] = field(default_factory=list)

    # Derived fields (populated after parsing)
    batting_runs_sum: int = 0
    bowling_runs_sum: int = 0
    bowling_wickets_sum: int = 0
    bowling_overs_sum: float = 0.0
    bowling_runs_charged: int = 0  # total minus byes minus leg-byes
    extras_breakdown_sum: int = 0
    fow_chain_ok: bool = False
    player_contributions: Dict[str, int] = field(default_factory=dict)


@dataclass
class MatchData:
    match_id: str
    venue: str = ""
    toss: str = ""
    result: str = ""
    player_of_match: str = ""
    umpires: str = ""
    referee: str = ""
    innings: List[InningsData] = field(default_factory=list)
    format_type: str = "Unknown"  # ODI, T20, Other

    # Derived
    result_margin: str = ""
    result_type: str = ""  # "runs" or "wickets"
    story_type: str = ""


def _int_or(v, default=0):
    try: return int(v)
    except: return default


def _float_or(v, default=0.0):
    try: return float(v)
    except: return default


def parse_scorecard_full(text: str, match_id: str) -> MatchData:
    """Parse scorecard.md into a complete MatchData structure with all derived fields."""
    md = MatchData(match_id=match_id)

    # ── Match metadata ──
    meta_map = {
        "Venue": "venue", "Toss": "toss", "Result": "result",
        "Player of the Match": "player_of_match", "Umpires": "umpires", "Referee": "referee"
    }
    for label, attr in meta_map.items():
        m = re.search(rf"\|\s*{label}\s*\|\s*(.+?)\s*\|", text)
        if m:
            setattr(md, attr, m.group(1).strip())

    # ── Detect format ──
    md.format_type = _detect_format(text)

    # ── Find innings headers ──
    inn_headers = list(re.finditer(r"^##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)", text, re.MULTILINE))

    for idx, m in enumerate(inn_headers):
        start = m.start()
        end = inn_headers[idx+1].start() if idx+1 < len(inn_headers) else len(text)
        section = text[start:end]

        inn = InningsData(
            name=m.group(1).strip(),
            total_runs=int(m.group(2)),
            total_wickets=int(m.group(3)),
            overs=m.group(4).strip(),
        )

        # Extras
        for ef, attr in [("Byes", "byes"), ("Leg Byes", "leg_byes"), ("No Balls", "no_balls"),
                          ("Wides", "wides"), ("Total Extras", "total_extras")]:
            em = re.search(rf"\|\s*{ef}\s*\|\s*(\d+)", section)
            if em: setattr(inn, attr, int(em.group(1)))
        rm = re.search(r"\|\s*Run Rate\s*\|\s*([\d.]+)", section)
        if rm: inn.run_rate = _float_or(rm.group(1))
        mpm = re.search(r"\|\s*Max Partnership\s*\|\s*(\d+)", section)
        if mpm: inn.max_partnership = _int_or(mpm.group(1))

        # Batting
        bat_sec = re.search(r"###\s*Batting\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if bat_sec:
            for bl in bat_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) < 7 or cols[2] == "R": continue
                inn.batters.append(BatterData(
                    name=cols[0], dismissal=cols[1],
                    runs=_int_or(cols[2]), balls=_int_or(cols[3]),
                    fours=_int_or(cols[4]), sixes=_int_or(cols[5]),
                    is_not_out=("not out" in cols[1].lower()),
                    is_captain="(c)" in cols[0],
                    is_wk="(wk)" in cols[0],
                ))

        # Bowling
        bowl_sec = re.search(r"###\s*Bowling\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if bowl_sec:
            for bl in bowl_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) < 8 or cols[2] == "R": continue
                inn.bowlers.append(BowlerData(
                    name=cols[0], overs=_float_or(cols[1]),
                    maidens=_int_or(cols[2]), runs_conceded=_int_or(cols[3]),
                    wickets=_int_or(cols[4]), econ=_float_or(cols[5]),
                    wides=_int_or(cols[6]), noballs=_int_or(cols[7]),
                ))

        # Partnerships
        part_sec = re.search(r"###\s*Partnerships\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if part_sec:
            for pl in part_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in pl.split("|")[1:-1]]
                if len(cols) < 7 or cols[2] == "Extras": continue
                inn.partnerships.append(PartnershipData(
                    pair=cols[0], runs=_int_or(cols[1]), extras=_int_or(cols[2]),
                    striker=cols[3], non_striker=cols[4], overs=cols[5], end=cols[6],
                ))

        # FOW
        fow_sec = re.search(r"###\s*Fall of Wickets\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if fow_sec:
            for fl in fow_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in fl.split("|")[1:-1]]
                if len(cols) < 3: continue
                sm = re.match(r"(\d+)/", cols[2])
                inn.fow.append(FOWData(
                    wicket_num=_int_or(cols[0]), batter=cols[1],
                    score=_int_or(sm.group(1)) if sm else 0, at=cols[2],
                ))

        # ── Compute derived fields ──
        inn.batting_runs_sum = sum(b.runs for b in inn.batters)
        inn.bowling_runs_sum = sum(b.runs_conceded for b in inn.bowlers)
        inn.bowling_wickets_sum = sum(b.wickets for b in inn.bowlers)
        inn.bowling_overs_sum = sum(b.overs for b in inn.bowlers)
        inn.bowling_runs_charged = inn.total_runs - inn.byes - inn.leg_byes
        inn.extras_breakdown_sum = inn.byes + inn.leg_byes + inn.no_balls + inn.wides

        # FOW chain check
        expected_scores = []
        running = 0
        for p in inn.partnerships:
            running += p.runs
            expected_scores.append(running)
        actual_scores = [f.score for f in inn.fow]
        inn.fow_chain_ok = (expected_scores == actual_scores)

        # Player partnership contributions
        for b in inn.batters:
            total_from_parts = 0
            clean_name = re.sub(r'\s*\([^)]*\)', '', b.name).strip()
            for p in inn.partnerships:
                if clean_name in p.pair:
                    parts = p.pair.split(" & ")
                    sm = re.match(r"(\d+)", p.striker)
                    nsm = re.match(r"(\d+)", p.non_striker)
                    if len(parts) == 2 and sm and nsm:
                        if clean_name == parts[0]:
                            total_from_parts += int(sm.group(1))
                        else:
                            total_from_parts += int(nsm.group(1))
            if total_from_parts > 0:
                inn.player_contributions[clean_name] = total_from_parts

        md.innings.append(inn)

    # ── Cross-innings derivations ──
    if len(md.innings) >= 2:
        t1, t2 = md.innings[0].total_runs, md.innings[1].total_runs
        w2 = md.innings[1].total_wickets
        if t2 > t1:
            md.result_margin = f"{10 - w2} wickets"
            md.result_type = "wickets"
        elif t1 > t2:
            md.result_margin = f"{t1 - t2} runs"
            md.result_type = "runs"
        else:
            md.result_margin = "Tie"
            md.result_type = "tie"
    else:
        md.result_margin = "N/A (abandoned)"
        md.result_type = "abandoned"

    md.story_type = _classify_story(md)
    return md


def _detect_format(text: str) -> str:
    if re.search(r"50\.\d*\s*Overs?", text):
        return "ODI"
    if re.search(r"20\.\d*\s*Overs?", text):
        return "T20"
    overs = re.findall(r"\(([\d.]+)\s*Overs?\)", text)
    if overs:
        max_ov = max(float(o) for o in overs)
        if max_ov > 35: return "ODI"
        if max_ov <= 20: return "T20"
        return "Other"
    return "Unknown"


def _classify_story(md: MatchData) -> str:
    """Classify the match narrative type from scorecard structure."""
    inns = md.innings
    if len(inns) < 2:
        return "abandoned"

    inn1 = inns[0]
    inn2 = inns[1]
    margin_runs = abs(inn1.total_runs - inn2.total_runs)

    # Blowout
    if md.result_type == "runs" and margin_runs >= 100:
        return "bowling_rout" if inn2.total_runs < 100 else "dominant_bat"
    if md.result_type == "wickets" and (10 - inn2.total_wickets) >= 8:
        return "bowling_rout"

    # Close match
    is_close = False
    if md.result_type == "runs" and margin_runs <= 20: is_close = True
    if md.result_type == "wickets" and (10 - inn2.total_wickets) <= 3: is_close = True

    # Early collapse check
    early_collapse = False
    if inn1.fow and len(inn1.fow) >= 3:
        if inn1.fow[2].score < 50:
            early_collapse = True
    if inn2.fow and len(inn2.fow) >= 3:
        if inn2.fow[2].score < 50:
            early_collapse = True

    # Big partnership check
    has_big_stand = any(p.runs >= 80 for inn in inns for p in inn.partnerships)

    # Classify
    if early_collapse and has_big_stand:
        return "rescue_innings" if not is_close else "nail_biter"
    if early_collapse:
        return "collapse_defense"
    if is_close:
        return "nail_biter"
    if has_big_stand:
        return "partnership_match"
    if inn1.bowling_wickets_sum >= 9 and inn2.bowling_wickets_sum >= 8:
        return "bowling_rout"

    # Check for all-round POM
    pom = md.player_of_match
    all_round = False
    best_bat = max((b for inn in inns for b in inn.batters if b.runs > 20), key=lambda b: b.runs, default=None)
    best_bowl = max((b for inn in inns for b in inn.bowlers if b.wickets >= 2), key=lambda b: b.wickets, default=None)
    if best_bat and best_bowl:
        all_round = (pom.replace("(c)", "").replace("(wk)", "").strip() in best_bat.name and
                     pom.replace("(c)", "").replace("(wk)", "").strip() in best_bowl.name)

    if all_round: return "all_round_showcase"
    if inn2.total_wickets >= 6: return "chase_wobble"
    return "dominant_bat"
