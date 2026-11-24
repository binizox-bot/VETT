# VETT 改判更新诊断 + 首批整表试点：完整报告

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


---

# 附录 A：DESIGN

# DESIGN：改判更新诊断 + 整表试点

日期：2026-11-13。本地 Qwen2.5:7b、Llama3.1:8b、Gemma2:9b；预算 120；实际 84；外部 API 0。

## 1. 开发比赛（6 场）

match_0009、0013、0014、0016、0018、0027。均来自上一轮留出集，本轮登记为开发样本。  
来源：scorecard 重渲染（seed=0），构造改判；不是真实赛果更正。  
优先纳入 0014/0016，并修正其总出局数证据：
- 0014：Harbor Peninsula XI closed on 226 for 7。
- 0016：Crestline XI closed on 138 for 3。

## 2. 条件（6×3×3=54）

| 条件 | 内容 |
|---|---|
| A | 全文：完整解说 + 改判前汇总 + Note + 正式改判通知 |
| B | 从 A 原样摘出六句：出局记录、两投手旧汇总、正确终局、Note、通知；保留 [EVIDENCE] |
| C | 与 B 同一文本；先输出 extraction（事件、原/新投手、旧值、总数），再输出最终五字段 |

A/B/C 同一问题、同一五字段、同一金标；C 多 extraction 结构。

五字段：原投手 wickets_credited、bowling_runs_conceded；新投手同两项；innings_wickets_lost。

主指标：两名投手最终 wickets 同时正确。辅助：总数、三项、两项失分、五项。

## 3. 核对

- 0014/0016 的总出局证据分别用 226 for 7、138 for 3，不再用错局。
- B 含“the bowling figures above are the pre-revision record”的 Note 和正式通知。
- B 去掉 [EVIDENCE] 后与 A 逐字一致；6 个标记；无更新后的 figures。
- 6 场全部通过；金标与证据见 ANSWER_KEY.md。

## 4. 预算

dev 54 + Lina 6 + retest 6 + full table 18 = 84/120。  
留出复验 0 场（预算与时间未用）；未跑无改判对照。

## 5. 整表试点

6 场：0003、0008、0010、0012、0015、0017；输入发布 commentary.txt；scorecard 离线评分；43 字段。  
6×3=18；qwen/gemma 6/6 解析，llama 0/6 格式失败。


---

# 附录 B：EVIDENCE_AUDIT

# EVIDENCE_AUDIT：证据修复与正控

## 1. 修复项

| 项 | 旧问题 | 本轮 |
|---|---|---|
| match_0014 总出局 | 证据标错局 | 改为 Harbor Peninsula XI closed on 226 for 7 |
| match_0016 总出局 | 证据标错局 | 改为 Crestline XI closed on 138 for 3 |
| 旧汇总状态 | 短版漏 Note | B/C 均含 the bowling figures above are the pre-revision record |
| 字段 | 旧 _runs 歧义 | 统一 wickets_credited / bowling_runs_conceded / innings_wickets_lost |

## 2. 构建检查（6/6 通过）

- B 去掉 [EVIDENCE] 后与 A 逐字一致。
- 六句证据：出局、A 旧汇总、B 旧汇总、正确终局、Note、通知；无重复。
- B 不含更新后的 figures 短语。
- 金标五项与证据一致；0014/0016 的终局分别 7、3。

## 3. 正控

- Lina gemma：original/explicit 五项全对，derivation 旧值 → 题面能区分“抄新值”和“应用改判”。
- Lina qwen：两人 wickets 对，但 total 恒定 9；说明 total 字段仍是弱点。
- scorer 能区分：两人对、只改一人、方向反、两人对但总数错、格式失败。

## 4. 复核

复核者：构建者本人；范围：6 场证据句、总出局、旧值、金标；未做独立第二人复核。  
未解决：C 的 extraction 字段常缺/错，导致 Python 更新无法执行；这是模型输出协议问题，不是证据缺口。


---

# 附录 C：ATTRIBUTION_RESULTS

# ATTRIBUTION_RESULTS：修好的完整短证据能否救回改判

日期：2026-11-13。6 场开发比赛 × A/B/C × 3 模型 = 54 次；Lina 6 次；重测 6 次。历史 0/42 保留。

## 0. 结论

- **修好的完整短证据（B）仍未救回改判**：B 的两名投手同时正确 0/18；A 也是 0/18；B−A=0。
- C 的分步作答只有 gemma 在 match_0014 做对两名投手（1/6），其余 0/6。
- C 的抽取+Python 更新：0 场修对、0 场改坏、1 场无法执行（gemma/qwen 各 1 场缺字段）；抽取本身几乎都错。
- 主要错法仍是两人都旧值：A/B 中 gemma 6/6、qwen 6/6、llama 3/6（A）与 5/6（B）。

## 1. 开发集（6 场）

| 模型 | 条件 | two_wickets | total | three | runs | five |
|---|---|---:|---:|---:|---:|---:|
| qwen | A | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| qwen | B | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| qwen | C | 0/6 | 2/6 | 0/6 | 4/6 | 0/6 |
| llama | A | 0/6 | 4/6 | 0/6 | 6/6 | 0/6 |
| llama | B | 0/6 | 4/6 | 0/6 | 6/6 | 0/6 |
| llama | C | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| gemma | A | 0/6 | 3/6 | 0/6 | 6/6 | 0/6 |
| gemma | B | 0/6 | 3/6 | 0/6 | 6/6 | 0/6 |
| gemma | C | 1/6 | 3/6 | 0/6 | 6/6 | 0/6 |

B−A 在 two_wickets、total、three 上均为 0。C−B 只有 gemma 的 two +1。

## 2. 错法

A/B：

- gemma：both_old 6/6（A、B 都是）。
- qwen：both_old 6/6。
- llama：A both_old 3、only_new_plus1 1、both_updated_wrong 2；B both_old 5、only_new_plus1 1。

C：

- gemma：both_old 3、only_new 1、only_orig 1、both_updated_wrong 1（其中 match_0014 两人都对）。
- llama：both_old 4、only_new 1、both_updated_wrong 1。
- qwen：both_old 1、both_updated_wrong 3、format 2。

## 3. C 的同一输出：模型最终值 vs Python 更新

| 模型 | 程序更新三项正确 | 修对 | 改坏 | 同 | 无法执行 |
|---|---:|---:|---:|---:|---:|
| qwen | 0/6 | 0 | 0 | 5 | 1 |
| llama | 0/6 | 0 | 0 | 6 | 0 |
| gemma | 0/6 | 0 | 0 | 5 | 1 |

抽取值普遍错（人物或旧值），所以程序没有可执行的正确输入；没有“程序修好”的场次，也没有“程序改坏”的场次。

## 4. Lina 通路

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 4、3、9（two 对，total 错） |
| explicit | 3/6、4/7、10 五项全对 | 3、4、9（two 对，total 错） |
| derivation | 4/6、3/7、10 旧值 | 4、3、9（two 对，total 错） |

qwen 在 Lina 上能读对两人 wickets，但 total 恒定 9；gemma 明示版能抄，推导版回旧值。

## 5. 重测

qwen/llama/gemma 在 match_0014、match_0016 的 A 条件均 5/5 一致。

## 6. 四句话

1. **修好的完整短证据让 0 个模型、0 场多做对两名投手**：B 的 two_wickets 0/18，A 也 0/18，B−A=0；总出局数 B 与 A 相同（qwen 2/6、llama 4/6、gemma 3/6）。
2. **最常见错误是两人都旧值**（gemma 6/6、qwen 6/6、llama 3/6），其次是只加新投手、两人都改但值错；C 的分步作答只在 gemma 的 match_0014 修对两人，其余仍错。
3. **Python 用同一份抽取修好 0 场、改坏 0 场、1 场无法执行**；抽取本身几乎都错，程序没有正确输入可更新。
4. **下一轮应先修“抽取协议/人物绑定”**：让模型稳定输出 orig/new 两人的旧值和事件，再谈程序更新；否则分步作答只会增加格式负担。


---

# 附录 D：FULL_TABLE_PILOT

# FULL_TABLE_PILOT：6 场整表试点

日期：2026-11-13。6 场 × 3 模型 = 18 次；输入为发布目录 commentary.txt；scorecard 离线评分。

## 0. 结论

- 43 字段的紧凑整表结构可被 qwen/gemma 完整输出：6/6 解析成功，done_reason=stop，eval 518–576，无截断。
- llama 6/6 格式失败（未给出可解析 JSON），不是长度截断。
- 可答字段准确率：qwen 12.2/43（28.3%），gemma 14.2/43（32.9%），llama 0/43（格式失败）。
- 缺行：qwen/gemma 0；llama 43 字段全缺。
- 下一批最该补：llama 的 JSON 协议、逐字段文本依据映射、以及 summary/extras 这些拖低准确率的子表。

## 1. 逐场

| match | qwen 正确/43 | gemma 正确/43 | llama |
|---|---:|---:|---|
| match_0003 | 17 (.395) | 18 (.419) | 格式失败 |
| match_0008 | 12 (.279) | 14 (.326) | 格式失败 |
| match_0010 | 6 (.140) | 11 (.256) | 格式失败 |
| match_0012 | 15 (.349) | 17 (.395) | 格式失败 |
| match_0015 | 11 (.256) | 11 (.256) | 格式失败 |
| match_0017 | 12 (.279) | 14 (.326) | 格式失败 |

## 2. 输出与截断

| 模型 | 解析 | done=stop | eval 范围 | 缺字段 |
|---|---:|---:|---|---:|
| qwen | 6/6 | 6/6 | 528–552 | 0 |
| gemma | 6/6 | 6/6 | 518–576 | 0 |
| llama | 0/6 | 6/6 | 426–508 | 43/43 |

llama 的失败是 JSON 结构/格式，不是 num_predict 截断；它的输出更短，说明不是预算问题。

## 3. 可答性与字段

- 本试点定义 43 字段：match 3；每局 summary 8×2；每局 top3 击球 name/runs 6×2；每局 top2 投手 name/wickets/runs 6×2。
- 43 个字段都能从 scorecard 金标取得；发布 commentary 是否逐项出现尚未做严格映射，因此本轮准确率按“全部 43 字段”计，未剔除“文本未提”的字段。这是下一批要补的。
- qwen/gemma 的击球/投手行覆盖 0 缺行；llama 全缺。

## 4. 账目检查

- 本轮结构未包含 extras 合计与 batting 合计的闭合字段，无法做完整账目检查；仅按 43 字段逐项对金标。
- 下一批应加：bat_sum+extras=total、extras 四项和、bowling_charged=total-byes-lb、wicket 合计。

## 5. 整表与改判的映射

- 整表 6 场与改判开发 6 场不同；字段规则一致。若同一场，改判会触及 bowling 表两名投手的 W 列和 summary 的 total_wickets，R 列不变。
- 当前整表结构可容纳这两行；下一步应在整表中加“投手行 W/R”与“summary W”的专项评分。

## 6. 下一步

1. 修 llama 的 JSON 协议（或换 JSON mode/更明确的 schema）。
2. 加逐字段文本依据映射，区分直接可答/可推导/证据不足，再算可答准确率。
3. 加闭合字段与账目检查。
4. 再决定 220 场单次整表还是按局分块；当前 eval 518–576 说明 1,200 预算足够 43 字段，不需要分块。


---

# 附录 E：BLIND_REVIEW

# BLIND_REVIEW：6 场改判题面

A 全文；B 为同一 A 加 [EVIDENCE] 的六句摘录。请填五字段。

## match_0009 — Dylan Shaw — Tyler Grant -> Luke Barrett
----- A FULL TEXT -----
At Eastbank Meadow Ground, Hillview, Coral Bay XI chose to field after winning the toss, reading conditions looked good for chasing. Ridgewater XI would bat first with Coral Bay XI to chase.. Ridgewater XI began through Tyler Grant and Ben Carter. The early exchanges set a tone of unforgiving, grinding.. Zane Foster broke through — Ben Carter gone for 5. Ridgewater XI were 9/1.. When Isaac Nolan fell to Evan Turner for 8, the scoreboard read 25/2.. Evan Turner found the breakthrough, Connor Vale departing for 4 to leave Ridgewater XI at 32/3.. A stand of 16 between Isaac Nolan and Tyler Grant rebuilt the innings. The arithmetic was straightforward — 8 from Isaac Nolan, 6 from Tyler Grant — and the scoreboard shifted from 9/1 to 25/2.. Tyler Grant and Caleb Marsh constructed a repair worth 52. With Tyler Grant scoring 16 and Caleb Marsh contributing 31, Ridgewater XI moved from 32/3 to 84/4.. A stand of 24 between Tyler Grant and Leo Turner rebuilt the innings. The arithmetic was straightforward — 12 from Tyler Grant, 10 from Leo Turner — and the scoreboard shifted from 105/6 to 129/7.. Ryan Cole and Leo Turner constructed a repair worth 17. With Ryan Cole scoring 8 and Leo Turner contributing 7, Ridgewater XI moved from 129/8 to 146/9.. A stand of 38 between Mason Hart and Leo Turner rebuilt the innings. The arithmetic was straightforward — 19 from Mason Hart, 17 from Leo Turner — and the scoreboard shifted from 146/9 to 184/10.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Tyler Grant held firm, compiling 39 from 76 balls. The 3 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Ridgewater XI.. Connor Blake broke through — Caleb Marsh gone for 31. Ridgewater XI were 84/4.. When Aaron Holt fell to Connor Blake for 10, the scoreboard read 96/5.. Noah Reed found the breakthrough, Luca Barrett departing for 7 to leave Ridgewater XI at 105/6.. Noah Reed broke through — Tyler Grant gone for 39. Ridgewater XI were 129/7.. The lower order flickered briefly — Liam Frost made 0 — but Ridgewater XI were 129/8 and the innings was nearly done.. The lower order flickered briefly — Ryan Cole made 8 — but Ridgewater XI were 146/9 and the innings was nearly done.. The lower order flickered briefly — Leo Turner made 34 — but Ridgewater XI were 184/10 and the innings was nearly done.. The innings closed at 184 from 46.5 overs.. Coral Bay XI's bowling effort was led by Noah Reed, whose 3 for 18 made the deepest incisions. Zane Foster kept the pressure on with 2 for 30, and together they ensured no partnership could breathe.. The total included 19 extras, with 14 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 165. All told, the innings reached 184.. Set 184 to win, Coral Bay XI sent out Ethan Ward and Owen Hayes. The chase would test temperament as much as technique.. The chase took a hit when Ethan Ward fell to Luke Barrett for 50. At 78/1, with 184 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Owen Hayes gone for 40. Coral Bay XI were 109/2 chasing 184, and the innings needed a partnership.. The chase took a hit when Dylan Shaw fell to Tyler Grant for 7. At 124/3, with 184 still needed, the pressure that had been theoretical was now real.. Tyler Grant broke through — Caleb Brooks gone for 16. Coral Bay XI were 158/4 chasing 184, and the innings needed a partnership.. Owen Hayes and Aiden Price constructed 31 together. With Owen Hayes contributing 19 and Aiden Price adding 11, Coral Bay XI moved from 78/1 to 109/2. The target of 184 had come into view.. The stand that changed the chase came from Dylan Shaw and Aiden Price. Their 15 — 7 from Dylan Shaw, 7 from Aiden Price — carried Coral Bay XI from 109/2 to 124/3, transforming the equation.. Caleb Brooks and Aiden Price constructed 34 together. With Caleb Brooks contributing 16 and Aiden Price adding 15, Coral Bay XI moved from 124/3 to 158/4. The target of 184 had come into view.. The chase found its centre in Ethan Ward, whose 50 from 44 deliveries carried Coral Bay XI from uncertainty toward their target of 184. The 8 fours and 0 sixes were the visible markers of an innings built in stages.. Coral Bay XI closed on 187 for 5 from 34.2 overs, the 5 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 13: 11 wides, 1 no-ball, plus 0 byes and 1 leg-bye. The batters produced 174 between them. The bowling side's ledger showed 186 charged to the attack, the remainder of the 187 having arrived through routes that bypass the bowler's figures.. Ridgewater XI's bowling effort was led by Tyler Grant, whose 2 for 25 made the deepest incisions. Luke Barrett kept the pressure on with 2 for 43, and together they ensured no partnership could breathe.. Coral Bay XI Won by 5 Wickets, with Noah Reed recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Dylan Shaw in the second innings was reassigned from Tyler Grant to Luke Barrett. All other figures stand.
----- END -----
----- B EVIDENCE -----
At Eastbank Meadow Ground, Hillview, Coral Bay XI chose to field after winning the toss, reading conditions looked good for chasing. Ridgewater XI would bat first with Coral Bay XI to chase.. Ridgewater XI began through Tyler Grant and Ben Carter. The early exchanges set a tone of unforgiving, grinding.. Zane Foster broke through — Ben Carter gone for 5. Ridgewater XI were 9/1.. When Isaac Nolan fell to Evan Turner for 8, the scoreboard read 25/2.. Evan Turner found the breakthrough, Connor Vale departing for 4 to leave Ridgewater XI at 32/3.. A stand of 16 between Isaac Nolan and Tyler Grant rebuilt the innings. The arithmetic was straightforward — 8 from Isaac Nolan, 6 from Tyler Grant — and the scoreboard shifted from 9/1 to 25/2.. Tyler Grant and Caleb Marsh constructed a repair worth 52. With Tyler Grant scoring 16 and Caleb Marsh contributing 31, Ridgewater XI moved from 32/3 to 84/4.. A stand of 24 between Tyler Grant and Leo Turner rebuilt the innings. The arithmetic was straightforward — 12 from Tyler Grant, 10 from Leo Turner — and the scoreboard shifted from 105/6 to 129/7.. Ryan Cole and Leo Turner constructed a repair worth 17. With Ryan Cole scoring 8 and Leo Turner contributing 7, Ridgewater XI moved from 129/8 to 146/9.. A stand of 38 between Mason Hart and Leo Turner rebuilt the innings. The arithmetic was straightforward — 19 from Mason Hart, 17 from Leo Turner — and the scoreboard shifted from 146/9 to 184/10.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Tyler Grant held firm, compiling 39 from 76 balls. The 3 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Ridgewater XI.. Connor Blake broke through — Caleb Marsh gone for 31. Ridgewater XI were 84/4.. [EVIDENCE] When Aaron Holt fell to Connor Blake for 10, the scoreboard read 96/5.. Noah Reed found the breakthrough, Luca Barrett departing for 7 to leave Ridgewater XI at 105/6.. Noah Reed broke through — Tyler Grant gone for 39. Ridgewater XI were 129/7.. The lower order flickered briefly — Liam Frost made 0 — but Ridgewater XI were 129/8 and the innings was nearly done.. The lower order flickered briefly — Ryan Cole made 8 — but Ridgewater XI were 146/9 and the innings was nearly done.. The lower order flickered briefly — Leo Turner made 34 — but Ridgewater XI were 184/10 and the innings was nearly done.. The innings closed at 184 from 46.5 overs.. Coral Bay XI's bowling effort was led by Noah Reed, whose 3 for 18 made the deepest incisions. Zane Foster kept the pressure on with 2 for 30, and together they ensured no partnership could breathe.. The total included 19 extras, with 14 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 165. All told, the innings reached 184.. Set 184 to win, Coral Bay XI sent out Ethan Ward and Owen Hayes. The chase would test temperament as much as technique.. The chase took a hit when Ethan Ward fell to Luke Barrett for 50. At 78/1, with 184 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Owen Hayes gone for 40. Coral Bay XI were 109/2 chasing 184, and the innings needed a partnership.. [EVIDENCE] The chase took a hit when Dylan Shaw fell to Tyler Grant for 7. At 124/3, with 184 still needed, the pressure that had been theoretical was now real.. Tyler Grant broke through — Caleb Brooks gone for 16. Coral Bay XI were 158/4 chasing 184, and the innings needed a partnership.. Owen Hayes and Aiden Price constructed 31 together. With Owen Hayes contributing 19 and Aiden Price adding 11, Coral Bay XI moved from 78/1 to 109/2. The target of 184 had come into view.. The stand that changed the chase came from Dylan Shaw and Aiden Price. Their 15 — 7 from Dylan Shaw, 7 from Aiden Price — carried Coral Bay XI from 109/2 to 124/3, transforming the equation.. Caleb Brooks and Aiden Price constructed 34 together. With Caleb Brooks contributing 16 and Aiden Price adding 15, Coral Bay XI moved from 124/3 to 158/4. The target of 184 had come into view.. The chase found its centre in Ethan Ward, whose 50 from 44 deliveries carried Coral Bay XI from uncertainty toward their target of 184. The 8 fours and 0 sixes were the visible markers of an innings built in stages.. Coral Bay XI closed on 187 for 5 from 34.2 overs, the 5 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 13: 11 wides, 1 no-ball, plus 0 byes and 1 leg-bye. The batters produced 174 between them. The bowling side's ledger showed 186 charged to the attack, the remainder of the 187 having arrived through routes that bypass the bowler's figures.. [EVIDENCE] Ridgewater XI's bowling effort was led by Tyler Grant, whose 2 for 25 made the deepest incisions. [EVIDENCE] Luke Barrett kept the pressure on with 2 for 43, and together they ensured no partnership could breathe.. Coral Bay XI Won by 5 Wickets, with Noah Reed recognised as Player of the Match after a performance that influenced both halves of the contest. [EVIDENCE] Note: the bowling figures above are the pre-revision record. [EVIDENCE] Match review: the dismissal of Dylan Shaw in the second innings was reassigned from Tyler Grant to Luke Barrett. All other figures stand.
----- END -----
- Tyler Grant_wickets_credited = ____
- Tyler Grant_bowling_runs_conceded = ____
- Luke Barrett_wickets_credited = ____
- Luke Barrett_bowling_runs_conceded = ____
- innings_wickets_lost = ____

## match_0013 — Leo Warren — Evan Turner -> Zane Carter
----- A FULL TEXT -----
At Eastbank Meadow Ground, Hillview, Mirage Lions XI chose to field after winning the toss, reading conditions looked good for chasing. Silver Pearl XI would bat first with Mirage Lions XI to chase.. Silver Pearl XI began through Tyler Marsh and Leo Warren. The early exchanges set a tone of tense, fluctuating.. Zane Carter broke through — Tyler Marsh gone for 5. Silver Pearl XI were 8/1.. When Leo Warren fell to Evan Turner for 24, the scoreboard read 50/2.. Connor Vale found the breakthrough, Isaac Hale departing for 36 to leave Silver Pearl XI at 116/3.. A stand of 42 between Isaac Hale and Leo Warren rebuilt the innings. The arithmetic was straightforward — 15 from Isaac Hale, 22 from Leo Warren — and the scoreboard shifted from 8/1 to 50/2.. Isaac Hale and Connor Wells constructed a repair worth 66. With Isaac Hale scoring 21 and Connor Wells contributing 41, Silver Pearl XI moved from 50/2 to 116/3.. A stand of 15 between Aaron Blake and Connor Wells rebuilt the innings. The arithmetic was straightforward — 13 from Aaron Blake, 0 from Connor Wells — and the scoreboard shifted from 116/3 to 131/4.. Aaron Blake and Caleb Shaw constructed a repair worth 70. With Aaron Blake scoring 34 and Caleb Shaw contributing 34, Silver Pearl XI moved from 131/4 to 201/5.. A stand of 18 between Luke Barrett and Aaron Blake rebuilt the innings. The arithmetic was straightforward — 17 from Luke Barrett, 0 from Aaron Blake — and the scoreboard shifted from 201/5 to 219/6.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Ryan Foster and Luke Barrett constructed a repair worth 36. With Ryan Foster scoring 12 and Luke Barrett contributing 23, Silver Pearl XI moved from 219/6 to 255/7.. Through the middle phase, Aaron Blake held firm, compiling 47 from 49 balls. The 4 boundaries and 2 sixes told only part of the story — the real value was the time he bought for Silver Pearl XI.. Caleb Brooks broke through — Connor Wells gone for 41. Silver Pearl XI were 131/4.. When Caleb Shaw fell to Evan Turner for 34, the scoreboard read 201/5.. Evan Turner found the breakthrough, Aaron Blake departing for 47 to leave Silver Pearl XI at 219/6.. Connor Vale broke through — Luke Barrett gone for 40. Silver Pearl XI were 255/7.. The lower order flickered briefly — Liam Foster made 3 — but Silver Pearl XI were 263/8 and the innings was nearly done.. The innings closed at 263 from 50.0 overs.. Mirage Lions XI's bowling effort was led by Evan Turner, whose 3 for 70 made the deepest incisions. Zane Carter kept the pressure on with 2 for 58, and together they ensured no partnership could breathe.. The total included 17 extras, with 12 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 246. All told, the innings reached 263.. Set 263 to win, Mirage Lions XI sent out Ethan Ward and Aiden Price. The chase would test temperament as much as technique.. The chase took a hit when Aiden Price fell to Evan Reed for 23. At 70/1, with 263 still needed, the pressure that had been theoretical was now real.. Evan Reed broke through — Ethan Ward gone for 52. Mirage Lions XI were 90/2 chasing 263, and the innings needed a partnership.. The chase took a hit when Owen Hayes fell to a bowler for 12. At 112/3, with 263 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Liam Parker gone for 45. Mirage Lions XI were 205/4 chasing 263, and the innings needed a partnership.. The chase took a hit when Lucas Reed fell to Connor Wells for 8. At 217/5, with 263 still needed, the pressure that had been theoretical was now real.. Ryan Foster broke through — Caleb Brooks gone for 20. Mirage Lions XI were 246/6 chasing 263, and the innings needed a partnership.. Ethan Ward and Liam Parker constructed 20 together. With Ethan Ward contributing 12 and Liam Parker adding 6, Mirage Lions XI moved from 70/1 to 90/2. The target of 263 had come into view.. The stand that changed the chase came from Owen Hayes and Liam Parker. Their 22 — 12 from Owen Hayes, 9 from Liam Parker — carried Mirage Lions XI from 90/2 to 112/3, transforming the equation.. Liam Parker and Connor Vale constructed 93 together. With Liam Parker contributing 30 and Connor Vale adding 59, Mirage Lions XI moved from 112/3 to 205/4. The target of 263 had come into view.. Caleb Brooks and Connor Vale constructed 29 together. With Caleb Brooks contributing 20 and Connor Vale adding 8, Mirage Lions XI moved from 217/5 to 246/6. The target of 263 had come into view.. The chase found its centre in Connor Vale, whose 72 from 83 deliveries carried Mirage Lions XI from uncertainty toward their target of 263. The 4 fours and 1 six were the visible markers of an innings built in stages.. Mirage Lions XI closed on 264 for 7 from 46.2 overs, the 3 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 18: 12 wides, 1 no-ball, plus 1 by and 4 leg-byes. The batters produced 246 between them. The bowling side's ledger showed 259 charged to the attack, the remainder of the 264 having arrived through routes that bypass the bowler's figures.. Silver Pearl XI's bowling effort was led by Evan Reed, whose 2 for 50 made the deepest incisions. Connor Wells kept the pressure on with 1 for 13, and together they ensured no partnership could breathe.. Mirage Lions XI Won by 3 Wickets, with Connor Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Leo Warren in the first innings was reassigned from Evan Turner to Zane Carter. All other figures stand.
----- END -----
----- B EVIDENCE -----
At Eastbank Meadow Ground, Hillview, Mirage Lions XI chose to field after winning the toss, reading conditions looked good for chasing. Silver Pearl XI would bat first with Mirage Lions XI to chase.. Silver Pearl XI began through Tyler Marsh and Leo Warren. The early exchanges set a tone of tense, fluctuating.. Zane Carter broke through — Tyler Marsh gone for 5. Silver Pearl XI were 8/1.. [EVIDENCE] When Leo Warren fell to Evan Turner for 24, the scoreboard read 50/2.. Connor Vale found the breakthrough, Isaac Hale departing for 36 to leave Silver Pearl XI at 116/3.. A stand of 42 between Isaac Hale and Leo Warren rebuilt the innings. The arithmetic was straightforward — 15 from Isaac Hale, 22 from Leo Warren — and the scoreboard shifted from 8/1 to 50/2.. Isaac Hale and Connor Wells constructed a repair worth 66. With Isaac Hale scoring 21 and Connor Wells contributing 41, Silver Pearl XI moved from 50/2 to 116/3.. A stand of 15 between Aaron Blake and Connor Wells rebuilt the innings. The arithmetic was straightforward — 13 from Aaron Blake, 0 from Connor Wells — and the scoreboard shifted from 116/3 to 131/4.. Aaron Blake and Caleb Shaw constructed a repair worth 70. With Aaron Blake scoring 34 and Caleb Shaw contributing 34, Silver Pearl XI moved from 131/4 to 201/5.. A stand of 18 between Luke Barrett and Aaron Blake rebuilt the innings. The arithmetic was straightforward — 17 from Luke Barrett, 0 from Aaron Blake — and the scoreboard shifted from 201/5 to 219/6.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Ryan Foster and Luke Barrett constructed a repair worth 36. With Ryan Foster scoring 12 and Luke Barrett contributing 23, Silver Pearl XI moved from 219/6 to 255/7.. Through the middle phase, Aaron Blake held firm, compiling 47 from 49 balls. The 4 boundaries and 2 sixes told only part of the story — the real value was the time he bought for Silver Pearl XI.. Caleb Brooks broke through — Connor Wells gone for 41. Silver Pearl XI were 131/4.. When Caleb Shaw fell to Evan Turner for 34, the scoreboard read 201/5.. Evan Turner found the breakthrough, Aaron Blake departing for 47 to leave Silver Pearl XI at 219/6.. Connor Vale broke through — Luke Barrett gone for 40. Silver Pearl XI were 255/7.. [EVIDENCE] The lower order flickered briefly — Liam Foster made 3 — but Silver Pearl XI were 263/8 and the innings was nearly done.. The innings closed at 263 from 50.0 overs.. [EVIDENCE] Mirage Lions XI's bowling effort was led by Evan Turner, whose 3 for 70 made the deepest incisions. [EVIDENCE] Zane Carter kept the pressure on with 2 for 58, and together they ensured no partnership could breathe.. The total included 17 extras, with 12 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 246. All told, the innings reached 263.. Set 263 to win, Mirage Lions XI sent out Ethan Ward and Aiden Price. The chase would test temperament as much as technique.. The chase took a hit when Aiden Price fell to Evan Reed for 23. At 70/1, with 263 still needed, the pressure that had been theoretical was now real.. Evan Reed broke through — Ethan Ward gone for 52. Mirage Lions XI were 90/2 chasing 263, and the innings needed a partnership.. The chase took a hit when Owen Hayes fell to a bowler for 12. At 112/3, with 263 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Liam Parker gone for 45. Mirage Lions XI were 205/4 chasing 263, and the innings needed a partnership.. The chase took a hit when Lucas Reed fell to Connor Wells for 8. At 217/5, with 263 still needed, the pressure that had been theoretical was now real.. Ryan Foster broke through — Caleb Brooks gone for 20. Mirage Lions XI were 246/6 chasing 263, and the innings needed a partnership.. Ethan Ward and Liam Parker constructed 20 together. With Ethan Ward contributing 12 and Liam Parker adding 6, Mirage Lions XI moved from 70/1 to 90/2. The target of 263 had come into view.. The stand that changed the chase came from Owen Hayes and Liam Parker. Their 22 — 12 from Owen Hayes, 9 from Liam Parker — carried Mirage Lions XI from 90/2 to 112/3, transforming the equation.. Liam Parker and Connor Vale constructed 93 together. With Liam Parker contributing 30 and Connor Vale adding 59, Mirage Lions XI moved from 112/3 to 205/4. The target of 263 had come into view.. Caleb Brooks and Connor Vale constructed 29 together. With Caleb Brooks contributing 20 and Connor Vale adding 8, Mirage Lions XI moved from 217/5 to 246/6. The target of 263 had come into view.. The chase found its centre in Connor Vale, whose 72 from 83 deliveries carried Mirage Lions XI from uncertainty toward their target of 263. The 4 fours and 1 six were the visible markers of an innings built in stages.. Mirage Lions XI closed on 264 for 7 from 46.2 overs, the 3 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 18: 12 wides, 1 no-ball, plus 1 by and 4 leg-byes. The batters produced 246 between them. The bowling side's ledger showed 259 charged to the attack, the remainder of the 264 having arrived through routes that bypass the bowler's figures.. Silver Pearl XI's bowling effort was led by Evan Reed, whose 2 for 50 made the deepest incisions. Connor Wells kept the pressure on with 1 for 13, and together they ensured no partnership could breathe.. Mirage Lions XI Won by 3 Wickets, with Connor Vale recognised as Player of the Match after a performance that influenced both halves of the contest. [EVIDENCE] Note: the bowling figures above are the pre-revision record. [EVIDENCE] Match review: the dismissal of Leo Warren in the first innings was reassigned from Evan Turner to Zane Carter. All other figures stand.
----- END -----
- Evan Turner_wickets_credited = ____
- Evan Turner_bowling_runs_conceded = ____
- Zane Carter_wickets_credited = ____
- Zane Carter_bowling_runs_conceded = ____
- innings_wickets_lost = ____

## match_0014 — Elias Ward — Leo Quinn -> Dylan Frost
----- A FULL TEXT -----
At East Ridge Cricket Ground, Hillview, Canyon Stars XI chose to bat after winning the toss, reading conditions looked good for chasing. Canyon Stars XI would bat first with Harbor Peninsula XI to chase.. Canyon Stars XI began through Adrian Vale and Nolan Greer. The early exchanges set a tone of tense, fluctuating.. Rafi Cole broke through — Adrian Vale gone for 12. Canyon Stars XI were 24/1.. When Nolan Greer fell to Mason Hart for 18, the scoreboard read 39/2.. Owen Shaw found the breakthrough, Mason Kline departing for 27 to leave Canyon Stars XI at 108/3.. Nolan Greer and Caleb Rowan constructed a repair worth 15. With Nolan Greer scoring 8 and Caleb Rowan contributing 6, Canyon Stars XI moved from 24/1 to 39/2.. A stand of 69 between Caleb Rowan and Mason Kline rebuilt the innings. The arithmetic was straightforward — 35 from Caleb Rowan, 27 from Mason Kline — and the scoreboard shifted from 39/2 to 108/3.. Aiden Knox and Caleb Rowan constructed a repair worth 40. With Aiden Knox scoring 25 and Caleb Rowan contributing 12, Canyon Stars XI moved from 121/4 to 161/5.. A stand of 46 between Aiden Knox and Dylan Frost rebuilt the innings. The arithmetic was straightforward — 12 from Aiden Knox, 30 from Dylan Frost — and the scoreboard shifted from 161/5 to 207/6.. Through the middle phase, Caleb Rowan held firm, compiling 57 from 67 balls. The 6 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Canyon Stars XI.. Lucas Vale broke through — Connor Shaw gone for 9. Canyon Stars XI were 121/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Caleb Rowan fell to Mason Hart for 57, the scoreboard read 161/5.. Zane Perry found the breakthrough, Dylan Frost departing for 30 to leave Canyon Stars XI at 207/6.. Zane Perry broke through — Aiden Knox gone for 41. Canyon Stars XI were 212/7.. The lower order flickered briefly — Evan Hale made 4 — but Canyon Stars XI were 225/8 and the innings was nearly done.. The innings closed at 225 from 36.0 overs.. Harbor Peninsula XI's bowling effort was led by Zane Perry, whose 2 for 47 made the deepest incisions. Mason Hart kept the pressure on with 2 for 48, and together they ensured no partnership could breathe.. The total included 17 extras, with 12 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 208. All told, the innings reached 225.. Set 225 to win, Harbor Peninsula XI sent out Elias Ward and Oliver Hayes. The chase would test temperament as much as technique.. The chase took a hit when Elias Ward fell to Leo Quinn for 4. At 6/1, with 225 still needed, the pressure that had been theoretical was now real.. Mason Kline broke through — Oliver Hayes gone for 10. Harbor Peninsula XI were 26/2 chasing 225, and the innings needed a partnership.. The chase took a hit when Caleb Brook fell to Ryan Wells for 34. At 61/3, with 225 still needed, the pressure that had been theoretical was now real.. Nolan Greer broke through — Rafi Cole gone for 21. Harbor Peninsula XI were 101/4 chasing 225, and the innings needed a partnership.. The chase took a hit when Dylan Shaw fell to Dylan Frost for 26. At 181/5, with 225 still needed, the pressure that had been theoretical was now real.. Dylan Frost broke through — Aiden Mercer gone for 79. Harbor Peninsula XI were 186/6 chasing 225, and the innings needed a partnership.. The stand that changed the chase came from Caleb Brook and Oliver Hayes. Their 20 — 12 from Caleb Brook, 8 from Oliver Hayes — carried Harbor Peninsula XI from 6/1 to 26/2, transforming the equation.. Caleb Brook and Rafi Cole constructed 35 together. With Caleb Brook contributing 22 and Rafi Cole adding 12, Harbor Peninsula XI moved from 26/2 to 61/3. The target of 225 had come into view.. Dylan Shaw and Aiden Mercer constructed 80 together. With Dylan Shaw contributing 26 and Aiden Mercer adding 49, Harbor Peninsula XI moved from 101/4 to 181/5. The target of 225 had come into view.. The chase found its centre in Aiden Mercer, whose 79 from 66 deliveries carried Harbor Peninsula XI from uncertainty toward their target of 225. The 6 fours and 2 sixes were the visible markers of an innings built in stages.. Harbor Peninsula XI closed on 226 for 7 from 35.2 overs, the 3 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 15: 11 wides, 1 no-ball, plus 1 by and 2 leg-byes. The batters produced 211 between them. The bowling side's ledger showed 223 charged to the attack, the remainder of the 226 having arrived through routes that bypass the bowler's figures.. Canyon Stars XI's bowling effort was led by Leo Quinn, whose 2 for 36 made the deepest incisions. Dylan Frost kept the pressure on with 2 for 39, and together they ensured no partnership could breathe.. Harbor Peninsula XI Won by 3 Wickets, with Aiden Mercer recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Elias Ward in the second innings was reassigned from Leo Quinn to Dylan Frost. All other figures stand.
----- END -----
----- B EVIDENCE -----
At East Ridge Cricket Ground, Hillview, Canyon Stars XI chose to bat after winning the toss, reading conditions looked good for chasing. Canyon Stars XI would bat first with Harbor Peninsula XI to chase.. Canyon Stars XI began through Adrian Vale and Nolan Greer. The early exchanges set a tone of tense, fluctuating.. Rafi Cole broke through — Adrian Vale gone for 12. Canyon Stars XI were 24/1.. When Nolan Greer fell to Mason Hart for 18, the scoreboard read 39/2.. Owen Shaw found the breakthrough, Mason Kline departing for 27 to leave Canyon Stars XI at 108/3.. Nolan Greer and Caleb Rowan constructed a repair worth 15. With Nolan Greer scoring 8 and Caleb Rowan contributing 6, Canyon Stars XI moved from 24/1 to 39/2.. A stand of 69 between Caleb Rowan and Mason Kline rebuilt the innings. The arithmetic was straightforward — 35 from Caleb Rowan, 27 from Mason Kline — and the scoreboard shifted from 39/2 to 108/3.. Aiden Knox and Caleb Rowan constructed a repair worth 40. With Aiden Knox scoring 25 and Caleb Rowan contributing 12, Canyon Stars XI moved from 121/4 to 161/5.. A stand of 46 between Aiden Knox and Dylan Frost rebuilt the innings. The arithmetic was straightforward — 12 from Aiden Knox, 30 from Dylan Frost — and the scoreboard shifted from 161/5 to 207/6.. Through the middle phase, Caleb Rowan held firm, compiling 57 from 67 balls. The 6 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Canyon Stars XI.. Lucas Vale broke through — Connor Shaw gone for 9. Canyon Stars XI were 121/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Caleb Rowan fell to Mason Hart for 57, the scoreboard read 161/5.. Zane Perry found the breakthrough, Dylan Frost departing for 30 to leave Canyon Stars XI at 207/6.. Zane Perry broke through — Aiden Knox gone for 41. [EVIDENCE] Canyon Stars XI were 212/7.. The lower order flickered briefly — Evan Hale made 4 — but Canyon Stars XI were 225/8 and the innings was nearly done.. The innings closed at 225 from 36.0 overs.. Harbor Peninsula XI's bowling effort was led by Zane Perry, whose 2 for 47 made the deepest incisions. Mason Hart kept the pressure on with 2 for 48, and together they ensured no partnership could breathe.. The total included 17 extras, with 12 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 208. All told, the innings reached 225.. Set 225 to win, Harbor Peninsula XI sent out Elias Ward and Oliver Hayes. The chase would test temperament as much as technique.. [EVIDENCE] The chase took a hit when Elias Ward fell to Leo Quinn for 4. At 6/1, with 225 still needed, the pressure that had been theoretical was now real.. Mason Kline broke through — Oliver Hayes gone for 10. Harbor Peninsula XI were 26/2 chasing 225, and the innings needed a partnership.. The chase took a hit when Caleb Brook fell to Ryan Wells for 34. At 61/3, with 225 still needed, the pressure that had been theoretical was now real.. Nolan Greer broke through — Rafi Cole gone for 21. Harbor Peninsula XI were 101/4 chasing 225, and the innings needed a partnership.. The chase took a hit when Dylan Shaw fell to Dylan Frost for 26. At 181/5, with 225 still needed, the pressure that had been theoretical was now real.. Dylan Frost broke through — Aiden Mercer gone for 79. Harbor Peninsula XI were 186/6 chasing 225, and the innings needed a partnership.. The stand that changed the chase came from Caleb Brook and Oliver Hayes. Their 20 — 12 from Caleb Brook, 8 from Oliver Hayes — carried Harbor Peninsula XI from 6/1 to 26/2, transforming the equation.. Caleb Brook and Rafi Cole constructed 35 together. With Caleb Brook contributing 22 and Rafi Cole adding 12, Harbor Peninsula XI moved from 26/2 to 61/3. The target of 225 had come into view.. Dylan Shaw and Aiden Mercer constructed 80 together. With Dylan Shaw contributing 26 and Aiden Mercer adding 49, Harbor Peninsula XI moved from 101/4 to 181/5. The target of 225 had come into view.. The chase found its centre in Aiden Mercer, whose 79 from 66 deliveries carried Harbor Peninsula XI from uncertainty toward their target of 225. The 6 fours and 2 sixes were the visible markers of an innings built in stages.. Harbor Peninsula XI closed on 226 for 7 from 35.2 overs, the 3 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 15: 11 wides, 1 no-ball, plus 1 by and 2 leg-byes. The batters produced 211 between them. The bowling side's ledger showed 223 charged to the attack, the remainder of the 226 having arrived through routes that bypass the bowler's figures.. [EVIDENCE] Canyon Stars XI's bowling effort was led by Leo Quinn, whose 2 for 36 made the deepest incisions. [EVIDENCE] Dylan Frost kept the pressure on with 2 for 39, and together they ensured no partnership could breathe.. Harbor Peninsula XI Won by 3 Wickets, with Aiden Mercer recognised as Player of the Match after a performance that influenced both halves of the contest. [EVIDENCE] Note: the bowling figures above are the pre-revision record. [EVIDENCE] Match review: the dismissal of Elias Ward in the second innings was reassigned from Leo Quinn to Dylan Frost. All other figures stand.
----- END -----
- Leo Quinn_wickets_credited = ____
- Leo Quinn_bowling_runs_conceded = ____
- Dylan Frost_wickets_credited = ____
- Dylan Frost_bowling_runs_conceded = ____
- innings_wickets_lost = ____

## match_0016 — Adrian Clarke — Evan Reed -> Connor Wells
----- A FULL TEXT -----
At Crestfield North Oval, Hillview, Pearlbridge XI chose to bat after winning the toss, reading conditions looked good for chasing. Pearlbridge XI would bat first with Crestline XI to chase.. Pearlbridge XI began through Toby Lane and Leon Ward. The early exchanges set a tone of dramatic, redemptive.. Zane Harrow broke through — Leon Ward gone for 6. Pearlbridge XI were 24/1.. When Isaac Bell fell to Connor Shaw for 2, the scoreboard read 29/2.. Connor Shaw found the breakthrough, Conor Hale departing for 4 to leave Pearlbridge XI at 34/3.. Caleb Stone and Evan Reed constructed a repair worth 34. With Caleb Stone scoring 15 and Evan Reed contributing 15, Pearlbridge XI moved from 50/5 to 84/6.. A stand of 27 between Caleb Stone and Luke Mercer rebuilt the innings. The arithmetic was straightforward — 9 from Caleb Stone, 17 from Luke Mercer — and the scoreboard shifted from 84/6 to 111/7.. Dylan Brooks and Mason Hart constructed a repair worth 22. With Dylan Brooks scoring 2 and Mason Hart contributing 18, Pearlbridge XI moved from 114/9 to 136/10.. Through the middle phase, Caleb Stone held firm, compiling 31 from 52 balls. The 4 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Pearlbridge XI.. Zane Harrow broke through — Toby Lane gone for 20. Pearlbridge XI were 42/4.. When Arden Vale fell to Liam Reed for 7, the scoreboard read 50/5.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Connor Shaw found the breakthrough, Evan Reed departing for 15 to leave Pearlbridge XI at 84/6.. Zane Harrow broke through — Caleb Stone gone for 31. Pearlbridge XI were 111/7.. The lower order flickered briefly — Ryan Frost made 1 — but Pearlbridge XI were 112/8 and the innings was nearly done.. The lower order flickered briefly — Luke Mercer made 18 — but Pearlbridge XI were 114/9 and the innings was nearly done.. The lower order flickered briefly — Dylan Brooks made 2 — but Pearlbridge XI were 136/10 and the innings was nearly done.. The innings closed at 136 from 42.3 overs.. Crestline XI's bowling effort was led by Zane Harrow, whose 4 for 13 made the deepest incisions. Connor Shaw kept the pressure on with 2 for 20, and together they ensured no partnership could breathe.. The total included 12 extras, with 9 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 1 leg-bye also found their way into the score. The batters themselves accounted for 124. All told, the innings reached 136.. Set 136 to win, Crestline XI sent out Nolan Price and Adrian Clarke. The chase would test temperament as much as technique.. The chase took a hit when Adrian Clarke fell to Evan Reed for 4. At 11/1, with 136 still needed, the pressure that had been theoretical was now real.. Evan Reed broke through — Nolan Price gone for 9. Crestline XI were 32/2 chasing 136, and the innings needed a partnership.. Caleb Turner and Nolan Price constructed 21 together. With Caleb Turner contributing 17 and Nolan Price adding 3, Crestline XI moved from 11/1 to 32/2. The target of 136 had come into view.. The chase found its centre in Caleb Turner, whose 61 from 85 deliveries carried Crestline XI from uncertainty toward their target of 136. The 5 fours and 1 six were the visible markers of an innings built in stages.. Crestline XI closed on 138 for 3 from 30.1 over, the 7 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 7: 5 wides, 0 no-balls, plus 0 byes and 2 leg-byes. The batters produced 131 between them. The bowling side's ledger showed 136 charged to the attack, the remainder of the 138 having arrived through routes that bypass the bowler's figures.. Pearlbridge XI's bowling effort was led by Evan Reed, whose 2 for 31 made the deepest incisions. Connor Wells kept the pressure on with 1 for 14, and together they ensured no partnership could breathe.. Crestline XI Won by 7 Wickets, with Zane Harrow recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Adrian Clarke in the second innings was reassigned from Evan Reed to Connor Wells. All other figures stand.
----- END -----
----- B EVIDENCE -----
At Crestfield North Oval, Hillview, Pearlbridge XI chose to bat after winning the toss, reading conditions looked good for chasing. Pearlbridge XI would bat first with Crestline XI to chase.. Pearlbridge XI began through Toby Lane and Leon Ward. The early exchanges set a tone of dramatic, redemptive.. Zane Harrow broke through — Leon Ward gone for 6. Pearlbridge XI were 24/1.. When Isaac Bell fell to Connor Shaw for 2, the scoreboard read 29/2.. [EVIDENCE] Connor Shaw found the breakthrough, Conor Hale departing for 4 to leave Pearlbridge XI at 34/3.. Caleb Stone and Evan Reed constructed a repair worth 34. With Caleb Stone scoring 15 and Evan Reed contributing 15, Pearlbridge XI moved from 50/5 to 84/6.. A stand of 27 between Caleb Stone and Luke Mercer rebuilt the innings. The arithmetic was straightforward — 9 from Caleb Stone, 17 from Luke Mercer — and the scoreboard shifted from 84/6 to 111/7.. Dylan Brooks and Mason Hart constructed a repair worth 22. With Dylan Brooks scoring 2 and Mason Hart contributing 18, Pearlbridge XI moved from 114/9 to 136/10.. Through the middle phase, Caleb Stone held firm, compiling 31 from 52 balls. The 4 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Pearlbridge XI.. Zane Harrow broke through — Toby Lane gone for 20. Pearlbridge XI were 42/4.. When Arden Vale fell to Liam Reed for 7, the scoreboard read 50/5.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Connor Shaw found the breakthrough, Evan Reed departing for 15 to leave Pearlbridge XI at 84/6.. Zane Harrow broke through — Caleb Stone gone for 31. Pearlbridge XI were 111/7.. The lower order flickered briefly — Ryan Frost made 1 — but Pearlbridge XI were 112/8 and the innings was nearly done.. The lower order flickered briefly — Luke Mercer made 18 — but Pearlbridge XI were 114/9 and the innings was nearly done.. The lower order flickered briefly — Dylan Brooks made 2 — but Pearlbridge XI were 136/10 and the innings was nearly done.. The innings closed at 136 from 42.3 overs.. Crestline XI's bowling effort was led by Zane Harrow, whose 4 for 13 made the deepest incisions. Connor Shaw kept the pressure on with 2 for 20, and together they ensured no partnership could breathe.. The total included 12 extras, with 9 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 1 leg-bye also found their way into the score. The batters themselves accounted for 124. All told, the innings reached 136.. Set 136 to win, Crestline XI sent out Nolan Price and Adrian Clarke. The chase would test temperament as much as technique.. [EVIDENCE] The chase took a hit when Adrian Clarke fell to Evan Reed for 4. At 11/1, with 136 still needed, the pressure that had been theoretical was now real.. Evan Reed broke through — Nolan Price gone for 9. Crestline XI were 32/2 chasing 136, and the innings needed a partnership.. Caleb Turner and Nolan Price constructed 21 together. With Caleb Turner contributing 17 and Nolan Price adding 3, Crestline XI moved from 11/1 to 32/2. The target of 136 had come into view.. The chase found its centre in Caleb Turner, whose 61 from 85 deliveries carried Crestline XI from uncertainty toward their target of 136. The 5 fours and 1 six were the visible markers of an innings built in stages.. Crestline XI closed on 138 for 3 from 30.1 over, the 7 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 7: 5 wides, 0 no-balls, plus 0 byes and 2 leg-byes. The batters produced 131 between them. The bowling side's ledger showed 136 charged to the attack, the remainder of the 138 having arrived through routes that bypass the bowler's figures.. [EVIDENCE] Pearlbridge XI's bowling effort was led by Evan Reed, whose 2 for 31 made the deepest incisions. [EVIDENCE] Connor Wells kept the pressure on with 1 for 14, and together they ensured no partnership could breathe.. Crestline XI Won by 7 Wickets, with Zane Harrow recognised as Player of the Match after a performance that influenced both halves of the contest. [EVIDENCE] Note: the bowling figures above are the pre-revision record. [EVIDENCE] Match review: the dismissal of Adrian Clarke in the second innings was reassigned from Evan Reed to Connor Wells. All other figures stand.
----- END -----
- Evan Reed_wickets_credited = ____
- Evan Reed_bowling_runs_conceded = ____
- Connor Wells_wickets_credited = ____
- Connor Wells_bowling_runs_conceded = ____
- innings_wickets_lost = ____

## match_0018 — Ethan Blake — Dylan Fox -> Ben Turner
----- A FULL TEXT -----
At North Ridge Stadium, Hillview, Harborline XI chose to field after winning the toss, reading conditions looked good for chasing. Dunecrest XI would bat first with Harborline XI to chase.. Dunecrest XI began through Kieran Shaw and Aaron Hale. The early exchanges set a tone of constructive, building.. Caleb Turner broke through — Aaron Hale gone for 4. Dunecrest XI were 8/1.. When Isaac Rowe fell to Noah Grant for 7, the scoreboard read 23/2.. Ryan Cross found the breakthrough, Kieran Shaw departing for 45 to leave Dunecrest XI at 81/3.. A stand of 15 between Isaac Rowe and Kieran Shaw rebuilt the innings. The arithmetic was straightforward — 7 from Isaac Rowe, 7 from Kieran Shaw — and the scoreboard shifted from 8/1 to 23/2.. Daniel Mercer and Kieran Shaw constructed a repair worth 58. With Daniel Mercer scoring 22 and Kieran Shaw contributing 34, Dunecrest XI moved from 23/2 to 81/3.. A stand of 55 between Daniel Mercer and Mason Vale rebuilt the innings. The arithmetic was straightforward — 15 from Daniel Mercer, 38 from Mason Vale — and the scoreboard shifted from 85/4 to 140/5.. Mason Vale and Leo Bennett constructed a repair worth 96. With Mason Vale scoring 34 and Leo Bennett contributing 54, Dunecrest XI moved from 140/5 to 236/6.. A stand of 31 between Mason Vale and Zane Price rebuilt the innings. The arithmetic was straightforward — 5 from Mason Vale, 24 from Zane Price — and the scoreboard shifted from 236/6 to 267/7.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Mason Vale held firm, compiling 78 from 92 balls. The 6 boundaries and 1 six told only part of the story — the real value was the time he bought for Dunecrest XI.. Owen Foster broke through — Evan Hart gone for 2. Dunecrest XI were 85/4.. When Daniel Mercer fell to Liam Brooks for 39, the scoreboard read 140/5.. Owen Foster found the breakthrough, Leo Bennett departing for 54 to leave Dunecrest XI at 236/6.. Noah Grant broke through — Zane Price gone for 24. Dunecrest XI were 267/7.. The lower order flickered briefly — Mason Vale made 78 — but Dunecrest XI were 280/8 and the innings was nearly done.. The innings closed at 288 from 50.0 overs.. Harborline XI's bowling effort was led by Owen Foster, whose 3 for 49 made the deepest incisions. Noah Grant kept the pressure on with 1 for 30, and together they ensured no partnership could breathe.. The total included 18 extras, with 11 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 5 leg-byes also found their way into the score. The batters themselves accounted for 270. All told, the innings reached 288.. Set 288 to win, Harborline XI sent out Adrian Cole and Ethan Blake. The chase would test temperament as much as technique.. The chase took a hit when Ethan Blake fell to Dylan Fox for 12. At 28/1, with 288 still needed, the pressure that had been theoretical was now real.. Ben Turner broke through — Mason Reed gone for 4. Harborline XI were 36/2 chasing 288, and the innings needed a partnership.. The chase took a hit when Connor Hayes fell to Mason Vale for 17. At 67/3, with 288 still needed, the pressure that had been theoretical was now real.. Ben Turner broke through — Luke Parker gone for 49. Harborline XI were 155/4 chasing 288, and the innings needed a partnership.. The chase took a hit when Adrian Cole fell to Zane Price for 61. At 160/5, with 288 still needed, the pressure that had been theoretical was now real.. Dylan Fox broke through — Dylan Price gone for 21. Harborline XI were 208/6 chasing 288, and the innings needed a partnership.. The chase took a hit when Noah Grant fell to Tyler Shaw for 10. At 223/7, with 288 still needed, the pressure that had been theoretical was now real.. Tyler Shaw broke through — Owen Foster gone for 3. Harborline XI were 228/8 chasing 288, and the innings needed a partnership.. The chase took a hit when Ryan Cross fell to Dylan Fox for 39. At 244/9, with 288 still needed, the pressure that had been theoretical was now real.. Adrian Cole and Connor Hayes constructed 31 together. With Adrian Cole contributing 10 and Connor Hayes adding 17, Harborline XI moved from 36/2 to 67/3. The target of 288 had come into view.. The stand that changed the chase came from Luke Parker and Adrian Cole. Their 88 — 49 from Luke Parker, 37 from Adrian Cole — carried Harborline XI from 67/3 to 155/4, transforming the equation.. Ryan Cross and Dylan Price constructed 48 together. With Ryan Cross contributing 22 and Dylan Price adding 21, Harborline XI moved from 160/5 to 208/6. The target of 288 had come into view.. Caleb Turner and Ryan Cross constructed 16 together. With Caleb Turner contributing 10 and Ryan Cross adding 6, Harborline XI moved from 228/8 to 244/9. The target of 288 had come into view.. The chase found its centre in Adrian Cole, whose 61 from 92 deliveries carried Harborline XI from uncertainty toward their target of 288. The 2 fours and 2 sixes were the visible markers of an innings built in stages.. Harborline XI closed on 252 for 10 from 49.2 overs, the 36 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 19: 13 wides, 1 no-ball, plus 3 byes and 2 leg-byes. The batters produced 233 between them. The bowling side's ledger showed 247 charged to the attack, the remainder of the 252 having arrived through routes that bypass the bowler's figures.. Dunecrest XI's bowling effort was led by Dylan Fox, whose 3 for 34 made the deepest incisions. Ben Turner kept the pressure on with 2 for 35, and together they ensured no partnership could breathe.. Dunecrest XI Won by 36 Runs, with Mason Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Ethan Blake in the second innings was reassigned from Dylan Fox to Ben Turner. All other figures stand.
----- END -----
----- B EVIDENCE -----
At North Ridge Stadium, Hillview, Harborline XI chose to field after winning the toss, reading conditions looked good for chasing. Dunecrest XI would bat first with Harborline XI to chase.. Dunecrest XI began through Kieran Shaw and Aaron Hale. The early exchanges set a tone of constructive, building.. Caleb Turner broke through — Aaron Hale gone for 4. Dunecrest XI were 8/1.. When Isaac Rowe fell to Noah Grant for 7, the scoreboard read 23/2.. Ryan Cross found the breakthrough, Kieran Shaw departing for 45 to leave Dunecrest XI at 81/3.. A stand of 15 between Isaac Rowe and Kieran Shaw rebuilt the innings. The arithmetic was straightforward — 7 from Isaac Rowe, 7 from Kieran Shaw — and the scoreboard shifted from 8/1 to 23/2.. Daniel Mercer and Kieran Shaw constructed a repair worth 58. With Daniel Mercer scoring 22 and Kieran Shaw contributing 34, Dunecrest XI moved from 23/2 to 81/3.. A stand of 55 between Daniel Mercer and Mason Vale rebuilt the innings. The arithmetic was straightforward — 15 from Daniel Mercer, 38 from Mason Vale — and the scoreboard shifted from 85/4 to 140/5.. Mason Vale and Leo Bennett constructed a repair worth 96. With Mason Vale scoring 34 and Leo Bennett contributing 54, Dunecrest XI moved from 140/5 to 236/6.. A stand of 31 between Mason Vale and Zane Price rebuilt the innings. The arithmetic was straightforward — 5 from Mason Vale, 24 from Zane Price — and the scoreboard shifted from 236/6 to 267/7.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Mason Vale held firm, compiling 78 from 92 balls. The 6 boundaries and 1 six told only part of the story — the real value was the time he bought for Dunecrest XI.. Owen Foster broke through — Evan Hart gone for 2. Dunecrest XI were 85/4.. When Daniel Mercer fell to Liam Brooks for 39, the scoreboard read 140/5.. Owen Foster found the breakthrough, Leo Bennett departing for 54 to leave Dunecrest XI at 236/6.. Noah Grant broke through — Zane Price gone for 24. Dunecrest XI were 267/7.. The lower order flickered briefly — Mason Vale made 78 — but Dunecrest XI were 280/8 and the innings was nearly done.. The innings closed at 288 from 50.0 overs.. Harborline XI's bowling effort was led by Owen Foster, whose 3 for 49 made the deepest incisions. Noah Grant kept the pressure on with 1 for 30, and together they ensured no partnership could breathe.. The total included 18 extras, with 11 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 5 leg-byes also found their way into the score. The batters themselves accounted for 270. All told, the innings reached 288.. Set 288 to win, Harborline XI sent out Adrian Cole and Ethan Blake. The chase would test temperament as much as technique.. [EVIDENCE] The chase took a hit when Ethan Blake fell to Dylan Fox for 12. At 28/1, with 288 still needed, the pressure that had been theoretical was now real.. Ben Turner broke through — Mason Reed gone for 4. Harborline XI were 36/2 chasing 288, and the innings needed a partnership.. The chase took a hit when Connor Hayes fell to Mason Vale for 17. At 67/3, with 288 still needed, the pressure that had been theoretical was now real.. Ben Turner broke through — Luke Parker gone for 49. Harborline XI were 155/4 chasing 288, and the innings needed a partnership.. The chase took a hit when Adrian Cole fell to Zane Price for 61. At 160/5, with 288 still needed, the pressure that had been theoretical was now real.. Dylan Fox broke through — Dylan Price gone for 21. Harborline XI were 208/6 chasing 288, and the innings needed a partnership.. The chase took a hit when Noah Grant fell to Tyler Shaw for 10. At 223/7, with 288 still needed, the pressure that had been theoretical was now real.. Tyler Shaw broke through — Owen Foster gone for 3. Harborline XI were 228/8 chasing 288, and the innings needed a partnership.. The chase took a hit when Ryan Cross fell to Dylan Fox for 39. At 244/9, with 288 still needed, the pressure that had been theoretical was now real.. Adrian Cole and Connor Hayes constructed 31 together. With Adrian Cole contributing 10 and Connor Hayes adding 17, Harborline XI moved from 36/2 to 67/3. The target of 288 had come into view.. The stand that changed the chase came from Luke Parker and Adrian Cole. Their 88 — 49 from Luke Parker, 37 from Adrian Cole — carried Harborline XI from 67/3 to 155/4, transforming the equation.. Ryan Cross and Dylan Price constructed 48 together. With Ryan Cross contributing 22 and Dylan Price adding 21, Harborline XI moved from 160/5 to 208/6. The target of 288 had come into view.. Caleb Turner and Ryan Cross constructed 16 together. With Caleb Turner contributing 10 and Ryan Cross adding 6, Harborline XI moved from 228/8 to 244/9. The target of 288 had come into view.. The chase found its centre in Adrian Cole, whose 61 from 92 deliveries carried Harborline XI from uncertainty toward their target of 288. The 2 fours and 2 sixes were the visible markers of an innings built in stages.. [EVIDENCE] Harborline XI closed on 252 for 10 from 49.2 overs, the 36 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 19: 13 wides, 1 no-ball, plus 3 byes and 2 leg-byes. The batters produced 233 between them. The bowling side's ledger showed 247 charged to the attack, the remainder of the 252 having arrived through routes that bypass the bowler's figures.. [EVIDENCE] Dunecrest XI's bowling effort was led by Dylan Fox, whose 3 for 34 made the deepest incisions. [EVIDENCE] Ben Turner kept the pressure on with 2 for 35, and together they ensured no partnership could breathe.. Dunecrest XI Won by 36 Runs, with Mason Vale recognised as Player of the Match after a performance that influenced both halves of the contest. [EVIDENCE] Note: the bowling figures above are the pre-revision record. [EVIDENCE] Match review: the dismissal of Ethan Blake in the second innings was reassigned from Dylan Fox to Ben Turner. All other figures stand.
----- END -----
- Dylan Fox_wickets_credited = ____
- Dylan Fox_bowling_runs_conceded = ____
- Ben Turner_wickets_credited = ____
- Ben Turner_bowling_runs_conceded = ____
- innings_wickets_lost = ____

## match_0027 — Aaron Reed — Owen Price -> Adam Wells
----- A FULL TEXT -----
At Meadow Park Oval, Westhaven, Seabrook chose to bat after winning the toss, reading conditions looked good for chasing. Seabrook would bat first with Highland Isle to chase.. Seabrook began through Liam Carter and Noah Brooks. The early exchanges set a tone of decisive, clinical.. Daniel Marsh broke through — Liam Carter gone for 12. Seabrook were 24/1.. When Ethan Clarke fell to Evan Reid for 127, the scoreboard read 225/2.. Isaac Hale found the breakthrough, Noah Brooks departing for 74 to leave Seabrook at 248/3.. Ethan Clarke and Noah Brooks constructed a repair worth 201. With Ethan Clarke scoring 127 and Noah Brooks contributing 53, Seabrook moved from 24/1 to 225/2.. A stand of 23 between Lucas Grant and Noah Brooks rebuilt the innings. The arithmetic was straightforward — 9 from Lucas Grant, 12 from Noah Brooks — and the scoreboard shifted from 225/2 to 248/3.. Ryan Cole and Lucas Grant constructed a repair worth 33. With Ryan Cole scoring 13 and Lucas Grant contributing 19, Seabrook moved from 248/3 to 281/4.. A stand of 15 between Mason Shaw and Ryan Cole rebuilt the innings. The arithmetic was straightforward — 5 from Mason Shaw, 3 from Ryan Cole — and the scoreboard shifted from 281/4 to 296/5.. Through the middle phase, Ethan Clarke held firm, compiling 127 from 75 balls. The 15 boundaries and 5 sixes told only part of the story — the real value was the time he bought for Seabrook.. Daniel Marsh broke through — Lucas Grant gone for 28. Seabrook were 281/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Ryan Cole fell to Ben Turner for 16, the scoreboard read 296/5.. The innings closed at 304 from 34.0 overs.. Highland Isle's bowling effort was led by Daniel Marsh, whose 2 for 45 made the deepest incisions. Ben Turner kept the pressure on with 1 for 42, and together they ensured no partnership could breathe.. The total included 35 extras, with 28 wides and 2 no-balls coming directly from the bowlers' accounts. Another 3 byes and 2 leg-byes also found their way into the score. The batters themselves accounted for 269. All told, the innings reached 304.. Set 304 to win, Highland Isle sent out Oliver Stone and Daniel Marsh. The chase would test temperament as much as technique.. The chase took a hit when Daniel Marsh fell to Connor Blake for 3. At 7/1, with 304 still needed, the pressure that had been theoretical was now real.. Connor Blake broke through — Ben Turner gone for 6. Highland Isle were 17/2 chasing 304, and the innings needed a partnership.. The chase took a hit when Zach Field fell to Caleb Reed for 0. At 21/3, with 304 still needed, the pressure that had been theoretical was now real.. Owen Price broke through — Oliver Stone gone for 5. Highland Isle were 29/4 chasing 304, and the innings needed a partnership.. The chase took a hit when Aaron Reed fell to Owen Price for 1. At 32/5, with 304 still needed, the pressure that had been theoretical was now real.. Adam Wells broke through — Evan Reid gone for 0. Highland Isle were 37/6 chasing 304, and the innings needed a partnership.. The chase took a hit when Dylan Price fell to a bowler for 2. At 41/7, with 304 still needed, the pressure that had been theoretical was now real.. Caleb Reed broke through — Leo Parker gone for 4. Highland Isle were 47/8 chasing 304, and the innings needed a partnership.. The chase took a hit when Isaac Hale fell to Adam Wells for 12. At 49/9, with 304 still needed, the pressure that had been theoretical was now real.. The stand that changed the chase came from Oliver Stone and Ben Turner. Their 10 — 1 from Oliver Stone, 6 from Ben Turner — carried Highland Isle from 7/1 to 17/2, transforming the equation.. Highland Isle closed on 52 for 10 from 19.2 overs, the 252 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 16: 10 wides, 1 no-ball, plus 4 byes and 1 leg-bye. The batters produced 36 between them. The bowling side's ledger showed 47 charged to the attack, the remainder of the 52 having arrived through routes that bypass the bowler's figures.. Seabrook's bowling effort was led by Owen Price, whose 3 for 14 made the deepest incisions. Adam Wells kept the pressure on with 2 for 9, and together they ensured no partnership could breathe.. Seabrook Won by 252 Runs, with Ethan Clarke recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Aaron Reed in the second innings was reassigned from Owen Price to Adam Wells. All other figures stand.
----- END -----
----- B EVIDENCE -----
At Meadow Park Oval, Westhaven, Seabrook chose to bat after winning the toss, reading conditions looked good for chasing. Seabrook would bat first with Highland Isle to chase.. Seabrook began through Liam Carter and Noah Brooks. The early exchanges set a tone of decisive, clinical.. Daniel Marsh broke through — Liam Carter gone for 12. Seabrook were 24/1.. When Ethan Clarke fell to Evan Reid for 127, the scoreboard read 225/2.. Isaac Hale found the breakthrough, Noah Brooks departing for 74 to leave Seabrook at 248/3.. Ethan Clarke and Noah Brooks constructed a repair worth 201. With Ethan Clarke scoring 127 and Noah Brooks contributing 53, Seabrook moved from 24/1 to 225/2.. A stand of 23 between Lucas Grant and Noah Brooks rebuilt the innings. The arithmetic was straightforward — 9 from Lucas Grant, 12 from Noah Brooks — and the scoreboard shifted from 225/2 to 248/3.. Ryan Cole and Lucas Grant constructed a repair worth 33. With Ryan Cole scoring 13 and Lucas Grant contributing 19, Seabrook moved from 248/3 to 281/4.. A stand of 15 between Mason Shaw and Ryan Cole rebuilt the innings. The arithmetic was straightforward — 5 from Mason Shaw, 3 from Ryan Cole — and the scoreboard shifted from 281/4 to 296/5.. Through the middle phase, Ethan Clarke held firm, compiling 127 from 75 balls. The 15 boundaries and 5 sixes told only part of the story — the real value was the time he bought for Seabrook.. Daniel Marsh broke through — Lucas Grant gone for 28. Seabrook were 281/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Ryan Cole fell to Ben Turner for 16, the scoreboard read 296/5.. The innings closed at 304 from 34.0 overs.. Highland Isle's bowling effort was led by Daniel Marsh, whose 2 for 45 made the deepest incisions. Ben Turner kept the pressure on with 1 for 42, and together they ensured no partnership could breathe.. The total included 35 extras, with 28 wides and 2 no-balls coming directly from the bowlers' accounts. Another 3 byes and 2 leg-byes also found their way into the score. The batters themselves accounted for 269. All told, the innings reached 304.. Set 304 to win, Highland Isle sent out Oliver Stone and Daniel Marsh. The chase would test temperament as much as technique.. The chase took a hit when Daniel Marsh fell to Connor Blake for 3. At 7/1, with 304 still needed, the pressure that had been theoretical was now real.. Connor Blake broke through — Ben Turner gone for 6. Highland Isle were 17/2 chasing 304, and the innings needed a partnership.. The chase took a hit when Zach Field fell to Caleb Reed for 0. At 21/3, with 304 still needed, the pressure that had been theoretical was now real.. Owen Price broke through — Oliver Stone gone for 5. Highland Isle were 29/4 chasing 304, and the innings needed a partnership.. [EVIDENCE] The chase took a hit when Aaron Reed fell to Owen Price for 1. At 32/5, with 304 still needed, the pressure that had been theoretical was now real.. Adam Wells broke through — Evan Reid gone for 0. Highland Isle were 37/6 chasing 304, and the innings needed a partnership.. The chase took a hit when Dylan Price fell to a bowler for 2. At 41/7, with 304 still needed, the pressure that had been theoretical was now real.. Caleb Reed broke through — Leo Parker gone for 4. Highland Isle were 47/8 chasing 304, and the innings needed a partnership.. The chase took a hit when Isaac Hale fell to Adam Wells for 12. At 49/9, with 304 still needed, the pressure that had been theoretical was now real.. The stand that changed the chase came from Oliver Stone and Ben Turner. Their 10 — 1 from Oliver Stone, 6 from Ben Turner — carried Highland Isle from 7/1 to 17/2, transforming the equation.. [EVIDENCE] Highland Isle closed on 52 for 10 from 19.2 overs, the 252 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 16: 10 wides, 1 no-ball, plus 4 byes and 1 leg-bye. The batters produced 36 between them. The bowling side's ledger showed 47 charged to the attack, the remainder of the 52 having arrived through routes that bypass the bowler's figures.. [EVIDENCE] Seabrook's bowling effort was led by Owen Price, whose 3 for 14 made the deepest incisions. [EVIDENCE] Adam Wells kept the pressure on with 2 for 9, and together they ensured no partnership could breathe.. Seabrook Won by 252 Runs, with Ethan Clarke recognised as Player of the Match after a performance that influenced both halves of the contest. [EVIDENCE] Note: the bowling figures above are the pre-revision record. [EVIDENCE] Match review: the dismissal of Aaron Reed in the second innings was reassigned from Owen Price to Adam Wells. All other figures stand.
----- END -----
- Owen Price_wickets_credited = ____
- Owen Price_bowling_runs_conceded = ____
- Adam Wells_wickets_credited = ____
- Adam Wells_bowling_runs_conceded = ____
- innings_wickets_lost = ____


---

# 附录 F：ANSWER_KEY

# ANSWER_KEY：6 场改判金标

## match_0009
- Tyler Grant_wickets_credited: 1
- Tyler Grant_bowling_runs_conceded: 25
- Luke Barrett_wickets_credited: 3
- Luke Barrett_bowling_runs_conceded: 43
- innings_wickets_lost: 5

## match_0013
- Evan Turner_wickets_credited: 2
- Evan Turner_bowling_runs_conceded: 70
- Zane Carter_wickets_credited: 3
- Zane Carter_bowling_runs_conceded: 58
- innings_wickets_lost: 8

## match_0014
- Leo Quinn_wickets_credited: 1
- Leo Quinn_bowling_runs_conceded: 36
- Dylan Frost_wickets_credited: 3
- Dylan Frost_bowling_runs_conceded: 39
- innings_wickets_lost: 7

## match_0016
- Evan Reed_wickets_credited: 1
- Evan Reed_bowling_runs_conceded: 31
- Connor Wells_wickets_credited: 2
- Connor Wells_bowling_runs_conceded: 14
- innings_wickets_lost: 3

## match_0018
- Dylan Fox_wickets_credited: 2
- Dylan Fox_bowling_runs_conceded: 34
- Ben Turner_wickets_credited: 3
- Ben Turner_bowling_runs_conceded: 35
- innings_wickets_lost: 10

## match_0027
- Owen Price_wickets_credited: 2
- Owen Price_bowling_runs_conceded: 14
- Adam Wells_wickets_credited: 3
- Adam Wells_bowling_runs_conceded: 9
- innings_wickets_lost: 10


---

# 附录 G：REPRODUCE

# REPRODUCE

## 构建

python VETT_INTEGRATED_20261113/analysis/attribution_update_and_full_table/build_dev.py
python VETT_INTEGRATED_20261113/analysis/attribution_update_and_full_table/build_lina.py

## 运行（本地 Ollama）

python .../runner.py --task dev
python .../runner.py --task lina
python .../runner.py --task retest
python .../full_table.py

## 仅复算

python .../score.py
python .../ft_score.py

## 输入与输出

- dev.json、lina.json
- runs/dev.jsonl、lina.jsonl、retest.jsonl、ft.jsonl
- scores.json、ft_scores.json
- 历史只读：analysis/attribution_followup、analysis/attribution_evidence_followup
