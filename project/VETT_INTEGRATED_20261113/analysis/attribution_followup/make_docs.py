import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
OUT=ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
samples=json.loads((OUT/"samples.json").read_text(encoding="utf-8"))
lina=json.loads((OUT/"lina.json").read_text(encoding="utf-8"))["cases"]
models=[("qwen2.5:7b-instruct-q4_K_M","845dbda0ea48…","Q4_K_M"),
        ("llama3.1:8b","46e0c10c039e…","Q4_K_M"),
        ("gemma2:9b","ff02c3702f32…","Q4_0")]
L=["# Attribution Followup 设计","",
   "日期：2026-11-13。本地 Ollama，外部 API 0，预算上限 120。","",
   "## 1. 模型","","| tag | digest | quant |","|---|---|---|"]
for t,d,q in models: L.append(f"| {t} | {d} | {q} |")
L += ["","temperature=0，seed=20261112，num_ctx=8192，num_predict=320。","",
      "## 2. 样本","",
      "从 220 场源池选 8 场，均未用于 Pilot-10 / Pilot-Next / 本轮调试；文本为 scorecard 重渲染（seed=0），因此这是**基于比赛记录构造的改判**，不是真实赛果更正。","",
      "| match | innings | batter | 原投手 A | A 旧 | 新投手 B | B 旧 | 本局总出局 | 新 gold |","|---|---|---|---|---|---|---|---|---|"]
for s in samples:
    L.append(f"| {s['match']} | {s['innings']} | {s['batter']} | {s['A']} | {s['Aw']}/{s['Ar']} | {s['B']} | {s['Bw']}/{s['Br']} | {s['total']} | {s['A']} {s['Aw']-1}/{s['Ar']}；{s['B']} {s['Bw']+1}/{s['Br']}；total {s['total']} |")
L += ["","## 3. 三个版本","",
      "| 版本 | 内容 |","|---|---|",
      "| explicit | 全文；改判句改为 B；A/B 汇总已更新；附改判通知 |",
      "| derivation | 全文；保留旧改判句与旧汇总；附“以下是改判前记录”和改判通知 |",
      "| short | 只摘出出局记录、旧汇总、改判通知、本局总出局数 |","",
      "不变量：explicit 含更新后的 A/B 汇总；derivation/short 不含更新后的汇总（按 figures 短语检查）；三版 gold 相同。","",
      "## 4. 字段与评分","",
      "五字段：A_wickets、A_runs、B_wickets、B_runs、innings_total_wickets。",
      "主指标：A_wickets、B_wickets、innings_total_wickets 三项同时正确。",
      "另报：两个 runs 字段同时正确；五字段同时正确。",
      "错误分类：两人都旧值；只给 B +1；只给 A −1；两人都改但值错；wicket 对但 total/runs 错；格式/漏字段。","",
      "## 5. 运行计划","",
      "main 8×3×3=72；Lina 3×3=9；retest 2×3=6；method 8×3=24；smoke 1–2。合计 112–113 / 120。","",
      "## 6. 方法对照","",
      "method：模型只抽取出局事件与旧数值（batter、原/新投手、双方旧 wickets/runs、总出局），Python 执行 A−1、B+1、runs/total 不变。与 short 版同一批比赛/模型比较；另标程序正控。",""]
(OUT/"DESIGN.md").write_text("\n".join(L),encoding="utf-8")

B=["# BLIND_REVIEW：改判题面（人工独立核对）","",
   "每场三版：explicit / derivation / short。请对五字段写出值、依据句、可答性；不要打开 ANSWER_KEY.md。",""]
for s in samples:
    B.append(f"## {s['match']} — {s['innings']} — {s['batter']} 的出局")
    for v in ["explicit","derivation","short"]:
        B.append(f"### {v}")
        B.append("----- BEGIN TEXT -----")
        B.append(s["texts"][v])
        B.append("----- END TEXT -----")
        B.append("作答：")
        for k in s["fields"]:
            B.append(f"- {k} = ____ ；依据句：____")
        B.append("")
    B.append("---")
(OUT/"BLIND_REVIEW.md").write_text("\n".join(B),encoding="utf-8")

K=["# ANSWER_KEY：改判样本金标",""]
for s in samples:
    K.append(f"## {s['match']} — {s['innings']} — {s['batter']}")
    K.append("")
    K.append("| 字段 | 值 |")
    K.append("|---|---:|")
    for k,v in s["fields"].items(): K.append(f"| {k} | {v} |")
    K.append("")
    K.append(f"- 旧改判句：{s['evidence']['dismissal_old']}")
    K.append(f"- 新改判句：{s['evidence']['dismissal_new']}")
    K.append(f"- 旧汇总 A：{s['evidence']['A_old']}；旧汇总 B：{s['evidence']['B_old']}")
    K.append(f"- 通知：{s['evidence']['notice']}")
    K.append("")
K.append("## Lina Fox 开发样例")
for c in ["original","explicit","derivation"]:
    K.append(f"- {c}: {lina[c]['gold']}")
(OUT/"ANSWER_KEY.md").write_text("\n".join(K),encoding="utf-8")
print("docs",len(L),len(B),len(K))
