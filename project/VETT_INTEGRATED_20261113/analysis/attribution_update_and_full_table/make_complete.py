from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_update_and_full_table"
front = """# VETT 改判更新诊断 + 首批整表试点：完整报告

日期：2026-11-13  
范围：6 场开发改判（A/B/C）、Lina 通路、重测、6 场整表试点  
预算：本地 Ollama，实际 84/120 次请求，外部 API 0；历史 0/42 保留。

## 0. 一页摘要

**改判诊断**

| 模型 | A two | B two | C two | A/B total | C total |
|---|---:|---:|---:|---:|---:|
| qwen | 0/6 | 0/6 | 0/6 | 2/6 / 2/6 | 2/6 |
| llama | 0/6 | 0/6 | 0/6 | 4/6 / 4/6 | 2/6 |
| gemma | 0/6 | 0/6 | 1/6 | 3/6 / 3/6 | 3/6 |

- 修好的完整短证据（B）没有救回改判：B 的两名投手同时正确 0/18，A 也 0/18，B−A=0。
- C 的分步作答只有 gemma 在 match_0014 做对两人（1/6）。
- C 的同输出 Python 更新：0 场修对、0 场改坏、1 场无法执行；抽取本身几乎都错。
- 主要错法仍是两人都旧值：gemma 6/6、qwen 6/6、llama 3/6（A）/5/6（B）。

**整表试点**

- 43 字段、6 场、18 次；qwen/gemma 6/6 解析，done=stop，eval 518–576，无截断。
- 可答字段准确率：qwen 12.2/43（28.3%），gemma 14.2/43（32.9%），llama 0/43（格式失败，非截断）。
- 缺行：qwen/gemma 0；llama 43 字段全缺。
- 下一批先修 llama 的 JSON 协议、补逐字段文本依据、加闭合账目。

## 1. 证据修复

- match_0014 总出局改为 Harbor Peninsula XI closed on 226 for 7。
- match_0016 总出局改为 Crestline XI closed on 138 for 3。
- B/C 均含 the bowling figures above are the pre-revision record 与正式通知。
- B 去标记后与 A 逐字一致；6 个标记；无更新后的 figures；6/6 通过。

## 2. 开发集逐场观察

- match_0014：gemma C 做对两人（Quinn 1/36、Frost 3/39、total 7），A/B 仍旧值；qwen/llama 仍错。
- match_0016：三家 A/B/C 都没有同时改对；total 3 的读取不是主要障碍。
- Lina：gemma original/explicit 五项全对，derivation 回旧值；qwen 两人 wickets 对但 total 恒 9。

## 3. 整表逐场

| match | qwen | gemma | llama |
|---|---:|---:|---|
| 0003 | 17/43 | 18/43 | 格式失败 |
| 0008 | 12/43 | 14/43 | 格式失败 |
| 0010 | 6/43 | 11/43 | 格式失败 |
| 0012 | 15/43 | 17/43 | 格式失败 |
| 0015 | 11/43 | 11/43 | 格式失败 |
| 0017 | 12/43 | 14/43 | 格式失败 |

## 4. 四句话

1. 修好的短证据让 0 个模型、0 场多做对两名投手：B 0/18，A 0/18，B−A=0；总出局数 B 与 A 相同。
2. 最常见错误是两人都旧值（gemma 6/6、qwen 6/6、llama 3/6），其次是只加新投手、两人都改但值错；gemma 的 match_0014 是唯一 C 修对两人的反例。
3. Python 用同一份抽取修好 0 场、改坏 0 场、1 场无法执行；抽取本身错，程序没有正确输入。
4. 首批整表 43 字段可答，qwen 28.3%、gemma 32.9% 逐项正确，llama 格式失败；下一批先修 llama JSON 与逐字段依据/闭合账目，再扩 220 场。

## 5. 缺口

- 未跑 4 场新比赛复验（预算/时间）；开发结论为探索性。
- 整表可答性未逐字段做“文本是否提到”的映射，准确率按全部 43 字段计。
- llama 的格式失败原因未逐条定位；未跑无改判对照。
"""
parts=[front]
for name,title in [("DESIGN.md","附录 A：DESIGN"),("EVIDENCE_AUDIT.md","附录 B：EVIDENCE_AUDIT"),("ATTRIBUTION_RESULTS.md","附录 C：ATTRIBUTION_RESULTS"),("FULL_TABLE_PILOT.md","附录 D：FULL_TABLE_PILOT"),("BLIND_REVIEW.md","附录 E：BLIND_REVIEW"),("ANSWER_KEY.md","附录 F：ANSWER_KEY"),("REPRODUCE.md","附录 G：REPRODUCE")]:
    parts.append(chr(10)*2+"---"+chr(10)*2+"# "+title+chr(10)*2)
    parts.append((P/name).read_text(encoding="utf-8"))
out="".join(parts)
(P/"COMPLETE_REPORT.md").write_text(out,encoding="utf-8")
print("wrote",len(out))
