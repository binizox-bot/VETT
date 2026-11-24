import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_multidimensional_20261116"
M=json.loads((P/"B_MIN_MANIFEST.json").read_text(encoding="utf-8"))
R=[json.loads(l) for l in (P/"RUNS"/"b_min.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
per={}
for r in R:
    s=next(x for x in M if x["match"]==r["match"] and x["cond"]==r["cond"]); d=r.get("parsed") or {}
    per.setdefault(r["cond"],[]).append(eq(d.get("total_runs"),s["runs"]) and eq(d.get("total_wickets"),s["wickets"]))
for c in ["O","P","L","E","WI","WIC","OI","OIC"]:
    x=per.get(c,[]); print(c,len(x),sum(x))
print("rows",len(R),"both",sum(sum(v) for v in per.values()))
