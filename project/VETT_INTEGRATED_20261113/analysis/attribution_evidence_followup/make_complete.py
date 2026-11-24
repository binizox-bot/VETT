from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_evidence_followup"
front = """# VETT 证据标注跟进：完整报告

日期：2026-11-13  
范围：旧结果复算、A/B/C 受控实验、6 场新比赛 A/B 复验、整表评测准备  
预算：本地 Ollama，实际 120/120 次请求，外部 API 0 次；历史结果只读。

## 0. 一页摘要

**问题 1：全文不变，只标出相关原句，模型会不会更容易把两名投手都改对？**

不会。开发集 8 场、留出集 6 场、3 个模型，B−A 在“两名投手同时正确”上全部为 0；三项同时正确也全部为 0。B 与 A 的输出逐场相同或几乎相同。

**问题 2：给足够原文证据后，剩余错误在哪一步？**

不在“找不到证据”：

- A/B 全文相同，只多 [EVIDENCE] 标记；模型仍以两人旧值为主（gemma 7/8、qwen 6/8、llama 4/8）。
- Lina 的 gemma 在明示版能抄 3/6、4/7，推导版回到 4/6、3/7；说明卡在把改判应用到最终数值，不是读不到数字。
- llama 还有“只加新投手/两人都改但值错”的错法；qwen 有字段名坍缩的格式失败。

**C 的构建缺陷**：C 漏了 A 中“the bowling figures above are the pre-revision record”的 Note，旧汇总没有状态标签。C 的总出局数改善（gemma +1、llama +2、qwen +2 场）只能作为探索，两名投手仍 0/8，不能当作“证据足够”的严格结论。

## 1. 旧结果复算

- 三项同时正确 0/24；两名投手都旧值且总数正确 **11/24**；只要求两人旧值则 18/24。
- 推导→短证据 two_wickets：qwen 7 场错→对、gemma 7、llama 1；没有对→错。
- Llama 短证据 1/8：唯一正确的 match_0003 总数也正确；“两人已对但总数错”为 0。
- 旧 method 的 parse_ok=0/8 是 runner 用 fields 键误判；doc 实际 8/8 可解析，但抽取值错，Python 更新后 qwen 0/8、llama 1/8、gemma 1/8。

## 2. 开发集 A/B/C（8 场）

| 模型 | 条件 | two_wickets | total | three |
|---|---|---:|---:|---:|
| qwen | A | 0/8 | 2/8 | 0/8 |
| qwen | B | 0/8 | 2/8 | 0/8 |
| qwen | C | 0/8 | 4/8 | 0/8 |
| llama | A | 0/8 | 6/8 | 0/8 |
| llama | B | 0/8 | 6/8 | 0/8 |
| llama | C | 0/8 | 8/8 | 0/8 |
| gemma | A | 0/8 | 7/8 | 0/8 |
| gemma | B | 0/8 | 7/8 | 0/8 |
| gemma | C | 0/8 | 8/8 | 0/8 |

## 3. 留出集 A/B（6 场）

| 模型 | A two | B two | A total | B total |
|---|---:|---:|---:|---:|
| qwen | 0/6 | 0/6 | 3/6 | 2/6 |
| llama | 0/6 | 0/6 | 3/6 | 3/6 |
| gemma | 0/6 | 0/6 | 3/6 | 3/6 |

## 4. 典型样例（match_0008）

gold：Luke Barrett 3→2、Ryan Frost 3→4、total 10。

- gemma A/B 都输出 3、3、10。
- qwen A/B 都输出 3、3、8。
- llama A 输出 4、4、10；B 输出 4、4、10；C 输出 3、4、10。
- 标注没有让 gemma/qwen 更新；llama 的 C 只更新了新投手。

## 5. Lina 与重测

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 字段名坍缩，协议失败 |
| explicit | 3/6、4/7、10 五项全对 | 同上 |
| derivation | 4/6、3/7、10 旧值 | 同上 |

重测：qwen/llama/gemma 在 match_0008、match_0017 的 A 条件均 5/5 一致。

## 6. 四句话

1. **同样的全文里只标出原句，在 0 场新比赛、0 个模型上有帮助**：开发 8 场和留出 6 场的 B−A 在两名投手同时正确上都是 0，三项同时正确也都是 0。
2. **开发集里删掉其他正文（C）只多做对了总出局数（gemma +1、llama +2、qwen +2 场），两名投手仍是 0/8**；但 C 漏了“旧汇总是改判前记录”的 Note，这个收益不能当作“证据足够”的证据。
3. **剩余错误主要不是“找不到证据”**：A/B 全文相同、只多标记，模型仍以两人旧值为主（gemma 7/8、qwen 6/8、llama 4/8）；Lina 的 gemma 在明示版能抄 3/6、4/7，推导版回到 4/6、3/7，说明卡在把改判应用到最终数值。
4. **220 场整表评测还差三件**：原始解说与 scorecard 的字段映射、可靠计分范围（目前 28 个核心字段，完整表约 450 cell 需要分块输出）、输出预算/截断控制；下一轮最值得投入的是改判应用/事件更新的结构化对照，而不是继续加证据标注。

## 7. 文件

- DESIGN.md、BASELINE_REANALYSIS.md、RESULTS.md、FULL_TABLE_READINESS.md、BLIND_REVIEW.md、ANSWER_KEY.md
- dev.json、holdout.json、lina.json
- runs/dev.jsonl、hold.jsonl、lina.jsonl、retest.jsonl
- scores.json、baseline_details.json
- runner.py、score.py、build_evidence.py
"""
parts=[front]
for name,title in [("DESIGN.md","附录 A：DESIGN.md 全文"),("BASELINE_REANALYSIS.md","附录 B：BASELINE_REANALYSIS.md 全文"),("RESULTS.md","附录 C：RESULTS.md 全文"),("FULL_TABLE_READINESS.md","附录 D：FULL_TABLE_READINESS.md 全文"),("ANSWER_KEY.md","附录 E：ANSWER_KEY.md 全文"),("BLIND_REVIEW.md","附录 F：BLIND_REVIEW.md 全文")]:
    parts.append(chr(10)*2+"---"+chr(10)*2+"# "+title+chr(10)*2)
    parts.append((P/name).read_text(encoding="utf-8"))
out="".join(parts)
(P/"COMPLETE_REPORT.md").write_text(out,encoding="utf-8")
print("wrote",len(out))
