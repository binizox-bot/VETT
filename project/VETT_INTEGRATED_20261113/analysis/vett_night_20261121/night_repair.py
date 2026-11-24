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
dg=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.batch_id,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_diag'")]
core=[dict(r) for r in c.execute("SELECT r.match,r.model,r.cond,r.correct,r.parsed_json FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event'")]
c.close()
D=defaultdict(lambda:{"n":0,"ok":0})
for r in dg:
    mode="window" if r["batch_id"]=="B246" else "full"
    D[(mode,r["cond"])]["n"]+=1; D[(mode,r["cond"])]["ok"]+=int(bool(r["correct"]))
# offline repair: use q4 old wickets to compute reassign, apply to N2_F errors
D4={(r["match"],r["model"]):unwrap(json.loads(r["parsed_json"] or "{}")) for r in dg if r["cond"]=="q4_old" and r["batch_id"]=="B243"}
rep=Counter()
for r in core:
    if r["cond"]!="N2_F": continue
    s=S[r["match"]]; p=unwrap(json.loads(r["parsed_json"] or "{}")); q4=D4.get((r["match"],r["model"]),{})
    try: a=int(q4.get(s["A"]+"_wickets")); b=int(q4.get(s["B"]+"_wickets"))
    except Exception: rep["refused_no_extraction"]+=1; continue
    newa,newb=a-1,b+1
    if newa==s["Aw"]-1 and newb==s["Bw"]+1:
        if not r["correct"]: rep["fixed_if_old_correct"]+=1
        else: rep["already_correct"]+=1
    else: rep["extraction_wrong_or_broken"]+=1
DI=["# 480 条最小诊断清点","",f"- 结果 {len(dg)} 条；独立根 {len({r['match'] for r in dg})}；q1 认人、q2 原投手、q3 最终投手、q4 两人旧值。","","| 输入 | 问题 | 正确/总数 |","|---|---|---:|"]
for (mode,q),x in sorted(D.items()): DI.append(f"| {mode} | {q} | {x['ok']}/{x['n']} |")
DI+=["","- 可按“比赛+模型”接回 24 行表；q2/q3/q4 对应原归属、最终归属、旧值。",""]
(ROOT/"DIAG_INVENTORY.md").write_text("\n".join(DI),encoding="utf-8")
RP=["# 离线双边更新（不再调模型）","",f"- 对象：核心 N2 全文 24 条；用同一模型 q4 旧值做 A-1/B+1。","",f"- 修复计数：{dict(rep)}","","- 说明：这是“程序脚手架”上界，不是模型能力；若 q4 抽错则拒绝或改坏。",""]
(ROOT/"REPAIR_OFFLINE.md").write_text("\n".join(RP),encoding="utf-8")
print(json.dumps({"diag":{f"{k[0]}/{k[1]}":v for k,v in D.items()},"repair":dict(rep)},ensure_ascii=False))
