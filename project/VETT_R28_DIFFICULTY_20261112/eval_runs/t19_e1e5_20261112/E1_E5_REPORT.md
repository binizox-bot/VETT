# R28 配对主实验 E1–E5 报告（t19，attempt 2）

- 预注册：`1.2.0`（AMEND-002；sha256 `b5c3984925666552…`）
- 数据集：`03_build/dataset_r28`（build_index sha256 `dd6de16a4001d414…`）
- 模型：`qwen2.5:7b-instruct-q4_K_M`，digest `845dbda0ea48ed749caa…`，temperature=0，seed=20261112，num_ctx=8192；主跑 num_predict=420，12 条失败重跑 num_predict=512
- 运行目录：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R28_DIFFICULTY_20261112\eval_runs\t19_e1e5_20261112`；`e1_raw.jsonl` 652 行（含 12 条重跑）；0 付费 API、仅 loopback

## 0. 结论摘要

- **主端点（严格配对，n=319）：`paired_accuracy_drop` = 0.557pp**（发布版 59.56% vs 对照版 60.12%）；按题 bootstrap 95% CI [-0.801, 1.846]，按族版 [-0.766, 1.881]，更保守下界 **-0.801pp（跨 0）**。
- 配对方向（逐题准确率比较）：control 更准 69 / hard 更准 47 / 并列 203，符号检验双侧 p=0.0507。9/9 信息字段全对口径的 McNemar：b=2, c=1, p=1.0000。
- **记录 exact：整记录（12/12 字段）exact = 0.63%（hard，2/319） vs 0.94%（control，3/319），1 对两臂都 exact；合计 5/638 次作答 = 0.78%。captain 在 attempt-1 的 295 对复算中为 0/295——两个快照都支持'12 字段联合正确'对 7B 几乎不可达；这是强证据，不能埋在字段级准确率里。**
- 预注册判定：`primary_outcome_statistical = DIRECTION_ONLY`；**允许 headline = `DIRECTION_ONLY`**；`harder_claim_permitted = False`；DEGRADED 标志：['G1_UNTESTED_ANCHOR_NOT_MEASURABLE', 'G1r_UNTESTED_ANCHOR_NOT_MEASURABLE', 'G7_UNTESTED_PANEL_DEGRADED', 'E4_DEFERRED_GPU_HANDOFF']。
- **E2 / HYP-R28-DOSE：REJECTED**。剂量 0/1/2 的信息字段准确率 = 59.38% / 62.67% / 60.94%（相对 dose0：3.30 / 1.56pp），非单调、方向与'加难'相反；OLS 斜率 0.781pp/step，95% CI [-1.82, 3.40]；4 个机制支持数 0/4。
- E3：**H3 不成立**（主效应 Holm 后无显著项；交互不可估：16 格 × 8 题不足以识别 6 个二阶交互）。
- E4：**DEFERRED_GPU_HANDOFF**（GPU 已交接给 t14/t21；材料已就绪，V− 可用率 substitution 271/320、introduced 49/320、none 0）。
- E5：**UNTESTED** —— 零付费硬约束 + 本机仅 1 个本地模型；预注册规定可执行模型数 <2 时 E5 记 DEGRADED/UNTESTED → **按预注册 S2 撤回"任务有区分度"的主张**（不是"E5 未跑"，而是面板降级导致区分度不可建立）。

## 1. E1 主实验（320 对；分析单位 = 实例）

| 指标 | 发布版（hard） | 对照版（shallow） | 配对差 |
|---|---:|---:|---:|
| 信息字段准确率（严格配对） | 59.56% | 60.12% | **0.557pp** |
| 记录 exact | 0.63% | 0.94% | 0.31pp |

- 剔除解析失败后的两臂均值：hard 59.56%（n=319）/ control 60.21%（n=320）
- ITT 敏感性（320 对，失败按 0）：drop 0.833pp，CI [-0.590, 2.222]
- 结构空配对（四剂量全 0，n=72）：drop -0.309pp（两臂 prompt 全同：True）
- active 配对（n=247）：drop 0.810pp
- **Conformance（独立轴）**：初始失败 12 条 = {'length': 9, 'service_unavailable': 3}；按臂 {'control': 4, 'published': 8}；重跑 12 条、修复 11 条，持久失败 [{'arm': 'published', 'item_id': 'r28q_0117'}]；最终 hard conformance 99.69% / control 100.00%；主分析只用严格配对，失败不进主分。

| 分层 | n | hard | control | drop (pp) |
|---|---:|---:|---:|---:|
| block:DL | 192 | 61.00% | 61.05% | 0.06 |
| block:FC | 127 | 57.39% | 58.71% | 1.31 |
| mechanism:D1 | 48 | 59.26% | 60.65% | 1.39 |
| mechanism:D2 | 48 | 63.43% | 61.81% | -1.62 |
| mechanism:D3 | 48 | 60.19% | 60.19% | 0.00 |
| mechanism:D4 | 48 | 61.11% | 61.57% | 0.46 |
| mechanism:FACTOR | 127 | 57.39% | 58.71% | 1.31 |
| dose_level:0 | 64 | 59.38% | 59.03% | -0.35 |
| dose_level:1 | 64 | 62.67% | 61.11% | -1.56 |
| dose_level:2 | 64 | 60.94% | 63.02% | 2.08 |
| dose_level:None | 127 | 57.39% | 58.71% | 1.31 |

## 2. 三条基线门槛（G1 / G1r / G2）

| 基线 | 冻结参考（R26.15） | R28 同集重测 | 门槛=min | 发布版 | 发布版严格更低? |
|---|---:|---:|---:|---:|---|
| 常数先验 | 52.89% | 55.03% | 52.89% | 59.56% | False |
| 只看题面 TF-IDF+LR | 54.22% | 54.76% | 54.22% | 59.56% | False |
| anchor 众数 | 73.33% | **NOT_MEASURABLE** | n/a | 59.56% | UNTESTED |
| family-only（泄漏轴） | — | 53.16% | — | — | 仅作泄漏核验 |
| anchor 记录 exact | 32.00% | **NOT_MEASURABLE** | n/a | 0.63% | UNTESTED |

- **G1 = UNTESTED**：anchor_mode same-set remeasurement NOT_MEASURABLE on R28 (no anchor field); prereg baseline_gate.fail_safe forces G1=UNTESTED
- G1r = UNTESTED；**G2 = FAIL**（skill_hard = 0.1007，prior = 0.5503）——模型在发布版上**高于**常数先验，按预注册不得使用'越过先验'表述。
- R28 无 anchor 字段：G1/G1r 不可执行 → 按 fail_safe 报 UNTESTED + DEGRADED，**不允许任何 HARDER 宣告**。

## 3. E2 剂量-反应（DL 192 题）

- 结局：逐题信息字段准确率（0–1）；主模型 OLS：acc ~ dose + mechanism FE，HC1。次模型 logit：majority-correct(≥5/9) ~ 同设计（预注册 P(correct) 的可行操作化；9/9 结局退化）。
- 总体 acc：dose0 59.38% / dose1 62.67% / dose2 60.94%；单调递减 = False；OLS 斜率 0.781pp/step（CI [-1.82, 3.40]）；logit majority 斜率 0.131（p=0.543）。

| 机制 | n | acc(0) | acc(1) | acc(2) | 单调 | Δ0→1 / Δ0→2 (pp) | acc0−acc2 [95% CI] | OLS 斜率 (pp/step) | 支持? |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| D1 | 48 | 59.72% | 55.56% | 62.50% | False | -4.17 / 2.78 | -2.78 [-11.83, 6.48] | 1.39 | False |
| D2 | 48 | 61.81% | 64.58% | 63.89% | False | 2.78 / 2.08 | -2.08 [-13.52, 9.40] | 1.04 | False |
| D3 | 48 | 60.42% | 61.11% | 59.03% | False | 0.69 / -1.39 | 1.39 [-8.73, 12.11] | -0.69 | False |
| D4 | 48 | 55.56% | 69.44% | 58.33% | False | 13.89 / 2.78 | -2.78 [-13.76, 7.72] | 1.39 | False |

- **HYP-R28-DOSE = REJECTED**：拒绝条件命中（非单调 + 方向与'加难'相反 + 效应绝对值 <10pp + CI 含 0）。四个机制的 acc 三连互不相同（distinct=4）。此结论与 captain 的初步复算一致，修复统计模型不改变否决。

## 4. E3 机制归因（FC；主效应可估，交互不可估）

- 结局：逐题信息字段准确率；**主效应模型** acc ~ D1+D2+D3+D4，HC1；**交互模型状态 = NOT_ESTIMABLE_WITH_16x8**（16 格 × 8 题无法识别 6 个二阶交互；不报为推断结论）。

| 主效应 | β (pp) | SE | z | p | 内层 Holm p (m=4) |
|---|---:|---:|---:|---:|---:|
| D1 | -1.18 | 3.00 | -0.39 | 0.6942 | 1.0000 |
| D2 | -1.87 | 3.01 | -0.62 | 0.5335 | 1.0000 |
| D3 | -2.22 | 3.00 | -0.74 | 0.4592 | 1.0000 |
| D4 | -6.11 | 3.00 | -2.04 | 0.0414 | 0.1657 |

- **H3 不成立**（Holm 后无主效应；D4 名义 p=0.0414，Holm 后 0.1657）。
- 因子 0→1 对比（非参数，题内 bootstrap 10k，未校正）：

| 因子 | acc(0) | acc(1) | diff (pp) | 95% CI |
|---|---:|---:|---:|---|
| D1 | 57.99% | 56.79% | -1.20 | [-7.12, 4.62] |
| D2 | 58.33% | 56.44% | -1.90 | [-7.84, 3.95] |
| D3 | 58.51% | 56.26% | -2.25 | [-8.33, 3.74] |
| D4 | 60.49% | 54.34% | -6.15 | [-12.05, -0.44] |

- 16 格 cell 表（每格 n=8）：已写入 `analysis_e3.json`；所有格的 **record exact = 0**。

## 5. E4 证据敏感性（DEFERRED）

- 状态 **DEFERRED_GPU_HANDOFF**：captain instructed GPU handoff to t14/t21 after E1 repair; E4 inference (40 items x V+/V-/V0 = 120 calls) not executed in this attempt
- V− 可用率（320 题，机械判定）：substitution 271/320 = 84.69%；introduced 49/320 = 15.31%；none 0/320。

| 机制 | substitution | introduced |
|---|---:|---:|
| FACTOR | 101 | 27 |
| D1 | 42 | 6 |
| D2 | 44 | 4 |
| D3 | 39 | 9 |
| D4 | 45 | 3 |

- 计划估计量（材料已就绪）：flip⁺（V+ 翻转 / 命中 V+ gold）、stability⁻（substitution 主指标 + introduced 单列 + not_available 计数）、stability⁰（顺序置换）、blind_flip（全盲交付下的 flip⁺）。substitution 栏 n=32（≥30，可作主指标；<30 则 DESCRIPTIVE_ONLY）。

## 6. E5 多模型区分度

- **UNTESTED**：零付费硬约束 + 本机仅 1 个本地模型；预注册规定可执行模型数 <2 时 E5 记 DEGRADED/UNTESTED；本机可执行模型 ['qwen2.5:7b-instruct-q4_K_M']；云端在零付费约束下禁止。
- **按预注册 S2 的结论是"撤回任务有区分度的主张"，不是"E5 未跑"这种含糊表述。** E5 需要 ≥2 个可执行模型的面板跨度（≥25pp）才能建立区分度；本轮只有 1 个本地模型且零付费禁止云端，面板降级 → 区分度主张撤回，且不得用单模型结果替代。

## 7. Claim gates G1–G9 与最终 headline

| 门 | 状态 | 说明 |
|---|---|---|
| G1 | **UNTESTED** | anchor 同集不可测 → UNTESTED |
| G1r | **UNTESTED** | anchor record-exact 不可测 → UNTESTED |
| G2 | **FAIL** | skill_hard=0.1007（>0 → FAIL） |
| G3 | **PASS** | t6 数据健康（320 互异记录、0 常数字段、每族 1 题、确定性重建） |
| G4 | **PASS** | t6 证书 100% + solver 重推 100% |
| G5 | **PASS** | AMEND-002：lift≤0 且 value-balanced≤0.40 且 p>0.05 |
| G6 | **PASS** | t6 双渲染逐字节一致 320/320 |
| G7 | **UNTESTED** | E5 面板降级 → UNTESTED |
| G8 | **PASS** | conformance 99.69% |
| G9 | **PASS** | n_pairs=320；12 条失败重跑一次（append，未删原行） |

**最终 headline：`DIRECTION_ONLY`。** `harder_claim_permitted=False`；阻断门：['G1', 'G1r', 'G2', 'G7']；DEGRADED：['G1_UNTESTED_ANCHOR_NOT_MEASURABLE', 'G1r_UNTESTED_ANCHOR_NOT_MEASURABLE', 'G7_UNTESTED_PANEL_DEGRADED', 'E4_DEFERRED_GPU_HANDOFF']。
- prereg decision_rules: HARDER requires point>=10pp AND min CI lower>0 AND G1-G9 all PASS; neither condition is met

## 8. 修前 / 修后对照（captain 指出的三个统计 bug）

| 问题 | 修前（attempt 2 早期产物） | 修后（本报告） |
|---|---|---|
| E2 pooled 模型结局 | 9/9 全对（全 0，完全分离；intercept≈−10.49） | 逐题信息字段准确率 OLS + majority(≥5/9) logit；acc 0.594/0.627/0.609 |
| E2 每机制斜率 | D1/D3/D4 斜率逐位相同（−1.8068…） | 四机制独立构数组；斜率 1.39 / 1.04 / −0.69 / 1.39；acc 三连 distinct=4 |
| E3 机制归因 | 完全分离，β≈−1223569，marginal_pp=0 | 主效应 OLS（HC1）+ 16 格 cell 表；交互 NOT_ESTIMABLE；H3=False |
| 失败记录 | 12 条失败按 0 计入主分 | 严格配对只取 parse_ok+stop；失败走 conformance；12 条重跑（11 修好，1 持久失败） |

## 9. Discussion（按 captain 要求原样写入）

> 两臂的 `solver_facts` 与金标逐字节相同，所以**推导本身就是同一个**；E1 只能测"呈现难度"的影响。实测是 0.56pp（attempt-1 的 295 对复算为 1.39pp；全量修复后为 0.56pp，均远低于 10pp 阈值）。这意味着：本设计在原理上就无法产生大幅落差，除非难度来自事实/推导本身——而那需要扩求解器（R29+）。

## 10. 诚实边界

1. 单模型 / 弱基线：仅 Qwen2.5-7B Q4_K_M；结论不外推到前沿模型。E5 未执行（零付费 + 仅 1 个本地模型）。
2. anchor 基线不可测（R28 无 anchor 字段）：G1/G1r=UNTESTED，按 fail_safe 报 DEGRADED；不得用同集常数先验替代后宣称通过。
3. E2 的预注册措辞是 logit P(correct)；9/9 结局退化，故主模型改为逐题准确率 OLS，次模型用 majority-correct logit。两种口径都指向 REJECTED。
4. E3 的 16 格 × 8 题撑不起 4 主效应 + 6 交互；只报主效应，交互明确标 NOT_ESTIMABLE。
5. E4 因 GPU 交接延后；本轮只报可用率与计划估计量，不报稳定性数值。
6. 12 条失败重跑使用了 num_predict=512（主跑 420），仅用于修复；原行保留在 raw 中（rerun_of/rerun_reason），分析取最新行。
7. 数据指纹治理：t6 `BUILD_ACCEPTANCE` 钉的 `build_index.json` 是 `2502aed5…`；t19 实际使用（也是当前磁盘文件）是 `dd6de16a…`（mtime 2026-11-12 20:30:05，t6 之后新增了 n_items/n_public/splits/schema/seed/solver 等顶层元数据）。t19 已对全部 640 条作答重算 prompt 输入与金标哈希，与当前文件 **0 mismatch**；但 t8 应重新冻结 index 指纹，避免验收指纹与磁盘不一致。

## 11. 撤回声明（E5 / S2，必须传播到 t11 / t23）

> **撤回：`任务有区分度`（task discrimination）的主张。** 依据：E5 面板降级为 `UNTESTED` —— 零付费硬约束下本机仅 1 个可执行本地模型（`qwen2.5:7b-instruct-q4_K_M`），云端 1 + 云端锚点 1 不可执行；预注册 S2 规定可执行模型数 <2 时记 DEGRADED/UNTESTED、撤回区分度主张、不得判 PASS。
>
> 这不是"E5 未跑"的中性状态，而是**已按预注册作出的否定性判决**：本数据集在现有证据下**未被建立**模型间区分度。该条必须原样进入 t11 总报告与 t23 论文 Limitations，不得改写为"E5 未完成/待补"。

## 12. 复现

```powershell
$py = "C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
& $py scripts\run_local.py e1        # 640 calls (resumable)
& $py scripts\rerun_failed.py        # 12 failed records, num_predict=512, append-only
& $py scripts\baselines_same_set.py  # same-set constant / qtext-LR / family-only / anchor audit
& $py scripts\analyze.py             # E1-E5 + gates
& $py scripts\make_report.py         # this report + MANIFEST.json
& $py scripts\verify_t19.py          # consistency assertions
```

产物：`e1_raw.jsonl`、`run_config.json`、`baselines_same_set.json`、`analysis.json`、`analysis_e1/e2/e3/e4.json`、`e4_availability.json`、`e4_variants.json`、`e5_availability.json`、本报告、`MANIFEST.json`。
