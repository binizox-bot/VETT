# R28 决策总报告（t11）

> **三个问题，只给数字与区间，不给安慰。**
> 团队：`vett-r27-opt` ｜ 作者：`measurement_auditor` ｜ 日期：2026-11-13
> 输入（只读）：`eval_runs/t19_e1e5_20261112/`（E1–E5）、`04_verify/`（t8/t20）、`04_verify/J_GATE.json`（t17 J 门）、`03_build/local/`（t14/t18/t21）、`05_release/academic_package/`（t9）、`05_release/paper/`（t23）、`05_pipeline/runs/live_full/gate_ledger.jsonl`（t13/t20）。
> 数字纪律：本报告只引用上述来源；不重算、不换指标、不事后改口径。所有 CI 均为 95%。付费 API：**¥0**；云端调用：**0**。

## 0. 三行结论

| 问题 | 判决 | 决定性证据 |
|---|---|---|
| **Q1 更难了吗** | **不成立（不成立就是“不成立”）** | E1 drop **0.557pp**，CI **[−0.801, +1.846]**（跨 0）；E2 剂量 **REJECTED**；E3 **H3=False**；且 E4 的 V0=0.125 证明模型不读证据——呈现侧加难在原理上无效 |
| **Q2 更有解释性吗** | **机械可验证性成立；模型“依赖证据”的解释忠实度不成立（S12 撤回）** | 证书 320/320、solver 重推 100%、`rule_path` 只含承载算子；但 V0 置换后 87.5% 答案改变，解释主张 `EXPLANATION_CLAIM_NOT_ESTABLISHED` |
| **Q3 更能发表吗** | **作为“能力基准”不可发表（四条限定缺一即 FAIL）；只能作为测量/零结果/验证装置论文发表** | T1 是词表匹配（余量 +0.125）；E5 UNTESTED 且区分度撤回；T3 n=12 仅描述；κ 全部 n<30 不估计；人工双标未执行、规则文本许可未闭环 |

---

## 1. Q1：更难了吗

### 1.1 E1 主端点（严格配对，n=319）

| 指标 | 值 | 来源 |
|---|---:|---|
| 配对 n | **319**（320 对中 1 对因 published 持久截断被排除；失败走 conformance） | `analysis.json#/E1` |
| 发布版信息字段准确率 | **59.56%**（1710/2871）Wilson95 [0.5775, 0.6134] | 同上 |
| 对照版信息字段准确率 | **60.12%**（1726/2871）Wilson95 [0.5831, 0.6189] | 同上 |
| **配对差 drop = control − hard** | **+0.557pp** | 同上 |
| 95% CI（按题 / 按族 bootstrap 两版取更保守下界） | **按题 [−0.801, +1.846]**；按族 [−0.766, +1.881]；保守下界 **−0.801pp（跨 0）** | `analysis.json#/E1/drop_pp_ci95_*` |
| 配对方向（逐题准确率比较） | control 更准 **69** / hard 更准 **47** / 并列 **203**；符号检验双侧 p=**0.0507** | `analysis.json#/E1/paired_accuracy_direction` |
| 9/9 信息字段全对 McNemar | b=2, c=1, 双侧 p=**1.0000** | `analysis.json#/E1/mcnemar_correct9` |
| **整记录 exact（12/12 字段）** | **5/638 = 0.78%**（hard 2/319、control 3/319；Wilson95 [0.34%, 1.82%]） | `analysis.json#/E1`、`e1_raw.jsonl` |
| 效应量 | Cohen's h=**−0.011368**；OR=**0.977077** | `05_release/paper/NUMBERS.json#/E1` |
| 预注册判定 | `primary_outcome=DIRECTION_ONLY`、`headline=DIRECTION_ONLY + DEGRADED`、`harder_claim_permitted=false` | `analysis.json#/claim` |

辅助一致性：ITT 敏感性（失败按 0）drop=0.833pp，CI [−0.590, +2.222]；空配对（四剂量全 0，n=72）drop=**−0.309pp**（两臂 prompt 全同，placebo 通过）；active 配对（n=247）drop=0.810pp。

### 1.2 E2 剂量-反应：**REJECTED**

| 指标 | 值 |
|---|---|
| DL 题数 | 192（D1–D4 × 剂量 0/1/2 × 16） |
| 信息字段准确率 dose 0/1/2 | **59.375% / 62.674% / 60.938%** |
| 相对 dose0 的 Δ | +3.299pp / +1.563pp（方向与“加难”相反） |
| OLS 斜率（逐题准确率，mechanism FE，HC1） | **+0.781pp/step**，CI **[−1.815, +3.402]**；单侧 p(β<0)=0.280 |
| 单调递减 | **False**；四机制支持数 **0/4** |
| 判决 | **HYP-R28-DOSE = REJECTED**（非单调 + 反向 + |效应|<10pp + CI 含 0，四条拒绝条件全部命中） |

来源：`analysis_e2.json`、`05_release/paper/NUMBERS.json#/E2`。

### 1.3 E3 机制归因：**H3=False**

| 主效应 | β(pp) | 95% CI | Holm p (m=4) |
|---|---:|---|---:|
| D1 证据跳数 | −1.18 | [−7.06, +4.70] | 1.000 |
| D2 修订链 | −1.87 | [−7.77, +4.03] | 1.000 |
| D3 权威裁决 | −2.22 | [−8.10, +3.66] | 1.000 |
| D4 干扰同构 | −6.11 | [−11.99, −0.24]（未校正名义显著） | **0.166** |

- **H3 不成立**：Holm 后无主效应；D4 名义 p=0.041，但 Holm 后 0.166。
- **交互模型 `NOT_ESTIMABLE_WITH_16x8`**：16 格 × 8 题无法识别 6 个二阶交互；不报推断结论。
- 来源：`analysis_e3.json#/coefficients`、`05_release/paper/NUMBERS.json#/E3`。

### 1.4 三条基线与 claim gates

| 基线（R28 同集） | 准确率 | 与 hard(59.56%) 的关系 | 门 |
|---|---:|---|---|
| 常数先验（LOFO） | **55.03%** | hard 更高（对“更难”方向不利） | G2 FAIL（skill_hard=**+0.1007**） |
| 只看题面 TF-IDF+LR | **54.76%** | hard 更高 | — |
| 族名众数（泄漏轴） | **53.16%**（值平衡 10.39%、lift −3.54pp、p=0.146） | — | HA10 PASS |
| anchor 众数（R26.15 参考 73.33% / exact 32%） | **NOT_MEASURABLE**（R28 无 anchor 字段） | 无法比较 | **G1/G1r = UNTESTED → DEGRADED** |

**G1 不可执行本身就是判决的一部分**：按预注册 `baseline_gate.fail_safe`，anchor 同集重测不可测 → G1=UNTESTED → **不允许任何 HARDER 宣告**。G2 又 FAIL（发布版反而高于常数先验 10.07 个百分点，skill=+0.1007）。来源：`01_measurement/baselines_same_set.json`、`analysis.json#/gates`。

### 1.5 Q1 的收束：E1 的零结果必须由 E4 解释（这是本节最重要的一段）

E4 的 V0 是“只把文档/span 顺序反转、文本多重集与 id 全部守恒、金标逐字节不变”的对照：

- **stability⁰ = 0.125（5/40）**，Wilson95 [0.055, 0.261] → **仅打乱文档顺序，87.5% 的情况下答案就变了**（门 ≥90%，FAIL）。
- stability⁻（改既有非决定性事实、金标不变，substitution n=32）= **0.500（16/32）**，CI [0.336, 0.664]（门 ≥80%，FAIL）。
- flip⁺（改决定性事实、金标改变）= **0.525（21/40）**，CI [0.375, 0.671]；**低于随机地板 0.875**（门 ≥2× 随机，FAIL）。

**因此，Q1 的正确表述是：**

> **E1 的 0.557pp 不是“数据集没变难”，而是“这个模型压根没在解题”。** 如果模型本来就不读证据（V0 单独就翻车），那么把证据呈现得更难当然不会让它更糟。**在模型不读证据的前提下，任何呈现侧的操纵都必然无效。**

这条单一机制同时解释：E1（无难度效应）、E2（非单调）、E3（无机制归因）、E4（三门全败）、record-exact 0.78%。**Q1 判决：不成立。**

---

## 2. Q2：更有解释性吗

### 2.1 正面：证书的机械可验证性成立

| 指标 | 值 | 来源 |
|---|---|---|
| 证书覆盖 | **320/320** | `04_verify/INDEPENDENT_VERIFICATION.md`、`BUILD_ACCEPTANCE` |
| 冻结 solver 重推金标 | **100%**（320/320） | 同上 |
| `rule_path` 只含承载算子 | **0 违规** | 同上 |
| 非承载算子登记 | **564** 条进入 `presentation_only_operators` / `mechanism_witness.presentation_only_registry` | 同上 |
| 双渲染隔离 | facts + record **320/320 逐字节相同**，仅呈现层不同 | t8 数据健康 PASS |

**机制归因硬约束**：只能对 `mechanism_witness.json` 中**未被标 PRESENTATION_ONLY** 的机制（D1–D4）归因；**564 条非承载算子只能计入呈现层，不得计入“更难”**。D1/D4 的机制可见性另见 §3.5（NOT_INSTRUMENTED）。

### 2.2 负向发现：31.6% 的规则引用是装饰性的（独立成节）

- 渲染规则 span 共 **1,546** 条，其中 **488 条（31.6%）从未承载**推导；
- **360/360 题**至少含一个非承载算子；
- `BAT_CREDIT` 渲染 **118** 次、`NB_COUNT` **100** 次、`WIDE_COUNT` **53** 次，**从未必要**；
- `COUNTS_IN_OVER` 仅 317/360 必要；`rule_path` 1199 条与必要算子 0 交集。

这直接推翻“多写规则文本 = 推导更深”的直觉；也是本计划最硬的负向测量结论之一。来源：`03_build/reports/derivation_depth_witness.json`、`mechanism_witness.json`、t9 数据卡 B3。

### 2.3 E4 三孪生：三条门全部 FAIL，`EXPLANATION_CLAIM_NOT_ESTABLISHED`

| 指标 | 实测 | 95% CI | 门 | 判定 |
|---|---:|---|---:|---|
| flip⁺ | **0.525**（21/40） | [0.375, 0.671] | ≥2× 随机地板（0.875） | **FAIL**（且低于地板） |
| stability⁻（substitution，n=32，主指标） | **0.500**（16/32） | [0.336, 0.664] | ≥80% | **FAIL** |
| stability⁻（introduced，n=8，单列不合并） | 0.125（1/8） | [0.022, 0.471] | 不合并 | 仅记录 |
| stability⁰（V0 顺序置换，n=40） | **0.125**（5/40） | [0.055, 0.261] | ≥90% | **FAIL** |

- V− 可用率（320 题机械判定）：substitution **271/320**、introduced **49/320**、none **0**；
- `S12=True` → **`EXPLANATION_CLAIM_NOT_ESTABLISHED`**：不得把证书当作“模型依赖证据”的证明；
- conformance：**120/120 `done_reason=stop`**、parse_ok 100%（num_predict 实际 640，未截断）。
- **append-only 说明**：E4 是 t19 完成后的补充实验（`supplemental_to_t19: true`，`generated_at_utc=2026-11-12T15:24:04Z`，输入 sha256 均已登记）；**原 t19 文件未改**（analysis.json / analysis_e1–e4.json / e1_raw.jsonl / E1_E5_REPORT.md 与 MANIFEST sha256 逐项一致）。
- 来源：`analysis_e4_supplemental.json`、`E4_SUPPLEMENTAL.md`、`e4_raw.jsonl`。

### 2.4 T2 偏好侧（辅助）

- 有效对 **317**（3 条 `INEFFECTIVE_CORRUPTION` 剔除：r28q_0067/0099/0159）；
- 序判定一致率 **0.9905（314/317）**，Wilson95 [0.9725, 0.9968]；t18 30 对校准 30/30；
- 绝对分只作描述，进阈值即 FAIL。

**Q2 判决：作为数据集属性，“证书可机械验证”成立；作为模型属性，“解释依赖证据”不成立（S12 撤回）。**

---

## 3. Q3：更能发表吗

**四条限定，缺一即 FAIL；四条全部命中 FAIL。**

### 3.1 限定一：T1 是词表/模式匹配倾向，不能当“读懂证据”的能力证据

| 指标 | 值 |
|---|---|
| 总体一致率 | **0.9750（312/320）**，Wilson95 [0.9515, 0.9873] |
| POS_OVERRIDE | **0.8333（40/48）**，Wilson95 [0.7042, 0.9130] |
| NEG_PLAIN / NEG_PROVENANCE_ADJACENT | 1.0 / 1.0 |
| 恒答 false 基线 | **0.8500（272/320）** → 总体余量仅 **+0.1250** |
| 错误集中度 | **8/8 错误全部落在 `authority_policy` 同一句式**；按 span role：`authority_policy` **0.7500（24/32）**，其余 role 1.0 |

**禁令（写入报告）**：**不得写“错集恰好等于词表不命中集 / 集合完全相同”**。verifier 实测：把 `controlling` 加入 `OVERRIDE_LEXICON` 后，词表不命中集变为 **0** 而错误仍是 **8**，等式即破（broad-semantic 变体同样 0/8）。该等式只是当时词表状态的偶然巧合，不能作为机制陈述。T1 可作标注劳动（过 0.85 门），但**不得**当作本地模型判断证据支持的能力证据。

### 3.2 限定二：E5 = UNTESTED，区分度主张已撤回

- 可执行模型数 **1**（仅 `qwen2.5:7b-instruct-q4_K_M`）；零付费硬约束禁止云端 1 + 云端锚点 1；
- 按预注册 S2：面板降级 → **DEGRADED/UNTESTED**、**撤回“任务有区分度”的主张**、不得判 PASS；
- **不得写成“E5 未跑”这种含糊表述**：这是已作出的否定性判决（E5 需要 ≥2 模型、最强−最弱 ≥25pp 才能建立区分度）。

### 3.3 限定三：T3 只有逐字段 verdict 可用（n=12 < 30，DESCRIPTIVE_ONLY）

| 指标 | 值 |
|---|---|
| 提报数 | 12（全部真错：overall=DEFECT 是平凡策略 12/12） |
| abstain / conformance | 12/12 PASS（**无区分度**） |
| 逐字段 verdict | **precision 0.9333（28/30）**；**recall 0.6087（28/46，漏 18）** |
| 云端自写 `correct_record` vs solver 金标 | **0.4514（65/144 字段）** → **模型输出绝不能当金标** |

### 3.4 限定四：κ 全部 n<30 → 不估计

- T1 R28 臂 n=**17**、T1 同刺激臂 n=**24**、T2 n=**16**：**均不估计**；
- 探索性合并（T1 两臂 n=41）：κ=0.8951，CI [0.7192, 1.0]，**只作量级、不得进主表**。

### 3.5 其他必报

| 项 | 值 / 状态 | 来源 |
|---|---|---|
| C_t14 跨实现一致性 | 仅 **17/24** 题同 span 可比（7 题不可比），**17/17 一致**；与同刺激臂合并 **2/41 = 4.88%**（<30%） | `J_GATE.md §3.1` |
| S1 span 主题 | **DESCRIPTIVE_ONLY**（R28 无机械主题真值；207 模型 + 96 机械回退 + 17 DEGRADED） | `J_GATE.md §2.3`、t14 |
| D1/D4 机制可见性 | **NOT_INSTRUMENTED**（T1v1 只筛修订/权威覆盖；false ≠ 剂量不可见） | t14 §3、`J_GATE.md` |
| J8 状态 | **PASS**、blocking=[]；内容摘要 `9b0f4d40…`；C1 账本 905/标注 320/变体 0；C2 raw 0/struct 0/unauditable 0；C4 71 缓存 0 错；C5 35 文件 0 生产引用 | `J_GATE.json/.md` |
| 协议终版 digest | PAMEND-004 后：`protocol.json` **1a87c316…c50c1293**、`PROTOCOL.md` **9758d0e1…7eb4300e**、`protocol_freeze.json` **ab18ee1b…0f0761697e**；`--check` **22/22 PASS**。任务书引用的 **a07463aa…02ff7a / 77caf7a0…e54475** 是 PAMEND-003 时值（PAMEND-004 扩了 r28* id 禁用模式） | `02_design/protocol_freeze.json`、`J_GATE.md §1` |
| R26.15 零漂移 | **165 文件 / 93,346,177 B / aggregate 343afde4…51bd**；总保护集 aggregate **66e108d8…a0433** | `INDEPENDENT_VERIFICATION.md §3` |
| R-R7 重放绑定 | 仅按当前解析器版本重放：**806/806 cache-key v2 独立复算**、旧模板 **0**、解析器不兼容 **0**；旧 `cost_ledger` 条目不计入 | `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json` D6、t13 |
| 数据健康 | 互异记录 320/320；恒定字段 0；BYE/LEG_BYE/PENALTY 96/78/153；status 166/100/53/1；合法 dismissal 10 + DEAD 1；solver 重推 0 失败；双渲染 0 失败；rule_path 0 违规 | t8 §5 |

**成本与耗时（全部本地、付费 API ¥0、云端 0 次）**

| 模块 | 调用/题数 | 墙钟 | 来源 |
|---|---:|---:|---|
| t18 能力矩阵 | 162 次全新调用 | 46.8s | t18 |
| t14 预标注 | **905** 次模型调用 | 195.836s | t14 REPORT |
| t19 E1 | 652 行（640 唯一对 + 12 重跑） | wall 合计 5,135.6s | `e1_raw.jsonl` |
| t19 E4 | 120 次 | wall 合计 466.5s | `e4_raw.jsonl` |
| t21 C1 | **2,835** 次 | 587.827s | t21 REPORT |
| t20 闭环验证 | 10/10 | **19.255s** | `CLOSED_LOOP_VERIFICATION.json` |

**DEGRADED / ESCALATED 清单（不掩盖）**

- 流水线 live_full：21 门 = **19 PASS / 2 DEGRADED**：`G_ANNOTATION_COVERAGE`（mode=mechanical_only，coverage=0.0）、`G_JUDGE_COMPARABILITY`（无 comparables）；
- t14：S1 **17 条 DEGRADED**（PARSE_FAILURE → 机械 PROVENANCE 回退）；
- t19：**1 条持久失败** `r28q_0117/published`（512 tokens 仍截断；双份保留，主分析排除该对）；
- t20 故障演练：D2 本地停服 → mechanical_only + **3 条 DEGRADED** + coverage 0；有界修复演示 **ESCALATED×1**（t13 单测/演练，非生产结论）；
- t8：`PASS_WITH_CAVEAT` 12 项 = 10 PASS + `PASS_WITH_DISCLOSURE`（时间戳回填）+ `PASS_WITH_CAVEAT`（GBK 复现，caveat 1 已由 t9 修复闭合；caveat 2 披露保留）。

**Q3 判决：作为“能力基准”不可发表（四条限定全 FAIL + 两项发表阻断）；作为测量/零结果/验证装置论文，证据链完整、可发表。**

### 3.6 四个发表阻断项 / 自纠固定段落

1. **人工双标未执行**：金标是 solver 生成的，t24 标注工具包 `ready_to_annotate=false`；这是发表阻断项，不是“待办”。
2. **MCC 规则文本许可未闭环**：数据 CC BY 4.0 / 代码 MIT 已定稿；规则摘要引用无再分发许可，发表前必须法律复核（B7）。
3. **审计产物时间戳曾回填**：`protocol_verify_result.checked_at` 曾被回填为 15:09:53Z，已在 `04_verify/PROTOCOL_VERIFY_RERUN_NOTE.json` 完整披露；规则已立：审计产物不得回填时间戳。t8 以 `PASS_WITH_DISCLOSURE` 记录，不掩盖。
4. **captain 两次同类错误（自纠）**：
   - “**剂量杠杆已验证**”——拿整级宏准确率 63.3/60.0/51.7 冒充同事实组配对比较；t3 逐对重算为 **5 降 / 4 升 / 1 平，均值 −3.3pp，符号 p=0.50**，断言错误；
   - “**S2 内容与 S1 相同**”——跨口径哈希比较（旧口径 `5d7efca5…` vs v2 `9b0f4d40…`）不可比，被 judge_architect 当场纠正。
   - **教训（写入验收规则）**：凡“看起来没变”或“看起来变难了”的主张，先问**这个比较能否被第二个人独立复算**；不能复算的比较不得进验收清单。

---

## 4. 零结果契约：哪些站得住、哪些被推翻

### 4.1 本报告直接写“不成立”的命题

| 命题 | 判决 | 原始数据路径 |
|---|---|---|
| R28 比 R26.15“更难” | **不成立**（drop 0.557pp，CI 跨 0；harder_claim_permitted=false） | `eval_runs/t19_e1e5_20261112/analysis.json` |
| 语义机制剂量↑ → 准确率单调↓（HYP-R28-DOSE） | **REJECTED** | `analysis_e2.json` |
| 机制可归因（H3） | **不成立**（H3=False；交互不可估） | `analysis_e3.json` |
| 模型依赖证据 / 证书可证明解释忠实度 | **不成立**（S12；解释主张撤回） | `analysis_e4_supplemental.json` |
| 任务有区分度 | **撤回**（E5 UNTESTED，S2） | `e5_availability.json`、`05_release/paper/NUMBERS.json#/E5` |
| 本地模型“读懂证据” | **不成立**（T1 词表匹配，余量 +0.125；D1/D4 NOT_INSTRUMENTED） | `03_build/local/t14/REPORT.md` |

### 4.2 Proposal 里被实测推翻的四条（必列）

1. **“呈现剂量已验证”** → 初稿据整级宏准确率 63.3/60.0/51.7 断言剂量杠杆有效；t3 同事实组逐对比较为 **5 降 / 4 升 / 1 平，p=0.50**。**该断言是错的。**
2. **“推导深度不可调”** → 初稿据此列为 REJECTED；t3 发现同事实组内 `rule_operators` 从 1→2→3→4 变化而金标逐字节相同；t5 逐算子消融证明 **1,546 条规则引用中 488 条（31.6%）非承载，BAT_CREDIT/NB_COUNT/WIDE_COUNT 从未必要**。**该断言也不对**（但换来了最硬的负向发现）。
3. **“记录空间接近上限”** → 初稿据 2 万次随机抽样只得 156 个互异记录，判断 160 题近天花板；t4 用分层定向枚举得到下界 **761**。**随机抽样不能估计可达空间。**
4. **“让数据集更难”** → 最初目标；实测本设计能操纵的是**呈现难度**，而呈现难度只值 **0.56pp**；且 E4 证明模型不读证据。**该目标在本设计下不成立。**

### 4.3 站得住的部分（同样要给证据）

| 资产 | 证据 |
|---|---|
| 金标可被确定性 solver 重推 | **320/320 = 100%** |
| 记录空间打开 | 互异记录 **320/320 = 1.0**（R26.15 为 16/100） |
| 族名捷径拆掉 | 值平衡 10.39%、lift −3.54pp、置换 p=0.146 |
| 证书可机械验证 | 320/320；rule_path 只含承载算子；564 条非承载登记 |
| 双渲染隔离 | facts + record 320/320 逐字节相同 |
| 闭环流水线 | 21 门、缓存可重放、熔断、降级、ESCALATED 均有实证（t20 10/10） |
| 统计修复可复算 | E2/E3 三个数值 bug 修前/修后表（E1_E5_REPORT §8），t8 独立复算一致 |

---

## 5. 下一步该改什么（R29+ 的前提）

1. **先换测量对象**：本轮所有呈现侧操纵（D1–D4）都在一个“不读证据”的 7B 上失效。R29 的第一个门槛应是**先找到一个对顺序置换稳定、对决定性事实敏感的模型**（V0 ≥90%、flip⁺ ≥2× 地板），再谈难度。
2. **难度必须来自事实/推导本身**：本设计的 `solver_facts` 与金标两臂逐字节相同，推导是同一个；只有扩求解器（多球累计、局内状态、后续击球顺序）才能让“更难”有可操纵空间。
3. **先做人工双标**：E 阶段不执行，任何“金标可信”的主张都是发表阻断项；t24 kit 已就绪。
4. **砍掉无效机制**：D1–D4 在本轮全部 UNTESTED→REJECTED（E2/E3/E4），文档数/上下文长度/bridge depth 早已 REJECTED；R29 不应再在这些机制上投入。
5. **报告口径固定**：主指标 = 信息字段 + 逐条件先验 skill；E1 配对 CI 必须报两版；record exact 单列；E5 缺面板就撤回区分度；T1 按 span role 分层披露。

---

## 6. 证据索引与复现

| 用途 | 路径 |
|---|---|
| E1–E5 全部数字 | `eval_runs/t19_e1e5_20261112/analysis.json`、`analysis_e1/e2/e3.json` |
| E4 补充（append-only） | `eval_runs/t19_e1e5_20261112/analysis_e4_supplemental.json`、`E4_SUPPLEMENTAL.md` |
| E1/E4 原始输出 | `eval_runs/t19_e1e5_20261112/e1_raw.jsonl`（652 行）、`e4_raw.jsonl`（120 行） |
| 独立验证 | `04_verify/INDEPENDENT_VERIFICATION.md`、`verification.json`（PASS_WITH_CAVEAT） |
| J 门（T1/T2/T3/κ/C_t14/S1/J8） | `04_verify/J_GATE.md`、`J_GATE.json` |
| 闭环验证 | `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json`（10/10，19.255s） |
| 本地模型预标注 | `03_build/local/t14/REPORT.md`、`t18/REPORT.md`、`t21/REPORT_T21.md` |
| 数据集/许可/复现 | `05_release/academic_package/`（`PACKAGE_STATUS.json` = READY_WITH_BLOCKERS） |
| 论文骨架与数字登记 | `05_release/paper/`（`NUMBERS.json`） |
| 流水线门账本 | `05_pipeline/runs/live_full/gate_ledger.jsonl`（19 PASS / 2 DEGRADED） |
| 冻结链 | `preregistration.json`（v1.2.0）、`02_contract/r28_contract.json`（v1.2.0）、`02_design/protocol_freeze.json` |

复现命令（离线、0 付费）：`python 05_release/academic_package/reproduce.py --check`；`cd 05_pipeline && python verify/run_closed_loop_verification.py --config r28.toml`（t9 修复后 vanilla GBK 控制台 **10/10**）。

---

## 7. 边界声明

- 单模型（7B Q4_K_M）、单数据集、单轮实验；结论不外推到前沿模型。
- 两臂 `solver_facts` 与金标逐字节相同：E1 只能测“呈现难度”，不能测“事实/推导难度”。
- R26.15 零字节改动（165 文件 / 93,346,177 B / 聚合 `343afde4…51bd`）；主项目文件未改；0 网络、0 付费 API、未读 `.secrets`。
- 人工双标与规则文本许可仍是发表阻断项；本报告不把它们写成“已完成”。
