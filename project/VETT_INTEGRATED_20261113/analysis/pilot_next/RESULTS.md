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

