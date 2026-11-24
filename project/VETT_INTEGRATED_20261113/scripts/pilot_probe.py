import sys, json, re, random
from pathlib import Path
from collections import Counter

ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
EXT = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches_extracted"
sys.path.insert(0, str(EXT))
from src.parser import parse_scorecard_full
from src.evidence_planner import build_evidence_map
from src.config import DifficultyConfig

d = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / "match_0001"
md = parse_scorecard_full((d/"scorecard.md").read_text(encoding="utf-8"), "match_0001")
comm = (d/"commentary.txt").read_text(encoding="utf-8").strip()
sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", comm) if s.strip()]
print("sentences:", len(sents))

# closure checks
for i, inn in enumerate(md.innings):
    bat = sum(b.runs for b in inn.batters)
    bowl = sum(b.runs_conceded for b in inn.bowlers)
    wkt = sum(b.wickets for b in inn.bowlers)
    print(f"inn{i+1}: bat_sum={bat} extras={inn.total_extras} total={inn.total_runs} -> {bat+inn.total_extras==inn.total_runs}")
    print(f"      extras {inn.byes}+{inn.leg_byes}+{inn.no_balls}+{inn.wides}={inn.byes+inn.leg_byes+inn.no_balls+inn.wides} -> {inn.byes+inn.leg_byes+inn.no_balls+inn.wides==inn.total_extras}")
    print(f"      bowl_runs={bowl} vs total-byes-lb={inn.total_runs-inn.byes-inn.leg_byes} -> {bowl==inn.total_runs-inn.byes-inn.leg_byes}")
    print(f"      wickets {wkt} vs {inn.total_wickets} -> {wkt==inn.total_wickets}")
    print(f"      fow last={inn.fow[-1].score if inn.fow else None} -> {inn.fow[-1].score==inn.total_runs if inn.fow else None}")

em = build_evidence_map(md, DifficultyConfig(), random.Random(0))
locatable, miss = [], []
for ev in em.items:
    val = str(ev.value)
    name = ev.player_name or ""
    hits = [s for s in sents if val in s]
    named = [s for s in hits if name and name in s] if name else hits
    if named or (not name and hits):
        locatable.append((ev.id, ev.field, val, len(hits), len(named)))
    else:
        miss.append((ev.id, ev.field, val, name, len(hits)))
print("\nevidence items:", len(em.items), "locatable:", len(locatable), "unlocated:", len(miss))
print("by level:", Counter(x.level for x in em.items))
print("\nfirst locatable:")
for x in locatable[:15]: print("  ", x)
print("\nfirst unlocated:")
for x in miss[:15]: print("  ", x)

# unique-value anchors: value appears in exactly one sentence, entity present
uniq = [x for x in locatable if x[3] == 1]
print("\nunique-sentence anchors:", len(uniq))
for x in uniq[:20]: print("  ", x)
