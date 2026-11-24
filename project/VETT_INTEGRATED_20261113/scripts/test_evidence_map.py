import sys, json, random
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches_extracted"))
from src.parser import parse_scorecard_full
from src.evidence_planner import build_evidence_map
from src.config import DifficultyConfig

d = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / "match_0001"
md = parse_scorecard_full((d/"scorecard.md").read_text(encoding="utf-8"), "match_0001")
print("innings:", len(md.innings), "result:", md.result, "type:", md.result_type)
for i, inn in enumerate(md.innings):
    print(f"  inn{i+1}: {inn.name} {inn.total_runs}/{inn.total_wickets} bat={len(inn.batters)} bowl={len(inn.bowlers)} fow={len(inn.fow)}")
try:
    cfg = DifficultyConfig()
except Exception as e:
    print("cfg default err", e)
    cfg = DifficultyConfig(level="D2")
em = build_evidence_map(md, cfg, random.Random(0))
from collections import Counter
print("evidence items:", len(em.items), "levels:", Counter(x.level for x in em.items))
print("by difficulty:", Counter(x.difficulty_class for x in em.items))
for x in em.items[:6]:
    print(" ", x.id, x.level, x.field, "=", x.value, "| op_of:", x.operand_of, "| phase", x.placement_phase)
