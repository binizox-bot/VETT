import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_evidence_followup"
dev=json.loads((P/"dev.json").read_text(encoding="utf-8")); hold=json.loads((P/"holdout.json").read_text(encoding="utf-8"))
L=["# Attribution Evidence Followup 设计","",
   "日期：2026-11-13。本地 Ollama 三模型；预算 120；实际 120；外部 API 0。","",
   "## 1. 模型","",
   "| tag | digest | quant |","|---|---|---|",
   "| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48… | Q4_K_M |",
   "| llama3.1:8b | 46e0c10c039e… | Q4_K_M |",
   "| gemma2:9b | ff02c3702f32… | Q4_0 |","",
   "temperature=0，seed=20261112，num_ctx=8192，num_predict=300。","",
   "## 2. 样本","",
   "开发集：上一轮 8 场（match_0003、0008、0010、0012、0015、0017、0026、0030），复用其全文推导版作为 A。",
   "留出集：6 场未用于前几轮（match_0009、0013、0014、0016、0018、0027），由 scorecard 重渲染并构造改判。",
   "文本来源：scorecard 重渲染（seed=0），属于基于比赛记录构造的改判，不是真实赛果更正。","",
   "## 3. 条件","",
   "| 条件 | 内容 |","|---|---|",
   "| A | 全文：完整解说 + 旧汇总 + 改判通知 |",
   "| B | A 逐字保留，只在五处相关原句前加 [EVIDENCE] |",
   "| C | 从 B 原样摘出五个标记句，保持顺序、措辞、数字写法 |","",
   "五处证据：原出局记录、原投手旧汇总、新投手旧汇总、本局总出局依据、改判通知。","",
   "逐场检查（构建脚本）：B 去掉标记后与 A 逐字一致；C 保留五个标记；C 不含更新后的 figures；五处证据可定位。","",
   "**已发现的构建问题**：C 没有包含 A 中“the bowling figures above are the pre-revision record”的 Note 句，因此 C 缺少“旧汇总”的状态标签。C 的结果只能作为探索，不能作为“证据足够”的严格条件。","",
   "## 4. 字段与评分","",
   "五字段：原投手 wickets_credited、bowling_runs_conceded；新投手同两项；innings_wickets_lost。",
   "主指标：两名投手 wickets 同时正确（two_wickets）。",
   "辅助：本局总出局正确、三项同时正确、两项失分正确、五项同时正确。",
   "错误分类：两人都旧值；只加新投手；只减原投手；方向反了；两人都改但值错；格式失败。","",
   "## 5. 运行","",
   "开发 8×3×3=72；留出 6×2×3=36；Lina 3×2=6；重测 2×3=6；合计 120。","",
   "## 6. 备注","",
   "C 的缺失 Note 是本轮题面缺陷；A/B 的比较不受影响。"]
(P/"DESIGN.md").write_text("\n".join(L),encoding="utf-8")

B=["# BLIND_REVIEW：人工核对题面（A 全文）","",
   "每场给 A 全文、五个字段和作答位。B 只是 A 加 [EVIDENCE]；C 是五个标记句的摘录（缺 pre-revision Note，见 DESIGN）。",""]
for s in dev+hold:
    B.append(f"## {s['match']} — {s['batter']} — {s['A_name']} -> {s['B_name']}")
    B.append("----- BEGIN TEXT -----")
    B.append(s["A"])
    B.append("----- END TEXT -----")
    B.append("作答：")
    for k in s["fields"]:
        B.append(f"- {k} = ____ ；依据句：____")
    B.append("")
(P/"BLIND_REVIEW.md").write_text("\n".join(B),encoding="utf-8")

K=["# ANSWER_KEY：证据跟进金标",""]
for s in dev+hold:
    K.append(f"## {s['match']} — {s['batter']}")
    K.append("")
    K.append("| 字段 | 值 |")
    K.append("|---|---:|")
    for k,v in s["fields"].items(): K.append(f"| {k} | {v} |")
    K.append("")
    K.append(f"- 出局旧记录：{s['evidence']['dis']}")
    K.append(f"- 原投手旧汇总：{s['evidence']['sumA']}")
    K.append(f"- 新投手旧汇总：{s['evidence']['sumB']}")
    K.append(f"- 总出局依据：{s['evidence']['total']}")
    K.append(f"- 改判通知：{s['evidence']['notice']}")
    K.append("")
(P/"ANSWER_KEY.md").write_text("\n".join(K),encoding="utf-8")
print("docs",len(L),len(B),len(K))
