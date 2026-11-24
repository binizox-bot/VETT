import sys, random, time
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
EXT = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches_extracted"
sys.path.insert(0, str(EXT))
from src.parser import parse_scorecard_full
from src.narrative_planner import plan_narrative
from src.linguistic_renderer import render_commentary
from src.config import MEDIUM_PROFILE

d = ROOT / "Self-cricket-clean_text_scorecard_v1_220_matches" / "match_0001"
md = parse_scorecard_full((d/"scorecard.md").read_text(encoding="utf-8"), "match_0001")
for seed in (0, 0, 1):
    t = time.time()
    rng = random.Random(seed)
    plan = plan_narrative(md, None, MEDIUM_PROFILE, rng)
    txt = render_commentary(plan, rng)
    print(f"seed={seed} chars={len(txt)} sents={txt.count('. ')} t={time.time()-t:.2f}s")
    print("   ", txt[:220].replace(chr(10), " "))
    print("   ...", txt[-220:].replace(chr(10), " "))
