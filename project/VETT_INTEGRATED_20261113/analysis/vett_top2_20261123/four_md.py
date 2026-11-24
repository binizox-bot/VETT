import json
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_top2_20261123")
R=json.loads((ROOT/"FOUR_PAIRED.json").read_text(encoding="utf-8"))
MS={"qwen2.5:7b-instruct-q4_K_M":"Qwen","llama3.1:8b":"Llama","gemma2:9b":"Gemma"}
def n(arm,k,model=None): return sum(1 for x in R if x["arm"]==arm and x[k] and (model is None or x["model"]==model))
L=["# 四根小规模复验：直接整表 / 独立选人 / 带自选名单整表","","## 1. 方法","", "- 4 根：match_0170、match_0096、match_0049、match_0180；每根维持+改判 ×3 模型。","- 直接整表 24 次、独立选人 24 次、带自选名单整表 24 次，共 72 次；后者的名单来自同场同模型独立选人。","- 主指标：合法 top-2 两人、各自 wickets/runs、局总 wickets 同时正确。",""]
L+=["## 2. 主指标（/12 每通知）","","| 通知 | 直接整表 | 独立选人成员对 | 带名单整表 | 直接→带名单救回 | 直接→带名单改坏 |","|---|---:|---:|---:|---:|---:|"]
for arm in ("N1","N2"):
    trans=Counter()
    for x in R:
        if x["arm"]!=arm: continue
        if x["dok"] and not x["hok"]: trans["bad"]+=1
        if not x["dok"] and x["hok"]: trans["good"]+=1
    L.append("| "+arm+" | "+str(n(arm,"dok"))+"/12 | "+str(n(arm,"tmem"))+"/12 | "+str(n(arm,"hok"))+"/12 | "+str(trans["good"])+" | "+str(trans["bad"])+" |")
L+=["","## 3. 分模型","","| 模型 | 通知 | 直接整表 | 独立成员 | 带名单整表 |","|---|---|---:|---:|---:|"]
for mod in MS:
    for arm in ("N1","N2"):
        L.append("| "+MS[mod]+" | "+arm+" | "+str(n(arm,"dok",mod))+"/4 | "+str(n(arm,"tmem",mod))+"/4 | "+str(n(arm,"hok",mod))+"/4 |")
L+=["","## 4. 代价与副作用","","- 直接整表：24 次调用；独立选人：24 次；带名单整表：24 次（另复用同批独立名单，不额外调用）。总计 72 次。","- 带名单相对直接：其他有依据字段退步 "+str(sum(x["reg"] for x in R))+" 格，改善 "+str(sum(x["gain"] for x in R))+" 格。","- 自选名单错误被带入整表："+str(sum(1 for x in R if x["carry"]))+" 例。"]
for x in R:
    if x["carry"]: L.append("  - "+x["match"]+" "+x["arm"]+" "+MS[x["model"]]+" 名单="+json.dumps(x["hlist"],ensure_ascii=False))
L+=["","## 5. 逐例配对","","| 比赛 | 通知 | 模型 | 独立名单 | 直接 | 带名单 | 其他字段退步 |","|---|---|---|---|---|---|---:|"]
for x in R: L.append("| "+x["match"]+" | "+x["arm"]+" | "+MS[x["model"]]+" | "+json.dumps(x["hlist"],ensure_ascii=False)+" | "+("对" if x["dok"] else "错")+" | "+("对" if x["hok"] else "错")+" | "+str(x["reg"])+" |")
L+=["","## 6. 开发案例","","match_0003 / N1 的 3 次提示回投：0 次救回，1 次改坏原本正确的 Llama，1 次格式失败；见 DEV_CASE_0003.md。",""]
(ROOT/"FOUR_ROOT_REPORT.md").write_text("\n".join(L),encoding="utf-8")
print("ok",len(R))
