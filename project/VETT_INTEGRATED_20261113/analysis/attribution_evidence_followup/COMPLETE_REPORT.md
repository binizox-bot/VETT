# VETT 证据标注跟进：完整报告

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


---

# 附录 A：DESIGN.md 全文

# Attribution Evidence Followup 设计

日期：2026-11-13。本地 Ollama 三模型；预算 120；实际 120；外部 API 0。

## 1. 模型

| tag | digest | quant |
|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48… | Q4_K_M |
| llama3.1:8b | 46e0c10c039e… | Q4_K_M |
| gemma2:9b | ff02c3702f32… | Q4_0 |

temperature=0，seed=20261112，num_ctx=8192，num_predict=300。

## 2. 样本

开发集：上一轮 8 场（match_0003、0008、0010、0012、0015、0017、0026、0030），复用其全文推导版作为 A。
留出集：6 场未用于前几轮（match_0009、0013、0014、0016、0018、0027），由 scorecard 重渲染并构造改判。
文本来源：scorecard 重渲染（seed=0），属于基于比赛记录构造的改判，不是真实赛果更正。

## 3. 条件

| 条件 | 内容 |
|---|---|
| A | 全文：完整解说 + 旧汇总 + 改判通知 |
| B | A 逐字保留，只在五处相关原句前加 [EVIDENCE] |
| C | 从 B 原样摘出五个标记句，保持顺序、措辞、数字写法 |

五处证据：原出局记录、原投手旧汇总、新投手旧汇总、本局总出局依据、改判通知。

逐场检查（构建脚本）：B 去掉标记后与 A 逐字一致；C 保留五个标记；C 不含更新后的 figures；五处证据可定位。

**已发现的构建问题**：C 没有包含 A 中“the bowling figures above are the pre-revision record”的 Note 句，因此 C 缺少“旧汇总”的状态标签。C 的结果只能作为探索，不能作为“证据足够”的严格条件。

## 4. 字段与评分

五字段：原投手 wickets_credited、bowling_runs_conceded；新投手同两项；innings_wickets_lost。
主指标：两名投手 wickets 同时正确（two_wickets）。
辅助：本局总出局正确、三项同时正确、两项失分正确、五项同时正确。
错误分类：两人都旧值；只加新投手；只减原投手；方向反了；两人都改但值错；格式失败。

## 5. 运行

开发 8×3×3=72；留出 6×2×3=36；Lina 3×2=6；重测 2×3=6；合计 120。

## 6. 备注

C 的缺失 Note 是本轮题面缺陷；A/B 的比较不受影响。

---

# 附录 B：BASELINE_REANALYSIS.md 全文

# BASELINE_REANALYSIS：上一轮 8 场改判实验复算

日期：2026-11-13。只读复用 analysis/attribution_followup/ 的 samples、runs、scores；0 次新模型调用。

## 0. 口径

- 首要指标：原投手与新投手的最终 wickets 两项绝对值同时正确（two_wickets）。
- 辅助：本局总出局正确、三项同时正确、两名投手失分正确、五项同时正确。
- 旧结果的 0/24 指三项同时正确；“两名投手都沿用旧值”的干净计数是 11/24（A、B 都旧值且总出局也正确）。若只要求 A、B 旧值、不要求总数，则为 18/24；其中 7 场总数也错。

## 1. 总体复算

| 模型 | 版本 | two_wickets | total | three | runs | five |
|---|---|---:|---:|---:|---:|---:|
| qwen | explicit | 5/8 | 6/8 | 4/8 | 8/8 | 4/8 |
| qwen | derivation | 0/8 | 6/8 | 0/8 | 8/8 | 0/8 |
| qwen | short | 7/8 | 8/8 | 7/8 | 8/8 | 7/8 |
| llama | explicit | 8/8 | 3/8 | 3/8 | 4/8 | 2/8 |
| llama | derivation | 0/8 | 3/8 | 0/8 | 2/8 | 0/8 |
| llama | short | 1/8 | 8/8 | 1/8 | 7/8 | 1/8 |
| gemma | explicit | 8/8 | 7/8 | 7/8 | 1/8 | 1/8 |
| gemma | derivation | 0/8 | 7/8 | 0/8 | 1/8 | 0/8 |
| gemma | short | 7/8 | 8/8 | 7/8 | 8/8 | 7/8 |

注意：explicit/derivation 的 runs 与 five 受旧题面 _runs 歧义污染（把失分读成击球得分），不能作为“失分更新”结论；total 也受 innings_total_wickets 被读成总得分的影响（llama 尤其明显）。

## 2. 两名投手都沿用旧值

| 定义 | 计数 |
|---|---:|
| A、B 都旧值（不要求总数） | 18/24 |
| A、B 都旧值且总出局正确 | **11/24** |
| A、B 都旧值但总数错 | 7/24 |

分模型（A、B 都旧值且总数正确）：qwen 3、llama 2、gemma 6。

## 3. 推导→短证据配对（two_wickets）

| 模型 | 错→对 | 对→错 | 对→对 | 错→错 |
|---|---:|---:|---:|---:|
| qwen | 7 | 0 | 0 | 1 |
| llama | 1 | 0 | 0 | 7 |
| gemma | 7 | 0 | 0 | 1 |

- qwen 错→对：0003、0008、0010、0012、0015、0017、0030；0026 仍错。
- gemma 错→对：0003、0008、0010、0012、0015、0026、0030；0017 仍错。
- llama 错→对：仅 0003；其余 7 场仍错。

## 4. Llama 短证据 1/8 的具体位置

llama short 只有 match_0003 两名投手都答对，且该场总数也正确（8）。  
“两位投手已答对但总数答错”的场次为 0。  
其余 7 场：5 场两人都旧值，2 场两人都改但值错。llama 的失败主要不在总数，而在不更新/更新错。

## 5. 旧 method.jsonl 离线重读

旧 runner 用 fields 键判断 parse，抽取协议把键放在顶层，所以 parse_ok=0/8；真实结构是可解析的。

| 模型 | doc 可解析 | 字段完整 | 原投手旧值正确 | Python 更新后三项正确 |
|---|---:|---:|---:|---:|
| qwen | 8/8 | 8/8 | 1/8 | 0/8 |
| llama | 8/8 | 8/8 | 1/8 | 1/8 |
| gemma | 8/8 | 5/8 | 2/8 | 1/8 |

- qwen match_0003 抽到 orig_wickets=2（gold 4）、orig_runs=17（28）、new_runs=102；llama 抽到 1/4、1/4；gemma 多数字段 None。
- 因此“程序更新”没有证明有效：抽取本身错，Python 只能传播错误。
- 该结果只说明旧抽取协议不可用，不说明“按事件记账”方法无效。

## 6. 对下一轮的含义

- 0/24 是三项同时正确；11/24 是干净“两人都旧值且总数正确”。两个数字并存。
- 短证据有效（qwen/gemma 7/8），但它同时缩短正文、展开数值写法、直接给总数，无法分离“标注证据”和“删正文/改写数值”。
- 下一轮保持全文不变，只加 EVIDENCE 标记；主比较 B−A。


---

# 附录 C：RESULTS.md 全文

# RESULTS：证据标注跟进（开发集 + 留出集）

日期：2026-11-13。本地 Ollama，实际 120/120，外部 API 0。历史结果只读。

## 0. 结论

- **只在全文中标出原句（B）没有帮助**：开发 8 场、留出 6 场、3 个模型，B−A 在“两名投手同时正确”上全部为 0；三项同时正确也全部为 0。
- C（摘出标记句）在“总出局数”上略好（gemma +1、llama +2、qwen +2 场），但两名投手仍 0/8；且 C 漏了“figures are the pre-revision record”的 Note，属于构建缺陷，不能作为“证据足够”的严格结论。
- Lina 修正字段后：gemma original/explicit 五项全对，derivation 仍旧值；qwen 出现字段名坍缩（输出 wickets_credited 等泛化键），协议失败。
- 重测 6/6 全一致。

## 1. 旧结果复算（详见 BASELINE_REANALYSIS.md）

- 三项同时正确 0/24；两名投手都旧值且总数正确 **11/24**；只要求两人旧值则 18/24。
- 推导→短证据 two_wickets：qwen 7 场错→对，gemma 7，llama 1；没有对→错。
- Llama 短证据 1/8：唯一正确的 match_0003 总数也正确；“两人已对但总数错”为 0；其余是 5 场两人旧值、2 场都改但值错。
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

B−A 在 two_wickets 上为 0；total 上 qwen −1、llama 0、gemma 0。

## 4. 配对变化

- B−A（开发）：two_wickets 从错到对 0 场，从对到错 0 场；three 同样 0。
- B−A（留出）：two_wickets 0/0；total qwen 1 场从对到错，其余无变化。
- C−B（开发）：two_wickets 0/0；total gemma +1、llama +2、qwen +2；但 C 缺 pre-revision Note，收益不能归因于“证据足够”。

## 5. 错法

开发 A/B：

- gemma：both_old 7/8，both_updated_wrong 1/8。
- llama：both_old 4/8，only_new_plus1 2/8，both_updated_wrong 2/8。
- qwen：both_old 6/8，only_new_plus1 1/8，format 1/8（B 条件 format 2/8）。

留出 A/B：

- gemma：both_old 6/6。
- llama：A both_old 5、only_new 1；B both_old 4、only_new 1、both_updated_wrong 1。
- qwen：A both_old 3、both_updated_wrong 2、format 1；B both_old 4、both_updated_wrong 1、format 1。

典型样例：match_0008（Luke Barrett 3→2、Ryan Frost 3→4、total 10）。gemma A/B 都输出 3、3、10；qwen A/B 都输出 3、3、8；llama A 输出 4、4、10，B 输出 4、4、10；C 只有 llama 改成 3、4、10。标注没有让 gemma/qwen 更新。

## 6. Lina

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 字段名坍缩，协议失败 |
| explicit | 3/6、4/7、10 五项全对 | 同上 |
| derivation | 4/6、3/7、10 旧值 | 同上 |

gemma 能抄更新后的数字，但不能应用改判；qwen 的失败是输出键不合法，不能作为能力读数。

## 7. 重测

qwen/llama/gemma 在 match_0008、match_0017 的 A 条件均 5/5 一致。

## 8. 四句话

1. **同样的全文里只标出原句，在 0 场新比赛、0 个模型上有帮助**：开发 8 场和留出 6 场的 B−A 在两名投手同时正确上都是 0，三项同时正确也都是 0；B 与 A 的输出逐场相同或几乎相同。
2. **开发集里删掉其他正文（C）只多做对了总出局数（gemma +1、llama +2、qwen +2 场），两名投手仍是 0/8**；但 C 漏了“旧汇总是改判前记录”的 Note，这个收益不能当作“证据足够”的证据，需修正后重跑。
3. **剩余错误主要不是“找不到证据”**：A/B 全文相同、只多标记，模型仍以两人旧值为主（gemma 7/8、qwen 6/8、llama 4/8）；Lina 的 gemma 在明示版能抄 3/6、4/7，推导版回到 4/6、3/7，说明卡在“把改判应用到最终数值”，不是读不到数字。
4. **220 场整表评测还差三件**：原始解说与 scorecard 的字段映射、可靠计分范围（目前 28 个核心字段，完整表约 450 cell 需要分块输出）、以及输出预算/截断控制；下一轮最值得投入的是“改判应用/事件更新”的结构化对照，而不是继续加证据标注。

## 9. 构建缺陷的影响

C 未包含 A 中“the bowling figures above are the pre-revision record”的 Note，导致 C 的旧汇总没有状态标签。C 的 total 改善只能作为探索性观察；C 的 two_wickets 0/8 不能解释为“给了足够证据仍失败”，因为证据并不完整。A/B 的比较不受此影响。


---

# 附录 D：FULL_TABLE_READINESS.md 全文

# FULL_TABLE_READINESS：220 场原始解说到整表评测的准备

日期：2026-11-13。0 次模型调用；只使用现有文件。

## 0. 结论

- 220 场都有原始 commentary、scorecard、meta；但当前真正能可靠计分的是 **28 个核心字段**（总分、wickets、extras 四项、击球和、投球失分、最大伙伴、每局最佳击球/投球）。
- 完整记分卡约 450 个 cell，现有 num_predict=300 的输出预算远远不够；需要分块（每局/每表）或更大的输出预算与截断检查。
- R28 改判诊断能映射到完整表的两个投手行（bowling 表的 W、R）和该局 summary 的 total wickets；这为整表评测提供了一个天然的“局部更新”入口。

## 1. 人工抽查的 6 场

| match | 原始解说 | scorecard | 重渲染来源 |
|---|---|---|---|
| match_0003 | Self-cricket-clean_text_scorecard_v1_220_matches/match_0003/commentary.txt | 同目录 scorecard.md | scorecard 重渲染 seed=0 |
| match_0008 | 同上/match_0008/commentary.txt | scorecard.md | 同上 |
| match_0010 | 同上/match_0010/commentary.txt | scorecard.md | 同上 |
| match_0012 | 同上/match_0012/commentary.txt | scorecard.md | 同上 |
| match_0015 | 同上/match_0015/commentary.txt | scorecard.md | 同上 |
| match_0017 | 同上/match_0017/commentary.txt | scorecard.md | 同上 |

原始解说是发布目录里的文本（模板生成）；本轮改判用的是 scorecard 重渲染，两者必须分开标注。

## 2. 字段可计分性

| 类别 | 例子 | 现状 |
|---|---|---|
| 直接可读 | 队名、球员名、击球 runs/balls/4s/6s、投手 O/M/R/W、总分、extras 四项 | 可计分；28 核心字段已覆盖主要项 |
| 可推导 | batting_runs_sum、bowling_runs_charged、extras 合计、wicket 合计、FOW 末值 | 可用闭合规则验证；本轮已用于 scorer |
| 证据不足/需额外处理 | 部分 partnership 明细、FOW 逐条、未命名出局、两局同名字段的绑定 | 需要更多证据映射或人工核对 |

## 3. 两名投手在完整表中的位置

以 match_0008 为例（第二局）：

- bowling 表：Luke Barrett 行（W=3、R=30）；Ryan Frost 行（W=3、R=37）。
- 该局 summary：Total = 157/10；total wickets = 10。
- R28 改判把 Luke 的一次出局改给 Ryan：Luke W 3→2，Ryan W 3→4，total wickets 10 不变；R 列不变。
- 完整表评分应同时检查这两个 W 单元格、两个 R 单元格、summary 的 W；这正是本轮五字段的全表版本。

## 4. 下一轮整表输出结构（建议）

每场输出一个 JSON：

- match: result, toss, pom, venue
- innings[2]: team, total_runs, total_wickets, overs, extras{byes,leg_byes,no_balls,wides}, batting[{name,runs,balls,fours,sixes,dismissal}], bowling[{name,overs,maidens,runs_conceded,wickets}], fow[], partnerships[]
- 评分字段：28 核心 + 49 字段版；完整表按 cell 计分，另报 record-exact。

输出预算：

- scorecard 约 1,360 tokens；当前 num_predict=300 只能输出五字段，整表需要 1,500–2,000 tokens，且要检查 done_reason=length。
- 220 场 × 1 次整表调用 ≈ 220 × 1.5k 输出 tokens；如果分块（每局/每表），调用数和预算增加，需先做 6 场试点。

## 5. 截断与可靠性检查

1. done_reason 是否为 stop；length 直接判截断。
2. JSON 是否完整、字段数是否等于 schema。
3. 闭合约束：bat_sum+extras=total；extras 四项和；bowling_charged=total-byes-lb；wicket 合计+run-out=total。
4. 逐字段与 scorecard 对比；完整表另报 cell accuracy 和 record exact。
5. 原始解说与重渲染文本必须分别标记，不能混为同一来源。

## 6. 目前可靠计分的范围

- 可靠：28 核心字段（本轮与 Pilot-10 已验证）、49 字段版中的 direct/derived 部分。
- 需补：完整 partnerships、FOW 逐条、部分 dismissal 细节、两局同名字段的绑定。
- 不建议现在直接跑 220 场整表；先 6 场试点，确认输出预算、截断率和闭合率，再扩到 30 场。


---

# 附录 E：ANSWER_KEY.md 全文

# ANSWER_KEY：证据跟进金标

## match_0003 — Brandon Hale

| 字段 | 值 |
|---|---:|
| Evan Clarke_wickets_credited | 3 |
| Evan Clarke_bowling_runs_conceded | 28 |
| Connor Reed_wickets_credited | 2 |
| Connor Reed_bowling_runs_conceded | 28 |
| innings_wickets_lost | 8 |

- 出局旧记录：When Brandon Hale fell to Evan Clarke for 4, the scoreboard read 17/2..
- 原投手旧汇总：Ridgehaven's bowling effort was led by Evan Clarke, whose 4 for 28 made the deepest incisions.
- 新投手旧汇总：Connor Reed kept the pressure on with 1 for 28, and together they ensured no partnership could breathe..
- 总出局依据：The lower order flickered briefly — Harvey Stone made 5 — but Brookmere were 164/8 and the innings was nearly done..
- 改判通知：Match review: the dismissal of Brandon Hale in the first innings was reassigned from Evan Clarke to Connor Reed.

## match_0008 — Noah Brooks

| 字段 | 值 |
|---|---:|
| Luke Barrett_wickets_credited | 2 |
| Luke Barrett_bowling_runs_conceded | 30 |
| Ryan Frost_wickets_credited | 4 |
| Ryan Frost_bowling_runs_conceded | 37 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Noah Brooks fell to Luke Barrett for 1.
- 原投手旧汇总：Coral Coast XI's bowling effort was led by Luke Barrett, whose 3 for 30 made the deepest incisions.
- 新投手旧汇总：Ryan Frost kept the pressure on with 3 for 37, and together they ensured no partnership could breathe..
- 总出局依据：Ridgeview XI closed on 157 for 10 from 43.3 overs, the 105 runs margin reflecting a chase that had been tested but never broken..
- 改判通知：Scorers' correction: Noah Brooks's dismissal, originally credited to Luke Barrett, now belongs to Ryan Frost.

## match_0010 — Caleb Marsh

| 字段 | 值 |
|---|---:|
| Ryan Foster_wickets_credited | 2 |
| Ryan Foster_bowling_runs_conceded | 48 |
| Evan Turner_wickets_credited | 3 |
| Evan Turner_bowling_runs_conceded | 38 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Caleb Marsh fell to Ryan Foster for 2.
- 原投手旧汇总：Summit Vale XI's bowling effort was led by Ryan Foster, whose 3 for 48 made the deepest incisions.
- 新投手旧汇总：Evan Turner kept the pressure on with 2 for 38, and together they ensured no partnership could breathe..
- 总出局依据：Gulfstone XI closed on 223 for 10 from 44.3 overs, the 59 runs margin reflecting a chase that had been tested but never broken..
- 改判通知：The review panel moved Caleb Marsh's dismissal from Ryan Foster to Evan Turner.

## match_0012 — Dylan Grant

| 字段 | 值 |
|---|---:|
| Caleb Brooks_wickets_credited | 3 |
| Caleb Brooks_bowling_runs_conceded | 56 |
| Lucas Vale_wickets_credited | 3 |
| Lucas Vale_bowling_runs_conceded | 44 |
| innings_wickets_lost | 10 |

- 出局旧记录：When Dylan Grant fell to Caleb Brooks for 12, the scoreboard read 184/5..
- 原投手旧汇总：Westmere XI's bowling effort was led by Caleb Brooks, whose 4 for 56 made the deepest incisions.
- 新投手旧汇总：Lucas Vale kept the pressure on with 2 for 44, and together they ensured no partnership could breathe..
- 总出局依据：The arithmetic was straightforward — 15 from Ryan Wells, 1 from Leo Bennett — and the scoreboard shifted from 231/9 to 247/10..
- 改判通知：Match review: the dismissal of Dylan Grant in the first innings was reassigned from Caleb Brooks to Lucas Vale.

## match_0015 — Owen Hayes

| 字段 | 值 |
|---|---:|
| Noah Grant_wickets_credited | 3 |
| Noah Grant_bowling_runs_conceded | 62 |
| Caleb Rourke_wickets_credited | 3 |
| Caleb Rourke_bowling_runs_conceded | 41 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Owen Hayes fell to Noah Grant for 6.
- 原投手旧汇总：Ridge Falcons XI's bowling effort was led by Noah Grant, whose 4 for 62 made the deepest incisions.
- 新投手旧汇总：Caleb Rourke kept the pressure on with 2 for 41, and together they ensured no partnership could breathe..
- 总出局依据：Coastal Meridian XI closed on 279 for 10 from 46.2 overs, the 65 runs margin reflecting a chase that had been tested but never broken..
- 改判通知：Scorers' correction: Owen Hayes's dismissal, originally credited to Noah Grant, now belongs to Caleb Rourke.

## match_0017 — Liam Reed

| 字段 | 值 |
|---|---:|
| Miles Carter_wickets_credited | 4 |
| Miles Carter_bowling_runs_conceded | 18 |
| Liam Brooks_wickets_credited | 4 |
| Liam Brooks_bowling_runs_conceded | 27 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Liam Reed fell to Miles Carter for 3.
- 原投手旧汇总：Ridgevale XI's bowling effort was led by Miles Carter, whose 5 for 18 made the deepest incisions.
- 新投手旧汇总：Liam Brooks kept the pressure on with 3 for 27, and together they ensured no partnership could breathe..
- 总出局依据：The arithmetic was straightforward — 33 from Miles Carter, 8 from Mason Gray — and the scoreboard shifted from 130/9 to 174/10..
- 改判通知：The review panel moved Liam Reed's dismissal from Miles Carter to Liam Brooks.

## match_0026 — Ryan Hale

| 字段 | 值 |
|---|---:|
| Dylan Cole_wickets_credited | 4 |
| Dylan Cole_bowling_runs_conceded | 5 |
| Ben Carter_wickets_credited | 3 |
| Ben Carter_bowling_runs_conceded | 5 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Ryan Hale fell to Dylan Cole for 0.
- 原投手旧汇总：Ridgeport's bowling effort was led by Dylan Cole, whose 5 for 5 made the deepest incisions.
- 新投手旧汇总：Ben Carter kept the pressure on with 2 for 5, and together they ensured no partnership could breathe..
- 总出局依据：Coral Bay closed on 33 for 10 from 17.5 overs, the 218 runs margin reflecting a chase that had been tested but never broken..
- 改判通知：Match review: the dismissal of Ryan Hale in the second innings was reassigned from Dylan Cole to Ben Carter.

## match_0030 — Ben Carter

| 字段 | 值 |
|---|---:|
| Logan Vale_wickets_credited | 3 |
| Logan Vale_bowling_runs_conceded | 10 |
| Owen Price_wickets_credited | 3 |
| Owen Price_bowling_runs_conceded | 1 |
| innings_wickets_lost | 10 |

- 出局旧记录：When Ben Carter fell to Logan Vale for 0, the scoreboard read 43/5..
- 原投手旧汇总：Harborfield's bowling effort was led by Logan Vale, whose 4 for 10 made the deepest incisions.
- 新投手旧汇总：Owen Price kept the pressure on with 2 for 1, and together they ensured no partnership could breathe..
- 总出局依据：The lower order flickered briefly — Dylan Grant made 1 — but Lagoon were 52/10 and the innings was nearly done..
- 改判通知：Scorers' correction: Ben Carter's dismissal, originally credited to Logan Vale, now belongs to Owen Price.

## match_0009 — Dylan Shaw

| 字段 | 值 |
|---|---:|
| Tyler Grant_wickets_credited | 1 |
| Tyler Grant_bowling_runs_conceded | 25 |
| Luke Barrett_wickets_credited | 3 |
| Luke Barrett_bowling_runs_conceded | 43 |
| innings_wickets_lost | 5 |

- 出局旧记录：The chase took a hit when Dylan Shaw fell to Tyler Grant for 7.
- 原投手旧汇总：Ridgewater XI's bowling effort was led by Tyler Grant, whose 2 for 25 made the deepest incisions.
- 新投手旧汇总：Luke Barrett kept the pressure on with 2 for 43, and together they ensured no partnership could breathe..
- 总出局依据：When Aaron Holt fell to Connor Blake for 10, the scoreboard read 96/5..
- 改判通知：Match review: the dismissal of Dylan Shaw in the second innings was reassigned from Tyler Grant to Luke Barrett.

## match_0013 — Leo Warren

| 字段 | 值 |
|---|---:|
| Evan Turner_wickets_credited | 2 |
| Evan Turner_bowling_runs_conceded | 70 |
| Zane Carter_wickets_credited | 3 |
| Zane Carter_bowling_runs_conceded | 58 |
| innings_wickets_lost | 8 |

- 出局旧记录：When Leo Warren fell to Evan Turner for 24, the scoreboard read 50/2..
- 原投手旧汇总：Mirage Lions XI's bowling effort was led by Evan Turner, whose 3 for 70 made the deepest incisions.
- 新投手旧汇总：Zane Carter kept the pressure on with 2 for 58, and together they ensured no partnership could breathe..
- 总出局依据：The lower order flickered briefly — Liam Foster made 3 — but Silver Pearl XI were 263/8 and the innings was nearly done..
- 改判通知：Match review: the dismissal of Leo Warren in the first innings was reassigned from Evan Turner to Zane Carter.

## match_0014 — Elias Ward

| 字段 | 值 |
|---|---:|
| Leo Quinn_wickets_credited | 1 |
| Leo Quinn_bowling_runs_conceded | 36 |
| Dylan Frost_wickets_credited | 3 |
| Dylan Frost_bowling_runs_conceded | 39 |
| innings_wickets_lost | 7 |

- 出局旧记录：The chase took a hit when Elias Ward fell to Leo Quinn for 4.
- 原投手旧汇总：Canyon Stars XI's bowling effort was led by Leo Quinn, whose 2 for 36 made the deepest incisions.
- 新投手旧汇总：Dylan Frost kept the pressure on with 2 for 39, and together they ensured no partnership could breathe..
- 总出局依据：Canyon Stars XI were 212/7..
- 改判通知：Match review: the dismissal of Elias Ward in the second innings was reassigned from Leo Quinn to Dylan Frost.

## match_0016 — Adrian Clarke

| 字段 | 值 |
|---|---:|
| Evan Reed_wickets_credited | 1 |
| Evan Reed_bowling_runs_conceded | 31 |
| Connor Wells_wickets_credited | 2 |
| Connor Wells_bowling_runs_conceded | 14 |
| innings_wickets_lost | 3 |

- 出局旧记录：The chase took a hit when Adrian Clarke fell to Evan Reed for 4.
- 原投手旧汇总：Pearlbridge XI's bowling effort was led by Evan Reed, whose 2 for 31 made the deepest incisions.
- 新投手旧汇总：Connor Wells kept the pressure on with 1 for 14, and together they ensured no partnership could breathe..
- 总出局依据：Connor Shaw found the breakthrough, Conor Hale departing for 4 to leave Pearlbridge XI at 34/3..
- 改判通知：Match review: the dismissal of Adrian Clarke in the second innings was reassigned from Evan Reed to Connor Wells.

## match_0018 — Ethan Blake

| 字段 | 值 |
|---|---:|
| Dylan Fox_wickets_credited | 2 |
| Dylan Fox_bowling_runs_conceded | 34 |
| Ben Turner_wickets_credited | 3 |
| Ben Turner_bowling_runs_conceded | 35 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Ethan Blake fell to Dylan Fox for 12.
- 原投手旧汇总：Dunecrest XI's bowling effort was led by Dylan Fox, whose 3 for 34 made the deepest incisions.
- 新投手旧汇总：Ben Turner kept the pressure on with 2 for 35, and together they ensured no partnership could breathe..
- 总出局依据：Harborline XI closed on 252 for 10 from 49.2 overs, the 36 runs margin reflecting a chase that had been tested but never broken..
- 改判通知：Match review: the dismissal of Ethan Blake in the second innings was reassigned from Dylan Fox to Ben Turner.

## match_0027 — Aaron Reed

| 字段 | 值 |
|---|---:|
| Owen Price_wickets_credited | 2 |
| Owen Price_bowling_runs_conceded | 14 |
| Adam Wells_wickets_credited | 3 |
| Adam Wells_bowling_runs_conceded | 9 |
| innings_wickets_lost | 10 |

- 出局旧记录：The chase took a hit when Aaron Reed fell to Owen Price for 1.
- 原投手旧汇总：Seabrook's bowling effort was led by Owen Price, whose 3 for 14 made the deepest incisions.
- 新投手旧汇总：Adam Wells kept the pressure on with 2 for 9, and together they ensured no partnership could breathe..
- 总出局依据：Highland Isle closed on 52 for 10 from 19.2 overs, the 252 runs margin reflecting a chase that had been tested but never broken..
- 改判通知：Match review: the dismissal of Aaron Reed in the second innings was reassigned from Owen Price to Adam Wells.


---

# 附录 F：BLIND_REVIEW.md 全文

# BLIND_REVIEW：人工核对题面（A 全文）

每场给 A 全文、五个字段和作答位。B 只是 A 加 [EVIDENCE]；C 是五个标记句的摘录（缺 pre-revision Note，见 DESIGN）。

## match_0003 — Brandon Hale — Evan Clarke -> Connor Reed
----- BEGIN TEXT -----
Brookmere began through Aiden Cole and Brandon Hale. The early exchanges set a tone of uncertain, tense finish.. Evan Clarke broke through — Aiden Cole gone for 7. Brookmere were 15/1.. When Brandon Hale fell to Evan Clarke for 4, the scoreboard read 17/2.. Caleb Price found the breakthrough, Marcus Drake departing for 34 to leave Brookmere at 87/3.. Marcus Drake and Dorian Cross constructed a repair worth 70. With Marcus Drake scoring 32 and Dorian Cross contributing 37, Brookmere moved from 17/2 to 87/3.. A stand of 15 between Dorian Cross and Elliot Reed rebuilt the innings. The arithmetic was straightforward — 9 from Dorian Cross, 6 from Elliot Reed — and the scoreboard shifted from 87/3 to 102/4.. Felix Grant and Dorian Cross constructed a repair worth 35. With Felix Grant scoring 13 and Dorian Cross contributing 21, Brookmere moved from 102/4 to 137/5.. A stand of 17 between Harvey Stone and Dorian Cross rebuilt the innings. The arithmetic was straightforward — 1 from Harvey Stone, 14 from Dorian Cross — and the scoreboard shifted from 137/6 to 154/7.. Through the middle phase, Dorian Cross held firm, compiling 81 from 56 balls. The 6 boundaries and 5 sixes told only part of the story — the real value was the time he bought for Brookmere.. Connor Reed broke through — Elliot Reed gone for 6. Brookmere were 102/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Felix Grant fell to Evan Clarke for 13, the scoreboard read 137/5.. Evan Clarke found the breakthrough, Gareth Bishop departing for 0 to leave Brookmere at 137/6.. Gavin Turner broke through — Dorian Cross gone for 81. Brookmere were 154/7.. The lower order flickered briefly — Harvey Stone made 5 — but Brookmere were 164/8 and the innings was nearly done.. The innings closed at 164 from 20.0 overs.. Ridgehaven's bowling effort was led by Evan Clarke, whose 4 for 28 made the deepest incisions. Connor Reed kept the pressure on with 1 for 28, and together they ensured no partnership could breathe.. The total included 9 extras, with 6 wides and 2 no-balls coming directly from the bowlers' accounts. Another 0 byes and 1 leg-bye also found their way into the score. The batters themselves accounted for 155. All told, the innings reached 164.. Set 164 to win, Ridgehaven sent out Ethan Parker and Lucas Bennett. The chase would test temperament as much as technique.. The chase took a hit when Ethan Parker fell to Isaac Wells for 16. At 38/1, with 164 still needed, the pressure that had been theoretical was now real.. Isaac Wells broke through — Nathan Brooks gone for 8. Ridgehaven were 57/2 chasing 164, and the innings needed a partnership.. The chase took a hit when Connor Reed fell to Gareth Bishop for 2. At 62/3, with 164 still needed, the pressure that had been theoretical was now real.. Jordan Pike broke through — Lucas Bennett gone for 37. Ridgehaven were 80/4 chasing 164, and the innings needed a partnership.. The chase took a hit when Dylan Foster fell to Isaac Wells for 30. At 129/5, with 164 still needed, the pressure that had been theoretical was now real.. Nathan Brooks and Lucas Bennett constructed 19 together. With Nathan Brooks contributing 8 and Lucas Bennett adding 10, Ridgehaven moved from 38/1 to 57/2. The target of 164 had come into view.. The stand that changed the chase came from Lucas Bennett and Dylan Foster. Their 18 — 6 from Lucas Bennett, 12 from Dylan Foster — carried Ridgehaven from 62/3 to 80/4, transforming the equation.. Mason Cooper and Dylan Foster constructed 49 together. With Mason Cooper contributing 29 and Dylan Foster adding 18, Ridgehaven moved from 80/4 to 129/5. The target of 164 had come into view.. The chase found its centre in Mason Cooper, whose 41 from 25 deliveries carried Ridgehaven from uncertainty toward their target of 164. The 3 fours and 2 sixes were the visible markers of an innings built in stages.. Ridgehaven closed on 165 for 6 from 19.4 overs, the 4 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 10: 7 wides, 2 no-balls, plus 0 byes and 1 leg-bye. The batters produced 155 between them. The bowling side's ledger showed 164 charged to the attack, the remainder of the 165 having arrived through routes that bypass the bowler's figures.. Brookmere's bowling effort was led by Isaac Wells, whose 3 for 25 made the deepest incisions. Gareth Bishop kept the pressure on with 1 for 27, and together they ensured no partnership could breathe.. Ridgehaven Won by 4 Wickets, with Evan Clarke recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Brandon Hale in the first innings was reassigned from Evan Clarke to Connor Reed. All other figures stand.
----- END TEXT -----
作答：
- Evan Clarke_wickets_credited = ____ ；依据句：____
- Evan Clarke_bowling_runs_conceded = ____ ；依据句：____
- Connor Reed_wickets_credited = ____ ；依据句：____
- Connor Reed_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0008 — Noah Brooks — Luke Barrett -> Ryan Frost
----- BEGIN TEXT -----
At Eastbank Meadow Ground, Hillview, Coral Coast XI chose to bat after winning the toss, reading conditions looked good for chasing. Coral Coast XI would bat first with Ridgeview XI to chase.. Coral Coast XI began through Rowan Vale and Lucas Hart. The early exchanges set a tone of commanding, inevitable.. Dylan Price broke through — Rowan Vale gone for 17. Coral Coast XI were 27/1.. When Evan Price fell to Dylan Price for 0, the scoreboard read 27/2.. Aaron Wells found the breakthrough, Nathan Wells departing for 35 to leave Coral Coast XI at 111/3.. Lucas Hart and Nathan Wells constructed a repair worth 84. With Lucas Hart scoring 45 and Nathan Wells contributing 35, Coral Coast XI moved from 27/2 to 111/3.. A stand of 67 between Adrian Blake and Lucas Hart rebuilt the innings. The arithmetic was straightforward — 36 from Adrian Blake, 29 from Lucas Hart — and the scoreboard shifted from 111/3 to 178/4.. Adrian Blake and Marcus Shaw constructed a repair worth 41. With Adrian Blake scoring 18 and Marcus Shaw contributing 22, Coral Coast XI moved from 178/4 to 219/5.. A stand of 17 between Isaac Reed and Ryan Frost rebuilt the innings. The arithmetic was straightforward — 4 from Isaac Reed, 8 from Ryan Frost — and the scoreboard shifted from 234/7 to 251/8.. Through the middle phase, Lucas Hart held firm, compiling 82 from 121 balls. The 8 boundaries and 1 six told only part of the story — the real value was the time he bought for Coral Coast XI.. Aaron Wells broke through — Lucas Hart gone for 82. Coral Coast XI were 178/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Marcus Shaw fell to Liam Turner for 22, the scoreboard read 219/5.. Liam Turner found the breakthrough, Liam Barrett departing for 6 to leave Coral Coast XI at 225/6.. Aaron Wells broke through — Adrian Blake gone for 58. Coral Coast XI were 234/7.. The lower order flickered briefly — Ryan Frost made 8 — but Coral Coast XI were 251/8 and the innings was nearly done.. The innings closed at 262 from 50.0 overs.. Ridgeview XI's bowling effort was led by Dylan Price, whose 2 for 33 made the deepest incisions. Liam Turner kept the pressure on with 2 for 44, and together they ensured no partnership could breathe.. The total included 17 extras, with 11 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 4 leg-byes also found their way into the score. The batters themselves accounted for 245. All told, the innings reached 262.. Set 262 to win, Ridgeview XI sent out Ethan Parker and Lucas Bennett. The chase would test temperament as much as technique.. The chase took a hit when Ethan Parker fell to Mason Hale for 13. At 22/1, with 262 still needed, the pressure that had been theoretical was now real.. Ryan Frost broke through — Lucas Bennett gone for 10. Ridgeview XI were 32/2 chasing 262, and the innings needed a partnership.. The chase took a hit when Owen Carter fell to Evan Reed for 20. At 49/3, with 262 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Mason Reid gone for 5. Ridgeview XI were 52/4 chasing 262, and the innings needed a partnership.. The chase took a hit when Noah Brooks fell to Luke Barrett for 1. At 56/5, with 262 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Caleb Hayes gone for 7. Ridgeview XI were 63/6 chasing 262, and the innings needed a partnership.. The chase took a hit when Dylan Price fell to Evan Reed for 25. At 120/7, with 262 still needed, the pressure that had been theoretical was now real.. Ryan Frost broke through — Liam Turner gone for 12. Ridgeview XI were 144/8 chasing 262, and the innings needed a partnership.. The chase took a hit when Aiden Cole fell to Ryan Frost for 51. At 155/9, with 262 still needed, the pressure that had been theoretical was now real.. Lucas Bennett and Owen Carter constructed 10 together. With Lucas Bennett contributing 2 and Owen Carter adding 7, Ridgeview XI moved from 22/1 to 32/2. The target of 262 had come into view.. The stand that changed the chase came from Mason Reid and Owen Carter. Their 17 — 4 from Mason Reid, 13 from Owen Carter — carried Ridgeview XI from 32/2 to 49/3, transforming the equation.. Aiden Cole and Dylan Price constructed 57 together. With Aiden Cole contributing 30 and Dylan Price adding 25, Ridgeview XI moved from 63/6 to 120/7. The target of 262 had come into view.. Zane Perry and Aiden Cole constructed 11 together. With Zane Perry contributing 1 and Aiden Cole adding 9, Ridgeview XI moved from 144/8 to 155/9. The target of 262 had come into view.. The chase found its centre in Aiden Cole, whose 51 from 70 deliveries carried Ridgeview XI from uncertainty toward their target of 262. The 4 fours and 1 six were the visible markers of an innings built in stages.. Ridgeview XI closed on 157 for 10 from 43.3 overs, the 105 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 11: 7 wides, 1 no-ball, plus 2 byes and 1 leg-bye. The batters produced 146 between them. The bowling side's ledger showed 154 charged to the attack, the remainder of the 157 having arrived through routes that bypass the bowler's figures.. Coral Coast XI's bowling effort was led by Luke Barrett, whose 3 for 30 made the deepest incisions. Ryan Frost kept the pressure on with 3 for 37, and together they ensured no partnership could breathe.. Coral Coast XI Won by 105 Runs, with Lucas Hart recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Scorers' correction: Noah Brooks's dismissal, originally credited to Luke Barrett, now belongs to Ryan Frost. All other figures stand.
----- END TEXT -----
作答：
- Luke Barrett_wickets_credited = ____ ；依据句：____
- Luke Barrett_bowling_runs_conceded = ____ ；依据句：____
- Ryan Frost_wickets_credited = ____ ；依据句：____
- Ryan Frost_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0010 — Caleb Marsh — Ryan Foster -> Evan Turner
----- BEGIN TEXT -----
At Northbank Meadow Ground, Hillview, Gulfstone XI chose to field after winning the toss, reading conditions looked good for chasing. Summit Vale XI would bat first with Gulfstone XI to chase.. Summit Vale XI began through Rowan Grant and Leo Bennett. The early exchanges set a tone of uncertain, tense finish.. Zane Foster broke through — Rowan Grant gone for 4. Summit Vale XI were 7/1.. When Leo Bennett fell to Lucas Reed for 9, the scoreboard read 23/2.. Connor Blake found the breakthrough, Connor Wells departing for 31 to leave Summit Vale XI at 85/3.. A stand of 16 between Isaac Ward and Leo Bennett rebuilt the innings. The arithmetic was straightforward — 8 from Isaac Ward, 7 from Leo Bennett — and the scoreboard shifted from 7/1 to 23/2.. Connor Wells and Isaac Ward constructed a repair worth 62. With Connor Wells scoring 31 and Isaac Ward contributing 28, Summit Vale XI moved from 23/2 to 85/3.. A stand of 24 between Evan Reid and Isaac Ward rebuilt the innings. The arithmetic was straightforward — 17 from Evan Reid, 5 from Isaac Ward — and the scoreboard shifted from 85/3 to 109/4.. Evan Reid and Aaron Vale constructed a repair worth 77. With Evan Reid scoring 6 and Aaron Vale contributing 68, Summit Vale XI moved from 109/4 to 186/5.. A stand of 32 between Aaron Vale and Luca Barrett rebuilt the innings. The arithmetic was straightforward — 22 from Aaron Vale, 10 from Luca Barrett — and the scoreboard shifted from 186/5 to 218/6.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Liam Frost and Aaron Vale constructed a repair worth 48. With Liam Frost scoring 30 and Aaron Vale contributing 12, Summit Vale XI moved from 218/6 to 266/7.. Through the middle phase, Aaron Vale held firm, compiling 102 from 74 balls. The 9 boundaries and 7 sixes told only part of the story — the real value was the time he bought for Summit Vale XI.. Caleb Marsh broke through — Isaac Ward gone for 41. Summit Vale XI were 109/4.. When Evan Reid fell to Lucas Reed for 23, the scoreboard read 186/5.. Daniel Cross found the breakthrough, Luca Barrett departing for 10 to leave Summit Vale XI at 218/6.. Owen Hayes broke through — Aaron Vale gone for 102. Summit Vale XI were 266/7.. The lower order flickered briefly — Ryan Foster made 8 — but Summit Vale XI were 274/8 and the innings was nearly done.. The innings closed at 282 from 50.0 overs.. Gulfstone XI's bowling effort was led by Zane Foster, whose 2 for 51 made the deepest incisions. Owen Hayes kept the pressure on with 1 for 18, and together they ensured no partnership could breathe.. The total included 16 extras, with 11 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 266. All told, the innings reached 282.. Set 282 to win, Gulfstone XI sent out Ethan Ward and Owen Hayes. The chase would test temperament as much as technique.. The chase took a hit when Owen Hayes fell to Mason Hart for 21. At 38/1, with 282 still needed, the pressure that had been theoretical was now real.. Ryan Foster broke through — Aiden Price gone for 17. Gulfstone XI were 67/2 chasing 282, and the innings needed a partnership.. The chase took a hit when Caleb Marsh fell to Ryan Foster for 2. At 70/3, with 282 still needed, the pressure that had been theoretical was now real.. Ryan Foster broke through — Ethan Ward gone for 24. Gulfstone XI were 76/4 chasing 282, and the innings needed a partnership.. The chase took a hit when Daniel Cross fell to Luke Barrett for 23. At 122/5, with 282 still needed, the pressure that had been theoretical was now real.. Liam Frost broke through — Zane Foster gone for 36. Gulfstone XI were 188/6 chasing 282, and the innings needed a partnership.. The chase took a hit when Noah Grant fell to Evan Turner for 53. At 199/7, with 282 still needed, the pressure that had been theoretical was now real.. Evan Turner broke through — Lucas Reed gone for 4. Gulfstone XI were 207/8 chasing 282, and the innings needed a partnership.. The chase took a hit when Connor Blake fell to Evan Reid for 15. At 217/9, with 282 still needed, the pressure that had been theoretical was now real.. Ethan Ward and Aiden Price constructed 29 together. With Ethan Ward contributing 9 and Aiden Price adding 17, Gulfstone XI moved from 38/1 to 67/2. The target of 282 had come into view.. The stand that changed the chase came from Noah Grant and Daniel Cross. Their 46 — 22 from Noah Grant, 23 from Daniel Cross — carried Gulfstone XI from 76/4 to 122/5, transforming the equation.. Noah Grant and Zane Foster constructed 66 together. With Noah Grant contributing 26 and Zane Foster adding 36, Gulfstone XI moved from 122/5 to 188/6. The target of 282 had come into view.. Ryan Cole and Connor Blake constructed 10 together. With Ryan Cole contributing 8 and Connor Blake adding 1, Gulfstone XI moved from 207/8 to 217/9. The target of 282 had come into view.. The chase found its centre in Noah Grant, whose 53 from 73 deliveries carried Gulfstone XI from uncertainty toward their target of 282. The 6 fours and 1 six were the visible markers of an innings built in stages.. Gulfstone XI closed on 223 for 10 from 44.3 overs, the 59 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 14: 10 wides, 0 no-balls, plus 2 byes and 2 leg-byes. The batters produced 209 between them. The bowling side's ledger showed 219 charged to the attack, the remainder of the 223 having arrived through routes that bypass the bowler's figures.. Summit Vale XI's bowling effort was led by Ryan Foster, whose 3 for 48 made the deepest incisions. Evan Turner kept the pressure on with 2 for 38, and together they ensured no partnership could breathe.. Summit Vale XI Won by 59 Runs, with Aaron Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. The review panel moved Caleb Marsh's dismissal from Ryan Foster to Evan Turner. All other figures stand.
----- END TEXT -----
作答：
- Ryan Foster_wickets_credited = ____ ；依据句：____
- Ryan Foster_bowling_runs_conceded = ____ ；依据句：____
- Evan Turner_wickets_credited = ____ ；依据句：____
- Evan Turner_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0012 — Dylan Grant — Caleb Brooks -> Lucas Vale
----- BEGIN TEXT -----
At Eastbank Meadow Ground, Hillview, Westmere XI chose to field after winning the toss, reading conditions looked good for chasing. Dune Harbor XI would bat first with Westmere XI to chase.. Dune Harbor XI began through Adrian Stone and Nolan Reed. The early exchanges set a tone of constructive, building.. Liam Frost broke through — Nolan Reed gone for 6. Dune Harbor XI were 23/1.. When Adrian Stone fell to Liam Frost for 27, the scoreboard read 68/2.. Lucas Vale found the breakthrough, Caleb Turner departing for 38 to leave Dune Harbor XI at 101/3.. Caleb Turner and Adrian Stone constructed a repair worth 45. With Caleb Turner scoring 32 and Adrian Stone contributing 11, Dune Harbor XI moved from 23/1 to 68/2.. A stand of 33 between Caleb Turner and Mason Clarke rebuilt the innings. The arithmetic was straightforward — 6 from Caleb Turner, 26 from Mason Clarke — and the scoreboard shifted from 68/2 to 101/3.. Mason Clarke and Connor Shaw constructed a repair worth 64. With Mason Clarke scoring 35 and Connor Shaw contributing 26, Dune Harbor XI moved from 101/3 to 165/4.. A stand of 19 between Dylan Grant and Mason Clarke rebuilt the innings. The arithmetic was straightforward — 12 from Dylan Grant, 6 from Mason Clarke — and the scoreboard shifted from 165/4 to 184/5.. Aiden Fox and Zane Carter constructed a repair worth 18. With Aiden Fox scoring 10 and Zane Carter contributing 7, Dune Harbor XI moved from 197/6 to 215/7.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. A stand of 16 between Ryan Wells and Leo Bennett rebuilt the innings. The arithmetic was straightforward — 15 from Ryan Wells, 1 from Leo Bennett — and the scoreboard shifted from 231/9 to 247/10.. Through the middle phase, Mason Clarke held firm, compiling 68 from 87 balls. The 8 boundaries and 1 six told only part of the story — the real value was the time he bought for Dune Harbor XI.. Caleb Brooks broke through — Connor Shaw gone for 26. Dune Harbor XI were 165/4.. When Dylan Grant fell to Caleb Brooks for 12, the scoreboard read 184/5.. Caleb Brooks found the breakthrough, Mason Clarke departing for 68 to leave Dune Harbor XI at 197/6.. Noah Grant broke through — Zane Carter gone for 7. Dune Harbor XI were 215/7.. The lower order flickered briefly — Evan Hart made 2 — but Dune Harbor XI were 219/8 and the innings was nearly done.. The lower order flickered briefly — Aiden Fox made 23 — but Dune Harbor XI were 231/9 and the innings was nearly done.. The lower order flickered briefly — Leo Bennett made 1 — but Dune Harbor XI were 247/10 and the innings was nearly done.. The innings closed at 247 from 49.3 overs.. Westmere XI's bowling effort was led by Caleb Brooks, whose 4 for 56 made the deepest incisions. Lucas Vale kept the pressure on with 2 for 44, and together they ensured no partnership could breathe.. The total included 12 extras, with 8 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 2 leg-byes also found their way into the score. The batters themselves accounted for 235. All told, the innings reached 247.. Set 247 to win, Westmere XI sent out Ethan Vale and Owen Hart. The chase would test temperament as much as technique.. The chase took a hit when Owen Hart fell to Dylan Grant for 44. At 96/1, with 247 still needed, the pressure that had been theoretical was now real.. Dylan Grant broke through — Aiden Price gone for 7. Westmere XI were 112/2 chasing 247, and the innings needed a partnership.. The chase took a hit when Ethan Vale fell to Aiden Fox for 92. At 190/3, with 247 still needed, the pressure that had been theoretical was now real.. Mason Clarke broke through — Connor Wells gone for 39. Westmere XI were 224/4 chasing 247, and the innings needed a partnership.. Ethan Vale and Aiden Price constructed 16 together. With Ethan Vale contributing 9 and Aiden Price adding 7, Westmere XI moved from 96/1 to 112/2. The target of 247 had come into view.. The stand that changed the chase came from Connor Wells and Ethan Vale. Their 78 — 39 from Connor Wells, 36 from Ethan Vale — carried Westmere XI from 112/2 to 190/3, transforming the equation.. Dylan Marsh and Connor Wells constructed 34 together. With Dylan Marsh contributing 31 and Connor Wells adding 0, Westmere XI moved from 190/3 to 224/4. The target of 247 had come into view.. The chase found its centre in Ethan Vale, whose 92 from 77 deliveries carried Westmere XI from uncertainty toward their target of 247. The 14 fours and 1 six were the visible markers of an innings built in stages.. Westmere XI closed on 249 for 5 from 38.2 overs, the 5 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 13: 10 wides, 1 no-ball, plus 0 byes and 2 leg-byes. The batters produced 236 between them. The bowling side's ledger showed 247 charged to the attack, the remainder of the 249 having arrived through routes that bypass the bowler's figures.. Dune Harbor XI's bowling effort was led by Dylan Grant, whose 2 for 42 made the deepest incisions. Aiden Fox kept the pressure on with 1 for 23, and together they ensured no partnership could breathe.. Westmere XI Won by 5 Wickets, with Ethan Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Dylan Grant in the first innings was reassigned from Caleb Brooks to Lucas Vale. All other figures stand.
----- END TEXT -----
作答：
- Caleb Brooks_wickets_credited = ____ ；依据句：____
- Caleb Brooks_bowling_runs_conceded = ____ ；依据句：____
- Lucas Vale_wickets_credited = ____ ；依据句：____
- Lucas Vale_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0015 — Owen Hayes — Noah Grant -> Caleb Rourke
----- BEGIN TEXT -----
At North Ridge Oval, Hillview, Coastal Meridian XI chose to field after winning the toss, reading conditions looked good for chasing. Ridge Falcons XI would bat first with Coastal Meridian XI to chase.. Ridge Falcons XI began through Toby Grant and Bennett Carter. The early exchanges set a tone of constructive, building.. Mason Reid broke through — Toby Grant gone for 44. Ridge Falcons XI were 105/1.. When Bennett Carter fell to Ethan Ward for 76, the scoreboard read 156/2.. Adrian Clarke found the breakthrough, Luca Barrett departing for 48 to leave Ridge Falcons XI at 218/3.. Bennett Carter and Luca Barrett constructed a repair worth 51. With Bennett Carter scoring 23 and Luca Barrett contributing 27, Ridge Falcons XI moved from 105/1 to 156/2.. A stand of 62 between Caleb Rourke and Luca Barrett rebuilt the innings. The arithmetic was straightforward — 39 from Caleb Rourke, 21 from Luca Barrett — and the scoreboard shifted from 156/2 to 218/3.. Caleb Rourke and Aaron Vale constructed a repair worth 73. With Caleb Rourke scoring 35 and Aaron Vale contributing 35, Ridge Falcons XI moved from 218/3 to 291/4.. A stand of 25 between Daniel Cross and Aaron Vale rebuilt the innings. The arithmetic was straightforward — 9 from Daniel Cross, 14 from Aaron Vale — and the scoreboard shifted from 305/6 to 330/7.. Through the middle phase, Bennett Carter held firm, compiling 76 from 73 balls. The 9 boundaries and 1 six told only part of the story — the real value was the time he bought for Ridge Falcons XI.. Evan Turner broke through — Caleb Rourke gone for 74. Ridge Falcons XI were 291/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Leo Turner fell to Adrian Clarke for 5, the scoreboard read 300/5.. Adrian Clarke found the breakthrough, Isaac Monroe departing for 2 to leave Ridge Falcons XI at 305/6.. Mason Reid broke through — Daniel Cross gone for 9. Ridge Falcons XI were 330/7.. The lower order flickered briefly — Liam Frost made 0 — but Ridge Falcons XI were 333/8 and the innings was nearly done.. The innings closed at 344 from 50.0 overs.. Coastal Meridian XI's bowling effort was led by Adrian Clarke, whose 3 for 72 made the deepest incisions. Evan Turner kept the pressure on with 2 for 61, and together they ensured no partnership could breathe.. The total included 20 extras, with 14 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 4 leg-byes also found their way into the score. The batters themselves accounted for 324. All told, the innings reached 344.. Set 344 to win, Coastal Meridian XI sent out Ethan Ward and Owen Hayes. The chase would test temperament as much as technique.. The chase took a hit when Owen Hayes fell to Noah Grant for 6. At 10/1, with 344 still needed, the pressure that had been theoretical was now real.. Mason Hart broke through — Aiden Price gone for 77. Coastal Meridian XI were 162/2 chasing 344, and the innings needed a partnership.. The chase took a hit when Ethan Ward fell to Mason Hart for 84. At 174/3, with 344 still needed, the pressure that had been theoretical was now real.. Noah Grant broke through — Dylan Brooks gone for 1. Coastal Meridian XI were 178/4 chasing 344, and the innings needed a partnership.. The chase took a hit when Ryan Cole fell to Noah Grant for 7. At 210/5, with 344 still needed, the pressure that had been theoretical was now real.. Daniel Cross broke through — Zane Foster gone for 11. Coastal Meridian XI were 228/6 chasing 344, and the innings needed a partnership.. The chase took a hit when Connor Wells fell to Caleb Rourke for 30. At 247/7, with 344 still needed, the pressure that had been theoretical was now real.. Noah Grant broke through — Lucas Reed gone for 5. Coastal Meridian XI were 259/8 chasing 344, and the innings needed a partnership.. The chase took a hit when Evan Turner fell to Caleb Rourke for 24. At 267/9, with 344 still needed, the pressure that had been theoretical was now real.. Aiden Price and Ethan Ward constructed 152 together. With Aiden Price contributing 77 and Ethan Ward adding 68, Coastal Meridian XI moved from 10/1 to 162/2. The target of 344 had come into view.. The stand that changed the chase came from Ethan Ward and Connor Wells. Their 12 — 12 from Ethan Ward, 0 from Connor Wells — carried Coastal Meridian XI from 162/2 to 174/3, transforming the equation.. Ryan Cole and Connor Wells constructed 32 together. With Ryan Cole contributing 7 and Connor Wells adding 23, Coastal Meridian XI moved from 178/4 to 210/5. The target of 344 had come into view.. Connor Wells and Evan Turner constructed 19 together. With Connor Wells contributing 0 and Evan Turner adding 17, Coastal Meridian XI moved from 228/6 to 247/7. The target of 344 had come into view.. The chase found its centre in Ethan Ward, whose 84 from 82 deliveries carried Coastal Meridian XI from uncertainty toward their target of 344. The 12 fours and 1 six were the visible markers of an innings built in stages.. Coastal Meridian XI closed on 279 for 10 from 46.2 overs, the 65 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 18: 14 wides, 0 no-balls, plus 2 byes and 2 leg-byes. The batters produced 261 between them. The bowling side's ledger showed 275 charged to the attack, the remainder of the 279 having arrived through routes that bypass the bowler's figures.. Ridge Falcons XI's bowling effort was led by Noah Grant, whose 4 for 62 made the deepest incisions. Caleb Rourke kept the pressure on with 2 for 41, and together they ensured no partnership could breathe.. Ridge Falcons XI Won by 65 Runs (Advanced), with Caleb Rourke recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Scorers' correction: Owen Hayes's dismissal, originally credited to Noah Grant, now belongs to Caleb Rourke. All other figures stand.
----- END TEXT -----
作答：
- Noah Grant_wickets_credited = ____ ；依据句：____
- Noah Grant_bowling_runs_conceded = ____ ；依据句：____
- Caleb Rourke_wickets_credited = ____ ；依据句：____
- Caleb Rourke_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0017 — Liam Reed — Miles Carter -> Liam Brooks
----- BEGIN TEXT -----
At North Ridge Oval, Hillview, Sandmere XI chose to field after winning the toss, reading conditions looked good for chasing. Ridgevale XI would bat first with Sandmere XI to chase.. Ridgevale XI began through Tariq Hale and Leo Mercer. The early exchanges set a tone of unforgiving, grinding.. Ryan Cole broke through — Tariq Hale gone for 5. Ridgevale XI were 9/1.. When Ishan Bell fell to Ryan Cole for 10, the scoreboard read 24/2.. Dylan Grant found the breakthrough, Leo Mercer departing for 24 to leave Ridgevale XI at 58/3.. A stand of 15 between Ishan Bell and Leo Mercer rebuilt the innings. The arithmetic was straightforward — 10 from Ishan Bell, 4 from Leo Mercer — and the scoreboard shifted from 9/1 to 24/2.. Cole Bennett and Leo Mercer constructed a repair worth 34. With Cole Bennett scoring 13 and Leo Mercer contributing 18, Ridgevale XI moved from 24/2 to 58/3.. A stand of 17 between Cole Bennett and Liam Brooks rebuilt the innings. The arithmetic was straightforward — 8 from Cole Bennett, 8 from Liam Brooks — and the scoreboard shifted from 58/3 to 75/4.. Cole Bennett and Evan Reed constructed a repair worth 18. With Cole Bennett scoring 6 and Evan Reed contributing 10, Ridgevale XI moved from 83/5 to 101/6.. A stand of 44 between Miles Carter and Mason Gray rebuilt the innings. The arithmetic was straightforward — 33 from Miles Carter, 8 from Mason Gray — and the scoreboard shifted from 130/9 to 174/10.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Miles Carter held firm, compiling 48 from 44 balls. The 6 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Ridgevale XI.. Ethan Parker broke through — Liam Brooks gone for 8. Ridgevale XI were 75/4.. When Arden Stone fell to Ethan Parker for 6, the scoreboard read 83/5.. Ethan Parker found the breakthrough, Cole Bennett departing for 29 to leave Ridgevale XI at 101/6.. Zach Foster broke through — Evan Reed gone for 12. Ridgevale XI were 109/7.. The lower order flickered briefly — Luke Barrett made 6 — but Ridgevale XI were 119/8 and the innings was nearly done.. The lower order flickered briefly — Dylan Frost made 5 — but Ridgevale XI were 130/9 and the innings was nearly done.. The lower order flickered briefly — Mason Gray made 8 — but Ridgevale XI were 174/10 and the innings was nearly done.. The innings closed at 174 from 43.5 overs.. Sandmere XI's bowling effort was led by Zach Foster, whose 4 for 46 made the deepest incisions. Ethan Parker kept the pressure on with 3 for 35, and together they ensured no partnership could breathe.. The total included 13 extras, with 9 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 2 leg-byes also found their way into the score. The batters themselves accounted for 161. All told, the innings reached 174.. Set 174 to win, Sandmere XI sent out Adrian Clarke and Nolan Price. The chase would test temperament as much as technique.. The chase took a hit when Adrian Clarke fell to Mason Gray for 10. At 16/1, with 174 still needed, the pressure that had been theoretical was now real.. Liam Brooks broke through — Caleb Turner gone for 8. Sandmere XI were 31/2 chasing 174, and the innings needed a partnership.. The chase took a hit when Mason Reid fell to Liam Brooks for 0. At 35/3, with 174 still needed, the pressure that had been theoretical was now real.. Miles Carter broke through — Nolan Price gone for 18. Sandmere XI were 39/4 chasing 174, and the innings needed a partnership.. The chase took a hit when Dylan Grant fell to Liam Brooks for 7. At 48/5, with 174 still needed, the pressure that had been theoretical was now real.. Miles Carter broke through — Connor Shaw gone for 6. Sandmere XI were 56/6 chasing 174, and the innings needed a partnership.. The chase took a hit when Zach Foster fell to Mason Gray for 14. At 83/7, with 174 still needed, the pressure that had been theoretical was now real.. Miles Carter broke through — Aiden Fox gone for 20. Sandmere XI were 94/8 chasing 174, and the innings needed a partnership.. The chase took a hit when Liam Reed fell to Miles Carter for 3. At 98/9, with 174 still needed, the pressure that had been theoretical was now real.. Nolan Price and Caleb Turner constructed 15 together. With Nolan Price contributing 6 and Caleb Turner adding 8, Sandmere XI moved from 16/1 to 31/2. The target of 174 had come into view.. The stand that changed the chase came from Zach Foster and Aiden Fox. Their 27 — 14 from Zach Foster, 11 from Aiden Fox — carried Sandmere XI from 56/6 to 83/7, transforming the equation.. Liam Reed and Aiden Fox constructed 11 together. With Liam Reed contributing 3 and Aiden Fox adding 6, Sandmere XI moved from 83/7 to 94/8. The target of 174 had come into view.. The chase found its centre in Aiden Fox, whose 20 from 25 deliveries carried Sandmere XI from uncertainty toward their target of 174. The 3 fours and 0 sixes were the visible markers of an innings built in stages.. Sandmere XI closed on 106 for 10 from 28.3 overs, the 68 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 10: 8 wides, 0 no-balls, plus 0 byes and 2 leg-byes. The batters produced 96 between them. The bowling side's ledger showed 104 charged to the attack, the remainder of the 106 having arrived through routes that bypass the bowler's figures.. Ridgevale XI's bowling effort was led by Miles Carter, whose 5 for 18 made the deepest incisions. Liam Brooks kept the pressure on with 3 for 27, and together they ensured no partnership could breathe.. Ridgevale XI Won by 68 Runs (Advanced), with Miles Carter recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. The review panel moved Liam Reed's dismissal from Miles Carter to Liam Brooks. All other figures stand.
----- END TEXT -----
作答：
- Miles Carter_wickets_credited = ____ ；依据句：____
- Miles Carter_bowling_runs_conceded = ____ ；依据句：____
- Liam Brooks_wickets_credited = ____ ；依据句：____
- Liam Brooks_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0026 — Ryan Hale — Dylan Cole -> Ben Carter
----- BEGIN TEXT -----
At Meadowbank Oval, Eastbridge, Ridgeport chose to bat after winning the toss, reading conditions looked good for chasing. Ridgeport would bat first with Coral Bay to chase.. Ridgeport began through Milo Grant and Nathan Wells. The early exchanges set a tone of decisive, clinical.. Toby Lane broke through — Milo Grant gone for 18. Ridgeport were 29/1.. When Leo Marsh fell to Jonah Price for 61, the scoreboard read 179/2.. Ryan Hale found the breakthrough, Nathan Wells departing for 116 to leave Ridgeport at 230/3.. Nathan Wells and Leo Marsh constructed a repair worth 150. With Nathan Wells scoring 76 and Leo Marsh contributing 61, Ridgeport moved from 29/1 to 179/2.. A stand of 51 between Connor Blake and Nathan Wells rebuilt the innings. The arithmetic was straightforward — 12 from Connor Blake, 33 from Nathan Wells — and the scoreboard shifted from 179/2 to 230/3.. Through the middle phase, Nathan Wells held firm, compiling 116 from 86 balls. The 10 boundaries and 2 sixes told only part of the story — the real value was the time he bought for Ridgeport.. Noah Finn broke through — Evan Brooks gone for 5. Ridgeport were 242/4.. The scoreboard was beginning to tell an uncomfortable story now.. The innings closed at 251 from 31.0 overs.. Coral Bay's bowling effort was led by Jonah Price, whose 1 for 24 made the deepest incisions. Noah Finn kept the pressure on with 1 for 38, and together they ensured no partnership could breathe.. The total included 24 extras, with 19 wides and 3 no-balls coming directly from the bowlers' accounts. Another 1 by and 1 leg-bye also found their way into the score. The batters themselves accounted for 227. All told, the innings reached 251.. Set 251 to win, Coral Bay sent out Toby Lane and Caleb Stone. The chase would test temperament as much as technique.. The chase took a hit when Caleb Stone fell to Lucas Barrett for 1. At 11/1, with 251 still needed, the pressure that had been theoretical was now real.. Ben Carter broke through — Toby Lane gone for 4. Coral Bay were 13/2 chasing 251, and the innings needed a partnership.. The chase took a hit when Owen Reed fell to Ben Carter for 7. At 19/3, with 251 still needed, the pressure that had been theoretical was now real.. Dylan Cole broke through — Noah Finn gone for 0. Coral Bay were 21/4 chasing 251, and the innings needed a partnership.. The chase took a hit when Ryan Hale fell to Dylan Cole for 0. At 21/5, with 251 still needed, the pressure that had been theoretical was now real.. Dylan Cole broke through — Liam Turner gone for 0. Coral Bay were 21/6 chasing 251, and the innings needed a partnership.. The chase took a hit when Aiden Cole fell to a bowler for 2. At 25/7, with 251 still needed, the pressure that had been theoretical was now real.. Dylan Cole broke through — Ethan Parker gone for 0. Coral Bay were 25/8 chasing 251, and the innings needed a partnership.. The chase took a hit when Mason Reed fell to Dylan Cole for 1. At 27/9, with 251 still needed, the pressure that had been theoretical was now real.. Coral Bay closed on 33 for 10 from 17.5 overs, the 218 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 13: 12 wides, 1 no-ball, plus 0 byes and 0 leg-byes. The batters produced 20 between them. The bowling side's ledger showed 33 charged to the attack, the remainder of the 33 having arrived through routes that bypass the bowler's figures.. Ridgeport's bowling effort was led by Dylan Cole, whose 5 for 5 made the deepest incisions. Ben Carter kept the pressure on with 2 for 5, and together they ensured no partnership could breathe.. Ridgeport Won by 218 Runs, with Nathan Wells recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Ryan Hale in the second innings was reassigned from Dylan Cole to Ben Carter. All other figures stand.
----- END TEXT -----
作答：
- Dylan Cole_wickets_credited = ____ ；依据句：____
- Dylan Cole_bowling_runs_conceded = ____ ；依据句：____
- Ben Carter_wickets_credited = ____ ；依据句：____
- Ben Carter_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0030 — Ben Carter — Logan Vale -> Owen Price
----- BEGIN TEXT -----
At Meadow Park Oval, Westhaven, Lagoon chose to bat after winning the toss, reading conditions looked good for chasing. Lagoon would bat first with Harborfield to chase.. Lagoon began through Daniel Marsh and Leo Turner. The early exchanges set a tone of decisive, clinical.. Connor Blake broke through — Leo Turner gone for 1. Lagoon were 9/1.. When Isaac Shaw fell to Caleb Hart for 12, the scoreboard read 33/2.. Noah Reed found the breakthrough, Daniel Marsh departing for 7 to leave Lagoon at 34/3.. A stand of 24 between Daniel Marsh and Isaac Shaw rebuilt the innings. The arithmetic was straightforward — 7 from Daniel Marsh, 9 from Isaac Shaw — and the scoreboard shifted from 9/1 to 33/2.. Caleb Hart broke through — Tyler Brooks gone for 5. Lagoon were 41/4.. When Ben Carter fell to Logan Vale for 0, the scoreboard read 43/5.. Logan Vale found the breakthrough, Aaron Price departing for 0 to leave Lagoon at 44/6.. Logan Vale broke through — Evan Reid gone for 3. Lagoon were 48/7.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. The lower order flickered briefly — Luke Barrett made 1 — but Lagoon were 49/8 and the innings was nearly done.. The lower order flickered briefly — Nathan Cole made 0 — but Lagoon were 49/9 and the innings was nearly done.. The lower order flickered briefly — Dylan Grant made 1 — but Lagoon were 52/10 and the innings was nearly done.. The innings closed at 52 from 19.2 overs.. Harborfield's bowling effort was led by Logan Vale, whose 4 for 10 made the deepest incisions. Owen Price kept the pressure on with 2 for 1, and together they ensured no partnership could breathe.. The total included 21 extras, with 19 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 0 leg-byes also found their way into the score. The batters themselves accounted for 31. All told, the innings reached 52.. Set 52 to win, Harborfield sent out Liam Foster and Mason Shaw. The chase would test temperament as much as technique.. The chase found its centre in Liam Foster, whose 22 from 25 deliveries carried Harborfield from uncertainty toward their target of 52. The 1 four and 0 sixes were the visible markers of an innings built in stages.. Harborfield closed on 53 for 1 from 8.1 over, the 9 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 12: 12 wides, 0 no-balls, plus 0 byes and 0 leg-byes. The batters produced 41 between them. The bowling side's ledger showed 53 charged to the attack, the remainder of the 53 having arrived through routes that bypass the bowler's figures.. Harborfield Won by 9 Wickets, with Logan Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Scorers' correction: Ben Carter's dismissal, originally credited to Logan Vale, now belongs to Owen Price. All other figures stand.
----- END TEXT -----
作答：
- Logan Vale_wickets_credited = ____ ；依据句：____
- Logan Vale_bowling_runs_conceded = ____ ；依据句：____
- Owen Price_wickets_credited = ____ ；依据句：____
- Owen Price_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0009 — Dylan Shaw — Tyler Grant -> Luke Barrett
----- BEGIN TEXT -----
At Eastbank Meadow Ground, Hillview, Coral Bay XI chose to field after winning the toss, reading conditions looked good for chasing. Ridgewater XI would bat first with Coral Bay XI to chase.. Ridgewater XI began through Tyler Grant and Ben Carter. The early exchanges set a tone of unforgiving, grinding.. Zane Foster broke through — Ben Carter gone for 5. Ridgewater XI were 9/1.. When Isaac Nolan fell to Evan Turner for 8, the scoreboard read 25/2.. Evan Turner found the breakthrough, Connor Vale departing for 4 to leave Ridgewater XI at 32/3.. A stand of 16 between Isaac Nolan and Tyler Grant rebuilt the innings. The arithmetic was straightforward — 8 from Isaac Nolan, 6 from Tyler Grant — and the scoreboard shifted from 9/1 to 25/2.. Tyler Grant and Caleb Marsh constructed a repair worth 52. With Tyler Grant scoring 16 and Caleb Marsh contributing 31, Ridgewater XI moved from 32/3 to 84/4.. A stand of 24 between Tyler Grant and Leo Turner rebuilt the innings. The arithmetic was straightforward — 12 from Tyler Grant, 10 from Leo Turner — and the scoreboard shifted from 105/6 to 129/7.. Ryan Cole and Leo Turner constructed a repair worth 17. With Ryan Cole scoring 8 and Leo Turner contributing 7, Ridgewater XI moved from 129/8 to 146/9.. A stand of 38 between Mason Hart and Leo Turner rebuilt the innings. The arithmetic was straightforward — 19 from Mason Hart, 17 from Leo Turner — and the scoreboard shifted from 146/9 to 184/10.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Tyler Grant held firm, compiling 39 from 76 balls. The 3 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Ridgewater XI.. Connor Blake broke through — Caleb Marsh gone for 31. Ridgewater XI were 84/4.. When Aaron Holt fell to Connor Blake for 10, the scoreboard read 96/5.. Noah Reed found the breakthrough, Luca Barrett departing for 7 to leave Ridgewater XI at 105/6.. Noah Reed broke through — Tyler Grant gone for 39. Ridgewater XI were 129/7.. The lower order flickered briefly — Liam Frost made 0 — but Ridgewater XI were 129/8 and the innings was nearly done.. The lower order flickered briefly — Ryan Cole made 8 — but Ridgewater XI were 146/9 and the innings was nearly done.. The lower order flickered briefly — Leo Turner made 34 — but Ridgewater XI were 184/10 and the innings was nearly done.. The innings closed at 184 from 46.5 overs.. Coral Bay XI's bowling effort was led by Noah Reed, whose 3 for 18 made the deepest incisions. Zane Foster kept the pressure on with 2 for 30, and together they ensured no partnership could breathe.. The total included 19 extras, with 14 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 165. All told, the innings reached 184.. Set 184 to win, Coral Bay XI sent out Ethan Ward and Owen Hayes. The chase would test temperament as much as technique.. The chase took a hit when Ethan Ward fell to Luke Barrett for 50. At 78/1, with 184 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Owen Hayes gone for 40. Coral Bay XI were 109/2 chasing 184, and the innings needed a partnership.. The chase took a hit when Dylan Shaw fell to Tyler Grant for 7. At 124/3, with 184 still needed, the pressure that had been theoretical was now real.. Tyler Grant broke through — Caleb Brooks gone for 16. Coral Bay XI were 158/4 chasing 184, and the innings needed a partnership.. Owen Hayes and Aiden Price constructed 31 together. With Owen Hayes contributing 19 and Aiden Price adding 11, Coral Bay XI moved from 78/1 to 109/2. The target of 184 had come into view.. The stand that changed the chase came from Dylan Shaw and Aiden Price. Their 15 — 7 from Dylan Shaw, 7 from Aiden Price — carried Coral Bay XI from 109/2 to 124/3, transforming the equation.. Caleb Brooks and Aiden Price constructed 34 together. With Caleb Brooks contributing 16 and Aiden Price adding 15, Coral Bay XI moved from 124/3 to 158/4. The target of 184 had come into view.. The chase found its centre in Ethan Ward, whose 50 from 44 deliveries carried Coral Bay XI from uncertainty toward their target of 184. The 8 fours and 0 sixes were the visible markers of an innings built in stages.. Coral Bay XI closed on 187 for 5 from 34.2 overs, the 5 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 13: 11 wides, 1 no-ball, plus 0 byes and 1 leg-bye. The batters produced 174 between them. The bowling side's ledger showed 186 charged to the attack, the remainder of the 187 having arrived through routes that bypass the bowler's figures.. Ridgewater XI's bowling effort was led by Tyler Grant, whose 2 for 25 made the deepest incisions. Luke Barrett kept the pressure on with 2 for 43, and together they ensured no partnership could breathe.. Coral Bay XI Won by 5 Wickets, with Noah Reed recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Dylan Shaw in the second innings was reassigned from Tyler Grant to Luke Barrett. All other figures stand.
----- END TEXT -----
作答：
- Tyler Grant_wickets_credited = ____ ；依据句：____
- Tyler Grant_bowling_runs_conceded = ____ ；依据句：____
- Luke Barrett_wickets_credited = ____ ；依据句：____
- Luke Barrett_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0013 — Leo Warren — Evan Turner -> Zane Carter
----- BEGIN TEXT -----
At Eastbank Meadow Ground, Hillview, Mirage Lions XI chose to field after winning the toss, reading conditions looked good for chasing. Silver Pearl XI would bat first with Mirage Lions XI to chase.. Silver Pearl XI began through Tyler Marsh and Leo Warren. The early exchanges set a tone of tense, fluctuating.. Zane Carter broke through — Tyler Marsh gone for 5. Silver Pearl XI were 8/1.. When Leo Warren fell to Evan Turner for 24, the scoreboard read 50/2.. Connor Vale found the breakthrough, Isaac Hale departing for 36 to leave Silver Pearl XI at 116/3.. A stand of 42 between Isaac Hale and Leo Warren rebuilt the innings. The arithmetic was straightforward — 15 from Isaac Hale, 22 from Leo Warren — and the scoreboard shifted from 8/1 to 50/2.. Isaac Hale and Connor Wells constructed a repair worth 66. With Isaac Hale scoring 21 and Connor Wells contributing 41, Silver Pearl XI moved from 50/2 to 116/3.. A stand of 15 between Aaron Blake and Connor Wells rebuilt the innings. The arithmetic was straightforward — 13 from Aaron Blake, 0 from Connor Wells — and the scoreboard shifted from 116/3 to 131/4.. Aaron Blake and Caleb Shaw constructed a repair worth 70. With Aaron Blake scoring 34 and Caleb Shaw contributing 34, Silver Pearl XI moved from 131/4 to 201/5.. A stand of 18 between Luke Barrett and Aaron Blake rebuilt the innings. The arithmetic was straightforward — 17 from Luke Barrett, 0 from Aaron Blake — and the scoreboard shifted from 201/5 to 219/6.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Ryan Foster and Luke Barrett constructed a repair worth 36. With Ryan Foster scoring 12 and Luke Barrett contributing 23, Silver Pearl XI moved from 219/6 to 255/7.. Through the middle phase, Aaron Blake held firm, compiling 47 from 49 balls. The 4 boundaries and 2 sixes told only part of the story — the real value was the time he bought for Silver Pearl XI.. Caleb Brooks broke through — Connor Wells gone for 41. Silver Pearl XI were 131/4.. When Caleb Shaw fell to Evan Turner for 34, the scoreboard read 201/5.. Evan Turner found the breakthrough, Aaron Blake departing for 47 to leave Silver Pearl XI at 219/6.. Connor Vale broke through — Luke Barrett gone for 40. Silver Pearl XI were 255/7.. The lower order flickered briefly — Liam Foster made 3 — but Silver Pearl XI were 263/8 and the innings was nearly done.. The innings closed at 263 from 50.0 overs.. Mirage Lions XI's bowling effort was led by Evan Turner, whose 3 for 70 made the deepest incisions. Zane Carter kept the pressure on with 2 for 58, and together they ensured no partnership could breathe.. The total included 17 extras, with 12 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 246. All told, the innings reached 263.. Set 263 to win, Mirage Lions XI sent out Ethan Ward and Aiden Price. The chase would test temperament as much as technique.. The chase took a hit when Aiden Price fell to Evan Reed for 23. At 70/1, with 263 still needed, the pressure that had been theoretical was now real.. Evan Reed broke through — Ethan Ward gone for 52. Mirage Lions XI were 90/2 chasing 263, and the innings needed a partnership.. The chase took a hit when Owen Hayes fell to a bowler for 12. At 112/3, with 263 still needed, the pressure that had been theoretical was now real.. Luke Barrett broke through — Liam Parker gone for 45. Mirage Lions XI were 205/4 chasing 263, and the innings needed a partnership.. The chase took a hit when Lucas Reed fell to Connor Wells for 8. At 217/5, with 263 still needed, the pressure that had been theoretical was now real.. Ryan Foster broke through — Caleb Brooks gone for 20. Mirage Lions XI were 246/6 chasing 263, and the innings needed a partnership.. Ethan Ward and Liam Parker constructed 20 together. With Ethan Ward contributing 12 and Liam Parker adding 6, Mirage Lions XI moved from 70/1 to 90/2. The target of 263 had come into view.. The stand that changed the chase came from Owen Hayes and Liam Parker. Their 22 — 12 from Owen Hayes, 9 from Liam Parker — carried Mirage Lions XI from 90/2 to 112/3, transforming the equation.. Liam Parker and Connor Vale constructed 93 together. With Liam Parker contributing 30 and Connor Vale adding 59, Mirage Lions XI moved from 112/3 to 205/4. The target of 263 had come into view.. Caleb Brooks and Connor Vale constructed 29 together. With Caleb Brooks contributing 20 and Connor Vale adding 8, Mirage Lions XI moved from 217/5 to 246/6. The target of 263 had come into view.. The chase found its centre in Connor Vale, whose 72 from 83 deliveries carried Mirage Lions XI from uncertainty toward their target of 263. The 4 fours and 1 six were the visible markers of an innings built in stages.. Mirage Lions XI closed on 264 for 7 from 46.2 overs, the 3 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 18: 12 wides, 1 no-ball, plus 1 by and 4 leg-byes. The batters produced 246 between them. The bowling side's ledger showed 259 charged to the attack, the remainder of the 264 having arrived through routes that bypass the bowler's figures.. Silver Pearl XI's bowling effort was led by Evan Reed, whose 2 for 50 made the deepest incisions. Connor Wells kept the pressure on with 1 for 13, and together they ensured no partnership could breathe.. Mirage Lions XI Won by 3 Wickets, with Connor Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Leo Warren in the first innings was reassigned from Evan Turner to Zane Carter. All other figures stand.
----- END TEXT -----
作答：
- Evan Turner_wickets_credited = ____ ；依据句：____
- Evan Turner_bowling_runs_conceded = ____ ；依据句：____
- Zane Carter_wickets_credited = ____ ；依据句：____
- Zane Carter_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0014 — Elias Ward — Leo Quinn -> Dylan Frost
----- BEGIN TEXT -----
At East Ridge Cricket Ground, Hillview, Canyon Stars XI chose to bat after winning the toss, reading conditions looked good for chasing. Canyon Stars XI would bat first with Harbor Peninsula XI to chase.. Canyon Stars XI began through Adrian Vale and Nolan Greer. The early exchanges set a tone of tense, fluctuating.. Rafi Cole broke through — Adrian Vale gone for 12. Canyon Stars XI were 24/1.. When Nolan Greer fell to Mason Hart for 18, the scoreboard read 39/2.. Owen Shaw found the breakthrough, Mason Kline departing for 27 to leave Canyon Stars XI at 108/3.. Nolan Greer and Caleb Rowan constructed a repair worth 15. With Nolan Greer scoring 8 and Caleb Rowan contributing 6, Canyon Stars XI moved from 24/1 to 39/2.. A stand of 69 between Caleb Rowan and Mason Kline rebuilt the innings. The arithmetic was straightforward — 35 from Caleb Rowan, 27 from Mason Kline — and the scoreboard shifted from 39/2 to 108/3.. Aiden Knox and Caleb Rowan constructed a repair worth 40. With Aiden Knox scoring 25 and Caleb Rowan contributing 12, Canyon Stars XI moved from 121/4 to 161/5.. A stand of 46 between Aiden Knox and Dylan Frost rebuilt the innings. The arithmetic was straightforward — 12 from Aiden Knox, 30 from Dylan Frost — and the scoreboard shifted from 161/5 to 207/6.. Through the middle phase, Caleb Rowan held firm, compiling 57 from 67 balls. The 6 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Canyon Stars XI.. Lucas Vale broke through — Connor Shaw gone for 9. Canyon Stars XI were 121/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Caleb Rowan fell to Mason Hart for 57, the scoreboard read 161/5.. Zane Perry found the breakthrough, Dylan Frost departing for 30 to leave Canyon Stars XI at 207/6.. Zane Perry broke through — Aiden Knox gone for 41. Canyon Stars XI were 212/7.. The lower order flickered briefly — Evan Hale made 4 — but Canyon Stars XI were 225/8 and the innings was nearly done.. The innings closed at 225 from 36.0 overs.. Harbor Peninsula XI's bowling effort was led by Zane Perry, whose 2 for 47 made the deepest incisions. Mason Hart kept the pressure on with 2 for 48, and together they ensured no partnership could breathe.. The total included 17 extras, with 12 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 3 leg-byes also found their way into the score. The batters themselves accounted for 208. All told, the innings reached 225.. Set 225 to win, Harbor Peninsula XI sent out Elias Ward and Oliver Hayes. The chase would test temperament as much as technique.. The chase took a hit when Elias Ward fell to Leo Quinn for 4. At 6/1, with 225 still needed, the pressure that had been theoretical was now real.. Mason Kline broke through — Oliver Hayes gone for 10. Harbor Peninsula XI were 26/2 chasing 225, and the innings needed a partnership.. The chase took a hit when Caleb Brook fell to Ryan Wells for 34. At 61/3, with 225 still needed, the pressure that had been theoretical was now real.. Nolan Greer broke through — Rafi Cole gone for 21. Harbor Peninsula XI were 101/4 chasing 225, and the innings needed a partnership.. The chase took a hit when Dylan Shaw fell to Dylan Frost for 26. At 181/5, with 225 still needed, the pressure that had been theoretical was now real.. Dylan Frost broke through — Aiden Mercer gone for 79. Harbor Peninsula XI were 186/6 chasing 225, and the innings needed a partnership.. The stand that changed the chase came from Caleb Brook and Oliver Hayes. Their 20 — 12 from Caleb Brook, 8 from Oliver Hayes — carried Harbor Peninsula XI from 6/1 to 26/2, transforming the equation.. Caleb Brook and Rafi Cole constructed 35 together. With Caleb Brook contributing 22 and Rafi Cole adding 12, Harbor Peninsula XI moved from 26/2 to 61/3. The target of 225 had come into view.. Dylan Shaw and Aiden Mercer constructed 80 together. With Dylan Shaw contributing 26 and Aiden Mercer adding 49, Harbor Peninsula XI moved from 101/4 to 181/5. The target of 225 had come into view.. The chase found its centre in Aiden Mercer, whose 79 from 66 deliveries carried Harbor Peninsula XI from uncertainty toward their target of 225. The 6 fours and 2 sixes were the visible markers of an innings built in stages.. Harbor Peninsula XI closed on 226 for 7 from 35.2 overs, the 3 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 15: 11 wides, 1 no-ball, plus 1 by and 2 leg-byes. The batters produced 211 between them. The bowling side's ledger showed 223 charged to the attack, the remainder of the 226 having arrived through routes that bypass the bowler's figures.. Canyon Stars XI's bowling effort was led by Leo Quinn, whose 2 for 36 made the deepest incisions. Dylan Frost kept the pressure on with 2 for 39, and together they ensured no partnership could breathe.. Harbor Peninsula XI Won by 3 Wickets, with Aiden Mercer recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Elias Ward in the second innings was reassigned from Leo Quinn to Dylan Frost. All other figures stand.
----- END TEXT -----
作答：
- Leo Quinn_wickets_credited = ____ ；依据句：____
- Leo Quinn_bowling_runs_conceded = ____ ；依据句：____
- Dylan Frost_wickets_credited = ____ ；依据句：____
- Dylan Frost_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0016 — Adrian Clarke — Evan Reed -> Connor Wells
----- BEGIN TEXT -----
At Crestfield North Oval, Hillview, Pearlbridge XI chose to bat after winning the toss, reading conditions looked good for chasing. Pearlbridge XI would bat first with Crestline XI to chase.. Pearlbridge XI began through Toby Lane and Leon Ward. The early exchanges set a tone of dramatic, redemptive.. Zane Harrow broke through — Leon Ward gone for 6. Pearlbridge XI were 24/1.. When Isaac Bell fell to Connor Shaw for 2, the scoreboard read 29/2.. Connor Shaw found the breakthrough, Conor Hale departing for 4 to leave Pearlbridge XI at 34/3.. Caleb Stone and Evan Reed constructed a repair worth 34. With Caleb Stone scoring 15 and Evan Reed contributing 15, Pearlbridge XI moved from 50/5 to 84/6.. A stand of 27 between Caleb Stone and Luke Mercer rebuilt the innings. The arithmetic was straightforward — 9 from Caleb Stone, 17 from Luke Mercer — and the scoreboard shifted from 84/6 to 111/7.. Dylan Brooks and Mason Hart constructed a repair worth 22. With Dylan Brooks scoring 2 and Mason Hart contributing 18, Pearlbridge XI moved from 114/9 to 136/10.. Through the middle phase, Caleb Stone held firm, compiling 31 from 52 balls. The 4 boundaries and 0 sixes told only part of the story — the real value was the time he bought for Pearlbridge XI.. Zane Harrow broke through — Toby Lane gone for 20. Pearlbridge XI were 42/4.. When Arden Vale fell to Liam Reed for 7, the scoreboard read 50/5.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Connor Shaw found the breakthrough, Evan Reed departing for 15 to leave Pearlbridge XI at 84/6.. Zane Harrow broke through — Caleb Stone gone for 31. Pearlbridge XI were 111/7.. The lower order flickered briefly — Ryan Frost made 1 — but Pearlbridge XI were 112/8 and the innings was nearly done.. The lower order flickered briefly — Luke Mercer made 18 — but Pearlbridge XI were 114/9 and the innings was nearly done.. The lower order flickered briefly — Dylan Brooks made 2 — but Pearlbridge XI were 136/10 and the innings was nearly done.. The innings closed at 136 from 42.3 overs.. Crestline XI's bowling effort was led by Zane Harrow, whose 4 for 13 made the deepest incisions. Connor Shaw kept the pressure on with 2 for 20, and together they ensured no partnership could breathe.. The total included 12 extras, with 9 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 1 leg-bye also found their way into the score. The batters themselves accounted for 124. All told, the innings reached 136.. Set 136 to win, Crestline XI sent out Nolan Price and Adrian Clarke. The chase would test temperament as much as technique.. The chase took a hit when Adrian Clarke fell to Evan Reed for 4. At 11/1, with 136 still needed, the pressure that had been theoretical was now real.. Evan Reed broke through — Nolan Price gone for 9. Crestline XI were 32/2 chasing 136, and the innings needed a partnership.. Caleb Turner and Nolan Price constructed 21 together. With Caleb Turner contributing 17 and Nolan Price adding 3, Crestline XI moved from 11/1 to 32/2. The target of 136 had come into view.. The chase found its centre in Caleb Turner, whose 61 from 85 deliveries carried Crestline XI from uncertainty toward their target of 136. The 5 fours and 1 six were the visible markers of an innings built in stages.. Crestline XI closed on 138 for 3 from 30.1 over, the 7 wickets margin reflecting a chase that had been tested but never broken.. The sundries column read 7: 5 wides, 0 no-balls, plus 0 byes and 2 leg-byes. The batters produced 131 between them. The bowling side's ledger showed 136 charged to the attack, the remainder of the 138 having arrived through routes that bypass the bowler's figures.. Pearlbridge XI's bowling effort was led by Evan Reed, whose 2 for 31 made the deepest incisions. Connor Wells kept the pressure on with 1 for 14, and together they ensured no partnership could breathe.. Crestline XI Won by 7 Wickets, with Zane Harrow recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Adrian Clarke in the second innings was reassigned from Evan Reed to Connor Wells. All other figures stand.
----- END TEXT -----
作答：
- Evan Reed_wickets_credited = ____ ；依据句：____
- Evan Reed_bowling_runs_conceded = ____ ；依据句：____
- Connor Wells_wickets_credited = ____ ；依据句：____
- Connor Wells_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0018 — Ethan Blake — Dylan Fox -> Ben Turner
----- BEGIN TEXT -----
At North Ridge Stadium, Hillview, Harborline XI chose to field after winning the toss, reading conditions looked good for chasing. Dunecrest XI would bat first with Harborline XI to chase.. Dunecrest XI began through Kieran Shaw and Aaron Hale. The early exchanges set a tone of constructive, building.. Caleb Turner broke through — Aaron Hale gone for 4. Dunecrest XI were 8/1.. When Isaac Rowe fell to Noah Grant for 7, the scoreboard read 23/2.. Ryan Cross found the breakthrough, Kieran Shaw departing for 45 to leave Dunecrest XI at 81/3.. A stand of 15 between Isaac Rowe and Kieran Shaw rebuilt the innings. The arithmetic was straightforward — 7 from Isaac Rowe, 7 from Kieran Shaw — and the scoreboard shifted from 8/1 to 23/2.. Daniel Mercer and Kieran Shaw constructed a repair worth 58. With Daniel Mercer scoring 22 and Kieran Shaw contributing 34, Dunecrest XI moved from 23/2 to 81/3.. A stand of 55 between Daniel Mercer and Mason Vale rebuilt the innings. The arithmetic was straightforward — 15 from Daniel Mercer, 38 from Mason Vale — and the scoreboard shifted from 85/4 to 140/5.. Mason Vale and Leo Bennett constructed a repair worth 96. With Mason Vale scoring 34 and Leo Bennett contributing 54, Dunecrest XI moved from 140/5 to 236/6.. A stand of 31 between Mason Vale and Zane Price rebuilt the innings. The arithmetic was straightforward — 5 from Mason Vale, 24 from Zane Price — and the scoreboard shifted from 236/6 to 267/7.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. Through the middle phase, Mason Vale held firm, compiling 78 from 92 balls. The 6 boundaries and 1 six told only part of the story — the real value was the time he bought for Dunecrest XI.. Owen Foster broke through — Evan Hart gone for 2. Dunecrest XI were 85/4.. When Daniel Mercer fell to Liam Brooks for 39, the scoreboard read 140/5.. Owen Foster found the breakthrough, Leo Bennett departing for 54 to leave Dunecrest XI at 236/6.. Noah Grant broke through — Zane Price gone for 24. Dunecrest XI were 267/7.. The lower order flickered briefly — Mason Vale made 78 — but Dunecrest XI were 280/8 and the innings was nearly done.. The innings closed at 288 from 50.0 overs.. Harborline XI's bowling effort was led by Owen Foster, whose 3 for 49 made the deepest incisions. Noah Grant kept the pressure on with 1 for 30, and together they ensured no partnership could breathe.. The total included 18 extras, with 11 wides and 1 no-ball coming directly from the bowlers' accounts. Another 1 by and 5 leg-byes also found their way into the score. The batters themselves accounted for 270. All told, the innings reached 288.. Set 288 to win, Harborline XI sent out Adrian Cole and Ethan Blake. The chase would test temperament as much as technique.. The chase took a hit when Ethan Blake fell to Dylan Fox for 12. At 28/1, with 288 still needed, the pressure that had been theoretical was now real.. Ben Turner broke through — Mason Reed gone for 4. Harborline XI were 36/2 chasing 288, and the innings needed a partnership.. The chase took a hit when Connor Hayes fell to Mason Vale for 17. At 67/3, with 288 still needed, the pressure that had been theoretical was now real.. Ben Turner broke through — Luke Parker gone for 49. Harborline XI were 155/4 chasing 288, and the innings needed a partnership.. The chase took a hit when Adrian Cole fell to Zane Price for 61. At 160/5, with 288 still needed, the pressure that had been theoretical was now real.. Dylan Fox broke through — Dylan Price gone for 21. Harborline XI were 208/6 chasing 288, and the innings needed a partnership.. The chase took a hit when Noah Grant fell to Tyler Shaw for 10. At 223/7, with 288 still needed, the pressure that had been theoretical was now real.. Tyler Shaw broke through — Owen Foster gone for 3. Harborline XI were 228/8 chasing 288, and the innings needed a partnership.. The chase took a hit when Ryan Cross fell to Dylan Fox for 39. At 244/9, with 288 still needed, the pressure that had been theoretical was now real.. Adrian Cole and Connor Hayes constructed 31 together. With Adrian Cole contributing 10 and Connor Hayes adding 17, Harborline XI moved from 36/2 to 67/3. The target of 288 had come into view.. The stand that changed the chase came from Luke Parker and Adrian Cole. Their 88 — 49 from Luke Parker, 37 from Adrian Cole — carried Harborline XI from 67/3 to 155/4, transforming the equation.. Ryan Cross and Dylan Price constructed 48 together. With Ryan Cross contributing 22 and Dylan Price adding 21, Harborline XI moved from 160/5 to 208/6. The target of 288 had come into view.. Caleb Turner and Ryan Cross constructed 16 together. With Caleb Turner contributing 10 and Ryan Cross adding 6, Harborline XI moved from 228/8 to 244/9. The target of 288 had come into view.. The chase found its centre in Adrian Cole, whose 61 from 92 deliveries carried Harborline XI from uncertainty toward their target of 288. The 2 fours and 2 sixes were the visible markers of an innings built in stages.. Harborline XI closed on 252 for 10 from 49.2 overs, the 36 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 19: 13 wides, 1 no-ball, plus 3 byes and 2 leg-byes. The batters produced 233 between them. The bowling side's ledger showed 247 charged to the attack, the remainder of the 252 having arrived through routes that bypass the bowler's figures.. Dunecrest XI's bowling effort was led by Dylan Fox, whose 3 for 34 made the deepest incisions. Ben Turner kept the pressure on with 2 for 35, and together they ensured no partnership could breathe.. Dunecrest XI Won by 36 Runs, with Mason Vale recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Ethan Blake in the second innings was reassigned from Dylan Fox to Ben Turner. All other figures stand.
----- END TEXT -----
作答：
- Dylan Fox_wickets_credited = ____ ；依据句：____
- Dylan Fox_bowling_runs_conceded = ____ ；依据句：____
- Ben Turner_wickets_credited = ____ ；依据句：____
- Ben Turner_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____

## match_0027 — Aaron Reed — Owen Price -> Adam Wells
----- BEGIN TEXT -----
At Meadow Park Oval, Westhaven, Seabrook chose to bat after winning the toss, reading conditions looked good for chasing. Seabrook would bat first with Highland Isle to chase.. Seabrook began through Liam Carter and Noah Brooks. The early exchanges set a tone of decisive, clinical.. Daniel Marsh broke through — Liam Carter gone for 12. Seabrook were 24/1.. When Ethan Clarke fell to Evan Reid for 127, the scoreboard read 225/2.. Isaac Hale found the breakthrough, Noah Brooks departing for 74 to leave Seabrook at 248/3.. Ethan Clarke and Noah Brooks constructed a repair worth 201. With Ethan Clarke scoring 127 and Noah Brooks contributing 53, Seabrook moved from 24/1 to 225/2.. A stand of 23 between Lucas Grant and Noah Brooks rebuilt the innings. The arithmetic was straightforward — 9 from Lucas Grant, 12 from Noah Brooks — and the scoreboard shifted from 225/2 to 248/3.. Ryan Cole and Lucas Grant constructed a repair worth 33. With Ryan Cole scoring 13 and Lucas Grant contributing 19, Seabrook moved from 248/3 to 281/4.. A stand of 15 between Mason Shaw and Ryan Cole rebuilt the innings. The arithmetic was straightforward — 5 from Mason Shaw, 3 from Ryan Cole — and the scoreboard shifted from 281/4 to 296/5.. Through the middle phase, Ethan Clarke held firm, compiling 127 from 75 balls. The 15 boundaries and 5 sixes told only part of the story — the real value was the time he bought for Seabrook.. Daniel Marsh broke through — Lucas Grant gone for 28. Seabrook were 281/4.. At last, a stand with some glue in it. The kind that makes you glance at the scoreboard and recalculate what is possible.. When Ryan Cole fell to Ben Turner for 16, the scoreboard read 296/5.. The innings closed at 304 from 34.0 overs.. Highland Isle's bowling effort was led by Daniel Marsh, whose 2 for 45 made the deepest incisions. Ben Turner kept the pressure on with 1 for 42, and together they ensured no partnership could breathe.. The total included 35 extras, with 28 wides and 2 no-balls coming directly from the bowlers' accounts. Another 3 byes and 2 leg-byes also found their way into the score. The batters themselves accounted for 269. All told, the innings reached 304.. Set 304 to win, Highland Isle sent out Oliver Stone and Daniel Marsh. The chase would test temperament as much as technique.. The chase took a hit when Daniel Marsh fell to Connor Blake for 3. At 7/1, with 304 still needed, the pressure that had been theoretical was now real.. Connor Blake broke through — Ben Turner gone for 6. Highland Isle were 17/2 chasing 304, and the innings needed a partnership.. The chase took a hit when Zach Field fell to Caleb Reed for 0. At 21/3, with 304 still needed, the pressure that had been theoretical was now real.. Owen Price broke through — Oliver Stone gone for 5. Highland Isle were 29/4 chasing 304, and the innings needed a partnership.. The chase took a hit when Aaron Reed fell to Owen Price for 1. At 32/5, with 304 still needed, the pressure that had been theoretical was now real.. Adam Wells broke through — Evan Reid gone for 0. Highland Isle were 37/6 chasing 304, and the innings needed a partnership.. The chase took a hit when Dylan Price fell to a bowler for 2. At 41/7, with 304 still needed, the pressure that had been theoretical was now real.. Caleb Reed broke through — Leo Parker gone for 4. Highland Isle were 47/8 chasing 304, and the innings needed a partnership.. The chase took a hit when Isaac Hale fell to Adam Wells for 12. At 49/9, with 304 still needed, the pressure that had been theoretical was now real.. The stand that changed the chase came from Oliver Stone and Ben Turner. Their 10 — 1 from Oliver Stone, 6 from Ben Turner — carried Highland Isle from 7/1 to 17/2, transforming the equation.. Highland Isle closed on 52 for 10 from 19.2 overs, the 252 runs margin reflecting a chase that had been tested but never broken.. The sundries column read 16: 10 wides, 1 no-ball, plus 4 byes and 1 leg-bye. The batters produced 36 between them. The bowling side's ledger showed 47 charged to the attack, the remainder of the 52 having arrived through routes that bypass the bowler's figures.. Seabrook's bowling effort was led by Owen Price, whose 3 for 14 made the deepest incisions. Adam Wells kept the pressure on with 2 for 9, and together they ensured no partnership could breathe.. Seabrook Won by 252 Runs, with Ethan Clarke recognised as Player of the Match after a performance that influenced both halves of the contest. Note: the bowling figures above are the pre-revision record. Match review: the dismissal of Aaron Reed in the second innings was reassigned from Owen Price to Adam Wells. All other figures stand.
----- END TEXT -----
作答：
- Owen Price_wickets_credited = ____ ；依据句：____
- Owen Price_bowling_runs_conceded = ____ ；依据句：____
- Adam Wells_wickets_credited = ____ ；依据句：____
- Adam Wells_bowling_runs_conceded = ____ ；依据句：____
- innings_wickets_lost = ____ ；依据句：____
