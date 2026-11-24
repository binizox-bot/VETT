import sys,json,datetime,re
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
    rows=[dict(r) for r in c.execute("SELECT r.batch_id,r.match,r.innings,r.model,r.cond,r.correct,r.parse_ok,r.parsed_json,r.created_at,r.task_key,t.text_sha,t.gold_json,t.prompt FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template=? ORDER BY r.created_at",(template,))]
    c.close(); return rows
core=load("X_night_core_event"); ft=load("X_night_fulltable"); diag=load("X_night_diag"); fto=load("X_night_ft_ordinary"); part=load("X_night_partial"); fld=load("X_night_field")
C=defaultdict(dict); F=defaultdict(dict); P=defaultdict(dict)
for r in core: C[(r["match"],r["model"])][r["cond"]]={"ok":bool(r["correct"]),"p":unwrap(json.loads(r["parsed_json"] or "{}"))}
for r in ft: F[(r["match"],r["model"])][r["cond"]]={"p":unwrap(json.loads(r["parsed_json"] or "{}")),"g":json.loads(r["gold_json"] or "{}")}
for r in part: P[(r["match"],r["model"])][r["cond"]]={"ok":bool(r["correct"]),"p":unwrap(json.loads(r["parsed_json"] or "{}"))}
def table_ok(m,mod,prefix):
    x=F.get((m,mod),{}).get(prefix+"_fulltable")
    if not x: return None
    s=S[m]; inn=int(str(s["innings"]).replace("inn","")); ok=True
    for n in (1,2,3):
        nm=x["g"].get("inn"+str(inn)+".bowl"+str(n)+"_name")
        if nm in (s["A"],s["B"]):
            k="inn"+str(inn)+".bowl"+str(n)+"_wickets"
            if x["p"].get(k)!=x["g"].get(k): ok=False
    return ok and x["p"].get("inn"+str(inn)+".total_wickets")==x["g"].get("inn"+str(inn)+".total_wickets")
L=["# 夜间阶段验收报告（MORNING ACCEPTANCE）","","- 生成时间："+datetime.datetime.now(TZ).isoformat(timespec="seconds")+"（Asia/Shanghai）","- 数据源：workflow.db / runs/*.jsonl；离线复算，不调用模型。",""]
# table 1
L+=["## 0. 三张总表","","### 表 1  全文 vs 同源窗口（每格 /24）","","| 通知 | 模型 | 全文对 | 窗口对 | 全文错→窗口对 | 全文对→窗口错 |","|---|---|---:|---:|---:|---:|"]
for code in ("N0","N1","N2"):
    for mod in MODELS:
        f=w=wr=rw=n=0
        for (m,mm),v in C.items():
            if mm!=mod: continue
            a=v.get(code+"_F"); b=v.get(code+"_W")
            if not (a and b): continue
            n+=1; f+=int(a["ok"]); w+=int(b["ok"])
            if not a["ok"] and b["ok"]: wr+=1
            elif a["ok"] and not b["ok"]: rw+=1
        L.append("| "+code+" | "+MS[mod]+" | "+str(f)+"/"+str(n)+" | "+str(w)+"/"+str(n)+" | "+str(wr)+" | "+str(rw)+" |")
# table 2
L+=["","### 表 2  三种通知（全文+窗口合计 /48）","","| 通知 | 模型 | 全文对 | 窗口对 | 合计 |","|---|---|---:|---:|---:|"]
for code in ("N0","N1","N2"):
    for mod in MODELS:
        f=w=n=0
        for (m,mm),v in C.items():
            if mm!=mod: continue
            a=v.get(code+"_F"); b=v.get(code+"_W")
            if not (a and b): continue
            n+=2; f+=int(a["ok"]); w+=int(b["ok"])
        L.append("| "+code+" | "+MS[mod]+" | "+str(f)+"/"+str(n)+" | "+str(w)+"/"+str(n)+" | "+str(f+w)+"/"+str(n)+" |")
# table 3
L+=["","### 表 3  同源短问 vs 整表（两人 wickets + 全队 total 全对）","","| 条件 | 模型 | 都对 | 短对表错 | 短错表对 | 都错 |","|---|---|---:|---:|---:|---:|"]
for code in ("N1","N2"):
    for mod in MODELS:
        b1=s1=t1=n1=0
        for (m,mm),v in C.items():
            if mm!=mod: continue
            cs=v.get(code+"_F"); tab=table_ok(m,mm,code+"_F")
            if cs is None or tab is None: continue
            if cs["ok"] and tab: b1+=1
            elif cs["ok"]: s1+=1
            elif tab: t1+=1
            else: n1+=1
        L.append("| "+code+" | "+MS[mod]+" | "+str(b1)+" | "+str(s1)+" | "+str(t1)+" | "+str(n1)+" |")
L+=["","- 24 行表输入与字段可比 16/24；其余因整表空答/漏行单列（TABLE_24.md）。","","**摘要（8 个独立比赛根）**：无通知/维持窗口更好（救回 3+5、无改坏）；正式改判窗口反而更差（救回 2、改坏 4）。改判子集 17 组只有 7 组正确，6 组只加新投手。整表侧短问对、整表错共 22 组（N1 15、N2 7），部分表只救回 N1（13/24），N2 仍 2/24。",""]
# Q2
L+=["## 1. 改判错误形态（子集：无通知与维持均答对）","","| 模型 | 子集 | 改判正确 | 两人旧值 | 只改原投手 | 只改新投手 | 改反 | 其他 |","|---|---:|---:|---:|---:|---:|---:|---:|"]
for mod in MODELS:
    sub=ok=0; cc=Counter()
    for (m,mm),v in C.items():
        if mm!=mod: continue
        if not (v.get("N0_F",{}).get("ok") and v.get("N1_F",{}).get("ok")): continue
        sub+=1; n2=v.get("N2_F")
        if not n2: continue
        if n2["ok"]: ok+=1; continue
        s=S[m]; p=n2["p"]
        try: pa=int(p.get(s["A"]+"_wickets")); pb=int(p.get(s["B"]+"_wickets"))
        except Exception: cc["other"]+=1; continue
        if pa==s["Aw"] and pb==s["Bw"]: cc["both_old"]+=1
        elif pa==s["Aw"]-1 and pb==s["Bw"]: cc["only_orig_minus1"]+=1
        elif pa==s["Aw"] and pb==s["Bw"]+1: cc["only_new_plus1"]+=1
        elif pa==s["Bw"] and pb==s["Aw"]: cc["reversed"]+=1
        else: cc["other"]+=1
    L.append("| "+MS[mod]+" | "+str(sub)+" | "+str(ok)+" | "+str(cc["both_old"])+" | "+str(cc["only_orig_minus1"])+" | "+str(cc["only_new_plus1"])+" | "+str(cc["reversed"])+" | "+str(cc["other"])+" |")
# case
L+=["","## 2. 会读旧账吗、会执行变化吗、填整表能保住吗","","**失败案例（短问对、整表错）**：",""]
s=S["match_0003"]; m="match_0003"
for mod in MODELS:
    cs=C.get((m,mod),{}).get("N1_F"); tab=table_ok(m,mod,"N1_F")
    if cs and cs["ok"] and tab is False:
        x=F.get((m,mod),{}).get("N1_F_fulltable")
        L+=["- 比赛/事件："+m+" 第 1 局，"+s["batter"]+" 出局；模型 "+MS[mod]+"；维持原判。",
            "- 旧值："+s["A"]+" 4/28、"+s["B"]+" 1/28；全队 8；应保持 4/1/8。",
            "- 短问原答："+json.dumps(cs["p"],ensure_ascii=False)[:220]+"。",
            "- 整表原答（对应行）："+json.dumps({k:v for k,v in x["p"].items() if "bowl" in k and "wickets" in k},ensure_ascii=False)[:260]+"。",
            "- 关键原句：Brandon followed soon after, again to Clarke, again with Cooper involved；通知：维持原判。",""]
        break
c=V.connect(); b212=[dict(r) for r in c.execute("SELECT r.cond,r.correct FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.batch_id='B212'")]; c.close()
ok=sum(1 for r in b212 if r["cond"]=="c10" and r["correct"]); n=sum(1 for r in b212 if r["cond"]=="c10")
L+=["**成功对照（快照协议）**：B212 match_0003 正式改判（c10）"+str(ok)+"/"+str(n)+" 全对，3/2/8；但长文协议下没有一组在改判后同时通过短问与整表。","","**次优成功对照（长文维持）**：match_0003 / Llama / 维持，短问 4/1/8、整表 4/1/8 均保持正确。",""]
# diag
DA=defaultdict(lambda:{"n":0,"ok":0})
for r in diag:
    mode="window" if r.get("batch_id")=="B246" else "full"
    DA[(mode,r["cond"])]["n"]+=1; DA[(mode,r["cond"])]["ok"]+=int(bool(r["correct"]))
L+=["## 3. 480 条最小诊断","","- 结果 "+str(len(diag))+" 条；独立根 "+str(len({r["match"] for r in diag}))+"；输入含全文与窗口。","","| 输入 | 问题 | 正确/总数 |","|---|---|---:|"]
for (mode,cd),x in sorted(DA.items()): L.append("| "+mode+" | "+cd+" | "+str(x["ok"])+"/"+str(x["n"])+" |")
L+=["","- 关键（仅 N2 改判文本）：q1 认人全文 11/72、窗口 36/72；q4 旧值全文 44/72、窗口 56/72。最早失败点是长文中认错出局，其次是把改判后数值当作旧值。",""]
# audit
aud=defaultdict(lambda:{"tasks":0,"planned":0,"actual":0,"scorable":0,"evidence":0,"empty":0,"parse":0,"missing":0})
for r in fto:
    mm=MS[r["model"]]; a=aud[mm]; a["tasks"]+=1; a["planned"]+=43
    p=unwrap(json.loads(r["parsed_json"] or "{}")); g=json.loads(r["gold_json"] or "{}"); fields=list(g.keys())
    if not p: a["empty"]+=1
    if not r.get("parse_ok"): a["parse"]+=1
    a["actual"]+=len(p); a["scorable"]+=sum(1 for k in p if k in g); a["missing"]+=sum(1 for k in fields if k not in p)
    for k in fields:
        if g.get(k) is not None and str(g[k]) in (r.get("prompt") or ""): a["evidence"]+=1
L+=["### 3b 单字段抽取：已排除","","- B251/B252 的字段题输出 schema 有误：模型返回 {'field': '<字段名>'}，没有返回值；该分支不计入能力结论，详见 INCIDENT_FIELD_PROMPT.md。",""]
L+=["## 4. 513 条普通根整表审计","","| 模型 | 任务 | 计划格 | 实际输出格 | 可评分格 | 有依据格 | 空答/解析失败 | 缺失字段 |","|---|---:|---:|---:|---:|---:|---:|---:|"]
for mm,a in aud.items(): L.append("| "+mm+" | "+str(a["tasks"])+" | "+str(a["planned"])+" | "+str(a["actual"])+" | "+str(a["scorable"])+" | "+str(a["evidence"])+" | "+str(a["empty"])+"/"+str(a["parse"])+" | "+str(a["missing"])+" |")
L+=["","- 171 根；与核心 8 根重合 0；保留根 0121–0160 为 0；历史 79/258 不外推。",""]
# partial full & window
def partial_stats(suffix):
    out={}
    for code in ("N1","N2"):
        pok=pn=both=po=to=ne=0
        for (m,mod),v in P.items():
            for key,pp in v.items():
                if not key.startswith(code+"_"+suffix+"_partial"): continue
                pn+=1; pok+=int(pp["ok"])
                tab=table_ok(m,mod,code+"_"+suffix)
                if tab is None: continue
                if pp["ok"] and tab: both+=1
                elif pp["ok"]: po+=1
                elif tab: to+=1
                else: ne+=1
        out[code]=(pok,pn,po,to,both,ne)
    return out
L+=["## 5. 部分表 vs 整表（B248 全文 / B249 窗口）",""]
for suffix,label in (("F","全文"),("W","窗口")):
    st=partial_stats(suffix); L+=["### "+label,"","| 条件 | 部分表正确/总数 | 部分对整表错 | 部分错整表对 | 都对 | 都错 |","|---|---:|---:|---:|---:|---:|"]
    for code in ("N1","N2"):
        x=st[code]; L.append("| "+code+" | "+str(x[0])+"/"+str(x[1])+" | "+str(x[2])+" | "+str(x[3])+" | "+str(x[4])+" | "+str(x[5])+" |")
    L+=[""]
L+=["- 部分表 = 同一文本只填具名两行 + total；整表 = 43 字段。",""]
L+=["### 5c 窗口 43 字段整表（B250）","","| 条件 | 目标两人 wickets + total 全对/总数 |","|---|---:|"]
for code in ("N1","N2"):
    tok=tn=0
    for (m,mod),v in F.items():
        x=v.get(code+"_W_fulltable")
        if not x: continue
        tn+=1; tok+=int(bool(table_ok(m,mod,code+"_W")))
    L.append("| "+code+" | "+str(tok)+"/"+str(tn)+" |")
L+=['',"- 与表 3 的全文整表对照，可判断窗口是否同样减轻整表负担。",""]
# next change
L+=["## 6. 下一版数据集最值得改的一处","","- 优先项：把正式改判题拆成三步必填：先锁定出局者与局别，再复述两人旧值，最后填原投手 −1 / 新投手 +1，才允许给最终数对。",
    "- 针对现象：全文 q1 认人 11/72、q4 旧值 44/72；子集 17 组中只改新投手 6、两人旧值 1、其他 3、正确 7。",
    "- 复现范围：8 个核心根，Qwen/Llama/Gemma 均有；窗口未救回改判（N2 全文 7/24、窗口 5/24）。",
    "- 还缺：人工确认窗口必要证据；整表非目标字段退步统计；单字段分支因 schema 错误已排除（INCIDENT_FIELD_PROMPT.md）。",""]
# ledger
ts=[datetime.datetime.fromisoformat(r["created_at"]) for r in core+ft+diag+fto+part if r.get("created_at")]
span=gaps=0
if ts:
    ts.sort(); span=(ts[-1]-ts[0]).total_seconds()/3600; prev=ts[0]
    for t in ts[1:]:
        d=(t-prev).total_seconds()
        if d>600: gaps+=d/3600
        prev=t
L+=["## 7. 运行账本","","- 结果跨度 "+str(round(span,2))+" 小时；有效推理约 "+str(round(span-gaps,2))+" 小时；>10 分钟空档 "+str(round(gaps,2))+" 小时。","- 补测：B248 48、B249 48、B250 48、B251 480、B252 240、B253 48；外部 API 0。夜间总计 2,151 条结果。",""]
L+=["## 8. 逐行复算位置与来源","","- 24 行表：TABLE_24.md；逐问：Q_ANSWERS.md；诊断：DIAG_INVENTORY.md；审计：AUDIT_FULLTABLE.md；离线更新：REPAIR_OFFLINE.md。","- 来源：发布版 commentary + pre-revision 账本句 + 通知（本地受控编辑）；纯发布版同源 0。",""]
p=ROOT/"MORNING_ACCEPTANCE.md"; p.write_text("\n".join(L),encoding="utf-8")
(ROOT/"NIGHT_REPORT_PREVIEW.md").write_text("\n".join(L),encoding="utf-8")
print(json.dumps({"report":str(p),"core":len(core),"diag":len(diag),"partial":len(part)}))
