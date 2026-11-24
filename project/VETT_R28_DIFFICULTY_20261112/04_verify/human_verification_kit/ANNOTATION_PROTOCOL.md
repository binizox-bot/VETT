# R28 人工双标协议（ANNOTATION_PROTOCOL v1）

**协议版本：** `ANNOTATION_PROTOCOL.v1`
**所属工具包：** `VETT-R28-HUMAN-VERIFICATION-KIT-20261112-v1`
**对应任务：** t24（人工核验就绪包；**本轮不执行人工标注**）
**上位文件：** `VETT-R28-CONTRACT-20261112-v1` v1.1.0（N=320）与 `VETT-R28-PREREG-20261112-v1` v1.1.0
**状态：** 已就绪，等待 R28 构建与标注者；**尚未执行**

> **边界声明（不得删改）：**
> 1. 本协议与工具包**不产生人工金标**。金标始终是确定性 solver 输出（`decision_record_flat` + `solver_facts` + 证书）。
> 2. 人工双标只做两件事：**确认**金标（verdict 为正）或**隔离**金标（verdict 为负/无法裁决）。
> 3. 在 `adjudicate.py` 对真实 R28 数据返回 `PASS` 之前，论文必须把
>    “金标未经独立人工双标核验”列为**发表阻断项（blocking limitation）**，不得写成“已人工验证”。
> 4. 本协议不允许任何语言模型生成/修改 12 字段记录、scope、规则版本或证明集合；本地模型只能提供可编辑提示（见 `preannotation/PREANNOTATION_POLICY.md`）。

---

## 0. 一页摘要

| 项 | 规则 |
|---|---|
| 标注单位 | 1 题 = 1 个发布集 item（一题一记录、一题一族） |
| 样本 | 从 R28 发布集 320 题中分层抽 **100 题**（种子 `20261112`；28 个设计格全覆盖） |
| 标注者 | A、B 两名独立标注者；另设 1 名仲裁者 C（不得是 A/B） |
| 阶段 | ① 盲推导（只看 public 卷宗）→ ② 揭示金标后逐维判定 → ③ 分歧和解 → ④ 仲裁 → ⑤ 合并出报告 |
| 四维 | **值**（12 字段）｜**范围（scope）**｜**规则版本**｜**最小证明** |
| 合格线 | H1 两标注者每维原始一致率 ≥98%；H2 确认金标缺陷 = 0；H3 两人资格测试各维 ≥98% 且关键错误 = 0 |
| 关键错误 | 值 MISMATCH；scope SCOPE_ERROR；规则版本 VERSION_ERROR；证明 INSUFFICIENT / FABRICATED |
| 非关键否定 | 证明 NOT_MINIMAL（证书冗余，不改记录值） |
| 无裁决 | 必须记 `UNDECIDABLE` + `UNRESOLVED`；不得为“通过”强行 CONFIRMED |
| 输出 | DERIVED / VERIFY / ADJUDICATION 三个 JSONL；必须经 `seal_export.py` 与 `validate_export.py` 后才能统计 |
| 金标状态 | `PASS` / `FAIL` / `NOT_EXECUTED`；只有 PASS 才能声称人工核验通过 |

---

## 1. 术语与消歧（先读这一节）

本协议中每个词只有一个含义。出现同形异义时，以本节为准。

| 术语 | 定义 | **不是**什么 |
|---|---|---|
| **gold / 金标** | 由确定性 solver 从卷宗事实生成的 `solver_facts` 与 `decision_record_flat`（12 字段），以及配套证书 | 不是人工写的答案，不是模型输出，不是本协议的产物 |
| **derived / 派生值** | 标注者在**看不到 gold** 时从 public 卷宗独立推导出的记录、范围、规则版本与证明集合 | 不是金标，也不要求与金标相同；与金标不同是待判定信息 |
| **value / 值** | `decision_record_flat` 的 12 个字段的取值（见 §3.1） | 不是“数值值域”本身；字段类型/非负/枚举属于维度 V 的 `V0` 检查 |
| **scope / 范围** | 证据与规则的**适用范围**：哪个来源是决定性的、哪些冲突存在、哪些 cell 被遮蔽、哪些材料在题外 | **不是**数值区间（如 0–6 runs）；数值区间归维度 V |
| **rule_version / 规则版本** | 支配本题的 ruleset（标题 + 生效日期）与被选中的 revision（版本链） | 不是模型版本、不是数据集版本 |
| **proof / 最小证明** | 足以推导整条记录、且去掉任一 span 则不可推导的证据 span 集合（含必要的规则路径与版本链） | 不是 gold 的“唯一答案”；同一记录可以有多组合法最小证明 |
| **LABEL（判定标签）** | 标注者对“金标在该维度是否正确”的离散判断 | 不是对 derived 的打分 |
| **MATCH / CONFIRMED** | 标注者独立复核后**同意**金标（金标在该维度正确） | 不表示“我猜对了” |
| **MISMATCH / SCOPE_ERROR / VERSION_ERROR / INSUFFICIENT / FABRICATED** | 标注者认为**金标在该维度有错**（关键错误，进入仲裁） | 不是标注者自评错误 |
| **NOT_MINIMAL** | 金标记录值正确，但证书多引用了不必要的 span（非关键） | 不是关键错误；不隔离金标记录 |
| **UNDECIDABLE** | 依据卷宗与规则**无法唯一判定**（卷宗缺失/冲突不可解/遮蔽不足等） | 不是“懒得看”；必须写明理由 |
| **qualification / 资格测试** | 在 20 道**已知正确**的合成校准题上验证标注者能正确确认金标 | 不是正式样本；不消耗 R28 held-out |
| **sealed / 密封** | 由 `seal_export.py` 补全哈希并加密封块的 JSONL | 不是加密；浏览器导出未密封前不得统计 |

**编号约定：** `V*` 值维度子检查；`S*` 范围子检查；`R*` 规则版本子检查；`P*` 证明子检查；`H1/H2/H3` 三道人工门；`K1–K8` 关键错误编号。

---

## 2. 标注单位、样本与角色

### 2.1 标注单位

- 一个单位 = 一个**发布集 item**（`item_id`），包含：public 卷宗（≤12 文档、≤80 span）、问题文本、ruleset 元数据。
- **一题一记录、一题一族**（合同 §4/HA2）：因此样本内不存在同族重复题；不需要按族聚类。
- 不标注 `variants/` 对照渲染：双渲染一致性由 HA8 机器检查（`solver_facts` + `decision_record_flat` 逐字节），不属于人工样本。
- 不标注 held-out 测试集的 40 题（资格测试用**合成校准题**，见 §6.3）。

### 2.2 样本

- 抽样方案、种子、分层与确定性复现见 `SAMPLING_PLAN.md`。
- 100 个 slot 的清单见 `sample_ids.json`（构建前是设计 slot；构建后由 `make_design.py resolve` 绑定真实 `item_id`）。
- 绑定前后的唯一合法差异是 `item_id` 映射；**不得**在绑定后增删或更换 slot。

### 2.3 角色

| 角色 | 资格 | 禁止 |
|---|---|---|
| 标注者 A | 通过资格测试（§6.3）；未参与 R28 数据构建 | 不看 B 的判定；不看 gold 直到阶段 2；不修改数据 |
| 标注者 B | 同上 | 同上；不得使用 A 的导出文件 |
| 仲裁者 C | 未参与 A/B；理解本协议与 R28 规则；可查看 A/B 判定与 gold | 不得在无理由时覆盖 A/B；不得把 UNDECIDABLE 强改为 CONFIRMED |
| 数据管理员 | 运行工具、密封导出、生成报告；不修改 labels | 不得代填/改写标注者的判定 |

所有角色必须签署“保密与利益冲突声明”：不得将 R28 public/private 数据上传到任何外部服务；不得把 gold 提供给 A/B 的阶段 1；不得用本数据训练/微调模型。标注者报酬与知情同意按机构要求单独记录（本协议不代替伦理审查）。

---

## 3. 四维判定规范

### 3.0 通用判定顺序

对每一题，在阶段 2 依次判定 V → S → R → P。每个维度只允许一个 verdict。若前一维度为关键错误，仍必须完成其余维度（不得跳过；报告需要完整分歧画像）。

判定必须基于**本题 public 卷宗**与**该题 gold 的证书字段**（`minimum_evidence_spans` / `rule_path` / `revision_chain` / `authority_decision` / `why_not_distractor`）。不得引用其他题的答案、不得引用模型输出、不得引用外部知识。

---

### 3.1 维度 V：值（`decision_record_flat` 12 字段）

#### 3.1.1 检查对象

12 字段（名字冻结，不得改写）：

`batter_runs`, `bowler_runs`, `counts_in_over`, `delivery_status`, `dismissal`,
`ledger.BATTER`, `ledger.BYE`, `ledger.LEG_BYE`, `ledger.NO_BALL_EXTRA`, `ledger.PENALTY`, `ledger.WIDE_EXTRA`, `total_runs`

- `V0` 结构/值域：字段齐全、类型正确、非负、枚举合法（`delivery_status ∈ {LEGAL, NO_BALL, WIDE, DEAD_REBALL}`；`dismissal ∈ {NONE, BOWLED, LBW, CAUGHT, STUMPED, RUN_OUT, OBSTRUCTING_FIELD, HIT_BALL_TWICE}`）。
- `V1` 契约级一致性（只包含冻结合同明写的规则）：`WIDE → ledger.BYE = ledger.LEG_BYE = 0`；`DEAD_REBALL → 所有 ledger 字段 = 0 且 dismissal = NONE`；`ledger.BYE` 与 `ledger.LEG_BYE` 互斥。
  - 以上规则由 `scripts/common.py::check_record_consistency` 与 HTML 工具同款实现；工具“检查记录一致性”按钮给出的错误必须清零才能锁定派生值。
- `V2` 不由标注者手算的跨字段关系：`counts_in_over` 与 `delivery_status` 的对应、`batter_runs` 的上界、`total_runs`/`bowler_runs` 与各 ledger 的算术恒等式，**冻结合同均未写死**（真实 R28 样本已出现 `LEGAL` 且 `counts_in_over=false`、`batter_runs=11` 的记录）。这些关系由 solver 证书与重推负责（HA7），标注者**不得**把它们当作金标错误规则；工具也不会因此阻止锁定。

#### 3.1.2 字段级判定

对每个字段：

| 字段级标签 | 精确条件（可机械复核） |
|---|---|
| `MATCH` | 标注者从卷宗独立推导出的字段值与 gold 字段值**完全相等**（类型与值都相等；布尔 `false ≠ 0`）。 |
| `MISMATCH` | 推导值与 gold **不相等**，且标注者能在卷宗中指出支持自己值的最小证据。 |
| `UNDECIDABLE` | 卷宗中存在不可消除的歧义/缺失/遮蔽，标注者无法在不猜测的前提下确定唯一值；**必须在 note 写出缺失/歧义的具体 span 或文档**。 |

**维度 V verdict 的合成规则（必须机械执行，不得人工覆盖）：**

1. 若任一字段为 `MISMATCH` → `MISMATCH`（关键错误）。
2. 否则若任一字段为 `UNDECIDABLE` → `UNDECIDABLE`。
3. 否则 → `MATCH`（全部 12 字段 MATCH）。

> 端点口径说明：预注册主端点只使用 9 个信息字段（`batter_runs, bowler_runs, counts_in_over, delivery_status, dismissal, ledger.BATTER, ledger.NO_BALL_EXTRA, ledger.WIDE_EXTRA, total_runs`）。人工核验对 **12 字段全部**检查，因为 record-exact 门槛需要全字段正确；但报告必须同时给出 9 字段与 12 字段的分列统计，不得用 12 字段替代主端点（预注册 ZR2）。

#### 3.1.3 关键错误 K1

`MISMATCH` 是 K1（关键错误）。**注意：** K1 指“金标可能错”，不是“标注者算错”。仲裁者按 §7 判定责任归属；只有最终归因 `GOLD_DEFECT` 的 K1 才触发金标隔离与 H2 失败。

---

### 3.2 维度 S：范围（scope）

“范围”= 证据与规则的适用范围，**不是**数值值域。必须检查以下 5 项，并给出维度 verdict。

| ID | 检查 | 通过条件 |
|---|---|---|
| `S1_source_in_scope` | 决定性来源是否在本题范围内 | gold 的 `authority_decision`（或等价字段）所选文档/span 属于本题卷宗，且与题目所声明范围（比赛/局/轮次）一致；不得把同一球员在其他局/其他比赛的记录借来。 |
| `S2_conflicts_enumerated` | 同议题冲突是否被穷举并裁决 | 卷宗内所有同议题、不同值的来源都被列出；每个被拒绝来源有明确规则依据（如 P-AUTH-2）；gold 的 `authority_decision` 未遗漏可影响答案的冲突源。 |
| `S3_masked_cells` | 遮蔽 cell 处理 | 被遮蔽的值不作为任何证据；若 gold 使用了被遮蔽值 → 失败。 |
| `S4_exclusions` | 题外材料排除 | 相似投球/近重复/其他局的 span 未被当作本题证据；`why_not_distractor` 对每个被引用的近重复给出排除理由。 |
| `S5_boundary` | 边界 | 本题的 match/innings/over 边界没有被跨越；跨边界取值即为失败。 |

**verdict 规则：**

| verdict | 精确条件 |
|---|---|
| `CONFIRMED` | S1–S5 全部通过。 |
| `SCOPE_ERROR`（关键错误 K2） | 任一项失败，且标注者能指出具体文档/span 与规则依据。 |
| `UNDECIDABLE` | 卷宗不足以判定某一项（例如权威政策缺失、遮蔽导致无法确定来源），且不是标注者知识不足；必须写明缺什么。 |

**与 D3 机制的关系：** R28 的 D3 剂量（`scope_decisions`）会引入冲突源与 masked cell；S2/S3 是 D3 的直接人工检查。D3 仍为 UNTESTED 机制（合同 §2），人工确认只验证“实现正确”，**不构成 D3 提高难度的证据**。

---

### 3.3 维度 R：规则版本（rule_version）

| ID | 检查 | 通过条件 |
|---|---|---|
| `R1_ruleset_identity` | ruleset 身份 | gold 的 ruleset 标题与生效日期 = 本题卷宗声明的 ruleset；不得使用其他版本。 |
| `R2_revision_selection` | revision 选择 | 若存在版本链，选中的 revision 必须符合冻结策略：`HIGHEST_REVISION`（最高生效版本）或 `LAST_PRE_LOCK`（锁定前最后版本）；策略由本题规则/合同指定。选错版本 = 失败。 |
| `R3_revision_chain` | 版本链完整性 | gold 的 `revision_chain` 覆盖所有可影响答案的版本，版本身份与生效时间可核，链中每一步可回放；不得跳过被替代值。 |

**verdict 规则：**

| verdict | 精确条件 |
|---|---|
| `CONFIRMED` | R1–R3 全部通过。 |
| `VERSION_ERROR`（关键错误 K3） | 任一失败，且可指出错误版本/缺失链接。 |
| `UNDECIDABLE` | 版本链/生效时间本身不可判定（卷宗缺失）。 |

**与 D2 机制的关系：** D2 剂量（`temporal_joins`）要求真实 revision chain；R2/R3 是 D2 的人工检查。同样，这不构成 D2 提高难度的证据。

---

### 3.4 维度 P：最小证明（proof）

证明集合的判定**不是**“与 gold 的 span 集合逐项相等”。同一记录可以有多个合法最小证明；因此按性质判定：

| ID | 检查 | 操作步骤（可机械复核） |
|---|---|---|
| `P1_sufficient` | 充分性 | 用所选 span + 规则路径 + 版本链，能否逐步推出 12 字段记录？对每个字段写出一条推导链（工具中记 note；至少列出字段→span）。存在字段无法推导 → 不充分。 |
| `P2_minimal` | 最小性 | 逐个移除所选 span：若移除某个 span 后仍能推出全部 12 字段，则该 span 冗余 → 不最小。至少找到一个冗余 span 即可判 `NOT_MINIMAL`。 |
| `P3_faithful` | 忠实性 | 每个 span_id 必须存在于本题 public 卷宗；角色/关系必须与卷宗事实一致；不得引用近重复/干扰 span；不得编造 span_id。 |

**verdict 规则：**

| verdict | 精确条件 | 关键性 |
|---|---|---|
| `CONFIRMED` | P1 充分 且 P2 最小 且 P3 忠实。 | — |
| `NOT_MINIMAL`（K4，非关键） | P1 充分、P3 忠实，但 P2 失败。必须列出冗余 span_id。 | 非关键；记录值仍可确认 |
| `INSUFFICIENT`（K5，关键） | P1 失败。必须列出无法推导的字段。 | 关键 |
| `FABRICATED`（K6，关键） | P3 失败：不存在的 span、错误的角色/关系，或把被明确排除的近重复当作证据。 | 关键 |
| `UNDECIDABLE` | 卷宗无法支持判断（如 span 缺失、文本被遮蔽）。 | 进入未裁决 |

**gold 集合与标注者集合的关系（仅描述性，不参与 verdict）：** 报告可给出 Jaccard、`excess_span_ids`、`missing_span_ids`。若标注者找到更小的充分集合而 gold 集合冗余 → gold 的 proof verdict 为 `NOT_MINIMAL`；若 gold 集合更小但标注者无法用其推出 → gold 为 `INSUFFICIENT`（需仲裁）。

---

## 4. 盲法与流程（五阶段）

### 4.1 阶段 0：准备

1. 数据管理员确认：R28 构建已冻结、`build_index.json` 已发布、`sample_ids_bound.json` 已绑定、`bundle_public.json` / `bundle_gold.json` 已生成并通过泄漏筛查。
2. 标注者 A/B 完成培训（本协议 + 2 道公开示例）、通过资格测试（§6.3）、签署保密声明。
3. A/B 各自独立工作，**不共享**导出文件、不讨论具体题目。

### 4.2 阶段 1：盲推导（DERIVED）

- 只加载 `bundle_public.json`；**不得加载** `bundle_gold.json`。
- 对每题填写：12 字段记录、scope 五项、规则版本三项、最小证明 span 集合。
- 工具在“锁定”时校验记录一致性（§3.1.1）；记录不合法（如 `WIDE` 带 BYE）时禁止锁定，必须回到卷宗重查。
- 锁定后派生值冻结；阶段 2 不允许修改。
- 导出：`annotations_derived_<A|B>.jsonl` → `seal_export.py --kind DERIVED`。

### 4.3 阶段 2：金标揭示与判定（VERIFY）

- 加载 `bundle_gold.json` 与已密封的 DERIVED 文件。
- 对每题逐维判定（§3）；字段级标签 12 个；scope/rule_version/proof 各一个 verdict。
- 判定必须引用卷宗/规则/证书；`UNDECIDABLE` 必须写理由。
- 导出：`annotations_verify_<A|B>.jsonl` → `seal_export.py --kind VERIFY`。
- **顺序强制：** 先锁定阶段 1，再加载 gold。工具/日志会记录 `locked_at_utc` 与 `verified_at_utc`；若某人先看 gold 再补 derived，视为协议违规（该标注者全部数据作废并重做）。

### 4.4 阶段 3：和解（RECONCILIATION）

- 数据管理员运行 `agreement.py`，生成 `disagreements.jsonl`。
- 仅对分歧条目，A/B 各自看到对方**判定 + 理由**（不看对方未分歧的题），可提交一次书面解释；**不得直接改标签**。最终仍以各自阶段 2 的标签为准，除非双方书面确认同一修正（修正必须记录理由与时间）。
- 和解后剩余的标签分歧进入仲裁。

### 4.5 阶段 4：仲裁（ADJUDICATION）

- 仲裁者 C 仅看分歧条目：public 卷宗 + gold 证书 + A/B 标签与理由。
- 按 §7 的判定树给出 `final_label` 与 `attribution`；必须写理由。
- 无法裁决时：`final_label = UNDECIDABLE`，`attribution = UNRESOLVED`。不得为了“通过”强行选正向标签。

### 4.6 阶段 5：合并报告

- `adjudicate.py` 合并：非分歧用双方一致标签；分歧用仲裁标签；重算 H1/H2/H3。
- 输出 `HUMAN_VERIFICATION_REPORT.json`、`final_labels.jsonl`、`gold_defects.jsonl`（如有）。
- 报告状态只有 `PASS` / `FAIL` / `NOT_EXECUTED`；只有 `PASS` 才可声称“人工双标核验通过”。

---

## 5. 判定示例（用于培训；非真实数据）

**示例 1（V 维度 MISMATCH）：** 卷宗写“extras: bye=0, leg-bye=1”，gold `ledger.LEG_BYE=1`，标注者推导也是 1 → `MATCH`。若 gold 写 `ledger.BYE=1` → 标注者字段 `MISMATCH` → V=`MISMATCH`，K1。

**示例 2（V 维度 UNDECIDABLE）：** 卷宗唯一记录总分的 cell 被遮蔽，且无其他可核来源 → `total_runs` 无法确定 → `UNDECIDABLE`（不是猜 0）。

**示例 3（S 维度 SCOPE_ERROR）：** gold 选了广播日志的 S2 值，但政策 P-AUTH-2 明写“记分册优先”，且记分册有不同值 → S2 失败 → `SCOPE_ERROR`，K2。

**示例 4（R 维度 VERSION_ERROR）：** 版本链 v1（2026-01-01）与 v2（2026-09-01），政策要求最高生效版本；gold 选了 v1 → `VERSION_ERROR`，K3。

**示例 5（P 维度 NOT_MINIMAL）：** gold 证明包含 total span 和 distractor span；distractor 在 `why_not_distractor` 中被排除，不参与推导 → 去掉后仍充分 → `NOT_MINIMAL`（非关键）；若 gold 把 distractor 当作正向证据 → `FABRICATED`（关键）。

**示例 6（P 维度 INSUFFICIENT）：** gold 只引用 status span 与 total span，但 `ledger.BYE` 无来源 → 某字段无法推导 → `INSUFFICIENT`（关键）。

**示例 7（合法多解）：** 标注者用 span {A,B,C} 能推出全部字段且最小；gold 用 {A,B,D} 也能推出且最小。两者都为 `CONFIRMED`；不得因集合不同判错。报告只记 Jaccard。

---

## 6. 合格线与统计口径

### 6.1 H1：两标注者逐维一致率

对每个维度 `d ∈ {value, scope, rule_version, proof}`：

```
agreement_d = (A 与 B 的维度 verdict 相同的题数) / 100
```

通过条件（必须同时）：

1. 样本完整：A、B 各 100 题，无缺失、无重复、无样本外条目；
2. 对每个 d：`agreement_d ≥ 0.98`；
3. 9 个信息字段的字段级一致率与 12 字段一致率必须分列报告（不参与 H1 门，但不得省略）。

**为什么用原始一致率而不是 kappa：** 当金标绝大多数正确时，双方标签高度集中于正类，Cohen's κ 的期望一致率接近 1，分母趋零，单个分歧可使 κ 剧烈波动甚至无定义。协议要求同时报告 Cohen's κ（含按题 bootstrap 95% CI）、PABAK 与正例一致率，但**门只按原始一致率 98%**。κ 无定义（双方全部同一类别）时必须写 `null` 并注明“数学上限”，不得伪造为 1。

### 6.2 H2：确认金标缺陷 = 0

```
gold_defects = { item | 存在维度 d，最终标签 ∈ 关键错误集合(d) }
```

通过条件：`gold_defects = ∅`，且不存在 `UNDECIDABLE` 未裁决项、不存在缺失题。

- 若 `gold_defects` 非空：对应 item 进入 `GOLD_QUARANTINED`，金标必须由 t6 修复（确定性 solver/证书重生成）后重新双标该 item；**不得**在报告里把缺陷题剔除后声称样本通过。
- 若存在 `UNRESOLVED`：H2 不通过，报告状态 `FAIL`（或 `NOT_EXECUTED` 仅当未开始）。

### 6.3 H3：标注者资格

在 20 道**已知正确**的合成校准题（`fixtures/` / `scripts/make_synthetic.py` 生成，不消耗 R28 held-out）上：

| 指标 | 通过条件 |
|---|---|
| 12 字段派生准确率（与校准 gold 逐字段比较） | ≥98%（20×12=240 格，≤4 格错） |
| 每维“确认正确”准确率（期望标签：V=MATCH，S/R/P=CONFIRMED） | 每维 ≥98%（20 题，即 20/20） |
| 关键错误数（在校准题上错报金标有缺陷） | 0 |

资格测试未通过 → 重训后重测；最多 2 次，仍失败则更换标注者。资格结果由 `qualification.py` 从原始导出重算；`adjudicate.py` 会再次独立重算（不信任自报 JSON）。

### 6.4 报告必须给出的数字

- 每维 `n`、原始一致率、κ、κ 的 95% bootstrap CI、PABAK、正例一致率、分歧数；
- 12 字段逐字段一致率；
- 分歧总数（维度级 / 字段级分列）；
- 四维全同题比例；
- H1/H2/H3 与总状态；
- 金标缺陷题清单（如有）与隔离状态；
- 明确声明 `human_gold_produced = false`。

---

## 7. 冲突处理与仲裁判定树

### 7.1 分歧类型

| 类型 | 例子 | 处理 |
|---|---|---|
| 维度级分歧 | A: V=MATCH，B: V=MISMATCH | 必须仲裁 |
| 字段级分歧但维度一致 | A/B 都 V=MISMATCH，但错在不同字段 | 记录字段差异；维度最终 MISMATCH；在缺陷报告中列出并集字段；如双方对字段责任有争议则仲裁字段 |
| 一方 UNDECIDABLE | A: CONFIRMED，B: UNDECIDABLE | 必须仲裁（B 需说明缺什么） |
| 双方不同关键错误 | A: SCOPE_ERROR，B: VERSION_ERROR | 必须仲裁（可能两者都错） |

同一 item 的多个维度分歧分别仲裁；不得“一揽子”覆盖。

### 7.2 仲裁判定树（按顺序执行，先满足者生效）

1. **重放卷宗**：仲裁者独立从 public 卷宗推导 12 字段、scope、规则版本、证明。
2. **可唯一确定** → 以重放结果为准：
   - 若重放与 gold 一致 → 最终正向标签（MATCH/CONFIRMED），归因给判错的一方（A_ERROR / B_ERROR / BOTH_ERROR）。
   - 若重放与 gold 不一致 → 最终关键错误，归因 `GOLD_DEFECT`。
3. **不可唯一确定**（卷宗缺失/遮蔽/冲突政策缺失）→ `UNDECIDABLE` + `UNRESOLVED`；该题不得计入“已验证”，H2 不通过。
4. **禁止的 tie-break：** 不得以“少数服从多数”“资历”“为了让样本通过”为依据；不得参考其他题答案；不得参考模型输出。

### 7.3 归因码

| attribution | 含义 | 是否隔离金标 |
|---|---|---|
| `ANNOTATORS_AGREE` | A/B 标签一致（无需仲裁） | 仅当标签为关键错误时隔离 |
| `A_ERROR` | A 判错，金标正确 | 否 |
| `B_ERROR` | B 判错，金标正确 | 否 |
| `BOTH_ERROR` | A/B 都判错，金标正确 | 否 |
| `GOLD_DEFECT` | 最终判定金标错误 | **是** |
| `UNRESOLVED` | 无法裁决 | 是（不得声称通过） |

**约束（代码强制）：** 最终标签为关键错误时必须 `GOLD_DEFECT`；`UNDECIDABLE` 必须 `UNRESOLVED`。违反则 `adjudicate.py` 直接报错，不生成报告。

---

## 8. 金标缺陷处理（不得静默修复）

1. `gold_defects.jsonl` 是唯一缺陷清单；每行包含 item、维度、最终标签、A/B 标签、归因、理由。
2. 缺陷 item 进入 `GOLD_QUARANTINED`：在论文/数据卡中标注“不可用于确认性分析，待修复”。
3. 修复只能由数据构建方执行：重推 solver、重生成证书；**不得手改金标值**。修复后必须重新执行该 item 的双标（阶段 1–4）。
4. 修复记录写入缺陷清单的 append-only 字段（`repair_id`、`reverified_at_utc`、`reverify_result`）。
5. 若缺陷涉及 >2% 样本（>2/100）或涉及同一机制 ≥2 题：停止发布，升级为设计/构建问题，走合同 amendment。

---

## 9. 数据保密、伦理与利益冲突

- R28 public/private 数据、gold、证书、人工标签均不得上传到任何外部服务/API；本工具离线运行，产物只保存在授权工作区。
- 标注者只能看到自己被分配的 bundle；不得查看他人的导出文件或 gold 文件（阶段 1）。
- 标注者不得参与 R28 的模型训练/提示词调参/数据构建；如参与过，必须披露并按利益冲突处理（不得担任该题仲裁者）。
- 标注者报酬、工时与知情同意按机构要求单独记录；本协议不替代伦理审查。建议工作量：100 题 × 阶段 1（约 4–6 分钟/题）+ 阶段 2（约 2–3 分钟/题）≈ 10–15 小时/人；仲裁约 1–3 小时（取决于分歧数）。
- 发现数据泄露（gold 出现在 public）→ 立即停止标注，报告数据管理员与 t8；不得继续用该 bundle。

---

## 10. 工具与产物（可执行命令）

| 步骤 | 命令（在工作区根执行；`KIT=VETT_R28_DIFFICULTY_20261112/04_verify/human_verification_kit`） | 产物 |
|---|---|---|
| 绑定样本 | `python $KIT/scripts/make_design.py resolve --index <build_index.json> --sample $KIT/sample_ids.json --out <bound> --receipt <receipt> --strict` | `sample_ids_bound.json` |
| 生成 bundle | `python $KIT/scripts/build_bundle.py --build-dir <candidate> --sample <bound> --out-dir <bundle>` | `bundle_public.json`、`bundle_gold.json`、`bundle_map.json` |
| 预标注（可选） | `python $KIT/scripts/preannotate.py --bundle <bundle_public.json> --out-dir <pre> --adapter local` | `preannotations.jsonl`（仅提示） |
| 阶段 1（浏览器） | 打开 `tool/annotate.html`，加载 public bundle，导出 | `annotations_derived_<X>.jsonl` |
| 阶段 1（CLI） | `python $KIT/scripts/annotate_cli.py derive ...` | 同上 |
| 密封 | `python $KIT/scripts/seal_export.py --kind DERIVED --file <in> --out <sealed> --public-bundle <public>` | 密封 JSONL |
| 校验 | `python $KIT/scripts/validate_export.py --kind DERIVED --file <sealed> ...` | `VALIDATION_REPORT.json` |
| 阶段 2 | 浏览器加载 gold + 密封 DERIVED → 导出；或 CLI `verify` | `annotations_verify_<X>.jsonl`（再密封、校验） |
| 资格 | `python $KIT/scripts/qualification.py ...` | `qualification_<X>.json` |
| 一致性 | `python $KIT/scripts/agreement.py --a ... --b ... --sample <bound> --out-dir <agreement>` | `agreement_report.json`、`disagreements.jsonl` |
| 仲裁 | 浏览器仲裁页导出；或手写 JSONL（schema 见 `schema/adjudication.schema.json`） | `adjudications.jsonl` |
| 合并 | `python $KIT/scripts/adjudicate.py ...` | `HUMAN_VERIFICATION_REPORT.json`、`final_labels.jsonl`、`gold_defects.jsonl` |

**文件命名（强制）：** `annotations_derived_A.jsonl`、`annotations_verify_A.jsonl`、`adjudications.jsonl`、`agreement_report.json`。任何未密封文件不得进入统计；`seal_export.py` 失败必须停机排查，不得手工补哈希。

---

## 11. 变更控制

- 本协议版本 `ANNOTATION_PROTOCOL.v1` 与 kit 版本绑定。判定规则、合格线、维度定义、仲裁树在标注开始后**不得修改**；任何修改必须：
  1. 由 captain 上报用户批准；
  2. 写入 `04_verify/human_verification_kit/PROTOCOL_AMENDMENTS.jsonl`（append-only，含 before/after、理由、批准人、时间）；
  3. 版本号升级（v1 → v2），并重做受影响的标注。
- 若发现协议本身有歧义：停止标注，报 captain，按上述流程修订；不得由单个标注者自行解释。
- 本协议与 `VETT-R28-CONTRACT` / 预注册冲突时，以预注册为准；本合同只增加人工核验流程，不改变端点、阈值、停止规则或报告口径。

---

## 12. 无歧义自检清单（发布前必须逐条打勾）

- [ ] 每个维度的 verdict 集合与判定条件在 §3 中互斥且穷尽（同一证据不可能同时满足两个 verdict）。
- [ ] “范围”从未被解释为数值值域；值域/类型明确归入 V0。
- [ ] MATCH/CONFIRMED 与 MISMATCH/关键错误的方向从未写反（“更难”不涉及本协议）。
- [ ] 所有关键错误编号 K1–K6 与 `common.CRITICAL_NEGATIVE` 完全一致。
- [ ] NOT_MINIMAL 明确为非关键；FABRICATED 明确为关键。
- [ ] 98% 的计算分母写明（每维 100 题；资格为 20 题/240 字段）。
- [ ] κ 无定义时的处理写明（报告 null，不伪造 1；不作为门）。
- [ ] 仲裁树的每一步都可由第三人机械执行；没有“视情况而定”。
- [ ] 未裁决项的后果写明（H2 失败，不得声称通过）。
- [ ] “本协议不产生人工金标”“论文阻断项”在文档开头与结尾各出现一次。
- [ ] 浏览器工具与 CLI 输出的 schema 一致；密封步骤不可省略。
- [ ] 所有命令可在工作区根直接复制执行；路径变量只有一个 `KIT`。

---

## 13. 结尾声明（重复，防止被忽略）

> **本协议不产生人工金标。** 金标始终是确定性 solver 输出；人工双标只确认或隔离它。
> **在 `adjudicate.py` 对真实 R28 数据返回 `PASS` 之前，论文必须把“金标未经独立人工双标核验”列为发表阻断项。**
