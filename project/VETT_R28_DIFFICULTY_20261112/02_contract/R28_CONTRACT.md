# R28 数据优化合同（冻结版）

**合同 ID：** `VETT-R28-CONTRACT-20261112-v1` ｜ **版本：** 1.2.0 ｜ **状态：** **FROZEN（已冻结；AMEND-001：N=320；AMEND-002：HA10 口径）**
**任务：** t4（依赖 t2 / t3 / t22）｜ **成员：** data_designer ｜ **团队：** vett-r27-opt

> **AMEND-002（2026-11-12，captain 裁决）：** HA10 泄漏统计量改为 `lift_over_marginal` + `value_balanced_accuracy` + `permutation_p`；拒绝 "the threshold is unreachable" 的理由。实测：per-cell 0.5149 / marginal 0.5503 / lift −3.54pp / value-balanced 0.1039 / p=0.146341。


> **AMEND-001（2026-11-12，用户 t25 授权 B2）：** `n_published` 160→320；blocks 128/192；scenes 64；E1 640 次；合法 dismissal 封顶 ≤11；NONE 124/320=38.75%。端点/基线门槛/报告口径不变。

**冻结时间：** v1.2.0 见 `contract_freeze.json`（v1.0.0 冻结于 2026-11-12T10:59:59Z；v1.1.0/AMEND-001 与 v1.2.0/AMEND-002 见 prior_versions）
**运行根：** `VETT_R28_DIFFICULTY_20261112/`
**机器可读版本：** `02_contract/r28_contract.json`（v1.2.0；sha256 见 `contract_freeze.json` / `CONTRACT.sha256`）
**冻指纹：** `02_contract/contract_freeze.json` + `CONTRACT.sha256`
**校验器：** `02_contract/scripts/contract_verify.py`（AMEND-002 后逐项结果见 `contract_verify_result.json`）
**上位约束：** 预注册 `VETT-R28-PREREG-20261112-v1` **v1.2.0**（endpoint_registry_sha256 `2462be08…0c77`；AMEND-002 后）。**端点、阈值、停止规则、零结果契约与报告口径一律以预注册为准；本合同不重新定义它们。**

> 本文件回答"R28 到底要造什么、怎么造、造出来怎么算合格"。它与预注册互补：预注册冻结"什么算通过"，本合同冻结"数据怎么构造"。

---

## 0. 一页摘要

| 项 | 内容 |
|---|---|
| 数据集 | `VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`；**N=320 题 / 64 场**（AMEND-001），一题一记录，每族至多 1 题 |
| 两臂 | **发布版 hard**（指派结构元组）vs **对照版 shallow**（四剂量全 0）；题内配对 **320 对 = 640 次推理** |
| 四剂量 | D1 `alias_hops` 0/1/2；D2 `temporal_joins` 0/1/2；D3 `scope_decisions` 0/1/≥2；D4 `isomorphic_distractors` 0/1/≥2。**全部 UNTESTED** |
| 两块 | 因子核 **128**（2⁴×8）+ 剂量阶梯 **192**（4 机制×3 剂量×16）= **320 题 / 64 场** |
| 记录空间 | 分层定向枚举**可达互异记录下界 761**（随机 2 万次只有 156，不代表可达空间）；67 个记录形态层 |
| 配额 | 写死（N=320）：状态 LEGAL 166 / NO_BALL 100 / WIDE 53 / DEAD_REBALL 1；dismissal NONE **124（38.75%）** / RUN_OUT 86 / OBS 50 / HIT 50 / 合法 dismissal **10（封顶 ≤11）**；BYE 96、LEG_BYE 78、PENALTY 153 非零 |
| 硬验收 | 18 条（互异率 1.0、恒定字段 0、常数字段非零、证书 100%、双渲染 320/320、确定性、族名 lift-over-marginal（AMEND-002）、泄漏、配额、prompt ≤7000 tokens、N 参数化、合法 dismissal 封顶） |
| 基线门槛 | 52.89% / 54.22% / 73.33%（信息字段）+ 记录 exact 32%；方向 = 发布版严格更低；仅越过常数先验不算成立 |
| N 参数 | `n_published` 显式参数（**当前 320**，必须是 40 的倍数）；**禁止硬编码**；AMEND-001（N）与 AMEND-002（HA10 口径）均已应用 |
| 用户决策 | **已决（2026-11-12）**：Q1=B2 → N=320（10pp 功效 80.7%、MDE 9.91pp）；Q2 接受天花板但合法 dismissal 封顶 ≤11；Q3 接受 renderer 扩展（须证明生效） |

---

## 1. 依据、范围与硬边界

**依据（只读输入）：**

| 工件 | 作用 |
|---|---|
| `preregistration.json`（t22，sha256 `fdd744b8…0f11`） | 主/次端点、判定规则、停止规则、零结果契约、报告口径 |
| `01_measurement/{BASELINES,gate_A_decision,gate_B_decision}.json`（t2/t3） | 三条基线数值、A1–A3 门、B1 两半判定 |
| `01_measurement/MECHANISM_REGISTRY.json`、`HYPOTHESIS_REGISTRY.md` | 9 条机制状态、HYP-R28-DOSE |
| `PROPOSAL_…md`、`AUDIT_GOAL_AND_DESIGN_20261112.md` | 设计提案与审计（参考快照） |
| `02_contract/evidence/record_space_probe.json` | 记录空间探针（t4 新增，761） |
| `02_contract/evidence/quota_assignment_check.json` | 配额与格分配可行性 |
| `_BACKUPS/…/PROTECTED_PATHS.json` | R26.15 零漂移权威清单 |

**硬边界：** 全程零付费推理 API（硬顶 ¥0）；不修改 R26.15 任何字节（165 文件 / 93,346,177 字节 / 聚合 `343afde4…51bd`）；金标/证书只能由确定性 solver 生成；不联网。

---

## 2. 先例：没有任何机制被证实（写死）

### 2.1 机制状态（t3 定稿，不得改写）

**VERIFIED = 0 ｜ UNTESTED = 6 ｜ REJECTED = 3**

> **当前没有任何机制被证实能提高难度。** R28 的"更难"只能由 E2 的结果建立，不能由设计意图或历史数据预设。

| 状态 | 机制 | 依据 |
|---|---|---|
| UNTESTED | D1 证据跳数、D2 修订链、D3 权威裁决、D4 干扰同构度 | 横断面相关（rho −0.32…−0.52）不等于剂量证据 |
| UNTESTED | 推导深度 / 算子数 | t3：同事实组内 `rule_operators` 1→2、2→3、3→4 而金标逐字节相同；**t5 必须用 solver 验证必要性**，验证前不得作为机制 |
| UNTESTED | 证据位置 | 尚无剂量阶梯实测 |
| **REJECTED** | 证据文档数 / 分散度 | 2→6→13 文档：信息字段 4.033→4.200→4.552（**反向上升**）；速度 71.9→65.4→33.0 t/s；配对 80K−15K=+0.552 |
| **REJECTED** | 上下文长度 | 同实验：80K 比 15K 只高 0.55/9，却慢约 4 倍 |
| **REJECTED** | bridge depth | 与等级双射（eta²=1.0），无法独立操纵 |

### 2.2 两个被推翻的理由（必须保留记录）

1. **"6 组同事实跨族产生 63.3/60.0/51.7 等级落差 ⇒ 剂量杠杆已验证"** —— **错误**。那是整级宏准确率；t3 重算为同事实组逐对：**10 对 = 5 降 / 4 升 / 1 平，均值 −3.3pp，符号检验 p = 0.50**。已改为 **HYP-R28-DOSE**（UNTESTED，责任实验 E2）。
2. **"推导深度不可在保金标前提下调节"** —— **被推翻**。同事实组内 `rule_operators` 1→2、2→3、3→4 而金标逐字节相同 → 改判 **UNTESTED**，由 t5 用 solver 验证；若要使用须走预注册 amendment（v2）。

### 2.3 B1 与等级政策

- B1 描述性 = **PASS**；预测性 = **UNTESTED**（75 题无任何模型评分；零付费 pilot 不可执行）；composite = `NOT_MET_PENDING_PREDICTIVE`。
- **`can_redesign_levels_from_25_questions = false`**。不得据 25 题重设等级；R28 **不使用 L1–L5** 作为难度因子或抽样单位（每级 n=5，记录 exact 95% CI [14.3%, 47.6%]）。

---

## 3. 四个可调剂量（语义冻结，全部 UNTESTED）

> 四剂量均由 `generator.py:306-381` 的真实渲染参数实现；**每实例独立赋值**，不再每族固定一个结构元组。所有剂量的 **`solver_facts` 与 `decision_record_flat` 不变**——只改"如何找到答案"，不改答案。

| 剂量 | 参数 | 0 | 1 | 2 | span 增量 | 渲染器状态 |
|---|---|---|---|---|---|---|
| **D1** 证据跳数 | `alias_hops` | 事实直接以 CASE 编号命名主体 | 1 个 locator（register→token） | locator + bridge（token→packet+时间/over） | +0/+1/+2 | 现有代码已支持（按实例取值） |
| **D2** 修订链 | `temporal_joins` | 无修订 | 2 个版本（被替代值 + 现行值，按 revision / pre-lock 选一） | 3 个版本、跨 2 字段，需沿链回放两次 | +0/+1/+2 | **t5 必须新增** revision-chain 渲染（现有代码只加 1 个 bridge span） |
| **D3** 权威裁决 | `scope_decisions` | 单一权威 | 2 源冲突 + policy span | ≥2 冲突（3 源）+ policy + masked cell，逐对裁决 | +0/+1/+2 | **t5 必须扩展**（现有代码只支持 1 个冲突源） |
| **D4** 干扰同构度 | `isomorphic_distractors` | 无干扰 | 1 个同构 shadow | ≥2 个，其中 1 个 near-miss（除 1 个事实外与目标一致） | +0/+1/+2 | 现有代码按数量生成；near-miss 需 t5 新增 1 个对照事实 |

**正交性：** 因子核取 2⁴ 全因子（0/1）；剂量阶梯只让一个机制取 0/1/2、其余固定 0。**禁止**从 R26.15 的 `difficulty_vector` / level / family 反推因子水平（t2 已证共线）。

---

## 4. 两臂双渲染与三集合拆分

| 集合 | 位置 | 内容 | 硬约束 |
|---|---|---|---|
| **发布集** | `public/` + `private/` | 320 题，一题一记录，逐题分配剂量 | 互异率 = **1.0** |
| **对照集** | `variants/` | 每题一份配对渲染（四剂量全 0） | `solver_facts` 与 `decision_record_flat` 逐字节相同 320/320 |
| **实验集** | `eval_runs/` | 320 × 2 = **640 次推理** | 题内配对（McNemar） |

> **纠正旧版冲突：** "互异记录 ≥0.9×题数"与"同金标双渲染"数学上冲突（160=80×2 时互异率上限 0.5）。R28 拆成两个集合：发布集 **320** 个互异记录 + `variants/` **320** 份配对渲染。发布集一题一记录，互异率 = 1.0。

**双渲染 identity（逐对校验）：**

- **必须逐字节相同：** `solver_facts`（canonical JSON）、`decision_record_flat`（12 字段）、`question_text`、output schema、ruleset。
- **允许不同：** dossier 文档与 span 文本/顺序、每臂证书的 `minimum_evidence_spans` / `rule_path` / `revision_chain` / `authority_decision` / `why_not_distractor`、token 长度、`state.active_source`（若 D3 引入策略；state 不进入 12 字段主端点）。
- **禁止不同：** 12 字段记录值、`delivery_status` / `dismissal` / `run_ledger`、任何答案、`question_text`、`scenario_family`（配对两臂共享同一 family）。

**"事实相同"的准确含义：** 指解析后的 `solver_facts` 与 `decision_record_flat` 逐字节相同，**不是**公开文本相同——公开文本正是被操纵的变量。这一点必须写进数据卡。

---

## 5. 两块结构、N 参数化与功效 ladder

### 5.1 两块

| 块 | n | 构造 | 用途 |
|---|---:|---|---|
| 因子核 | **128** | 2⁴ = 16 格 × 每格 **c = N/40 = 8** 题 | 主效应与二阶交互（H3/E3） |
| 剂量阶梯 | **192** | 4 机制 × 3 剂量 × 每格 **m = N/20 = 16** 题 | 剂量斜率与单调性（H2/E2） |
| 合计 | **320** | **64 场** × 5 题 | E1 主实验 |

### 5.2 N 是显式参数（不得硬编码）

- 参数名 `n_published`，**当前 320**（AMEND-001），约束 **必须是 40 的倍数**（保证 2N/5 可被 16 整除、3N/5 可被 12 整除、N/5 为整数）。
- 派生：因子核 `2N/5`、剂量阶梯 `3N/5`、`c = N/40`、`m = N/20`、场数 `N/5`、对照 `N`、E1 推理 `2N`。
- 生成器/构建/评测/报告模板**均不得硬编码 n_published**；所有计数写入 `MANIFEST/config_digest`。
- amendment 只需改 `n_published` 一个数；配额用 `quota_rescale_v1`（AMEND-001 修正版：合法 dismissal 封顶 ≤11、缺口优先补 NONE→RUN_OUT→OBS/HIT、NONE ≤38.75%）重标定，再由 t8 复算、用户签字。

### 5.3 功效 ladder（40% 不一致率、双侧 α=0.05；主端点对全部 N 对）

| N | 因子核/阶梯 | 场 | 预期空配对 | active | SE | 95% CI 半宽 | 80% MDE | 10pp 功效 | 互异记录需求（含 held_out +10%） | 记录空间可行 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|:--:|
| 160（历史） | 64/96 | 32 | 36 | 124 | 5.00pp | ±9.80pp | 14.01pp | 51.6% | 216 | ✅ |
| 200 | 80/120 | 40 | 45 | 155 | 4.47pp | ±8.77pp | 12.53pp | 60.9% | 264 | ✅ |
| 240 | 96/144 | 48 | 54 | 186 | 4.08pp | ±8.00pp | 11.44pp | 68.8% | 304 | ✅ |
| 280 | 112/168 | 56 | 63 | 217 | 3.78pp | ±7.41pp | 10.59pp | 75.4% | 344 | ✅ |
| **320（AMEND-001 选定）** | 128/192 | 64 | 72 | 248 | **3.54pp** | **±6.93pp** | **9.91pp** | **80.7%** | **392** | ✅ |
| 400 | 160/240 | 80 | 90 | 310 | 3.16pp | ±6.20pp | 8.86pp | 88.5% | 480 | ✅ |

> 空配对 = 因子核全 0 格（N/40）+ 剂量阶梯 dose=0（4 × N/20）= 9N/40（22.5%）。它们按构造预期差值为 0，作为 placebo 操作检查（预注册 V3），不得静默剔除。

### 5.4 记录空间不是瓶颈（旧结论作废）

| 口径 | 结果 |
|---|---|
| 随机 2 万组事实（旧） | 156 个互异记录 → 旧文据此说"160 已接近天花板" |
| 另一次 4000 抽样（旧） | 315 个互异记录 |
| **本合同的**分层定向枚举（新） | **761 个互异记录下界**（15,840 组构造事实，0 失败，67 层） |

**结论：** 记录空间足以支撑 N=320（需 360 互异记录 + 10% 余量 = 392 ≤ 761）甚至 N=400（480 ≤ 761）。**本轮真正的瓶颈是功效与构建/审计成本，不是记录空间。** 旧版"160 已接近上限、超出必须扩 solver"的结论作废；solver 扩展只在 N 或新机制需要超过可达空间 90% 时触发（属 R29+）。

---

## 6. 记录空间的结构天花板（必须写进数据卡）

| ID | 事实 | 后果 |
|---|---|---|
| CEIL-1 | `DEAD_REBALL` 在 solver 中强制全账本清零且 dismissal=NONE → 整个状态只有 **1 个可达记录** | 发布集最多 1 题 DEAD_REBALL；"四类都有量"按"四类都出现"执行 |
| CEIL-2 | `BOWLED` / `LBW` / `CAUGHT` 各只有 **2 个可达记录**，`STUMPED` 4 个（合法 dismissal 合计 ≤10） | 合法 dismissal 合计最多 10 题；不得重复记录凑分布 |
| CEIL-3 | `WIDE` 状态 contact 必须为 NONE → BYE/LEG_BYE 恒 0，非零账本只有 WIDE_EXTRA 与 PENALTY | BYE/LEG_BYE 覆盖只能来自 LEGAL/NO_BALL |
| CEIL-4 | BYE 与 LEG_BYE 由 contact 决定，互斥 | 常数字段非零分别统计，不要求同一记录同时非零 |

**记录空间安全规则：** `可达下界 ≥ N + 40(held_out) + 0.10 × N`。**N=320 → 392 ≤ 761 ✅**（历史 160 → 216 ✅）。

---

## 7. 分层定向枚举与配额（写死，不得随机采样）

### 7.1 策略

1. 按配额表选目标 `(delivery_status, dismissal, BYE/LEG_BYE/PENALTY 非零 mask)` 层与目标记录。
2. 反解满足该记录的最小事实集（status 路线 × dismissal 路线 × running/boundary/penalty 参数）。
3. 调 `solver.solve()`，要求 `flatten_record` 逐字段等于目标记录；否则换事实集，**不改记录**。
4. 选 `visible_fields`：每个入证据集的字段必须有 countermodel 证明 pivotal；非 pivotal 事实只能作干扰。
5. 生成两臂渲染与证书；校验 twin identity；写入 quota 与 audit。

**禁止：** 随机采样 FACT_DOMAINS（2 万次只得 156 记录，dismissal=NONE 占 74%）；重复记录凑数；事后改配额；用模型生成事实/金标/证书。

### 7.2 配额（N=320，逐层写死）

**状态分布（N=320）：** LEGAL 166 ｜ NO_BALL 100 ｜ WIDE 53 ｜ DEAD_REBALL 1

**dismissal 分布（N=320）：** NONE **124（38.75%）** ｜ RUN_OUT 86 ｜ OBSTRUCTING_FIELD 50 ｜ HIT_BALL_TWICE 50 ｜ BOWLED 2 ｜ LBW 2 ｜ CAUGHT 2 ｜ STUMPED 4（合法 dismissal 10 + DEAD 1 = **封顶 11**）

**账本非零覆盖（N=320）：** `ledger.BYE` 96 ｜ `ledger.LEG_BYE` 78 ｜ `ledger.PENALTY` 153

**分块（N=320）：** 因子核 128（16 格 ×8）｜ 剂量阶梯 192（12 格 ×16）

**格分配算法** `balanced_heterogeneity_v1`：按层轮转发牌 → 每格贪心选"同 status/dismissal 最少"的未满格 → 每格内按记录 sha256 升序取未使用记录。可行性已实测：16 个因子格全满（每格 ≥2 种 status、≥3 种 dismissal），12 个剂量格全满（每格 ≥3 种 status、≥4 种 dismissal）。逐层配额见 `r28_contract.json → design.quota_table.rows`（67 层，含 `n_factor_core` / `n_dose_ladder`）。

**未共存事实组合（至少各 1 题，逐条记录）：**

1. `appeal_made=False + dismissal_candidate=LBW`
2. `appeal_in_time=False + dismissal_candidate=CAUGHT`
3. `contact=PERSON + wide_called=True`
4. `dead_before_wicket=True + dismissal_candidate=RUN_OUT`
5. `penalty_runs_batting=5 + boundary_mode=OVERTHROW`

### 7.3 held-out 与 split

- 发布集 **320** = `development`；`held_out_test` = 40（16 因子格 ×1 + 12 剂量格 ×2），记录与发布集互异，**不进入公开包**。
- `calibration` = 0：R28 不做任何模型/提示调参（模型与 prompt 由预注册冻结），避免把评测题用于选择。
- 记录需求：320 + 40 = **360 个互异记录**（含 10% 余量 392 ≤ 可达下界 761，余量充足）。

---

## 8. 硬验收（t6 构建后必须全绿，t8 独立复验）

| ID | 验收 | 阈值 | 阻断 |
|---|---|---|:--:|
| HA1 | 发布集互异记录率 | `distinct_record_ratio == 1.0`（320/320） | ✅ |
| HA2 | 每族至多 1 题 | 320 个互异中性 family；配对共享 family | ✅ |
| HA3 | 恒定字段 | 12 字段中无任何字段恒定 | ✅ |
| HA4 | 常数字段非零 | BYE ≥80、LEG_BYE ≥64、PENALTY ≥120（计划 96/78/153） | ✅ |
| HA5 | dismissal 不退化 | NONE ≤38.75%（124/320）；RUN_OUT ≥60；OBS ≥40；HIT ≥40；合法 dismissal ≥8（计划 10） | ✅ |
| HA6 | delivery_status 覆盖 | LEGAL ≥120、NO_BALL ≥80、WIDE ≥40、DEAD_REBALL = 1（计划 166/100/53/1） | ✅ |
| HA7 | 证书覆盖率与重推 | 覆盖率 100%；solver 重推 100%（两臂各自） | ✅ |
| HA8 | 双渲染一致性 | `solver_facts` + `decision_record_flat` 320/320；题面 320/320；两臂证书各自重推 100% | ✅ |
| HA9 | 确定性重建 | 同 seed + 同配置 → MANIFEST tree aggregate 相同 | ✅ |
| HA10 | 族名基线（泄漏，AMEND-002） | `lift_over_marginal ≤ 0` 且 `value_balanced_accuracy ≤ 0.40` 且 `permutation_p > 0.05`；五项并列（value_balanced / lift / p / per-cell / marginal_mode） | ✅ |
| HA11 | 泄漏审计 | public 无 gold/level/dose/族名语义、无答案串、无近重复、held_out 不入 public | ✅ |
| HA12 | 配额与格分配 | 逐层配额 = 合同值；16×4 / 12×8；每格 ≥2 status、≥2 dismissal | ✅ |
| HA13 | 未共存组合 | 5 个组合各 ≥1 题 | — |
| HA14 | 记录空间安全余量 | 360 互异；含 10% 余量 392 ≤ 761 × 0.9 = 684.9 | ✅ |
| HA15 | prompt 预算 | ≤7000 tokens（硬上下文 8192）；≤12 文档、≤80 span；超限判不合格、不截断 | ✅ |
| HA16 | 输出 schema | 12 字段与枚举冻结；字段名不得改 | ✅ |
| HA17 | N 参数化 | 代码/配置无硬编码 n_published；计数由 `n_published` 派生 | ✅ |

---

## 9. 基线门槛与报告口径（引用预注册）

### 9.1 族名泄漏契约（AMEND-002）

- **判定（两条同时成立）：** `lift_over_marginal = per_cell_accuracy − marginal_mode ≤ 0`；`value_balanced_accuracy ≤ 0.40` 且 `permutation_p > 0.05`。
- **实测：** per-cell 0.514931；marginal_mode 0.550347；lift -3.54pp；value-balanced 0.10387；p=0.146341；record-exact 0.00625。
- **五项并列报告：** value_balanced_accuracy / lift_over_marginal / permutation_p / per_cell_accuracy / marginal_mode（缺一不可）。
- **理由：** per-cell accuracy conflates marginal skew with leakage; the leakage statistic is lift-over-marginal
- **保留：** `per_cell_threshold_met=false` 可查，但 `per_cell_is_not_a_leakage_statistic=true` 并附边际数字。
- **族名编码检查：** `rfam_<12 hex>` 中性哈希，320/320 唯一，不含 D1-D4/M1-M4/F-/L-D/block/cell/dose/level 等标签；public 中虽含 `scenario_family`，但盲包剥离、且字符串不编码设计信息 → 对基线解释无混杂。

- **三条基线（信息字段）：** 常数先验 **52.89%**、只看题面 TF-IDF+LR **54.22%**、anchor 众数 **73.33%**；记录 exact 另需越过 **32%**。方向 = **发布版严格更低**；必须严格低于 `min(冻结参考值, R28 同集重测值)`；**仅越过常数先验不算成立**。
- **Brier 四项并列：** `per_record_brier` + `base_rate` + `brier_skill`（气候学 0.2016）+ `per_cell_brier`（0.2956 / 0.3927）；**禁止 vs 0.25**。
- **边指标五分列：** 端到端 0.2993 / 给定恢复节点 0.4886 / 给定 gold 节点 0.3857 / 端点恢复率 0.3253 / 内容依赖边 0.0923；as-coded 0.7696 仅 legacy 脚注。
- **主指标：** `decision_informative_field_accuracy`（9 字段，ITT）；全字段仅描述。

**有效 n：** R28 = 320 题 / 320 族 / 320 互异记录；与 R26.15 比较 n_eff ≤25 族 / 16 记录、按族 bootstrap；禁止把 100 题或 640 次推理当独立样本。

---

## 10. 禁用项（10 条）

1. 证据文档数/分散度作为加难机制（实测反向上升：4.033→4.200→4.552）。
2. 上下文长度作为加难机制（80K 比 15K 只高 0.55/9）。
3. bridge depth 作为 R28 因子（与等级双射）。
4. 随机采样构造记录（2 万次仅 156 个互异，dismissal=NONE 74%）。
5. 硬编码 `n_published`（否则 amendment 失效）。
6. 把设计意图当证据（VERIFIED=0；HYP-R28-DOSE=UNTESTED）。
7. 修改 R26.15 任何字节。
8. 用 L1–L5 等级作为抽样单位或难度因子。
9. 付费推理 API（硬约束 ¥0）。
10. 语言模型生成事实/金标/证书。

---

## 11. t2 findings 与 6 条硬约束（合同复述）

| ID | finding | 对 R28 的含义 |
|---|---|---|
| F1 | 100 题 = 25 族×4 副本，16 个互异记录，族分类器 100% | 一题一族一记录；R26.15 比较按族聚类 |
| F2 | 常数 64.67% vs GLM 66.33%；信息字段 52.89 vs 55.11 | 主指标 = 信息字段 + skill |
| F3 | 题面 LR 54.22%，与 GLM 55.11% 只差 0.89pp | 无卷宗基线强制对照 |
| F4 | Brier 参考类错（气候学 0.2016，skill −2.11） | 四项并列，禁止 vs 0.25 |
| F5 | as-coded 0.7696 条件混用；端点恢复 0.3253 | 边指标五分列 |
| F6 | 因子与等级强共线（bridge 双射等） | 四剂量独立赋值 |
| F7 | 族名内嵌等级；anchor 是唯一正交区组 | 族名中性化 |
| F8 | 41 是去重桶数，不是分母 | 报告写分子/分母 |

**约束：** C1 信息字段 + skill；C2 四类基线；C3 按族 n_eff；C4 边指标分列；C5 Brier 气候学参考；C6 因子与等级正交。

---

## 12. 风险与限制（必须进数据卡/论文）

| ID | 风险 | 状态 | 处理 |
|---|---|---|---|
| RISK-1 | 剂量效应未被验证 | UNTESTED | E2 唯一裁决；合同不预设成立；失败按零结果契约报告 |
| RISK-2 | D2/D3 的 0/1/2 语义当前 renderer 只支持布尔/单冲突 | IMPLEMENTATION_REQUIRED | t5 实现真 revision chain 与 ≥2 冲突+masked cell；HA 覆盖 |
| RISK-3 | 记录空间不均匀（DEAD_REBALL=1、合法 dismissal≤10） | KNOWN_CEILING | 配额按可达上限；数据卡披露；不重复记录 |
| RISK-4 | 模型上下文 8192 | HARD_CAP | 每题紧凑 dossier；prompt ≤7000 tokens；长文档不是难度机制 |
| RISK-5 | 功效（v1.0.0：10pp 仅 ~51.6%） | **DECIDED_B2_N320** | 已按用户授权 AMEND-001 到 N=320（80.7% / 9.91pp）；见 §14 |
| RISK-6 | 金标未经人工双标 | KNOWN_LIMITATION | t24 就绪包；论文列为发表阻断项 |
| RISK-7 | 本地 7B 弱基线；temperature=0 非逐位确定 | KNOWN_LIMITATION | 预注册声明；E5 面板；数据构建确定性不受影响 |
| RISK-8 | solver 是单球规则查表器 | KNOWN_LIMITATION | 数据卡不得称"多跳推理机" |

---

## 13. 变更控制

- **CC1** 冻结后，剂量语义、两臂拆分、配额、硬验收阈值、N 约束、禁用项不得静默修改；任何修改写入 `02_contract/contract_amendments.jsonl` 并重新冻结。
- **CC2** 涉及预注册端点/阈值/停止规则的修改一律走预注册 amendment（AM2/AM5）；合同不得先于预注册改动。
- **CC3** t8 必须独立重算合同 sha256、配额与格分配、twin identity、R26.15 零漂移、N 参数化；任一不符 → FAIL。
- **CC4** **用户未确认 t25 前，t5/t12/t13/t24 不得开工。**

---

## 14. 已决：功效/N（用户 2026-11-12 授权 B2 → N=320）

**决定：** Q1=B2 → `n_published=320`（10pp 功效 80.7%、MDE 9.91pp、CI 半宽 ±6.93pp、记录需求 392 ≤ 761）；Q2 接受结构天花板但合法 dismissal 封顶 ≤11；Q3 接受 D2/D3 renderer 扩展（须证明生效）。合同版本升级 1.0.0→1.1.0，AMEND-001 记录见 `contract_amendments.jsonl`。

**决策前评估（历史记录）：**

| 选项 | N | 10pp 功效 | 80% MDE | 互异记录需求* | 结论 |
|---|---:|---:|---:|---:|---|
| A 保持 | 160 | 51.6% | 14.01pp | 216 | 未采用 |
| B 扩量 | 240 | 68.8% | 11.44pp | 304 | 未采用 |
| **B2 扩量（选定）** | **320** | **80.7%** | **9.91pp** | **392** | **已授权并应用** |
| C 改口径 | 160 | 51.6% | 14.01pp | 216 | 未采用 |

\* 含 40 题 held_out + 10% 安全余量。当前设计按 320 题、640 次 E1 推理执行；未再扩量。

## 15. 验证与复现

```powershell
python VETT_R28_DIFFICULTY_20261112\02_contract\scripts\probe_record_space.py   # 记录空间探针（只读，秒级）
python VETT_R28_DIFFICULTY_20261112\02_contract\scripts\quota_design.py         # 配额与格分配可行性
python VETT_R28_DIFFICULTY_20261112\02_contract\scripts\build_contract.py --freeze   # 构建并冻结合同
python VETT_R28_DIFFICULTY_20261112\02_contract\scripts\build_contract.py --check    # 冻指纹一致性
python VETT_R28_DIFFICULTY_20261112\02_contract\scripts\contract_verify.py --check   # 107 项语义校验
```

- 冻指纹：`contract_freeze.json`（合同文件 sha256、R28_CONTRACT.md sha256、quota digest `ea9ec367…93f`、HA digest `d79bf20c…7c2`、剂量语义 digest `894bf3f3…a29`；以文件内值为准）。
- `contract_verify.py` 同时逐文件重算 R26.15：165 文件 / 93,346,177 字节 / 聚合 `343afde4…51bd`。
- 下一步：t25 合同复核包（≤2 页）→ 通知 captain → 保持 in_progress 等用户确认；确认前 t5/t12/t13/t24 不得开工。

---

## 附录 A：本合同与任务书 (A)–(K) 的对应

| 任务书 | 本文件位置 |
|---|---|
| (A) 机制登记以 t3 为准、无机制被证实 | §2.1 |
| (B) 两个被推翻的理由 | §2.2 |
| (C) 四剂量 0/1/2 语义 | §3 |
| (D) REJECTED 禁止项 | §2.1 / §10 |
| (E) 三集合拆分、旧 0.9 冲突 | §4 |
| (F) 两块结构 128+192=320/64 场 | §5.1 |
| (G) 分层定向枚举、禁随机 | §7 |
| (H) 硬验收：互异率/常数字段/证书/确定性/记录空间 | §6 / §8 |
| (I) 三条基线门槛 + exact 32 | §9 |
| (J) Brier 四项 / 边五分列 | §9 |
| (K) B1 预测性 UNTESTED、can_redesign=false | §2.3 |
| captain：功效不足 + A/B/C + N 参数化 | §5.2 / §14 |

## 附录 B：机器可读段索引（`02_contract/r28_contract.json`）

`precedent` ｜ `design.doses` ｜ `design.twin_identity` ｜ `design.record_space` ｜ `design.quota_table` ｜ `design.n_published_parameter` ｜ `enumeration` ｜ `hard_acceptance` ｜ `baselines_and_metrics` ｜ `effective_n` ｜ `forbidden_items` ｜ `findings_and_constraints` ｜ `risks_and_limitations` ｜ `user_decision_required` ｜ `change_control` ｜ `digests`
