import sys,json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"vett_evidence_upgrade_20261115"; O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
P=INT/"analysis"/"vett_overnight_20261114"
R=[json.loads(l) for l in (P/"runs"/"u_full.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
cache={}
def get(m,inn):
    if m not in cache:
        md=L.parse_scorecard_full((L.DATASET/m/"scorecard.md").read_text(encoding="utf-8"),m); cache[m]=md
    return cache[m].innings[inn-1]
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
groups={"both":0,"runs_only":0,"wk_only":0,"neither":0}; parse={"service":len(R),"response":0,"json":0,"scorable":0}
per_pos={}
for r in R:
    inn=get(r["match"],r["innings"]); d=r.get("parsed") or {}
    parse["response"]+=1 if r.get("raw_output") else 0
    parse["json"]+=1 if r.get("parse_ok") else 0
    def v(k):
        x=d.get(k) or {}; return x.get("value") if isinstance(x,dict) else None
    okr=eq(v("total_runs"),inn.total_runs); okw=eq(v("total_wickets"),inn.total_wickets)
    g="both" if okr and okw else "runs_only" if okr else "wk_only" if okw else "neither"; groups[g]+=1
    per_pos.setdefault((r["match"],r["innings"]),[]).append((r["model"],g,okr,okw))
parse["scorable"]=sum(1 for r in R if r.get("parse_ok"))
positions=sorted(per_pos); roots=sorted({m for m,i in positions})
missing=[]
for i in range(1,221):
    m=f"match_{i:04d}"
    for inn in (1,2):
        if (m,inn) not in per_pos: missing.append((m,inn))
out={"parse":parse,"groups":groups,"positions":len(positions),"roots":len(roots),"missing":missing}
(O/"U_RECALC.json").write_text(json.dumps(out,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
# T paired new 6
B={}
for r in [json.loads(l) for l in (P/"runs"/"t_expand.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]:
    B[(r["match"],r["model"])]=r.get("fields") or r.get("parsed") or {}
Lc={}
for r in [json.loads(l) for l in (P/"runs"/"t_expand_locator.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]:
    Lc[(r["match"],r["model"])]=r.get("fields") or r.get("parsed") or {}
T=json.loads((P/"t_expand_manifest.json").read_text(encoding="utf-8")); G={x["match"]:x["gold"] for x in T}
cells=["inn1.total_runs","inn1.total_wickets","inn2.total_runs","inn2.total_wickets"]
trans={"gain":0,"loss":0,"both":0,"neither":0}; changed=[]
for k,b in B.items():
    l=Lc.get(k,{}); g=G[k[0]]
    for c in cells:
        bo=eq(b.get(c),g[c]); lo=eq(l.get(c),g[c])
        if bo and lo: trans["both"]+=1
        elif not bo and lo: trans["gain"]+=1; changed.append((k[0],k[1],c,b.get(c),l.get(c),g[c]))
        elif bo and not lo: trans["loss"]+=1; changed.append((k[0],k[1],c,b.get(c),l.get(c),g[c]))
        else: trans["neither"]+=1
out["t_paired"]={"trans":trans,"changed":changed}
(O/"T_PAIRED.json").write_text(json.dumps(out["t_paired"],ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
print(json.dumps({"parse":parse,"groups":groups,"positions":len(positions),"roots":len(roots),"missing":len(missing),"t":trans,"changed":changed},ensure_ascii=False,indent=1))
