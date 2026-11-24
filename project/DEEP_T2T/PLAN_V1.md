# DeepTable：深度文本转表格 V1（2026-11-13）

> 合并对象：220 场记分卡语料（`Self-cricket-clean_text_scorecard_v1_220_matches`）
> × R28 机制层（版本化规则、冲突裁决、证据必要性、证书）。
> 目标口径：ACL/EMNLP Resource & Evaluation。周期：1 周最小可行切片。预算：¥0。

## 0. 一句话

把 220 场的“整场表”从**抄写任务**改造成**约束满足任务**：
输入一份约 25KB 的卷宗（解说 + 事件级修订备忘 + 版本化规则 + 干扰文档），
输出约 40 个**必须被推导**的 cell；每个 cell 有证据链/证书。

## 1. 审计事实（`corpus_audit.json`）

| 项 | 值 |
|---|---:|
| 场数 | 220 |
| 表格 cell 总数 | **98,572** |
| 每场平均 cell | **448.1** |
| batting / partnership / bowling / FOW / summary | 33,908 / 24,563 / 20,992 / 9,837 / 9,260 |
| evidence chain L1 / L2 / L3 | 32.1% / **40.9%** / **27.0%** |
| 文本均值 | commentary 6.4 KB、scorecard 5.2 KB、evidence 2.5 KB |

**关键读法**：语料本身不浅——68% 的证据目标是 L2/L3（闭合/综合），
浅的是“当前任务只问 L1 直取”。深度不是再造数据，是**把评分对象移到 L2/L3 的 cell 上**。

## 2. 三个硬约束（设计必须绕开）

1. **220 源只有局级聚合，没有逐球事实**（数据卡 B1）。不能在 220 场上直接注入 R28 单球；
   合并只能发生在“表格 cell + 事件级修订”这一层。
2. **本地 8K 上下文**：卷宗 ≤ ~25KB（约 6.5K token），输出 ≤ ~1K token。
   65KB 需要 32K/cloud，不在本周范围。
3. **1 周 + 只有作者 1 人**：本周不做人工双标；这是 feasibility 切片，不是最终论文。

## 3. 任务定义

**输入（~25KB 卷宗）**
- 解说原文（6.4KB，叙事）
- 3–5 条**事件级**修订备忘：写“某球发生了什么”，不写最终数字
- 2 份规则摘录（v2025 / v2026，其中一份被取代）
- 2 份干扰文档（另一场的数据）

**输出（紧凑记分卡表，~40 cells）**
- 两局 innings summary：total / extras / byes / leg-byes / no-balls / wides / RR / max partnership（16）
- 每局 top-3 batters ×（R, B, 4s, 6s）（24）
- 每局 top-3 bowlers ×（O, M, R, W）（24）
- FOW chain（10 + 5）（15）
（约 79 cells；实际进入评分的 ~40 个是 L2/L3 依赖 cell）

**cell 构成**
- 25% L1：直取（抄对即可）
- 50% L2：闭合（行和、列和、extras、bowling 账、wickets 和、overs 和）
- 25% L3：版本/跨文档（哪条规则生效、哪份修订在force、干扰文档是否被误用）

## 4. 四个条件

| 条件 | 操纵 | 回答 |
|---|---|---|
| **C0** | 只有解说 | 浅层基线：模型能抄多少 |
| **C1** | + 事件级修订备忘 | 修订后能否重算，而不是只读最后一条 |
| **C2** | + 规则版本冲突 | 同一事实在两版规则下答案不同，考“哪条生效” |
| **C3** | + 删一条决定性文档 | 证据必要性：答案必须变/必须弃权 |

## 5. 指标

- `cell_exact`（按 cell 类型分组）
- `table_exact`（整表全对）
- `closure_violation`（行和≠总、extras 和≠总、bowling 账≠总−byes/leg-byes、wickets 和≠10）
- `copy_rate`（cell 等于文中直接出现的数字 → 浅层抄写）
- `derivation_rate`（L2 cell 正确率）
- `version_sensitivity`（C2 vs C1 的 cell 变化率）
- `flip_rate`（C3 下答案改变率 = 证据必要性）

## 6. 预注册门（本周切片）

| 门 | 条件 | 不过怎么办 |
|---|---|---|
| G1 | C0 的 `cell_exact` > 0.80 | 太浅，加修订/冲突 |
| G2 | C1 的 `table_exact` = 0 且 `closure_violation` > 0.50 | 任务成立，继续 |
| G3 | 3 个模型都 `parse_fail` | 换输出 schema（JSON/grammar） |
| G4 | C2 的 `version_sensitivity` < 0.10 | 版本冲突没生效，重做文档 |

## 7. 一周排期

| 天 | 做什么 | 产出 |
|---|---|---|
| D1 | 20 场 builder：解析 scorecard → 选 cell → 注入修订 → 渲染卷宗 | `build_deep20.py` + 20 卷宗 |
| D2 | 证书/金标重算 + 泄漏筛查 | `gold/` + `CERT.json` |
| D3 | eval harness + 3 模型 × 4 条件（240 次） | `runs/` + 首张表 |
| D4 | 可靠性：10 题重复 2 次；C3 必要性 | `reliability.json` |
| D5 | 1 页 memo + go/no-go + 论文骨架 | `MEMO.md` |

## 8. 不做什么

- 不物化 220 进 R28；不合并成一篇 8 页。
- 不做 65KB/云端；本周只做 25KB 本地切片。
- 不做人工双标；论文必须写“作者自标/未独立验证”。
- 不在本周追“更难”的话术；只报读数。
