# ABSTRACT（投稿骨架，非最终稿）

**Title（working）**：R28: A Highly Instrumented Diagnostic Benchmark for Evidence-Grounded Rule Decisions

**Background.** 规则/多跳推理基准通常以端到端准确率或“是否更难”作为主要信号，但准确率同时混合了证据可见性、作用域判定、规则版本选择与最小证明构造等不同失败来源。R28 的目标不是提出更高的排行榜分数，而是提供一个**可分解、可审计、可复现**的诊断对象：每题有独立卷宗、确定性 solver 金标、证书、规则路径与双渲染对照。

**Data.** 在 `05_pipeline` 的 gate ledger 中，R28 发布集为 **320** 题、held-out **40** 题、合计 **360** 题（`G_DATASET_COUNTS`/`G_DATASET_INTEGRITY`）；记录互异率 **1.0**、家族互异、常数信息字段 **0**、最大发布 token **1339**。数据是半合成的：事实由场景模板注入，不是从真实比赛逐球抽取。

**Evaluation.** 预注册的配对实验（E1）比较发布渲染与四剂量全 0 的对照渲染（同一 facts/记录）。在 **319** 个严格配对上，信息字段准确率为 **59.561%**（hard）与 **60.118%**（control），drop **0.557pp**，按题 bootstrap 95% CI **[−0.801, +1.846]**；方向为 control 更准 **69** / hard 更准 **47** / tied **203**，符号检验 p=**0.0507**；整记录 exact 为 **5/638 = 0.78%**。预注册结论为 **DIRECTION_ONLY**，`harder_claim_permitted=false`。剂量实验 E2 的准确率为 **59.375% / 62.674% / 60.938%**（非单调），`HYP-R28-DOSE = REJECTED`；因子实验 E3 的 `H3 = false`，交互 **NOT_ESTIMABLE_WITH_16x8**；E4 的 V− substitution 为 **0.500**（n=32，95% CI [0.336, 0.664]）；E5 因只有 1 个可执行本地模型、零付费约束禁止云端，记为 **UNTESTED**。

**Contributions.** 本文贡献是（i）一个高仪器化度的诊断基准与审计协议；（ii）一个预注册的“难度不成立”负结果及可复现的效应量报告；（iii）规则引用/证书与双渲染的消融框架；（iv）一套把数据卡、held-out 协议、失败 gating 与人工双标阻断项绑定的发布工程。我们不声称 R28 比 R26.15 更难，也不声称 7B Q4 基线可外推到其他模型。

**Limitations.** 半合成数据外部效度有限；唯一可执行模型是 7B Q4 弱基线，不能外推；金标未经人工双标，**这是发表阻断项**；E5 是 UNTESTED，不得写成“未跑”或当作 PASS。

> 所有数字来源：`eval_runs/t19_e1e5_20261112/analysis.json`、`analysis_e4_supplemental.json`、`e1_raw.jsonl`、`05_pipeline/runs/live_full/gate_ledger.jsonl`；见 `NUMBERS.json`。本文不写未在这些来源中的估计值。
