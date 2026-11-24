import sys,json
from pathlib import Path
from collections import defaultdict
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
MODELS=("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b"); MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
S={s["match"]:s for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
def unwrap(p):
    if isinstance(p,dict) and isinstance(p.get("fields"),dict): return p["fields"]
    return p if isinstance(p,dict) else {}
c=V.connect()
core=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.parsed_json,r.raw_output,r.task_key,t.text_sha FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event'")]
ft=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.parsed_json,r.task_key,t.text_sha,t.gold_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable'")]
c.close()
C=defaultdict(dict); F=defaultdict(dict)
for r in core: C[(r["match"],r["model"])][r["cond"]]={"ok":bool(r["correct"]),"p":unwrap(json.loads(r["parsed_json"] or "{}")),"raw":r["raw_output"],"tk":r["task_key"],"ts":r["text_sha"]}
for r in ft: F[(r["match"],r["model"])][r["cond"]]={"p":unwrap(json.loads(r["parsed_json"] or "{}")),"g":json.loads(r["gold_json"] or "{}"),"tk":r["task_key"],"ts":r["text_sha"]}
L=["# 24 行逐事件对照表（8 事件 × 3 模型）","","> 数值为 A_wickets/B_wickets/total_wickets；短问与整表均来自同一臂 full 文本（N0_F/N1_F/N2_F）。","","| # | 比赛 | 局 | 事件 | 模型 | 旧 A/B | 新 A/B | N0 短 F/W | N1 短 F/W | N2 短 F/W | 整表 N0/N1/N2 | 来源 | 可比 | 原始位置 |","|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i,(m,s) in enumerate(S.items(),1):
    inn=int(str(s["innings"]).replace("inn","")); old=f"{s['Aw']}/{s['Bw']}"; new=f"{s['Aw']-1}/{s['Bw']+1}"
    for mod in MODELS:
        c_=C.get((m,mod),{}); f_=F.get((m,mod),{})
        def sv(cond):
            x=c_.get(cond); return "--" if not x else f"{x['p'].get(s['A']+'_wickets','?')}/{x['p'].get(s['B']+'_wickets','?')}/{x['p'].get('innings_total_wickets','?')}"
        def tv(cond):
            x=f_.get(cond); return "--" if not x else f"{x['p'].get('inn'+str(inn)+'.bowl'+str(_row(f_,s,inn,s['A']))+'_wickets','?') if _row(f_,s,inn,s['A']) else '?'}/{x['p'].get('inn'+str(inn)+'.bowl'+str(_row(f_,s,inn,s['B']))+'_wickets','?') if _row(f_,s,inn,s['B']) else '?'}/{x['p'].get('inn'+str(inn)+'.total_wickets','?')}"
        # define row helper inline via gold names
        def row_of(nm):
            for n in (1,2,3):
                if f_.get('N1_F_fulltable',{}).get('g',{}).get('inn'+str(inn)+'.bowl'+str(n)+'_name')==nm: return n
            return None
        def tv2(cond):
            x=f_.get(cond); 
            if not x: return "--"
            ra,rb=row_of(s["A"]),row_of(s["B"])
            def gv(nm,k):
                r=row_of(nm); return x['p'].get('inn'+str(inn)+'.bowl'+str(r)+'_'+k) if r else None
            return f"{gv(s['A'],'wickets','?') if False else gv(s['A'],'wickets')}/{gv(s['B'],'wickets')}/{x['p'].get('inn'+str(inn)+'.total_wickets')}"
        same=[]
        for cs,cf in (("N0_F","N0_F_fulltable"),("N1_F","N1_F_fulltable"),("N2_F","N2_F_fulltable")):
            if c_.get(cs) and f_.get(cf): same.append(cs.split("_")[0]+":"+("Y" if c_[cs]["ts"]==f_[cf]["ts"] else "N"))
        ra,rb=row_of(s["A"]),row_of(s["B"])
        missing=any(f_.get(cf,{}).get("p",{}).get('inn'+str(inn)+'.bowl'+str(ra)+'_wickets') is None for cf in ("N0_F_fulltable","N1_F_fulltable","N2_F_fulltable"))
        if ra is None or rb is None: comp="否"; note="球员不在表行"
        elif ra>2 or rb>2: comp="否"; note="排名/行次不在 top-2"
        elif missing: comp="否"; note="整表漏行"
        elif not all(x.endswith("Y") for x in same): comp="否"; note="同臂正文不一致"
        else: comp="是"; note=""
        L.append(f"| {i}-{MS[mod][0]} | {m} | {inn} | {s['batter']} | {MS[mod]} | {old} | {new} | {sv('N0_F')} / {sv('N0_W')} | {sv('N1_F')} / {sv('N1_W')} | {sv('N2_F')} / {sv('N2_W')} | {tv2('N0_F_fulltable')} / {tv2('N1_F_fulltable')} / {tv2('N2_F_fulltable')} | 发布版+账本+通知 | {comp}{(' ('+note+')') if note else ''} | {c_.get('N2_F',{}).get('tk','')[:10]} |")
(ROOT/"TABLE_24.md").write_text("\n".join(L),encoding="utf-8")
print(json.dumps({"rows":len(L)-4}))
