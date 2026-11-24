# VETT 小模型诊断 v1：完整报告

日期：2026-11-13  
范围：43 字段 V3 复核、两场抽取诊断、数据集升级  
调用：新增 6/24 次；外部 API 0。

## 0. 一页摘要

- 同一份 B 短证据：直接最终值 two **0/6**；纯抽取 6/6 全部正确（出局者、原/新投手、方向、两个旧 wicket）；用实际抽取做 Python 更新，**two 6/6**。
- 具体错误是**最终值更新**，不是读旧数、认人或弄反方向。
- 43 字段 V3 仍为 73/258；Qwen 29/73、Gemma 32/73、Llama 26/73；185 待核。
- 40 格盲审已升级为全文 + 段号 + 候选句；人工未返回。
- 数据集升级：新增“同一 B 文本 + 纯抽取”配对条件；C 拆成纯抽取；评分分 identity/direction/old/final/program 五步。

## 1. 诊断核心

| 环节 | 结果 |
|---|---|
| JSON 解析 | 6/6 |
| 五键齐全 | 6/6 |
| 出局者正确 | 6/6 |
| 原/新投手正确 | 6/6 |
| 方向正确 | 6/6 |
| 两个旧 wicket 正确 | 6/6 |
| 程序更新后 two | 6/6 |
| 直接最终值 two | 0/6 |

0014：Quinn 2→1、Frost 2→3；0016：Reed 2→1、Wells 1→2。  
同一文本、同一模型，抽取全对而最终值全错，说明模型知道事件，但不会把 −1/+1 落到最终答案。

## 2. 43 字段

- 73/258 可答（69 直接 + 4 可推导）；185 待核。
- 新增“同一句比分支持 total”规则，258 格变更 0。
- Qwen 29/73、Gemma 32/73、Llama 26/73；全字段 73/85/63。
- 40 格盲审全文已交付，人工未返回。

## 3. 四句话

1. **具体错误是最终值更新**：三个模型、两场比赛、6 条直接作答全部 two 错；同一文本纯抽取 6/6 正确。
2. **用同一 B 文本、同一模型做“直接最终值 vs 纯抽取”对照**，把“读证据”与“算最终值”分开；身份/方向/旧值全对而最终值全错，排除题面歧义和格式失败。
3. **数据集升级为配对条件**：保留直接输出，另加纯抽取 + Python 更新；C 不再一次要求 extraction+final；评分拆成五步。
4. **下一轮最值得验证“直接 vs 抽取+程序”在新比赛上的差异**：2 场 ×2 条件 ×3 模型 =12 次，需预先选 2 场干净比赛、冻结短证据与金标；同时等 40 格人工复核。

## 4. 缺口

- 40 格人工复核未返回；V3 73 格仍是启发式。
- 新比赛配对未跑（预算 18 剩余）；无改判正控未跑。
- 43 字段逐场 Llama 未拆同分母。
- 闭合约束仍不可检查。


---

# 附录 A：SMALL_MODEL_DIAGNOSTICS

# SMALL_MODEL_DIAGNOSTICS：改判错在哪一步

日期：2026-11-13。新增 6 次抽取请求（预算 24），外部 API 0。

## 0. 核心发现

同一份 B 短证据（572/571 字符）：

- 直接输出最终五项：两场 × 3 模型 = 6 条，**two_wickets 0/6**。
- 只要求抽取事实：6/6 全部 JSON 可解析、五键齐全、**出局者/原投手/新投手/方向/两个旧 wicket 数全部正确**。
- 用这 6 条实际抽取做 Python 更新：**6/6 两人最终绝对值同时正确**。

所以错误不在“读旧数、认人、弄反方向”，而在**把改判应用到最终数值**这一步；程序更新可以把 0/6 修到 6/6。

## 1. 逐条

| match | model | 出局者 | 原/新投手 | 旧 W | 程序 two |
|---|---|---|---|---|---|
| 0014 | Qwen | Elias Ward | Leo Quinn / Dylan Frost | 2 / 2 | 对 |
| 0014 | Llama | 同 | 同 | 2 / 2 | 对 |
| 0014 | Gemma | 同 | 同 | 2 / 2 | 对 |
| 0016 | Qwen | Adrian Clarke | Evan Reed / Connor Wells | 2 / 1 | 对 |
| 0016 | Llama | 同 | 同 | 2 / 1 | 对 |
| 0016 | Gemma | 同 | 同 | 2 / 1 | 对 |

金标：0014 Quinn 2→1、Frost 2→3；0016 Reed 2→1、Wells 1→2。  
程序更新：orig−1、new+1；6/6 得到正确 final。

## 2. 与直接作答对照

上一轮 B 直接作答：6 条 two 0/6；错法多为两人旧值，Llama 一场只加新投手。  
同一文本、同一模型、同一旧值，抽取全对而最终值全错，说明模型“知道发生了什么”，但不会把 −1/+1 落到最终答案。

## 3. C 的旧协议

上一轮 C 把 extraction 与 final fields 放在一个提示里，6/6 缺更新所需字段。  
本轮把任务拆成纯抽取后 6/6 成功，说明旧 C 的失败是**协议/输出结构**，不是事实不可得。

## 4. 格式与正控

- 抽取：6/6 解析、6/6 五键齐全、6/6 身份方向正确、6/6 旧值正确。
- 程序：6/6 two 正确；用正确结构化输入的正控 2/2 通过。
- 无改判正控未跑（预算保留）。

## 5. 结论

具体错误：**最终值更新**，不是证据读取或方向判断。  
这支持把“抽取 + Python 更新”作为独立条件，而不是继续让模型直接算最终五项。

---

# 附录 B：SCORECARD_RESCORE_V3

# SCORECARD_RESCORE_V3：258 字段复核与同分母成绩

日期：2026-11-13。0 次模型调用。

## 1. 可答性

- V3 仍为 **73/258**：直接 69 + 可推导 4；185 待核。
- 新增“同一句比分同时支持 total_runs 与 total_wickets”的规则；在 258 格上没有新增可答格（相关 total 字段已被旧规则覆盖或该句未匹配），变更 0 格。
- 40 格盲审已升级为全文本 + 段落编号（BLIND_REVIEW.md、texts/）；**人工结果未返回**。

## 2. 同分母 73

| 模型 | 可答答对 | 分母 | 准确率 | 全字段 |
|---|---:|---:|---:|---:|
| Qwen | 29 | 73 | 39.7% | 73/258 |
| Gemma | 32 | 73 | 43.8% | 85/258 |
| Llama | 26 | 73 | 35.6% | 63/258 |

Llama 5/6 嵌套 JSON 恢复，0008 空；相关格按错计。

## 3. 逐场

| match | 可答 | Qwen | Gemma | Llama |
|---|---:|---:|---:|---:|
| 0003 | 16 | 10 | 10 | — |
| 0008 | 12 | 5 | 5 | 0（空） |
| 0010 | 12 | 1 | 3 | — |
| 0012 | 11 | 4 | 6 | — |
| 0015 | 11 | 5 | 3 | — |
| 0017 | 11 | 4 | 5 | — |

Llama 只报总分 26/73；逐场未拆。

## 4. 分表与闭合

- 分表：比赛摘要、局汇总、击球行、投手行的覆盖与准确率沿用 43 字段预测；本轮未改变字段清单。
- 闭合：schema 缺 extras 合计与 bat_sum，记为不可检查。
- 格式：Qwen/Gemma 6/6；Llama 旧协议 0/6，展平后 5/6。

## 5. 限制

- 73 格是启发式，不是人工确认；40 格待返回。
- V3 规则未改变分母，不能宣称覆盖率提升。
- 缺答在 73 格中按错计。

---

# 附录 C：DATASET_CHANGELOG

# DATASET_CHANGELOG：从错例到下一版样本

## 1. 发现

| 错误 | 证据 | 出现范围 |
|---|---|---|
| 直接最终值不更新 | B 短证据 two 0/6 | 3 模型 × 2 场 |
| 抽取事实其实正确 | 抽取 6/6 身份/方向/旧值 | 同上 |
| 程序更新可修复 | 6/6 two 正确 | 同上 |
| 旧 C 协议缺字段 | 6/6 无法执行 | 3 模型 × 2 场 |

## 2. 修改

| 项 | 改法 | 核验 |
|---|---|---|
| 样本条件 | 新增“同一 B 文本 + 纯抽取”条件，与直接最终值配对 | 6/6 抽取成功 |
| 评分 | 分开 identity、direction、old values、final two、program two | 逐条记录 |
| C 协议 | 拆成纯抽取；不再要求一次输出 extraction+final | 6/6 可解析 |
| 可答性 | 新增同一句比分的 total 规则 | 258 格变更 0 |
| 盲审 | 全文 + 段号 + 候选句 | 40 格 |

## 3. 指标前后

- 直接 B：two 0/6 → 抽取后程序 two 6/6。
- C：旧协议 0/6 可执行 → 纯抽取 6/6 可执行。
- 43 字段：73/258 不变；Qwen 29/73、Gemma 32/73、Llama 26/73。

## 4. 还缺

- 40 格人工复核。
- 新比赛上的“直接 vs 抽取+程序”配对（2 场 ×2 条件 ×3 模型 =12）未跑。
- 无改判正控未跑。

---

# 附录 D：BLIND_REVIEW（40 格）

# BLIND_REVIEW：40 格可答性复核（全文本版）

复核者先只看原文和任务作答，再对 scorecard。每场完整解说见 texts/ 目录，段落编号可直接引用。

排名规则：旧任务按 runs/wickets 降序；并列按 scorecard 行序；旧提示未定义并列，属于旧任务歧义。

## S01 match_0003 / inn1.no_balls
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.no_balls；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S02 match_0008 / match.result
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S03 match_0010 / inn2.bat3_runs
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.bat3_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S04 match_0012 / inn1.wides
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.wides；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S05 match_0015 / inn2.wides
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.wides；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - A few wides arrived just when a quiet over was nearly secured, one no-ball smudged the rhythm, and the first stand grew into the sort of draining opening passage where a captain keeps feeling one mistake away from contro
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S06 match_0017 / match.result
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S07 match_0003 / inn2.byes
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn2.byes；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S08 match_0008 / inn1.total_wickets
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S09 match_0010 / inn1.bowl2_runs
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn1.bowl2_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S10 match_0012 / inn1.overs
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.overs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Mason took the longer route, not pretty every over but solid enough to make the middle overs matter, while Connor added the steadier scoring beside him, working gaps and punishing the loose ball without trying to turn th
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S11 match_0015 / inn1.total_wickets
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S12 match_0017 / inn1.total_runs
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.total_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S13 match_0003 / inn1.bowl2_wickets
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.bowl2_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S14 match_0008 / inn1.total_runs
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.total_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S15 match_0010 / inn2.total_wickets
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S16 match_0012 / inn1.total_wickets
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S17 match_0015 / inn2.byes
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.byes；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S18 match_0017 / inn1.bat2_runs
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.bat2_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S19 match_0003 / match.result
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S20 match_0008 / inn1.bat3_runs
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.bat3_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S21 match_0010 / inn1.bowl2_wickets
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn1.bowl2_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S22 match_0012 / match.result
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S23 match_0015 / inn2.no_balls
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.no_balls；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S24 match_0017 / inn2.wides
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn2.wides；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S25 match_0003 / inn2.bowl2_wickets
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn2.bowl2_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S26 match_0008 / inn1.bowl1_wickets
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.bowl1_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S27 match_0010 / inn2.overs
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.overs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Owen Hayes played the sharper opening role, Ethan Ward gave the first stand a steadier shape, and for a few overs Summit Vale had to work rather than wait.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S28 match_0012 / inn2.bat3_name
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn2.bat3_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S29 match_0015 / inn1.bowl1_runs
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn1.bowl1_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S30 match_0017 / inn1.bat2_name
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.bat2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S31 match_0003 / inn1.team
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Seabank Cricket Ground in Stonehaven had that sharp feel from the first over, not quite evening yet but already narrow enough in the light for every fielder in the ring to look a little closer than he really was, and Rid
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S32 match_0008 / inn2.bat1_name
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn2.bat1_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Aiden Cole gave Ridgeview their one proper argument.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S33 match_0010 / inn2.team
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediat
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S34 match_0012 / inn1.bowl2_name
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.bowl2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Liam Frost removed Adrian, Lucas Vale pinned Caleb after he had started to settle, and the score was pushed back into repair mode again.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S35 match_0015 / inn2.bowl2_name
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.bowl2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Caleb Rourke arrived and changed the middle overs.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S36 match_0017 / inn1.bowl2_name
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.bowl2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Zach Foster’s spell was the visible cutting edge through the middle-late section, not always perfectly cheap, but constantly dangerous, while Ethan Parker kept hitting the card in ways that stopped any repair from becomi
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S37 match_0003 / inn1.total_wickets
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start ch
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S38 match_0008 / inn1.bat2_name
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.bat2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Adrian Blake then arrived and shifted the tone.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S39 match_0010 / inn1.team
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn1.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediat
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S40 match_0012 / inn2.team
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn2.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - At Eastbank Meadow Ground in Hillview, Westmere XI won the toss and chose to field, and the call had the feel of a side trusting the first hour rather than guessing at the day, because the surface looked playable from th
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

---

# 附录 E：REPRODUCE

# REPRODUCE

## 45 字段复核（0 调用）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_v3.py

## 抽取诊断（6 调用）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/run_extract.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/score_extract.py

## 盲审文本

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_texts.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_blind.py

## 输出

- runs/extract.jsonl、extract_scores.json
- FIELD_ANSWERABILITY_V3.jsonl
- BLIND_REVIEW.md、texts/
- 本轮调用 6/24。