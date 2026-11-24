import sys,json,datetime
from pathlib import Path
from collections import defaultdict,Counter
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
S={s["match"]:s for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
c=V.connect()
rows=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.parsed_json,r.raw_output,t.gold_json,t.fields_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event'")]
by=defaultdict(dict); errs=Counter(); pairs=defaultdict(dict)
for r in rows:
    by[(r["match"],MS[r["model"]])][r["cond"]]=bool(r["correct"]); pairs[(r["match"],r["model"])][r["cond"]]=bool(r["correct"])
    if not r["correct"]:
        s=S[r["match"]]; p=json.loads(r["parsed_json"] or "{}")
        try: pa=int(p.get(s["A"]+"_wickets")); pb=int(p.get(s["B"]+"_wickets"))
        except Exception: errs["empty/format"]+=1; continue
        if pa==s["Aw"] and pb==s["Bw"]: errs["both_old"]+=1
        elif pa==s["Aw"]-1 and pb==s["Bw"]: errs["only_orig_minus1"]+=1
        elif pa==s["Aw"] and pb==s["Bw"]+1: errs["only_new_plus1"]+=1
        elif pa==s["Aw"]-1 and pb==s["Bw"]+1: errs["both_new_but_total_or_runs"]+=1
        elif pa==s["Bw"] and pb==s["Aw"]: errs["swapped"]+=1
        else: errs["other"]+=1
acc=Counter(); tot=Counter()
for (m,mod),v in by.items():
    for cond,ok in v.items():
        acc[(cond,ok)]+=1; tot[cond]+=1
print("N",len(rows),"MATCHES",len({r["match"] for r in rows}))
print("COND_ACC")
for cond in sorted(tot): print(" ",cond,acc[(cond,True)],"/",tot[cond])
print("MODEL")
for mod in MS.values(): 
    n=sum(1 for (m,mm) in by if mm==mod); ok=sum(1 for (m,mm),v in by.items() if mm==mod for x in v.values() if x)
    print(" ",mod,ok,"/",sum(len(v) for (m,mm),v in by.items() if mm==mod))
print("ERRORS",dict(errs))
print("TRANSITIONS")
for m in sorted({r["match"] for r in rows}):
    for mod in MS.values():
        v=pairs.get((m,mod),{}); cts=[0,0,0,0]
        for code in ("N0","N1","N2"):
            f=v.get(code+"_F"); w=v.get(code+"_W")
            if f is None or w is None: continue
            if not f and w: cts[0]+=1
            elif f and not w: cts[1]+=1
            elif f and w: cts[2]+=1
            else: cts[3]+=1
        print(" ",m,mod,"wrong->right",cts[0],"right->wrong",cts[1],"both",cts[2],"neither",cts[3])
print("FT")
ft=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.parsed_json,t.gold_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable'")]
fts=defaultdict(dict)
for r in ft: fts[(r["match"],MS[r["model"]])][r["cond"]]=r
for (m,mod),v in sorted(fts.items()):
    out=[]
    for cond in ("N1_F_fulltable","N2_F_fulltable"):
        r=v.get(cond)
        if not r: continue
        s=S[m]; g=json.loads(r["gold_json"]); p=json.loads(r["parsed_json"] or "{}")
        inn=int(str(s["innings"]).replace("inn",""))
        rowsb=[n for n in (1,2) if g.get("inn"+str(inn)+".bowl"+str(n)+"_name") in (s["A"],s["B"])]
        tw=[(g.get("inn"+str(inn)+".bowl"+str(n)+"_wickets"),p.get("inn"+str(inn)+".bowl"+str(n)+"_wickets")) for n in rowsb]
        out.append((cond.split("_")[0],tw,g.get("inn"+str(inn)+".total_wickets"),p.get("inn"+str(inn)+".total_wickets")))
    print(" ",m,mod,out)
c.close()
