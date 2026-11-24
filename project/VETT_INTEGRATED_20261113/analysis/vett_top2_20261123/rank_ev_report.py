import sys,json,re
from pathlib import Path
from collections import Counter,defaultdict
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
GOLD={"match_0008":["Ryan Frost","Evan Reed"],"match_0010":["Evan Turner","Luke Barrett"]}
MISS={"match_0008":("Reed","27"),"match_0010":("Barrett","38")}
def norm(x): return re.sub(r"\s+"," ",str(x)).strip().lower()
c=V.connect(); R={}
for r in c.execute("SELECT match,model,cond,parsed_json FROM results WHERE batch_id='B260'"):
    R[(r[0],r[1],r[2])]=json.loads(r[3] or "{}")
rows=[]
for m in ("match_0008","match_0010"):
    for mod in MS:
        miss=R.get((m,mod,"RANK_MISS"),{}); ev=R.get((m,mod,"RANK_EVID"),{})
        mtxt=json.dumps(miss,ensure_ascii=False).lower()
        mu=bool(miss.get("uncertain") is True)
        name,run=MISS[m]
        mok=mu and name.lower() in mtxt and ("run" in mtxt)
        et=ev.get("bowlers")
        eok=isinstance(et,list) and len(et)==2 and set(map(norm,et))==set(map(norm,GOLD[m]))
        eord=isinstance(et,list) and [norm(x) for x in et]==[norm(x) for x in GOLD[m]]
        ml=miss.get("bowlers"); both_list=isinstance(ml,list) and isinstance(et,list) and set(map(norm,ml))==set(map(norm,et))
        both_u=mu and ev.get("uncertain") is True
        rows.append({"match":m,"model":mod,"mok":mok,"eok":eok,"eord":eord,"both":mok and eok,"same":both_list,"bothu":both_u,"miss":miss,"ev":ev})
agg=Counter()
for x in rows:
    for k in ("mok","eok","eord","both","same","bothu"): agg[k]+=int(x[k])
L=["# 0008 / 0010 排名缺证—最少补证对照","","## 1. 协议","", "- 先查完全匹配：这两场在 uncertainty 协议下的既有任务为 0；B255 的 top-2 题强制两名，不能复用。","- 冻结新版本 V2：两臂同题面、同输出协议，均允许 {\"uncertain\": true, \"missing\": ...}；不再强制两名。","- 缺证臂：N2 原文。补证臂：原文末尾加一句。","- 0008 加：Additional evidence: Evan Reed conceded 27 runs.","- 0010 加：Additional evidence: Luke Barrett conceded 38 runs.","- 2 场 ×2 版本 ×3 模型 =12 次本地调用；外部 API 0。","","## 2. 金标与所缺信息","","| 场 | 改判后 top-2 | 缺证臂应指出 |","|---|---|---|","| match_0008 | Ryan Frost, Evan Reed | Evan Reed 的 27 runs（与 Barrett 30 比较） |","| match_0010 | Evan Turner, Luke Barrett | Luke Barrett 的 38 runs（与 Foster 48 比较） |","","## 3. 首页结果","","| 指标 | 结果 |","|---|---|","| 缺证时正确指出所缺信息 | "+str(agg["mok"])+"/6 |","| 补证后给出合法名单（成员集合） | "+str(agg["eok"])+"/6 |","| 两种条件都答对（主结果） | "+str(agg["both"])+"/6 |","| 两次都猜同一名单 | "+str(agg["same"])+"/6 |","| 两次都答不确定 | "+str(agg["bothu"])+"/6 |","","## 4. 分模型","","| 模型 | 缺证正确 | 补证合法 | 两者都对 | 两次同名单 |","|---|---:|---:|---:|---:|"]
for mod in MS:
    rr=[x for x in rows if x["model"]==mod]
    L.append("| "+MS[mod]+" | "+str(sum(x["mok"] for x in rr))+"/2 | "+str(sum(x["eok"] for x in rr))+"/2 | "+str(sum(x["both"] for x in rr))+"/2 | "+str(sum(x["same"] for x in rr))+"/2 |")
L+=["","## 5. 逐对输出","","| 场 | 模型 | 缺证输出 | 补证输出 | 缺证对 | 补证对 |","|---|---|---|---|---|---|"]
for x in rows: L.append("| "+x["match"]+" | "+MS[x["model"]]+" | "+json.dumps(x["miss"],ensure_ascii=False)+" | "+json.dumps(x["ev"],ensure_ascii=False)+" | "+str(x["mok"])+" | "+str(x["eok"])+" |")
L+=["","## 6. 解释","","- 12 次输出全部给出两名投手，没有一次使用 uncertain 选项；缺证臂没有指出所缺的 runs。","- 补证后也没有产生合法名单：0008 三模型都未选 Evan Reed；0010 只有 Qwen 选到 Evan Turner，但第二人仍是 Ryan Foster。","- 结论：缺证—补证对照为负；模型在缺证时自信猜测，补一条数字不足以纠正成员集合。",""]
(ROOT/"RANK_EVIDENCE_REPORT.md").write_text("\n".join(L),encoding="utf-8")
print(json.dumps(dict(agg),ensure_ascii=False))
