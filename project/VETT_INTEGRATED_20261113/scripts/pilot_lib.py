"""Pilot-10 construction library: fields, closure, deterministic variants."""
from __future__ import annotations

import copy
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
EXT = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches_extracted"
DATASET = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches"
OUT = ROOT / "VETT_INTEGRATED_20261113"

import sys
sys.path.insert(0, str(EXT))
from src.parser import parse_scorecard_full, MatchData  # noqa: E402
from src.narrative_planner import plan_narrative  # noqa: E402
from src.linguistic_renderer import render_commentary  # noqa: E402
from src.config import MEDIUM_PROFILE  # noqa: E402


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def render(md: MatchData, seed: int = 0) -> str:
    rng = random.Random(seed)
    plan = plan_narrative(md, None, MEDIUM_PROFILE, rng)
    return render_commentary(plan, rng)


def target_roster(md: MatchData) -> dict:
    """Fix which batters/bowlers are graded, so mutation cannot change field ids."""
    r = {}
    for i, inn in enumerate(md.innings, 1):
        r[f"inn{i}"] = {
            "batters": [b.name for b in sorted(inn.batters, key=lambda b: b.runs, reverse=True)[:3]],
            "bowlers": [b.name for b in sorted(inn.bowlers, key=lambda b: (b.wickets, -b.runs_conceded), reverse=True)[:2]],
        }
    return r


def target_fields(md: MatchData, roster: dict | None = None) -> dict:
    """~52 gradeable fields derived only from structured match data."""
    f = {}
    def add(fid, value, table, row, col, level, deps=None):
        f[fid] = {"value": value, "table": table, "row": row, "col": col,
                  "level": level, "depends_on": deps or []}

    add("match.venue", md.venue, "match", "-", "venue", "L1")
    add("match.toss", md.toss, "match", "-", "toss", "L1")
    add("match.result", md.result, "match", "-", "result", "L1")
    add("match.pom", md.player_of_match, "match", "-", "pom", "L1")
    add("match.result_type", md.result_type, "match", "-", "result_type", "L2")

    for i, inn in enumerate(md.innings, 1):
        p = f"inn{i}"
        add(f"{p}.team", inn.name, p, "-", "team", "L1")
        add(f"{p}.total_runs", inn.total_runs, p, "-", "total", "L1")
        add(f"{p}.total_wickets", inn.total_wickets, p, "-", "wickets", "L1")
        add(f"{p}.overs", inn.overs, p, "-", "overs", "L1")
        add(f"{p}.total_extras", inn.total_extras, p, "-", "extras", "L1")
        add(f"{p}.byes", inn.byes, p, "-", "byes", "L2", [f"{p}.total_extras"])
        add(f"{p}.leg_byes", inn.leg_byes, p, "-", "leg_byes", "L2", [f"{p}.total_extras"])
        add(f"{p}.no_balls", inn.no_balls, p, "-", "no_balls", "L2", [f"{p}.total_extras"])
        add(f"{p}.wides", inn.wides, p, "-", "wides", "L2", [f"{p}.total_extras"])
        bat_sum = sum(b.runs for b in inn.batters)
        bowl_runs = sum(b.runs_conceded for b in inn.bowlers)
        add(f"{p}.batting_runs_sum", bat_sum, p, "-", "bat_sum", "L2", [f"{p}.total_runs"])
        add(f"{p}.bowling_runs_charged", bowl_runs, p, "-", "bowl_runs", "L2", [f"{p}.total_runs"])
        add(f"{p}.max_partnership", inn.max_partnership, p, "-", "max_partnership", "L2")
        add(f"{p}.fow_count", len(inn.fow), p, "-", "fow_count", "L2")

        names_b = (roster or {}).get(p, {}).get("batters") or [b.name for b in sorted(inn.batters, key=lambda b: b.runs, reverse=True)[:3]]
        by_name = {b.name: b for b in inn.batters}
        for r, name in enumerate(names_b, 1):
            b = by_name.get(name)
            if b is None:
                continue
            add(f"{p}.bat{r}_{b.name}.runs", b.runs, p, b.name, "R", "L1" if r == 1 else "L2")
        names_w = (roster or {}).get(p, {}).get("bowlers") or [b.name for b in sorted(inn.bowlers, key=lambda b: (b.wickets, -b.runs_conceded), reverse=True)[:2]]
        bow_by_name = {b.name: b for b in inn.bowlers}
        for r, name in enumerate(names_w, 1):
            b = bow_by_name.get(name)
            if b is None:
                continue
            add(f"{p}.bowl{r}_{b.name}.figures", f"{b.wickets}/{b.runs_conceded}", p, b.name, "figures", "L2")
            add(f"{p}.bowl{r}_{b.name}.runs_conceded", b.runs_conceded, p, b.name, "R", "L2")
            add(f"{p}.bowl{r}_{b.name}.wides", b.wides, p, b.name, "Wd", "L2", [f"{p}.wides"])
    return f


def closure(md: MatchData) -> list[dict]:
    cs = []
    def add(cid, formula, lhs, rhs, ok):
        cs.append({"id": cid, "formula": formula, "lhs": lhs, "rhs": rhs, "ok": bool(ok)})
    for i, inn in enumerate(md.innings, 1):
        p = f"inn{i}"
        bat = sum(b.runs for b in inn.batters)
        bowl = sum(b.runs_conceded for b in inn.bowlers)
        wk = sum(b.wickets for b in inn.bowlers)
        add(f"{p}.bat_plus_extras", "batting_runs_sum + total_extras == total_runs",
            bat + inn.total_extras, inn.total_runs, bat + inn.total_extras == inn.total_runs)
        add(f"{p}.extras_parts", "byes+leg_byes+no_balls+wides == total_extras",
            inn.byes + inn.leg_byes + inn.no_balls + inn.wides, inn.total_extras,
            inn.byes + inn.leg_byes + inn.no_balls + inn.wides == inn.total_extras)
        add(f"{p}.bowling_recon", "sum(bowler.runs_conceded) == total_runs - byes - leg_byes",
            bowl, inn.total_runs - inn.byes - inn.leg_byes,
            bowl == inn.total_runs - inn.byes - inn.leg_byes)
        runouts = sum(1 for b in inn.batters if "run out" in (b.dismissal or "").lower())
        add(f"{p}.wicket_sum", "sum(bowler.wickets) + run_outs == total_wickets",
            wk + runouts, inn.total_wickets, wk + runouts == inn.total_wickets)
        if inn.fow:
            add(f"{p}.fow_monotone", "fow scores non-decreasing and <= total",
                [x.score for x in inn.fow],
                inn.total_runs,
                all(inn.fow[j].score <= inn.fow[j+1].score for j in range(len(inn.fow)-1))
                and inn.fow[-1].score <= inn.total_runs)
    return cs


def mutate_extras_swap(md: MatchData, delta: int = 2) -> tuple[MatchData, dict]:
    """Move runs from wides to byes for one innings; total and extras unchanged.

    Also reduces the widest bowler's conceded runs and wides by delta so the
    bowling reconciliation stays true.
    """
    m = copy.deepcopy(md)
    chosen = None
    for inn in m.innings:
        if inn.wides >= delta + 1 and inn.byes + delta <= inn.total_extras:
            bowler = max(inn.bowlers, key=lambda b: b.wides)
            if bowler.wides >= delta:
                chosen = (inn, bowler)
                break
    if not chosen:
        return m, {"applied": False}
    inn, bowler = chosen
    before = {"inn.wides": inn.wides, "inn.byes": inn.byes,
              "bowler": bowler.name, "bowler.wides": bowler.wides,
              "bowler.runs_conceded": bowler.runs_conceded}
    inn.wides -= delta
    inn.byes += delta
    bowler.wides -= delta
    bowler.runs_conceded -= delta
    after = {"inn.wides": inn.wides, "inn.byes": inn.byes,
             "bowler": bowler.name, "bowler.wides": bowler.wides,
             "bowler.runs_conceded": bowler.runs_conceded}
    return m, {"applied": True, "delta": delta, "innings": inn.name,
               "before": before, "after": after}


def split_blocks(text: str) -> list[list[str]]:
    """Two blocks (innings) split near the chase intro; returns sentence list."""
    s = sentences(text)
    if len(s) < 8:
        return [s]
    mid = len(s) // 2
    return [s[:mid], s[mid:]]


def shuffle_sentences(text: str, seed: int = 7) -> str:
    blocks = split_blocks(text)
    rng = random.Random(seed)
    out = []
    for bi, block in enumerate(blocks):
        if len(block) <= 4:
            out.extend(block)
            continue
        head, mid, tail = block[:2], block[2:-2], block[-2:]
        rng.shuffle(mid)
        out.extend(head + mid + tail)
    return " ".join(out)


def find_extras_sentence(text: str) -> str | None:
    for s in sentences(text):
        low = s.lower()
        if ("sundries" in low or "extras" in low) and ("wide" in low or "bye" in low):
            return s
    return None


def mentioned(text: str, fid: str, value) -> bool:
    v = str(value)
    low = text.lower()
    suffix = fid.split(".")[-1]
    patterns = []
    if suffix == "wides":
        patterns = [rf"\b{re.escape(v)}\s+wides?\b"]
    elif suffix == "byes":
        patterns = [rf"\b{re.escape(v)}\s+byes?\b"]
    elif suffix == "leg_byes":
        patterns = [rf"\b{re.escape(v)}\s+leg[- ]byes?\b"]
    elif suffix == "no_balls":
        patterns = [rf"\b{re.escape(v)}\s+no[- ]balls?\b"]
    elif suffix == "total_extras":
        patterns = [rf"\b{re.escape(v)}\s+extras?\b", rf"sundries column read {re.escape(v)}\b"]
    elif suffix == "total_runs":
        patterns = [rf"\b{re.escape(v)}\s+all out\b", rf"\b{re.escape(v)}/\d", rf"reached {re.escape(v)}\b"]
    if patterns:
        return any(re.search(p, low) for p in patterns)
    return v.lower() in low


def mutate_bowler_wickets(md: MatchData, delta: int = 1) -> tuple[MatchData, dict]:
    """Move one wicket between bowlers: team total, extras and runs are unchanged.

    This revision is NOT recoverable by the accounting closure, so it separates
    real re-extraction from closure-driven repair.
    """
    m = copy.deepcopy(md)
    for inn in m.innings:
        if len(inn.bowlers) < 2:
            continue
        top = max(inn.bowlers, key=lambda b: (b.wickets, -b.runs_conceded))
        others = [b for b in inn.bowlers if b.name != top.name and b.wickets >= delta]
        if not others:
            continue
        src = max(others, key=lambda b: b.wickets)
        before = {"top": top.name, "top_w": top.wickets, "src": src.name, "src_w": src.wickets}
        top.wickets += delta
        src.wickets -= delta
        return m, {"applied": True, "innings": inn.name, "delta": delta,
                   "before": before,
                   "after": {"top_w": top.wickets, "src_w": src.wickets}}
    return m, {"applied": False}


def build_variants(md: MatchData, seed: int = 0) -> dict:
    base = render(md, seed)
    roster = target_roster(md)
    gold = target_fields(md, roster)
    variants = {}

    variants["control"] = {"text": base, "gold": gold, "edit": {"type": "none"}}

    variants["shuffled"] = {"text": shuffle_sentences(base, seed + 1), "gold": gold,
                            "edit": {"type": "shuffle", "scope": "within-innings-sentence-order"}}

    m2, log = mutate_extras_swap(md, 2)
    if log.get("applied"):
        t2 = render(m2, seed)
        g2 = target_fields(m2, roster)
        changed = sorted(k for k in gold if gold[k]["value"] != g2[k]["value"])
        variants["revised"] = {"text": t2, "gold": g2,
                               "edit": {"type": "extras_swap", **log},
                               "changed_fields": changed,
                               "unchanged_fields": sorted(k for k in gold if k not in changed)}
    else:
        variants["revised"] = {"text": base, "gold": gold, "edit": {"type": "unavailable"}}

    # conflict: lower-authority note contradicts the extras total
    inn = md.innings[0]
    note = (f"An unofficial club note filed after the match listed the first-innings extras "
            f"as {inn.total_extras + 3}, but it was not signed by either umpire.")
    variants["conflict"] = {"text": base + " " + note, "gold": gold,
                            "edit": {"type": "conflict_note", "authority": "unofficial",
                                     "asserted_value": inn.total_extras + 3,
                                     "true_value": inn.total_extras}}

    # missing: delete the extras breakdown sentence
    ex = find_extras_sentence(base)
    if ex:
        remaining = base.replace(ex, "").strip()
        unknown = [k for k, meta in gold.items()
                   if mentioned(base, k, meta["value"])
                   and not mentioned(remaining, k, meta["value"])]
        variants["missing"] = {"text": remaining, "gold": gold,
                               "edit": {"type": "delete_sentence", "deleted": ex},
                               "unknown_fields": unknown}
    else:
        variants["missing"] = {"text": base, "gold": gold, "edit": {"type": "unavailable_no_extras_sentence"}}

    distractor = ("In an earlier fixture at the same ground, a different side had made 168 for 6 "
                  "after being 44 for 3, with the ninth-wicket pair adding 61.")
    variants["distractor"] = {"text": base + " " + distractor, "gold": gold,
                              "edit": {"type": "insert_distractor"}}

    # inline_revision: a later official correction supersedes an earlier fact.
    # This is the versioned-ledger probe: the old value is still present in the text.
    def base_name(n: str) -> str:
        return re.sub(r"\s*\([^)]*\)", "", n).strip().lower()
    all_bat = [b for inn in md.innings for b in inn.batters]
    alt = None
    pom_base = base_name(md.player_of_match)
    for b in sorted(all_bat, key=lambda x: x.runs, reverse=True):
        if base_name(b.name) != pom_base:
            alt = b.name
            break
    if alt:
        note = (f"Scorers' correction issued after the match: the Player of the Match award "
                f"was reassigned from {md.player_of_match} to {alt}.")
        g_rev = copy.deepcopy(gold)
        g_rev["match.pom"]["value"] = alt
        variants["revision_inline"] = {
            "text": base + " " + note, "gold": g_rev,
            "edit": {"type": "inline_revision", "field": "match.pom",
                     "old": md.player_of_match, "new": alt, "authority": "official correction"},
            "changed_fields": ["match.pom"],
            "unchanged_fields": sorted(k for k in gold if k != "match.pom"),
        }
    else:
        variants["revision_inline"] = {"text": base, "gold": gold, "edit": {"type": "unavailable"}}

    m3, log3 = mutate_bowler_wickets(md, 1)
    if log3.get("applied"):
        t3 = render(m3, seed)
        g3 = target_fields(m3, roster)
        changed3 = sorted(k for k in gold if gold[k]["value"] != g3[k]["value"])
        variants["revised_hard"] = {"text": t3, "gold": g3,
                                    "edit": {"type": "wicket_transfer", **log3},
                                    "changed_fields": changed3,
                                    "unchanged_fields": sorted(k for k in gold if k not in changed3)}
    else:
        variants["revised_hard"] = {"text": base, "gold": gold, "edit": {"type": "unavailable"}}
    return variants


def leak_check(text: str, gold: dict) -> list[str]:
    bad = []
    for token in ("gold", "answer_key", "correct_answer", "record_gold"):
        if token in text.lower():
            bad.append(token)
    return bad
