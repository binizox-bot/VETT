# VETT 两场新比赛配对 + 维持原判 + V4 可答性：完整报告

日期：2026-11-13  
调用：18/18，外部 API 0；43 字段 0 次。

## 0. 一页摘要

**两场新比赛（match_0031、match_0019）**

| 模型 | 直接 two | 抽取+程序 two |
|---|---:|---:|
| Qwen | 1/2 | 2/2 |
| Llama | 1/2 | 2/2 |
| Gemma | 2/2 | 2/2 |
| 合计 | 4/6 | 6/6 |

- 两步法多答对 **2 场**，少答对 **0 场**；错→对 2、对→错 0。
- 直接组只输出两个字段，已到 4/6；两步法收益 +2，不是上一轮的 +6。
- Llama 0031 的值正确但键名写成下划线；严格匹配判错，归一化后直接组为 5/6，两步法收益 +1。

**维持原判**

- 误更新 **0/6**。
- 正确保留原值：Llama 2/2；Qwen 0/2（识别成 reassign 但 final==original，程序拒绝）；Gemma 0/2（retain 但旧值 UNKNOWN，程序拒绝）。
- 4/6 无法执行，失败在决定标签或旧值完整性，不在擅自加减。

**43 字段**

- V4 为 **79/258（30.6%）**：修正队名后缀匹配，新增 6 格，包括 match_0008 的 inn1.total_wickets（Coral Coast finished on 262 for eight）。
- Qwen 33/79、Gemma 38/79；Llama 仍只报 V3 的 26/73，V4 79 未重算。
- 40 格人工复核未返回。

## 1. 配对结论

- 同一份短证据、同一个模型、各一次调用；最终目标都只含两名投手 wicket。
- 直接组没有输出中间事实，不能从得分差判断它是否读对旧值；本轮只说明“抽取+程序”在这两场上改善了最终答案。
- 维持原判组证明程序不会在 retain 时擅自改数；失败是抽取协议问题。

## 2. 四句话

1. **两步法多做对 2 场、少做对 0 场**：4/6→6/6（严格键匹配）；Llama 键名归一化后为 5/6→6/6，+1。
2. **维持原判误更新 0/6**；4/6 无法执行：Qwen 2 条决定矛盾、Gemma 2 条旧值 UNKNOWN，Llama 2/2 正确。
3. **40 格人工复核完成 0/40**；可答清单 73→79（+6，队名后缀规则）；Qwen 33/79、Gemma 38/79、Llama 26/73（V4 未重算）。
4. **本轮升级了“同事件正式改判/维持原判”配对和“直接两字段/抽取+程序”配对**；下一批最值得验证维持原判的更多措辞，以及把 Llama 的 V4 79 分母补齐。

## 3. 缺口

- 维持原判仅 2 场，不能覆盖多种措辞。
- Llama 的 V4 79 未重算；逐场同分母仍缺。
- 40 格人工未返回；V4 仍标 pending。
- 无改判程序正控只做离线样例，未跑模型。
- 键名归一化若采用，直接组严格 4/6 会变为 5/6，需在下一版冻结规则。


---

# 附录 A：DESIGN

# DESIGN：两场新比赛配对 + V4 可答性

日期：2026-11-13。调用 18/18，外部 API 0。

## 1. 样本

| match | 局 | batter | 原投手 | 旧 | 新投手 | 旧 | 正确 |
|---|---|---|---|---|---|---|---|
| match_0031 | inn1 | Connor Shaw | Evan Vale | 4/19 | Leo Shaw | 1/26 | 3/19、2/26 |
| match_0019 | inn2 | Ethan Ward | Evan Turner | 5/13 | Liam Foster | 1/15 | 4/13、2/15 |

两场均未用于前几轮；源文本为 scorecard 重渲染（seed=0），改判为人工构造。  
每种有序对（正确、旧值、对调、反向）互不相同，无碰撞。

## 2. 版本

- 正式改判：同一事件原记录、两投手旧汇总、旧汇总时点、改判通知；金标为 −1/+1。
- 维持原判：同事件、同旧汇总，只把通知改为复核维持原归属；金标为原值。
- 两版短证据均 6 句；B 正文 ~? 字符；无更新后数字泄露。

## 3. 调用矩阵

- 直接正式改判：2×3=6，只输出两个最终 wicket。
- 抽取正式改判：2×3=6，输出 decision/身份/旧值。
- 抽取维持原判：2×3=6，同协议。
- 合计 18。

## 4. 程序规则

- reassign 且 original/final 合法：orig−1、final+1。
- retain 且 original==final：输出旧值。
- 缺字段/UNKNOWN/矛盾/非法值：无法执行。
- 正控：正确 reassign 与 retain 输入各验证一次。

## 5. 可答性

- V4 79/258：V3 73 + 6 格队名后缀修正。
- 人工 40 格未返回；V4 仍标 pending。

---

# 附录 B：PAIRED_RESULTS

# PAIRED_RESULTS：两场新比赛的配对结果

日期：2026-11-13。18 次请求（6 直接 + 6 抽取改判 + 6 抽取维持），外部 API 0。

## 0. 样本

- match_0031 第一局：Evan Vale 4/19 → 3/19；Leo Shaw 1/26 → 2/26。
- match_0019 第二局：Evan Turner 5/13 → 4/13；Liam Foster 1/15 → 2/15。
- 旧值对、正确值、旧值对调、反向更新四种有序对均不同，无答案碰撞。

## 1. 正式改判：直接 vs 抽取+程序

| 模型 | 直接 two | 抽取+程序 two |
|---|---:|---:|
| Qwen | 1/2 | 2/2 |
| Llama | 1/2 | 2/2 |
| Gemma | 2/2 | 2/2 |
| 合计 | 4/6 | 6/6 |

配对变化：错→对 2、对→错 0、对→对 4、错→错 0。

- Qwen 0019 直接给 4、1（只减原投手，未加新投手）；抽取+程序给 4、2。
- Llama 0031 直接值 3、2 正确，但键名写成下划线（Evan_Vale_wickets），严格键匹配判错；归一化则直接组 5/6，两步法收益 +1。
- Gemma 两场直接都对。

## 2. 维持原判

| 模型 | retain 识别 | 两人最终值同时正确 | 误更新 | 无法执行 |
|---|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0 | 2 |
| Llama | 2/2 | 2/2 | 0 | 0 |
| Gemma | 2/2 | 0/2 | 0 | 2 |

- Qwen：识别成 reassign，但 final_bowler == original_bowler，决定与人物矛盾 → 程序拒绝执行，未误改。
- Gemma：识别成 retain，但旧值填 UNKNOWN → 无法执行，未误改。
- Llama：两场都正确保留原值。
- 误更新 0/6；4/6 无法执行，失败在决定标签或旧值完整性，不在擅自改数。

## 3. 程序正控

- 正确 reassign 输入：两人最终值正确。
- 正确 retain 输入：两人原值不变。
- 缺字段/UNKNOWN/方向矛盾：程序拒绝执行，未产生数值。

## 4. 结论

两场新比赛上，先抽取再由程序更新比直接给最终值多答对 2 场（严格键匹配 4/6→6/6），没有把原来对的改错。  
维持原判没有误更新；失败是决定标签矛盾或旧值 UNKNOWN，不是程序擅自加减。  
直接组这次只要求两个字段，已到 4/6；两步法收益是 +2，不是上一轮的 +6。

---

# 附录 C：SCORECARD_RESCORE_V4

# SCORECARD_RESCORE_V4：258 字段

日期：2026-11-13。0 次模型调用。

## 1. 可答性

- V4 为 79/258（30.6%）：在 V3 73 格基础上，修正球队名后缀匹配（去掉 XI/Women/CC），新增 6 格。
- 新增例：match_0008 inn1.total_wickets 由 Coral Coast finished on 262 for eight 支持；V3 因球队名写成 Coral Coast XI 未匹配，V4 记 direct。
- 185 格中 6 格转 direct，其余 179 待核。
- 40 格盲审沿用 v1 全文本；人工未返回。

## 2. 同分母 79

| 模型 | 可答答对 | 分母 | 准确率 |
|---|---:|---:|---:|
| Qwen | 33 | 79 | 41.8% |
| Gemma | 38 | 79 | 48.1% |
| Llama | 26 | 73 | 35.6%（V4 79 未重算） |

Llama 的 V4 分母未重算：0008 空答、5 条嵌套 JSON 可恢复；当前只保留 V3 的 26/73，不能与 79 直接比较。

## 3. 逐场（Qwen/Gemma）

| match | 可答 V4 | Qwen | Gemma |
|---|---:|---:|---:|
| 0003 | 16 | 10 | 10 |
| 0008 | 13 | 6 | 6 |
| 0010 | 12 | 1 | 3 |
| 0012 | 11 | 4 | 6 |
| 0015 | 11 | 5 | 3 |
| 0017 | 11 | 4 | 5 |

## 4. 格式与闭合

- Qwen/Gemma 6/6 解析；Llama 旧协议 0/6，展平 5/6，0008 空。
- 闭合约束仍不可检查（schema 缺 extras 合计/bat_sum）。
- 旧口径 73/258 保留为历史对照；V4 79 的 6 格变化逐条在 FIELD_ANSWERABILITY_V4.jsonl 的 change_reason_v4。

---

# 附录 D：DATASET_CHANGELOG

# DATASET_CHANGELOG：本轮升级

## 1. 错例

| 错例 | 现象 | 范围 |
|---|---|---|
| 直接两字段仍会漏更新 | 0019 Qwen 只减原投手；0031 Llama 键名格式错 | 2/6 |
| 两步法修复 | 同一抽取+程序 6/6 | 2 场 ×3 模型 |
| 维持原判误更新 | 0/6；失败为 UNKNOWN 或决定矛盾 | 4 条无法执行 |
| 可答性漏判 | match_0008 total_wickets 因队名后缀未匹配 | 6 格 |

## 2. 改动

| 项 | 改法 | 验收 |
|---|---|---|
| 样本 | 增加“维持原判”同事件配对 | 2 场 ×3 模型 6 条 |
| 直接组 | 只输出两名投手两个最终 wicket | 4/6 |
| 抽取组 | 固定 JSON：decision/身份/旧值；程序更新 | 6/6 |
| 评分 | 保留 parse/身份/方向/旧值/最终/程序六层 | 逐条 |
| 键名 | 记录严格与下划线归一化两版 | Llama 0031 |
| 可答性 | 队名去 XI/Women/CC 后匹配比分句 | 73→79，+6 |

## 3. 还缺

- 维持原判只 2 场；需更多措辞。
- Llama V4 79 分母未重算。
- 40 格人工未返回。
- 无改判正控未跑。

---

# 附录 E：BLIND_REVIEW

# BLIND_REVIEW：40 格（沿用 v1 全文与段号）

人工复核状态：未返回。以下题面可直接发给复核者。

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

# 附录 F：REPRODUCE

# REPRODUCE

## 构建与运行（18 次）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v2/build_run.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v2/resume_run.py

## 仅复算（0 次）

python .../score.py
python .../make_v4.py
python .../v4_rescore.py

## 输出

- SAMPLE_MANIFEST.json
- runs/paired.jsonl（18 条）
- paired_scores.json
- FIELD_ANSWERABILITY_V4.jsonl
- 实际调用 18/18。