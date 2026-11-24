import sys,json
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
S={s["match"]:s for s in json.loads((Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117").parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
c=V.connect()
top={}
for r in c.execute("SELECT r.match,r.model,r.cond,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership'"):
    p=json.loads(r[3] or "{}"); top[(r[0],r[1],r[2].replace("T2_",""))]=p.get("bowlers")
def norm(x): return str(x).strip().lower()
hits=defaultdict(list)
for r in c.execute("SELECT r.match,r.model,r.cond,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable'"):
    m,mod,cond,parsed=r; s=S.get(m); 
    if not s or not cond.endswith("_fulltable"): continue
    arm=cond.split("_")[0]
    if arm not in ("N0","N1","N2"): continue
    tb=top.get((m,mod,arm))
    if not tb: continue
    gold=[s["A"],s["B"]]
    if set(map(norm,tb))!=set(map(norm,gold)): continue
    p=json.loads(parsed or "{}"); p=p.get("fields",p) if isinstance(p,dict) else {}
    inn=int(str(s["innings"]).replace("inn","")); pre="inn"+str(inn)
    rows=[p.get(pre+".bowl1_name"),p.get(pre+".bowl2_name")]
    if set(map(norm,[x for x in rows if x]))!=set(map(norm,gold)):
        hits[m].append((MS[mod],arm,rows,gold))
print("ROOTS",sorted(hits))
for m,v in hits.items():
    print(m,len(v),v)
c.close()
