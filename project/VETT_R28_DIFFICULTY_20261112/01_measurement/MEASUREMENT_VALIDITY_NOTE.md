# R28 A 阶段测量有效性复核 / MEASUREMENT_VALIDITY_NOTE

- 团队：`vett-r27-opt` · 角色：`measurement_auditor`（A 阶段独立复核）
- 日期：2026-11-12 · 运行根：`VETT_R28_DIFFICULTY_20261112\01_measurement\`
- 依据：`VETT_UPGRADE_STRATEGY_V2_20261112.md` §1 / §5 / §13；R28 任务 t2（A 阶段门 A1–A3）
- 性质：**独立重算**。只读既有工件；未联网、未调用任何付费 API、未读 `.secrets`；未写入 R26.15 任何字节（只读取），全部产物在 `01_measurement\`。
- 数据源：
  - `r26_15_content_dependency_candidate_v3`（20 场 / 100 题；`RELEASE_SUMMARY.json` sha256 `01f32665…`）
  - `eval_runs\r26_18_s5_20261112\r26_18_glm53_canonical_set_sentinel5`（5 场 / 25 题已评分；`predictions.jsonl` sha256 `c082c85d…`，`ANALYSIS.json` sha256 `58d5a91e…`）
  - 5 个评分场的 `private_gold.json` 逐文件 sha256 记录在 `A_RESULTS.json` 的 `provenance`。
- 复现：`python scripts/measure_a.py` → `A_RESULTS.json`；`python scripts/proxies_cd.py` → `DIFFICULTY_PROXIES.json`；`python scripts/baselines_b.py` → `BASELINES.json`；`python scripts/compose_gate.py` → `gate_A_decision.json`。纯标准库（无 numpy/sklearn），全部脚本在 `scripts\`。

> 结论先行：**A1 / A2 / A3 全部 PASS → 可进入设计与实现**，但必须把本文 §9 的硬约束写进 t4 合同。
> 同时给出三条会改变设计方向的实测结论：**(i)** 66.33% 相对常数先验只高 1.66pp，主指标必须换成信息字段+skill；**(ii)** 100 题里每个场景族有 4 道金标记录完全相同的副本（仅 16 个不同记录），"族分类器"可 100% 命中；**(iii)** 只看题面的 TF-IDF+逻辑回归已达 54.2%（GLM 55.1%），当前测量无法区分"读卷宗"与"只读题面"。

---

## 1. A 复算总表（分子 / 分母）

评分集：5 场（match_0021 / 0066 / 0067 / 0162 / 0220）× 5 题 = 25 题；决策记录扁平化后 12 个字段，其中 3 个在 100 题上恒为 0（`ledger.BYE`、`ledger.LEG_BYE`、`ledger.PENALTY`），信息字段 9 个。
**300 = 25 × 12 cells；225 = 25 × 9 信息 cells。**

| 指标 | 分子/分母 | 值 | 与官方 ANALYSIS 对照 |
| --- | ---: | ---: | --- |
| 决策字段宏准确率（全 12 字段，cell 级） | 199 / 300 | **66.33%** | 0.663333 一致 |
| 信息字段准确率 | 124 / 225 | **55.11%** | 0.551111 一致 |
| 整记录 exact | 7 / 25 | **28.00%** | 0.28 一致 |
| 值平衡信息字段准确率 | 9 个字段的值桶平均 | 41.73% | 0.417305 一致 |
| 信息字段 (字段,值) 去重桶数 | 41 | — | 即 `observed_informative_field_value_cells`，**不是分母** |
| 常数先验（信息字段，LOMO/100 题） | 119 / 225 | 52.89% | 0.528889 一致 |
| 常数先验（全字段） | 194 / 300 | 64.67% | 0.646667 一致 |

逐级（每级 5 题；信息 45 cells / 全字段 60 cells / 记录 5 题）：

| 等级 | 信息字段 | 全字段 | 记录 exact |
| --- | ---: | ---: | ---: |
| L1 | 45/45 = 100.0% | 60/60 = 100.0% | 5/5 |
| L2 | 19/45 = 42.22% | 34/60 = 56.67% | 1/5 |
| L3 | 23/45 = 51.11% | 38/60 = 63.33% | 1/5 |
| L4 | 21/45 = 46.67% | 36/60 = 60.00% | 0/5 |
| L5 | 16/45 = 35.56% | 31/60 = 51.67% | 0/5 |

**95% Wilson 区间**（写进报告，避免把小样本当结论）：

| 指标 | 点估计 | 95% CI | 常数先验 | 先验 95% CI |
| --- | ---: | --- | ---: | --- |
| 信息字段 | 124/225 = 55.11% | [48.58%, 61.47%] | 119/225 = 52.89% | [46.37%, 59.31%] |
| 全字段 | 199/300 = 66.33% | [60.81%, 71.44%] | 194/300 = 64.67% | [59.10%, 69.86%] |
| 记录 exact | 7/25 = 28.00% | [14.28%, 47.58%] | — | — |

模型与常数先验的区间大幅重叠：**n=25 上 66.33% vs 64.67% 不可区分。**

### 1.1 逐级先验（`official_lomo100_by_level`，复现任务书目标值）

定义：对每题每个信息字段，取**同等级、其余 19 场比赛（全 100 题）**的字段众数；tie-break 与官方 `_answer_profile` 一致（`(-count, key)`）。该定义逐位复现任务书目标 55.6 / 42.2 / 71.1 / 44.4 / 48.9 与 skill 1.0 / 0 / −0.69 / 0.04 / −0.26：

| 等级 | 先验 | 实测信息字段 | skill = (acc−prior)/(1−prior) |
| --- | ---: | ---: | ---: |
| L1 | 25/45 = 55.56% | 100.00% | +1.00 |
| L2 | 19/45 = 42.22% | 42.22% | 0.00 |
| L3 | 32/45 = 71.11% | 51.11% | −0.6923 |
| L4 | 20/45 = 44.44% | 46.67% | +0.04 |
| L5 | 22/45 = 48.89% | 35.56% | −0.2609 |
| **L2–L5 均值** | — | — | **−0.2283** |

稳健性（先验换成与评分集完全不相交的 75 题、逐级重算，`holdout75_by_level`）：
先验 64.44 / 51.11 / 73.33 / 53.33 / 53.33%，skill 1.00 / **−0.18** / **−0.83** / **−0.14** / **−0.38**，L2–L5 均值 **−0.385**。结论方向不变、幅度更大。

另一种"只在本评分集内部 LOMO"（每级 4 题，`lomo_sentinel4`）先验为 51.11 / 42.22 / 71.11 / 24.44 / 33.33%，skill 1.00 / 0.00 / −0.69 / +0.29 / +0.03，L2–L5 均值 −0.091：**n=4 的逐级先验极不稳定，不应作为主口径**，仅作敏感性分析。

**A1 解释（可解释 L2–L5）**：无论用哪种先验，L2–L5 都处于"等于或低于自身先验"的状态，L3/L5 显著低于先验；L1 的 100% 是因为该级记录/字段几乎被先验覆盖（记录 exact 5/5），不提供区分度。所以 §1 所说的 "L2–L5 低于先验" **不是全局先验比逐级结果的聚合假象**，而是真实存在的"等级阶梯不单调、且整体不高于先验"。

### 1.2 全局先验的四种口径（全部等于 52.89%）

| 口径 | 全字段 | 信息字段 | 说明 |
| --- | ---: | ---: | --- |
| 官方 LOMO（100 题，去自身场） | 64.67% | **52.89%**（476/900） | 与 `ANALYSIS.json` 一致 |
| LOMO 应用到评分 25 题 | 64.67% | 52.89%（119/225） | 逐题先验，逐题比对 |
| 75 题严格 hold-out → 25 | 64.67% | 52.89% | 与评分集完全不相交 |
| 100 题 in-sample 众数 / 25 题 in-sample | 64.67% | 52.89% | 众数映射稳定，故各口径同值 |

即：**常数预测器在信息字段上稳定为 52.89%，模型 55.11%，skill 仅 +4.72%。**

### 1.3 逐字段信号（信息字段，25 题）

| 字段 | 100 题众数份额 | 25 题众数份额 | 模型准确率 | 逐题先验准确率 | skill |
| --- | ---: | ---: | ---: | ---: | ---: |
| `batter_runs` | 52% | 52% | 56% | 52% | +0.083 |
| `bowler_runs` | 32% | 32% | 32% | 32% | 0.000 |
| `counts_in_over` | 52% | 52% | 64% | 52% | +0.250 |
| `delivery_status` | 52% | 52% | 48% | 52% | **−0.083** |
| `dismissal` | 48% | 48% | 60% | 48% | +0.231 |
| `ledger.BATTER` | 52% | 52% | 52% | 52% | 0.000 |
| `ledger.NO_BALL_EXTRA` | 76% | 76% | 80% | 76% | +0.167 |
| `ledger.WIDE_EXTRA` | 80% | 80% | 72% | 80% | **−0.400** |
| `total_runs` | 32% | 32% | 32% | 32% | 0.000 |

9 个信息字段中：4 个略高于先验、3 个恰好等于先验、2 个低于先验。**"信息字段"内部仍有大量先验成分**（`ledger.NO_BALL_EXTRA` 76%、`ledger.WIDE_EXTRA` 80% 是众数）。这正是 A2 要求主指标改为"信息字段 + skill"的直接证据。

---

## 2. §5.4 三个测量 bug 的核查结论

### 2.1 逐级先验未算 → 已算（见 §1.1）

结论：补算后 L2–L5 依然不高于先验，"低于先验"不是聚合假象；且 L1 的满分是平凡结果。**A1 PASS。**

### 2.2 Brier 标度与计算单位 → 无标度错误，但参考类选错

- `confidence` 为每题一个 [0,1] 标量（本评分集 min 0.93 / median 0.93 / mean 0.934 / max 0.95），Brier 按 25 题逐题计算：**(1/25)Σ(conf − exact)² = 0.626796**，与官方 `confidence_brier_score` 逐位一致。**不存在标度错误。**
- 但 `0.627 vs 常数 0.5 = 0.25` 是**单位与参考类错配**：0.25 是二分类 p=0.5 的 Brier；记录 exact 的基率是 28%，其气候学常数 Brier = 0.28×0.72 = **0.2016**。模型 Brier skill = 1 − 0.626796/0.2016 = **−2.11**。
- Murphy 分解：reliability = **0.4746**（严重过度自信：平均置信 0.934 vs 28% 命中），resolution = 0.0494，uncertainty = 0.2016，三者合成 0.626796。
- 若按 **cell 级**（300/225 cells）计算同一条置信度：Brier = 0.2956（全字段）/ 0.3927（信息字段）。这说明 0.627 与 0.25 的差不是"算错"，而是"**每记录** vs **每字段** 两个不同单位的混用。

建议：报告 `per_record_brier + base_rate + brier_skill + per_cell_brier` 四项；0.627 与 0.25 的对比删除。

### 2.3 `observed_informative_field_value_cells: 41` 的含义

41 = 25 题金标中出现的 **(字段, 值) 去重桶数**（例如 `delivery_status=LEGAL` 与 `dismissal=NONE` 各算 1 桶），**不是分母**。信息字段分母恒为 **25 × 9 = 225**。官方 `decision_informative_field_accuracy = 124/225` 与此一致。报告里必须写明分子/分母，避免把 41 误读为"只观察了 41 个细胞"。

---

## 3. 边指标分解（A3）

25 题、gold 最小证据边 704 条、模型预测边 519 条。独立复算：

| 指标 | P | R | F1 | tp / fp / fn |
| --- | ---: | ---: | ---: | --- |
| 最小证据 span（集合） | 0.5314 | 0.3936 | 0.4522 | 161 / 142 / 248 |
| **端到端 edge F1**（`minimal_evidence_edge_f1`） | 0.3526 | 0.2599 | **0.2993** | 183 / 336 / 521 |
| **conditional_edge_link_f1（as-coded）** | 0.7459 | 0.7948 | **0.7696** | 182 / 62 / 47 |
| 一致版：给定"模型恢复节点" | 0.3527 | 0.7948 | **0.4886** | 182 / 334 / 47 |
| 一致版：给定"gold 节点" | 0.7469 | 0.2599 | **0.3857** | 183 / 62 / 521 |
| content-dependency 边（`conditions_rule`） | 0.1224 | 0.0741 | **0.0923** | 6 / 43 / 75 |
| gold 边端点恢复率 | — | — | **0.3253**（229/704） | — |
| 预测边落在 gold 节点上的比例 | — | — | 0.4721（245/519） | — |

关系组 F1：identity_binding 0.6619；authority_resolution 0.2202；decision_support 0.3222；content_dependency 0.0923。

**A3 PASS，但必须修正表述。** as-coded 的 0.7696 的 precision 以 **gold 节点**为条件、recall 却以 **模型恢复节点**为条件，两个条件集不同，因此不是"给定正确节点，边连对 77%"。真实读数是：

- 瓶颈 1：**节点/span 恢复**——只有 32.53% 的 gold 边两端都被模型恢复；
- 瓶颈 2：**边连接本身也不强**——即使给 gold 节点，recall 仅 0.2599（P 0.7469，F1 0.3857）；给定恢复节点，P 仅 0.3527（R 0.7948，F1 0.4886）；
- content-dependency 边（最核心的"内容依赖"关系）F1 只有 0.0923，几乎未恢复。

因此"瓶颈在 span 恢复、不在边推理"只对了一半：span 恢复是第一瓶颈，但边推理在正确节点条件下仍只有 26% recall。**报告必须分列 edge F1 0.2993 / 两个一致条件 F1 / endpoint recovery 0.3253。**

---

## 4. 族重复与有效 n（R26.15 的结构性缺陷）

- 100 题 = 20 场 × 5 级；**25 个 `scenario_family` × 每族 4 题**（每级 5 族）。
- **族内 4 道题的金标 `decision_record` 完全相同：25/25 个族都是"族内唯一记录"。** 100 题只有 **16 个不同金标记录**：7 组跨族碰撞（组大小 3+3+2+2+2+2+2，16 个族只对应 7 个记录），其余 9 个族各 1 个记录，合计 7 + 9 = 16。
- 每级 5 族 → **每级只有 5 个不同记录**（各重复 4 次）。
- 评分集 25 题恰好覆盖 25 个不同的族（每族 1 题），Kish 有效 n = 25.0；但 25 题仍只对应 **16 个不同记录**；7 个 exact 题只覆盖 **6 个不同记录**。
- 族聚类 ICC（记录 exact，按 anchor 5 组）：−0.176（负值、n 太小，仅作描述）；按族无法估计（评分集每族 1 题）。

**后果（已实测，见 §5）**：给定 `scenario_family`，"族分类器"在 100 题和 75→25 上 **field/record 全部 = 100%**。也就是说：对记录级指标而言，R26.15 的 100 题有效 n 至多 **25 族 / 16 个不同记录**，不是 100；按题独立计算的任何 CI 都会高估精度。R28 若继续按题抽 split，会重复同一缺陷。

---

## 5. B 阶段：难度基线下界（纯标准库；这是"什么才算更难"的下界）

题面 = `public_instance.json → decision_question_schema[*].question`（不含卷宗文本、不含答案）。TF-IDF 词表 153 词，逻辑回归 = 多项式 softmax（每字段一个），5 折按场分组（每折 4 场 × 5 级 = 20 题，分层）或 75→25 hold-out。

| 基线 | 全字段 | 信息字段 | 记录 exact | 说明 |
| --- | ---: | ---: | ---: | --- |
| 常数先验（75→25） | 64.67% | 52.89% | 0/25 | 每字段众数 |
| anchor 众数（75→25，给定 5 类 anchor） | 80.00% | 73.33% | 8/25 = 32% | 5 个 anchor × 众数记录 |
| **族分类器（75→25，给定族名）** | **100%** | **100%** | **25/25 = 100%** | 族内 4 题记录相同 |
| 题面 1NN（75→25） | 61.00% | 48.00% | 3/25 = 12% | TF-IDF 余弦最近邻 |
| 题面 TF-IDF + LR（75→25） | 65.67% | 54.22% | 0/25 | 不读卷宗 |
| 题面 TF-IDF + LR（5 折 CV，80 题训练） | 61.75% | 49.00% | 0/100 | 不读卷宗 |
| **GLM-5.3-Flash Sentinel5（对照）** | **66.33%** | **55.11%** | **7/25 = 28%** | 冻结官方值 |
| 题面 LR − GLM | −0.66pp | **−0.89pp** | −28pp | — |

读法：

1. **GLM 相对"不读卷宗"的题面 LR 只高 0.66–0.89pp**（n=25，区间完全重叠）。当前主指标**不能证明模型在读卷宗**。
2. **anchor 众数已拿到 73.33% 信息字段 / 32% 记录 exact**，记录 exact 高于 GLM 的 28%。5 个 anchor 标签是不读卷宗的粗线索，却已超过被测模型。
3. **族分类器 100%**：R26.15 的记录答案由族唯一决定，这是"答案记忆"上界，不是难度上界；它同时证明按族泄漏的评测没有意义。
4. 题面文本**不含等级泄漏**：题面 5 类等级分类 5 折准确率 17.0%（随机 20%），macro AUC 0.494 —— 等级本身不可从题面直接读出；但字段答案仍可被题面统计到 ≈ 常数先验（53–54%），说明字段级信号主要来自题面里的场景词/模板，而非卷宗。
5. 因此 R28 的"更难"判定必须同时超过：常数 52.89%、anchor 73.33%、题面 LR 54.22%（信息字段）；记录级还必须报告族聚类 n_eff（16–25）并避免与族分类器 100% 的可达上界混淆。

---

## 6. C 阶段：难度代理量分布（100 题；每级 20 题）

| 代理量 | mean | median | p10 | p25 | p75 | p90 | min | max | distinct | eta²(level) | 判定 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| evidence_dispersion | 0.2770 | 0.2767 | 0.2300 | 0.2520 | 0.2995 | 0.3250 | 0.1874 | 0.3598 | 100 | 0.011 | **无等级信号**（各级几乎同均值） |
| evidence_span_count | 16.36 | 17 | 9 | 14 | 20 | 22 | 7 | 23 | 14 | 0.655 | 强混杂（L1 9.8 → L5 20.4） |
| evidence_doc_count | 12.74 | 13 | 8 | 10 | 15 | 17.1 | 5 | 19 | 14 | 0.459 | 强混杂 |
| distractor_count | 2.00 | 1 | 1 | 1 | 3 | 4 | 1 | 4 | 3 | **1.000** | **等级的确定性函数**（L1–L3=1, L4=3, L5=4） |
| derivation_depth | 2.60 | 3 | 1 | 2 | 3 | 4 | 1 | 4 | 4 | 0.900 | 强混杂（L1=1, L2=2.2, L3=2.6, L4=3.2, L5=4.0） |
| semantic_bridge_depth | 3.00 | 3 | 1 | 2 | 4 | 5 | 1 | 5 | 5 | **1.000** | **与等级双射**（L1..L5 = 1..5） |
| lexical_bridge_depth | 3.00 | 3 | 1 | 2 | 4 | 5 | 1 | 5 | 5 | **1.000** | **与等级双射** |
| temporal_depth | 0.84 | 1 | 0 | 0 | 2 | 2 | 0 | 2 | 3 | 0.770 | 强混杂（L2 全 0，L4/L5 无 0） |
| temporal_joins | 0.80 | 1 | 0 | 0 | 1 | 2 | 0 | 2 | 3 | **1.000** | **等级的确定性函数** |
| operator_count | 6.00 | 7 | 4 | 5 | 7 | 7 | 2 | 9 | 6 | 0.372 | **非单调**（L1 4.2, L2 6.8, L3 6.6, L4 6.2, L5 6.2） |

另：3 个 `difficulty_vector` 元数据字段**零方差**——`authority_decisions ≡ 1`、`output_payload ≡ 7`、`hard_negative_similarity ≡ "HIGH"`。

**哪些几乎无变化空间**（不可作为难度因子）：

- 零方差：`authority_decisions`、`output_payload`、`hard_negative_similarity`；
- 与等级共线/确定：`semantic_bridge_depth`、`lexical_bridge_depth`（= 等级本身）、`distractor_count`、`temporal_joins`（等级的函数）；
- 等级内几乎无变化：`distractor_count`（每级只有 1 个值）、`derivation_depth`（L1 恒 1、L5 恒 4）、`temporal_depth`（L2 恒 0）；
- **唯一"有跨题变化但几乎无等级信号"的是 `evidence_dispersion`（eta²=0.011）**；`operator_count` 有变化但非单调（eta²=0.372）。

结论：R26.15 的"难度代理量"大多不是独立因子，而是等级的别名或确定性函数；R28 的 2×2×2×2 设计不能沿用这些字段，必须重建正交因子。

---

## 7. D 阶段：交叉表与共线性

`state.active_source × level`（V = 0.707，dof = 8）：

| active_source | L1 | L2 | L3 | L4 | L5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| DIRECT_OBSERVATION | 20 | 20 | 20 | 0 | 0 |
| HIGHEST_REVISION | 0 | 0 | 0 | 10 | 10 |
| LAST_PRE_LOCK | 0 | 0 | 0 | 10 | 10 |

→ 不是严格共线（L4/L5 内不可分），但 **`active_source` 完全分离 L1–L3 与 L4–L5**：它是"是否 review 级"的完美二值指示器，与等级强混杂。

`temporal_depth × level`（V = 0.693）：

| temporal_depth | L1 | L2 | L3 | L4 | L5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 16 | 20 | 8 | 0 | 0 |
| 1 | 4 | 0 | 12 | 8 | 4 |
| 2 | 0 | 0 | 0 | 12 | 16 |

→ 任一取值都不对应单一等级，但 L2 全 0、L4/L5 无 0；强混杂、非完全共线。

`derivation_depth × level`（V = 0.853）：

| derivation_depth | L1 | L2 | L3 | L4 | L5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 20 | 0 | 0 | 0 | 0 |
| 2 | 0 | 16 | 8 | 0 | 0 |
| 3 | 0 | 4 | 12 | 16 | 0 |
| 4 | 0 | 0 | 0 | 4 | 20 |

→ `d=1` **只出现在 L1**，`d=4` 只出现在 L4/L5；等级阶梯几乎被 derivation_depth 编码。非双射但接近嵌套。

补充（同一方法）：

- `scenario_family × level`：V = **1.000**，族 → 等级 **确定性**（每族只属于一个等级，等级含 5 族）；即等级被族名内嵌，两者不可当独立因子。
- `anchor × level`：V = **0.000**，5×5 完全平衡（每格 4 题）——**R26.15 中唯一与等级正交的可用区组因子。**
- `operator_count × level`：V = 0.471（弱、非单调）；`context_band × level`：V = 0.000（正交，但只有 3 个取值且与其说难度不如说是上下文长度配置）。

**明写哪些因子与等级完全共线**：

1. **完全共线（双射）**：`semantic_bridge_depth` / `lexical_bridge_depth`（= 等级编号 1..5）；
2. **确定性函数（单向共线，等级 → 因子）**：`distractor_count`、`temporal_joins`；
3. **强混杂但非确定**：`derivation_depth`（V=0.853）、`active_source`（V=0.707）、`temporal_depth`（V=0.693）、`evidence_span_count`（eta²=0.655）、`evidence_doc_count`（eta²=0.459）；
4. **与等级正交**：`anchor`（V=0）、`context_band`（V=0）。

---

## 8. 复算与官方值的逐项对照（独立验证）

| 官方字段 / 指标 | 官方值 | 本次复算 | 一致 |
| --- | ---: | ---: | :--: |
| `decision_field_macro_accuracy` | 0.663333 | 199/300 = 0.663333 | ✓ |
| `decision_informative_field_accuracy` | 0.551111 | 124/225 = 0.551111 | ✓ |
| `full_record_exact_match` | 0.28 | 7/25 = 0.28 | ✓ |
| `decision_informative_field_value_balanced_accuracy` | 0.417305 | 0.417305 | ✓ |
| `unconditional_informative_field_prior` | 0.528889 | 476/900 = 0.528889 | ✓ |
| `unconditional_field_prior` | 0.646667 | 776/1200 = 0.646667 | ✓ |
| `observed_informative_field_value_cells` | 41 | 41 | ✓ |
| `confidence_brier_score` | 0.626796 | 0.626796 | ✓ |
| `minimal_evidence_edge_f1` | 0.299264 | 0.299264 | ✓ |
| `conditional_edge_link_f1` | 0.769556 | 0.769556 | ✓ |
| `conditional_edge_link_precision_given_gold_nodes` | 0.745902 | 0.745902 | ✓ |
| `conditional_edge_link_recall_given_recovered_endpoints` | 0.79476 | 0.79476 | ✓ |
| `gold_edge_endpoint_recovery_rate` | 0.325284 | 0.325284 | ✓ |
| `content_dependency_edge_f1` | 0.092308 | 0.092308 | ✓ |
| 逐级先验（任务书目标） | 55.6/42.2/71.1/44.4/48.9 | 同上（逐位） | ✓ |
| 逐级 skill（任务书目标） | 1.0/0/−0.69/0.04/−0.26 | 同上（逐位） | ✓ |

---

## 9. 对 R28 设计与实现的硬约束（进入下一阶段的先决条件）

1. **主指标冻结**：`decision_informative_field_accuracy`（分子/分母必须写明）＋ **逐级 skill**（先验必须来自与评估集不相交的 held-out 池重算，禁止用全局先验代替逐级先验）。`decision_field_macro_accuracy` 降为描述性指标。
2. **强制四类对照**：常数先验、anchor 众数、题面 1NN、题面 TF-IDF+LR。任何"更难"的主张必须同时超过这四条；否则不成立。
3. **族作为抽样单位**：100 题 → 25 族 / 16 个不同记录；R28 候选必须每族至多 1 题进入评价，或报告族聚类 n_eff 与按族 bootstrap 的 CI。禁止在同族副本之间做 split。
4. **因子必须与等级正交**：`semantic_bridge_depth` / `lexical_bridge_depth` 不得再作为难度因子（与等级双射）；`distractor_count`、`temporal_joins` 是等级的确定性函数，不得当独立因子；`derivation_depth` / `temporal_depth` / `active_source` 需重采样；可复用 `anchor` 作为 5 水平区组（R26.15 中唯一 V=0 的区组）。
5. **常数字段非零且非常数**：`ledger.BYE` / `ledger.LEG_BYE` / `ledger.PENALTY` 在 100 题上恒 0，`ledger.NO_BALL_EXTRA`（76% 众数）/`ledger.WIDE_EXTRA`（80% 众数）先验过重；R28 必须保证这些字段有真实取值分布。
6. **边指标分列**：端到端 edge F1、as-coded conditional、两个一致条件版本、endpoint recovery、content-dependency edge F1，各自单独报，禁止再出现"给定正确节点 77%"的表述。
7. **Brier 口径**：record 级 Brier + 基率 + skill + cell 级 Brier 四项并列；参考类用 0.2016。
8. **报告样本量**：25 题的记录 exact CI 宽达 [14.3%, 47.6%]，L1 的 5/5 使 28% 偏向平凡项；R28 的预注册必须先用功效分析确定每格样本量。

---

## 10. 门判定

| 门 | 判据 | 结果 | 证据 |
| --- | --- | --- | --- |
| **A1** | 逐级先验算完且能解释 L2–L5 | **PASS** | 目标值 55.6/42.2/71.1/44.4/48.9 与 skill 1.0/0/−0.69/0.04/−0.26 逐位复现；L2–L5 均值 skill −0.228（严格 hold-out −0.385），L2–L5 整体不高于先验；L1 平凡 |
| **A2** | 主指标改为信息字段 + skill | **PASS** | 全字段 66.33% vs 常数 64.67%（+1.66pp）；信息字段 55.11% vs 52.89%（+2.22pp，skill 4.72%，CI 重叠）；九个字段 2 个低于先验、3 个等于先验 |
| **A3** | conditional_edge_link_f1 与 edge F1 分列 | **PASS** | edge F1 0.2993；as-coded conditional 0.7696；一致版 0.4886 / 0.3857；endpoint recovery 0.3253；content edge 0.0923（全部独立复算） |

**综合：PASS → 可进入设计与实现。** 无 FAIL 项，因此不写"不得进入设计与实现"。
但 A2/A3 的"改口径"必须原样落入 t4 的 R28 数据优化合同；若合同仍以 `decision_field_macro_accuracy` 为主指标、或仍把 0.7696 写成"给定正确节点"，则视为 **A2/A3 未落地**，下游不得开工。

判定文件：`gate_A_decision.json`（机器可读，含 8 条 findings 与 6 条 conditions）。

---

## 11. 产物与复现

| 文件 | 内容 |
| --- | --- |
| `A_RESULTS.json` | A 阶段全部数字：headline / per_field / 4 种全局先验 / 5 种逐级先验 / Brier / 边分解 / 族重复 / Wilson CI / 输入 sha256 |
| `BASELINES.json` | 10 个难度基线（常数、族、anchor、1NN、LR×2 训练制度）+ 等级泄漏检查 |
| `DIFFICULTY_PROXIES.json` | 10 个代理量的分布/分位数/eta²/共线判定 + 5 张交叉表 + 每题明细 |
| `gate_A_decision.json` | A1–A3 判定、findings、conditions_to_proceed |
| `scripts\` | `common.py`、`measure_a.py`、`proxies_cd.py`、`baselines_b.py`、`compose_gate.py`（+ 4 个只读 schema 探查脚本） |

复现命令（纯标准库，约 90 秒）：

```powershell
$py = "C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py 01_measurement\scripts\measure_a.py
& $py 01_measurement\scripts\proxies_cd.py
& $py 01_measurement\scripts\baselines_b.py
& $py 01_measurement\scripts\compose_gate.py
```

安全声明：全部脚本只读 `r26_15_content_dependency_candidate_v3` 与 `eval_runs\r26_18_s5_20261112\...`；未修改任何 R26.15 字节；未读 `.secrets`；网络调用 0；付费 API 调用 0；除 `01_measurement\` 外零写入。
