import sys,json,re
from pathlib import Path
from collections import defaultdict,Counter
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
MODELS=("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b")
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
S={s["match"]:s for s in json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))}
def norm(x): return re.sub(r"\s+"," ",str(x)).strip().lower()
def unwrap(p):
    if isinstance(p,dict) and isinstance(p.get("fields"),dict): return p["fields"]
    return p if isinstance(p,dict) else {}
c=V.connect()
rows=[dict(r) for r in c.execute("SELECT r.match,r.innings,r.model,r.cond,r.correct,r.parsed_json,t.gold_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership'")]
core=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event'")]
ft=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.parsed_json,t.gold_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable'")]
c.close()
T=defaultdict(dict)
for r in rows:
    p=json.loads(r["parsed_json"] or "{}"); pred=p.get("bowlers") if isinstance(p,dict) else None
    gold=json.loads(r["gold_json"] or "{}").get("bowlers",[])
    if not isinstance(pred,list) or len(pred)!=2: T[(r["match"],r["model"])][r["cond"]]={"membership":False,"order":False,"pred":pred,"gold":gold,"fmt":True}
    else: T[(r["match"],r["model"])][r["cond"]]={"membership":set(map(norm,pred))==set(map(norm,gold)),"order":[norm(x) for x in pred]==[norm(x) for x in gold],"pred":pred,"gold":gold,"fmt":False}
agg=Counter(); bymodel=defaultdict(lambda:Counter())
for (m,mod),v in T.items():
    for cond,x in v.items():
        agg[("n",cond)]+=1; agg[("mem",cond)]+=int(x["membership"]); agg[("ord",cond)]+=int(x["order"])
        bymodel[mod][("n",cond)]+=1; bymodel[mod][("mem",cond)]+=int(x["membership"]); bymodel[mod][("ord",cond)]+=int(x["order"])
# classification
def top2(s,arm):
    b=V.load_bundle(s["match"]); inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    arr=[{"name":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers]
    if arm=="N2":
        for x in arr:
            if x["name"]==s["A"]: x["w"]-=1
            if x["name"]==s["B"]: x["w"]+=1
    arr.sort(key=lambda x:(-x["w"],x["r"],x["name"]))
    return [x["name"] for x in arr[:2]]
cls={}
for m,s in S.items():
    old=top2(s,"N0"); new=top2(s,"N2")
    b=V.load_bundle(m); inn=b["md"].innings[int(str(s["innings"]).replace("inn",""))-1]
    arr=sorted([{"n":x.name,"w":x.wickets,"r":x.runs_conceded} for x in inn.bowlers],key=lambda x:(-x["w"],x["r"],x["n"]))
    tie=len(arr)>=3 and (arr[1]["w"],arr[1]["r"])==(arr[2]["w"],arr[2]["r"])
    cls[m]={"old":old,"new":new,"rank_exit":sorted(set(old)-set(new)),"tie":tie}
# report
L=["# Top-2 中性任务报告","","## 1. 排序规则与可答性（冻结）","","- 规则：wickets 降序，runs conceded 升序，姓名升序；先评成员集合，行序单列。","- 可接受名单：标准全名（名+姓，空格归一、大小写不敏感）；不接受只写姓或只写名。","- 可答性按“文本是否给出 top-2 与第一竞争者的 wicket 数字”审计，4/8 根保守可答；不可答根仍运行，但单列。","","## 2. 总体（成员集合 / 行序）","","| 通知 | 成员对 | 行序对 | 总数 |","|---|---:|---:|---:|"]
for cond in ("T2_N0","T2_N1","T2_N2"): L.append("| "+cond+" | "+str(agg[("mem",cond)])+" | "+str(agg[("ord",cond)])+" | "+str(agg[("n",cond)])+" |")
L+=["","## 3. 分模型","","| 模型 | 通知 | 成员对 | 行序对 | 总数 |","|---|---|---:|---:|---:|"]
for mod in MODELS:
    for cond in ("T2_N0","T2_N1","T2_N2"):
        x=bymodel[mod]; L.append("| "+MS[mod]+" | "+cond+" | "+str(x[("mem",cond)])+" | "+str(x[("ord",cond)])+" | "+str(x[("n",cond)])+" |")
ANS={"match_0003":False,"match_0008":True,"match_0010":True,"match_0012":False,"match_0015":False,"match_0017":True,"match_0026":False,"match_0030":True}
SA=defaultdict(lambda:Counter())
for (m,mod),v in T.items():
    for cond,x in v.items():
        f="answerable" if ANS.get(m) else "not_answerable"
        SA[f][("n",cond)]+=1; SA[f][("mem",cond)]+=int(x["membership"]); SA[f][("ord",cond)]+=int(x["order"])
L+=["","### 2b 按可答性拆分","","| 可答性 | 通知 | 成员对 | 行序对 | 总数 |","|---|---|---:|---:|---:|"]
for f in ("answerable","not_answerable"):
    for cond in ("T2_N0","T2_N1","T2_N2"):
        x=SA[f]; L.append("| "+f+" | "+cond+" | "+str(x[("mem",cond)])+" | "+str(x[("ord",cond)])+" | "+str(x[("n",cond)])+" |")
L+=["","## 4. 普通唯一排名 / 排名退出 / 同分","","| 比赛 | 旧 top-2 | 改判后 top-2 | 排名退出 | 同分 |","|---|---|---|---|---|"]
for m,v in cls.items(): L.append("| "+m+" | "+", ".join(v["old"])+" | "+", ".join(v["new"])+" | "+", ".join(v["rank_exit"] or ["-"])+" | "+str(v["tie"])+" |")
CAT=defaultdict(lambda:Counter())
for (m,mod),v in T.items():
    re_=bool(cls[m]["rank_exit"]); ti=bool(cls[m]["tie"])
    cat="rank_exit_and_tie" if (re_ and ti) else ("rank_exit" if re_ else ("tie" if ti else "unique"))
    for cond,x in v.items():
        CAT[cat][("n",cond)]+=1; CAT[cat][("mem",cond)]+=int(x["membership"]); CAT[cat][("ord",cond)]+=int(x["order"])
L+=["","### 4b 按排名类别拆分","","| 类别 | 通知 | 成员对 | 行序对 | 总数 |","|---|---|---:|---:|---:|"]
for cat in ("unique","rank_exit","rank_exit_and_tie","tie"):
    for cond in ("T2_N0","T2_N1","T2_N2"):
        x=CAT[cat]; L.append("| "+cat+" | "+cond+" | "+str(x[("mem",cond)])+" | "+str(x[("ord",cond)])+" | "+str(x[("n",cond)])+" |")
L+=["","## 5. match_0003：三种任务对照（Qwen / Llama）","","| 模型 | 通知 | 中性 top-2 | 具名短问 5 字段 | 整表目标两格+total |","|---|---|---|---|---|"]
for mod in ("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b"):
    for arm in ("N0","N1","N2"):
        t=T.get(("match_0003",mod),{}).get("T2_"+arm)
        cs=next((x["correct"] for x in core if x["match"]=="match_0003" and x["model"]==mod and x["cond"]==arm+"_F"),None)
        tab="?"
        x=next((z for z in ft if z["match"]=="match_0003" and z["model"]==mod and z["cond"]==arm+"_F_fulltable"),None)
        if x:
            s=S["match_0003"]; inn=1; g=json.loads(x["gold_json"]); p=unwrap(json.loads(x["parsed_json"] or "{}")); ok=True
            for n in (1,2,3):
                nm=g.get("inn"+str(inn)+".bowl"+str(n)+"_name")
                if nm in (s["A"],s["B"]):
                    k="inn"+str(inn)+".bowl"+str(n)+"_wickets"
                    if p.get(k)!=g.get(k): ok=False
            ok=ok and p.get("inn"+str(inn)+".total_wickets")==g.get("inn"+str(inn)+".total_wickets")
            tab=str(ok)
        L.append("| "+MS[mod]+" | "+arm+" | "+("成员对/行序对" if t and t["membership"] and t["order"] else "成员错/行序错" if t else "缺")+" | "+str(cs)+" | "+tab+" |")
L+=["","- 首场 match_0003 的 9 个位置全部返回恰好两个人名（格式 9/9 通过），再扩到其余 7 根。","- Qwen：中性 top-2 三个通知都成员/行序全对；具名短问也全对；但 43 字段整表目标两格+total 全错（维持/无通知把 Connor Reed 写成 2，改判写 0）。","- Llama：中性 top-2 三个通知都错，且把第二人写成 Isaac Wells（另一局投手）；具名短问全对，整表维持/无通知目标两格+total 正确、改判错。","- 这说明“点名式短问”可以正确，但无目标提示的 top-2 需要自己绑定局别与行序，Llama 在这一步绑到另一局；Qwen 相反，点名能对，整表行映射错。",""]
L+=["","### 5b 全部 8 根的三任务连接（同场/同通知/同模型）","","| 比赛 | 模型 | N0 top-2/短问/整表 | N1 top-2/短问/整表 | N2 top-2/短问/整表 |","|---|---|---|---|---|"]
for m in S:
    for mod in MODELS:
        cells=[]
        for arm in ("N0","N1","N2"):
            t=T.get((m,mod),{}).get("T2_"+arm)
            cs=next((x["correct"] for x in core if x["match"]==m and x["model"]==mod and x["cond"]==arm+"_F"),None)
            tab="?"
            x=next((z for z in ft if z["match"]==m and z["model"]==mod and z["cond"]==arm+"_F_fulltable"),None)
            if x:
                s=S[m]; inn=int(str(s["innings"]).replace("inn","")); g=json.loads(x["gold_json"]); p=unwrap(json.loads(x["parsed_json"] or "{}")); ok=True
                for n in (1,2,3):
                    nm=g.get("inn"+str(inn)+".bowl"+str(n)+"_name")
                    if nm in (s["A"],s["B"]):
                        k="inn"+str(inn)+".bowl"+str(n)+"_wickets"
                        if p.get(k)!=g.get(k): ok=False
                ok=ok and p.get("inn"+str(inn)+".total_wickets")==g.get("inn"+str(inn)+".total_wickets")
                tab=str(ok)
            t2="缺" if not t else ("M" if t["membership"] else "-")+("/O" if t["order"] else "")
            cells.append(t2+"; "+str(cs)+"; "+tab)
        L.append("| "+m+" | "+MS[mod]+" | "+" | ".join(cells)+" |")
L+=["","- M=成员对，/O=行序对；短问为 5 字段 task_correct；整表为目标两格+total 全对。",""]
L+=["","## 6. 逐条输出","","| 比赛 | 模型 | 通知 | 预测 | 金标 | 成员 | 行序 |","|---|---|---|---|---|---|---|"]
for (m,mod),v in sorted(T.items()):
    for cond,x in v.items(): L.append("| "+m+" | "+MS[mod]+" | "+cond+" | "+json.dumps(x["pred"],ensure_ascii=False)+" | "+json.dumps(x["gold"],ensure_ascii=False)+" | "+str(x["membership"])+" | "+str(x["order"])+" |")
(ROOT/"TOP2_REPORT.md").write_text("\n".join(L),encoding="utf-8")
print(json.dumps({"results":len(rows),"roots":len({r['match'] for r in rows})},ensure_ascii=False))
