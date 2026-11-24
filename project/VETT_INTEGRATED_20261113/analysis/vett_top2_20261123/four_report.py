import sys,json,re
from pathlib import Path
from collections import Counter,defaultdict
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
c=V.connect(); design=json.loads(c.execute("SELECT design_json FROM batches WHERE batch_id='B258'").fetchone()[0])
def norm(x): return re.sub(r"\s+"," ",str(x)).strip().lower()
def ranked(inn,A,B,arm):
    arr=[{"n":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers]
    if arm=="N2":
        for x in arr:
            if x["n"]==A: x["w"]-=1
            if x["n"]==B: x["w"]+=1
    return sorted(arr,key=lambda x:(-x["w"],x["r"],x["n"]))
def golds(inn,A,B,arm,idx):
    top=ranked(inn,A,B,arm)[:2]; old=V.gold43(inn if False else inn) if False else None
    g={}
    return top
def build_roots():
    out=[]
    for p in design["positions"]:
        b=V.load_bundle(p["match"]); ii=p["innings"]; inn=b["md"].innings[ii-1]
        bat=next(x for x in inn.batters if x.name==p["event"])
        mm=re.search(r"\bb\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)",bat.dismissal or ""); A=mm.group(1)
        B=next(x for x in sorted(inn.bowlers,key=lambda x:(-x.wickets,x.runs_conceded,x.name)) if x.name!=A)
        out.append({"match":p["match"],"idx":ii,"inn":inn,"b":b,"A":A,"B":B.name})
    return out
def g43(b,inn,idx,A,B,arm):
    g=V.gold43(b["md"]); pre="inn"+str(idx); top=ranked(inn,A,B,arm)[:2]
    for n,x in enumerate(top,1):
        g[pre+".bowl"+str(n)+"_name"]=x["n"]; g[pre+".bowl"+str(n)+"_wickets"]=x["w"]; g[pre+".bowl"+str(n)+"_runs"]=x["r"]
    return g
def table_ok(f,g,idx):
    pre="inn"+str(idx); top=[g[pre+".bowl1_name"],g[pre+".bowl2_name"]]
    names=[f.get(pre+".bowl1_name"),f.get(pre+".bowl2_name")]
    mem=set(map(norm,[x for x in names if x]))==set(map(norm,top))
    vals=True
    for n in (1,2):
        nm=g.get(pre+".bowl"+str(n)+"_name")
        # find row by name
        hit=None
        for k in (1,2):
            if norm(f.get(pre+".bowl"+str(k)+"_name"))==norm(nm): hit=k
        if hit is None: vals=False; continue
        if f.get(pre+".bowl"+str(hit)+"_wickets")!=g.get(pre+".bowl"+str(n)+"_wickets") or f.get(pre+".bowl"+str(hit)+"_runs")!=g.get(pre+".bowl"+str(n)+"_runs"): vals=False
    tot=f.get(pre+".total_wickets")==g.get(pre+".total_wickets")
    return mem,vals,tot,mem and vals and tot
roots=build_roots(); res=[]
for r in roots:
    for arm in ("N1","N2"):
        g=g43(r["b"],r["inn"],r["idx"],r["A"],r["B"],arm); pre="inn"+str(r["idx"]); top=[g[pre+".bowl1_name"],g[pre+".bowl2_name"]]
        for mod in MS:
            dq=c.execute("SELECT parsed_json FROM results WHERE batch_id='B258' AND match=? AND model=? AND cond=? ORDER BY rowid DESC LIMIT 1",(r["match"],mod,arm+"_F_fulltable_direct")).fetchone()
            hq=c.execute("SELECT parsed_json FROM results WHERE batch_id='B259' AND match=? AND model=? AND cond=? ORDER BY rowid DESC LIMIT 1",(r["match"],mod,arm+"_F_fulltable_hint")).fetchone()
            tq=c.execute("SELECT parsed_json FROM results WHERE batch_id='B258' AND match=? AND model=? AND cond=? ORDER BY rowid DESC LIMIT 1",(r["match"],mod,"T2_"+arm)).fetchone()
            dp=json.loads(dq[0] or "{}") if dq else {}; df=dp.get("fields",dp) if isinstance(dp,dict) else {}
            hp=json.loads(hq[0] or "{}") if hq else {}; hf=hp.get("fields",hp) if isinstance(hp,dict) else {}
            tp=json.loads(tq[0] or "{}") if tq else {}; tb=tp.get("bowlers") if isinstance(tp,dict) else None
            dm,dv,dt,dok=table_ok(df,g,r["idx"]); hm,hv,ht,hok=table_ok(hf,g,r["idx"])
            tmem=isinstance(tb,list) and len(tb)==2 and set(map(norm,tb))==set(map(norm,top))
            tord=isinstance(tb,list) and [norm(x) for x in tb]==[norm(x) for x in top]
            # other fields regression direct correct -> hint wrong
            reg=[k for k in g if g.get(k) not in (None,"") and df.get(k)==g.get(k) and hf.get(k)!=g.get(k)]
            gain=[k for k in g if g.get(k) not in (None,"") and df.get(k)!=g.get(k) and hf.get(k)==g.get(k)]
            hnames=[hf.get(pre+".bowl1_name"),hf.get(pre+".bowl2_name")]
            carry=isinstance(tb,list) and set(map(norm,[x for x in hnames if x]))==set(map(norm,tb)) and set(map(norm,[x for x in hnames if x]))!=set(map(norm,top))
            res.append({"gain":len(gain),"carry":carry,"match":r["match"],"arm":arm,"model":mod,"top":top,"dok":dok,"dm":dm,"dv":dv,"dt":dt,"hok":hok,"hm":hm,"hv":hv,"ht":ht,"tmem":tmem,"tord":tord,"reg":len(reg),"gain":len(gain),"carry":carry,"hlist":tb})
(ROOT/"FOUR_PAIRED.json").write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding="utf-8")
agg=Counter()
for x in res:
    for k in ("dok","dm","dv","dt","hok","hm","hv","ht","tmem","tord"):
        agg[(x["arm"],k)]+=int(x[k])
    agg[(x["arm"],"n")]+=1
print(json.dumps({str(k):v for k,v in agg.items()},ensure_ascii=False))
print("PAIRS",len(res),"REGRESS_FIELDS",sum(x["reg"] for x in res))
trans=Counter()
for x in res:
    if x["dok"] and not x["hok"]: trans["direct_ok_hint_bad"]+=1
    if not x["dok"] and x["hok"]: trans["direct_bad_hint_ok"]+=1
    if x["dok"] and x["hok"]: trans["both_ok"]+=1
    if not x["dok"] and not x["hok"]: trans["both_bad"]+=1
    if not x["tmem"] and x["hok"]: trans["wrong_list_hint_ok"]+=1
print("TRANS",dict(trans))
