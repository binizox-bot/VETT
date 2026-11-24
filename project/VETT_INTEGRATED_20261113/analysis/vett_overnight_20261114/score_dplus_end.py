import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
M=json.loads((P/"dplus_end_manifest.json").read_text(encoding="utf-8"))
R=[json.loads(l) for l in (P/"runs"/"dplus_end.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
per={}
for r in R:
    s=next(x for x in M if x["match"]==r["match"]); d=r.get("parsed") or {}
    per[(r["match"],r["model"])]=eq(d.get("total_runs"),s["runs"]) and eq(d.get("total_wickets"),s["wickets"])
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rows=[v for k,v in per.items() if k[1]==model]; print(model,sum(rows),"/",len(rows))
print("total",sum(per.values()),"/",len(per))
