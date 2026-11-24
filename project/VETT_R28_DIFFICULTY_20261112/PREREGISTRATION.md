# VETT-R28 预注册与统计分析计划（SAP）

**文档 ID：** `VETT-R28-PREREG-20261112-v1` ｜ **版本：** 1.2.0 ｜ **状态：** **FROZEN（已冻结；AMEND-001：N=320；AMEND-002：HA10 口径）**
**修订：** AMEND-002（captain 2026-11-12 裁决：HA10 泄漏统计量改为 lift-over-marginal，拒绝 "unreachable" 理由）
**修订：** AMEND-001（用户 2026-11-12 在 t25 确认门授权 B2/N=320）——样本量 160→320，端点/阈值/停止规则/零结果契约不变。
**任务：** t22（依赖 t3）｜ **成员：** data_designer ｜ **团队：** vett-r27-opt
**运行根：** `VETT_R28_DIFFICULTY_20261112/`
**机器可读版本：** `VETT_R28_DIFFICULTY_20261112/preregistration.json`（本文件是它的人类可读镜像；两者由 `scripts/prereg_verify.py` 做一致性校验）
**冻结指纹：** `prereg_freeze.json`（JSON/MD 文件 sha256 + 端点登记表 digest）与 `PREREGISTRATION.sha256`

> **这份文件在写任何 R28 数据之前冻结。** 冻结后，主端点、次要端点、判定阈值、停止规则、零结果契约、Brier/边指标口径的任何改动都必须走 §14 的 amendment 流程，并会触发 t8 的预注册一致性告警。若预注册与实测冲突，以预注册为准；若预注册本身有误，必须如实登记为 amendment，不得静默修改。

---

## 0. 一页摘要

| 项 | 内容 |
|---|---|
| 唯一主端点 | `paired_accuracy_drop = acc(对照 shallow) − acc(发布 hard)`，**题内配对，320 对**；准确率 = 9 个信息字段准确率（ITT） |
| 判定 | 点估计 **≥ +10.0pp** 且两种 95% CI 下界均 **> 0** → `HARDER`；点估计 > 0 但不满足 → `DIRECTION_ONLY`；点估计 ≤ 0 → `NOT_HARDER` |
| 三条基线门槛 | 必须**同时**越过 常数先验 **52.89%**、只看题面 TF-IDF+LR **54.22%**、anchor 众数 **73.33%**（信息字段，方向 = 发布版准确率严格更低）；记录 exact 还需越过 **32%**。**仅越过常数先验不算成立。** |
| 功效 | 不一致率 40% 时 N=**320** 给出 SE=**3.54pp**、95% CI 半宽 ±**6.93pp**、10pp 功效 **80.7%**（MDE≈9.91pp；预期 active 248 对 → SE 4.02pp/±7.87pp） |
| 有效 n | 发布集每族至多 1 题、一题一记录（320 族/320 记录）；与 R26.15 比较必须按族聚类（n_eff ≤ 25 族 / 16 记录）；R28 自身 n_eff = 320 族 / 320 记录 |
| 停止规则 | E1 CI 跨 0 → 不扩量不换指标；E5 跨度 <25pp → 停；证书重推 <100% → 阻断；泄漏审计失败 → 阻断；预算触顶 → `BUDGET_STOP`（共 13 条） |
| 零结果契约 | 未变难必须如实报告；**禁止**改端点、换指标、事后剔除、重跑找显著 |
| 多重比较 | 主端点单一不校正；5 个可检验次要端点 Holm–Bonferroni，全部标注 *exploratory* |
| 报告口径 | Brier **四项并列**（记录级 + 基率 + skill + cell 级）；边指标 **五分列**；不得回退到 "vs 0.25" 或 as-coded 0.7696 |

---

## 1. 身份、依赖与数据状态

### 1.1 冻结时点的事实

- **不存在任何 R28 题面、金标、证书或模型输出。** 冻结时的检查：R28 运行根下无 `r28_candidate/`、`eval_runs/`、`certificates/`、`variants/`；`03_build/local/` 只有 t18 的本地推理基础设施与能力矩阵产物；`01_measurement/` 的全部数字都是 **R26.15** 的测量，不是 R28 数据。
- 本预注册的全部输入来自已落盘工件（见 §1.2），不联网。
- **R26.15 零字节改动**：165 文件 / 93,346,177 字节 / tree aggregate `343afde4c91d7785f42296074ecea685d5d466260674ab5a8c3bc37323d851bd`（权威清单 `_BACKUPS/VETT_R28_PRE_CHANGE_20261112/PROTECTED_PATHS.json`）。历史聚合 `2cb1ea2c…9417` 已由 t1 证实不可复现，任何文书引用它即为 FAIL。

### 1.2 输入工件（内容寻址；sha256 见 `preregistration.json → bindings` 与 `prereg_freeze.json`）

| 工件 | 用途 |
|---|---|
| `01_measurement/BASELINES.json` | 三条基线门槛与 32% exact 门槛的**数值出处**（52.89 / 54.22 / 73.33 / 32） |
| `01_measurement/gate_A_decision.json` | A1/A2/A3 判定、8 条 findings、6 条硬约束 |
| `01_measurement/gate_B_decision.json` | B1 两半判定、机制状态、HYP-R28-DOSE 条款 |
| `01_measurement/MECHANISM_REGISTRY.json` | 9 条机制登记（VERIFIED 0 / UNTESTED 6 / REJECTED 3） |
| `01_measurement/HYPOTHESIS_REGISTRY.md` | H1–H6 与 HYP-R28-DOSE、B1 限制 |
| `01_measurement/MEASUREMENT_VALIDITY_NOTE.md` | Brier 四项 / 边五分列 / 逐级先验的权威口径 |
| `01_measurement/A_RESULTS.json`、`B1_RECHECK.json`、`DIFFICULTY_PROXIES.json` | A 阶段复算、B1 复算、因子共线证据 |
| `03_build/local/routing_card.json`、`capability_matrix.json`、`service_snapshot.json` | 本地 ALLOW/DENY、H6 参照、主模型参数 |
| `_BACKUPS/VETT_R28_PRE_CHANGE_20261112/PROTECTED_PATHS.json` | R26.15 零漂移权威清单 |

> **R26.15 口径（对照材料，不是 R28 数据）**：100 题 = 25 族 × 4 副本，族内金标记录完全相同，只有 **16 个不同记录**；族分类器（给定族名）field/record = 100%。因此 R26.15 的记录级有效 n 至多 **25 族 / 16 记录**，任何按题独立的 CI 都会高估精度。

---

## 2. 设计

### 2.1 设计摘要

| 项 | 值 |
|---|---|
| 发布集 | 320 题 / 64 场（每场 5 题），一题一记录（互异记录 = 320） |
| 对照集 | 同一 320 个实例的**配对渲染**（`variants/`），不是独立题 |
| 实验集 | 320 对 = **640 次推理**（每实例各跑发布版与对照版） |
| 两块结构 | **因子核 128 题**：2×2×2×2（D1/D2/D3/D4 各 0/1）× 每格 8 题；**剂量阶梯 192 题**：D1–D4 各 3 剂量 × 16 题 |
| 主模型 | 本地 `qwen2.5:7b-instruct-q4_K_M`（Ollama 0.40.16，RTX 3070 8GB，100% GPU，temperature=0，seed=20261112，num_ctx=8192）——**弱基线，不外推到前沿模型** |
| 对照定义 | 同一 `solver_facts` 与同一 `decision_record_flat` 渲染为**四剂量全 0** 的最小卷宗（`alias_hops=0, temporal_joins=0, scope_decisions=0, isomorphic_distractors=0`） |
| 发布定义 | 同一事实渲染为 R28 指派结构元组：因子核按 0/1，剂量阶梯按 0/1/2 |
| 执行顺序 | 每对固定先对照、后发布；前 40 对反向顺序复跑作顺序效应检查 |

### 2.2 设计不变量（任一不满足 → 停止规则）

| ID | 不变量 |
|---|---|
| D1 | 每对两臂的 `solver_facts` 逐字节相同（320/320） |
| D2 | 每对两臂的 `decision_record_flat` 逐字节相同（12 字段，320/320） |
| D3 | 发布集一题一记录：320 个互异 12 字段记录（`distinct_record_ratio = 1.0`） |
| D4 | 发布集每族至多 1 题：320 个互异 `scenario_family` |
| D5 | 对照版只是同一实例的配对渲染，不构成独立题、不增加有效 n |
| D6 | 两臂只有呈现层不同；两臂 token 长度差逐对记录为协变量 |
| D7 | 发布版至少一个剂量维度严格高于对照版；结构性空配对必须披露、不得事后剔除 |
| D8 | 不修改 R26.15 任何字节 |
| D9 | `held_out_test` 40 题不进公开包；任何评估集不得按族与拟合集交叉 |

### 2.3 结构性空配对（必须披露，不得静默剔除）

按提案 §4.2 的两块结构：因子核全 0 格 **8 题** + 剂量阶梯 dose=0 的 **64 题** = **72 对结构性空配对**（发布版 = 对照版），预期配对差为 0；**active pairs 预计 248**。处理方式：

- 主端点仍在全部 **320 对**上计算（ITT，不剔除任何对）；
- 空配对作为 **placebo 操作检查**（V3）：\|drop_placebo\| > 5pp → `DEGRADED`；
- **active-pair（248 对）敏感性分析 V1** 必须报告；若 320 对判 `HARDER` 而 active-pair 不满足同一判定，以更保守者为准；
- 若 t4 最终设计的空配对数不同，必须在合同中登记新数量并重算功效；**不得据此改变主端点定义**。若 n_active=248，40% 不一致率下 SE=4.02pp、CI 半宽 ±7.87pp（已列入 §5 功效表）。

---

## 3. 唯一主端点

### 3.1 定义

```
paired_accuracy_drop = acc(control) − acc(published)
```

- **准确率函数**：`decision_informative_field_accuracy`（t2/A2 冻结口径）。分子 = Σ 全部 320 题 × 9 个信息字段的正确 cell 数；分母恒为 **320 × 9 = 2880**（两臂各自计算）。
- **9 个信息字段**（冻结，不因 R28 让 BYE/LEG_BYE/PENALTY 非常数而改变）：`batter_runs, bowler_runs, counts_in_over, delivery_status, dismissal, ledger.BATTER, ledger.NO_BALL_EXTRA, ledger.WIDE_EXTRA, total_runs`。
- **record exact**：12 个扁平字段**全部**等于金标；分母为题数。它是次要/门槛指标，**不得替代**信息字段主端点。
- **ITT**：解析失败、缺失、非法值、弃权一律按该题全部 12 字段判错；**不剔除任何配对**。
- **同金标、同模型**：两臂 `solver_facts` 与 `decision_record_flat` 逐字节相同；同一模型、temperature=0、seed、num_ctx、prompt 模板。
- **统计单位**：题内配对（pair = instance = `scenario_family`），**不是 640 个独立样本**。

### 3.2 统计

- 点估计 `Δ = (b − c)/320`：b = 对照对、发布错的配对数；c = 对照错、发布对的配对数；不一致对 = b + c。
- **精确 McNemar 检验**：`b | (b+c) ~ Binomial(b+c, 0.5)`；报告双侧 p 与方向一致的单侧 p。
- **95% CI（两种）**：① 按题配对 bootstrap 10,000 次（seed=20261112）；② 按族聚类 bootstrap 10,000 次。判定使用**两个下界中更小者**（更保守）；方向矛盾时按更保守者判定并披露。
- 效应量以 **pp** 报告；p 值只作辅助。

### 3.3 判定规则（冻结）

| 判定 | 条件 | 允许的结论语言 |
|---|---|---|
| `HARDER` | 点估计 ≥ **+10.0pp** 且 `min(CI_lower_item, CI_lower_family)` **> 0** 且 G1–G9 全 PASS | 可以声称"更难" |
| `DIRECTION_ONLY` | 点估计 > 0 且（点估计 < 10pp 或 CI 下界 ≤ 0）；或主端点通过但有 claim gate 未过 | 只能报"方向一致但不显著" |
| `NOT_HARDER` | 点估计 ≤ 0 | 预注册结论"未变难" |

> **CI 跨 0 的处理**：不扩量、不加题、不更换端点、不重跑基线、不改模型/prompt；按 §10 零结果契约报告（停止规则 **S1**）。

### 3.4 Claim gates（"更难"声称的必要条件；全部 PASS 才允许 `HARDER`）

| Gate | 内容 | 不通过时 |
|---|---|---|
| **G1** | 三条基线门槛（§4）：发布版信息字段准确率严格低于每条基线的 `min(冻结参考值, R28 同集重测值)` | 降级为 `GATE_FAIL`，不得声称"更难/有区分度" |
| **G1r** | 记录 exact 门槛：发布版 exact 严格低于 `min(32%, anchor 同集重测 exact)` | 同上 |
| **G2** | `skill_hard_overall < 0`（发布版低于自身常数先验） | 禁止"越过先验"表述 |
| **G3** | 数据健康：互异记录 320/320、恒数字段 0、BYE/LEG_BYE/PENALTY 非零、每族 ≤1 题、确定性重建 | `BLOCK_DATA` |
| **G4** | 证书覆盖率 100% 且 solver 重推 100% | `BLOCK_RELEASE` |
| **G5** | 泄漏审计全项 PASS（白名单/答案串/近重复/族名基线/held_out） | `BLOCK_RELEASE` |
| **G6** | 双渲染逐字节一致（`solver_facts` + `decision_record_flat`，320/320） | `BLOCK_DATA` |
| **G7** | E5 已执行面板（≥2 模型）最强−最弱 ≥ 25pp；面板降级 → UNTESTED | 撤回区分度主张（S2） |
| **G8** | `conformance_rate ≥ 90%`（否则标 DEGRADED 并报 conforming-only 敏感性） | DEGRADED |
| **G9** | 设计完整性：n_pairs=320、无缺对、两臂模型/参数一致、无事后剔除或换指标 | `BLOCK_ANALYSIS` |

---

## 4. 三条基线门槛（t2 新增，写进判定规则）

> **数值出处：`01_measurement/BASELINES.json`**（`baselines.constant_75_to_25` / `tfidf_logreg_question_text_75_to_25` / `anchor_classifier_75_to_25`，信息字段 rate 与 record_exact rate）。

### 4.1 门槛

| 基线 | 冻结参考值（信息字段） | R26.15 记录 exact | 含义 |
|---|---:|---:|---|
| 常数先验（逐字段众数，75→25） | **52.89%** | 0% | 什么都不学 |
| 只看题面 TF-IDF+LR（不读卷宗） | **54.22%** | 0% | 读了题面但不读卷宗 |
| anchor 众数（只查锚，不读证据） | **73.33%** | **32%** | 只查锚 |
| *（背景，不作门槛）* GLM-5.3-Flash | *55.11%* | *28%* | 真读卷宗；仅比常数先验高 **0.89pp**，比 anchor 低 **18.22pp**，**不得**用它声称"读卷宗有效" |

### 4.2 方向定义（防止反向解释）

> **"更难" = 准确率更低。** "越过基线 b" = 发布版（hard）在 320 题上的信息字段准确率**严格低于**基线 b 的准确率。**禁止**把"高于基线"解释为"更难"，也禁止把差值方向写反。

### 4.3 双阈值规则（G1 / G1r）

对每条基线 b：

```
required: acc_hard_informative  <  min(reference_rate_b, same_set_rate_b)      # 严格小于
G1r:      acc_hard_record_exact <  min(0.32, anchor_same_set_record_exact)     # 严格小于
```

- `same_set_rate` 必须在 **R28 同一 320 题、同一 9 字段口径、同一 ITT** 下重测：
  - 常数先验：leave-one-family-out 逐字段众数；
  - 只看题面 TF-IDF+LR：按族分组 5 折 OOF（`fold = int(sha256(family_id)[0:8],16) mod 5`）；
  - anchor 众数：同一 anchor 内 leave-one-family-out 众数。
- **双阈值理由**：同时使用 R26.15 冻结参考值与 R28 同集重测值并取更严者——审稿人只需指出其中任一个未被越过，即可推翻"更难"。

### 4.4 三条硬规则

1. **仅越过常数先验不算成立**：若 `constant_prior` 分量通过而 `question_text_tfidf_logreg` 或 `anchor_mode` 未通过 → **G1 FAIL**，不得声称"更难"。
2. **fail-safe**：任一 same-set 基线因数据/资源原因无法在相同口径下测量 → **G1 = UNTESTED**，不得声称"更难"，必须报告 `DEGRADED`。
3. **禁止单基线判定**：只报告"vs 常数先验"的表格视为未满足本预注册。

---

## 5. 事前功效分析（AMEND-001：N=320）

**公式**：`SE(Δ) = sqrt(p_discordant / n_pairs)`；`CI 半宽 = 1.96 × SE`；`MDE(80%) = (1.96 + 0.8416) × SE`；`power(10pp) = Φ(0.10/SE − 1.96)`（双侧 α=0.05）。

| n（配对） | 不一致率 | SE | 95% CI 半宽 | 80% 功效 MDE | 10pp 功效 | 判定 |
|---:|---:|---:|---:|---:|---:|---|
| 160 | 40% | 5.00pp | ±9.80pp | 14.01pp | 51.6% | 历史基线（v1.0.0；功效不足） |
| 240 | 40% | 4.08pp | ±8.00pp | 11.44pp | 68.8% | 候选 B（评估后未采用） |
| **320** | 40% | **3.54pp** | **±6.93pp** | **9.91pp** | **80.7%** | **AMEND-001 选定（用户 B2）** |
| 400 | 40% | 3.16pp | ±6.20pp | 8.86pp | 88.5% | 未采用（10% 余量需求 480） |
| 248（N=320 active-pair） | 40% | 4.02pp | ±7.87pp | 11.25pp | 70.2% | 预注册敏感性（预期 72 空配对） |

**冻结的计算陈述（AMEND-001）：** 不一致率 40% 时 **N=320 给出 SE=3.54pp、95% CI 半宽 ±6.93pp、10pp 功效 80.7%（80% 功效 MDE≈9.91pp）**，因此采用 320 题（用户 2026-11-12 在 t25 确认门授权 B2）。

**诚实功效说明：** 上表是精度与功效计算。按双侧 α=0.05、Δ=10pp、N=320、40% 不一致率，SE=3.54pp，10pp 功效 80.7%；预期 active 248 对时 SE=4.02pp、10pp 功效约 70.2%。非显著结果仍只能报"未检出预注册阈值的效应，且研究对该阈值功效不足"。扩量已按用户授权完成；不得再扩量或更换端点（除新 amendment）。v1.0.0 注记（N=160：10pp 功效约 51.6%、MDE 14.01pp）保留为历史记录。

**其他冻结条款：** 若实际不一致率偏离 40%，报告实际 SE、CI 与实现功效；不得改用单侧检验、修改 α、继续扩量或更换端点。若发布版准确率接近 0，报告两臂绝对准确率与 95% Wilson CI，不得只报差值（地板效应）。记录需求：N=320 + 40 held_out + 10% 余量 = **392 ≤ 可达下界 761**（record_space_ok=true）。

## 6. 有效 n 规则

1. **EN1**：发布集每族至多 1 题，且一题一记录（`distinct_record_ratio = 1.0`）。
2. **EN2**：R28 的有效 n = **320 题 / 320 族 / 320 个互异记录**；每张结果表必须打印 `n_items / n_families / n_distinct_records`。
3. **EN3**：与 R26.15 的任何比较必须按族聚类：**n_eff 上限 = 25 族（仅 16 个互异记录）**，使用按族 bootstrap（25 clusters）或按族置换检验；**禁止**把 100 题当作 100 个独立样本。
4. **EN4**：禁止同族跨 split；所有基线拟合使用按族分组 5 折或 leave-one-family-out。
5. **EN5**：对照版是同一实例的配对渲染，不增加有效 n；**不得**把 640 次推理当作 640 个独立样本。
6. **EN6**：R28 vs R26.15 的跨数据集比较不是确认性端点，只能作为探索性描述，且必须同时报两边的 n_eff 与聚类方式。

> 依据（t2 F1）：R26.15 的 100 题 = 25 族 × 4 副本，同族副本金标记录完全相同，族分类器 100%；记录 exact 7/25 的 95% Wilson CI 为 **[14.3%, 47.6%]**。R28 用"一题一族一记录"把有效 n 从 16 抬到 320。

---

## 7. 多重比较

| 层 | 内容 | 校正 |
|---|---|---|
| 主端点 | `paired_accuracy_drop` | **单一检验，不校正**（α=0.05 双侧；单侧 p 仅辅助） |
| 次要端点（5 个可检验） | `dose_slope`(pooled)、`mechanism_effect`、`informative_field_skill`、`ablation_flip`、`risk_coverage_auc` | **Holm–Bonferroni，m=5，α=0.05，FWER 控制**；全部标注 **EXPLORATORY** |
| 内层 Holm（探索性） | `mechanism_effect` 的 10 个系数（4 主效应 + 6 二阶交互）；`dose_slope` 的 4 个机制斜率 | Holm；不计入外层 FWER（仅用于描述性归因，已明确标注探索性） |
| 阈值端点（4 个） | `distinct_record_ratio`、`family_only_baseline`、`certificate_validity`、`conformance_rate` | 确定性阈值，无零假设，不进入 Holm；作为门条件 |

**报告义务**：所有次要端点无论显著与否都必须报告点估计 + 95% CI；p 值原始值与校正值并列；**不得**把次要端点显著结果升级为确认性结论，**不得**只报 p 不报效应量。

---

## 8. 停止规则（13 条，全部冻结）

| ID | 触发 | 动作 / 代码 |
|---|---|---|
| **S1** | 主端点 CI 跨 0（`min(CI_lower) ≤ 0`）或点估计 < 10pp | **不扩量、不加题、不换端点、不重跑基线**；按零结果契约报告（`STOP_NO_EXPANSION`） |
| **S2** | E5 已执行面板（≥2 模型）最强−最弱 < **25pp** | 任务无区分度 → 停止扩量、回设计（`STOP_REDESIGN`）；若面板 <2 模型（零付费降级）→ UNTESTED，撤回区分度主张，不判 PASS |
| **S3** | 证书覆盖率 < 100% 或 solver 重推金标 < 100% | **阻断发布**，修 solver，100% 前不得定稿结论（`BLOCK_RELEASE`） |
| **S4** | 泄漏审计任一项失败 | **阻断发布**（`BLOCK_RELEASE`） |
| **S5** | 累计成本 ≥ ¥100 硬顶；任一金额 >¥0 的付费 API；云端 >¥3 软顶 | **`BUDGET_STOP`**：立即落盘停止，不自动续跑；付费调用按合约违规记录（S5 触发后仅人工裁决） |
| **S6** | 任一配对两臂 `solver_facts` 或 `decision_record_flat` 不逐字节相同 | `BLOCK_DATA` |
| **S7** | 互异记录 <320；存在恒定字段；BYE/LEG_BYE/PENALTY 任一无非零值；某族 >1 题 | `BLOCK_DATA` |
| **S8** | `family_only_baseline` 信息字段 > **40%** | `BLOCK_RELEASE`（族名等价答案的泄漏） |
| **S9** | 同一门连续 2 轮修复后仍 FAIL（第 3 轮） | `ESCALATED_HUMAN`：停下等人，禁止无限重试或自动改设计 |
| **S10** | R26.15 任何字节漂移 | `EMERGENCY_STOP`：停止全部工作，用 `restore.ps1` 回滚，提交事故报告 |
| **S11** | 设计偏离：n_pairs≠320、缺对、两臂模型/参数不一致、事后剔除/换指标 | `BLOCK_ANALYSIS`；不可恢复 → 主端点 UNTESTED |
| **S12** | E4：flip⁺ <2× 随机 / stability⁻ <80% / stability⁰ <90% / cited flip <90% 或 placebo >10% | 解释忠实度主张撤回（`EXPLANATION_CLAIM_NOT_ESTABLISHED`），不阻断数据发布 |
| **S13** | placebo \|drop\| >5pp；顺序效应 >5pp；`conformance_rate` <90% | `DEGRADED_FLAG`：报告不确定性来源，不得静默通过 |

---

## 9. 零结果报告契约

**原则：若数据没有变难，必须如实报告。禁止改用其他指标制造结论。**

1. **ZR1** 主端点不是 `HARDER` 时，摘要与结论必须直接写出配对差、95% CI、b/c 与判定（`DIRECTION_ONLY` / `NOT_HARDER`），不得只放附录。
2. **ZR2** 禁止动作（t8 按预注册一致性检查判 FAIL）：更换主端点定义；用全字段准确率或记录 exact 替代信息字段主端点作标题结论；静默剔除空配对/placebo 配对；更换模型、prompt、seed、温度寻找显著；把 per-field p 或事后子组当确认性证据；把"趋势一致"写成"更难"；使用旧表述（63.3/60.0/51.7、0.7696"给定正确节点"、Brier vs 0.25）作支持。
3. **ZR3** 9 个次要端点无论显著与否全部报告（点估计 + 95% CI + 判定）。
4. **ZR4** 某机制不成立时，必须报告"该机制未使任务变难"并公开其配对差与 CI；不得计入"更难"。
5. **ZR5** 主端点不显著时，不得只用"样本量不足"作解释而不报实现功效；必须同时报告实现 SE、实际不一致率与 MDE。
6. **ZR6** 零结果必须写进报告与（若适用）论文摘要，引用原始数据路径与命令；t11 决策报告必须包含零结果契约履行声明。

**允许的标题模板（只允许这些或其等价直译）：**

- `HARDER`：在 320 对题内配对中，发布版信息字段准确率比对照版低 {drop_pp}pp（95% CI [{lo_pp}, {hi_pp}]，McNemar 精确 p={p}），并同时越过常数先验、只看题面 TF-IDF+LR 与 anchor 众数三条基线（发布版 {acc_hard}% vs {b1}% / {b2}% / {b3}%）→ 可以声称"更难"。
- `DIRECTION_ONLY`：配对差为 {drop_pp}pp（95% CI [{lo_pp}, {hi_pp}]），方向与假设一致但未达到预注册的"显著且 ≥10pp"标准 → 只能报告"方向一致但不显著"，不得声称"更难"。
- `NOT_HARDER`：配对差为 {drop_pp}pp（95% CI [{lo_pp}, {hi_pp}]）→ 预注册结论为"未变难"。
- `GATE_FAIL`：配对差成立（{drop_pp}pp），但未同时越过三条无卷宗基线中的 {failed_n} 条（未越过：{failed_list}）→ 预注册结论为"未建立相对无卷宗基线的区分度"，不得声称"更难"。
- `BLOCKED`：存在阻断项（{blockers}）→ 本轮不发布任何难度结论。
- `ZERO_RESULT`：本轮未获得支持"更难"的证据；该结果与"数据未变难"和"功效不足"均相容，不能据此宣称任一方向。

---

## 10. 报告口径冻结（t2 修正版）

### 10.1 指标定义

- 主指标：`decision_informative_field_accuracy`（9 字段，ITT）。`decision_field_macro_accuracy`（全字段）**仅作描述**，不得作主端点或标题结论。
- `record_exact`：12 字段全等；分母为题数。
- `ledger.BYE / LEG_BYE / PENALTY` 在 R28 中必须**非恒定且非零**——这是数据健康要求（G3），**不改变** 9 字段信息分母，也**不得**用 12 字段准确率替代主端点。

### 10.2 Brier：四项并列（冻结）

| 项 | 定义 | R26.15 参考值 |
|---|---|---:|
| `per_record_brier` | `(1/n) Σ (confidence_i − 1[record_exact_i])²`，按题 | 0.626796 |
| `base_rate` | record exact 基率 | 0.28 |
| `brier_skill` | `1 − per_record_brier / [base_rate × (1 − base_rate)]`；参考类固定为 record-exact 基率的气候学常数 | −2.11（气候学 = 0.2016） |
| `per_cell_brier` | 以 (题, 字段) 为 cell 的 `(confidence_i − 1[field_correct])²` 均值；全字段与信息字段**分列** | 0.2956 / 0.3927 |

**冻结规则**：四项必须并列出现；参考类固定为 record-exact 基率的气候学常数；**禁止出现 "vs 0.25"**，禁止把 0.25 当作常数预测器 Brier，禁止用 "0.627 vs 0.25" 的旧对比。R26.15 数值只是口径示例，R28 必须按同一形式重算。

### 10.3 边指标：五分列（冻结）

| 列 | 定义 | R26.15 参考值 |
|---|---|---:|
| `minimal_evidence_edge_f1` | 端到端：预测边 vs gold 最小证据边的 P/R/F1 | 0.299264 |
| `conditional_f1_given_recovered_nodes` | precision 与 recall 都以**模型恢复端点**为条件（一致条件） | 0.4886 |
| `conditional_f1_given_gold_nodes` | precision 与 recall 都以 **gold 端点**为条件（一致条件） | 0.3857 |
| `gold_edge_endpoint_recovery_rate` | gold 边端点被恢复的比例 | 0.325284 |
| `content_dependency_edge_f1` | 内容依赖边子集上的 F1 | 0.092308 |

**legacy 混合条件**：as-coded `conditional_edge_link_f1 = 0.769556`（precision 以 gold 节点为条件、recall 以恢复节点为条件）只能作为**脚注**出现在五分列之后，必须标注 `LEGACY_MIXED_CONDITION_NOT_INTERPRETABLE_AS_GIVEN_CORRECT_NODES`；**禁止**写成"给定正确节点 77%"，**禁止**只报 as-coded 不报五分列。

### 10.3b 族名泄漏口径（AMEND-002）

- 判定：`lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0` 且 `value_balanced_accuracy ≤ 0.40` 且 `permutation_p > 0.05`；五项并列报告（value_balanced / lift / p / per-cell / marginal_mode），缺一不可。
- 实测：per-cell 0.514931；marginal 0.550347；lift -3.54pp；value-balanced 0.10387；p=0.146341。
- 理由：per-cell accuracy conflates marginal skew with leakage; the leakage statistic is lift-over-marginal；**不得**把理由写成 'the threshold is unreachable'。
- 族名 `rfam_<12 hex>` 中性哈希，不含设计标签；`per_cell_threshold_met=false` 可查，但 `per_cell_is_not_a_leakage_statistic=true`。

### 10.4 禁止表述清单

`Brier 0.627 vs 0.25` ｜ `vs 0.25` ｜ `conditional_edge_link_f1 = 0.7696 表示给定正确节点` ｜ `给定正确节点 77%` ｜ `63.3 / 60.0 / 51.7 证明剂量杠杆已验证` ｜ `GLM 55.11% 证明模型在读卷宗` ｜ 主端点未通过时 `R28 已变难` ｜ 仅凭常数先验对照声称"更难"。

---

## 11. 假设登记与机制状态

### 11.1 H1–H6（冻结时全部 UNTESTED，H6 为冻结前参照）

| ID | 假设 | 支持条件 | 拒绝条件 | 实验 | 冻结状态 |
|---|---|---|---|---|---|
| **H1** | 同一金标下发布版准确率显著低于对照版 | Δ ≥ 10pp + CI 不含 0 + G1–G9 | CI 跨 0 → "方向一致但不显著"；Δ<0 → "未变难" | E1（320 对） | UNTESTED |
| **H2** | 剂量 0/1/2 准确率单调递减且斜率显著 | 机制层：单调 + 0→2 ≥10pp + 斜率 CI 不含 0；整体 ≥2/4 机制 | 非单调/反向/<10pp/CI 含 0 | E2（192 题） | UNTESTED |
| **H3** | 至少 1 个机制主效应 CI 不含 0 | 内层 Holm 后 ≥1 主效应 CI 不含 0 | 全部含 0 → "难度不可归因" | E3（128 题） | UNTESTED |
| **H4** | 证书重推 100%，删被引证据翻转 ≥90% | `certificate_validity=100%` 且 cited flip ≥90%（placebo ≤10%） | 任一不达 | E4（40×3） | UNTESTED |
| **H5** | 多模型面板最强−最弱 ≥25pp | 已执行面板跨度 ≥25pp | 不达 → 无区分度；降级 → UNTESTED | E5（64 题） | UNTESTED |
| **H6** | 本地白名单任务一致率 ≥0.85 | t18：T1 0.933 / T2 1.000 / S1 1.000 / C1 1.000（R1 0.667→DENY） | 不达 → 降级回云端 | E6（t18 已做；R28 只验路由一致性） | REFERENCE_ONLY_T18 |

### 11.2 HYP-R28-DOSE（正式登记，唯一剂量假设）

- **陈述**：同一模型上，语义机制剂量↑ → 字段准确率单调下降。
- **范围**：仅 D1–D4（`alias_hops` / `temporal_joins` / `scope_decisions` / `isomorphic_distractors`）。**明确排除** REJECTED 机制（文档数/分散度、上下文长度、bridge depth）；推导深度/算子数暂不纳入（UNTESTED，待 t5 验证）。
- **操纵**：同一 `solver_facts` 与同一 `decision_record_flat`（**逐字节相同**），只改一个机制的剂量 0/1/2。
- **成立条件**：① 0→1→2 单调递减（任一步不得反向或持平）；② 0→2 总效应 **≥10pp**；③ 斜率 95% CI 不含 0；④ 在 E2 的 192 题上执行。
- **拒绝条件**：**非单调 / 方向反转 / 效应 <10pp / 斜率 CI 含 0，任一命中即判该机制不成立，不得计为"更难"。**
- **状态**：**UNTESTED**；**唯一裁决实验 E2**（t19，本地 7B；E3 提供机制归因旁证）。
- **失败报告契约**：若拒绝，如实报告"该机制未使任务变难"，公开配对差与 CI；**不得改端点/换指标制造更难结论**。
- **已推翻的旧论证**：初稿曾用"6 组同事实跨族产生 63.3 / 60.0 / 51.7 的等级落差"论证剂量杠杆已验证。t3 证明那三个数是整级宏准确率（混杂场景/比赛/抽样误差）；同事实组逐对比较的真实结果为 **10 对：5 降 / 4 升 / 1 平、均值 −3.3pp、符号检验 p = 0.50**。因此剂量效应降级为 UNTESTED。

### 11.3 机制状态（写死，设计时无任何机制被证实）

**VERIFIED = 0 ｜ UNTESTED = 6 ｜ REJECTED = 3**

> **设计时没有任何机制被证实**（VERIFIED = 0）。不得把设计意图当作证据。

| 状态 | 机制 | 依据 |
|---|---|---|
| UNTESTED | D1 证据跳数（`alias_hops`） | 横断面 rho = −0.520（p_holm = 0.064，边缘）；无剂量阶梯 |
| UNTESTED | D2 修订链（`temporal_joins`） | 横断面 rho = −0.353（ns） |
| UNTESTED | D3 权威裁决（`scope_decisions`） | 横断面 rho = −0.320（ns） |
| UNTESTED | D4 干扰同构度（`isomorphic_distractors`） | 横断面 rho = −0.524（p_holm = 0.064，边缘） |
| UNTESTED | 推导深度/算子数（`rule_operators` / `derivation_depth`） | **t3 修正**：同事实组内 `rule_operators` 1→2、2→3、3→4 变化而金标逐字节相同 → 原 REJECTED 理由被推翻；t5 必须用 solver 验证必要性，**验证前不得作为 R28 机制**；若验证通过并要使用，必须走 amendment（v2） |
| UNTESTED | 证据位置 | 尚无剂量阶梯实测 |
| **REJECTED** | 证据文档数/分散度 | 本地 7B：2→6→13 文档，信息字段 4.033→4.200→4.552（**反向上升**），速度 71.9→65.4→33.0 t/s，配对 80K−15K = +0.552 → **"加文档"不是加难** |
| **REJECTED** | 上下文长度 | 同实验：80K 比 15K 仅高 0.55/9，却慢约 4 倍 |
| **REJECTED** | bridge depth | 与等级双射（eta²=1.0），无法独立操纵 |

**因子共线警告**：R26.15 的 `bridge_depth` 与等级双射（eta²=1.0）；`distractor_count`、`temporal_joins` 是等级的确定性函数；`derivation_depth` 0.90、`temporal_depth` 0.77、`active_source` V=0.707 强混杂；仅 anchor 与 context_band 与等级正交。**四剂量必须由 R28 生成器独立赋值构造，禁止从 R26.15 的 `difficulty_vector` 反推因子水平。**

### 11.4 B1 的已知限制（冻结）

- 描述性 = **PASS**；预测性 = **UNTESTED**（75 题没有任何模型评分；零付费 pilot 不可执行）；composite = `NOT_MET_PENDING_PREDICTIVE`。
- **`can_redesign_levels_from_25_questions = false`**。
- **不得据 25 题重设等级。** 等级只保留为描述性标签（每级 n=5，记录 exact 95% CI [14.3%, 47.6%]）；R28 **不使用 L1–L5 作为难度因子或抽样单位**；加难只能由机制剂量实验（同金标双渲染、题内配对）判定。

---

## 12. 敏感性 / 效度检查（预注册，探索性）

| ID | 检查 | 矛盾处理 |
|---|---|---|
| **V1** | active-pair 敏感性（排除结构性空配对，预计 248 对） | 320 对判 HARDER 而 active-pair 不满足同一判定 → 以 active-pair 为准并披露 |
| **V2** | 长度协变量：`logit P(correct) ~ arm + length_delta + arm×length_delta`（族聚类稳健 SE） | 调整后效应 < 未调整的 50% 或 CI 含 0 → 报"长度混杂不能排除"，降级为 `DIRECTION_ONLY` |
| **V3** | placebo 配对操作检查（结构性空配对，预期 Δ=0） | \|drop_placebo\| >5pp（>2/72）→ `DEGRADED`（S13） |
| **V4** | 顺序效应：前 40 对反向顺序复跑（80 次本地推理） | \|order_effect\| >5pp → `DEGRADED`（S13） |
| **V5** | conforming-only 敏感性（conformance 通过子集重算） | 与 ITT 方向相反 → 两者都报，主结论用 ITT，标 DEGRADED |
| **V6** | R28 vs R26.15 跨数据集比较（按族聚类，n_eff ≤25/16） | **探索性**；不得作"更难"的唯一证据 |
| **V7** | 剂量/机制/因子格/族子组报告 | **描述性**；子组显著不得升级为标题结论 |

---

## 13. Claim 决策矩阵

| 主端点 | Gates | 允许的标题 | 说明 |
|---|---|---|---|
| `HARDER` | G1–G9 全 PASS | `HARDER` | 唯一允许声称"更难"的组合 |
| `HARDER` | G1 或 G1r FAIL | `GATE_FAIL` | 配对差成立但未越过无卷宗基线；不得声称"更难/有区分度" |
| `HARDER` | G2–G9 任一 FAIL | `DIRECTION_ONLY` | 按对应停止规则处理 |
| `DIRECTION_ONLY` | 任意 | `DIRECTION_ONLY` | 不得声称"更难" |
| `NOT_HARDER` | 任意 | `NOT_HARDER` | 零结果契约生效 |
| 任意 | G3/G4/G5/G6 任一 FAIL | `BLOCKED` | 不发布任何难度结论 |

---

## 14. 冻结后的修改政策

- **AMEND-001（已执行，2026-11-12）：** 用户于 t25 确认门授权 B2，`n_published` 160→320；端点/阈值/停止规则/零结果契约不变；见 `prereg_amendments.jsonl`。

- **AM1 允许**：错别字、格式、补充出处链接、不改变含义的措辞澄清。必须写入 `prereg_amendments.jsonl`（append-only）并重新生成 `prereg_freeze.json`。
- **AM2 禁止（必须人工批准 + 版本升级 + t8 告警）**：修改主端点定义、次要端点清单/定义、判定阈值（含 10pp、25pp、40%、90%、100%、32%、52.89%、54.22%、73.33%）、停止规则、零结果契约、多重比较方案、有效 n 规则、Brier/边指标口径。
- **AM3**：看到任何 R28 结果之后，端点与判定规则不得再改；任何事后分析只能标注 `EXPLORATORY`，不得替换主端点。
- **AM4 t8 一致性检查**：重算 `preregistration.json`、`PREREGISTRATION.md` 的 sha256 与 `endpoint_registry_sha256`，与 `prereg_freeze.json` 比对；任一不符 → **FAIL** 并输出 diff。
- **AM5 人工门**：预注册冻结后的任何端点修改必须由 captain 上报用户批准；批准前不得执行对应分析。

---

## 15. 验证与复现

```powershell
# 1) 校验预注册（结构/数值/规则/口径/假设/绑定/冻结一致性/R26.15 零漂移）
python VETT_R28_DIFFICULTY_20261112\scripts\prereg_verify.py --check

# 2) （仅首次冻结时）生成冻指纹
python VETT_R28_DIFFICULTY_20261112\scripts\prereg_verify.py --freeze
```

- 输出：`VETT_R28_DIFFICULTY_20261112/prereg_verify_result.json`（逐项 PASS/FAIL + 证据）。
- 关键不变量：`preregistration.json` / `PREREGISTRATION.md` 字节 hash 与 `prereg_freeze.json` 一致；`endpoint_registry_sha256` 重算一致；13 条任务要求覆盖；5 条强制停止规则存在；9 个次要端点 id 精确匹配；Brier 四项 / 边五分列存在；HYP-R28-DOSE 拒绝条件存在；VERIFIED 0 / UNTESTED 6 / REJECTED 3；B1 限制存在；R26.15 165 文件 / 93,346,177 字节 / 聚合 `343afde4…51bd` 无漂移。

---

## 附录 A：任务要求覆盖（13 条）

| # | 任务书要求 | 本文件位置 | JSON 指针 |
|---|---|---|---|
| 1 | 唯一主端点 `paired_accuracy_drop`，320 对 | §3 | `/primary_endpoint` |
| 2 | 9 个次要端点清单 | §10 / 附录 B | `/secondary_endpoints` |
| 3 | 三条基线门槛（52.89/54.22/73.33 + exact 32） | §4 | `/baseline_gate` |
| 4 | 事前功效（v1.0.0：40%、n=160、SE=5.0pp、±9.8pp；**AMEND-001：N=320、SE=3.54pp、±6.93pp、10pp 功效 80.7%**） | §5 | `/power_analysis` |
| 5 | 有效 n 规则（每族 ≤1 题、一题一记录、R26.15 按族聚类） | §6 | `/effective_n_rules` |
| 6 | 停止规则（E1/E5/证书/泄漏/预算） | §8 | `/stopping_rules` |
| 7 | 零结果契约 | §9 | `/zero_result_contract` |
| 8 | 多重比较（主端点不校正；次要 Holm + 探索性） | §7 | `/multiplicity` |
| 9 | Brier 四项 / 边五分列，禁止回退旧表述 | §10 | `/reporting_contract` |
| 10 | captain 更正 1：HYP-R28-DOSE（成立/拒绝条件、UNTESTED、E2） | §11.2 | `/hypotheses/hyp_r28_dose` |
| 11 | captain 更正 2：机制状态 VERIFIED 0 / UNTESTED 6 / REJECTED 3 | §11.3 | `/hypotheses/mechanism_status` |
| 12 | captain 更正 3：B1 限制、不得据 25 题重设等级 | §11.4 | `/hypotheses/b1_limits` |
| 13 | captain 更正 4：推导深度改判 UNTESTED，t5 solver 验证 | §11.3 | `/hypotheses/mechanism_status/untested` |

## 附录 B：次要端点一览

| 端点 | 角色 | 数据源 | 判定 | Holm |
|---|---|---|---|---|
| `dose_slope` | 次要（H2） | E2 192 题 | 机制层单调 + ≥10pp + 斜率 CI 不含 0；整体 ≥2/4 | 外层成员（pooled）；内层 4 |
| `mechanism_effect` | 次要（H3） | E3 128 题 | ≥1 主效应内层 Holm 后 CI 不含 0 | 外层成员；内层 10 |
| `informative_field_skill` | 次要（构念效度） | E1 + E2 | `skill_hard < 0`（G2），逐条件重算先验 | 外层成员 |
| `distinct_record_ratio` | 阈值（数据健康） | 发布集 | = 1.0（320/320） | 否 |
| `family_only_baseline` | 阈值（泄漏） | 发布集 | `lift_over_marginal ≤ 0` 且 `value_balanced ≤ 0.40` 且 `permutation_p > 0.05`（五项并列；AMEND-002） | 否 |
| `certificate_validity` | 阈值（H4） | 发布集 + solver | 覆盖率 100% 且重推 100% | 否 |
| `ablation_flip` | 次要（H4） | E4 40 题 | cited ≥90% 且 placebo ≤10% | 外层成员 |
| `risk_coverage_auc` | 次要（部署） | E1 320 响应 | AUROC > 0.5 且 CI 不含 0.5 | 外层成员 |
| `conformance_rate` | 数据质量 | 全部响应 | ≥90%，否则 DEGRADED；ITT 依据 | 否 |

---

**冻结签署（机器可判）：** 本文件与 `preregistration.json` 的 sha256、`endpoint_registry_sha256` 记录在 `prereg_freeze.json`；`scripts/prereg_verify.py --check` 可逐项复现。任何端点修改将改变 digest 并触发 t8 告警。
