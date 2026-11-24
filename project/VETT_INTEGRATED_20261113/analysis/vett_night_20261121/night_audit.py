import sys,json
from pathlib import Path
from collections import defaultdict,Counter
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
MODELS=("qwen2.5:7b-instruct-q4_K_M","llama3.1:8b","gemma2:9b")
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
def unwrap(p):
    if isinstance(p,dict) and isinstance(p.get("fields"),dict): return p["fields"]
    return p if isinstance(p,dict) else {}
c=V.connect()
ft=[dict(r) for r in c.execute("SELECT r.match,r.model,r.correct,r.parsed_json,r.raw_output,t.fields_json,t.gold_json,t.prompt FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_ft_ordinary'")]
dg=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.batch_id FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_diag'")]
core=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event'")]
c.close()
# full-table audit
aud=defaultdict(lambda:{"tasks":0,"planned":0,"actual":0,"scorable":0,"evidence":0,"empty":0,"parse_fail":0,"missing_fields":0})
for r in ft:
    m=MS[r["model"]]; a=aud[m]; a["tasks"]+=1; a["planned"]+=43
    try: p=unwrap(json.loads(r["parsed_json"] or "{}"))
    except Exception: p={}
    if not p: a["empty"]+=1
    if not r["correct"]: a["parse_fail"]+=1
    g=json.loads(r["gold_json"] or "{}"); fields=json.loads(r["fields_json"] or "[]")
    a["actual"]+=len(p); a["scorable"]+=sum(1 for k in fields if k in g); a["missing_fields"]+=sum(1 for k in fields if k not in p)
    txt=r["prompt"]
    for k in fields:
        gv=g.get(k)
        if gv is None: continue
        if str(gv) in txt: a["evidence"]+=1
roots=len({r["match"] for r in ft})
AUD=[f"# 513 条普通根整表审计","",f"- 任务：{len(ft)}；独立根：{roots}；与核心 8 根重合：{len({r['match'] for r in ft} & {x['match'] for x in core})}；保留根 0121–0160：0。","","| 模型 | 任务 | 计划格 | 实际输出格 | 可评分格 | 文本有依据格 | 空答 | 解析失败 | 缺失字段 |","|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for m,a in aud.items(): AUD.append(f"| {m} | {a['tasks']} | {a['planned']} | {a['actual']} | {a['scorable']} | {a['evidence']} | {a['empty']} | {a['parse_fail']} | {a['missing_fields']} |")
AUD+=["","- 说明：可评分格 = 金标存在且字段在输出中；文本有依据格 = 金标字符串出现在实际 prompt 中（仅字符串存在性，不等于语义可核对）。","- 历史 79/258 的可答比例只适用于原 258 格材料，不外推到本批 171 根。",""]
(ROOT/"AUDIT_FULLTABLE.md").write_text("\n".join(AUD),encoding="utf-8")
# diag inventory
D=defaultdict(lambda:{"n":0,"ok":0})
for r in dg:
    mode="window" if r["batch_id"]=="B246" else "full"
    key=(mode,r["cond"],MS[r["model"]]); D[key]["n"]+=1; D[key]["ok"]+=int(bool(r["correct"]))
DI=["# 480 条最小诊断清点","",f"- 结果：{len(dg)}；独立根：{len({r['match'] for r in dg})}；问题：q1 认人、q2 原投手、q3 改判后投手、q4 两人旧值。","","| 输入 | 问题 | 模型 | 正确/总数 |","|---|---|---|---:|"]
for (mode,q,m),x in sorted(D.items()): DI.append(f"| {mode} | {q} | {m} | {x['ok']}/{x['n']} |")
DI+=["","- 可接回 24 行：同比赛+同模型；q2/q3/q4 直接对应原归属、最终归属与两人旧值。",""]
(ROOT/"DIAG_INVENTORY.md").write_text("\n".join(DI),encoding="utf-8")
# Q breakdowns per model
Q1=Counter(); Q2=Counter(); Q2n=0
for r in core:
    pass
print(json.dumps({"ft":{m:aud[m] for m in aud},"ft_roots":roots,"diag":len(dg),"diag_roots":len({r['match'] for r in dg})},ensure_ascii=False))
