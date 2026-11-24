import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_multidimensional_20261116"
def score(man,run):
    T={x["match"]:x for x in json.loads((P/man).read_text(encoding="utf-8"))}
    R=[json.loads(l) for l in (P/run).read_text(encoding="utf-8").splitlines() if l.strip()]
    def eq(a,b):
        try: return int(a)==int(b)
        except Exception: return False
    good=tot=tgt=tgtok=0
    for r in R:
        f=r.get("parsed") or {}; g=T[r["match"]]["gold"]
        for k,v in g.items():
            tot+=1; good+=eq(f.get(k),v) if isinstance(v,int) else str(f.get(k)).strip()==str(v).strip()
        for k in ["inn1.total_runs","inn1.total_wickets","inn2.total_runs","inn2.total_wickets"]:
            if k in g: tgt+=1; tgtok+=eq(f.get(k),g[k])
    return len(R),good,tot,tgtok,tgt
x=score("A_DEV3_MANIFEST.json","RUNS/a_dev3.jsonl")
print("dev3",x)
print("combined",48+x[0],572+x[1],1632+x[2],168+x[3],186+x[4])
