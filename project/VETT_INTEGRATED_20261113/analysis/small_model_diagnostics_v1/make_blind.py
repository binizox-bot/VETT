import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v1"
samp=json.loads((P/".."/"answerability_and_short_evidence"/"sample.json").read_text(encoding="utf-8"))
B=["# BLIND_REVIEW：40 格可答性复核（全文本版）","",
   "复核者先只看原文和任务作答，再对 scorecard。每场完整解说见 texts/ 目录，段落编号可直接引用。","",
   "排名规则：旧任务按 runs/wickets 降序；并列按 scorecard 行序；旧提示未定义并列，属于旧任务歧义。",""]
for x in samp:
    B.append(f"## {x['sample_id']} {x['match']} / {x['field']}")
    B.append(f"- 原文：[texts/{x['match']}.md](texts/{x['match']}.md)（段落编号见文件）")
    B.append(f"- 字段：{x['field']}；局别按字段名；统计时点：该局结束时")
    B.append("- 候选句（可选索引，不替代全文）：")
    if x.get("evidence"): B.append(f"  - {x['evidence']}")
    B.append("- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____")
    B.append("")
(P/"BLIND_REVIEW.md").write_text("\n".join(B),encoding="utf-8")
print(len(B))
