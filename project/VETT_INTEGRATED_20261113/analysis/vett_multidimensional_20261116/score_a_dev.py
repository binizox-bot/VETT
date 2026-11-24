import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_multidimensional_20261116"
T={x["match"]:x for x in json.loads((P/"A_DEV_MANIFEST.json").read_text(encoding="utf-8"))}
R=[json.loads(l) for l in (P/"RUNS"/"a_dev.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
tot=0; good=0; cell=0; cellok=0; tgt=0; tgtok=0
for r in R:
    f=r.get("fields") or r.get("parsed") or {}; g=T[r["match"]]["gold"]
    for k,v in g.items():
        tot+=1; ok=False
        if isinstance(v,int): ok=eq(f.get(k),v)
        else: ok=str(f.get(k)).strip()==str(v).strip()
        good+=ok; cell+=1; cellok+=ok
    for k in ["inn1.total_runs","inn1.total_wickets","inn2.total_runs","inn2.total_wickets"]:
        tgt+=1; tgtok+=eq(f.get(k),g[k])
print("rows",len(R),"full",good,"/",tot,"target",tgtok,"/",tgt)
for model in ["qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"]:
    rr=[r for r in R if r["model"]==model]; print(model,"rows",len(rr),"parse",sum(1 for r in rr if r["parse_ok"]))
