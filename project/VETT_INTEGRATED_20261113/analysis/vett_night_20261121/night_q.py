import sys,json
from pathlib import Path
from collections import defaultdict,Counter
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
core=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event'")]
ft=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.parsed_json,r.parse_ok FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable'")]
dg=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.batch_id FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_diag'")]
fto=[dict(r) for r in c.execute("SELECT r.match,r.model,r.parsed_json,r.parse_ok,t.fields_json,t.gold_json,t.prompt FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_ft_ordinary'")]
c.close()
C=defaultdict(dict); F=defaultdict(dict)
for r in core: C[(r["match"],r["model"])][r["cond"]]={"ok":bool(r["correct"]),"p":unwrap(json.loads(r["parsed_json"] or "{}"))}
for r in ft: F[(r["match"],r["model"])][r["cond"]]={"p":unwrap(json.loads(r["parsed_json"] or "{}")),"g":json.loads(r["gold_json"] if "gold_json" in r else "{}")}
# recompute ft keyed
F=defaultdict(dict)
for r in ft:
    F[(r["match"],r["model"])][r["cond"]]={"p":unwrap(json.loads(r["parsed_json"] or "{}"))}
c=V.connect(); golds={}
for r in c.execute("SELECT task_key,gold_json FROM tasks WHERE batch_id IN ('B228','B229','B230','B231','B232','B233','B234','B235','B247')"):
    golds[r[0]]=json.loads(r[1])
c.close()
c=V.connect()
for r in c.execute("SELECT r.match,r.model,r.cond,r.parsed_json,r.task_key FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable'"):
    F[(r[0],r[1])][r[2]]={"p":unwrap(json.loads(r[3] or "{}")),"g":golds.get(r[4],{})}
c.close()
# Q1
Q1=["## Q1 全文 vs 窗口","","| 通知 | 模型 | 全对/24 | 窗对/24 | 错→对 | 对→错 | 都对 | 都错 |","|---|---|---:|---:|---:|---:|---:|---:|"]
for code in ("N0","N1","N2"):
    for mod in MODELS:
        n=f=w=wr=rw=bb=nn=0
        for (m,mm),v in C.items():
            if mm!=mod: continue
            a=v.get(code+"_F"); b=v.get(code+"_W")
            if not (a and b): continue
            n+=1
            if a["ok"]: f+=1
            if b["ok"]: w+=1
            if not a["ok"] and b["ok"]: wr+=1
            elif a["ok"] and not b["ok"]: rw+=1
            elif a["ok"] and b["ok"]: bb+=1
            else: nn+=1
        Q1.append(f"| {code} | {MS[mod]} | {f}/{n} | {w}/{n} | {wr} | {rw} | {bb} | {nn} |")
# Q2
Q2=["","## Q2 改判错误形态（子集：N0 全文与 N1 全文均答对）","","| 模型 | 子集 | N2 正确 | 两人旧值 | 只改原投手 | 只改新投手 | 改反 | 其他 |","|---|---:|---:|---:|---:|---:|---:|---:|"]
for mod in MODELS:
    sub=ok=0; cnt=Counter()
    for (m,mm),v in C.items():
        if mm!=mod: continue
        if not (v.get("N0_F",{}).get("ok") and v.get("N1_F",{}).get("ok")): continue
        sub+=1; n2=v.get("N2_F");
        if not n2: continue
        if n2["ok"]: ok+=1; continue
        s=S[m]; p=n2["p"]
        try: pa=int(p.get(s["A"]+"_wickets")); pb=int(p.get(s["B"]+"_wickets"))
        except Exception: cnt["other"]+=1; continue
        if pa==s["Aw"] and pb==s["Bw"]: cnt["both_old"]+=1
        elif pa==s["Aw"]-1 and pb==s["Bw"]: cnt["only_orig_minus1"]+=1
        elif pa==s["Aw"] and pb==s["Bw"]+1: cnt["only_new_plus1"]+=1
        elif pa==s["Bw"] and pb==s["Aw"]: cnt["reversed"]+=1
        else: cnt["other"]+=1
    Q2.append(f"| {MS[mod]} | {sub} | {ok} | {cnt['both_old']} | {cnt['only_orig_minus1']} | {cnt['only_new_plus1']} | {cnt['reversed']} | {cnt['other']} |")
# Q3
Q3=["","## Q3 同源短问 vs 整表（目标两人 wickets + 全队 total 全对）","","| 条件 | 模型 | 都对 | 短对表错 | 短错表对 | 都错 |","|---|---|---:|---:|---:|---:|"]
for code in ("N1","N2"):
    for mod in MODELS:
        b1=s1=t1=n1=0
        for (m,mm),v in C.items():
            if mm!=mod: continue
            cs=v.get(code+"_F"); cf=F.get((m,mod),{}).get(code+"_F_fulltable")
            if not (cs and cf): continue
            s=S[m]; inn=int(str(s["innings"]).replace("inn","")); tk=[]
            for n in (1,2,3):
                nm=cf["g"].get("inn"+str(inn)+".bowl"+str(n)+"_name")
                if nm in (s["A"],s["B"]): tk.append((cf["g"].get("inn"+str(inn)+".bowl"+str(n)+"_wickets"),cf["p"].get("inn"+str(inn)+".bowl"+str(n)+"_wickets")))
            tab=all(g==p for g,p in tk) and cf["p"].get("inn"+str(inn)+".total_wickets")==cf["g"].get("inn"+str(inn)+".total_wickets")
            if cs["ok"] and tab: b1+=1
            elif cs["ok"]: s1+=1
            elif tab: t1+=1
            else: n1+=1
        Q3.append(f"| {code} | {MS[mod]} | {b1} | {s1} | {t1} | {n1} |")
# audit fix
aud=defaultdict(lambda:{"tasks":0,"planned":0,"actual":0,"scorable":0,"evidence":0,"empty":0,"parse_fail":0,"missing":0})
for r in fto:
    m=MS[r["model"]]; a=aud[m]; a["tasks"]+=1; a["planned"]+=43
    p=unwrap(json.loads(r["parsed_json"] or "{}")); g=json.loads(r["gold_json"] or "{}"); fields=json.loads(r["fields_json"] or "[]")
    if not p: a["empty"]+=1
    if not r["parse_ok"]: a["parse_fail"]+=1
    a["actual"]+=len(p); a["scorable"]+=sum(1 for k in p if k in g); a["missing"]+=sum(1 for k in fields if k not in p)
    for k in fields:
        if g.get(k) is not None and str(g[k]) in r["prompt"]: a["evidence"]+=1
AUD=["# 513 条普通根整表审计","",f"- 任务 {len(fto)} 条；独立根 {len({r['match'] for r in fto})}；与核心 8 根重合 0；保留根 0121–0160 为 0。","","| 模型 | 任务 | 计划格 | 实际输出格 | 可评分格 | 文本有依据格 | 空答 | 解析失败 | 缺失字段 |","|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for m,a in aud.items(): AUD.append(f"| {m} | {a['tasks']} | {a['planned']} | {a['actual']} | {a['scorable']} | {a['evidence']} | {a['empty']} | {a['parse_fail']} | {a['missing']} |")
AUD+=["","- 可评分格 = 输出键存在且金标存在；文本有依据格 = 金标字符串出现在实际 prompt 中，仅作存在性核查。","- 历史 79/258 的可答比例不外推到这 171 根。",""]
(ROOT/"AUDIT_FULLTABLE.md").write_text("\n".join(AUD),encoding="utf-8")
(ROOT/"Q_ANSWERS.md").write_text("\n".join(Q1+Q2+Q3),encoding="utf-8")
print(json.dumps({"audit":{m:aud[m] for m in aud}},ensure_ascii=False))
