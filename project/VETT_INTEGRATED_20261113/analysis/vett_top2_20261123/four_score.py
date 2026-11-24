import sys,json,re
from pathlib import Path
from collections import Counter,defaultdict
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
design=json.loads(V.connect().execute("SELECT design_json FROM batches WHERE batch_id='B258'").fetchone()[0])
def norm(x): return re.sub(r"\s+"," ",str(x)).strip().lower()
def get_event(m,batter):
    b=V.load_bundle(m)
    for ii,inn in enumerate(b["md"].innings,1):
        for bat in inn.batters:
            if bat.name==batter:
                mm=re.search(r"\bb\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",bat.dismissal or "")
                A=mm.group(1) if mm else None
                t2=sorted(inn.bowlers,key=lambda x:(-x.wickets,x.runs_conceded,x.name))
                return b,ii,inn,bat,A,t2
    raise SystemExit("event missing")
roots=[]
for p in design["positions"]:
    b,ii,inn,bat,A,t2=get_event(p["match"],p["event"])
    B=next(x for x in t2 if x.name!=A)
    roots.append({"match":p["match"],"inn":ii,"batter":bat.name,"A":A,"B":B.name,"inn":inn,"idx":ii,"text":b["text"]})
def ranked(inn,A,B,arm):
    arr=[{"n":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers]
    if arm=="N2":
        for x in arr:
            if x["n"]==A: x["w"]-=1
            if x["n"]==B: x["w"]+=1
    return sorted(arr,key=lambda x:(-x["w"],x["r"],x["n"]))
def goldmap(inn,A,B,arm):
    top=ranked(inn,A,B,arm)[:2]
    vals={x["n"]:(x["w"],x["r"]) for x in top}
    return [x["n"] for x in top],vals
c=V.connect(); res=[]
for r in roots:
    for arm in ("N1","N2"):
        top,vals=goldmap(r["inn"],r["A"],r["B"],arm)
        pre="inn"+str(r["idx"])
        for mod in MS:
            row=c.execute("SELECT parsed_json FROM results WHERE batch_id='B258' AND match=? AND model=? AND cond=? ORDER BY rowid DESC LIMIT 1",(r["match"],mod,arm+"_F_fulltable_direct")).fetchone()
            p=json.loads(row[0] or "{}") if row else {}; f=p.get("fields",p) if isinstance(p,dict) else {}
            names=[f.get(pre+".bowl1_name"),f.get(pre+".bowl2_name")]
            mem=set(map(norm,[x for x in names if x]))==set(map(norm,top))
            valsok=True
            for nm,(w,rr) in vals.items():
                hit=[f.get(pre+".bowl1_"+k) for k in ("wickets","runs")] if norm(f.get(pre+".bowl1_name"))==norm(nm) else ([f.get(pre+".bowl2_"+k) for k in ("wickets","runs")] if norm(f.get(pre+".bowl2_name"))==norm(nm) else [None,None])
                if hit!=[w,rr]: valsok=False
            tot=f.get(pre+".total_wickets")==r["inn"].total_wickets
            ok=mem and valsok and tot
            rt=c.execute("SELECT parsed_json FROM results WHERE batch_id='B258' AND match=? AND model=? AND cond=? ORDER BY rowid DESC LIMIT 1",(r["match"],mod,"T2_"+arm)).fetchone()
            tp=json.loads(rt[0] or "{}") if rt else {}; tb=tp.get("bowlers") if isinstance(tp,dict) else None
            tmem=isinstance(tb,list) and len(tb)==2 and set(map(norm,tb))==set(map(norm,top))
            tord=isinstance(tb,list) and [norm(x) for x in tb]==[norm(x) for x in top]
            res.append({"match":r["match"],"arm":arm,"model":mod,"txt":r["text"],"top":top,"direct":ok,"mem":mem,"vals":valsok,"tot":tot,"tmem":tmem,"tord":tord,"dnames":names,"tp":tb})
(ROOT/"FOUR_SCORE.json").write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
agg=Counter()
for x in res: agg[(x["arm"],"direct")]+=int(x["direct"]); agg[(x["arm"],"mem")]+=int(x["mem"]); agg[(x["arm"],"tmem")]+=int(x["tmem"]); agg[(x["arm"],"tord")]+=int(x["tord"]); agg[(x["arm"],"n")]+=1
print(json.dumps({str(k):v for k,v in agg.items()},ensure_ascii=False))
print("N",len(res))
