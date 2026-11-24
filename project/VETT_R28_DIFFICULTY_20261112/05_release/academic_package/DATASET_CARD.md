# R28 Dataset Card（Datasheets for Datasets 结构）

- **Dataset**：`VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`
- **Design**：`R28-DOSE-DIAGNOSTIC-PAIR`
- **Version**：R28 candidate，2026-11-12
- **Paper role**：诊断/误差分解基准（diagnostic benchmark），**不是**真实板球分布样本，**不是**难度基准，**不是**人类金标。
- **配套核验**：`04_verify/INDEPENDENT_VERIFICATION.md`（t8，独立复算）、`04_verify/J_GATE.json`（J 门）、本包 `reproduce.py`。
- **数据位置**：`VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/`（`public/` + `variants/` 为公开包；`held_out/` 不发布）。
- **本包不复制数据本体**：只提供数据卡、许可、held-out 协议、复现脚本和边界声明；数据按同一交付根目录引用。

---

## 1. 动机（Motivation）

R26.15 的测量暴露了三类不可分离的混淆：字段准确率受边际分布支配、题面文本可绕过卷宗、规则引用数量不等于推理必要性。R28 的目标不是“造一个更难的数据集”，而是造一个**可分解误差来源的诊断对象**：

1. **独立题**：一题一记录、一题一族；族名是中性哈希，不能作为泄漏信号。
2. **2×2×2×2 因子平衡**：FC（factor core）四个二值因子各 128 题中的平衡组合；DL（dose ladder）D1–D4 各 48 题，剂量 0/1/2 各 64 题。
3. **常数字段非零**：R26.15 中恒为 0 的 `ledger.BYE` / `ledger.LEG_BYE` / `ledger.PENALTY` 在 R28 发布集分别非零 96 / 78 / 153 次。
4. **孪生卷宗**：同一 `solver_facts` 与同一 12 字段记录，渲染成发布版（带剂量）与对照版（四剂量全 0）；差异只在呈现层。

**不适用**：真实比赛预测、球员/球队能力估计、规则文本生成质量评估、任何“模型已理解板球规则”的结论。

## 2. 构成（Composition）

| 项目 | 值 | 说明 |
|---|---:|---|
| 发布题（public） | **320** | `public/<item>/public_instance.json` + `variants/<item>/public_instance.json` |
| held-out | **40** | `held_out/`，不进入公开包；见 `HELD_OUT_PROTOCOL.md` |
| 总实例 | **360** | 320 + 40 |
| 发布场景 | **64** | 320/64 = 5 题/场；held-out 40 场独立，不计入公开 64 |
| FC（factor core） | **128** | 2×2×2×2，16 格 × 8 |
| DL（dose ladder） | **192** | D1–D4 各 48；剂量 0/1/2 各 64 |
| 记录字段 | **12** | 9 个信息字段 + 3 个 ledger 字段 |
| 互异记录 | **320/320 = 1.0** | 发布集记录两两不同 |
| 常数记录字段 | **0** | `reproduce.py` 逐字段复核 |
| HA18 封顶 | **11** | 合法送达型 dismissal 可达上限；见边界 B2 |

### 2.1 分布（发布集，`reproduce.py` 独立重算）

- `delivery_status`：`DEAD_REBALL 1 / LEGAL 166 / NO_BALL 100 / WIDE 53`
- `dismissal`：`BOWLED 2 / CAUGHT 2 / HIT_BALL_TWICE 50 / LBW 2 / NONE 124 / OBSTRUCTING_FIELD 50 / RUN_OUT 86 / STUMPED 4`
- ledger 非零：`ledger.BYE 96 / ledger.LEG_BYE 78 / ledger.PENALTY 153`
- 合法 dismissal（BOWLED/LBW/CAUGHT/STUMPED）= **10**；加上 `DEAD_REBALL` 的 1 条可达记录，合计 **11**（HA18）。

> 这些比例是**构造配额**，不是真实板球频率。不得把分布当作外部效度证据。

## 3. 生成方式（Generation）

- **金标**：冻结的确定性单球 solver `vett_r25.solver`（`src/vett_r25/solver.py`，sha256 见 `MANIFEST.json`），**无任何语言模型参与事实、金标或证书**。
- **事实注入**：每题的 `solver_facts` 由场景模板/定向枚举选择；同一 facts 渲染成发布版和对照版（四剂量全 0），两版 `solver_facts` 与 12 字段记录逐字节相同（t6 REQ4：320/320）。
- **证书**：每题生成 `certificate.json`，`rule_path` 只列出**承载算子**（消融会改变记录或使推导无法成立）；装饰性行为单独登记为 `presentation_only_operators`，不进入 `rule_path`。
- **确定性**：同 seed（20261112）+ 同配置可重建；`MANIFEST.json` 的 `tree_aggregate` 为 `0f7dedd6…`（t6 构建期）。当前 `build_index.json` 的冻结收据见 `04_verify/BUILD_INDEX_FREEZE.json`（`dd6de16a…`）。

## 4. 预处理（Preprocessing）

1. solver 记录先扁平化为 12 个 canonical 字段（`batter_runs` … `total_runs`）。
2. 记录用 `json.dumps(sort_keys=True, ensure_ascii=False, separators=(",", ":"))` 做 sha256 绑定；证书/记录/事实各自有 sha256。
3. 公开包只含 `public/` 与 `variants/`；`private/`、`held_out/`、`audit/` 不进入公开包（审核方另行持有）。
4. 没有 NLP 清洗、没有去标识化、没有外部抓取；源素材是虚构场景（见 B1）。

## 5. 适用与不适用（Uses / Non-uses）

**适用**
- 诊断“证据可见性 / 范围 / 规则版本 / 最小证明”四维失败；
- 研究规则引用装饰性、证书可解释性、长上下文检索与事实一致性；
- 作为可复现的“诊断对象”，而不是排行榜。

**不适用**
- 真实板球结果预测或投注；
- 任何“本数据集比 R26.15 更难”的主张（见 B4）；
- 把本地模型 T1 标注当作“语义支持判断”（见 B5）；
- 未经人工双标的金标推断（见 B6）。

## 6. 维护与版本（Maintenance）

- 数据构建脚本：`03_build/scripts/build_dataset.py`；配置：`config/r28_build_config.json`（sha256 `cc78be40…`）。
- 冻结合同 v1.2.0：`02_contract/r28_contract.json` sha256 `dc657f9c…`；预注册 v1.2.0：`preregistration.json` sha256 `b5c39849…`。
- 任何数据/规则/指标改动都必须走 amendment + 重新冻结；不要就地改 `dataset_r28/`。
- 指纹：`04_verify/BUILD_INDEX_FREEZE.json`（文件 + 逐题 header 双钉）、`04_verify/verification.json`（t8 独立验证）。
- **单命令复现（t20 闭环）**：`cd 05_pipeline && python verify/run_closed_loop_verification.py --config r28.toml`；修复后已在 **vanilla Windows GBK 控制台（chcp 936，未设 PYTHONUTF8/PYTHONIOENCODING/PYTHONLEGACYWINDOWSSTDIO）** 实测 **10/10 PASS、exit 0**，无需环境前置；pre 归档与 append-only 复核见 `04_verify/INDEPENDENT_VERIFICATION.md`。若使用修复前代码才需要 `PYTHONUTF8=1`。

---

# 七个诚实边界（论文必须同页披露）

> 任务要求“六个诚实边界”；下面 B1–B6 是六条主边界。B7 是发布许可的附加边界（规则文本引用），同样必须披露。

## B1 — 半合成：事实由场景模板注入，不是从真实比赛抽取

- 220 场源素材是**半合成**的虚构场景（虚构球场/球员），且源侧只有**局级聚合**，**没有逐球事实明细**（`AUDIT_GOAL_AND_DESIGN_20261112.md` §189–191）。
- 每题的 `solver_facts` 是模板/枚举注入的，不是从真实 delivery 记录抽取的；因此 R28 的分布、频率、相关性都不是真实板球分布的无偏样本。
- “孪生卷宗”只保证两版**facts/record 相同**，不保证公开文本相同；呈现层正是被操纵的变量。
- **不得**用 R28 估计真实比赛中的规则歧义率、裁判错误率或模型泛化能力。

## B2 — 记录空间与结构天花板：761 下界 / 392 需求 / 11 合法 dismissal

- 定向枚举（67 个 status × dismissal × ledger-mask 层）得到的**可达互异记录下界 = 761**；67 层逐层相加 = 761（`02_contract/evidence/record_space_probe.json`，`reproduce.py` 重算）。
- N=320 的设计需求 = 320 + 40 held-out + 10%×320 = **392**，761 ≥ 392，满足安全余量；这是“够用”，不是“空间大”。
- 合法送达型 dismissal 仅 **11** 条可达：`DEAD_REBALL 1 / BOWLED 2 / LBW 2 / CAUGHT 2 / STUMPED 4`；HA18 封顶 11。原因是冻结的**单球 solver 表达力**，不是数据配额问题。
- 扩大记录空间需要 R29+ 扩展 solver；在 R28 上扩大 N 只会重复组合，不会增加结构多样性。

## B3 — 规则引用的装饰性（t5 机器证明）

- 360 个实例共 **1,546** 个唯一渲染规则 span；其中 **488（31.57% ≈ 31.6%）** 是**从未承载**的 span（presentation-only-only；`reproduce.py` 按 `rule_path` 与 `presentation_only_operators` 的 span_id 集合重算）。
- **360/360** 实例至少含一个装饰性算子。
- `BAT_CREDIT` 118 次、`NB_COUNT` 100 次、`WIDE_COUNT` 53 次**从未必要**；`COUNTS_IN_OVER` 在 **317/360** 实例中非承载。
- 证书 `rule_path` 只含承载算子：360 份证书共 1,199 个 `rule_path` 条目，与 `presentation_only_operators` 的交集为 **0**。
- 三条方法局限（原文见 `derivation_depth_witness.json.limitations`）：
  1. 消融是**单算子 leave-one-out**，不覆盖“仅交互才必要”的情况；
  2. 必要性是**相对冻结单球 solver**的，不证明人类读者觉得难；
  3. **推导深度不是已验证的难度机制**，其效应 UNTESTED，必须由 E2 检验后才能作难度主张。
- 因此：规则引用数量/证书长度不能当作难度或解释质量的代理指标。

## B4 — 难度主张不成立（必须与数据集同页披露）

- E1（n=319 严格配对）：drop = **0.557pp**（hard 59.56% vs control 60.12%），按题 bootstrap 95% CI **[−0.801, +1.846]**，跨 0；`harder_claim_permitted = false`，headline = **DIRECTION_ONLY + DEGRADED**。
- E2：剂量准确率 59.38 / 62.67 / 60.94%，**非单调**；`HYP-R28-DOSE = REJECTED`。
- E3：主效应 Holm 后均不显著；交互 `NOT_ESTIMABLE_WITH_16x8`；`H3 = false`。
- record-exact = **5/638 = 0.78%**（hard 2/319、control 3/319）。
- **数据卡、摘要、图注都不得暗示 R28 比 R26.15 难。** 若论文需要“难度”一词，必须同时给出上述四个数和 “no harder claim” 声明。

## B5 — T1 标注的机制限定；E5 = UNTESTED

- 本地 T1（`annotations_T1_factor_visibility.jsonl`）总体 312/320 = **0.975**，但它是**词表/句式匹配**，不是“模型判断证据支持”：
  - `authority_policy` role：24/32 = **0.75**；
  - constant-false 基线：**0.85**；
  - 余量仅 **+0.125**；POS_OVERRIDE 40/48=0.8333，负类 1.0。
- 因此 T1 可作为**标注劳动力/召回检查**，**不得**写成“本地模型能判断证据支持”的能力证据。
- E5（跨模型区分度）只有 1 个可执行本地模型（qwen2.5:7b-instruct-q4_K_M），零付费约束禁止云端 → **E5 = UNTESTED**；区分度主张已撤回，**不得把 UNTESTED 写成“未跑”或“不适用”，也不得当作 PASS**。
- 云端 T3 n=12 < 30：一致率只能 DESCRIPTIVE_ONLY，不能作推断性质量门（R-C4）。

## B6 — 金标未经人工双标；这是发表阻断项

- R28 的金标是确定性 solver 输出，**不是人类标注**；截至本包生成，人工双标**尚未执行**（E 阶段尚未启动）。
- t24 已交付可移交的人工核验 kit（`04_verify/human_verification_kit/`），但 `STATUS.json` 明确 `ready_to_annotate=false`、`ready_for_handoff=true`，且**没有产生任何人工 gold**。
- 人工双标未完成前：论文必须把“gold 未经人工一致性验证”写入 Limitations 与数据卡；**不得**声称 H2（关键缺陷=0）或 H1（每维≥98%）已满足。
- 这是**发表阻断项**，不是“以后再做”的脚注。

## B7 — 许可/规则文本引用边界（附加）

- 数据候选 **CC BY 4.0**；代码候选 **MIT**（见 `LICENSE_DATA_CC_BY_4.0.md` / `LICENSE_CODE_MIT.txt`）。
- `src/vett_r25/scenarios.py` 的 `RULE_TEXT` 是**简短的规则摘要/改写**，引用 MCC Laws 的条号与概念；仓库中没有找到 MCC 规则全文的再分发许可，也没有找到显式 LICENSE 文件。**对外发布前必须做一次法律复核**：保留“引用/改写”声明与条号，不复制 MCC 全文；如复核不通过，替换为自建规则摘要。
- 220 场源素材的原始许可需由数据所有者确认；本包只声明“生成器输出”的许可，不替源素材授权。
- 若未来接入 Cricsheet，必须遵守其许可并在数据卡中声明来源/衍生关系（见 `EXTERNAL_VALIDITY.md`）。

---

## 7. 复现

```powershell
cd VETT_R28_DIFFICULTY_20261112\05_release\academic_package
D:\Conda\python.exe reproduce.py --check
```

预期：`[ok] all metrics match metrics_expected.json`。所有数字来源见 `REPRODUCIBILITY.md`；无网络、无模型调用、无付费 API。
