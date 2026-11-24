import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; P=INT/"analysis"/"vett_overnight_20261114"; O=INT/"analysis"/"vett_evidence_upgrade_20261115"
def eq(a,b):
    try: return int(a)==int(b)
    except Exception: return False
Or={}
for r in [json.loads(l) for l in (P/"runs"/"expand.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]:
    if r.get("cond")=="O": Or[(r["match"],r["model"])]=r.get("parsed") or {}
for r in [json.loads(l) for l in (P/"runs"/"all.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]:
    if r.get("phase")=="D" and r.get("cond")=="O": Or[(r["match"],r["model"])]=r.get("parsed") or {}
S=json.loads((INT/"analysis"/"vett_evidence_position_transfer"/"scores.json").read_text(encoding="utf-8"))
for k,v in S["per"].items():
    m,model=k.split("|"); Or[(m,model)]={"total_runs":v["O"]["runs"],"total_wickets":v["O"]["wk"]}
def paired(man,run):
    M={x["match"]:x for x in json.loads((P/man).read_text(encoding="utf-8"))}
    R=[json.loads(l) for l in (P/run).read_text(encoding="utf-8").splitlines() if l.strip()]
    out={"n":0,"O":0,"V":0,"gain":0,"loss":0,"both":0,"neither":0,"missing":0}
    for r in R:
        m=r["match"]; s=M[m]; o=Or.get((m,r["model"])); d=r.get("parsed") or {}
        if not o: out["missing"]+=1; continue
        oc=eq(o.get("total_runs"),s["runs"]) and eq(o.get("total_wickets"),s["wickets"])
        vc=eq(d.get("total_runs"),s["runs"]) and eq(d.get("total_wickets"),s["wickets"])
        out["n"]+=1; out["O"]+=oc; out["V"]+=vc
        if oc and vc: out["both"]+=1
        elif not oc and vc: out["gain"]+=1
        elif oc and not vc: out["loss"]+=1
        else: out["neither"]+=1
    return out
res={"mid":paired("dplus_remove_manifest.json","runs/dplus_remove.jsonl"),"end":paired("dplus_end_manifest.json","runs/dplus_end.jsonl"),"other":paired("dplus_other_manifest.json","runs/dplus_other.jsonl")}
(O/"DPLUS_PAIRED.json").write_text(json.dumps(res,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
print(json.dumps(res,ensure_ascii=False,indent=1))
