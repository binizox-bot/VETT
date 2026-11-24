import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
M=json.loads((P/"manifest.json").read_text(encoding="utf-8")); R=[json.loads(l) for l in (P/"runs"/"all.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
D=[]; T=[]
for r in R:
    if r["phase"]=="D":
        d=r.get("parsed") or {}; D.append((r["cond"],r["model"],eq(d.get("total_runs"),M["D"]["runs"]),eq(d.get("total_wickets"),M["D"]["wickets"])))
    else:
        f=r.get("fields") or r.get("parsed") or {}; g=next(x["gold"] for x in M["T"] if x["match"]==r["match"])
        ok=sum(1 for k in ["inn1.total_runs","inn1.total_wickets","inn2.total_runs","inn2.total_wickets"] if k in g and eq(f.get(k),g[k]))
        T.append((r["match"],r["model"],ok,4,r["parse_ok"]))
print("D",[(c,m.split(":")[0],a,b) for c,m,a,b in D])
print("D totals",{c:sum(1 for x in D if x[0]==c and x[2] and x[3]) for c in "OME"})
print("T",T)
print("T target",sum(x[2] for x in T),"/",sum(x[3] for x in T))
