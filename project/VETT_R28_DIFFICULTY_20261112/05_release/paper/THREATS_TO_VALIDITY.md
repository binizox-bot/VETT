# THREATS TO VALIDITY（六类逐条：处理 + 残余风险）

> 数字只来自 eval_runs / gate_ledger；没有估计值。每条都给出“已做什么”与“仍然不能说什么”。

## 1. 构念效度（Construct validity）

**威胁**：把“信息字段准确率”当作“规则推理能力/难度”，或把“规则引用数量/证书长度”当作“解释质量”。

**处理**：
- E1 的预注册判定是 **DIRECTION_ONLY**，`harder_claim_permitted=false`；E2 **REJECTED**；E3 **H3=false**；整记录 exact **5/638=0.78%**，说明 12 字段联合正确几乎不可达，不能把字段准确率直接解释成“读懂规则”。
- T1 本地标注是**词表/句式匹配**，不是“语义支持判断”；E5 **UNTESTED**，撤回跨模型区分度主张。
- 证书只作为“可重推的规则路径”，不当作解释质量分数。

**残余风险**：即使我们不声称难度，读者仍可能把 hard/control 的 0.557pp 差异误读为“更难”。**处理**：在摘要、表注、Limitations 同页写 `DIRECTION_ONLY / no harder claim`，并给 CI 跨 0。

## 2. 内部效度（Internal validity）

**威胁**：数据/渲染/评分流程不一致；缓存或重跑改变结果；facts 与 record 不匹配。

**处理**：
- 发布版与对照版同一 `solver_facts` + 12 字段记录；E1 使用 319 个严格配对（两端 parse_ok 且 stop）。
- 12 条失败按 append-only 重跑（原行保留）；G9 PASS；E1 的 `conformance` hard 0.996875 / control 1.0。
- `gate_ledger` live_full：**21** 个 gate，**19 PASS / 2 DEGRADED**；DEGRADED 为 `G_ANNOTATION_COVERAGE`（mechanical-only，coverage 0.0，floor 0.95）与 `G_JUDGE_COMPARABILITY`（无 comparables），不是模型准确率。
- 数据计数/完整性/确定性 gate：`G_DATASET_COUNTS`、`G_DATASET_INTEGRITY`、`G_DATASET_DETERMINISM` 均 PASS（published 320 / held_out 40 / total 360；distinct ratio 1.0；constant fields 0）。

**残余风险**：live_full 是 mechanical-only 运行，不能把它当作“完整模型流水线”的内部效度证明；模型侧只有 t19 的 E1–E5。**处理**：在实验中明确区分 pipeline gates 与模型实验。

## 3. 统计效度（Statistical validity）

**威胁**：小样本、多重比较、CI 跨 0 被误读；把未校正 p 当结论；E4 小 n。

**处理**：
- E1 n=**319**；drop 0.557297pp，CI **[−0.801115,+1.846047]**；方向 69/47/203；符号检验 p=**0.050730**；预注册判定 DIRECTION_ONLY。
- E2 n=**192**；slope +0.78125pp/step，CI **[−1.815290,+3.401827]**；单侧 p=0.279527；REJECTED。
- E3 n=**127**；D1–D4 βpp 的 95% CI 均跨 0；Holm p 均不显著（D4 0.165731）；交互 NOT_ESTIMABLE。
- E4 substitution n=**32**，rate 0.500，Wilson **[0.336306,0.663694]**；introduced n=8；flip n=40 vs floor 0.875；均不支撑强主张。
- 不在文本中把“未校正 p<0.05”当显著；E3 只报 Holm 后结果。

**残余风险**：E1 的 CI 跨 0 但仍接近 0；不能排除小效应。**处理**：结论只写 DIRECTION_ONLY，不写“无差异”或“更难”。

## 4. 外部效度（External validity）

**威胁**：半合成数据、虚构场景、无逐球明细；7B Q4 单模型；结果不能外推到真实板球或其他模型。

**处理**：
- 数据卡/附录明确半合成边界；Cricsheet 只作可选附录，不作为主结论。
- E5 只有 **1** 个可执行本地模型（qwen2.5:7b-instruct-q4_K_M），零付费禁止云端；E5=**UNTESTED**，区分度主张撤回。
- 不在摘要/结论中写“通用模型能力”或“真实比赛难度”。

**残余风险**：即使不声称外推，读者可能把 R28 当作真实分布。**处理**：数据卡与 Limitations 同页写“semi-synthetic, diagnostic only”，并把 Cricsheet 列为未来工作。

## 5. 生态效度（Ecological validity）

**威胁**：R28 是单球规则/卷宗任务，不是完整比赛；没有时间压力、队伍互动、裁判现场决策；发布渲染的阅读负担不等于真实工作流。

**处理**：
- 论文把任务定义为“证据受限的单球规则判定”，不声称模拟完整比赛。
- 双渲染只操纵呈现层，不模拟真实裁判环境；E1 只测模型在给定卷宗下的字段准确率。
- 不将 token 长度/阅读时间当作生态难度证据（数据卡只作构造统计）。

**残余风险**：实验室任务与真实裁判工作流仍有差距。**处理**：在 Discussion 明确“instrumented diagnostic, not ecological simulation”，并建议未来做人类双标/工作流研究。

## 6. 金标效度（Gold validity）

**威胁**：金标是确定性 solver 输出，不是人类标注；模型自写证书/答案不能当金标；T3/abstention 小样本无区分度。

**处理**：
- 金标由冻结 solver 生成；发布版/对照版 facts/record 相同；证书可重推（gate G4 PASS）。
- 模型输出只作预测，不作金标；E5 UNTESTED；T3 小样本只描述性，不作质量门（本论文不使用未支持的 T3 数字）。
- **人工双标未执行**：t24 kit 的状态是 `ready_for_handoff=true`、`ready_to_annotate=false`、无 human gold；H1/H2/H3 不得声称。
- 这是**发表阻断项**，写入数据卡 B6 与 Limitations。

**残余风险**：solver 规则实现本身可能有建模选择偏差；没有人类一致性无法量化。**处理**：把“solver-generated gold, not human-validated”写进标题级限制；在人工双标完成前不投稿为“人类金标基准”。

---

## 汇总表

| 威胁 | 已处理 | 残余风险 | 论文动作 |
|---|---|---|---|
| 构念 | DIRECTION_ONLY / no harder；T1 词表；E5 UNTESTED | 读者误读 | 同页披露 |
| 内部 | 同 facts 双渲染；append-only 重跑；21 gates（19 PASS/2 DEGRADED） | mechanical-only 非全模型 | 明确 gate 与实验分层 |
| 统计 | n/CI/效应量；Holm；E4 小 n | 小效应/功效不足 | 只写 DIRECTION_ONLY |
| 外部 | 半合成；单模型；E5 UNTESTED | 外推误读 | 数据卡 + Limitations |
| 生态 | 单球任务定义 | 真实工作流差距 | Discussion |
| 金标 | solver 可重推；模型不作金标 | 无人类一致性 | **发表阻断项** |
