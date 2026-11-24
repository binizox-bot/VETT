import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"pilot_next"
samples=json.loads((ROOT/"samples.json").read_text(encoding="utf-8"))
lina=json.loads((ROOT/"lina.json").read_text(encoding="utf-8"))["cases"]
models=[("qwen2.5:7b-instruct-q4_K_M","845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e","Q4_K_M"),
        ("llama3.1:8b","46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e","Q4_K_M"),
        ("gemma2:9b","ff02c3702f322b9e075e9568332d96c0a7028002f1a5a056e0a6784320a4db0b","Q4_0")]
L=["# Pilot-Next 设计：跨局串值与局号标注","",
   "日期：2026-11-13。外部 API 预算 0；本地 Ollama 三模型；请求上限 120。","",
   "## 1. 问题","",
   "1. 同一批证据段完整换位后，模型会不会把另一局的同名字段值填进目标局？在证据旁写清局号能减少多少？",
   "2. 给改判前投手数据 + 一次具体改判，模型能否同时更新两名投手并保持全队总数？","",
   "## 2. 模型","","| tag | digest | quant |","|---|---|---|"]
for t,d,q in models: L.append(f"| {t} | {d} | {q} |")
L += ["","上下文 8192；temperature=0；seed=20261112；num_predict=300。","",
      "## 3. 留出比赛与字段","",
      "来源：220 场中 closure-clean 且未参与 Pilot-10 / case audit 的比赛；按 scorecard sha256 去重；文本为 scorecard 的确定性重渲染（seed=0），不是发布 commentary。","",
      "| match | tokens | result | inn1/inn2 total_extras | wides | leg_byes |","|---|---:|---|---|---|---|"]
for s in samples:
    p={x["name"]:(x["inn1"],x["inn2"]) for x in s["pairs"]}
    L.append(f"| {s['match']} | {s['tokens']} | {s['result'][:32]} | {p['total_extras'][0]}/{p['total_extras'][1]} | {p['wides'][0]}/{p['wides'][1]} | {p['leg_byes'][0]}/{p['leg_byes'][1]} |")
L += ["","每场 3 对字段（6 个目标字段），两局值均不同。","",
      "## 4. 四条件","",
      "| 条件 | 顺序 | 局号 |","|---|---|---|",
      "| A | 原顺序 | 无 |","| B | 证据段移到本局末尾 | 无 |",
      "| C | 原顺序 | 证据段前加 First/Second innings |","| D | 同 B | 同 C |","",
      "证据段：inn1 的 \"The total included ... extras\"（若紧跟 \"Another ... byes/leg-byes\" 则一起移动）；inn2 的 \"The sundries column read ...\"。移动只在各自局内进行。","",
      "不变量已逐场检查：A/B、C/D 句子多重集相同；A/C、B/D 去掉标签后逐字相同；标签只含 \"First innings: \"/\"Second innings: \"，不含数字；四版金标相同。","",
      "## 5. Lina Fox 三题面",""]
for k in ["original","explicit","derivation"]:
    L.append(f"- {k}: gold {lina[k]['gold']}")
L += ["","derivation 版 = 原 control 全文 + 一条改判通知（不给新 figures）；已检查全文没有 \"3 for 6\" / \"4 for 7\"，\"4/7\" 只出现在比分 44/7 中。","",
      "## 6. 提示与输出","",
      "system 要求只返回 JSON：{\"fields\": {<field_id>: <integer>}}，无法确定用 UNKNOWN；固定字段清单；同一提示用于所有模型与条件。Lina 额外请求 evidence 字符串。","",
      "## 7. 预算","",
      "smoke 2 + main 8×4×3=96 + Lina 3×3=9 + 重测 2 场×3 模型×A=6 = 113（≤120）。","",
      "## 8. 指标","",
      "- 字段准确率：逐场 + 比赛宏平均。",
      "- 另一局同字段命中：预测错值 == 另一局同名字段金标；分母为全部 6 字段，另报在数值错例中的比例；0 等易撞值单独标注。",
      "- 转移：A→B、C→D 的对→错/错→对/净变化；B→D 与 A→C 比较局号效果。",
      "- 解析/覆盖：格式失败、漏字段、有效输出；重测作波动参照。","",
      "## 9. 文件","",
      "samples.json、lina.json、runs/*.jsonl、score 脚本、RESULTS.md。"]
(ROOT/"DESIGN.md").write_text("\n".join(L)+"\n",encoding="utf-8")
cfg={"schema":"vett.pilot_next.config.v1","models":[{"tag":t,"digest":d,"quant":q} for t,d,q in models],
     "num_ctx":8192,"num_predict":300,"temperature":0,"seed":20261112,
     "budget":120,"smoke":2,"main":96,"lina":9,"retest":6,
     "samples":[s["match"] for s in samples]}
(ROOT/"config.json").write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8")
print("DESIGN.md lines",len(L))
