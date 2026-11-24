import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
T={x["match"]:x for x in json.loads((P/"t_locator_manifest.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"runs"/"t_locator.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
ok=n=0
for r in R:
    t=T[r["match"]]; f=r.get("fields") or r.get("parsed") or {}; g=t["gold"]
    for k in ["inn1.total_runs","inn1.total_wickets","inn2.total_runs","inn2.total_wickets"]:
        n+=1; ok+=eq(f.get(k),g[k])
print("T locator",ok,"/",n,"rows",len(R))
