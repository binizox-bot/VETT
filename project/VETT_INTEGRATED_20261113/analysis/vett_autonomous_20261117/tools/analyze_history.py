
import sys, json, collections
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT / "VETT_INTEGRATED_20261113"
sys.path.insert(0, str(INT / "scripts"))
import pilot_lib as L

u = INT / "analysis" / "vett_overnight_20261114" / "runs" / "u_full.jsonl"
rows = [json.loads(l) for l in u.read_text(encoding="utf-8").splitlines() if l.strip()]
gold = {}
def get_gold(m, i):
    key = (m, i)
    if key in gold: return gold[key]
    md = L.parse_scorecard_full((L.DATASET / m / "scorecard.md").read_text(encoding="utf-8"), m)
    if i < 1 or i > len(md.innings): return None
    inn = md.innings[i-1]
    g = {"total_runs": inn.total_runs, "total_wickets": inn.total_wickets, "team": inn.name}
    gold[key] = g
    return g

def val(x):
    if isinstance(x, dict): x = x.get("value")
    try: return int(str(x).strip())
    except Exception: return None

pos = collections.defaultdict(lambda: {"n":0, "runs":0, "wk":0, "both":0, "models":[], "team":""})
for r in rows:
    m, i = r.get("match"), r.get("innings")
    if not m or i is None: continue
    g = get_gold(m, int(i))
    if not g: continue
    p = r.get("parsed") or {}
    if not isinstance(p, dict): p = {}
    okr = val(p.get("total_runs")) == g["total_runs"]
    okw = val(p.get("total_wickets")) == g["total_wickets"]
    d = pos[(m, int(i))]
    d["n"] += 1; d["runs"] += int(okr); d["wk"] += int(okw); d["both"] += int(okr and okw)
    d["team"] = g["team"]
    d["models"].append({"model": r.get("model"), "ok": bool(okr and okw), "runs": okr, "wk": okw})

ranked = sorted(pos.items(), key=lambda kv: (kv[1]["both"], kv[1]["runs"]+kv[1]["wk"], kv[0]))
hard = [{"match":k[0], "innings":k[1], **{kk:vv for kk,vv in v.items() if kk!="models"}, "model_fail": [x["model"] for x in v["models"] if not x["ok"]]} for k,v in ranked if v["both"] <= 1][:12]
easy = [{"match":k[0], "innings":k[1], **{kk:vv for kk,vv in v.items() if kk!="models"}} for k,v in ranked if v["both"] >= 3][:8]
print("hard_count", sum(1 for _,v in ranked if v["both"]<=1), "of", len(ranked))
print("hard", json.dumps(hard, ensure_ascii=False, indent=1)[:2600])
print("easy", json.dumps(easy, ensure_ascii=False, indent=1)[:1200])
out = {"u_rows": len(rows), "positions": len(pos), "hard": hard, "easy": easy}
(Path(__file__).parent / "history_analysis.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote")
