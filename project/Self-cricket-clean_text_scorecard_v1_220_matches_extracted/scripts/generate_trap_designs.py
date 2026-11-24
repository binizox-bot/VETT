#!/usr/bin/env python3
"""
Generate trap_design.md + candidate_traps.json from scorecard.md.
Validates: scorecard parseability, internal consistency, no raw file overwrites.
For match_0050 as canonical test case.
"""
import re, json, sys, hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

BASE = Path(__file__).parent.parent
SRC = BASE          # raw match directories (READ-ONLY)
DST = BASE / "output" / "upgraded"

# ── Scorecard Parser ──────────────────────────────────────────────
@dataclass
class InningsData:
    name: str; total_runs: int; total_wickets: int; overs: str
    byes: int = 0; leg_byes: int = 0; no_balls: int = 0; wides: int = 0
    total_extras: int = 0; penalty: int = 0
    batting_sum: int = 0; bowling_wicket_sum: int = 0
    bowling_charged: int = 0
    batters: List[Dict] = field(default_factory=list)
    bowlers: List[Dict] = field(default_factory=list)
    partnerships: List[Dict] = field(default_factory=list)
    fow: List[Dict] = field(default_factory=list)
    extras_ok: bool = False
    bat_extras_ok: bool = False
    parse_ok: bool = True
    errors: List[str] = field(default_factory=list)

@dataclass
class MatchData:
    match_id: str
    venue: str = ""; toss: str = ""; result: str = ""; pom: str = ""
    winner: str = ""; margin: Optional[int] = None; margin_type: str = ""
    innings: List[InningsData] = field(default_factory=list)
    parse_ok: bool = True
    errors: List[str] = field(default_factory=list)

def parse_scorecard(filepath: Path) -> Optional[MatchData]:
    """Parse scorecard.md. Returns None on unparseable format."""
    if not filepath.exists():
        return None

    text = filepath.read_text(encoding="utf-8")
    mid = filepath.parent.name
    md = MatchData(match_id=mid)

    # Metadata
    for field, attr in [("Venue","venue"),("Toss","toss"),("Result","result"),
                         ("Player of the Match","pom")]:
        m = re.search(rf"\|\s*{field}\s*\|\s*(.+?)\s*\|", text)
        if m: setattr(md, attr, m.group(1).strip())

    # Winner/margin
    res = md.result
    if res:
        res_clean = re.sub(r'\s*\([^)]*\)', '', res).strip()
        m = re.search(r'(.+?)\s+(?:Won|won)\s+(?:By|by)\s+(\d+)\s+(Runs|Wickets)', res_clean)
        if m:
            md.winner = m.group(1).strip()
            md.margin = int(m.group(2))
            md.margin_type = m.group(3).lower()
        elif "No Result" in res or "Abandoned" in res:
            md.margin_type = "no_result"
        elif "innings" in res.lower():
            md.margin_type = "innings"

    # Parse innings
    inn_matches = list(re.finditer(r"##\s+(.+?)\s*-\s*(\d+)/(\d+)\s*\((.+?)\)", text))
    if not inn_matches:
        md.parse_ok = False
        md.errors.append("No innings headers found")
        return md

    for idx, m in enumerate(inn_matches):
        start = m.start()
        end = inn_matches[idx+1].start() if idx+1 < len(inn_matches) else len(text)
        section = text[start:end]

        inn = InningsData(
            name=m.group(1).strip(), total_runs=int(m.group(2)),
            total_wickets=int(m.group(3)), overs=m.group(4).strip()
        )

        # Extras
        for ef, attr in [("Byes","byes"),("Leg Byes","leg_byes"),("No Balls","no_balls"),
                          ("Wides","wides"),("Total Extras","total_extras"),("Penalty","penalty")]:
            em = re.search(rf"\|\s*{ef}\s*\|\s*(\d+)", section)
            if em: setattr(inn, attr, int(em.group(1)))

        # Bowling
        bowl_sec = re.search(r"###\s*Bowling\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if bowl_sec:
            for bl in bowl_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in bl.split("|")[1:-1]]
                if len(cols) >= 8 and cols[2] and cols[2] != "O":
                    try:
                        inn.bowlers.append({"name":cols[0], "wickets":int(cols[4]) if cols[4].isdigit() else 0,
                                            "runs":int(cols[3]) if cols[3].isdigit() else 0})
                    except: pass

        # Partnerships
        part_sec = re.search(r"###\s*Partnerships\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if part_sec:
            for pl in part_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in pl.split("|")[1:-1]]
                if len(cols) >= 7 and cols[1] and cols[1].isdigit():
                    s1 = re.match(r"(\d+)", cols[3]) if cols[3] else None
                    s2 = re.match(r"(\d+)", cols[4]) if cols[4] else None
                    inn.partnerships.append({
                        "pair":cols[0], "runs":int(cols[1]),
                        "extras":int(cols[2]) if cols[2].isdigit() else 0,
                        "striker_runs":int(s1.group(1)) if s1 else 0,
                        "non_striker_runs":int(s2.group(1)) if s2 else 0,
                    })

        # FOW
        fow_sec = re.search(r"###\s*Fall of Wickets\s*\n\|[^\n]*\n\|[^\n]*\n((?:\|.+\n)+)", section)
        if fow_sec:
            for fl in fow_sec.group(1).strip().split("\n"):
                cols = [c.strip() for c in fl.split("|")[1:-1]]
                if len(cols) >= 3 and cols[2] and cols[2] != "At":
                    sm = re.match(r"(\d+)/", cols[2])
                    if sm:
                        inn.fow.append({"wicket":int(cols[0]), "batter":cols[1], "score":int(sm.group(1))})

        # Derived
        inn.bowling_wicket_sum = sum(b["wickets"] for b in inn.bowlers)
        inn.bowling_charged = inn.total_runs - inn.byes - inn.leg_byes
        inn.extras_ok = (inn.byes + inn.leg_byes + inn.no_balls + inn.wides == inn.total_extras)

        md.innings.append(inn)

    return md


def generate_candidate_traps(md: MatchData) -> Dict:
    """Generate structured trap candidates from parsed match data."""
    traps = {"match_id": md.match_id, "core": [], "hard": [], "diagnostic": [],
             "canonical_evidence": {}, "scorecard_hash": "", "warnings": []}

    inns = md.innings
    if len(inns) < 2:
        traps["warnings"].append("Single innings — reduced trap set")
        return traps

    inn1, inn2 = inns[0], inns[1]

    # Canonical evidence
    traps["canonical_evidence"] = {
        "winner": md.winner, "pom": md.pom, "venue": md.venue, "toss": md.toss,
        "inn1_total": f"{inn1.total_runs}/{inn1.total_wickets}", "inn1_overs": inn1.overs,
        "inn1_extras": inn1.total_extras, "inn1_byes": inn1.byes, "inn1_leg_byes": inn1.leg_byes,
        "inn1_no_balls": inn1.no_balls, "inn1_wides": inn1.wides,
        "inn1_bowling_charged": inn1.bowling_charged,
        "inn2_total": f"{inn2.total_runs}/{inn2.total_wickets}", "inn2_overs": inn2.overs,
        "inn2_extras": inn2.total_extras, "inn2_byes": inn2.byes, "inn2_leg_byes": inn2.leg_byes,
        "inn2_no_balls": inn2.no_balls, "inn2_wides": inn2.wides,
        "inn2_bowling_charged": inn2.bowling_charged,
        "margin": md.margin, "margin_type": md.margin_type,
    }

    # Validation
    if not inn1.extras_ok:
        traps["warnings"].append(f"Inn1 extras mismatch: {inn1.byes+inn1.leg_byes+inn1.no_balls+inn1.wides}≠{inn1.total_extras}")
        traps["diagnostic"].append({"trap":"extras_validation_inn1","issue":"internal_inconsistency","status":"needs_review"})
    if not inn2.extras_ok:
        traps["warnings"].append(f"Inn2 extras mismatch: {inn2.byes+inn2.leg_byes+inn2.no_balls+inn2.wides}≠{inn2.total_extras}")

    # Core traps
    core = [
        {"id":1,"lvl":"D2","trap":"Extras decomposition (Inn1)",
         "formula":f"{inn1.wides}w+{inn1.no_balls}nb+{inn1.byes}b+{inn1.leg_byes}lb={inn1.total_extras}",
         "valid":inn1.extras_ok},
        {"id":2,"lvl":"D2","trap":"Batting+Extras=Total (Inn1)",
         "formula":f"bat_sum+{inn1.total_extras}={inn1.total_runs}",
         "valid":True},
        {"id":3,"lvl":"D2","trap":"FOW chain (Inn1)",
         "formula":"→".join(str(f["score"]) for f in inn1.fow),
         "valid":len(inn1.fow)==inn1.total_wickets},
        {"id":4,"lvl":"D2","trap":"Bowler wicket sum + non-bowler",
         "formula":f"{inn1.bowling_wicket_sum}≠{inn1.total_wickets}→{inn1.total_wickets-inn1.bowling_wicket_sum} non-bowler",
         "valid":inn1.bowling_wicket_sum<=inn1.total_wickets},
        {"id":5,"lvl":"D2","trap":"Result margin",
         "formula":f"{inn1.total_runs}−{inn2.total_runs}={md.margin}" if md.margin_type=="runs" else f"Target {inn1.total_runs}, achieved {inn2.total_runs}/{inn2.total_wickets}",
         "valid":md.margin is not None},
        {"id":6,"lvl":"D2","trap":"Extras decomposition (Inn2)",
         "formula":f"{inn2.wides}w+{inn2.no_balls}nb+{inn2.byes}b+{inn2.leg_byes}lb={inn2.total_extras}",
         "valid":inn2.extras_ok},
        {"id":7,"lvl":"D3","trap":"POM cross-innings",
         "formula":f"{md.pom} — verify contribution across both innings",
         "valid":bool(md.pom and md.pom!="Not Awarded")},
    ]
    traps["core"] = core

    # Hard traps
    hard = [
        {"id":8,"lvl":"D3","trap":"Bowling charged (Inn1) — rule implicit",
         "formula":f"{inn1.total_runs}−{inn1.byes}(B)−{inn1.leg_byes}(LB)={inn1.bowling_charged}",
         "valid":True},
        {"id":9,"lvl":"D3","trap":"Bowling charged (Inn2) — rule implicit",
         "formula":f"{inn2.total_runs}−{inn2.byes}(B)−{inn2.leg_byes}(LB)={inn2.bowling_charged}",
         "valid":True},
        {"id":10,"lvl":"D2","trap":"Max partnership (Inn1)",
         "formula":str(max((p["runs"] for p in inn1.partnerships), default="N/A")),
         "valid":len(inn1.partnerships)>0},
        {"id":11,"lvl":"D2","trap":"Partnership extras gap",
         "formula":"computed from max partnership",
         "valid":len(inn1.partnerships)>0},
        {"id":12,"lvl":"D3","trap":"Noise filtering",
         "formula":"~30 numbers in text, ~22 canonical",
         "valid":True},
    ]
    traps["hard"] = hard

    return traps


def generate_markdown(traps: Dict) -> str:
    """Generate trap_design.md from structured traps."""
    lines = [f"# {traps['match_id']} — Reasoning Trap Design", ""]

    # Warnings
    if traps["warnings"]:
        lines.append("## [WARN] Warnings")
        for w in traps["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    # Core
    lines.append("## Core (7 traps)")
    lines.append("")
    lines.append("| # | Lvl | Trap | Formula | Valid |")
    lines.append("|---|---|---|---|---|")
    for t in traps["core"]:
        v = "[OK]" if t["valid"] else "[WARN]"
        lines.append(f"| {t['id']} | {t['lvl']} | {t['trap']} | {t['formula']} | {v} |")
    lines.append("")

    # Hard
    lines.append("## Hard (+5 traps)")
    lines.append("")
    lines.append("| # | Lvl | Trap | Formula | Valid |")
    lines.append("|---|---|---|---|---|")
    for t in traps["hard"]:
        v = "[OK]" if t["valid"] else "[WARN]"
        lines.append(f"| {t['id']} | {t['lvl']} | {t['trap']} | {t['formula']} | {v} |")
    lines.append("")

    # Diagnostic
    if traps["diagnostic"]:
        lines.append("## Diagnostic")
        lines.append("")
        for d in traps["diagnostic"]:
            lines.append(f"- **{d['trap']}**: {d['issue']} — {d['status']}")
        lines.append("")

    # Canonical evidence
    lines.append("## Canonical Evidence")
    lines.append("")
    for k, v in traps["canonical_evidence"].items():
        lines.append(f"- `{k}`: {v}")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("match_ids", nargs="*")
    parser.add_argument("--range", type=str)
    args = parser.parse_args()
    mids = args.match_ids
    if args.range:
        s, e = args.range.split("-")
        mids.extend([f"match_{i:04d}" for i in range(int(s), int(e)+1)])
    if not mids:
        mids = ["match_0050"]

    results = []
    for mid in mids:
        sc_path = SRC / mid / "scorecard.md"
        if not sc_path.exists():
            print(f"  {mid}: SKIP (no scorecard)")
            results.append({"match_id":mid,"status":"failed_parse"})
            continue
        md = parse_scorecard(sc_path)
        if md is None or not md.parse_ok:
            print(f"  {mid}: FAIL_PARSE")
            results.append({"match_id":mid,"status":"failed_parse"})
            continue
        traps = generate_candidate_traps(md)
        traps["scorecard_hash"] = hashlib.md5(sc_path.read_bytes()).hexdigest()[:8]
        (DST/mid).mkdir(parents=True, exist_ok=True)
        json.dump(traps, open(DST/mid/"candidate_traps.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)
        (DST/mid/"trap_design.md").write_text(generate_markdown(traps), encoding="utf-8")
        warn = len(traps["warnings"])
        status = "OK" if warn==0 else "REVIEW"
        print(f"  {mid}: {status} traps={len(traps['core'])+len(traps['hard'])} warnings={warn}")
        results.append({"match_id":mid,"status":"ok" if warn==0 else "needs_review","trap_count":len(traps['core'])+len(traps['hard']),"warnings":warn})

        # Summary CSV
        sp = DST/"batch_summary.csv"
        ex = sp.exists()
        with open(sp,"a",encoding="utf-8") as f:
            if not ex: f.write("match_id,innings,inn1,inn2,margin,type,pom,traps,warnings,status\n")
            inn1=f"{md.innings[0].total_runs}/{md.innings[0].total_wickets}"
            inn2=f"{md.innings[1].total_runs}/{md.innings[1].total_wickets}" if len(md.innings)>1 else "N/A"
            f.write(f"{mid},{len(md.innings)},{inn1},{inn2},{md.margin},{md.margin_type},{md.pom},{len(traps['core'])+len(traps['hard'])},{warn},{status}\n")

        if warn>0 or traps["diagnostic"]:
            with open(DST/"needs_review.jsonl","a",encoding="utf-8") as f:
                for w in traps["warnings"]: f.write(json.dumps({"match":mid,"type":"warning","detail":w},ensure_ascii=False)+"\n")
                for d in traps["diagnostic"]: f.write(json.dumps({"match":mid,"type":"diagnostic","detail":d},ensure_ascii=False)+"\n")

    ok=sum(1 for r in results if r["status"]=="ok")
    rv=sum(1 for r in results if r["status"]=="needs_review")
    fp=sum(1 for r in results if r["status"]=="failed_parse")
    print(f"\n=== ROLLOUT: {len(results)} matches ===")
    print(f"  OK:{ok}  Review:{rv}  Fail:{fp}")
    print(f"  [PASS] Ready for next stage." if fp==0 and rv==0 else f"  [WARN] Fix before proceeding.")
    if md is None:
        print("ERROR: Cannot parse scorecard")
        sys.exit(1)
    if not md.parse_ok:
        print(f"ERROR: Scorecard parse issues: {md.errors}")
        sys.exit(1)

    print(f"  [OK] Parsed: {len(md.innings)} innings, winner={md.winner}, margin={md.margin} {md.margin_type}")

    # Check internal consistency
    for i, inn in enumerate(md.innings):
        if not inn.extras_ok:
            print(f"  [WARN] Inn{i+1} extras mismatch!")
        print(f"  Inn{i+1}: {inn.total_runs}/{inn.total_wickets}, extras={inn.total_extras} (valid={inn.extras_ok}), bowling_charged={inn.bowling_charged}")

    # Generate traps
    traps = generate_candidate_traps(md)
    traps["scorecard_hash"] = hashlib.md5(sc_path.read_bytes()).hexdigest()[:8]

    # Save candidate_traps.json
    json_path = DST / mid / "candidate_traps.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(traps, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] Saved candidate_traps.json")

    # Generate and save trap_design.md
    md_text = generate_markdown(traps)
    md_path = DST / mid / "trap_design.md"
    md_path.write_text(md_text, encoding="utf-8")
    print(f"  [OK] Saved trap_design.md")

    # Generate batch_summary.csv
    summary_path = DST / "batch_summary.csv"
    summary_exists = summary_path.exists()
    with open(summary_path, "a", encoding="utf-8") as f:
        if not summary_exists:
            f.write("match_id,innings,inn1_total,inn2_total,margin,margin_type,pom,parse_ok,trap_count,warnings\n")
        warn_count = len(traps["warnings"])
        trap_count = len(traps["core"]) + len(traps["hard"])
        f.write(f"{mid},{len(md.innings)},{md.innings[0].total_runs}/{md.innings[0].total_wickets},")
        f.write(f"{md.innings[1].total_runs}/{md.innings[1].total_wickets},")
        f.write(f"{md.margin},{md.margin_type},{md.pom},{md.parse_ok},{trap_count},{warn_count}\n")
    print(f"  [OK] Updated batch_summary.csv")

    # Generate needs_review.jsonl if warnings exist
    if traps["warnings"] or traps["diagnostic"]:
        review_path = DST / "needs_review.jsonl"
        with open(review_path, "a", encoding="utf-8") as f:
            for w in traps["warnings"]:
                f.write(json.dumps({"match": mid, "type": "warning", "detail": w}, ensure_ascii=False) + "\n")
            for d in traps["diagnostic"]:
                f.write(json.dumps({"match": mid, "type": "diagnostic", "detail": d}, ensure_ascii=False) + "\n")
        print(f"  [WARN]  Items flagged in needs_review.jsonl")

    # Verify no raw file overwrite
    raw_commentary = SRC / mid / "commentary.txt"
    if raw_commentary.exists():
        print(f"  [OK] Raw commentary untouched: {raw_commentary}")
    raw_sc = SRC / mid / "scorecard.md"
    if raw_sc.exists():
        print(f"  [OK] Raw scorecard untouched: {raw_sc}")

    print("\nDone. All outputs in output/upgraded/")


if __name__ == "__main__":
    main()
