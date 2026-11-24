import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_multidimensional_20261116"
T={x["match"]:x for x in json.loads((P/"A_DEV2_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"RUNS"/"a_dev2.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
good=tot=tgt=tgtok=0
for r in R:
    f=r.get("parsed") or {}; g=T[r["match"]]["gold"]
    for k,v in g.items():
        tot+=1; ok=eq(f.get(k),v) if isinstance(v,int) else str(f.get(k)).strip()==str(v).strip(); good+=ok
    for k in ["inn1.total_runs","inn1.total_wickets","inn2.total_runs","inn2.total_wickets"]:
        if k in g: tgt+=1; tgtok+=eq(f.get(k),g[k])
print("rows",len(R),"full",good,"/",tot,"target",tgtok,"/",tgt)
