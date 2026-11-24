import sys,json,datetime
from pathlib import Path
from collections import defaultdict,Counter
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
MODELS=("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b")
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
S={s["match"]:s for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
TZ=datetime.timezone(datetime.timedelta(hours=8))

def unwrap(p):
    if isinstance(p,dict) and isinstance(p.get("fields"),dict): return p["fields"]
    return p if isinstance(p,dict) else {}

def load(template):
    c=V.connect()
    rows=[dict(r) for r in c.execute("SELECT r.match,r.innings,r.model,r.cond,r.correct,r.parsed_json,r.raw_output,r.task_key,t.text_sha,t.prompt_sha,t.fields_json,t.gold_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template=?",(template,))]
    c.close(); return rows

core=load("X_night_core_event"); ft=load("X_night_fulltable"); diag=load("X_night_diag")
C=defaultdict(dict); F=defaultdict(dict)
for r in core:
    p=unwrap(json.loads(r["parsed_json"] or "{}")); C[(r["match"],r["model"])][r["cond"]]={"ok":bool(r["correct"]),"p":p,"raw":r["raw_output"],"tk":r["task_key"],"ts":r["text_sha"]}
for r in ft:
    p=unwrap(json.loads(r["parsed_json"] or "{}")); F[(r["match"],r["model"])][r["cond"]]={"p":p,"g":json.loads(r["gold_json"] or "{}"),"ok":bool(r["correct"]),"raw":r["raw_output"],"tk":r["task_key"],"ts":r["text_sha"]}

def pair(p,s):
    a,bb=s["A"],s["B"]
    return (p.get(a+"_wickets"),p.get(bb+"_wickets"),p.get("innings_total_wickets"))

# 24-row table
lines=["# 24 行逐事件对照表","","> 每行 = 比赛+局+事件+模型；短问 F/W 与整表 N0/N1/N2 并列。数值为 (A/B/total)。","",
"| # | 比赛 | 局 | 事件 | 模型 | 旧 A/B | 正确新 A/B | N0 F / W | N1 F / W | N2 F / W | 整表 N0 / N1 / N2 | 同臂正文 | 可比 |",
"|---|---|---:|---|---|---|---|---|---|---|---|---|---|"]
for i,(m,s) in enumerate(S.items(),1):
    inn=int(str(s["innings"]).replace("inn","")); old=str(s["Aw"])+"/"+str(s["Bw"]); new=str(s["Aw"]-1)+"/"+str(s["Bw"]+1)
    for mod in MODELS:
        c=C.get((m,mod),{}); f=F.get((m,mod),{})
        def sv(cond):
            x=c.get(cond); return "--" if not x else "/".join("?" if v is None else str(v) for v in pair(x["p"],s))
        def tv(cond):
            x=f.get(cond); return "--" if not x else "/".join("?" if x["p"].get(k) is None else str(x["p"].get(k)) for k in (s["A"]+"_wickets",s["B"]+"_wickets","innings_total_wickets"))
        same=[]
        for cs,cf in (("N0_F","N0_F_fulltable"),("N1_F","N1_F_fulltable"),("N2_F","N2_F_fulltable")):
            if c.get(cs) and f.get(cf): same.append(cs.split("_")[0]+":"+("Y" if c[cs]["ts"]==f[cf]["ts"] else "N"))
        rows_found=all(any(f.get(cf,{}).get("g",{}).get("inn"+str(inn)+".bowl"+str(n)+"_name")==nm for n in (1,2,3)) for nm in (s["A"],s["B"]))
        missing=any((f.get(cf,{}).get("p",{}).get(s["A"]+"_wickets") is None or f.get(cf,{}).get("p",{}).get(s["B"]+"_wickets") is None) for cf in ("N0_F_fulltable","N1_F_fulltable","N2_F_fulltable"))
        comp="是" if rows_found and not missing and all(x.endswith("Y") for x in same) else "否"
        note=[]
        if not rows_found: note.append("球员不在表行")
        if missing: note.append("整表漏行")
        if not all(x.endswith("Y") for x in same): note.append("同臂正文不一致")
        lines.append("| "+str(i)+"-"+MS[mod][0]+" | "+m+" | "+str(inn)+" | "+s["batter"]+" | "+MS[mod]+" | "+old+" | "+new+" | "+sv("N0_F")+" / "+sv("N0_W")+" | "+sv("N1_F")+" / "+sv("N1_W")+" | "+sv("N2_F")+" / "+sv("N2_W")+" | "+tv("N0_F_fulltable")+" / "+tv("N1_F_fulltable")+" / "+tv("N2_F_fulltable")+" | "+",".join(same)+" | "+comp+(" ("+" ;".join(note)+")" if note else "")+" |")
(ROOT/"TABLE_24.md").write_text("\n".join(lines),encoding="utf-8")

# Q1
q1=Counter(); tr=Counter()
for (m,mod),v in C.items():
    for code in ("N0","N1","N2"):
        f=v.get(code+"_F"); w=v.get(code+"_W")
        if f and w:
            q1[(code,"F_correct")]+=int(f["ok"]); q1[(code,"W_correct")]+=int(w["ok"]); q1[(code,"n")]+=1
            if not f["ok"] and w["ok"]: tr[(code,"wrong2right")]+=1
            elif f["ok"] and not w["ok"]: tr[(code,"right2wrong")]+=1
            elif f["ok"] and w["ok"]: tr[(code,"both")]+=1
            else: tr[(code,"neither")]+=1
# Q2 subset N0_F & N1_F correct
sub=[]; q2=Counter()
for (m,mod),v in C.items():
    if v.get("N0_F",{}).get("ok") and v.get("N1_F",{}).get("ok"):
        n2=v.get("N2_F"); s=S[m]
        if not n2: continue
        sub.append((m,mod))
        p=n2["p"]; a,bb=s["A"],s["B"]
        try: pa=int(p.get(a+"_wickets")); pb=int(p.get(bb+"_wickets"))
        except Exception: q2["empty/format"]+=1; continue
        if pa==s["Aw"] and pb==s["Bw"]: q2["both_old"]+=1
        elif pa==s["Aw"]-1 and pb==s["Bw"]: q2["only_orig_minus1"]+=1
        elif pa==s["Aw"] and pb==s["Bw"]+1: q2["only_new_plus1"]+=1
        elif pa==s["Aw"]-1 and pb==s["Bw"]+1: q2["both_updated_wrong_total"]+=1
        elif pa==s["Bw"] and pb==s["Aw"]: q2["reversed"]+=1
        else: q2["other"]+=1
# Q3 short vs table
q3=Counter(); pairs3=[]
for (m,mod),v in C.items():
    s=S[m]; inn=int(str(s["innings"]).replace("inn",""))
    for code in ("N1","N2"):
        cs=v.get(code+"_F"); cf=F.get((m,mod),{}).get(code+"_F_fulltable")
        if not (cs and cf): continue
        tk=[]; ok=True
        for n in (1,2,3):
            nm=cf["g"].get("inn"+str(inn)+".bowl"+str(n)+"_name")
            if nm in (s["A"],s["B"]): tk.append((nm,cf["g"].get("inn"+str(inn)+".bowl"+str(n)+"_wickets"),cf["p"].get("inn"+str(inn)+".bowl"+str(n)+"_wickets")))
        tab_ok=all(g==p for _,g,p in tk) and cf["p"].get("inn"+str(inn)+".total_wickets")==cf["g"].get("inn"+str(inn)+".total_wickets")
        k=("both" if cs["ok"] and tab_ok else "short_only" if cs["ok"] else "table_only" if tab_ok else "neither")
        q3[k]+=1; q3[("n_"+code)]+=0
        pairs3.append((m,mod,code,cs["ok"],tab_ok))
print(json.dumps({"q1":{str(k):v for k,v in q1.items()},"tr":{str(k):v for k,v in tr.items()},"q2_subset_n":len(sub),"q2":dict(q2),"q3":dict(q3),"table_rows":len(lines)-5},ensure_ascii=False))
