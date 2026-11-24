# VETT 一体化论文方案 v2（2026-11-13）
> 目标：把 220 场语料、R28 扰动、状态方法收束成一篇论文；
> 约束：本地模型为主，DeepSeek V4.1 Flash 只做极少量锚点，token 成本可控。
> 本文件替代此前的"三线并行"，是本轮及后续的执行基线。

---

## 0. 一句话结论

核心问题成立，但原计划有 **3 个与仓库事实冲突的地方**，必须改：

1. **"超长文本"不成立**：220 场 commentary 中位 1,641 tokens、最大 2,462 tokens（≈5.5–10 KB），
   离 8K 上下文还很远。真正的难点是 **多事件聚合 + 修订 + 冲突 + 账目闭合**，不是长上下文检索。
   → 论文不要写 long-context，写 *narrative-dense state maintenance*。
2. **"220 场全量物化六变体"不划算**：220×6×多系统 = 1.5 万次调用，且现有证据表明
   聚合指标会把效应平均掉。→ 先 10 场深加工，30 场复现，220 场只做**源池 + 发布**。
3. **R28 要分两层**：现有 320 题单球诊断（R28-core）已经跑完 H1/H2，不要推倒；
   新做的是 **match-level 六变体**（R28-match），落在真实记分卡字段上。

---

## 1. 已核实的仓库事实（本轮实测，非推测）

| 事实 | 数值 | 含义 |
|---|---|---|
| commentary tokens | min 876 / med 1,641 / max 2,462 | 不是长上下文任务 |
| scorecard tokens | med 1,360；**219/220 > 640** | 旧 num_predict=640 必然截断 → 输出长度是瓶颈 |
| 每场表格数据行 | med 97 行 | 整表 exact 不现实，必须字段级评分 |
| evidence_chain.md | 每场仅 ~15 条（L1/L2/L3 ≈ 4/5/3） | 现有证据链**不是**逐字段证据 |
| **可再生成的全量证据图** | match_0001 生成 **61 条**，含 operand_of 依赖边 | 逐字段证据层可零成本批量重建 ✅ |
| 220 场目录完整性 | 220/220，四件套齐全 | 底座可用 |

**关键发现（省下最大一笔标注成本）**：
`Self-cricket..._extracted/src/evidence_planner.py` 的 `build_evidence_map()`
能从 scorecard 解析结果确定性地生成完整的 *EvidenceRequirementsMap*：
每条含 `field / value / level / evidence_type / operand_of / difficulty_class / placement_phase`。
match_0001 实测 61 条、L1=22、L2=39，且 `operand_of` 就是字段依赖图。
→ **第二层（字段证据）与第四层（依赖/闭合）不用 LLM 标注，用生成器重建。**

### 1.1 H1 正确性转移（本轮复算，40 题 × 12 字段 = 480 cell）

| 比较 | C→C | **C→W** | W→C | W→W(同错) | W→W(异错) | 均正确字段 |
|---|---:|---:|---:|---:|---:|---:|
| P1 vs P2（同 prompt 重测） | 294 | **0** | 1 | 180 | 5 | 7.35 → 7.38 |
| P1 vs V0（纯换序） | 252 | **42** | 39 | 90 | 57 | 7.35 → 7.28 |
| P1 vs E1（跨 max_tokens，仅参考） | 294 | 0 | 9 | 169 | 8 | 7.35 → 7.58 |

**这是全项目最强的一张表**：
- 重测 **0 个**"对→错"；换序 **42 个**"对→错"。
- 净变化只有 −0.07 字段/题，但 **81 个 cell 发生了翻转**（42 坏 + 39 好）。
- 40 题里 18 题变差、11 题变好、11 题不变 —— 平均值把方向完全抹平了。
- 结论一句话：**顺序敏感性是真实的状态不稳定，不是采样噪声；聚合准确率是它的遮盖物。**

### 1.2 模型身份 bug（已定位，未修）

`t19_panel_20261113/panel_llama3.1_8b.jsonl` 与 `panel_gemma2_9b.jsonl` 的
`model_digest` / `model_quantization` 全部写成 qwen 的
`845dbda0…` / `Q4_K_M`。根因在
`t19_e1e5_20261112/scripts/run_local.py:291,326-328`：
`model = service.model_info() or {}` 与 `"model_tag": MODEL_TAG` 都取全局默认，
`service.model_info(tag)` 明明支持传 tag，但没传。
→ 修法：行级记录改为 `service.model_info(tag)` 并把 tag 写进行；
  重跑 3×320=960 次（本地 ≈2–3 h，¥0），产物写新目录，不碰冻结件。

---

## 2. 调整后的论文主张（可证伪版）

**标题方向**：*Maintaining a Consistent Table under Revision: A Paired Diagnostic for State-tracking in LLMs*

- **RQ1（能力）**：从叙述文本生成记分卡，模型在**哪些字段类型**上失败？
  预期：直接事实/规则裁决尚可，跨字段聚合与依赖传播显著差。
- **RQ2（机制）**：在**只改证据状态、不改任务**的配对扰动下，失败如何变化？
  六变体：original / shuffled / revised / conflict / missing / distractor。
- **RQ3（方法）**：显式版本化事件账本 + 依赖传播，是否降低旧值残留与错误传播？

**贡献（四条，均可单独证伪）**：
1. 一个带**逐字段证据 + 可回答性 + 依赖闭合**的配对诊断集（10→30 场公开，220 场源池）。
2. 一个**配对成功指标**：原始对 ∧ 修订更新对 ∧ 无关字段不变，三者同时满足。
3. 一个**顺序/重测分离**的可靠性证据（42 vs 0）。
4. 一个**外部状态账本**方法，附 3 个消融与同预算强提示基线。

**明确不主张**：长上下文能力、真实比赛事实抽取（数据是模板注入的半合成，DATASET_CARD 必须写明）。

---

## 3. 10 场整合样本：目录与规格

```
VETT_INTEGRATED_20261113/
  pilot10/
    match_XXXX/
      source/{commentary.txt, scorecard.md, meta.json}   # 只读复制
      fields.jsonl          # 每字段一行，见下
      closure.json          # 闭合约束 + 求解器可执行规则
      variants/
        original/{commentary.txt, gold.json}
        shuffled/{commentary.txt, gold.json}
        revised/{commentary.txt, gold.json}
        conflict/{commentary.txt, gold.json}
        missing/{commentary.txt, gold.json}
        distractor/{commentary.txt, gold.json}
      manifest.json         # 每文件 sha256 + 编辑日志 + gold diff + 泄漏检查
```

**fields.jsonl 一行**：
```json
{"field_id":"inn1.bat.Ethan_Drake.R","table":"batting","row":"Ethan Drake","col":"R",
 "value":49,"answerability":"answerable",
 "evidence_type":"direct|aggregate|revision|rule|underdetermined",
 "evidence_spans":["ev_0012","ev_0031"],"depends_on":["inn1.total_runs"],
 "closure":"inn1.bat_sum + inn1.extras == inn1.total_runs"}
```
**可回答性五类**：直接给出 / 多事件聚合 / 需处理修订 / 需规则推导 / 文本无法唯一确定（gold=UNKNOWN）。

**pilot 目标字段（每场 ~60–80 个，不做全表 450 cell）**：
比赛级 6 + 每局 8（总分/ wicket/ extras 四项/ 轮次）+ 每局 top3 击球 + top2 投球
+ FOW 链 + 最大 partnership + 结果边际。全部落在生成器 61 条证据图覆盖范围内。

**10 场抽样（分层，脚本可复现）**：按 commentary tokens 三分位 × L2+L3 数量三分位 × 结果类型
（runs / wickets / 异常：No Result / Abandoned）分层，固定 seed，输出抽样清单与理由。

---

## 4. R28-match：六变体生成规则（确定性，禁止泄漏）

| 变体 | 操作 | gold 变化 | 必查 |
|---|---|---|---|
| original | 原文 | 原表 | 基线 |
| shuffled | 同局内事件句序打乱（不跨局） | **不变** | 位置捷径 |
| revised | 选 1 个决定性事件改写数值（如 batter +2、no-ball 改 wide） | 按求解器重算受影响字段 | 更新 + 传播 |
| conflict | 插入一份低权威"记分员便条"与正文冲突 | 取权威源 | 冲突裁决 |
| missing | 删除决定性证据句 | 受影响字段 = UNKNOWN，下游传播 UNKNOWN | 正确拒答 |
| distractor | 插入相似事件（不同球员/局） | **不变** | 干扰抵抗 |

**硬约束**：
- gold 由 Python 求解器重算，不由模型生成；
- revised/missing 必须给出 *changed_fields* 与 *unchanged_fields* 清单；
- 泄漏检查：变体文本不得包含 gold 表、不得出现"正确答案"字样；
- 每变体记录 `edit_log`（span 级增删改）与 sha256。

---

## 5. 方法：Versioned Event Ledger + Dependency Propagation

不堆 Agent。一个外部脚手架，三个部件：

1. **Event extraction（每场 1 次调用）**：模型只做"事件三元组"抽取
   `{entity, delta, source_span, time/over}`，输出短 JSON（≤400 tokens）。
2. **Ledger（Python）**：判定 new / duplicate / revision / conflict / irrelevant；
   维护 `entity → version → value`，冲突按权威级裁决。
3. **Propagation（Python）**：按 `operand_of` 依赖图只重算受影响字段，跑闭合断言。

**关键成本属性**：调用次数 O(1)/场，输出长度 O(events) 而非 O(cells)；
确定性的账本与算术全部离线。**这正是把 23× 输出瓶颈拆掉的设计。**

**消融（4 个）**：Direct / RAG-top-k / extract-then-table / full ledger。
**同预算基线**：full ledger 的 token 预算下，给 Direct 加 few-shot + 自检提示。

---

## 6. 成本模型（按 token 计，价格用你的账户单价乘）

| 阶段 | 调用量 | 输入 tokens | 输出 tokens | 费用 |
|---|---:|---:|---:|---|
| H1 复算 + 数据审计 | 0 | 0 | 0 | **¥0（已完成）** |
| 证据图重建（10→220 场） | 0 | 0 | 0 | **¥0（生成器）** |
| 身份修复后 H2 重跑 | 960 本地 | ~1.5M | ~0.25M | **¥0** |
| 10 场 pilot × 6 变体 × 3 本地模型 | 720 本地 | ~1.4M | ~0.4M | **¥0** |
| 10 场 × 6 变体 × 方法（3 消融） | 540 本地 | ~1.1M | ~0.3M | **¥0** |
| **DeepSeek V4.1 Flash 锚点（可选）** | **60** | **~0.12M** | **~0.04M** | **最小** |
| 220 场全量（若做） | 15,840 | ~32M | ~9.5M | 约 pilot 的 22× |

**成本纪律**：
- 批量实验一律本地 Ollama；V4.1 Flash 只做 ① 60 次强模型锚点 ② 抽样复核代码/数据。
- 所有调用落盘 raw JSONL + sha256；失败不重跑，先查缓存。
- 输出一律短 JSON schema；禁止让模型复述整表。
- 先 pilot 后扩展：10 场不过门，不碰 220。

---

## 7. 阶段门（不过门就停，不加难度）

- **G0（本周）**：H1 转移表 ✅；身份 bug 修复 + 重跑 ✅；证据图 10 场重建 ≥95% 字段覆盖。
- **G1**：10 场 fields/closure 求解器 100% 复现 gold；两人独立可读性检查通过。
- **G2**：六变体求解器 100% 复现；泄漏检查 0 命中；edit_log 完整。
- **G3**：pilot 出现可分离信号——方法在"正确更新率/旧值残留率"上 ≥ Direct +10pp，
  且换序效应 > 重测噪声（42 vs 0 已满足）。
- **G4**：30 场复现 G3；成本/调用数记录完整 → 才允许 220 场发布级物化。

**结果不符合预期时的预注册处理**（照你原计划六种情况，简化为）：
- 全低 → 先 oracle 证据测试，区分"定位"还是"状态更新"，再决定修数据还是修方法；
- 全高 → 查捷径（末段答案、众数、位置），先消捷径再谈难度；
- 方法无效 → 三个 oracle 消融定位（事件/版本/依赖），不堆模块；
- 方法只对小模型有效 → 直接写成应用贡献（与你的小模型方向一致）。

---

## 8. 本轮已完成 vs 下一步 72h

**已完成（本轮，全部 ¥0）**
1. `h1_transitions.py` + `h1_transitions.json`：三组比较的 5 类转移矩阵。
2. `dataset_audit.py` + `dataset_audit.json`：220 场规模、结构、上下文/输出 token 分布。
3. 证据图再生验证：match_0001 生成 61 条含依赖边。
4. 身份 bug 根因定位（run_local.py）。

**下一步**
1. 修 `run_local.py` 身份记录 → 重跑 3×320（后台，本地）。
2. 写 `build_pilot10.py`：分层抽样 + 证据图 + fields/closure + 六变体 + solver。
3. 先做 1 场端到端（match_0001），人工核对后再批量 10 场。
4. 本地三模型跑 pilot，产出第一版配对指标表。

---

## 9. 需要你拍板的 4 件事

1. **定位**：ACL/EMNLP Resource（诊断+数据，稳）还是主会方法论文（需要更强方法结果）？
   我建议先按 Resource 写，方法作为 RQ3 的一节；结果好再升级。
2. **220 的用法**：接受"220 = 源池 + 最终发布，正文只物化 10→30 场"吗？
   这是省 90% 成本和 80% 时间的关键。
3. **付费预算**：V4.1 Flash 上限给多少？（建议 ≤¥50：60 次锚点 + 复核；
   若为 0，则全部本地，论文写"本地 7–9B 面板"，仍成立。）
4. **人工检查**：10 场的可读性与 gold 审计，你能出 2 位标注者吗？
   若不能，我改为单人 + 脚本一致性检查，并在 Limitations 如实写。

---

## 附录：220 场闭合审计（2026-11-13 实测）

- 可解析 218 场；完全闭合 **191/218 = 87.6%**；至少一项缺陷 **27/218 = 12.4%**。
- 缺陷分布：bowling_recon 19、bat_plus_extras 8、wicket_sum 7、fow_monotone 1。
- 不可解析 2 场：match_0004（两局制 "innings and 32 runs"）、match_0066（Abandoned）。
- 发布时须给缺陷场打 `gold_defect` 标；pilot 只从 191 场干净样本抽取。
- 闭合规则修正：run-out 不计入投手 wicket（已计入）；追逐局 FOW 末值 ≤ 总分。

