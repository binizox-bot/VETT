# VETT 下一轮完整报告：跨局串值、局号标注与归属改判

日期：2026-11-13  
范围：Pilot-Next 主实验、Lina Fox 归属题验证、Pilot-10 审计 v2 的关键更正  
预算：本地 Ollama，实际 113/120 次请求，外部 API 0 次  
原始 Pilot-10、旧结果、预注册文件未修改。

## 0. 一页摘要

本轮回答两个问题。

**Q1：完整证据段换位后，模型会不会把另一局的数据填进目标局？标局号能减少多少？**

- 8 场留出比赛，每条件 48 个可查字段；跨局命中只有 0–3 个，且几乎全是 inn1.leg_byes 的 0/1 碰撞。
- 局号标注：gemma B→D +12.5pp（3 个跨局命中全部消失）；qwen +6.25pp（2→1）；llama +2.1pp（1→0）。
- qwen 例外：原顺序加标签 +6.25pp，换序加标签反而 −2.1pp；标签不是单调增益。
- 完整段落换序的破坏（A→B：−2.1 到 −12.5pp）明显小于旧句级 scrambled（−10.6 到 −12.8pp）；旧 match_0182 的整块搬运没有复现。

**Q2：给改判前的投手数据和一次具体改判，模型能不能自己更新两名投手并保留全队总数？**

- 明示版（直接给 3/6、4/7）：gemma 完整正确；qwen/llama 只输出 3、4 个 wickets，不写 runs（figures 判错、wicket 数判对）。
- 推导版（只给 4/6、3/7 + 改判通知）：三个模型全部保留旧值 4/6、3/7，没有一个完成“Nora −1、Ruby +1”的推导。
- 全队 10 在所有题面、所有模型都正确。

**结论**：R28 在本轮找到的具体问题不是“模型普遍跨局抄数”，而是“模型不会把一次命名改判转成两名投手的双向更新”；旧“串值”现象对句级打乱敏感，对完整证据段移动不稳健。

## 1. 背景：Pilot-10 审计 v2 的关键更正

| 位置 | 更正 |
|---|---|
| A（match_0108） | inn2 命名 5 次出局（Nora 3、Ruby 2），全队 10 个 wicket，另有 5 个未命名；被转移的 wicket 属于未命名部分，无法定位具体出局。 |
| C（match_0167） | 删除句属于 inn1；“sundries 8”属于 inn2。inn1 仍可由 124−115=9 推出，gold UNKNOWN 错误。 |
| D（match_0091） | 删除句属于 inn1；“sundries 10”属于 inn2。total_extras 可由 136−122=14 推出；只有 wides/no_balls 真缺证。 |
| F（match_0203） | inn1.total_extras 实际是 16（不是 10）；fields/gold/pred 三层一致，v1 只是报告转录错误。 |
| 字段口径 | eval 实际按 32 字段计分（多含 4 个投手 .wides）；计划 28 字段。32 字段把 control 准确率压低约 7.7pp。 |
| revised_hard | prompt/scorer 只含 bowl1 figures，不含 bowl2/donor；0.529 不能解释为“不会双边归属”。 |

## 2. 主实验设置

| 项 | 值 |
|---|---|
| 模型 | qwen2.5:7b-instruct-q4_K_M（Q4_K_M）、llama3.1:8b（Q4_K_M）、gemma2:9b（Q4_0） |
| 解码 | temperature=0，seed=20261112，num_ctx=8192，num_predict=300 |
| 留出比赛 | match_0201、0198、0065、0106、0043、0063、0052、0064 |
| 字段 | 每场 3 对（total_extras、wides、leg_byes），两局值不同，共 6 个目标字段 |
| 条件 | A 原序 / B 证据段移到本局末尾 / C 原序+局号 / D 换序+局号 |
| 来源 | scorecard 确定性重渲染（seed=0），未参与 Pilot-10 / case audit，按 scorecard sha256 去重 |

逐场不变量已检查：A/B、C/D 句子多重集相同；A/C、B/D 去掉标签后逐字相同；标签不含数字；四版金标相同。

## 3. 主结果

### 3.1 字段准确率（每条件 48 字段）

| 模型 | A | B | C | D |
|---|---:|---:|---:|---:|
| qwen2.5:7b | 41/48 = .854 | 40/48 = .833 | 44/48 = .917 | 43/48 = .896 |
| llama3.1:8b | 43/48 = .896 | 42/48 = .875 | 43/48 = .896 | 43/48 = .896 |
| gemma2:9b | 48/48 = 1.000 | 42/48 = .875 | 48/48 = 1.000 | 48/48 = 1.000 |

### 3.2 另一局同字段命中（分母 48）

| 模型 | A | B | C | D |
|---|---:|---:|---:|---:|
| qwen | 1 | 2 | 0 | 1 |
| llama | 0 | 1 | 0 | 0 |
| gemma | 0 | 3 | 0 | 0 |

全部命中都是 inn1.leg_byes，且多为 0/1 默认值；最强一例是 match_0063：pred 4，gold 2，另一局 4。

### 3.3 换序转移与局号效果

| 模型 | A→B 净变化 | C→D 净变化 | A→C | B→D | B→D 命中 |
|---|---:|---:|---:|---:|---:|
| qwen | −2.1pp | −2.1pp | +6.25pp | +6.25pp | 2→1 |
| llama | −2.1pp | 0 | 0 | +2.1pp | 1→0 |
| gemma | −12.5pp | 0 | 0 | +12.5pp | 3→0 |

## 4. Lina Fox 三题面

固定姓名，不用 bowl1/bowl2。

| 题面 | 模型 | Nora | Ruby | 全队 | figures 三值 | wickets 三值 |
|---|---|---|---:|---:|---|---|
| original | qwen | 4 | 3 | 10 | 否（缺 runs） | 是 |
| original | llama | 4 | 3 | 10 | 否（缺 runs） | 是 |
| original | gemma | 4/6 | 3/7 | 10 | 是 | 是 |
| explicit | qwen | 3 | 4 | 10 | 否（缺 runs） | 是 |
| explicit | llama | 3 | 4 | 10 | 否（缺 runs） | 是 |
| explicit | gemma | 3/6 | 4/7 | 10 | 是 | 是 |
| derivation | qwen | 4 | 3 | 10 | 否 | 否（旧值） |
| derivation | llama | 4 | 3 | 10 | 否 | 否（旧值） |
| derivation | gemma | 4/6 | 3/7 | 10 | 否 | 否（旧值） |

## 5. 旧结果对照

- 旧句级 shuffled（Pilot-10，32 字段）：qwen .6906→.5625（−12.8pp）；llama .7375→.6312（−10.6pp）。
- 本轮完整段落换序（8 场，48 字段）：qwen .854→.833（−2.1pp）；llama .896→.875（−2.1pp）；gemma 1.0→.875（−12.5pp）。
- 旧 match_0182 的整块搬运（bat_sum 295、extras 17、wides 12、no_balls 1）在本轮没有复现。
- 同一输出重算 closure：qwen control .6906→.6687；llama .7375→.7438；qwen missing .5312→.4719。旧 closure 的“增益”来自独立调用，不能归功于 propagate。

## 6. 讨论、限制、通俗回答

**支持现象**：gemma 在 B 条件丢了 6 个 cell（3 场各 2 个，都是 leg_byes），加局号后 C/D 都恢复 48/48，3 个跨局命中全部消失；qwen B→D +6.25pp，命中 2→1。

**例外**：qwen 的标签不单调（A→C +6.25，C→D −2.1）；llama 基本平；跨局串值整体很弱，旧强现象没有复现。

**限制**：8 场、6 字段、3 个 7–9B 模型；文本为 scorecard 重渲染；gemma 为 Q4_0；leg_byes 的 0/1 碰撞多；Lina 只有一场，qwen/llama 输出裸整数是协议偏差；没有人工检查。

**通俗回答**：

跨局错值主要出现在 inn1.leg_byes：gemma 在 match_0065/0043/0063 的 B 条件各 1 个；qwen 在 match_0198（A/B/D）和 match_0063（B）各 1 个；llama 在 match_0198（B）1 个。没有 total_extras/wides 的跨局命中。

标局号有帮助但不均匀：gemma 最明显（B 的 6 个错误在 C/D 全部恢复，3 个命中归零）；qwen 换序后 +6.25pp、命中 2→1；llama 只有 +1 个 cell。

下一轮不要扩大句级 scrambling；用完整证据段在更多独立比赛上复验，固定 leg_byes 的 0/1 默认值；把 Lina 推导版作为主题型，比较直接填表与“先按局、按事件记账再填表”。

## 7. 文件与复现

- pilot_next/DESIGN.md、RESULTS.md
- pilot_next/samples.json、lina.json
- pilot_next/runs/main.jsonl、lina.jsonl、retest.jsonl、smoke.jsonl
- pilot_next/scores.json、lina_scores.json
- pilot_next/runner.py、score.py、score_lina.py
- 盲审工具 pilot10_case_audit/REVIEW_BLIND.md 与两臂全文 attribution_case/FULL_TEXT.md 作为独立附件保留，不并入本报告正文

    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_samples.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_lina.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task main
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task lina
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task retest
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score_lina.py

---

# 附录 A：DESIGN.md 全文

# Pilot-Next 设计：跨局串值与局号标注

日期：2026-11-13。外部 API 预算 0；本地 Ollama 三模型；请求上限 120。

## 1. 问题

1. 同一批证据段完整换位后，模型会不会把另一局的同名字段值填进目标局？在证据旁写清局号能减少多少？
2. 给改判前投手数据 + 一次具体改判，模型能否同时更新两名投手并保持全队总数？

## 2. 模型

| tag | digest | quant |
|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e | Q4_K_M |
| llama3.1:8b | 46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e | Q4_K_M |
| gemma2:9b | ff02c3702f322b9e075e9568332d96c0a7028002f1a5a056e0a6784320a4db0b | Q4_0 |

上下文 8192；temperature=0；seed=20261112；num_predict=300。

## 3. 留出比赛与字段

来源：220 场中 closure-clean 且未参与 Pilot-10 / case audit 的比赛；按 scorecard sha256 去重；文本为 scorecard 的确定性重渲染（seed=0），不是发布 commentary。

| match | tokens | result | inn1/inn2 total_extras | wides | leg_byes |
|---|---:|---|---|---|---|
| match_0201 | 982 | Ridgefield Won by 9 Wickets | 14/9 | 12/7 | 2/1 |
| match_0198 | 985 | Westhaven Won by 8 Wickets | 15/5 | 10/4 | 1/0 |
| match_0065 | 1801 | Northbridge Won by 31 Runs | 20/24 | 15/21 | 2/1 |
| match_0106 | 1802 | Meadowridge Spirits Women Won By | 29/9 | 18/8 | 4/1 |
| match_0043 | 1792 | Eastshore Won by 170 Runs | 7/9 | 4/8 | 2/1 |
| match_0063 | 2462 | Brookfield Won by 54 Runs | 25/20 | 19/15 | 2/4 |
| match_0052 | 2418 | Crestbrook Won by 46 Runs | 24/19 | 21/16 | 2/3 |
| match_0064 | 2387 | Ridgefield Won by 229 Runs | 24/12 | 19/10 | 2/1 |

每场 3 对字段（6 个目标字段），两局值均不同。

## 4. 四条件

| 条件 | 顺序 | 局号 |
|---|---|---|
| A | 原顺序 | 无 |
| B | 证据段移到本局末尾 | 无 |
| C | 原顺序 | 证据段前加 First/Second innings |
| D | 同 B | 同 C |

证据段：inn1 的 "The total included ... extras"（若紧跟 "Another ... byes/leg-byes" 则一起移动）；inn2 的 "The sundries column read ..."。移动只在各自局内进行。

不变量已逐场检查：A/B、C/D 句子多重集相同；A/C、B/D 去掉标签后逐字相同；标签只含 "First innings: "/"Second innings: "，不含数字；四版金标相同。

## 5. Lina Fox 三题面

- original: gold {'inn2.Nora_Vale.figures': '4/6', 'inn2.Ruby_North.figures': '3/7', 'inn2.team_wickets': 10}
- explicit: gold {'inn2.Nora_Vale.figures': '3/6', 'inn2.Ruby_North.figures': '4/7', 'inn2.team_wickets': 10}
- derivation: gold {'inn2.Nora_Vale.figures': '3/6', 'inn2.Ruby_North.figures': '4/7', 'inn2.team_wickets': 10}

derivation 版 = 原 control 全文 + 一条改判通知（不给新 figures）；已检查全文没有 "3 for 6" / "4 for 7"，"4/7" 只出现在比分 44/7 中。

## 6. 提示与输出

system 要求只返回 JSON：{"fields": {<field_id>: <integer>}}，无法确定用 UNKNOWN；固定字段清单；同一提示用于所有模型与条件。Lina 额外请求 evidence 字符串。

## 7. 预算

smoke 2 + main 8×4×3=96 + Lina 3×3=9 + 重测 2 场×3 模型×A=6 = 113（≤120）。

## 8. 指标

- 字段准确率：逐场 + 比赛宏平均。
- 另一局同字段命中：预测错值 == 另一局同名字段金标；分母为全部 6 字段，另报在数值错例中的比例；0 等易撞值单独标注。
- 转移：A→B、C→D 的对→错/错→对/净变化；B→D 与 A→C 比较局号效果。
- 解析/覆盖：格式失败、漏字段、有效输出；重测作波动参照。

## 9. 文件

samples.json、lina.json、runs/*.jsonl、score 脚本、RESULTS.md。

---

# 附录 B：RESULTS.md 全文

# Pilot-Next 结果：完整证据段换序、局号标注、归属更正

日期：2026-11-13。所有数字来自 runs/*.jsonl 与 scores.json；本地 Ollama，外部 API 0 次，实际请求 113/120。

## 0. 结论摘要

1. **完整证据段换序的破坏远小于旧句级打乱。** A→B 的净准确率变化为 −2.1 到 −12.5pp；旧句级 shuffled 是 −10.6 到 −12.8pp（qwen/llama，按实际 32 字段），且旧样本出现大面积跨局复制。
2. **跨局串值在这批样本里很少。** 每个条件 48 个可查字段，命中另一局同名字段只有 0–3 个；几乎全部是 inn1.leg_byes 的 0/1 碰撞。
3. **局号标注有效但不均匀。** B→D：gemma +12.5pp（3 个错值全部消失）、qwen +6.25pp、llama +2.1pp；qwen 在 A→C（原顺序加标签）反而比 D 更高，说明标签不是单调增益。
4. **Lina Fox：明示更新能抄，推导更新不能。** 给出改判后的 3/6、4/7 时，qwen/llama 能给出 3、4 个 wickets（但不写 runs），gemma 给出完整 figures；只给改判通知、不给新 figures 时，**三个模型都保留旧值 4/6、3/7**。
5. **重测零波动。** 2 场 × 3 模型 × A 条件共 6 次重测，6/6 逐字段完全一致。

## 1. 配置与预算

| 项 | 值 |
|---|---|
| 模型 | qwen2.5:7b-instruct-q4_K_M（Q4_K_M）、llama3.1:8b（Q4_K_M）、gemma2:9b（Q4_0） |
| 解码 | temperature=0，seed=20261112，num_ctx=8192，num_predict=300 |
| 主实验 | 8 场 × 4 条件 × 3 模型 = 96 |
| Lina | 3 题面 × 3 模型 = 9 |
| smoke | 2 |
| 重测 | 2 场 × 3 模型 = 6 |
| 合计 | 113 / 120 |

留出比赛：match_0201、0198、0065、0106、0043、0063、0052、0064。  
来源：220 场中 closure-clean、未参与 Pilot-10 / case audit、按 scorecard sha256 去重；文本为 scorecard 确定性重渲染（seed=0），不是发布 commentary。  
字段：每场 3 对（total_extras、wides、leg_byes），两局值不同，共 6 个目标字段。

## 2. 四条件主结果

### 2.1 字段准确率（每条件 48 字段）

| 模型 | A 原序 | B 换序 | C 原序+局号 | D 换序+局号 |
|---|---:|---:|---:|---:|
| qwen2.5:7b | 41/48 = 0.854 | 40/48 = 0.833 | 44/48 = 0.917 | 43/48 = 0.896 |
| llama3.1:8b | 43/48 = 0.896 | 42/48 = 0.875 | 43/48 = 0.896 | 43/48 = 0.896 |
| gemma2:9b | 48/48 = 1.000 | 42/48 = 0.875 | 48/48 = 1.000 | 48/48 = 1.000 |

逐场：

| match | qwen A/B/C/D | llama A/B/C/D | gemma A/B/C/D |
|---|---|---|---|
| match_0201 | .833/.833/.833/.833 | .833/.833/.833/.833 | 1/1/1/1 |
| match_0198 | .833/.833/1/1 | 1/.833/1/1 | 1/1/1/1 |
| match_0065 | .833/1/1/1 | 1/1/1/1 | 1/.667/1/1 |
| match_0106 | .833/.833/.833/.833 | .833/.833/.833/.833 | 1/1/1/1 |
| match_0043 | .833/.833/1/.833 | .833/.833/.833/.833 | 1/.667/1/1 |
| match_0063 | .833/.5/.833/.833 | .833/.833/.833/.833 | 1/.667/1/1 |
| match_0052 | .833/.833/.833/.833 | .833/.833/.833/.833 | 1/1/1/1 |
| match_0064 | 1/1/1/1 | 1/1/1/1 | 1/1/1/1 |

### 2.2 另一局同字段命中（分母 48）

| 模型 | A | B | C | D |
|---|---:|---:|---:|---:|
| qwen | 1 (0.021) | 2 (0.042) | 0 | 1 (0.021) |
| llama | 0 | 1 (0.021) | 0 | 0 |
| gemma | 0 | 3 (0.063) | 0 | 0 |

在数值错例中的比例：

| 模型 | A | B | C | D |
|---|---:|---:|---:|---:|
| qwen | 1/7 = .143 | 2/8 = .250 | 0 | 1/5 = .200 |
| llama | 0 | 1/6 = .167 | 0 | 0 |
| gemma | 0 | 3/6 = .500 | 0 | 0 |

全部命中都是 inn1.leg_byes，且值多为 0/1：

- gemma B：match_0065 pred 1（gold 2，另一局 1）；match_0043 pred 1（gold 2，另一局 1）；match_0063 pred 4（gold 2，另一局 4）。
- qwen B：match_0198 pred 0（gold 1，另一局 0）；match_0063 pred 4（gold 2，另一局 4）。
- qwen A/D：match_0198 pred 0；match_0043 pred 1。
- llama B：match_0198 pred 0。

注意：0 和 1 是高频默认值，这些“命中”不能单独证明跨局复制；match_0063 的 4（gold 2，另一局 4）是最强的一例。

### 2.3 换序后的正确性转移

| 模型 | 比较 | C→W | W→C | C→C | W→W | 净变化 |
|---|---|---:|---:|---:|---:|---:|
| qwen | A→B | 2 | 1 | 39 | 6 | −2.1pp |
| qwen | C→D | 1 | 0 | 43 | 4 | −2.1pp |
| llama | A→B | 1 | 0 | 42 | 5 | −2.1pp |
| llama | C→D | 0 | 0 | 43 | 5 | 0 |
| gemma | A→B | 6 | 0 | 42 | 0 | −12.5pp |
| gemma | C→D | 0 | 0 | 48 | 0 | 0 |

### 2.4 局号标注的效果

| 模型 | A→C（原序加标签） | B→D（换序加标签） | B→D 跨局命中变化 |
|---|---|---|---|
| qwen | +6.25pp | +6.25pp | 2 → 1 |
| llama | 0 | +2.1pp | 1 → 0 |
| gemma | 0 | +12.5pp | 3 → 0 |

## 3. Lina Fox 三题面

固定姓名，不使用 bowl1/bowl2。fields 要求 figures；qwen/llama 实际只输出 wickets（整数），gemma 输出 "W for R"。

| 题面 | 模型 | Nora | Ruby | 全队 | figures 三值同时正确 | wickets 三值同时正确 |
|---|---|---|---:|---:|---|---|
| original | qwen | 4 | 3 | 10 | 否（缺 runs） | 是 |
| original | llama | 4 | 3 | 10 | 否（缺 runs） | 是 |
| original | gemma | 4/6 | 3/7 | 10 | 是 | 是 |
| explicit | qwen | 3 | 4 | 10 | 否（缺 runs） | 是 |
| explicit | llama | 3 | 4 | 10 | 否（缺 runs） | 是 |
| explicit | gemma | 3/6 | 4/7 | 10 | 是 | 是 |
| derivation | qwen | 4 | 3 | 10 | 否 | 否（旧值） |
| derivation | llama | 4 | 3 | 10 | 否 | 否（旧值） |
| derivation | gemma | 4/6 | 3/7 | 10 | 否 | 否（旧值） |

读法：

- **明示版**：qwen/llama 的 wicket 数正确（3、4），但没有输出 runs；gemma 完整正确。
- **推导版**：三个模型都保留旧值 4/6、3/7，没有把 Lina Fox 的出局从 Nora 转给 Ruby。qwen 的 evidence 甚至写“Nora took 4 for 6”，说明它引用了旧汇总，未采纳改判通知。
- 全队 10 在所有题面、所有模型都正确。

## 4. 解析、覆盖、重测

| 项目 | 结果 |
|---|---|
| 主实验 | 96/96 parse_ok，0 漏字段 |
| Lina | 9/9 parse_ok，0 漏字段 |
| 重测 | 6/6 逐字段与 A 完全一致（2 场 × 3 模型） |
| 截断 | 无（eval_count 50–140，num_predict 300 足够） |

Lina 的 qwen/llama 输出裸整数是**协议偏差**（只给 wickets，不给 runs），不是 parse 失败；已单列。

## 5. 支持现象与例外

**支持现象（局号有效）**：gemma 在 B 条件丢了 6 个 cell（3 场各 2 个，都是 leg_byes），加上局号后 C/D 都恢复到 48/48；3 个跨局命中全部消失。qwen 的 B→D 也 +6.25pp，命中 2→1。

**例外 1（qwen 的标签不单调）**：qwen 在 A→C（原顺序加标签）是 41→44（+6.25pp），但在 C→D（换序加标签）是 44→43（−2.1pp）。也就是说，局号在原顺序下帮助更大，换序后反而引入 1 个新错。

**例外 2（llama 基本平）**：llama 的 A/B/C/D 都在 42–43/48，B→D 只 +1 个 cell；局号标注对它的作用很弱。

**例外 3（跨局串值很弱）**：与旧句级 shuffled 中 match_0182 整块搬运（bat_sum 295、extras 17、wides 12、no_balls 1）不同，本次完整证据段换序只出现 0–3 个命中，且多为 0/1 默认值。**旧现象对句级 scrambling 敏感，对完整段落移动不敏感。**

## 6. 通俗回答

**跨局错值出现在哪些比赛和模型？**  
主要出现在 inn1.leg_byes：gemma 在 match_0065/0043/0063 的 B 条件各有 1 个；qwen 在 match_0198（A/B/D）和 match_0063（B）各 1 个；llama 在 match_0198（B）1 个。没有出现 total_extras/wides 的跨局命中。

**标局号有没有帮助？**  
有，但不均匀。gemma 最明显：B 的 6 个错误在 C/D 全部恢复，3 个跨局命中全部消失；qwen 在换序后 +6.25pp、命中 2→1；llama 只有 +1 个 cell。qwen 在“原顺序加标签”比“换序加标签”更好，说明标签不能修复所有位置效应。

**下一轮最值得投入什么？**  
先不要扩大句级 scrambling；应该用**完整证据段**在更多独立比赛上复验，并固定 leg_byes 的 0/1 默认值控制。若跨局串值仍只有个位数，就把旧“串值”主张收窄为“句级打乱下的现象”；同时把 Lina 的推导版作为主题型——因为三个模型都在“只给改判通知、不给新 figures”时保留旧值，这是比泛泛的状态维护更具体、更可复现的失败。

## 7. 文件

- DESIGN.md：设计、样本清单、四条件差异、指标
- samples.json / lina.json：文本、字段、金标
- runs/main.jsonl、runs/lina.jsonl、runs/retest.jsonl：原始输出
- scores.json、lina_scores.json：逐字段评分
- runner.py、score.py、score_lina.py：可复算脚本

## 8. 复现命令

    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_samples.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_lina.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task main
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task lina
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task retest
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score_lina.py


---

# 附录 C：Pilot-10 审计 CASES.md 全文

# Pilot-10 样本审计 v2（已更正）

日期：2026-11-13  
范围：只使用已有 Pilot-10 数据与输出；模型调用 0 次。  
新增产物目录：VETT_INTEGRATED_20261113/analysis/pilot10_case_audit/  
原始数据、旧报告、预注册文件未修改。

## 0. 更正日志：哪一层写错了

| 位置 | v1 说法 | 实际 | 出错层 |
|---|---|---|---|
| A 逐次出局 | “命名出局只有 5 次，与汇总不闭合” | inn1 命名 1 次；inn2 命名 5 次（Nora 3、Ruby 2），inn2 共 10 个 wicket，另有 5 个未命名。被转移的 wicket 属于未命名部分，所以无法定位到具体出局。 | 报告层（我漏了按局拆分与“未命名”说明） |
| C 缺证 | “剩余 sundries 说 8，与 gold 9 矛盾” | “sundries 8”是 **inn2** 的句子；C 的目标是 **inn1.total_extras**。inn1 剩余文本为 124 总分、115 击球和，仍可推出 9，但没有 inn1 的矛盾句。 | 报告层（把 inn2 句子当成 inn1） |
| D 缺证 | “剩余 sundries 说 10，与 gold 14 矛盾” | “sundries 10”是 **inn2** 的句子；D 的目标是 inn1 的 extras/wides/no_balls。inn1 剩余 136 总分、122 击球和，total_extras 可推出 14；wides/no_balls 才真正缺证。 | 报告层（同上） |
| F 10 vs 16 | “inn1.total_extras = 10” | fields.jsonl、gold.json、两模型两臂的输出全部是 **16**；只有 v1 报告写成 10。 | 报告层（转录错误），数据/金标/评分一致 |
| 32 vs 28 | 报告称“28 core 字段” | eval 实际按 32 字段计分：E.is_core 把任何以 wides 结尾的字段都算进来，多出 4 个投手 .wides。 | 评测层（is_core 判定） |
| revised_hard 双边 | 0.529 被当作“模型不会双边归属” | prompt 与 32 字段 scorer 只含 bowl1 figures，不含 bowl2/donor。 | 评测层（schema 缺口） |

## 1. 对齐与口径

- 六对样本按 (match, variant, system, model) 对齐；文本路径与 JSONL 行号逐对核对。
- direct 与 closure 是两次独立调用；closure 不是从 direct 输出后处理而来（这是旧实验的混杂，见第 10 节）。
- 所有文本是 scorecard 的确定性重渲染（seed=0），不是发布目录的原始 commentary。
- eval 行只保存 pred，未保存 raw_output；本文引用的是解析后的字段。
- closure 的 propagate() 只重写 inn{1,2}.total_extras、total_runs、bowling_runs_charged；重写前的 pred 未保存。

## 2. 总表

| 对 | 比赛 | 变体 | 关键字段 | qwen direct | llama direct | 处置 |
|---|---|---|---|---|---|---|
| A | match_0108 | control vs revised_hard | 两投手 figures；全队 wickets | 1/1 被提示的投手正确；第二名未提示 | 0/1（W/R 占位符）；第二名未提示 | 需修评测 + 需修样本 |
| B | match_0035 | control vs revised_hard | 首席投手 figures；全队 wickets | 1/1 正确；全队正确 | 1/1 正确；全队正确 | 证据待核（只验证汇总） |
| C | match_0167 | control vs missing | inn1.total_extras | 0 | 8 | 需修样本（gold 应为 9） |
| D | match_0091 | control vs missing | inn1.total_extras / wides / no_balls | 0/0/0 | 10/0/8 | 需修样本（total_extras 应为 14） |
| E | match_0092 | control vs shuffled | 9 个 C→W 字段 | 9 个 C→W；1 个是 figures 格式 | 3 个 C→W | 可保留（换序）+ 需修评测 |
| F | match_0203 | control vs shuffled | 4 个稳定字段 | 6 个 C→W | 0 个 C→W，24 个稳定正确 | 可保留（模型差异） |

---

## 3. Pair A：match_0108，归属更正（control vs revised_hard）

### A1. 模型看到了什么

- control 第 45 句（char 3336）："Bayview Royals Women's bowling effort was led by Nora Vale, whose 4 for 6 made the deepest incisions."
- control 第 46 句（char 3389）："Ruby North kept the pressure on with 3 for 7..."
- revised_hard 第 45 句：Nora 改为 "5 for 6"；第 46 句：Ruby 改为 "2 for 7"。
- 按局拆分：
  - inn1 只命名 1 次出局（Clara Moss → Farah Noor），与本对无关。
  - inn2 命名 5 次出局：Lina Fox → Nora（第 18 句）、Mira Khan → Ruby（第 22 句）、Zara Field → Ruby（第 26 句）、Hana Qureshi → Nora（第 30 句）、Sarah Pike → Nora（第 34 句）。
  - inn2.total_wickets = 10，因此另有 5 个 wicket 没有在叙述中命名。

路径：.../match_0108/variants/control/commentary.txt；.../revised_hard/commentary.txt。

### A2. 正确答案

| 字段 | control | revised_hard | 依据 |
|---|---:|---:|---|
| inn2.bowl1_Nora Vale.figures | 4/6 | 5/6 | Nora +1 |
| inn2.bowl2_Ruby North.figures | 3/7 | 2/7 | Ruby -1 |
| inn2.total_wickets | 10 | 10 | 全队不变 |

- 两名投手的汇总在文本中都出现（第 45、46 句）。
- 但“哪一次出局”无法确定：被转移的 wicket 属于 inn2 中未命名的 5 个；文本没有把它绑定到任何具体出局。
- 修订后 Nora 的命名出局仍是 3 次（Lina、Hana、Sarah），汇总 5；Ruby 命名 2 次（Mira、Zara），汇总 2。总命名 5 次，inn2 共 10 个 wicket，另有 5 个未命名；被转移的 wicket 属于未命名部分，因此无法从命名出局反推。

### A3. 模型实际答了什么

| 记录 | 字段 | 值 | 解析 | 评分 |
|---|---|---:|---|---|
| qwen direct，第 225 行 | bowl1 Nora | "5/6" | 正常 | 正确 |
| 同上 | bowl2 Ruby | 键不存在 | 正常 | 未评分（不在 32 字段） |
| qwen closure，第 226 行 | 同上 | "5/6" / 键不存在 | 正常 | 同上 |
| llama direct，第 225 行 | bowl1 Nora | "W/R" | 正常 | 错误（占位符） |
| 同上 | bowl2 Ruby | 键不存在 | 正常 | 未评分 |
| llama closure，第 226 行 | 同上 | "W/R" / 键不存在 | 正常 | 同上 |

对照 control：qwen 4/6（正确），llama 仍是 "W/R"（错误）。  
所以 llama 的占位符是修订前就存在的格式失败；qwen 正确跟踪了 Nora 的 4→5。

### A4. 能否用于下一轮

**需修评测 + 需修样本。**

- 已核实：bowl2 不在 prompt/scorer；“另一名投手”从未被问。
- 已核实：文本没有把被转移的 wicket 绑定到具体出局。
- 未核实：模型若被问到 bowl2 是否能答对；本轮未调用。

---

## 4. Pair B：match_0035，归属更正（control vs revised_hard）

### B1. 模型看到了什么

- control 第 32 句（char 2465）："Harborfield's bowling effort was led by Isaac Shaw, whose 3 for 35..."
- revised_hard 第 32 句：改为 "whose 4 for 35"。
- 第 24 句：Caleb Price → Isaac Shaw；第 33 句：Liam Foster 2/24 未变。
- 转移日志：Isaac 3→4，Luke Barrett 2→1；Luke 的名字在文本出现，但他的 figures 从未出现。
- inn1.total_wickets = 10，未变。

### B2. 正确答案

| 字段 | control | revised_hard | 依据 |
|---|---:|---:|---|
| inn1.bowl1_Isaac Shaw.figures | 3/35 | 4/35 | Isaac +1 |
| inn1.total_wickets | 10 | 10 | 全队不变 |

- 文本只写首席投手的汇总 +1，没有写 Luke 的 2→1，也没有命名被转移的出局。
- 因此只能验证“首席投手汇总更新 + 全队不变”，不能验证双边归属。

### B3. 模型实际答了什么

| 记录 | 字段 | 值 | 评分 |
|---|---|---:|---|
| qwen direct，第 217 行 | Isaac | "4/35" | 正确 |
| qwen closure，第 218 行 | Isaac | "4/35" | 正确；未重算 |
| llama direct，第 217 行 | Isaac | "4/35" | 正确 |
| llama closure，第 218 行 | Isaac | "4/35" | 正确 |
| 两模型 | inn1.total_wickets | 10 | 正确 |

对照 control：两模型都输出 3/35，说明确实读到了修订后的 4/35。

### B4. 能否用于下一轮

**证据待核。** 可作“汇总更新答对”的对照，但不能回答双边归属；donor 既不在文本也不在 schema。

---

## 5. Pair C：match_0167，缺证（control vs missing）

### C1. 模型看到了什么

- 被删句：control 第 23 句（char 1595）："The total included 9 extras, with 7 wides and 0 no-balls..."
- 剩余 inn1 证据：
  - "The batters themselves accounted for 115."
  - "The innings closed at 124 from 20.0 overs.."
  - "All told, the innings reached 124.."
- 注意：第 58 句 "The sundries column read 8..." 属于 **inn2**，不是本对的目标局。

### C2. 正确答案

gold：control inn1.total_extras = 9；missing 标为 UNKNOWN。

- inn1 仍可用 124 − 115 = 9 推出；删除的只是显式句。
- 因此该字段不是“无法唯一确定”；gold=UNKNOWN 与剩余证据冲突。
- inn2 的 sundries 8 与 inn1 无关，v1 把它当成矛盾是错的。

### C3. 模型实际答了什么

| 记录 | 值 | 字段存在 | 解析 | 评分 |
|---|---:|---|---|---|
| qwen direct，第 21 行 | 0 | 是 | 正常 | 错误 |
| qwen closure，第 22 行 | 0 | 是 | 正常 | 错误；未改 |
| llama direct，第 21 行 | 8 | 是 | 正常 | 错误 |
| llama closure，第 22 行 | 8 | 是 | 正常 | 错误；未改 |

无 UNKNOWN、无漏字段、无解析失败。

### C4. 能否用于下一轮

**需修样本。** 已核实：124−115=9；gold=UNKNOWN 错误。  
处理：把 gold 改为 9；若要制造真缺证，必须同时删除总分或击球和。

---

## 6. Pair D：match_0091，缺证（control vs missing）

### D1. 模型看到了什么

- 被删句：control 第 22 句（char 1608）："The total included 14 extras, with 11 wides and 1 no-ball..."
- 剩余 inn1：136 总分、122 击球和；"Another 0 byes and 2 leg-byes..."。
- 第 49 句 "The sundries column read 10..." 属于 **inn2**，与本对无关。

### D2. 正确答案

gold：inn1 total_extras=14、wides=11、no_balls=1；missing 三项都标 UNKNOWN。

- total_extras = 136 − 122 = 14，可唯一确定；gold 错标 UNKNOWN。
- wides / no_balls 没有独立剩余来源，确实不可唯一确定。
- 所以正确拆法是：total_extras=14；wides/no_balls=UNKNOWN。

### D3. 模型实际答了什么

| 记录 | total_extras | wides | no_balls | 解析 |
|---|---:|---:|---:|---|
| qwen direct，第 117 行 | 0 | 0 | 0 | 正常 |
| qwen closure，第 118 行 | 0 | 0 | 0 | 正常；未改 |
| llama direct，第 117 行 | 10 | 8 | 0 | 正常 |
| llama closure，第 118 行 | 10 | 8 | 0 | 正常；未改 |

### D4. 能否用于下一轮

**需修样本（部分）。** total_extras 可答为 14；wides/no_balls 可保留为 UNKNOWN。  
处理：拆分金标，不要把三项一起标 UNKNOWN。

---

## 7. Pair E：match_0092，换序（control vs shuffled）

### E1. 模型看到了什么

同局内重排，事实不变，时间线被打乱：
- "When Jonah Walker fell to Robert Mills for 3..." 被移到 shuffled 第 2 句（char 112），出现在 2/2、3/3 之前。
- "With George King scoring 9 and Brendan Young contributing 19..." 被移到第 15 句（char 1194）；control 第 9 句。
- "When Samuel Wright fell to Marcus Hale for 0..." control 第 4 句，shuffled 中后移。

### E2. 正确答案

gold 不变：inn1.leg_byes=2、inn1.batting_runs_sum=65、inn1.bowl1_Marcus Hale.figures="3/18"、inn2.total_extras=17、inn2.byes=1、inn2.leg_byes=4、inn2.wides=12、inn2.bowling_runs_charged=77。

### E3. 模型实际答了什么

qwen direct，第 75 行（closure 第 76 行）：

| 字段 | control | shuffled | gold | 评分 | 是否等于另一局同名字段 |
|---|---:|---:|---:|---|---|
| inn1.leg_byes | 2 | 4 | 2 | 错 | 是：inn2.leg_byes gold=4、control pred=4 |
| inn1.batting_runs_sum | 65 | 81 | 65 | 错 | 否 |
| inn1.bowl1_Marcus Hale.figures | "3/18" | "3 for 18" | "3/18" | 格式误判 | — |
| inn2.total_extras | 17 | 0 | 17 | 错 | 否 |
| inn2.byes | 1 | 0 | 1 | 错 | 否 |
| inn2.leg_byes | 4 | 0 | 4 | 错 | 否 |
| inn2.wides | 12 | 0 | 12 | 错 | 否 |
| inn2.bowling_runs_charged | 77 | 82 | 77 | 错 | 否 |

第 9 个 C→W 是 inn2.bowl1_Kieran Hall.figures（未展开）。  
closure 第 76 行的 figures 变成 "3/18" 是独立调用的输出，不是 propagate。

### E4. 能否用于下一轮

**可保留（换序不稳定）+ 需修评测。**

- 已核实：9 个 C→W 中 1 个是 figures 格式问题；其余包含 inn1.leg_byes 的跨局串值（4 = inn2 的 4）与 inn2 extras 的整体塌陷。
- 需修 value_match 的 figures 归一化，然后重算（见第 9 节）。

---

## 8. Pair F：match_0203，换序（control vs shuffled）

### F1. 模型看到了什么

- "The lower order flickered briefly..." 被移到 shuffled 第 2 句（char 111）。
- "When Ethan Wells fell to Ethan Shaw for 27..." 被移动。
- "Through the middle phase, Connor Hart held firm..." 被移动。

### F2. 正确答案

gold 不变：
- match.result = "Ridgeline Won by 5 Wickets"
- inn1.total_runs = 174
- inn1.total_wickets = 10
- inn1.total_extras = 16（不是 10）
- inn2.total_extras = 20

10 vs 16 的追查：fields.jsonl=16，gold.json=16，qwen/llama 两臂 pred 都是 16；只有 v1 报告写成 10。数据、金标、评分三层一致，错在报告层。

### F3. 模型实际答了什么

- llama direct，第 27 行：0 个 C→W、0 个 W→C、24 个字段两臂都正确；上述 4 个字段两臂均正确。
- qwen direct，第 27 行：6 个 C→W：inn1.max_partnership、inn2.total_extras、inn2.leg_byes、inn2.no_balls、inn2.wides、inn2.bowling_runs_charged；上述 4 个字段仍正确。

### F4. 能否用于下一轮

**可保留。** 同一换序操纵下 llama 完全稳定、qwen 6 个字段变错；是模型差异的干净对照。  
但不能用 v1 的 10 作为 gold；正确值是 16。

---

## 9. 换序复算（用已有输出，0 次调用）

### 9.1 figures 归一化

把 "3 for 18"、"3/18"、"3-18" 都归一为 (3,18) 比较。旧评分只接受 "W/R" 或 "W-R"。

### 9.2 28 字段 vs 32 字段

- 计划中的 28 字段：4 个比赛级 + 每局 10 个基础字段 + 每局 bat1 runs + 每局 bowl1 figures。
- 实际 32 字段：E.is_core 把任何以 wides 结尾的字段都算进来，额外包含 4 个投手 .wides（每局 2 个）。
- 结果（10 场 macro 平均）：

| 字段集 | 模型 | control（旧） | shuffled（旧） | control（新） | shuffled（新） |
|---|---|---:|---:|---:|---:|
| planned28 | qwen | 0.7678 | 0.6250 | 0.7678 | 0.6321 |
| actual32 | qwen | 0.6906 | 0.5625 | 0.6906 | 0.5688 |
| planned28 | llama | 0.8107 | 0.6928 | 0.8107 | 0.6928 |
| actual32 | llama | 0.7375 | 0.6312 | 0.7375 | 0.6312 |

读法：
- 32 字段把 control 准确率压低约 7.7pp（qwen 0.691 vs 0.768；llama 0.738 vs 0.811），因为多出的投手 wides 很难。
- figures 归一化只影响 qwen（+0.6pp shuffled），llama 没有 figures 错误。
- 旧结果保留在 analysis/pilot10_metrics.json，未覆盖。

### 9.3 换序错例的跨局串值检查

对每个 C→W 字段，比较 shuffled 的错误值是否等于“另一局同名字段”的 gold 或 control pred。只列有意义的（两局 gold 不同）：

| 模型 | 比赛 | 字段 | control | shuffled | gold | 另一局同名字段 | 另一局 gold | 另一局 control pred |
|---|---|---|---:|---:|---:|---|---:|---:|
| qwen | match_0092 | inn1.leg_byes | 2 | 4 | 2 | inn2.leg_byes | 4 | 4 |
| qwen | match_0108 | inn1.wides | 12 | 7 | 12 | inn2.wides | 7 | 7 |
| qwen | match_0007 | inn1.leg_byes | 3 | 2 | 3 | inn2.leg_byes | 2 | 0 |
| qwen | match_0090 | inn1.byes | 1 | 0 | 1 | inn2.byes | 0 | 0 |
| qwen | match_0007 | inn1.total_wickets | 8 | 10 | 8 | inn2.total_wickets | 10 | 10 |
| llama | match_0182 | inn2.batting_runs_sum | 154 | 295 | 154 | inn1.batting_runs_sum | 295 | 295 |
| llama | match_0182 | inn2.total_extras | 18 | 17 | 18 | inn1.total_extras | 17 | 17 |
| llama | match_0182 | inn2.wides | 9 | 12 | 9 | inn1.wides | 12 | 12 |
| llama | match_0182 | inn2.no_balls | 2 | 1 | 2 | inn1.no_balls | 1 | 1 |
| llama | match_0092 | inn1.leg_byes | 2 | 4 | 2 | inn2.leg_byes | 4 | 4 |
| llama | match_0108 | inn1.leg_byes | 2 | 0 | 2 | inn2.leg_byes | 0 | 0 |

结论：串值不是个例。llama 在 match_0182 把 inn1 的 bat_sum/extras/wides/no_balls 整块搬到 inn2；qwen 在 match_0092/0108 把另一局的 leg_byes/wides 搬过来。  
这支持“模型没有把证据绑定到正确的局”，比泛泛的“状态维护失败”更具体。

---

## 10. 归属更正：新样本 + 同一输出重算

### 10.1 新样本（可判输赢）

路径：analysis/pilot10_case_audit/attribution_case/  
基于 match_0108 control，显式改一次命名出局：

- 原文："The chase took a hit when Lina Fox fell to Nora Vale for 0."
- 新文："The chase took a hit when Lina Fox fell to Ruby North for 0."
- 同步汇总："Nora ... 4 for 6" → "3 for 6"；"Ruby ... 3 for 7" → "4 for 7"。
- 全队 inn2.total_wickets 保持 10。

gold：

| 字段 | control | attribution_named |
|---|---:|---:|
| inn2.bowl1_Nora Vale.figures | 4/6 | 3/6 |
| inn2.bowl2_Ruby North.figures | 3/7 | 4/7 |
| inn2.total_wickets | 10 | 10 |

评分三项同时检查（score_spec.json）：
1. Nora 比 control 少 exactly 1 个 wicket；
2. Ruby 比 control 多 exactly 1 个 wicket；
3. 全队 total_wickets 与 control 相同。

这样“哪次出局从 A 改给 B”在文本中可判定（Lina Fox），汇总与逐次描述一致。  
本轮未跑模型（预算 0）；下一轮可直接用它做 direct vs 记账的对照。

盲审回答已核对：3/3 正确（第二局 Lina Fox、Nora 3/6、Ruby 4/7、全队 10）；证据句与 char 位置见 attribution_case/ANSWER_KEY.md。注意样本用 batter + 比分定位，未写 over 号。

### 10.2 同一输出重算 closure

旧实验的 direct 与 closure 是两次独立调用，不能把差异归功于 propagate。  
对现有 direct 输出直接应用 propagate（0 次调用）后：

| 模型 | variant | direct | direct+propagate（同输出） | 旧 closure（独立调用） |
|---|---|---:|---:|---:|
| qwen | control | 0.6906 | 0.6687 | 0.6750 |
| qwen | shuffled | 0.5625 | 0.5156 | 0.5188 |
| qwen | revised | 0.6906 | 0.6937 | 0.6813 |
| qwen | missing | 0.5312 | 0.4719 | 0.4844 |
| llama | control | 0.7375 | 0.7438 | 0.7438 |
| llama | revised | 0.7500 | 0.7906 | 0.7750 |
| llama | missing | 0.6312 | 0.6062 | 0.5969 |

读法：
- 对同一份 direct 输出重算，qwen 的 control/shuffled/missing 反而下降（组件错，重算放大错误）；只有 revised 略升。
- llama 的 control/revised 有 +0.6~+4pp，missing 下降。
- 旧 closure 的数值与独立调用绑定，不能作为“propagate 的增益”。
- 下一轮必须用同一输出重算，再比较 direct vs closure。

---

## 附录 A：28 / 32 / 48 / 49 字段口径

- 49 = fields.jsonl 总数（5 个比赛级 + 每局 22 个）。
- 32 = eval 实际分母：E.is_core 把任何以 wides 结尾的字段算进来，额外含 4 个投手 .wides。
- 28 = 计划核心：4 比赛级 + 每局 12（10 基础 + bat1 runs + bowl1 figures）。
- 48 = 现有 schema/scorer 中不存在；只有“49 − match.result_type”才会得到 48，但没有任何代码路径使用它。本轮 6 对不受 48 影响。
- 影响：A 的 bowl2 不在 32/28；B 的 donor 不在 32/28；C/D/F 的目标字段都在 28 内；E 的 figures 受 value_match 影响。

## 附录 B：UNKNOWN 的接受情况

- Prompt：要求 UNKNOWN；JSON：无严格校验，接受；Scorer：value_match("UNKNOWN","UNKNOWN") 为真。
- 漏字段会被当空串判错，而不是 UNKNOWN。
- 本轮 missing 记录全部输出具体值，没有一条输出 UNKNOWN。

## 附录 C：对齐、缺口与未核实项

- 六对文本、JSONL 行号、变体名逐条核对；同一场比赛、同一变体。
- 未保存 raw_output：只能引用解析后的 pred。
- 未保存 closure 重算前的 pred：无法判断 propagate 覆盖了哪些字段。
- revised_hard 的 bowl2/donor 未进入 prompt/scorer；本轮无法回答“双边是否都改对”，除非重跑。
- 所有“模型为什么错”均区分已核实的输出事实与对原因的推测。

---

# 附录 D：Lina Fox 作答核对 ANSWER_KEY.md 全文

# 归属更正新样本：作答核对（ANSWER KEY）

你的三问回答与仓库中的 gold 完全一致：**3/3 正确**。

## 1. 改判的是哪次出局

- 正确：第二局（Sandbank Spirits Women 的追分 innings），Lina Fox 得 0 分时的出局；原记 Nora Vale，改判给 Ruby North。
- 证据句（attribution_named，char 1239）：
  "The chase took a hit when Lina Fox fell to Ruby North for 0."
- 对照句（control，char 1239）：
  "The chase took a hit when Lina Fox fell to Nora Vale for 0."

## 2. 两位投手的 wicket 数

| 字段 | control | attribution_named | 你的回答 |
|---|---:|---:|---|
| inn2.bowl1_Nora Vale.figures | 4/6 | 3/6 | 3 个 wickets（3/6）✓ |
| inn2.bowl2_Ruby North.figures | 3/7 | 4/7 | 4 个 wickets（4/7）✓ |

- 证据句（attribution_named，char 3337）："Nora Vale, whose 3 for 6 made the deepest incisions."
- 证据句（attribution_named，char 3390）："Ruby North kept the pressure on with 4 for 7..."

## 3. 全队 wicket 总数

- 正确：第二局仍是 10。
- 证据句（attribution_named，char 2888）：
  "Sandbank Spirits Women closed on 55 for 10 from 16.5 overs, the 164 runs margin reflecting a chase that had been tested but never broken.."
- 一减一加：Nora 4→3，Ruby 3→4，总和不变。

## 三项评分检查

| 检查 | 结果 |
|---|---|
| Nora 比 control 少 1 个 wicket | 通过（4→3） |
| Ruby 比 control 多 1 个 wicket | 通过（3→4） |
| 全队 total_wickets 与 control 相同 | 通过（10→10） |

## 你可能需要知道的两个细节

1. 你提到的 "55 for 10 from 16.5 overs" 确实在文本中（char 2888），不是只在 scorecard 里；所以全队总数是可从题面直接核对的。
2. 当前样本用 **batter + 比分（Lina Fox, 0/1）** 定位这次出局，没有写 over 号。若下一轮要求“明确标出局号/over 号”，需要在改判句里补 over（例如 "in the 4th over"），否则只能定位到“Lina Fox 这次出局”，不能定位到某一球。

## 附件缺口

你提到 attribution_named 的完整正文未随附件提供；仓库中该文件存在：
- attribution_case/control/commentary.txt
- attribution_case/attribution_named/commentary.txt

两份全文也已汇总到 attribution_case/FULL_TEXT.md，便于独立复核。