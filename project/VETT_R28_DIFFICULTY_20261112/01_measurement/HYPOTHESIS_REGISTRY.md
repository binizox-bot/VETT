# R28 假设登记表 / HYPOTHESIS_REGISTRY

- 团队：`vett-r27-opt` · 复核：`measurement_auditor`（t3 / B1 门）
- 日期：2026-11-12 · 运行根：`VETT_R28_DIFFICULTY_20261112\`
- 依据：`VETT_UPGRADE_STRATEGY_V2_20261112.md` §9（B1）、`PROPOSAL_VETT_R28_DIFFICULTY_AND_INTERPRETABILITY.md` §3/§4.1/§7、`TEAM_ROLES_AND_AUTOMATION_PLAN.md` t3
- 证据：`B1_RECHECK.json`、`factor_attribution.json`、`_local_model_smoke\RESULTS.md`、t2 `MEASUREMENT_VALIDITY_NOTE.md`
- 只读、0 网络、0 付费 API；本文件只登记假设与状态，不做任何等级重设计。

## 0. 结论摘要

1. **B1 描述性 = PASS**：`operator_cost_max` 与每题信息字段准确率 rho = -0.6669，95% Fisher CI [-0.841, -0.369]，bootstrap CI [-0.863, -0.317]；Holm 校正后 p = 0.010449（复现）/ 0.00760（独立 20 万次置换）。`operator_cost_sum` 同样通过 Holm；`derivation_depth` 为边缘（0.061 > 0.05）。
2. **B1 预测性 = UNTESTED**：B2 已冻结 75 题预测（sha256 `e1f997b8dbc46323…`），但 75 题没有任何模型的评分；零付费约束下无法执行预注册的样本外检验。**B1 整体 NOT MET**。
3. **H1–H6 全部 UNTESTED**（R28 数据/实验尚未构建）。新增 **HYP-R28-DOSE** 作为剂量假设，见 §3。
4. **不得据 25 题重设计等级**；加难必须以机制剂量实验（同金标双渲染、题内配对）为准，见 §4。
5. 已有唯一完成的剂量实测是**否证性**的：文档数 2→6→13 时信息字段 4.03→4.20→4.55（上升），生成速度 71.9→65.4→33.0 t/s（腰斩）。因此文档数/分散度/上下文长度写入 **REJECTED**。

## 1. 状态图例

| 状态 | 含义 |
| --- | --- |
| **VERIFIED** | 有实测的剂量/配对/干预证据支持登记方向（同一金标，只改机制） |
| **REJECTED** | 实测显示不能加难（方向相反/无效应），或结构上不可作为独立机制 |
| **UNTESTED** | 尚无实测证据；横断面相关不等于剂量证据 |

## 2. H1–H6 登记（预注册，来源 PROPOSAL §3）

| 编号 | RQ | 假设 | 证伪/拒绝条件 | 实验 | 状态 | 当前依据 |
| --- | --- | --- | --- | --- | --- | --- |
| **H1** | RQ1 难度能否被构造而非调参 | 同一金标下 hard 版准确率显著低于 shallow 版 | 配对差 ≥10pp 且 95% CI 不含 0 才成立；CI 跨 0 → 只能报"方向一致但不显著" | E1（160 对，本地 7B） | **UNTESTED** | 双渲染数据未建 |
| **H2** | RQ2 难度是否随机制剂量单调上升 | dose 0/1/2 上准确率单调递减且斜率显著 | 非单调或斜率 CI 含 0 即不成立 | E2（96 题） | **UNTESTED** | 由 **HYP-R28-DOSE** 细化；R26.15 自然对照 10 对 5 降/4 升/1 平（p=0.50）不构成支持 |
| **H3** | RQ3 失败能否归因到具体机制 | 混合效应模型中至少 1 个机制主效应 CI 不含 0 | 全部 CI 含 0 → 报"难度不可归因" | E3（2^4 因子核 64 题） | **UNTESTED** | B1 横断面只有描述性相关；D1–D4 无因果证据 |
| **H4** | RQ4 解释是否可被机械验证 | 证书重推金标成功率 100%，删被引证据后答案翻转率 ≥90% | 任一不达 → 解释主张不成立 | E4（40 题 × 3 孪生） | **UNTESTED** | 证书/孪生尚未构建 |
| **H5** | RQ5 数据集是否真有区分度 | 多模型面板最强−最弱 ≥25pp | 不达 → 任务无区分度，停止扩量 | E5（4 模型 × 64 题） | **UNTESTED** | 只有单模型 GLM 与本地 7B 冒烟 |
| **H6** | RQ6 本地小模型能否承担规模化标注 | 白名单任务上本地与机械真值一致率 ≥0.85 | 不达 → 降级回云端，记 DEGRADED | E6（各 ≥30） | **UNTESTED** | `_local_model_smoke` 只测了任务作答，未做白名单一致性判定 |

## 3. HYP-R28-DOSE（新增，正式登记）

| 字段 | 内容 |
| --- | --- |
| **ID** | `HYP-R28-DOSE` |
| **版本 / 日期** | v1 / 2026-11-12 |
| **陈述** | **同一模型上，语义机制剂量↑ → 字段准确率单调下降。** |
| **适用范围** | 仅 D1–D4：`alias_hops`、`temporal_joins`、`scope_decisions`、`isomorphic_distractors`（renderer 已有参数，`generator.py:306–370`）。**明确排除**所有 REJECTED 机制（文档数/分散度、上下文长度、bridge depth）；推导深度/算子数暂不纳入，待 t5 可行性验证后再定。 |
| **操纵** | 同一 `solver_facts` 与同一 `decision_record_flat`（逐字节相同），只改一个机制的剂量 0/1/2；发布集与对照集配对渲染。 |
| **主端点** | `paired_accuracy_drop` = acc(dose 0) − acc(dose 2)（信息字段，逐条件重算先验）。 |
| **次端点** | `dose_slope`（准确率对剂量的斜率，混合效应）；每级/每机制各自先验与 skill。 |
| **成立条件** | ① 0→1→2 单调递减（无任一步反向或持平）；② 0→2 总效应 **≥10pp**；③ 斜率 95% CI 不含 0；④ 在 E2 的 96 题（4 机制 × 3 剂量 × 8 题）上执行。 |
| **拒绝条件** | 任一步**非单调**；或方向**反向**（准确率上升）；或总效应 **<10pp**；或斜率 CI 含 0。满足任一即判 HYP-R28-DOSE 不成立。 |
| **统计单位** | 题（不是字段）；题内配对消除题目/模型方差；报告族聚类 n_eff。 |
| **当前状态** | **UNTESTED**。已有唯一剂量实测（文档数/上下文）为否证性，已排除出本假设；R26.15 自然对照 10 对 5 降/4 升/1 平（均值 -3.3pp，符号 p=0.50），不能作为支持证据。 |
| **失败报告契约** | 若拒绝，如实报告"该机制未使任务变难"，公开配对差与 CI；**不得改端点/换指标制造更难结论**。 |
| **责任实验** | E2（t19，本地 7B）；E3 提供机制归因旁证。 |

## 4. 明写：不得据 25 题重设计等级

1. 25 题 = 5 场 × 5 级，**每级 n=5**；记录 exact 的 95% Wilson CI = [14.3%, 47.6%]（7/25）。
2. 25 题覆盖 25 个族，但只有 **16 个不同金标记录**；族分类器（给定族名）在 75→25 上 field/record = 100%（t2）——等级与答案不可分。
3. **L1 全对（5/5 记录 exact、45/45 信息字段）是平凡结果**；逐级先验非单调（L3 0.7111 > L1 0.5556），等级阶梯不能当难度标尺。
4. n=5/级时比例的标准误约 22pp；提案已算过 8pp 显著差需约 604 题/级。
5. 因此：**加难只能由机制剂量实验（同金标双渲染、题内配对）判定**；等级只是描述标签，不得据 25 题重排/重设计等级。

## 5. 证据附录

### 5.1 B1 描述性（25 题，GLM-5.3-Flash）

| 特征 | rho | 95% Fisher CI | p_perm | p_holm | 判定 |
| --- | ---: | --- | ---: | ---: | --- |
| `operator_cost_max` | -0.6669 | [-0.841, -0.369] | 0.00040 | 0.00760 | 显著（复现 0.010449） |
| `operator_cost_sum` | -0.6421 | [-0.827, -0.331] | 0.00081 | 0.01458 | 显著 |
| `derivation_depth` | -0.5690 | [-0.787, -0.224] | 0.00356 | 0.06060 | 边缘（0.061 > 0.05，未过 Holm 显著线） |
| `alias_hops`（D1） | -0.5204 | [-0.759, -0.158] | 0.00877 | 0.06396 | 边缘（Holm 后不显著） |
| `isomorphic_distractors`（D4） | -0.5241 | [-0.762, -0.163] | 0.00799 | 0.06396 | 边缘 |
| `temporal_joins`（D2） | -0.3526 | [-0.656, 0.049] | 0.08430 | 0.33722 | 不显著 |
| `scope_decisions`（D3） | -0.3199 | [-0.635, 0.086] | 0.11979 | 0.33722 | 不显著 |

### 5.2 自然对照（6 组同事实跨族，10 对同金标配对）

| 配对 | 准确率变化 | alias/ tj/ scope/ iso 剂量变化 |
| --- | ---: | --- |
| L1_LEGAL_BOWLED/L2_NB_BOWLED | 1.000 → 0.333 (-0.667) | +1/+0/+0/+1 |
| L2_NB_OVER_WIDE/L4_REVIEW_NB_OVER_WIDE | 0.333 → 0.222 (-0.111) | +1/+1/+1/+1 |
| L2_WIDE_STUMP/L4_REVIEW_WIDE_STUMP | 0.222 → 0.444 (+0.222) | +1/+1/+1/+1 |
| L2_WIDE_STUMP/L5_WIDE_STUMP_REVIEW | 0.222 → 0.444 (+0.222) | +1/+2/+1/+2 |
| L4_REVIEW_WIDE_STUMP/L5_WIDE_STUMP_REVIEW | 0.444 → 0.444 (+0.000) | +0/+1/+0/+1 |
| L3_CATCH_BOUNDARY/L4_REVIEW_CATCH_CONTROL | 1.000 → 0.889 (-0.111) | +1/+0/+1/+1 |
| L3_OVERTHROW_CROSS/L4_REVIEW_OVERTHROW | 0.556 → 0.222 (-0.333) | +1/+0/+1/+1 |
| L3_DEAD_BEFORE_RUNOUT/L4_REVIEW_DEAD_SEQUENCE | 0.222 → 0.556 (+0.333) | +1/+0/+1/+1 |
| L3_DEAD_BEFORE_RUNOUT/L5_RUNOUT_LATER_BOUNDARY | 0.222 → 0.444 (+0.222) | +1/+1/+1/+2 |
| L4_REVIEW_DEAD_SEQUENCE/L5_RUNOUT_LATER_BOUNDARY | 0.556 → 0.444 (-0.111) | +0/+1/+0/+1 |

汇总：10 对中 **5 对下降、4 对上升、1 对持平**；均值 -0.0333；符号检验 p = 0.50。**不构成剂量杠杆的正面证据。**（AUDIT/PROPOSAL 引用的 63.3/60.0/51.7 是整级宏准确率，不是这 6 组的配对落差。）

### 5.3 本地 7B 剂量实测（REJECTED 证据）

| 条件 | 文档数 | n | 信息字段/9 | 常数先验/9 | 生成 t/s | 墙钟 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| question_only | 0 | 30 | 2.000 | 4.767 | 77.4 | 2.3 |
| 15K_2docs | 2 | 30 | 4.033 | 4.767 | 71.9 | 4.1 |
| 40K_6docs | 6 | 30 | 4.200 | 4.767 | 65.4 | 8.0 |
| 80K_13docs | 13 | 29 | 4.552 | 4.759 | 33.0 | 17.7 |

配对（29 题共同集）：40K−15K = +0.1724；80K−15K = +0.5517；15K→80K 改善 11 题、恶化 6 题、持平 12 题。结论：**加文档 = 加成本，不是加难**。

### 5.4 B1 预测性空缺

- `factor_attribution.json` 的 B2 规则：选 p_holm<0.10 中 |rho| 最大者 = `operator_cost_max`，对 75 题冻结线性预测并给出 sha256 `e1f997b8dbc463239fe27d07a23868bdf1f11290231ecba6cf84b1a93c2e6a63`。
- 75 题**没有任何模型的评分结果**；零付费 pilot 不可行（硬约束）。
- 零成本旁证（**非预注册、不同模型、n=15**）：本地 7B 40K 条件下预测分数与实测信息字段准确率 Spearman rho = 0.3759458271018408。不得用于 B1 判定。
- 关闭条件：用零成本本地面板在 **75 题**上取得评分（不得复用 25 题），再按冻结规则计算样本外 rho → 才能把 B1 预测性从 UNTESTED 改为 PASS/FAIL。

## 6. 机制登记摘要（详见 MECHANISM_REGISTRY.json）

| 机制 | 参数 | 状态 | 理由 |
| --- | --- | --- | --- |
| D1 证据跳数 | `alias_hops` | UNTESTED | 已有参数，无剂量阶梯；横断面 rho=-0.520 仅为描述 |
| D2 修订链 | `temporal_joins` | UNTESTED | 无剂量阶梯；横断面不显著 |
| D3 权威裁决 | `scope_decisions` | UNTESTED | 无剂量阶梯；横断面不显著 |
| D4 干扰同构度 | `isomorphic_distractors` | UNTESTED | 无剂量阶梯；横断面 rho=-0.524 边缘 |
| 推导深度/算子数 | `rule_operators` / `derivation_depth` | UNTESTED（原 REJECTED 理由被推翻） | 同事实组内算子数可变而金标不变；待 t5 可行性验证 |
| 文档数/分散度 | `evidence_doc_count` / `evidence_dispersion` | **REJECTED** | 本地 7B 剂量实测：准确率上升、速度腰斩 |
| 上下文长度 | `estimated_context_tokens` | **REJECTED** | 同一实验：长度是成本杠杆 |
| 证据位置/顺序 | `evidence_position_mean` | UNTESTED | variants/ 已可构造，未跑模型 |
| bridge depth | `semantic/lexical_bridge_depth` | **REJECTED** | 与等级双射（t2），不是独立因子 |

## 7. 复现

```powershell
$py = "C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py 01_measurement\scripts\run_all_b.py   # recompute_b1 -> compose_gate_b -> verify_gate_b
```

产物：`B1_RECHECK.json`（证据底座）、`MECHANISM_REGISTRY.json`、`gate_B_decision.json`、本文件。`verify_gate_b.py` 对 rho / p_holm / CI / 机制状态 / REJECTED 读数 / HYP-R28-DOSE 条款逐项断言（0 failures）。

只读 `r26_15_content_dependency_candidate_v3`、R26.18 评分工件、`VETT_V2_MEASUREMENT_20261112` 与 `_local_model_smoke`；0 网络、0 付费 API。
