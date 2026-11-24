# EXPERIMENTS（E1–E6 结果表模板）

> **数字纪律**：本表所有数字只来自 `eval_runs/t19_e1e5_20261112/analysis.json`、`analysis_e4_supplemental.json`、`e1_raw.jsonl` 与 `05_pipeline/runs/live_full/gate_ledger.jsonl`。没有手写估计值；E6 未在 R28 eval_runs 中运行，**保持空白**。

## 1. 主表（点估计 + 95% CI + 效应量）

| 实验 | 端点 / 比较 | n | 点估计 | 95% CI | 效应量 | 预注册判定 | 来源 |
|---|---|---:|---|---|---|---|---|
| **E1** | published（hard）vs control 信息字段准确率；配对差（control−hard） | 319 pairs | hard **0.595611**；control **0.601184**；drop **0.557297 pp** | hard [0.577543, 0.613424]；control [0.583149, 0.618949]；drop [−0.801115, +1.846047]（item bootstrap） | Cohen's h **−0.011368**；OR **0.977077**；方向 69/47/203；符号检验 p=**0.050730** | **DIRECTION_ONLY**；`harder_claim_permitted=false` | `analysis.json E1`；`e1_raw.jsonl` |
| **E1b** | 整记录 exact | 638 arm-records | **5/638 = 0.78%** | Wilson [0.003352, 0.018213] | 与 E1 同一配对；描述性 | 不作难度证据 | `analysis.json E1` |
| **E2** | 剂量 0/1/2 的逐题信息字段准确率 | 192 items | **59.375% / 62.674% / 60.938%** | slope **+0.78125 pp/step**，[−1.815290, +3.401827] | 非单调；`delta_vs_dose0` +3.298611 / +1.562500 pp | **HYP-R28-DOSE REJECTED**；单侧 p=0.279527 | `analysis.json E2` |
| **E3** | 四个机制主效应（FC，n=127） | 127 items | D1 **−1.179991 pp**；D2 **−1.874435**；D3 **−2.221658**；D4 **−6.111676** | D1 [−7.063255,+4.703273]；D2 [−7.774694,+4.025823]；D3 [−8.104454,+3.661139]；D4 [−11.985953,−0.237398] | 系数 β_pp；Holm p：1.0/1.0/1.0/**0.165731** | **H3=false**；交互 **NOT_ESTIMABLE_WITH_16x8** | `analysis.json E3` |
| **E4** | V− substitution（主列） | 32 | **0.500** | Wilson [0.336306, 0.663694] | 稳定 16/32；introduced 0.125（n=8，[0.022417,0.470895]） | 主门 ≥0.80 **FAIL**；S12 trigger true | `analysis_e4_supplemental.json` |
| **E4b** | 位置/顺序稳定性 + flip⁺ | 40 | order **0.125**；flip⁺ **0.525** | order [0.054594, 0.261124]；flip [0.374971, 0.670648] | random floor **0.875** | flip 未达 ≥2× floor；描述性 | 同上 |
| **E5** | 跨模型区分度 | 1 executable model | **UNTESTED** | — | — | 零付费 + 仅 1 个本地模型；区分度主张撤回 | `analysis.json E5` |
| **E6** | 本地白名单标注能力（H6） | — | **NOT_IN_R28_EVAL_RUNS** | — | — | reference-only（t18）；R28 无 endpoint；**不填数字** | — |

### 1.1 E1 的效应量说明

- Cohen's h 由 `hard_cell_counts=1710/2871` 与 `control_cell_counts=1726/2871` 计算：`h = 2 asin(sqrt(p_hard)) − 2 asin(sqrt(p_control)) = −0.011368`；OR = `(p_h/(1−p_h))/(p_c/(1−p_c)) = 0.977077`。
- 效应量很小且 CI 跨 0；这正是 **不能声称“更难”** 的统计理由，而不是“没跑出显著”。

## 2. 基线矩阵（同测试集；来自 `analysis.json`）

| 预测器 | 信息字段准确率 | 说明 |
|---|---:|---|
| constant prior（same-set） | **0.550347** | `gates.G1.constant_prior.same_set` |
| question-text TF-IDF + LR | **0.547569** | `gates.G1.question_text_tfidf_logreg.same_set` |
| hard（published） | **0.595611** | `E1.hard_informative_rate` |
| control（dose=0） | **0.601184** | `E1.control_informative_rate` |
| anchor-mode same-set | **NOT_MEASURABLE** | `G1` fail-safe → UNTESTED |

> 基线表只陈述同集读数；不得把 hard/control 差异解释为“难度效应”（E1 的预注册判定是 DIRECTION_ONLY）。

## 3. 预注册 gate 读数（`analysis.json gates`）

| Gate | 状态 | 读数 |
|---|---|---|
| G1 / G1r | **UNTESTED** | R28 无 anchor 字段；fail-safe |
| G2 | **FAIL** | `skill_hard=0.100664`，模型高于常数先验；不能声称“更难” |
| G5 | **PASS** | family-only lift −0.035416；value-balanced 0.103870；permutation p 0.146341 |
| G7 | **UNTESTED** | 只有 1 个可执行本地模型 |
| G8 | **PASS** | control conformance 1.0；hard 0.996875 |
| G9 | **PASS** | n_pairs=320（含 12 条 append-only 重跑，原行保留） |

## 4. 流水线 gate ledger（`gate_ledger.jsonl`；非模型准确率）

- 共 **21** 个 gate：**19 PASS / 2 DEGRADED**。
- DEGRADED：`G_ANNOTATION_COVERAGE`（mechanical-only，coverage 0.0，floor 0.95）与 `G_JUDGE_COMPARABILITY`（无 comparables）。这是 **mechanical-only 运行**的覆盖/可比性状态，不是模型结果。
- 其余 19 个 gate PASS，包括数据计数/完整性/确定性、本地路由、预算、artifact 确定性等。

## 5. 表格填写规则（给合作者）

1. 任何新数字先在 `NUMBERS.json` 登记来源路径；没有来源的数字不得进表。
2. E6 只有在 R28 eval_runs 真正运行并产出 endpoint 后才能填；不得从 t18 平移。
3. 点估计、95% CI、效应量、n 四列缺一不可；E5/E6 没有估计时写 `UNTESTED` / `NOT_IN_R28_EVAL_RUNS`，不写“约”“大概”。
4. 不把 gate ledger 的 PASS 当作模型准确率；它是流水线/数据 gate。
