# VETT 一体化论文项目：完整报告

日期：2026-11-13  
范围：220 场语料审计、H1 复算、pilot-10 一体化样本、本地模型实验、方法验证与论文骨架  
费用：全部本地推理，付费 API 调用 0 次，¥0

---

## 0. 执行摘要

本项目已回答并把问题收束为一个核心命题：

> 模型能否从叙述文本中维护一张正确、稳定、内部一致的表格？

围绕它完成了四件事：

1. 复核 220 场语料的真实能力边界（不是长上下文任务；瓶颈在输出与聚合）。
2. 复算 H1 正确性转移，证明“换序破坏”是真实状态不稳定，而非采样噪声。
3. 构建 10 场一体化样本：49 字段（28 个核心评分字段）、字段证据、可回答性、闭合约束、8 类配对变体。
4. 用两个 7–9B 本地模型完成探索实验，得到三个稳健发现与一个关键负结果。

三个稳健发现：

- 纯换序使 14.3%–29% 的“原本正确”字段变错；同 prompt 重测为 0/294。
- 证据缺失时，所有模型、所有系统的 UNKNOWN 正确率都是 0.000（100% 编造）。
- 只给“证据句”反而更差（−7.8pp / −9.7pp），长文本定位不是主瓶颈，聚合与状态维护才是。

一个关键负结果：

- 外部闭合传播（closure）在“可闭合修订”上把 changed 字段准确率从 0.54/0.62 提到 0.78/0.89，
  但在“不可闭合修订”（投手间转移 wicket）上，direct 与 closure 完全相同（0.529）。
- 因此它只是“一致性修复层”，不是“状态跟踪器”。这是论文 RQ3 必须诚实处理的核心。

当前可投稿定位：ACL/EMNLP Resource & Evaluation 或 LREC（诊断 + 负结果 + 数据资源），
而不是主会方法论文。理由见第 9 节。

---

## 1. 背景与目标

原计划把三条线分开推进（220 场数据集、R28 扰动、状态方法），容易变成“三个项目都做了很多，
但论文主线不清楚”。本报告采用收束后的主线：

- RQ1：从真实叙述文本生成整场表格，能力边界在哪里？
- RQ2：在只改变证据状态的配对扰动下，失败如何变化？
- RQ3：显式状态机制（版本化账本 + 依赖传播）能否改善这些失败？

三部分的关系是：RQ1 建立任务与字段级证据，RQ2 拆出失败机制，RQ3 检验机制性修复。

---

## 2. 数据事实核查

### 2.1 规模

| 指标 | 数值 |
|---|---|
| 源池 | 220 场 |
| 可解析 | 218 场 |
| 完全闭合 | 191 场（87.6%） |
| 至少一项金标缺陷 | 27 场（12.4%） |
| 不可解析 | 2 场（match_0004 两局制、match_0066 Abandoned） |

### 2.2 不是“超长文本”

| 指标 | min | p10 | median | p90 | max |
|---|---:|---:|---:|---:|---:|
| commentary tokens | 876 | 1,194 | 1,641 | 2,054 | 2,462 |
| scorecard tokens | 608 | 1,168 | 1,360 | 1,538 | 2,496 |
| 每场表格数据行 | 45 | 87 | 97 | 106 | 168 |
| evidence_chain.md 条目 | — | — | 约 15 | — | — |

结论：最大 commentary 也只有约 2.5k tokens，离 8K 上下文很远。论文不能声称 long-context，
应写成 narrative-dense state maintenance（叙述密集的状态维护）。

### 2.3 输出长度才是旧瓶颈

219/220 场的 scorecard 超过 640 tokens。旧实验的 num_predict=640 必然截断；
这解释了此前“吞吐差 23 倍”的现象——瓶颈是输出长度，不是输入长度。
因此本项目的实验一律使用短 JSON 输出（28 核心字段，约 440 tokens/次）。

### 2.4 逐字段证据层可以零成本重建

现有 evidence_chain.md 每场只有约 15 条，不是逐字段证据。
但生成器中的 build_evidence_map() 可从 scorecard 确定性重建完整证据图：

- match_0001 实测 61 条；
- L1 = 22，L2 = 39；
- 每条含 field / value / level / evidence_type / operand_of / difficulty_class / placement_phase；
- operand_of 就是字段依赖边。

这是整个项目最大的一笔成本节省：第二层（字段证据）与第四层（依赖/闭合）不需要 LLM 标注。

### 2.5 220 场闭合审计

对 218 场执行 6 类闭合约束（并修正 cricket 规则）：

- run-out 不计入投手 wicket；
- 追逐局 FOW 末值允许小于总分。

缺陷分布：

| 缺陷 | 场次 |
|---|---:|
| bowling_recon（投手失分 ≠ 总分 − byes − legbyes） | 19 |
| bat_plus_extras（击球和 + extras ≠ 总分） | 8 |
| wicket_sum（投手 wicket + run-out ≠ 总 wicket） | 7 |
| fow_monotone | 1 |
| 至少一项 | 27 |

发布时必须给这 27 场打 gold_defect 标；pilot 只从 191 场干净样本抽取。

---

## 3. H1 正确性转移复算

数据：40 题 × 12 字段 = 480 个 cell；三组比较。

| 比较 | 对→对 | 对→错 | 错→对 | 错→同错 | 错→异错 | 均正确字段 |
|---|---:|---:|---:|---:|---:|---:|
| 同 prompt 重测 P1–P2 | 294 | 0 | 1 | 180 | 5 | 7.35 → 7.38 |
| 纯换序 P1–V0 | 252 | 42 | 39 | 90 | 57 | 7.35 → 7.28 |
| 跨 max_tokens P1–E1（参考） | 294 | 0 | 9 | 169 | 8 | 7.35 → 7.58 |

统计：

- 换序 对→错 = 42/294 = 14.3%，Wilson 95% CI [10.8%, 18.8%]；
- 重测 对→错 = 0/294；
- Fisher 单侧 p = 4.7 × 10⁻¹⁴；
- 40 题中 18 题变差、11 题变好、11 题不变；净变化仅 −0.075 字段/题。

解释：平均值把方向抹平了。换序同时造成 42 个“对→错”和 39 个“错→对”，
净效应接近零，但状态发生了 81 次翻转。这说明聚合准确率是顺序不稳定的遮盖物。

---

## 4. 10 场一体化样本（pilot10）

### 4.1 抽样

规则：191 场干净样本中，按 commentary 长度三分位 × (L2+L3) 三分位 × 结果类型分层，固定种子。

| match | tokens | L2+L3 | 结果 |
|---|---:|---:|---|
| match_0090 | 1,254 | 7 | Norchester Won By 7 Wickets |
| match_0167 | 1,203 | 8 | Bayport Women Won by 37 Runs |
| match_0203 | 1,194 | 30 | Ridgeline Won by 5 Wickets |
| match_0035 | 1,700 | 6 | Capeview Won by 82 Runs |
| match_0159 | 1,700 | 8 | Coastvale A Won By 22 Runs |
| match_0007 | 1,706 | 22 | Cedar Heights XI Won by 87 Runs |
| match_0092 | 1,865 | 7 | Ridgegate Won By 1 Wicket |
| match_0108 | 2,133 | 12 | Bayview Royals Women Won By 164 Runs |
| match_0182 | 2,204 | 27 | Cedar Vale Won by 140 Runs |
| match_0091 | 1,699 | 7 | Norchester Won By 93 Runs |

### 4.2 每场目录

    match_XXXX/
      source/                 原始 commentary / scorecard / meta（只读复制）
      fields.jsonl            49 字段：level、depends_on、answerability、evidence_sentences
      closure.json            6 类闭合约束及逐条状态
      variants/
        control/              确定性重渲染（RQ2 配对基准）
        shuffled/             同局内句序打乱
        revised/              wides↔byes 等额转移（可闭合恢复）
        revised_hard/         投手间转移 1 个 wicket（闭合不可恢复）
        conflict/             低权威记分员便条与正文冲突
        missing/              删除 extras 证据句，受影响字段 = UNKNOWN
        distractor/           插入相似但无关的旧比赛句
        revision_inline/      正文后文正式更正 POM（版本化探针）
      manifest.json           sha256、edit_log、changed/unknown、泄漏检查

### 4.3 字段层

- 49 个可评分字段：6 个比赛级 + 每局 21 个；
- 28 个核心字段用于实验：总分、wicket、extras 四项、击球和、投球失分、最大伙伴、
  每局最佳击球 runs、每局最佳投球 figures；
- 答案性分布：351 direct / 108 aggregate / 31 underdetermined（共 490）；
- 每个字段带句级证据位置（evidence_sentences），用于 oracle 诊断。

### 4.4 变体规则（确定性，禁止泄漏）

- control：同 md、同 seed 重渲染，作为严格配对基准；
- shuffled：同局内句子打乱，gold 不变；
- revised：wides 减 2、byes 加 2，同时把投手失分与 wides 减 2；总分与 extras 不变；
- revised_hard：把 1 个 wicket 从一名投手转给同队另一名投手；总分、extras、闭合全不变；
- conflict：加入未签字的低权威便条，把 extras 说成 +3；gold 取正文；
- missing：删除 extras 句，受影响字段标 UNKNOWN；
- distractor：插入另一场比赛的相似数字，gold 不变；
- revision_inline：正文末尾加入官方更正，把 POM 从 A 改为 B；gold 只改 POM。

### 4.5 验证结果

validation.json：10/10 场 all_ok。

- 基础表与修订表都闭合；
- 6+ 变体齐全；shuffled/conflict/distractor 的 gold 与 control 完全一致；
- revised 的 changed_fields 与结构化重算一致（3 或 6 个字段）；
- 修订句在文本中真实出现（如 wides 15→13、byes 2→4，总分 21 不变）；
- missing 正确标出 1–3 个 UNKNOWN 字段；
- 渲染确定性：同 seed 两次逐字节一致；
- 泄漏检查 0 命中。

---

## 5. 预注册

PILOT_PREREGISTRATION.md 在跑模型前冻结，含：

- 7 条假设（H1–H7）；
- 3 个系统；
- 7 个主要终点；
- 排除与计分规则；
- 判定阈值。

冻结哈希在 prereg_freeze.json。两次 amendment 已记录：

1. 新增 revision_inline 变体（版本化探针，在跑之前声明）；
2. 评测限 28 个核心字段（输出成本原因，49 字段仍保留）。

---

## 6. 实验设置

模型（本地 Ollama）：

| model | digest（前 12） | 量化 |
|---|---|---|
| qwen2.5:7b-instruct-q4_K_M | 845dbda0ea48 | Q4_K_M |
| llama3.1:8b | 46e0c10c039e | Q4_K_M |

模型身份 bug 已修：原实现 service.model_info(tag=config.MODEL_TAG) 的默认参数在 import 时绑定，
后续修改 config 不生效，导致 llama/gemma 行被写成 qwen 的 digest。
新脚本 panel_v2.py 显式传 tag，探针已验证三模型 digest 分离。
完整 960 次面板重跑进行到 qwen 182/320 时主动停止，可用 scripts/panel_v2.py 续跑。

系统：

- direct：一次调用输出字段 JSON；
- closure：同 direct，但 Python 按闭合规则重算 total_extras / total_runs / bowling_charged；
- guided：prompt 内写账目规则，无后处理（同预算强提示基线）。

解码：temperature=0，seed=20261112，num_ctx=8192，num_predict=700（guided 900）。

规模：最终 460 条有效行；含 oracle 与 hard 补测、被丢弃的 guided 首轮，累计约 700 次本地调用。

费用：¥0。未调用任何付费 API。

---

## 7. 主结果

### 7.1 主表（10 场 macro 平均）

| model | system | 原表 acc | 换序 对→错 | revised changed | 旧值残留 | 未变保持 | 缺证 UNKNOWN | 闭合率 | 字段级配对 | hard changed |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| llama3.1:8b | direct | 0.738 | 0.170 | 0.622 | 0.027 | 0.767 | 0.000 | 0.683 | 0.731 | 0.529 |
| llama3.1:8b | closure | 0.744 | 0.294 | 0.892 | 0.000 | 0.760 | 0.000 | 1.000 | 0.728 | 0.529 |
| llama3.1:8b | guided | 0.066* | 0.190 | 0.108* | 0.000 | 0.145* | 0.000 | 0.667 | 0.072* | — |
| qwen2.5:7b | direct | 0.691 | 0.222 | 0.541 | 0.000 | 0.710 | 0.000 | 0.583 | 0.666 | 0.529 |
| qwen2.5:7b | closure | 0.675 | 0.292 | 0.784 | 0.000 | 0.668 | 0.000 | 1.000 | 0.644 | 0.529 |
| qwen2.5:7b | guided | 0.703 | 0.200 | 0.541 | 0.027 | 0.689 | 0.000 | 0.650 | 0.666 | — |

* llama 的 guided 有 63/70 行无法解析出 JSON（只输出散文），按预注册记全错；
这些数字不能与其他行直接比较，它是格式合规失败，不是能力读数。

### 7.2 分项解读

1. 换序效应稳健：两个模型、三个系统下 17%–29% 的已正确字段在纯换序后变错；
   与 H1 的 14.3% 一致。重测基线为 0/294。
2. 缺证 100% 编造：missing 变体的 UNKNOWN 正确率全部为 0.000；
   每个模型在 10 场中共有 22 个应判 UNKNOWN 的字段，全部被填了具体值。
3. closure 的收益有边界：
   - 可闭合修订上 changed acc 0.54/0.62 → 0.78/0.89，闭合率 0.58/0.68 → 1.00；
   - 不可闭合修订（hard）上 direct = closure = 0.529，完全无差异。
4. prompt 规则基本无效：
   - qwen guided 与 direct 持平（0.703 vs 0.691）；
   - llama guided 63/70 行解析失败，格式崩掉。
5. 旧值残留不是主失败模式：
   - revised stale rate 0–2.7%；
   - revision_inline 的旧值率 0.000，两个模型都采纳了后文更正；
   - 说明在“单次、显式更正”场景下版本化不是它们的短板。
6. 干扰抵抗较好：distractor 的 same-pred 比例 0.72–0.98；
   conflict 字段（extras）准确率 0.6–1.0。
7. 严格整场配对为 0/10（32 字段全对不现实）；
   字段级配对 0.64–0.73，建议作为主配对指标。

### 7.3 Oracle 证据诊断

把 commentary 缩减为“仅含被评分字段证据句”的版本：

| model | 全文 control | 仅证据句 | 差值 |
|---|---:|---:|---:|
| llama3.1:8b | 0.738 | 0.659 | −7.8pp |
| qwen2.5:7b | 0.691 | 0.594 | −9.7pp |

去掉非证据句后准确率下降。说明：

- 失败不是“找不到目标句”，长文本检索不是主瓶颈；
- 模型需要上下文完成聚合（总分、边际、伙伴关系），而这些不在“字段证据句”里；
- 方法应针对聚合与状态维护，而不是检索压缩。

注意：该 oracle 过于激进，只作为下界诊断；30 场应做“证据句 + 邻句”的温和版本。

---

## 8. 方法定位：负结果与两条出路

当前 closure 方法只做了一件事：用账目恒等式重算派生字段。
它能消除账目矛盾，但不能发现“文本中的事实变了”。

两条出路：

A. 升级为事件级账本（Versioned Event Ledger）
- 每场 1 次调用抽取事件三元组（entity, stat, value, source）；
- Python 维护 entity→version→value，冲突按权威裁决；
- 只重算依赖图受影响字段。
- 代价：需要再投工程；收益需在 revised_hard 上验证（当前 hard 场景是它的用武之地）。

B. 收窄主张（推荐，风险低）
- 论文写“外部闭合修复能消除账目矛盾，但不能替代抽取”；
- 把事件账本列为 future work；
- 这仍是有效诊断结论，与其余发现一致，适合 Resource/负结果路线。

---

## 9. 论文骨架与投稿建议

工作标题：

> Maintaining a Consistent Table under Revision: A Paired Diagnostic of State Tracking in Small LLMs

四条贡献：

1. 带字段证据、可回答性、闭合约束的配对诊断集（10 场深度物化，220 场源池）。
2. 顺序 vs 重测的可靠性分离（42 vs 0）。
3. 缺证拒答失败模式（UNKNOWN 正确率 0）。
4. 闭合修复的边界（负结果：hard 修订零提升）。

推荐投稿：

- 首选 ACL/EMNLP Resource & Evaluation：8 页，负结果 + 数据 + 可靠性审计匹配度高。
- 备选 LREC：数据卡与许可做好即可。
- 不建议主会正刊：单领域、半合成、只有 2 个 7–9B 模型、方法负结果。

---

## 10. 成本

实际支出：¥0（全部本地推理）。

可选强模型锚点（未执行）：

- 10 场 × 6 变体 × 1 系统 = 60 次调用；
- 估计输入约 0.12M tokens、输出约 0.04M tokens；
- 是否执行取决于你的 V4.1 Flash 预算；即使为 0，论文写“本地 7–9B 面板”仍成立。

220 场全量扩展（未执行，仅估算）：

- 220 × 6 变体 × 4 系统 × 3 模型 ≈ 15,840 次调用；
- 估计输入约 32M tokens、输出约 9.5M tokens；
- 约为 pilot 的 22 倍，不建议在方法有效性未解决前做。

成本纪律：

- 批量一律本地；
- 输出短 JSON；
- 失败不重跑，先查缓存；
- 220 只作源池与最终发布，正文物化 10→30 场。

---

## 11. 风险与限制

1. 半合成数据：事实由场景模板注入，不是真实比赛抽取；DATASET_CARD 已写明。
2. 只有 10 场、2 个 7–9B 模型；gemma2 未跑；结论不外推到前沿模型。
3. 无人工金标：目前是 solver 金标 + 脚本一致性检查，人工可读性审计未做。
4. revised 的 closure 优势部分“按定义正确”；hard 修订已把这块分离。
5. oracle 诊断过于激进（只留证据句），只能作为下界。
6. panel 重跑未完成（qwen 182/320），H2 v2 的完整三模型表待补。
7. 27 场金标缺陷未修复，只登记并排除。
8. 严格整场配对 0/10，说明该指标在 32 字段下无区分度，已改用字段级配对。

---

## 12. 未完成项与下一步

按优先级：

1. 决定 RQ3 走 A（事件账本）还是 B（收窄主张）。
2. 若走 B：把 PILOT_RESULTS 扩写成论文 Results/Discussion，补 2–3 张图。
3. 补 panel_v2 完整 320×3，确认身份修复后 law/count 分裂。
4. 可选：gemma2 跑 pilot（约 30–40 分钟）。
5. 30 场扩展前必须先解决“方法有效性”，否则只是重复负结果。
6. 人工可读性检查：10 场 × 2 人；若无人，则单人 + 脚本检查并在 Limitations 写明。

30 场扩展的门（沿用计划书）：

- 字段证据覆盖 ≥95%；
- 闭合求解器 100% 复现；
- 6+ 变体求解器复现、泄漏 0；
- pilot 出现可分离信号；
- 方法在至少一个明确错误类型上有效。

当前第 5 条不满足（hard 修订零提升），所以不应直接扩 30 场。

---

## 13. 需要你决策

1. RQ3：升级事件账本，还是收窄为“闭合修复边界”的负结果？
2. V4.1 Flash 预算上限：是否跑 60 次强模型锚点（建议 ≤¥50）？
3. 人工标注：10 场可读性与 gold 审计，能否出 2 位标注者？

---

## 14. 文件清单与复现

核心文档：

- PLAN_V2.md：调整后的总方案、成本模型、阶段门
- PILOT_RESULTS.md：完整结果与限制
- PAPER_SKELETON.md：论文骨架（含真实数字）
- DATASET_CARD_DRAFT.md：数据卡草稿
- PILOT_PREREGISTRATION.md、prereg_freeze.json、prereg_amendments.md
- ROUND_REPORT.md、RUN_STATE.md：过程记录

数据与分析：

- pilot10/：10 场样本、selection.json、validation.json、gold_defects.json
- analysis/h1_transitions.json、h1_stats.json
- analysis/closure_audit_220.json、dataset_audit.json
- analysis/pilot10_metrics.json
- runs/eval_pilot10/*.jsonl：原始模型输出
- runs/panel_v2_20261113/：身份修复后的面板（部分）

脚本：

- scripts/h1_transitions.py、h1_stats.py
- scripts/dataset_audit.py、audit_closure_220.py
- scripts/pilot_lib.py、build_one.py、select_and_build.py、validate_pilot10.py
- scripts/eval_pilot10.py、analyze_pilot10.py
- scripts/panel_v2.py、make_defect_registry.py、freeze_prereg.py

复现命令（在仓库根目录，使用 bundled python）：

    python VETT_INTEGRATED_20261113/scripts/select_and_build.py
    python VETT_INTEGRATED_20261113/scripts/validate_pilot10.py
    python VETT_INTEGRATED_20261113/scripts/eval_pilot10.py
    python VETT_INTEGRATED_20261113/scripts/analyze_pilot10.py
    python VETT_INTEGRATED_20261113/scripts/panel_v2.py

---

## 15. 诚实边界声明

- 本报告中的每个数字都来自本会话实际运行的脚本与产物；没有把估计值写成实测值。
- 方法目前是负结果，不应写成“我们的方法提升了状态维护”。
- 数据是半合成的，不能声称“真实比赛抽取”。
- 10 场 pilot 只能支持方法可行性判断，不能支持领域级结论。
- 220 场全量扩展与 30 场复现都还没有做。
- 付费 API 调用次数为 0；DeepSeek V4.1 Flash 的任何费用尚未发生。
