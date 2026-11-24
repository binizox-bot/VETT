from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT=ROOT/"VETT_INTEGRATED_20261113"
P=INT/"analysis"/"pilot_next"
C=INT/"analysis"/"pilot10_case_audit"

front = """# VETT 下一轮完整报告：跨局串值、局号标注与归属改判

日期：2026-11-13  
范围：Pilot-Next 主实验 + Lina Fox 归属题验证 + Pilot-10 审计 v2 的关键更正  
预算：本地 Ollama，实际 113/120 次请求，外部 API 0 次  
原始 Pilot-10、旧结果、预注册文件未修改。

## 0. 一页摘要

本轮回答两个问题：

1. **完整证据段换位后，模型会不会把另一局的数据填进目标局？标局号能减少多少？**
   - 在 8 场留出比赛、每条件 48 个可查字段上，跨局命中只有 0–3 个，且几乎全是 inn1.leg_byes 的 0/1 碰撞。
   - 局号标注：gemma B→D +12.5pp（3 个跨局命中全部消失）；qwen +6.25pp（2→1）；llama +2.1pp（1→0）。
   - qwen 有例外：原顺序加标签 +6.25pp，换序加标签反而 −2.1pp；标签不是单调增益。
   - 完整段落换序的破坏（A→B：−2.1 到 −12.5pp）明显小于旧句级 scrambled（−10.6 到 −12.8pp）；旧 match_0182 的整块搬运没有复现。

2. **给改判前的投手数据和一次具体改判，模型能不能自己更新两名投手并保留全队总数？**
   - 明示版（直接给 3/6、4/7）：gemma 完整正确；qwen/llama 只输出 3、4 个 wickets，不写 runs（figures 判错、wicket 数判对）。
   - 推导版（只给 4/6、3/7 + 改判通知）：**三个模型全部保留旧值 4/6、3/7**，没有一个完成“Nora −1、Ruby +1”的推导。
   - 全队 10 在所有题面、所有模型都正确。

**结论**：R28 在本轮找到的具体问题不是“模型普遍跨局抄数”，而是“模型不会把一次命名改判转成两名投手的双向更新”；旧“串值”现象对句级打乱敏感，对完整证据段移动不稳健。

## 1. 背景：Pilot-10 审计 v2 的四个关键更正

本轮设计直接建立在上一轮六对审计的更正上：

| 位置 | 更正 |
|---|---|
| A（match_0108） | inn2 命名 5 次出局（Nora 3、Ruby 2），全队 10 个 wicket，另有 5 个未命名；被转移的 wicket 属于未命名部分，无法定位具体出局。 |
| C（match_0167） | 删除句属于 inn1；“sundries 8”属于 inn2。inn1 仍可由 124−115=9 推出，gold UNKNOWN 错误。 |
| D（match_0091） | 删除句属于 inn1；“sundries 10”属于 inn2。total_extras 可由 136−122=14 推出；只有 wides/no_balls 真缺证。 |
| F（match_0203） | inn1.total_extras 实际是 16（不是 10）；fields/gold/pred 三层一致，v1 只是报告转录错误。 |
| 字段口径 | eval 实际按 32 字段计分（多含 4 个投手 .wides）；计划 28 字段。32 字段把 control 准确率压低约 7.7pp。 |
| revised_hard | prompt/scorer 只含 bowl1 figures，不含 bowl2/donor；0.529 不能解释为“不会双边归属”。 |

这些更正决定了本轮不再用“missing 100% 编造”和“hard 0.529”作为主结论，而是转向两个更干净的问题：**局绑定**与**改判推导**。

## 2. 主实验设计（Pilot-Next）

### 2.1 模型

| tag | digest | quant |
|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48… | Q4_K_M |
| llama3.1:8b | 46e0c10c039e… | Q4_K_M |
| gemma2:9b | ff02c3702f32… | Q4_0 |

解码：temperature=0，seed=20261112，num_ctx=8192，num_predict=300。gemma 为 Q4_0，与另两个不同源，写论文需注明。

### 2.2 留出比赛

8 场，均来自 220 场中 closure-clean、未参与 Pilot-10 / case audit、按 scorecard sha256 去重的比赛：

| match | tokens | result |
|---|---:|---|
| match_0201 | 982 | Ridgefield Won by 9 Wickets |
| match_0198 | 985 | Westhaven Won by 8 Wickets |
| match_0065 | 1801 | Northbridge Won by 31 Runs |
| match_0106 | 1802 | Meadowridge Spirits Women Won |
| match_0043 | 1792 | Eastshore Won by 170 Runs |
| match_0063 | 2462 | Brookfield Won by 54 Runs |
| match_0052 | 2418 | Crestbrook Won by 46 Runs |
| match_0064 | 2387 | Ridgefield Won by 229 Runs |

文本为 scorecard 的确定性重渲染（seed=0），不是发布 commentary；只用于本轮对照，不进入正式数据集。

### 2.3 字段

每场 3 对同名字段（两局值不同）：total_extras、wides、leg_byes，共 6 个目标字段。

### 2.4 四条件

| 条件 | 证据段顺序 | 局号标注 |
|---|---|---|
| A | 原顺序 | 无 |
| B | 证据段移到本局末尾 | 无 |
| C | 原顺序 | 证据段前加 First/Second innings |
| D | 同 B | 同 C |

证据段：inn1 的 “The total included ... extras”（若紧跟 “Another ... byes/leg-byes” 则一起移动）；inn2 的 “The sundries column read ...”。移动只在各自局内进行。

逐场不变量已检查：A/B、C/D 句子多重集相同；A/C、B/D 去掉标签后逐字相同；标签不含数字；四版金标相同；目标值都在对应局文本中。

## 3. 主实验结果

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

数值错例中的比例：qwen A 1/7、B 2/8、D 1/5；llama B 1/6；gemma B 3/6。  
全部命中都是 inn1.leg_byes，且多为 0/1 默认值；最强的一例是 match_0063：pred 4，gold 2，另一局 4。

### 3.3 换序后的转移

| 模型 | 比较 | C→W | W→C | 净变化 |
|---|---|---:|---:|---:|
| qwen | A→B | 2 | 1 | −2.1pp |
| qwen | C→D | 1 | 0 | −2.1pp |
| llama | A→B | 1 | 0 | −2.1pp |
| llama | C→D | 0 | 0 | 0 |
| gemma | A→B | 6 | 0 | −12.5pp |
| gemma | C→D | 0 | 0 | 0 |

### 3.4 局号效果

| 模型 | A→C | B→D | B→D 命中 |
|---|---|---:|---:|
| qwen | +6.25pp | +6.25pp | 2→1 |
| llama | 0 | +2.1pp | 1→0 |
| gemma | 0 | +12.5pp | 3→0 |

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

读法：明示更新能抄；推导更新三个模型全失败；全队总数始终正确。qwen 的 derivation evidence 甚至写 “Nora took 4 for 6”，引用了旧汇总。

## 5. 旧结果对照

- 旧句级 shuffled（Pilot-10，32 字段）：qwen .6906→.5625（−12.8pp）；llama .7375→.6312（−10.6pp）。
- 本轮完整段落换序（8 场，48 字段）：qwen .854→.833（−2.1pp）；llama .896→.875（−2.1pp）；gemma 1.0→.875（−12.5pp）。
- 旧 match_0182 的整块搬运（bat_sum 295、extras 17、wides 12、no_balls 1）在本轮没有复现；本轮命中全部是 leg_byes 的 0/1 碰撞。
- 同一输出重算 closure：qwen control .6906→.6687；llama .7375→.7438；qwen missing .5312→.4719。旧 closure 的“增益”来自独立调用，不能归功于 propagate。

## 6. 讨论

1. **旧“串值”需要收窄。** 句级 scrambled 下的强现象（match_0182 整块搬运）在完整证据段移动下消失；如果论文要主张“模型跨局抄数”，必须说明操纵强度，不能泛化为真实长文本行为。
2. **局号标注是有效的，但只对部分模型/位置有效。** gemma 的 6 个错误全部被标签修复；qwen 在原顺序下更受益；llama 基本平。标签不是万能修复。
3. **归属改判是更具体的失败。** 明示更新能抄，推导更新全失败；这比“状态维护失败”更容易验证，也更能指导方法（按事件账本、双向更新、全队守恒）。
4. **默认值控制很重要。** leg_byes 的 0/1 命中大多只是默认值碰撞；后续必须固定默认值或分层统计。

## 7. 限制

- 8 场、6 字段、3 个 7–9B 模型；探索性复验，不是领域结论。
- 文本为 scorecard 重渲染，不是发布 commentary；与真实叙述的分布可能有差异。
- gemma 为 Q4_0，量化不同源。
- 跨局命中分母小，0/1 碰撞多；需要更多独立比赛和默认值分层。
- 没有人工检查；没有 raw_output 之外的过程信息（本轮已保存 raw_output 与 prompt hash）。
- Lina 只有一场；qwen/llama 的裸整数是协议偏差，不是完整 figures。

## 8. 通俗回答

**跨局错值出现在哪些比赛和模型？**  
主要是 inn1.leg_byes：gemma 在 match_0065/0043/0063 的 B 条件各 1 个；qwen 在 match_0198（A/B/D）和 match_0063（B）各 1 个；llama 在 match_0198（B）1 个。没有 total_extras/wides 的跨局命中。

**标局号有没有帮助？**  
有，但不均匀。gemma 最明显：B 的 6 个错误在 C/D 全部恢复，3 个跨局命中全部消失；qwen 换序后 +6.25pp、命中 2→1；llama 只有 +1 个 cell。qwen 原顺序加标签比换序加标签更好，说明标签不能修复所有位置效应。

**下一轮最值得投入什么？**  
不要扩大句级 scrambling；用完整证据段在更多独立比赛上复验，并固定 leg_byes 的 0/1 默认值。把 Lina 的推导版作为主题型：三个模型都在“只给改判通知、不给新 figures”时保留旧值。下一步比较直接填表与“先按局、按事件记账再填表”，用同一模型、相同输入、接近预算。

## 9. 文件与复现

本轮产物：
- pilot_next/DESIGN.md、RESULTS.md
- pilot_next/samples.json、lina.json
- pilot_next/runs/main.jsonl、lina.jsonl、retest.jsonl、smoke.jsonl
- pilot_next/scores.json、lina_scores.json
- pilot_next/runner.py、score.py、score_lina.py

复现命令：

    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_samples.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_lina.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task main
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task lina
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task retest
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score_lina.py

---

# 附录 A：DESIGN.md 全文

"""

parts=[front]
for name in ["DESIGN.md","RESULTS.md"]:
    parts.append((P/name).read_text(encoding="utf-8"))
parts.append("

---

# 附录 B：Pilot-10 审计 CASES.md 全文

")
parts.append((C/"CASES.md").read_text(encoding="utf-8"))
parts.append("

---

# 附录 C：Lina Fox 作答核对 ANSWER_KEY.md 全文

")
parts.append((C/"attribution_case"/"ANSWER_KEY.md").read_text(encoding="utf-8"))
out=P/"COMPLETE_REPORT.md"
out.write_text("
".join(parts),encoding="utf-8")
print("wrote",out,"chars",len("
".join(parts)))
