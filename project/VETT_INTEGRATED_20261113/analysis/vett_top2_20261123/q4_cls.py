import sys,json
from collections import Counter
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
S={s["match"]:s for s in json.loads((V.WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))} if hasattr(V,"WF") else {}
if not S:
    from pathlib import Path
    S={s["match"]:s for s in json.loads((Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117").parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
def cls(s,p):
    a=str(s["A"])+"_wickets"; b=str(s["B"])+"_wickets"
    try: av=int(p.get(a)); bv=int(p.get(b))
    except Exception: return "format"
    old=(s["Aw"],s["Bw"]); new=(s["Aw"]-1,s["Bw"]+1)
    if (av,bv)==old: return "fully_old"
    if (av,bv)==new: return "fully_new"
    if (av,bv)==(s["Aw"]-1,s["Bw"]): return "only_orig_minus1"
    if (av,bv)==(s["Aw"],s["Bw"]+1): return "only_new_plus1"
    return "other"
c=V.connect()
for bid,label in (("B243","full"),("B246","window")):
    rows=c.execute("SELECT r.match,r.model,t.prompt,r.parsed_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id=? AND r.cond='q4_old'",(bid,)).fetchall()
    out=[]
    for m,mod,prompt,parsed in rows:
        if bid=="B246" and "formally reassigned" not in (prompt or ""): continue
        s=S[m]; p=json.loads(parsed or "{}")
        out.append((m,mod.split(":")[0],cls(s,p),p))
    print(label,"N",len(out),"CLASS",Counter(x[2] for x in out))
    for x in out:
        if x[2]=="fully_new": print("  NEW",x[0],x[1],x[3])
c.close()
