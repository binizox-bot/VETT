# 论文骨架 v0.1（2026-11-13）
> 工作标题：*Maintaining a Consistent Table under Revision: A Paired Diagnostic of State Tracking in Small LLMs*

## Abstract（草稿）
从叙述文本生成结构化表格，不只是抽取：模型必须在顺序变化、事实修订、来源冲突与证据缺失下，
维持一张正确、稳定、内部一致的表格。我们用 220 场板球叙述—记分卡语料构建配对诊断：
10 场深度物化样本、49 个字段级证据与闭合约束、8 类受控变体，并在两个 7–9B 本地模型上
比较直接生成、闭合传播、提示规则三种系统。三个稳健发现：
(1) 纯换序使 17–29% 的已正确字段变错（同 prompt 重测 0/294）；
(2) 证据缺失时模型 100% 编造，从不输出 UNKNOWN；
(3) 外部闭合修复能消除账目矛盾（闭合率 0.58→1.00），但对不可由闭合恢复的修订零提升
（0.529 vs 0.529），说明“一致性修复”不能替代“状态跟踪”。

## 1. Introduction
- 表格生成 = 抽取 + 聚合 + 版本 + 冲突 + 闭合。
- 聚合准确率把五种能力混成一个数（引用 R28 的 law/accounting 分裂）。
- 贡献：
  1. 配对诊断集（字段证据、可回答性、闭合、8 变体）；
  2. 顺序/重测分离的可靠性证据；
  3. 缺证拒答的失败模式；
  4. 负结果：闭合修复 ≠ 状态跟踪。

## 2. Task & Data
- 源池 220 场；可解析 218；闭合干净 191（87.6%）；缺陷 27；不可解析 2。
- pilot 10 场：分层抽样（长度 × L2+L3 × 结果类型），28 core 字段，49 字段完整版。
- 每场产物：fields.jsonl（level/depends_on/answerability/evidence_sentences）、closure.json、8 变体。
- 数据边界：模板注入、无逐球明细、合成名称（DATASET_CARD）。

## 3. Protocol
- 变体：control / shuffled / revised / revised_hard / conflict / missing / distractor / revision_inline。
- 系统：direct / closure（Python 重算派生字段）/ guided（prompt 写规则）。
- 指标：changed acc、stale rate、retention、order C→W、UNKNOWN acc/overclaim、closure rate、字段级配对。
- 预注册 + 2 次 amendment；温度 0、固定 seed。

## 4. Results（填入 PILOT_RESULTS 数字）

### 4.1 H1：顺序效应不是噪声
| 比较 | 对→错 | 95% CI |
|---|---:|---|
| 重测 | 0/294 | — |
| 换序 | 42/294 | [10.8, 18.8] |
Fisher p=4.7e-14。

### 4.2 Pilot 主表
（见 PILOT_RESULTS 表；qwen/llama × direct/closure/guided）

### 4.3 三个稳健发现
1. 换序 C→W 17–29%，跨模型复现。
2. missing UNKNOWN 正确率 0.000（全部编造）。
3. revised_hard：direct=closure=0.529 → 闭合修复不补抽取。

### 4.4 Oracle 证据诊断
仅保留证据句后准确率反而下降（llama −7.8pp，qwen −9.7pp）→ 失败不在检索，在聚合/状态维护。

### 4.5 方法负结果
- closure 在可闭合修订上 0.54/0.62 → 0.78/0.89，但 hard 修订零提升。
- guided 对 qwen 无效；对 llama 63/70 解析失败。
- stale rate 0–2.7%；行内更正旧值率 0 → 旧值残留不是主失败模式。

## 5. Discussion
- 为什么聚合指标掩盖顺序不稳定（42 好 + 39 坏 ≈ 净零）。
- 一致性修复 vs 状态跟踪：前者是约束求解，后者需要事件级版本。
- 对 benchmark 设计的建议：逐字段 + 配对 + 缺证 + 不可闭合修订。

## 6. Limitations
- 半合成、单领域、英语；10 场；2 个 7–9B 模型；无人工金标（计划中）。
- revised 的 closure 优势部分按定义正确；hard 修订已分离。
- llama guided 的格式失败需单独报告。

## 7. Contributions（最终版）
(i) 带字段证据/可回答性/闭合的配对诊断集；
(ii) 顺序 vs 重测的可靠性分离；
(iii) 缺证拒答失败模式；
(iv) 闭合修复的边界（负结果）。

## 待补实验
- panel 320×3 完整身份修复结果；
- gemma2 pilot；
- 事件账本最小实现（若时间允许）；
- 30 场复现（G4 门）。
