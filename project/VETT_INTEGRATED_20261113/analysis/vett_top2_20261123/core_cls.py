import sys,json
from pathlib import Path
from collections import Counter
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
S={s["match"]:s for s in json.loads((Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117").parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
def unwrap(p):
    if isinstance(p,dict) and isinstance(p.get("fields"),dict): return p["fields"]
    return p if isinstance(p,dict) else {}
def cls(s,p):
    p=unwrap(p); a=str(s["A"])+"_wickets"; b=str(s["B"])+"_wickets"
    try: av=int(p.get(a)); bv=int(p.get(b))
    except Exception: return "format"
    old=(s["Aw"],s["Bw"]); new=(s["Aw"]-1,s["Bw"]+1)
    if (av,bv)==old: return "fully_old"
    if (av,bv)==new: return "fully_new"
    if (av,bv)==(s["Aw"]-1,s["Bw"]): return "only_orig_minus1"
    if (av,bv)==(s["Aw"],s["Bw"]+1): return "only_new_plus1"
    return "other"
c=V.connect()
rows=c.execute("SELECT r.match,r.model,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event' AND r.cond='N2_F'").fetchall()
print("CORE_N2_F",len(rows),Counter(cls(S[m],p) for m,mod,p in rows))
rows=c.execute("SELECT r.match,r.model,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event' AND r.cond='N2_W'").fetchall()
print("CORE_N2_W",len(rows),Counter(cls(S[m],p) for m,mod,p in rows))
c.close()
