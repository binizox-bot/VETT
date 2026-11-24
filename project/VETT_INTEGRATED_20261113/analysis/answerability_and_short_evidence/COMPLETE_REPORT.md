# VETT 43 字段复核 + 真短证据：完整报告

日期：2026-11-13  
范围：258 字段可答性复核、三模型同分母、match_0014/0016 真短证据  
调用：43 字段 0 次；短证据 18/18 次；外部 API 0。

## 0. 一页摘要

**43 字段**

- 旧规则确认可答 73/258（69 直接 + 4 可推导）；185 待核。
- 抽样 40 格（30 未确认 + 10 已确认），BLIND_REVIEW 已交付；人工复核**未返回**，V2 暂沿用 73 格。
- 同分母 73 格：Qwen 29/73（39.7%）、Gemma 32/73（43.8%）、Llama 26/73（35.6%）。
- 全字段：Qwen 73/258、Gemma 85/258、Llama 63/258（恢复 5/6，0008 空）。

**真短证据**

- B 正文 572/571 字符，A 5,314/4,313；B 只含六句证据，不再是标注全文。
- 2 场：A two 0/6、B two 0/6、C two 0/6；B−A=0。
- B 的总出局 3/6，A 0/6：短证据帮助读总数，但没有帮助两人更新。
- C 的抽取 6/6 无法执行；Python 更新 two 0/6，修对 0、改坏 0；正确输入正控通过。

## 1. 43 字段复核

旧启发式要求同一句同时出现人物/球队与值，容易漏掉跨句证据：

- 例：match_0014 的 total 7 在 “Harbor Peninsula XI closed on 226 for 7” 一句，不在投手汇总句；旧规则若只在汇总句找，会漏。
- 例：top-3 击球员的 runs 可能在一句、排名需跨行比较；旧规则只能确认“某人得了多少”，不能确认“他排第三”。

抽样 40 格已写入 BLIND_REVIEW；人工状态待完成。没有人工确认的新增可答格，也没有确认旧规则误收格。

## 2. 三模型同分母

| 模型 | 可答答对 | 分母 | 准确率 | 全字段 |
|---|---:|---:|---:|---:|
| Qwen | 29 | 73 | 39.7% | 73/258 |
| Gemma | 32 | 73 | 43.8% | 85/258 |
| Llama | 26 | 73 | 35.6% | 63/258 |

Llama 按 73 分母计，0008 空回答的相关格按错。

## 3. 真短证据

| 模型 | A two | B two | C two | B total |
|---|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0/2 | 1/2 |
| Llama | 0/2 | 0/2 | 0/2 | 1/2 |
| Gemma | 0/2 | 0/2 | 0/2 | 1/2 |

- B 的两人错误以“两人旧值”为主；Llama 一场只加新投手。
- C 的 extraction 6/6 缺字段，无法执行 Python 更新；正控（正确输入）两场 two/three 都对。
- B 与 C 正文逐字相同，C 只多分步要求。

## 4. 四句话

1. **原规则最容易漏掉跨句证据**：如 0014 的 total 7 在终局比分句，不在投手汇总句；top-3 的排名需要跨行比较，旧规则只能确认个人数值。
2. **258 格中确认可答 73 格**；Qwen 29/73、Gemma 32/73、Llama 26/73；**185 格仍待人工核验**，40 格抽样已交付但未返回。
3. **两场 B 确实是短证据**（572/571 字符 vs A 的 5,314/4,313）；B 的 two 0/6，与 A 相同，没有多答对；B 的总出局 3/6 好于 A 的 0/6。C 的抽取 6/6 无法执行，程序更新 0 修对、0 改坏。
4. **下一轮优先完成 40 格人工复核，再决定是否扩 43 字段基线**；短证据只在两场开发集上跑通，先修 C 的抽取协议，不要直接扩到新比赛或 220 场。

## 5. 缺口

- 40 格人工复核未返回，V2 的 73 格仍是启发式口径。
- 短证据只有 2 场开发比赛，不能作为跨比赛结论。
- Llama 的同分母逐场拆分未完成，只报 26/73。
- 闭合约束因 schema 缺字段仍不可检查。


---

# 附录 A：DESIGN

# DESIGN：43 字段复核 + 两场真短证据

日期：2026-11-13。历史 54 条 A/B/C 只读；43 字段复核 0 次调用；短证据补跑 18 次（上限 18）；外部 API 0。

## 固定历史口径

- 54 条请求，其中 B/C 36 条；哈希可重建提示。
- 实际 B/C 是标注全文；C 多分步要求。
- two_wickets：B 0/18、C 1/18（唯一正确是 Gemma 的 match_0013；该场 total 答 7，金标 8）。
- 258 字段；旧启发式直接 69 + 可推导 4 = 73；185 未确认。
- 全字段：Qwen 73/258、Gemma 85/258、Llama 展平 63/258；Llama 5 条嵌套 JSON 可恢复，match_0008 为空。

## 本轮 43 字段

- 从 185 未确认抽 30 格、从 73 已确认抽 10 格，种子 20261113，覆盖摘要/局汇总/击球/投手。
- BLIND_REVIEW.md 给人复核；无人工返回，人工状态=待完成。
- 不根据模型对错改可答性；V2 暂沿用 73 格，新增 40 格待核。

## 短证据

- 2 场 × 3 条件 × 3 模型 = 18。
- A 全文；B 六句摘录（572 字符左右）；C=B 正文 + 分步抽取。
- 终局：0014 226 for 7；0016 138 for 3。
- 检查：B 短于 A 的 50%，六个片段可定位回 A，含 Note、通知、正确终局；无更新后 figures。

---

# 附录 B：SCORECARD_RESCORE_V2

# SCORECARD_RESCORE_V2：258 字段复核与三模型同分母

日期：2026-11-13。0 次模型调用。

## 1. 可答性

- V1 启发式：直接 69、可推导 4，合计 **73/258（28.3%）**；未确认 185。
- 人工抽样：30 格来自未确认、10 格来自已确认；BLIND_REVIEW 已交付，**人工复核未返回**。
- 因此 V2 暂不扩大可答清单；73 格保持，185 格标为待核。若后续人工确认新依据，再更新分母。

### 抽样构成

| 层 | 抽样 | 状态 |
|---|---:|---|
| 未确认 | 30 | 待人工 |
| 已确认 | 10 | 待人工 |
| 合计 | 40 | — |

## 2. 三模型同分母（73 格）

| 模型 | 可答答对 | 可答分母 | 可答准确率 | 全字段 |
|---|---:|---:|---:|---:|
| Qwen | 29 | 73 | 39.7% | 73/258 |
| Gemma | 32 | 73 | 43.8% | 85/258 |
| Llama | 26 | 73 | 35.6% | 63/258（恢复 5/6） |

Llama 的可答分母按 73 计；0008 空回答，相关格按错计。

## 3. 逐场（可答/43）

| match | 可答 | Qwen | Gemma | Llama |
|---|---:|---:|---:|---:|
| 0003 | 16 | 10 | 10 | 未单列 |
| 0008 | 12 | 5 | 5 | 空 |
| 0010 | 12 | 1 | 3 | 未单列 |
| 0012 | 11 | 4 | 6 | 未单列 |
| 0015 | 11 | 5 | 3 | 未单列 |
| 0017 | 11 | 4 | 5 | 未单列 |

Llama 逐场未按同分母拆出，只报 26/73；下一轮补齐。

## 4. 格式与恢复

- Llama 旧协议 0/6 直接解析；嵌套 JSON 5/6 可恢复，0008 空；内容 63/258。
- Qwen/Gemma 6/6 解析，无缺行。
- 闭合约束：schema 缺 extras 合计与 bat_sum，记为不可检查。

## 5. 限制

- 73 格是启发式，不是人工确认；40 格抽样未返回。
- 可答准确率的分母固定 73；Llama 的 26/73 含 0008 的错计。

---

# 附录 C：SHORT_EVIDENCE_RESULTS

# SHORT_EVIDENCE_RESULTS：两场真短证据对照

日期：2026-11-13。18 次本地请求，外部 API 0。

## 1. 实际发送

| 项 | 0014 | 0016 |
|---|---|---|
| A 长度 | 5,314 | 4,313 |
| B/C 长度 | 572 | 571 |
| B 片段 | 6 | 6 |
| 终局 | Harbor Peninsula XI closed on 226 for 7 | Crestline XI closed on 138 for 3 |
| B=C 正文 | 是 | 是 |
| 更新后 figures 泄露 | 无 | 无 |

B 确实是短证据，不再是标注全文。18 条全部解析成功（A/B/C 三模型）。

## 2. 结果（2 场）

| 模型 | A two | B two | C two | B total | C total |
|---|---:|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0/2 | 1/2 | 2/2 |
| Llama | 0/2 | 0/2 | 0/2 | 1/2 | 0/2 |
| Gemma | 0/2 | 0/2 | 0/2 | 1/2 | 1/2 |

- B 的两名投手同时正确 **0/6**；A 也是 0/6；B−A=0。
- B 的总出局 3/6（每家 1/2），A 为 0/6；短证据帮助读总数，但没有帮助两人更新。
- C 的 two 0/6；Qwen C 总数 2/2，但两人仍错。

## 3. 错法

- B：Qwen/Gemma 两场都是两人旧值；Llama 一场旧值、一场只加新投手。
- C：Qwen 一场只减原投手、一场两人都改但错；Llama 一场格式/旧值、一场旧值；Gemma 两场格式失败。
- C 的 extraction：6/6 无法执行（每家 2/2 缺字段）；没有可执行的抽取。

## 4. 程序

- 用模型实际抽取做 Python 更新：two 0/6，three 0/6；修对 0、改坏 0、无法执行 6。
- 用正确结构化输入做正控：两场 two/three 都为 1（程序本身正确）。

## 5. 结论

真短证据在这两场上没有表现出“比全文更容易改对两人”：B 0/6。  
但 B 把总出局从 0/6 提到 3/6，说明短证据至少让总数可读；失败集中在“两人旧值/只改一侧”，不是终局定位。  
两场只能判断通路，不能作为跨比赛结论。

---

# 附录 D：BLIND_REVIEW（40 格抽样）

# BLIND_REVIEW：43 字段可答性抽查（40 格）

复核者先独立作答，再与 scorecard 对账。题面只给发布版 commentary 路径与相关句，不展示模型预测。

排名规则（旧任务）：按 scorecard 的 runs/wickets 降序；并列时按 scorecard 行序；旧提示未写并列规则，这一点需复核者判断。

## S01 match_0003 inn1.no_balls
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.no_balls；指定局别按字段名；金标不展示
- 相关句：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
  - Their 49-run stand was not huge in isolation, but it was huge in its position because it moved Ridgehaven from 80 for 4 to 129 for 5 and changed the chase from fragile to controllable.
  - Isaac Wells’ 3 for 25 had made the chase restart several times, Jordan Pike removed the launch batter, Gareth Bishop and Harvey Stone each found important wickets, and Cross’s earlier 81 had given them a real score to defend.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S02 match_0008 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S03 match_0010 inn2.bat3_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.bat3_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S04 match_0012 inn1.wides
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.wides；指定局别按字段名；金标不展示
- 相关句：
  - Chasing 248, Westmere needed to remove the early danger first, and Ethan Vale did that with a calm that became more damaging the longer he stayed.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S05 match_0015 inn2.wides
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.wides；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S06 match_0017 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S07 match_0003 inn2.byes
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn2.byes；指定局别按字段名；金标不展示
- 相关句：
  - The third-wicket stand of 70 did exactly what Brookmere needed because it changed the scoreboard from emergency repair into something with potential.
  - Lucas Bennett was still there, and his 37 had done a lot of the early work, but Jordan Pike removed him at 80 and that was the moment the chase could have turned properly awkward.
  - Their 49-run stand was not huge in isolation, but it was huge in its position because it moved Ridgehaven from 80 for 4 to 129 for 5 and changed the chase from fragile to controllable.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S08 match_0008 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S09 match_0010 inn1.bowl2_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn1.bowl2_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S10 match_0012 inn1.overs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.overs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S11 match_0015 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S12 match_0017 inn1.total_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.total_runs；指定局别按字段名；金标不展示
- 相关句：
  - Mason’s tiny but rapid contribution mattered, but Miles was the hand that moved the innings from nearly finished to genuinely defensible, carrying Ridgevale to 174 all out in the forty-fourth over.
  - Ridgevale advanced because they survived their weakest phase, made Sandmere chase more than they expected, and then used Miles Carter’s spell to make 174 feel less like a modest total and more like a trap that closed every time Sandmere tried to step through it.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S13 match_0003 inn1.bowl2_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.bowl2_wickets；指定局别按字段名；金标不展示
- 相关句：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
  - He bowled Felix, then removed Gareth Bishop almost at once, and that double hit at 137 froze what could have become a 175-type finish.
  - His 81 from 56 had both rescue and acceleration inside it, built from the early wobble, stretched through the middle, and then pushed hard when Brookmere needed the late lift.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S14 match_0008 inn1.total_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.total_runs；指定局别按字段名；金标不展示
- 相关句：
  - Coral Coast finished on 262 for eight, a total that felt less like a straight batting display than a repaired and rebuilt innings, shaped first by Lucas Hart’s patience, then by Adrian Blake’s acceleration, then by a final cluster of smaller but useful pushes.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S15 match_0010 inn2.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S16 match_0012 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S17 match_0015 inn2.byes
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.byes；指定局别按字段名；金标不展示
- 相关句：
  - Adrian Clarke threw a few late shots, Mason Reid helped drag the total further, but by then the match had turned from chase into resistance, and when Mason was run out at 279, Ridge Falcons had completed a 65-run win and advanced.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S18 match_0017 inn1.bat2_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.bat2_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S19 match_0003 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S20 match_0008 inn1.bat3_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.bat3_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S21 match_0010 inn1.bowl2_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn1.bowl2_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S22 match_0012 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S23 match_0015 inn2.no_balls
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.no_balls；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S24 match_0017 inn2.wides
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn2.wides；指定局别按字段名；金标不展示
- 相关句：
  - The margin of 68 runs makes the match look clearer than it had felt when Ridgevale were nine down, but that is the point of the story: Sandmere won most of the first innings and still lost the match because Miles Carter changed both halves.
  - His unbeaten 48 gave Ridgevale a total with teeth; his five wickets turned a chase that should have been manageable into a procession of restarts.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S25 match_0003 inn2.bowl2_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn2.bowl2_wickets；指定局别按字段名；金标不展示
- 相关句：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
  - He bowled Felix, then removed Gareth Bishop almost at once, and that double hit at 137 froze what could have become a 175-type finish.
  - His 81 from 56 had both rescue and acceleration inside it, built from the early wobble, stretched through the middle, and then pushed hard when Brookmere needed the late lift.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S26 match_0008 inn1.bowl1_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.bowl1_wickets；指定局别按字段名；金标不展示
- 相关句：
  - Coral Coast finished on 262 for eight, a total that felt less like a straight batting display than a repaired and rebuilt innings, shaped first by Lucas Hart’s patience, then by Adrian Blake’s acceleration, then by a final cluster of smaller but useful pushes.
  - Chasing 263, Ridgeview needed a calm opening and one serious middle-order partnership.
  - They were under pressure at 27 for two, rebuilt through Lucas Hart and Nathan Wells, sharpened through Adrian Blake and Marcus Shaw, then defended through a layered attack: Mason Hale for the first incision, Luke Barrett for the middle collapse, Evan Reed for the main repair stand, and Ryan Frost for the closing pressure.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S27 match_0010 inn2.overs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.overs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S28 match_0012 inn2.bat3_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn2.bat3_name；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S29 match_0015 inn1.bowl1_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn1.bowl1_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S30 match_0017 inn1.bat2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.bat2_name；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S31 match_0003 inn1.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.team；指定局别按字段名；金标不展示
- 相关句：
  - Seabank Cricket Ground in Stonehaven had that sharp feel from the first over, not quite evening yet but already narrow enough in the light for every fielder in the ring to look a little closer than he really was, and Ridgehaven’s decision to field first felt less like a gamble than a test of whether Brookmere’s top order could survive pressure before the ball softened.
  - He did not go hunting for magic, he just kept forcing Aiden Cole and Brandon Hale to play from uncomfortable positions, a length neither fully forward nor comfortably back, and Brookmere’s opening stand never really became a launch even though the score moved with a few early extras.
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S32 match_0008 inn2.bat1_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn2.bat1_name；指定局别按字段名；金标不展示
- 相关句：
  - Aiden Cole gave Ridgeview their one proper argument.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S33 match_0010 inn2.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.team；指定局别按字段名；金标不展示
- 相关句：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediately into uncomfortable batting rather than the clean first-use rhythm they would have wanted.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S34 match_0012 inn1.bowl2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.bowl2_name；指定局别按字段名；金标不展示
- 相关句：
  - Liam Frost removed Adrian, Lucas Vale pinned Caleb after he had started to settle, and the score was pushed back into repair mode again.
  - Lucas Vale’s two wickets gave Westmere important middle control, Noah Grant cut into the scoring sequence, and Zane Foster’s wicketless spell still mattered because it gave Westmere ten overs of dry pressure that denied Dune Harbor an easy acceleration phase.
  - Connor then fell after doing his structural work, and Lucas Vale was bowled before the finish, so the scorecard retained enough late movement to avoid looking like a stroll.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S35 match_0015 inn2.bowl2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.bowl2_name；指定局别按字段名；金标不展示
- 相关句：
  - Caleb Rourke arrived and changed the middle overs.
  - Noah Grant kept finding the wickets that mattered around the lower middle, Daniel Cross removed Zane before his burst could grow, and Caleb Rourke returned with the ball to close down the last organized resistance, first taking Connor with his own hands and then removing Evan when the late counterpunch still carried a little danger.
  - Caleb Rourke’s player-of-the-match award fits because his seventy-four made the first innings heavy at the exact time it might have slowed, and his two wickets later removed the last serious structure from Coastal’s reply.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S36 match_0017 inn1.bowl2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.bowl2_name；指定局别按字段名；金标不展示
- 相关句：
  - Zach Foster’s spell was the visible cutting edge through the middle-late section, not always perfectly cheap, but constantly dangerous, while Ethan Parker kept hitting the card in ways that stopped any repair from becoming a platform.
  - He trapped Aiden, then Liam Reed, then Ryan Cole, and the innings folded for 106 in the twenty-ninth over, Ethan Parker stranded at the end with only a small late touch.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S37 match_0003 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
  - By the time Caleb Price bowled Drake at 87, the innings had not fully broken free, but it had stopped bleeding.
  - His 81 from 56 had both rescue and acceleration inside it, built from the early wobble, stretched through the middle, and then pushed hard when Brookmere needed the late lift.
  - Harvey Stone and Isaac Wells still squeezed enough from the last few balls to drag Brookmere to 164 for 8, but the innings had been contained just enough.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S38 match_0008 inn1.bat2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.bat2_name；指定局别按字段名；金标不展示
- 相关句：
  - Adrian Blake then arrived and shifted the tone.
  - Coral Coast finished on 262 for eight, a total that felt less like a straight batting display than a repaired and rebuilt innings, shaped first by Lucas Hart’s patience, then by Adrian Blake’s acceleration, then by a final cluster of smaller but useful pushes.
  - They were under pressure at 27 for two, rebuilt through Lucas Hart and Nathan Wells, sharpened through Adrian Blake and Marcus Shaw, then defended through a layered attack: Mason Hale for the first incision, Luke Barrett for the middle collapse, Evan Reed for the main repair stand, and Ryan Frost for the closing pressure.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S39 match_0010 inn1.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn1.team；指定局别按字段名；金标不展示
- 相关句：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediately into uncomfortable batting rather than the clean first-use rhythm they would have wanted.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S40 match_0012 inn2.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn2.team；指定局别按字段名；金标不展示
- 相关句：
  - At Eastbank Meadow Ground in Hillview, Westmere XI won the toss and chose to field, and the call had the feel of a side trusting the first hour rather than guessing at the day, because the surface looked playable from the rope but still carried enough early seam and uneven pace to make Dune Harbor XI work before they could score freely.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

---

# 附录 E：REPRODUCE

# REPRODUCE

## 抽样与只复算（0 次模型调用）

python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/sample.py
python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/score_short.py

## 短证据构建与补跑（18 次）

python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/build_short.py
python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/runner_short.py

## 输出

- short_samples.json、runs/short.jsonl
- short_scores.json
- sample.json、BLIND_REVIEW.md

本轮新增调用 18/18。