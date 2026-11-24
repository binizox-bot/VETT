# CONTRIBUTIONS（投稿骨架）

> 定位：**高仪器化度诊断基准**（highly instrumented diagnostic benchmark），不是排行榜；所有数字仅来自 eval_runs 与 gate_ledger（见 `NUMBERS.json`）。

## C1. 可分解的诊断对象，而不是单一准确率

- 一题一记录、一题一族；发布渲染与四剂量全 0 对照共享 `solver_facts` 与 12 字段记录，公开文本是唯一被操纵变量。
- 每条记录带确定性 solver 证书与规则路径；证书的 `rule_path` 只列承载算子，装饰性行为单独登记（数据卡细节）。
- 贡献：把“证据可见性 / 作用域 / 规则版本 / 最小证明”的失败从端到端分数中拆出来，允许后续实验分别估计。

## C2. 一个预注册的负结果：R28 不构成“更难”

- E1 的严格配对 drop 为 **0.557pp**（95% CI **[−0.801, +1.846]**，n=**319**），方向 control 更准 **69** / hard 更准 **47** / tied **203**；预注册结论 **DIRECTION_ONLY**，`harder_claim_permitted=false`。
- E2 剂量准确率为 **59.375 / 62.674 / 60.938%**（非单调），`HYP-R28-DOSE = REJECTED`；E3 `H3=false`，交互 **NOT_ESTIMABLE_WITH_16x8**；整记录 exact **5/638 = 0.78%**。
- 贡献：把“构造了更多剂量/更多证据”与“确实更难”分开报告；负结果本身是可复现的仪器读数，而不是失败被隐藏。

## C3. 基线/消融矩阵与效应量报告

- 同一测试集上的基线：constant prior **0.550347**、question-text TF-IDF+LR **0.547569**、hard **0.595611**、control **0.601184**（`analysis.json`）。
- 双渲染是已执行的消融（E1）；证据预算与证书消融只有计划矩阵，**没有** eval_runs 估计，论文中必须标 `NOT_RUN`，不得填估计值。
- 贡献：把“基线比较”和“消融”写成可复算的表格模板（点估计 + 95% CI + 效应量 + n + 来源）。

## C4. 可审计的发布工程与失败 gating

- 21 个 pipeline gate 的 live_full ledger：**19 PASS / 2 DEGRADED**；DEGRADED 为 `G_ANNOTATION_COVERAGE` 与 `G_JUDGE_COMPARABILITY`，发生在 **mechanical-only** 运行，不是模型准确率结果。
- 数据卡、held-out 协议、单命令复现、输入/输出哈希、R-R7 解析器绑定与“重放=重算评分”均有独立文档；出错路径（编码、时间戳、锚点）保留披露。
- 贡献：把“可复现”从口号变成可检查的 gate ledger + 数据卡 + 复现器组合。

## C5. 诚实的边界作为贡献的一部分

- 半合成数据、记录空间/结构天花板、规则引用装饰性、T1 词表匹配、E5 UNTESTED、人工双标未执行，均在数据卡/Limitations 同页披露。
- 贡献：明确区分“仪器读数”与“关于真实世界的结论”；不把诊断基准包装成排行榜或人类能力结论。

## 非贡献（明确排除）

- 不提出新的 SOTA 模型或训练方法；
- 不声称 R28 比 R26.15 难；
- 不声称 7B Q4 基线可外推到其他模型；
- 不声称 solver 金标等于人类金标。
