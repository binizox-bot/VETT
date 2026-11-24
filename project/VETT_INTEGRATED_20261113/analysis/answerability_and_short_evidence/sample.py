import json,random,sys
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; O=INT/"analysis"/"answerability_and_short_evidence"
sys.path.insert(0,str(INT/"scripts")); import pilot_lib as L
FA=[json.loads(l) for l in (INT/"analysis"/"input_and_score_audit"/"FIELD_ANSWERABILITY.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
rng=random.Random(20261113)
un=[x for x in FA if x["status"]=="insufficient"]
co=[x for x in FA if x["status"] in ("direct","derived")]
def spread(pool,n):
    picks=[]; by={}
    for x in pool: by.setdefault(x["match"],[]).append(x)
    keys=list(by)
    while len(picks)<n and keys:
        for k in list(keys):
            if by[k] and len(picks)<n: picks.append(by[k].pop(rng.randrange(len(by[k]))))
            if not by[k]: keys.remove(k)
    return picks
samp=spread(un,30)+spread(co,10)
for i,x in enumerate(samp,1): x["sample_id"]=f"S{i:02d}"
(O/"sample.json").write_text(json.dumps(samp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
B=["# BLIND_REVIEW：43 字段可答性抽查（40 格）","",
   "复核者先独立作答，再与 scorecard 对账。题面只给发布版 commentary 路径与相关句，不展示模型预测。","",
   "排名规则（旧任务）：按 scorecard 的 runs/wickets 降序；并列时按 scorecard 行序；旧提示未写并列规则，这一点需复核者判断。",""]
for x in samp:
    text=(L.DATASET/x["match"]/"commentary.txt").read_text(encoding="utf-8")
    ss=L.sentences(text); key=str(x["gold"])
    rel=[s for s in ss if key.lower() in s.lower()][:3]
    B.append(f"## {x['sample_id']} {x['match']} {x['field']}")
    B.append(f"- 原文：{L.DATASET/x['match']}/commentary.txt")
    B.append(f"- 目标字段：{x['field']}；指定局别按字段名；金标不展示")
    B.append("- 相关句：")
    for s in rel: B.append(f"  - {s}")
    B.append("- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____")
    B.append("")
(O/"BLIND_REVIEW.md").write_text("\n".join(B),encoding="utf-8")
print("sample",len(samp),"un",sum(x["status"]=="insufficient" for x in samp),"conf",sum(x["status"]!="insufficient" for x in samp))
