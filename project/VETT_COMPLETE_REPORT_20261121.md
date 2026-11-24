# VETT-Cricket 项目完全报告（总合并版）

**版本**：v1.0  
**生成时间**：2026-11-21 11:06（Asia/Shanghai）  
**覆盖范围**：2026-09-03 至 2026-11-21，VETT-Cricket 全部数据集、实验、测试与运行记录  
**数据快照**：见 6.1，写作时刻从 state/workflow.db 与 reports/STATUS.md 实时读取  
**本地模型**：qwen2.5:7b-instruct-q4_K_M、llama3.1:8b、gemma2:9b（本机 Ollama）  
**外部 API**：0 次（全项目贯穿约束）  
**报告性质**：汇总与复核，不新增任何模型调用；所有数字来自原始报告、runs/*.jsonl 与 workflow.db  
**附录**：A1–A38，本项目阶段报告全文并入

> 阅读提示：本报告把「事实读数」「解释」「未定项」分开写。凡未从原始 runs 复算的数字，均标注来源；跨报告冲突处保留双方口径，不强行合并。

---

## 0. 一页摘要

**总判断**：项目不缺实验量，也不缺执行管线；缺的是冻结的分母与主因变量。截至 2026-11-21，本地推理累计约 1 万次、外部 API 0 次、8 小时无人值守已达成；R28 的「更难」主张被自身数据否掉，DeepTable 证明任务不浅但整表全错，证据干预在单格上很强、到整表就消失，43 字段的人工分母仍是 0/40。

### 0.1 已完成的五件事

1. **220 场语料与审计**：220 场 × 4 文件、98,572 个 cell、448.1 cell/场；闭合审计 218 场可解析，27 场（12.4%）存在至少一项金标缺陷，191 场（87.6%）闭合干净。
2. **R28 诊断集交付**：320 发布 + 40 held-out，一题一记录一证书，确定性 solver 金标，320/320 证书覆盖，双渲染 facts+record 逐字节相同。
3. **DeepTable V1 首轮**：18 场 × 4 条件 × 3 模型 = 216 次；cell_exact 0.272–0.313，整表全对 0/216，closure 违规率约 1.00。
4. **小模型诊断与 attribution**：v1 证明「抽取 6/6 对、最终值 0/6 错」；v7 直接 39/66 vs 按归属 51/66，实际误转移 14；attribution 三连证明修好的完整短证据仍救不回两名投手同时改判（0/18）。
5. **自治工作流**：11-17 验收 10 批，11-19 达 149 批并完成 8 小时无人值守里程碑，11-21 已到 210 批、6,913 条结果，仍在运行。

### 0.2 五个最硬读数

| 读数 | 数值 | 来源 |
|---|---:|---|
| R28 E1 难度差 | 发布 59.56% vs 对照 60.12%，drop 0.557pp，CI [-0.801, +1.846] | R28_DECISION_REPORT |
| R28 解释稳定性 | stability⁰ 0.125（5/40） | 同上 |
| DeepTable 整表 | 0/216 全对；cell_exact 0.272–0.313 | DEEP_T2T/REPORT_V1 |
| 证据摘录 D | E 54/54、M 50/54、O 44/54 | 1115 总报告 |
| 整表 locator | 130/144 → 131/144，仅 +1 格 | 同上 |
| U 全池 | 598/1311 两格同时正确（45.6%） | 同上 |
| 43 字段可答 | 73/258；人工盲审 0/40 | answerability |
| 目标四格 vs 全表 | 89.3% vs 34.1%（A 20 根） | 多维 A |
| 自治工作流 | 210 批、6,913 done、1,061 queued、外部 API 0 | STATUS 10:37 |

### 0.3 四个最大风险

1. **分母未冻结**：43 字段只有 73/258 可答、185 待核、40 格人工 0/40；所有 79/258、73/258、整表百分比都还不能进论文。
2. **主结果未锁定**：现有最强信号是「目标格饱和、整表崩溃」，但尚未写成预注册的主对比。
3. **自治 sweep 的边际价值递减**：210 批里 S/P 覆盖批占大头，均值 0.55/0.50，继续刷主要是在加样本而不是加结论。
4. **发表口径**：主会 Reject；Resource 轨道 Borderline；LREC/负结果 workshop 才有较大接受面，且必须放弃「更难」话术。

---

## 1. 目标与定位

### 1.1 三层目标

| 层 | 目标 | 现状 |
|---|---|---|
| 资产层 | 220 场长文语料 + R28 诊断集 + 长文整表任务 | 已交付，可复现 |
| 科学层 | 定位 7–9B 小模型在「长文 → 整表」上的失败环节，并验证可迁移的干预 | 已定位到状态更新/字段绑定；干预未冻结 |
| 发表层 | ACL/EMNLP Resource & Evaluation；退路 LREC 或负结果 workshop | 未达投稿状态；审稿人判主会 Reject |

### 1.2 审稿人判决（2026-11-13）

审稿人结论：**「你不缺数据，也不缺工程量；你缺一个正确的因变量。」** 原始输出里已经有一个比「难度不成立」更好的结果：这个 7B 模型「会判规则、不会算账」，但主指标把两件事平均成了 59.56%，于是所有呈现侧操纵都显得没用。

| 定位 | 现稿 | 按 P0 修完（约 2 周、¥0） |
|---|---|---|
| 主会（ACL/NeurIPS/ICLR 正刊） | Reject | 仍 Reject（这是另一篇 R29） |
| NeurIPS D&B / ACL Resource | Weak Reject | Borderline，有机会 |
| LREC / 诊断与负结果 workshop | Borderline | 接受面较大 |

按维度：Novelty 2/5、方法 Soundness 3.5/5、主张 Soundness 2/5、Data quality 2.5/5、Reproducibility 5/5、Clarity/positioning 2/5。

### 1.3 硬约束（全程未破）

- 零付费 API、零外网；所有推理走本机 127.0.0.1:11434 的 Ollama。
- 不改 220 场源池、原记分表、R26.15 任何字节；不读 private/。
- 保留根 0121–0160 冻结，不用于方法开发。
- 新增内容放独立目录，交付可回滚补丁与报告。

---

## 2. 资产底座

### 2.1 220 场语料

| 项 | 值 |
|---|---:|
| 场数 | 220 |
| 每场文件 | 4：commentary.txt、scorecard.md、evidence_chain.md、meta.json |
| 表格 cell 总数 | 98,572 |
| 每场平均 cell | 448.1 |
| batting / partnership / bowling / FOW / summary | 33,908 / 24,563 / 20,992 / 9,837 / 9,260 |
| 证据层级 L1 / L2 / L3 | 32.1% / 40.9% / 27.0% |
| 文本均值（解说/记分卡/证据） | 6.4 / 5.2 / 2.5 KB |

读法：68% 的证据目标在 L2/L3（闭合/综合），浅的是以往任务只问 L1 直取；深度不需要新造数据，只需要把评分对象移到 L2/L3 的 cell 上。

### 2.2 R28 数据集

| 项 | 值 |
|---|---|
| 版本 | VETT-Cricket-v0.37-R28-diagnostic-pair-20261112 |
| 规模 | 发布 320 + held-out 40 = 360 |
| 题块 | DL 216 + FC 144 |
| 机制 | D1 alias_hops / D2 temporal_joins / D3 scope_decisions / D4 isomorphic_distractors，各 54 题（剂量 0/1/2 各 18） |
| 记录 | 12 字段 decision_record_flat |
| 金标 | 确定性 solver vett_r25.solver，无语言模型参与事实、金标或证书 |
| 证书 | 320/320 覆盖；564 条非承载算子登记为 presentation_only |
| 双渲染 | 发布版与对照版 facts+record 320/320 逐字节相同 |
| 记录空间 | 可达互异记录 4001；实际 320/320 互异 |
| 结构天花板 | 合法 dismissal ≤ 11（DEAD_REBALL 1、BOWLED/LBW/CAUGHT 各 2、STUMPED 4） |
| 分布 | status：LEGAL 166 / NO_BALL 100 / WIDE 53 / DEAD_REBALL 1 |

限制必须同时说出：solver 是单球规则查表器，不是多跳推理机；金标未经人工双标；族名是中性哈希，不是泄漏轴。

### 2.3 43 字段与 79/258 口径

- 43 字段整表含两局，共 129 格（单模型）；目标子集是 4 格（每局 total_runs/total_wickets）。
- 可答性复核：**73/258**（69 直接 + 4 可推导），**185 待人工核验**。
- 同分母 73 格：Qwen 29/73（39.7%）、Gemma 32/73（43.8%）、Llama 26/73（35.6%）。
- 全字段：Qwen 73/258、Gemma 85/258、Llama 63/258。
- 历史启发式口径 **79/258**（Qwen 33、Gemma 38、Llama 30）保留不变；40 格人工复核仍为 **0/40**。
- 注意：73/258 是「可答」，79/258 是「历史启发式答对」，两者不是同一分母，报告不得混用。

### 2.4 数据质量：闭合审计

对 218 场可解析比赛执行 6 类闭合约束：

| 缺陷 | 场次 |
|---|---:|
| bowling_recon（投手失分 ≠ 总分−byes−legbyes） | 19 |
| bat_plus_extras（击球和+extras ≠ 总分） | 8 |
| wicket_sum（投手 wicket+run-out ≠ 总 wicket） | 7 |
| fow_monotone | 1 |
| 至少一项缺陷 | **27 / 218 = 12.4%** |
| 完全闭合 | **191 / 218 = 87.6%** |

另有 2 场不可解析：match_0004（两局制 innings and 32 runs）、match_0066（Abandoned，仅 1 局）。结论：发布前必须给 27 场打 gold_defect 标记或修复；pilot 只用 191 场干净样本。

---

## 3. 实验总表

| 阶段 | 时间 | 规模 | 关键读数 | 状态 |
|---|---|---|---:|---|
| R28 裁决 E1–E4 | 11-12 | 320+40；E1 n=319 | drop 0.557pp；stability 0.125 | 完成，harder 不成立 |
| Pilot10 | 11-13 | 10 场×6 变体×3 模型，约 700 次 | 换序对→错 17–29%；缺证 UNKNOWN 正确率 0 | 完成 |
| 闭合审计 | 11-13 | 218 场 | 27/218 缺陷；191 干净 | 完成 |
| DeepTable V1 | 11-13 | 216 次 | cell 0.272–0.313；整表 0/216；C2 作废 | 首轮完成 |
| 小模型诊断 v1–v7 | 11-13 | 6→264 次 | 抽取 6/6 vs 最终值 0/6；v7 39/42/51 of 66 | 完成，开发候选 |
| Attribution 三连 | 11-13 | 120+120+54 次 | 推导 0/24；短证据 15/24；修好短证据 0/18 | 完成 |
| 输入审计 | 11-13 | 54/54 哈希核对 | B/C 实为全文+标记；4/6 终局句错局 | 完成，旧结论作废 |
| D/D+ 位置与干扰 | 11-14/15 | 186 + 1476 次 | O44/M50/E54；D+ 净 −3/−3/−1 | 完成 |
| T locator | 11-14/15 | 12 根 144 格 | 130→131，仅 +1 | 完成，无方法收益 |
| U 全池 + 抽样 | 11-15 | 1311 + 432 次 | 598/1311；抽样 181/432 | 完成 |
| 多维 A/B | 11-16 | 60 + 111 行 | 目标 89.3% vs 全表 34.1%；B 110/111 | 完成 |
| 自治工作流 | 11-17→11-21 | 210 批、6,913 结果 | S 0.554、P 0.503、全表 26.8/23.6/13.0/10.8% | 运行中 |

---

## 4. 分阶段详述

### 4.1 R28：难度与解释性裁决（2026-11-12）

**设计与规模**：320 发布 + 40 held-out；E1 配对 n=319；E2 剂量-反应；E3 机制归因；E4 三孪生稳定性。

| 问题 | 判决 | 决定性读数 |
|---|---|---|
| Q1 更难了吗 | 不成立 | E1 发布 59.56% vs 对照 60.12%，drop 0.557pp，CI [-0.801, +1.846]；整记录 exact 5/638 = 0.78% |
| Q2 更有解释性吗 | 机械可验证成立；解释忠实度不成立 | 证书 320/320、solver 重推 100%；E4 stability⁰=0.125 → EXPLANATION_CLAIM_NOT_ESTABLISHED |
| Q3 更能发表吗 | 作「能力基准」不可发表 | 四条限定全 FAIL；只能作测量/零结果/验证装置论文 |

- **E2 剂量-反应 REJECTED**：dose 0/1/2 准确率 59.375% / 62.674% / 60.938%，斜率 +0.781pp/step（方向相反），CI [-1.815, +3.402]，单调性 False。
- **E3 机制归因 H3=False**：Holm 校正后无主效应；D4 名义 p=0.041 → Holm 后 0.166；交互模型 NOT_ESTIMABLE_WITH_16x8。
- **E4 三孪生全 FAIL**：stability⁰ 0.125（5/40）、stability⁻ 0.500（16/32）、flip⁺ 0.525（21/40）（低于随机地板 0.875）。
- **非承载规则**：1,546 条渲染规则引用中 488 条（31.6%）从未承载推导；BAT_CREDIT 118、NB_COUNT 100、WIDE_COUNT 53 从未必要；360/360 题至少含一个非承载算子。

**最硬解释**：0.557pp 不是「数据没变难」，而是模型压根没在解题——只打乱文档顺序，87.5% 的答案就变了。在模型不读证据的前提下，任何呈现侧操纵都必然无效。

**决定**：DIRECTION_ONLY + DEGRADED；harder_claim_permitted = False。

### 4.2 Pilot10 与闭合审计（2026-11-13）

**Pilot10**：10 场（0090/0167/0203/0035/0159/0007/0092/0108/0182/0091），49 个可评分字段，6 套变体（control/shuffled/revised/conflict/missing/distractor），validation all_ok=true；约 700 次本地调用（qwen/llama × direct/closure/guided × 8 变体 + oracle）。

三个核心发现：

1. 换序「对→错」17–29%，重测 0/294 波动。
2. 缺证 UNKNOWN 正确率 0（100% 编造）。
3. closure 只修账不补抽取：hard 修订 0.529 = 0.529；oracle 证据反而更差 → 瓶颈在聚合/状态维护。

**关键设计修正**：原始 commentary 是 smart_expand 产物，不能复现，因此 RQ2 用确定性 control 渲染作基准（同 md、同 seed），六变体全部由它派生；原始 commentary 只服务 RQ1。

**闭合审计**：见 2.4；27 场缺陷是发布前必须处理的 Data Quality 事实。

### 4.3 DeepTable V1（2026-11-13）

**任务**：把整场表从抄写改造成约束满足；输入约 19.3KB 卷宗（解说 + 事件级修订 + 版本化规则 + 干扰文档），输出 76 个必须推导的 cell。

**规模**：18 场（0004、0011 因 innings 数不等于 2 跳过）× 4 条件 × 3 模型 = 216 次；T=0、seed=20261112、num_ctx=8192、num_predict=900；墙钟约 95 分钟；¥0。

| 模型 | 条件 | n | cell_exact | table_exact | closure 违规率 |
|---|---|---:|---:|---:|---:|
| gemma2:9b | C0 | 18 | 0.2788 | 0.00 | 1.00 |
| gemma2:9b | C1 | 18 | 0.2986 | 0.00 | 1.00 |
| gemma2:9b | C2 | 18 | 0.2905 | 0.00 | 1.00 |
| gemma2:9b | C3 | 18 | 0.2920 | 0.00 | 1.00 |
| llama3.1:8b | C0 | 18 | 0.3125 | 0.00 | 1.00 |
| llama3.1:8b | C1 | 18 | 0.3067 | 0.00 | 1.00 |
| llama3.1:8b | C2 | 18 | 0.3067 | 0.00 | 1.00 |
| llama3.1:8b | C3 | 18 | 0.2847 | 0.00 | 1.00 |
| qwen2.5:7b | C0 | 18 | 0.2722 | 0.00 | 1.00 |
| qwen2.5:7b | C1 | 18 | 0.2340 | 0.00 | 1.00 |
| qwen2.5:7b | C2 | 18 | 0.2458 | 0.00 | 0.94 |
| qwen2.5:7b | C3 | 18 | 0.2465 | 0.00 | 1.00 |

- **整表全对 0/216**；最好单场 0.526（gemma2 / match_0001 / C0）。
- **copy_rate 0.69–0.76**：约七成数值预测能在原文找到出处，但只有约 27% 落在正确 cell——模型大量「从文中抄错数」。
- **C1 修订跟随不成立**：145 个修订 cell 上正确率 0.145–0.193，低于各自整体 0.234–0.307。
- **C2 规则版本冲突失效**：金标变化 0/1368，等于加了一份无关文档；G4 用「金标变化率」是口径错误，C2 必须重建。
- **C3 证据必要性**：72 个变化 cell，正确率 0.19–0.31，全表翻转 26–35%，更像采样噪声。

**预注册门**：G1 PASS（C0 最高 0.3125）、G2 PASS（table 0、closure 1.00）、G3 未触发（json_ok 1.000）、G4 FAIL→重做 C2。

**结论**：任务不浅、失败面是闭合推导；C2 作废；修订跟随不成立。

### 4.4 小模型诊断 v1–v7（2026-11-13）

这是一条「同一事件、只改通知」的改判更新任务线：原记 A，改判 B，A 的 wickets −1、B +1，runs 与全队 total 不变。

| 版本 | 规模 | 关键读数 |
|---|---|---|
| v1 | 6 次新增 | 同一短证据：直接最终值 two 0/6；纯抽取 6/6 全对；Python 更新 6/6 |
| v2 | 18 次 | 两场新比赛：直接 4/6 vs 抽取+程序 6/6；维持无错误更新，4/6 无法执行 |
| v7 | 264/264 次，22 场 | 直接 39/66、严格 42/66、按归属 51/66；实际误转移 14 |

**v1 的核心发现**：模型知道事件（出局者、原/新投手、方向、两个旧 wicket 全对），但不会把 −1/+1 落到最终答案。错误在「最终值更新」，不是读旧数、认人或弄反方向。

**v7 的取舍**：

| 方法 | 正式 | 维持 | 联合 |
|---|---:|---:|---:|
| 直接 | 42/66 | 63/66 | 39/66 |
| v5 严格标签 | 65/66 | 42/66 | 42/66 |
| v5 按归属 | 65/66 | 51/66 | 51/66 |

- 直接→按归属：错→对 24、对→错 12、对→对 27、错→错 3。
- 严格规则拦住 Qwen 12 条误转移，但损失 9 条本可正确交付；按归属放行 14 条错误转移，换来 Llama 15 条联合提升；两者都没有净收益。
- Qwen 12/22 把「维持」读成「改判」：decision=reassign、原归属 A、最终归属 B，结构自洽但与通知相反。
- 旧值方向：高 22 场，低 0 场；低旧值方向仍是缺口。

### 4.5 Attribution 三连与输入审计（2026-11-13）

| 目录 | 规模 | 结论 |
|---|---:|---|
| attribution_followup | 120 次，8 场 | 全文推导三项全对 0/24；短证据 15/24（Qwen 7/8、Gemma 7/8、Llama 1/8）；程序更新无收益 |
| attribution_evidence_followup | 120 次，开发 8 + 留出 6 | 只标原句（B）无帮助：B−A 两名投手全为 0；C 的总出局略好但缺 pre-revision Note，不能作严格结论 |
| attribution_update_and_full_table | 54 + 6 + 6 次 | 修好的完整短证据 B 的 two_wickets 0/18，A 也 0/18，B−A=0；Python 更新 0 修对、0 改坏、1 无法执行 |

**输入审计（决定性更正）**：54/54 条请求的提示哈希与重建一致；但 **B、C 实际收到的是「全文 + 六个 [EVIDENCE] 标记」，不是六句短证据**；C 与 B 正文完全相同，只多分步要求。终局证据 **4/6 场属于错误局或非终局**（0009 用第一局 96/5、0013 用非终局措辞、0014 用第一局 212/7、0016 用第一局 34/3）。因此旧 0/18 是「标注全文 + 部分错误终局」的结果，不能当作短证据结论。

**错法**：最常见是「两人都旧值」（gemma 6/6–7/8、qwen 6/6），其次只加新投手、两人都改但值错；程序没有正确输入可更新。

### 4.6 位置、干扰、整表与全池证据（11-14/15）

**D：证据位置对照（18 根）**

| 条件 | 正确 | 配对变化 |
|---|---:|---|
| O 原文 | 44/54 | — |
| M 移位 | 50/54 | O→M 救回 8、改坏 2，净 +6 |
| E 摘录 | 54/54 | O→E 救回 10、改坏 0 |

扩展 12 根：O 28/36、M 35/36、E 36/36；O→M 净 +7、O→E 净 +8。合并 18 根即上表。

**D+：三个单项干扰（配对同根同模型）**

| 变体 | 配对数 | O | 变体 | 救回 | 改坏 | 净 |
|---|---:|---:|---:|---:|---:|---:|
| 移除局中竞争比分 | 54 | 44 | 41 | 0 | 3 | −3 |
| 第二个证据落点 | 45 | 37 | 34 | 1 | 4 | −3 |
| 移除另一局比分 | 30 | 28 | 27 | 0 | 1 | −1 |

三个变体配对后均净负；绝对数不能直接比较干预优劣。

**T：整表 locator**

| 批次 | 基线 | locator | 变化 |
|---|---:|---:|---:|
| 0100/0111/0120/0130/0140/0160 | 68/72 | 68/72 | 0 |
| 0183–0188 | 62/72 | 63/72 | +1 |
| 合计 | 130/144 | 131/144 | +1 |

唯一变化：match_0186、Qwen、inn2.total_wickets：基线 2、locator 1、金标 1。结论：当前 locator 不足以形成整表方法收益；全 43 格未评分。

**U：全池证据审计**

| 模型 | 两格正确 | total_runs | total_wickets | JSON 成功 |
|---|---:|---:|---:|---:|
| Qwen | 175/437 | 214 | 211 | 430/437 |
| Llama | 208/437 | 230 | 240 | 437/437 |
| Gemma | 215/437 | 221 | 248 | 437/437 |
| 合计 | **598/1311** | 665/1311 | 699/1311 | 1304/1311 |

覆盖 437 局位、219 根；缺 match_0004 两局、match_0066 第二局。错误形态：局中比分、另一局比分、字段对调、只答对一个字段。**有引文不等于终局语义正确。**

**U 抽样 1–5**：432 次、144 局位，两格 181/432；Qwen 43/120、Llama 68/120、Gemma 70/120；旧「只对 wickets」组 108 条只恢复 8 条 → 问题在 runs 定位或字段绑定，不是 JSON 格式。第六批 35/72 未完成。

**位置传输试点**：5 场 45 次，O 13/15、M 13/15、E 15/15；所有变化集中在 match_0087，只涉及 1 个独立根；未达「两个独立根」阈值，整表回投未运行。

**本地证据长跑**：60 次；8 场证据（每模型 4/8）+ 4 场 A/B/C（A 6/12、B 9/12、C 5/12，C 引用有效 10/12）。B 比 A 多 3、无对→错；C 比 A 少 1、无错→对。新增 16 个发布版同格链接。

**220 与 R28 两场联动**：36 次新请求 + 6 个整表锚点复用；A 无通知 3/6、维持 3/6、改判 0/6；B 1/6、0/6、1/6；联合按交集为 0/6（此前的 3/6 是条件计数误当交集）。发布版缺精确事件/旧汇总，R28 用 scorecard 重渲染，不能写成发布版长文错误。

### 4.7 多维 A/B（2026-11-16）

**A：43 字段整表开发批**

| 批次 | 根 | 行 | 目标四格 | 全 43 格 |
|---|---:|---:|---:|---:|
| dev1 | 8 | 24 | 84/90 | 272/792 |
| dev2 | 8 | 24 | 84/96 | 300/840 |
| dev3 | 4 | 12 | 41/48 | 127/420 |
| 合计 | 20 | 60 | **209/234（89.3%）** | **699/2052（34.1%）** |

目标四格接近 90%，不能用来证明整表方法；全 43 格只有 34.1%，主要损失在非目标字段。runner 的 fields=None 仍导致 parse_ok 误报，按顶层键评分。

**B：证据与干扰最小批**

37 个条件-根组 × 3 模型 = 111 行，0 失败，两格 110/111。

| 条件 | 正确 |
|---|---:|
| O 原文 | 15/15 |
| P 前移 | 11/12 |
| L 后移 | 15/15 |
| E 摘录 | 15/15 |
| WI 删同局局中比分 | 15/15 |
| WIC 等长无关删除 | 15/15 |
| OI 删另一局比分 | 12/12 |
| OIC 等长无关删除 | 12/12 |

删除类条件在这 8 根上没有退步 → 这些根对干扰不敏感，B 需要更多难根或更强干扰。

### 4.8 自治工作流（2026-11-17 → 2026-11-21，仍在运行）

**架构**：vettctl / supervisor / worker / planner / scorer / reporting / vettlib + SQLite workflow.db；唯一 GPU worker，一次一个请求；task_key = sha256(match | innings | model | cond | field_scope | prompt_sha)；BEGIN IMMEDIATE + 条件更新领取；worker 死亡或心跳超 30 秒（后改 150 秒）自动退回 queued；结果已落盘则 recovered_with_existing_result。

**11-17 验收**：10 批（B001–B010）、54 请求、57 任务、11 条决策、14 根、0 外部 API；12 项验收全 PASS，包括模拟 worker 被杀后恢复、关终端后继续落盘、stop 同时停派发与重启。

| 批次 | 模板 | 根 | 条件 | 请求 | 格正确 | 准确率 |
|---|---|---|---|---:|---:|---:|
| B001 | T1 基线 | 0066, 0085 | O | 6 | 12/12 | 1.0000 |
| B002 | T2 困难摘录 | 0002, 0003 | E | 6 | 10/12 | 0.8333 |
| B003 | T3 配对删除 | 0002 | O/WI/OI | 9 | 3/18 | 0.1667 |
| B004 | T4 整表 | 0002 | O | 3 | 25/129 | 0.1938 |
| B005 | T2 困难摘录 | 0008 | E | 3 | 5/6 | 0.8333 |
| B006 | T3 配对删除 | 0008 | O | 3 | 0/6 | 0.0000 |
| B007 | T5 困难全文 | 0009, 0010 | O | 6 | 0/12 | 0.0000 |
| B008 | T1 基线扩展 | 0087, 0096 | O | 6 | 11/12 | 0.9167 |
| B009 | T5 困难全文 | 0011, 0013 | O | 6 | 0/12 | 0.0000 |
| B010 | T1 基线扩展 | 0165, 0021 | O | 6 | 12/12 | 1.0000 |
| B011 | T5 困难全文 | 0015 | O | 3 | 0/6 | 0.0000 |

**11-18 14:50 → 11-19 09:10 连续段**：149 批、3,502 结果、3,453 attempts、0 外部 API；8 小时里程碑 11-19 08:24:45 达成（新段 00:24:45–08:24:45，9 份小时报、08:00 阶段报告 17,480 字节）；主机 09:10 重启终止，全程 8h44m，非代码异常。

| 模板 | 批数 | 平均准确率 |
|---|---:|---:|
| S_coverage_sweep | 88 | 0.554 |
| P_field_sweep | 43 | 0.503 |
| T1_baseline_o | 4 | 0.9375 |
| T5_hard_fulltext | 3 | 0.0 |
| T3_matched_deletion | 3 | 0.1296 |
| T2_hard_excerpt | 2 | 0.8333 |
| C_adjudication | 2 | 0.95 |
| T4_full_table | 1 | 0.1938 |
| B_cross_innings | 1 | 0.0 |
| B2_matched_control | 1 | 0.0 |
| A_field_probe | 1 | 0.9167 |

**11-20 → 11-21 新增**：

| 批次 | 模板 | 结果 |
|---|---|---|
| B198 | T4_full_table_scale | 2072/7740 = 26.8% |
| B199 | T4_full_table_scale2 | 1825/7740 = 23.6% |
| B200 | T4_full_table_O_scale | 338/2603 = 13.0% |
| B207 | T4_full_table_E_used | 381/3526 = 10.8% |
| B209 | B_cross_innings_scale | 0.5862（87 任务） |
| B210 | P_E_probe | 运行中（68 unit，E 条件） |

**事故**：

| 时间 | 事件 | 影响 | 处理 |
|---|---|---|---|
| 11-18 19:13 | 主机休眠 + Ollama 停止 | 旧段 4h23m，8h 未达 | keep-awake（SetThreadExecutionState）+ Ollama watchdog；00:24:45 重启新段 |
| 11-19 09:10 | 主机重启 | 8h44m 处终止 | state 改 stopped，stop_reason=host_reboot_20261119_0910，可 resume |
| 11-20 17:35 | Ollama 连接拒绝 | 1,063 任务 failed | 全部重新入队；worker 对 transient 错误重试 5 次、间隔 15 秒 |

B201–B206 在 STATUS 中标 failed，即 11-20 Ollama 中断那一段；B207 起恢复并有结果。

**当前实时状态**（写作时刻 11:06 读取，可能已继续前进）：

    # VETT workflow status
    
    - time: 2026-11-21T10:37:08+08:00
    - workflow state: running
    - batch state: running
    - task state: {"claimed": 1, "done": 6913, "failed": 8, "queued": 1061}
    - schema: 2; planning: rule_template
    - external API calls: 0
    - supervisor: 13076 alive=True
    - worker: 2724 alive=True heartbeat=26.5s restarts=28
    - queue: {"claimed": 1, "done": 6913, "failed": 8, "queued": 1061}
    

- 当前连续段约 1.9 小时；累计结果与 attempts 跨重启保留。
- 8 小时里程碑已达成，但 48 小时目标未达成：48h 按 5.2 秒/请求约需 33,200 条不同请求；当前合法 sweep 只有约 7,560 个任务位，估算 10–18 小时，见附录 A33。
- 人工复核：40 格盲审 0/40；自治线 7 条 records 仍 pending_human_review；证据索引 96 条、人工确认 0。
- planning 仍是 rule_template，不是模型驱动假设生成。

---

## 5. 横向结论与反例

### 5.1 强结论（多批复现，可写进论文）

1. **证据呈现是强信号，但不迁移到整表**：E 摘录 54/54、M 移位 50/54 vs O 44/54；B 短证据在构造任务上 15/24 vs 0/24；可 T locator 只有 +1 格。
2. **小模型瓶颈是状态更新/字段绑定，不是检索**：v1 抽取 6/6 而最终值 0/6；v7 14 次误转移、Qwen 12/22 把维持读成改判；U 598/1311 两格全对，引文有效但终局错。
3. **目标格与整表有稳定落差**：B004 目标四格 7/12、全表 25/129；A 20 根 89.3% vs 34.1%；B198 26.8%。三处独立复现。
4. **简单删除/移动不是稳定干预**：D+ 三变体配对净 −3/−3/−1；等长非证据删除（B021）也全错，把 B003 的 OI +3 打成未定。
5. **数据质量是发布阻断项**：27/218 金标缺陷；43 字段 185 格待核；40 格人工 0/40。

### 5.2 中等结论（方向一致，样本有限）

1. 8 小时无人值守可达成；但需要 keep-awake + Ollama watchdog，且主机重启仍需外部自启动。
2. 8–18 根难根上，E 摘录接近饱和；T5 困难全文 0% 有可能是真缺证，也可能是否定证据，需逐任务分类。
3. 多维 B 的 8 根对删除不敏感；需要更多难根/更强干扰才能检验干扰假说。
4. R28 的严格规则与按归属规则各有代价，尚无净收益方案。

### 5.3 未定或被推翻（必须与结果同时出现）

1. **D+ 的删除/移动效应**：全部净负，不能写成「移除干扰有用」。
2. **B003 的 OI +3**：被 B021 等长对照推翻为未定；B020 的 OI 0.0833 与 B003 方向相反。
3. **旧短证据 0/18**：输入审计证明 B/C 不是短证据且 4/6 终局句错局，旧结论作废。
4. **DeepTable C2**：金标 0/1368，当前不能作为版本敏感性证据。
5. **R28 「更难」**：不成立；**「解释忠实」**：不成立。
6. **0087 的位置收益**：只在 1 个独立根，不能当方法。

### 5.4 科学更正清单（按发生顺序）

| # | 原结论 | 更正 | 依据 |
|---|---|---|---|
| 1 | A 联合 3/6 | 按同模型同比赛交集为 0/6 | 本地证据长跑复算 |
| 2 | B/C 是六句短证据 | 实为全文 + 6 个 [EVIDENCE] 标记；4/6 终局句错局 | 输入审计 54/54 哈希 |
| 3 | B009 0% 是缺证 | 加入英文数字词后 6/6 有明确总分句，0% 是模型错 | SCIENCE_CORRECTIONS |
| 4 | B003 OI +3 是跨局干扰收益 | 等长非证据删除也全错，效应未定 | B021 |
| 5 | DeepTable G4 看金标变化 | C2 设计不改变金标，判据口径错误 | REPORT_V1 §3 |
| 6 | R28 更难 | drop 0.557pp，CI 跨 0 | R28_DECISION_REPORT |
| 7 | v7 method parse_ok=0/8 | runner 用 fields 键误判，doc 实际 8/8 可解析但抽取值错 | attribution_evidence_followup |
| 8 | U 解析 1311/1311 | JSON 成功 1304，Qwen 7 条格式失败 | 1115 总报告 |

---

## 6. 当前状态（2026-11-21 11:06）

### 6.1 实时快照

见 4.8 的实时块：workflow state running、batch running、supervisor/worker alive、外部 API 0、当前批次 B210 P_E_probe、队列 1,061 queued、8 failed、18 uncertain。

### 6.2 运行账本（分阶段）

| 阶段 | 本地请求 | 结果/读数 | 失败 |
|---|---:|---|---:|
| 11-12 前 R20–R26 | 未在本次汇总内逐条复算 | 资产与谱系 | — |
| Pilot10 | 约 700 | 8 变体 × 2 模型 + oracle | 0 |
| DeepTable V1 | 216 | 18 场 × 4 条件 × 3 模型 | 0 |
| 诊断 v1–v7 | 约 300 | 6 → 264 | 0 |
| Attribution 三连 | 294 | 120 + 120 + 54 | 0 |
| 夜间 D/T/U + 抽样 | 1,662 + 432 | U 全池 1311；D+ 129；T 36 | 0 |
| 多维 A/B | 171 | A 60 + B 111 | 0 |
| 自治工作流 | 6,913 结果 / 7,949 attempts | 210 批 | 8 failed / 18 uncertain |

说明：各阶段存在复用与重叠（同一批原始输出被多份报告复算），因此上表相加不是去重总数；全项目规模约 9,000–11,000 次本地推理，外部 API 全程 0。

### 6.3 8 小时与 48 小时

- **8h**：2026-11-19 08:24:45 达成（新段 00:24:45 起），9 份小时报、08:00 阶段报告，推理未停。
- **48h**：未达成；合法任务池约 7,560 个任务位（S 最多 4,320 + P 3,240），按 425–591 结果/小时估算 10–18 小时；不重复确定性调用、不硬凑。
- **exactly-once**：不宣称；只宣称「结果持久化一次，尝试可能多次」。

---

## 7. 未完成、风险与边界

### 7.1 未完成清单

| 项 | 现状 | 影响 |
|---|---|---|
| 40 格人工复核 | 0/40 | 43 字段分母不能冻结 |
| 185 格可答性 | 待核 | 73/258 仍是启发式 |
| 7 条 records 人工确认 | pending | 证据索引不能升级为金标 |
| 48h 有效队列 | 10–18h | 对外只能写 8h |
| 主机重启自恢复 | 未做 | 需 Windows 计划任务/服务 |
| planning 模型化 | 未做 | 仍是 rule_template |
| R28 低旧值方向 | 0 场 | 分层结论只覆盖高方向 |
| C 缺证矩阵 | 未跑 | 缺证与模型错仍可能混淆 |
| D R28 低旧值 | 未跑 | 同上 |
| E 温度/seed 复现 | 未跑 | 确定性只有单点证据 |
| F held-out 40 根整表 | 未跑 | 泛化性未验证 |
| T 全 43 格退步评分 | 未评 | 不能写「整表无退步」 |

### 7.2 风险

1. **分母漂移**：73/258、79/258、129 格、43 格、4 格目标混用会直接毁掉论文数字纪律。
2. **sweep 替代科学**：210 批里大量覆盖率批，边际信息低；继续跑主要是消耗 GPU。
3. **单根效应被过度解释**：0087、B003、B020 都出现过单根/单批方向反转。
4. **过程产物膨胀**：hourly/snapshot/blind review 已有上百份，检索成本高；本报告只并入阶段报告，过程快照按目录索引。
5. **发表定位**：不放弃「更难」话术就会继续被审稿人否掉。

---

## 8. 下一步建议（预注册式）

### P0：冻结分母（1–2 天，0 推理）

1. 完成 40 格人工复核，给出 73/258 的确认版与 95% 区间。
2. 对 185 格逐条标「可答/不可答/文本未核实」，不可答格从分母剔除并留痕。
3. 把 79/258 历史口径与 73/258 新口径并列写进数据卡，不再混用。

**门**：人工复核 ≥ 40 格且一致率可报告；否则论文只写启发式分母并明确限制。

### P1：把主结果换成「目标格 vs 全表」（2–3 天，0 新推理）

用已跑的 B004、A-dev、B198–B200 做同一张表：

| 口径 | 目标四格 | 全 43 格 |
|---|---:|---:|
| B004（1 根） | 7/12 = 58.3% | 25/129 = 19.4% |
| A-dev（20 根） | 209/234 = 89.3% | 699/2052 = 34.1% |
| B198（scale） | — | 2072/7740 = 26.8% |

主主张改为：**长文整表任务的失败集中在非目标字段与状态更新，目标格饱和会系统性高估模型能力。**

### P2：只保留一个干预（3–5 天，约 100–200 次）

冻结「证据窗口 + 字段名消歧」，在 6–8 个未调试新根上验：

- O→E 至少 2 个独立根净正；
- T 目标格净正；
- 其他已确认有证据的格不退步；
- 证据语义人工复核通过。

**任一不满足即不冻结为方法。**

### P3：论文口径（与 P0–P2 并行）

- 定位：LREC / 诊断与负结果 workshop 优先；Resource 轨道作为冲刺目标。
- 主张：小模型「会判规则、不会算账/更新状态」，不写「更难」。
- 必须披露：单模型面板、半合成、无人工金标（P0 前）、solver 为单球查表器。

---

## 9. 复现与文件索引

### 9.1 复现命令（节选）

    # 夜间 D/T/U
    cd VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114
    python u_full.py
    python dplus_remove.py
    python dplus_end.py
    python dplus_other.py
    python t_expand.py
    python t_expand_locator.py
    python score_u_full.py
    python score_dplus.py
    python score_t_expand.py

    # 自治工作流
    cd VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117
    python vettctl.py start
    python vettctl.py status
    python vettctl.py stop
    python vettctl.py snapshot
    python vettctl.py report

### 9.2 目录地图

| 目录 | 内容 |
|---|---|
| Self-cricket-clean_text_scorecard_v1_220_matches/ | 220 场源语料（4 文件/场） |
| VETT_R28_DIFFICULTY_20261112/ | R28 数据集、预注册、裁决报告 |
| VETT_INTEGRATED_20261113/ | 综合报告、pilot、prereg amendments |
| VETT_INTEGRATED_20261113/analysis/ | 21 个实验目录（见附录索引） |
| VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/ | 自治工作流、workflow.db、210 批结果 |
| DEEP_T2T/ | DeepTable V1 计划/分析/报告 |
| REVIEW_20261113/ | 审稿人判决与 P0 路线 |
| VETT_V2_MEASUREMENT_20261112/ | 早期 V2 测量 |
| VETT_Cricket_v0.22_R16_Multisource_Dilemmas/ | R16 多源困境集 |

### 9.3 附录索引

| 编号 | 标题 | 原文件 | 行数 |
|---|---|---|---:|
| A1 | 项目综合报告（2026-11-13） | VETT_COMPREHENSIVE_REPORT_20261113.md | 267 |
| A2 | 审稿人判决与最低成本提升路线 | REVIEW_20261113/REVIEWER_JUDGMENT_AND_PLAN.md | 321 |
| A3 | R28 决策报告 | VETT_R28_DIFFICULTY_20261112/R28_DECISION_REPORT.md | ? |
| A4 | R28 新实验独立审计 | VETT_R28_NEW_EXPERIMENTS_INDEPENDENT_AUDIT_20261113.md | ? |
| A5 | DeepTable V1 计划 | DEEP_T2T/PLAN_V1.md | ? |
| A6 | DeepTable V1 首轮分析 | DEEP_T2T/ANALYSIS_V1.md | 123 |
| A7 | DeepTable V1 首轮报告 | DEEP_T2T/REPORT_V1.md | 231 |
| A8 | 2026-11-15 实验总报告 | VETT_INTEGRATED_20261113/analysis/VETT_REPORT_20261115_FINAL.md | 190 |
| A9 | 2026-11-15 夜间合并报告 | VETT_INTEGRATED_20261113/analysis/VETT_OVERNIGHT_CONSOLIDATED_REPORT_20261115.md | ? |
| A10 | 夜间首轮 D/T 最终报告 | VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114/REPORT_FINAL.md | ? |
| A11 | 220 场与 R28 两场联动试点 | VETT_INTEGRATED_20261113/analysis/vett_220_r28_link_pilot/REPORT.md | 77 |
| A12 | 本地证据核对与长文联动 | VETT_INTEGRATED_20261113/analysis/vett_local_evidence_long_run/REPORT.md | 78 |
| A13 | 证据位置对照与整表回投 | VETT_INTEGRATED_20261113/analysis/vett_evidence_position_transfer/REPORT.md | 75 |
| A14 | 43 字段复核与真短证据 | VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/COMPLETE_REPORT.md | 519 |
| A15 | A/B/C 实际输入审计 | VETT_INTEGRATED_20261113/analysis/input_and_score_audit/ACTUAL_INPUT_AUDIT.md | ? |
| A16 | Attribution Followup 结果 | VETT_INTEGRATED_20261113/analysis/attribution_followup/RESULTS.md | 121 |
| A17 | 证据标注跟进结果 | VETT_INTEGRATED_20261113/analysis/attribution_evidence_followup/RESULTS.md | 88 |
| A18 | 修好的完整短证据与整表回投 | VETT_INTEGRATED_20261113/analysis/attribution_update_and_full_table/ATTRIBUTION_RESULTS.md | 71 |
| A19 | 小模型诊断 v1 完整报告 | VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/COMPLETE_REPORT.md | 480 |
| A20 | 小模型诊断 v2 配对结果 | VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v2/PAIRED_RESULTS.md | ? |
| A21 | 小模型诊断 v7 报告 | VETT_INTEGRATED_20261113/analysis/VETT_SMALL_MODEL_DIAGNOSTICS_V7_REPORT.md | 81 |
| A22 | v6 修正 | VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v7/V6_CORRECTION.md | 31 |
| A23 | 多维 A 开发批结果 | VETT_INTEGRATED_20261113/analysis/vett_multidimensional_20261116/A_DEV_RESULTS.md | 13 |
| A24 | 多维 B 最小批结果 | VETT_INTEGRATED_20261113/analysis/vett_multidimensional_20261116/B_MIN_RESULTS.md | 19 |
| A25 | Pilot10 案例审计 | VETT_INTEGRATED_20261113/analysis/pilot10_case_audit/CASES.md | 388 |
| A26 | Pilot-Next 结果 | VETT_INTEGRATED_20261113/analysis/pilot_next/RESULTS.md | 167 |
| A27 | 证据升级更正 | VETT_INTEGRATED_20261113/analysis/vett_evidence_upgrade_20261115/CORRECTION.md | 75 |
| A28 | 自治工作流执行报告（11-17） | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/EXECUTION_REPORT_20261117.md | 206 |
| A29 | 执行汇总（11-18 至 11-19） | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/DAILY_SUMMARY_20261118.md | ? |
| A30 | 科学结论修正（B002–B015） | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/SCIENCE_CORRECTIONS.md | ? |
| A31 | 验收日志 V2 | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/ACCEPTANCE_V2.md | 153 |
| A32 | 8 小时里程碑 | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/MILESTONE_8H.md | 34 |
| A33 | 48 小时覆盖估算与限制 | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/RUN_PLAN_48H.md | 56 |
| A34 | 事故：11-18 休眠与 Ollama 停止 | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/INCIDENT_20261118_1913.md | 32 |
| A35 | 事故：11-19 主机重启 | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/INCIDENT_20261119_0910.md | 9 |
| A36 | 覆盖缺口 | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/reports/COVERAGE_GAP.md | 24 |
| A37 | 阶段报告（11-21 08:00） | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/reports/STAGE_20261121_0800.md | 208 |
| A38 | 小时报告（11-21 09:44） | VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/reports/HOURLY_20261121_094456.md | 228 |


---

## 10. 报告声明

- 本报告由 2026-11-21 会话汇总生成；未调用任何模型；未修改任何历史结果。
- 所有百分比保留原报告精度；跨报告冲突已保留双方口径并标注。
- 本报告之后的实验请以 vett_autonomous_20261117 的 STATE/STATUS 为准。


---

## 附录 A1：项目综合报告（2026-11-13）

> 原文件：VETT_COMPREHENSIVE_REPORT_20261113.md（267 行）

# VETT-Cricket 研究项目综合报告

**日期**：2026-11-13　**作者**：项目 agent（captain）　**团队**：`vett-r27-opt`（8 人）
**硬约束**：零付费 API · 零外网 · 不改 R26.15 任何字节 · 不读 `private/` · 不改冻结 packet
**本报告覆盖**：既有基础（220 场语料与 R20–R26.15 谱系）→ R28 数据集与结论 → 本轮 DeepTable V1 设计、执行与结果 → 现状与下一步。

> 数字纪律：本报告每个数字都标注来源文件。未经复算的数字不进结论。
---

## 0. 一页摘要

| 问题 | 状态 | 一句话结论 |
|---|---|---|
| 220 场底座 | ✅ 稳固 | 220 场 × 4 文件（解说/记分卡/证据链/元数据），98,572 个表格 cell，L2/L3 证据占 68% |
| R28 数据集 | ✅ 已交付 | 320 发布 + 40 held-out，一题一记录一族，确定性 solver 金标，证书 320/320 |
| R28 结论 | ⚠️ 零结果 | **“更难”不成立**（drop 0.557pp，CI 跨 0）；呈现侧操纵在 7B 上全部失效，因为模型根本不读证据（V0=0.125） |
| DeepTable V1（本轮） | ✅ 首轮完成 | 18 场 × 4 条件 × 3 模型 = 216 次；C0 只有 0.272–0.313，整表全对 0/216，失败面是闭合推导 |
| 下一步 | 待决 | 先写 D5 memo，再决定是否重建 C2 / 强化 C3 / 做人工双标 |

**一句话总判断**：R28 证明“把呈现做得更难”没有用；DeepTable V1 证明“把评分对象换成推导”有用——但当前 7–9B 模型在闭合推导上仍未过关，这正是下一阶段的价值所在。

## 1. 全局脉络

```
220 场记分卡语料（Self-cricket-clean_text_scorecard_v1_220_matches）
   └─ R20.220 → R22.220 → R24.220（规则 L1–L5 + 开放推理）
        └─ R26.13 / R26.14 / R26.15（answer-blind 影子、内容依赖图 +324 边，静态候选）
             └─ R28（单球裁决记录 + 四机制剂量 + 证书 + 双渲染）
                  └─ DeepTable V1（220 场表格 cell × R28 机制层 → 长卷宗整场记分卡）
```
三条主线始终没变：**事实来自确定性 solver**、**金标可机械重推**、**数据与实验全程零付费**。

## 2. 现有基础

### 2.1 语料底座：220 场
| 项 | 值 | 来源 |
|---|---:|---|
| 场数 | 220 | `Self-cricket-clean_text_scorecard_v1_220_matches/`（220 个 `match_*` 目录） |
| 每场文件 | 4：`commentary.txt`、`scorecard.md`、`evidence_chain.md`、`meta.json` | 同上 |
| 表格 cell 总数 | 98,572（均值 448.1/场） | `DEEP_T2T/corpus_audit.json` |
| cell 构成 | 击球 33,908 / 伙伴 24,563 / 投球 20,992 / FOW 9,837 / 汇总 9,260 | 同上 |
| 证据层级 L1 / L2 / L3 | 32.1% / 40.9% / 27.0% | 同上 |
| 文本均值 | 解说 6.4 KB、记分卡 5.2 KB、证据 2.5 KB | 同上 |

**读法**：语料并不浅——68% 的证据目标在 L2/L3（闭合/综合）。浅的是以往任务只问 L1 直取。

### 2.2 数据集谱系
| 版本 | 规模 | 主要内容 | 状态 |
|---|---:|---|---|
| R20 / R22 / R24 | 220 场 | 表格目标 + 证据探针；R24 增加 L1–L5 规则应用题与开放推理题 | 已发布（各自 `DATASET_CARD.md`、`MANIFEST.json`） |
| R26.15 candidate v3 | 220 场 | answer-blind 影子 + 324 条 `conditions_rule` 内容依赖边 | 静态候选，未做经验校准 |
| **R28** | 320 + 40 | 单球裁决记录 + 四机制剂量 + 证书 + 双渲染 | **已交付**（本报告 §2.3） |
| DeepTable V1 | 18 场切片 | 长卷宗 → 整场记分卡（76 cell/场） | **本轮完成**（§3） |

### 2.3 R28 数据集规格

> 来源：`VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/DATASET_CARD.md`、`build_index.json`、`MANIFEST.json`。

| 项 | 值 |
|---|---|
| 数据集版本 | `VETT-Cricket-v0.37-R28-diagnostic-pair-20261112`（design `R28-DOSE-DIAGNOSTIC-PAIR`） |
| 规模 | 发布 **320** + held-out **40** = 360 题；**一题一记录、一题一族、每题独立卷宗** |
| 题块 | `DL`（dose ladder）216 + `FC`（factor core）144 |
| 机制 | D1 alias_hops / D2 temporal_joins / D3 scope_decisions / D4 isomorphic_distractors，各 54 题（剂量 0/1/2 各 18） |
| 记录 | 12 字段 `decision_record_flat`（击球/投球得分、status、dismissal、账本 4 项等） |
| 金标 | 确定性 solver `vett_r25.solver`；**无任何语言模型参与事实、金标或证书** |
| 证书 | 320/320 覆盖；`rule_path` 只含承载算子；564 条非承载算子登记为 `presentation_only` |
| 双渲染 | 发布版（剂量按格赋值）与对照版（四剂量全 0）的 `solver_facts` + 记录 **逐字节相同**，只差呈现层 |
| 记录空间 | 规范网格可达互异记录 **4001**；实际 **320/320 互异**（R26.15 为 16/100） |
| 结构天花板 | `DEAD_REBALL` 只有 1 个可达记录；BOWLED/LBW/CAUGHT 各 2、STUMPED 4 → 合法 dismissal ≤ 11 |
| 分布（发布集） | status：LEGAL 166 / NO_BALL 100 / WIDE 53 / DEAD_REBALL 1；dismissal：RUN_OUT 86、NONE 124、HIT_BALL_TWICE 50、OBSTRUCTING_FIELD 50 等 |
| 构建确定性 | 同 seed 同配置可逐字节重建（`config_sha256 cc78be40…`，合同 v1.1.0 `7f10f983…`，预注册 v1.1.0 `5e0056e1…`） |
| 验收 | 12 项 t6 验收（`BUILD_ACCEPTANCE.json`，由 `scripts/verify_build.py` 只读磁盘独立重算） |

**必须同时说出的限制**：solver 是单球规则查表器，不是多跳推理机；金标未经人工双标；族名是中性哈希（`rfam_`+12 hex），不是泄漏轴。

### 2.4 R28 实验结论（t19 / t8 / t20 / t11）

> 来源：`R28_DECISION_REPORT.md`（289 行，sha256 `08406850…`）。

| 问题 | 判决 | 决定性读数 |
|---|---|---|
| Q1 更难了吗 | **不成立** | E1 配对 n=319：发布 59.56% vs 对照 60.12%，**drop 0.557pp**，CI **[−0.801, +1.846]**；整记录 exact **5/638 = 0.78%** |
| Q2 更有解释性吗 | 机械可验证成立；解释忠实度不成立 | 证书 320/320、solver 重推 100%；但 E4 顺序置换 stability⁰=**0.125** → `EXPLANATION_CLAIM_NOT_ESTABLISHED` |
| Q3 更能发表吗 | 作“能力基准”**不可发表** | 四条限定全 FAIL；只能作测量/零结果/验证装置论文 |

三条关键证据：
1. **E2 剂量-反应 REJECTED**：dose 0/1/2 准确率 59.375% / 62.674% / 60.938%，斜率 **+0.781pp/step**（方向相反），CI [−1.815, +3.402]，单调性 False。
2. **E3 机制归因 H3=False**：Holm 校正后无主效应；D4 名义 p=0.041 → Holm 后 **0.166**；交互模型 `NOT_ESTIMABLE_WITH_16x8`。
3. **E4 三孪生全 FAIL**：stability⁰ **0.125 (5/40)**、stability⁻ **0.500 (16/32)**、flip⁺ **0.525 (21/40)**（低于随机地板 0.875）。

**最硬的一段解释**：E1 的 0.557pp 不是“数据没变难”，而是**模型压根没在解题**——只打乱文档顺序，87.5% 的答案就变了。在模型不读证据的前提下，任何呈现侧操纵都必然无效。

**另一个最硬的负向发现**：1,546 条渲染规则引用中 **488 条（31.6%）从未承载推导**，`BAT_CREDIT` 118 次、`NB_COUNT` 100 次、`WIDE_COUNT` 53 次**从未必要**；360/360 题至少含一个非承载算子。这直接推翻“多写规则文本 = 推导更深”。

### 2.5 站得住的资产 vs 发表阻断项

**站得住（有证据）**：

| 资产 | 证据 |
|---|---|
| 金标可被确定性 solver 重推 | 320/320 = 100% |
| 记录空间打开 | 互异记录 320/320 = 1.0 |
| 族名捷径拆掉 | 值平衡 10.39%、lift −3.54pp、置换 p=0.146 |
| 证书可机械验证 | 320/320；`rule_path` 0 违规；564 条非承载登记 |
| 双渲染隔离 | facts + record 320/320 逐字节相同 |
| 闭环流水线 | 21 门 = 19 PASS / 2 DEGRADED；缓存可重放、熔断、降级均有实证（t20 10/10，19.3s） |
| 数据健康 | 互异 320/320、恒定字段 0、solver 重推 0 失败 |
| R26.15 零漂移 | 165 文件 / 93,346,177 B / aggregate `343afde4…` |

**发表阻断项（必须如实披露，不是待办）**：
1. **人工双标未执行**：金标由 solver 生成，t24 标注包 `ready_to_annotate=false`；
2. **MCC 规则文本许可未闭环**：规则摘要引用无再分发许可，发表前须法律复核；
3. **审计产物时间戳曾回填**：已在 `04_verify/PROTOCOL_VERIFY_RERUN_NOTE.json` 完整披露，规则已立“审计产物不得回填时间戳”；
4. **E5 区分度 UNTESTED**：只有 1 个可执行本地模型，区分度主张已撤回；T1 是词表匹配（余量 +0.125），不得当作能力证据。

### 2.6 本地推理与验证工具（可复用）

| 工具 | 位置 | 作用 |
|---|---|---|
| `local_inference.service` | `VETT_R28_DIFFICULTY_20261112/03_build/local/` | 冻结解码配置（`temperature=0`、`seed=20261112`、`num_ctx=8192`、`keep_alive=30m`）调用本机 ollama |
| `verify_build.py` | `03_build/scripts/` | 只读磁盘独立重算 12 项构建验收 |
| 闭环验证 | `04_verify/t20_closed_loop/` | 10/10 门、可重放、熔断演练 |
| 人工核验包 | `04_verify/human_verification_kit/` | 126 文件 / 11.8 MB，`ready_to_annotate=false`（阻断项） |
| 学术包 | `05_release/academic_package/` | `PACKAGE_STATUS.json = READY_WITH_BLOCKERS` |
| 论文骨架 | `05_release/paper/` | `NUMBERS.json` 登记全部发表数字 |
| 成本 | 全部本地 | R28 阶段实际调用：t14 905 次、t19 652 行、t21 2,835 次；**付费 ¥0、云端 0 次** |

## 3. 本轮做了什么：DeepTable V1

### 3.1 动机
R28 的判决指出了唯一出路：**难度必须来自事实与推导本身，而不是呈现**。DeepTable V1 就是把 220 场语料里 68% 的 L2/L3 cell 变成“必须推导”的评分对象——一卷宗一场，输出整场记分卡，用 closure（账目闭合）机械判错。

### 3.2 数据与任务
| 项 | 值 |
|---|---|
| 切片 | 18 场（`match_0001–0020` 中 0004/0011 因解析出的 innings ≠ 2 被 builder 跳过） |
| 卷宗 | 4 / 6 / 8 篇文档（C0/C1/C3/C2），均值 19,265 B（15.9–23.0 KB），另含 2 份他场干扰 |
| 输出 | 76 cell/场：2 局 ×（10 汇总 + 15 击球 + 12 投球）+ `result` + `pom` |
| 金标 | 由 `build_deep20.py` 的确定性 `finish()`/`amend()` 生成，closure 恒等式自洽 |
| 清单 | `data/build_manifest.json`，SHA256 `9dd7b31d…` |

### 3.3 四个条件
| 条件 | 操纵 | 文档数 | 金标变化 |
|---|---|---:|---:|
| C0 | 只有解说 + 设定 | 4 | — |
| C1 | + 2 条事件级修订备忘（M1 补 byes、M2 修最高分） | 6 | 145 cells（8/场） |
| C2 | + 在效 2026 规则 + 被取代 2025 规则（byes 计入投手）+ 冲突声明 | 8 | 0（设计使然：2025 是诱饵） |
| C3 | 删掉 M2 备忘 | 6 | 72 cells（4/场） |

### 3.4 执行
| 项 | 值 |
|---|---|
| 任务 | `bash-c0513adb23da412a`（12:41 启动，14:16 完成，exit 0） |
| 调用数 | 216 次（3 模型 × 4 条件 × 18 场） |
| 解码 | `temperature=0`、固定 seed → **确定性**，预测变化只来自提示变化 |
| 墙钟 | 约 95 分钟；gemma2:9b 最慢（约 60 s/次），qwen 约 12 s/次 |
| 成本 | **¥0**（本机 GPU，零外网） |
| 中断记录 | 旧会话 12:33:18 因 teardown 被杀，本会话 12:41 从 C3 第 5 行续跑（脚本按 `match_id` 去重） |

### 3.5 结果
**主表（12 格，全部 18 场）**

| 模型 | C0 | C1 | C2 | C3 |
|---|---:|---:|---:|---:|
| qwen2.5:7b-instruct-q4_K_M | 0.2722 | 0.2340 | 0.2458 | 0.2465 |
| llama3.1:8b | 0.3125 | 0.3067 | 0.3067 | 0.2847 |
| gemma2:9b | 0.2788 | 0.2986 | 0.2905 | 0.2920 |

整表全对 **0/216**；closure 违规率 **≈1.00**（qwen 平均每题 3.1–3.7 处违规 / 满 8）。

**按 cell 族**（cell_exact）：局汇总、击球手、投球手三族全部在 **0.19–0.38**；只有 2 个 cell 的 `pom`/`result` 达 0.44–0.50（二分类，运气成分高）。

**行为指标**：

| 指标 | 读数 | 含义 |
|---|---|---|
| copy_rate | 0.69–0.76 | 预测数值能在原文找到出处，但正确率仅 0.23–0.31 → **抄了错的数** |
| 修订跟随（C1，145 cells） | 0.145–0.193 | 低于各模型整体（0.234–0.307）→ 备忘成了上下文负担 |
| C3 证据必要性（72 cells） | 0.194–0.306 | 与 C1 相当 → 没“识别到证据缺失” |
| C2 陷阱（36 cells） | 正确 0–3%，落入 2025 陷阱 **0 次** | 闭合 cell 在地板上，走不到“哪版规则”那一步 |

### 3.6 预注册门判定
| 门 | 判据 | 读数 | 判定 |
|---|---|---|---|
| G1 | C0 cell_exact > 0.80 则太浅 | 最高 0.3125 | **PASS** |
| G2 | C1 table_exact = 0 且 closure > 0.50 | 0；1.00 | **PASS** |
| G3 | 三模型全 parse_fail | json_ok 1.000 | 未触发 |
| G4 | C2 version_sensitivity < 0.10 则重做 | 金标变化 0/1368；陷阱命中 0/36 | **判据作废**（对诱饵型操纵用“金标变化”判是本末倒置） |

G4 改写建议：改为“陷阱命中率 > 0 且 `bowling_runs` 基线正确率 > 0.30”，否则该条件在本能力档位不可用。

## 4. 两段实验合起来的判断

| | R28 | DeepTable V1 |
|---|---|---|
| 操纵 | 呈现侧（文档数、桥接深度、干扰同构、权威裁决） | 推导侧（修订重算、规则版本、证据缺失、闭合） |
| 结果 | 0.557pp，CI 跨 0 → 无效 | C0 0.272–0.313 → 有效但未过门 |
| 根因 | 模型不读证据（V0=0.125） | 模型不会闭合（closure 违规 1.00） |
| 结论 | 呈现侧加难在原理上无效 | 推导侧是唯一有价值的方向 |

**合起来的一句话**：R28 拆掉了“靠排版变难”的幻想，DeepTable V1 证明了“靠推导变难”的方向成立；现在缺的不是更多文档，而是让模型能算对账的机制与数据设计。

## 5. 局限

- **单模型/小样本**：R28 单模型（7B Q4_K_M）；DeepTable 18 场 × 18 次/格，CI 宽；均不外推到前沿模型。
- **金标非人工**：R28 与 DeepTable 的金标都是 solver/规则重算，不是独立人工标注——两处都构成发表阻断，不得写成“已标注”。
- **确定性解码的边界**：`temperature=0` 保证同 prompt 同输出，但不同 prompt 的差异不能完全归因于被操纵变量（C3 同时改了备忘集）。
- **C2 本档位无信号**：只能写“在本能力档位测不到”，不能写“版本冲突无效”。
- **copy_rate 是弱证据**：数值在文中出现 ≠ 抄对，只用于诊断。

## 6. 现状清单

| 资产 | 状态 | 位置 |
|---|---|---|
| 220 场语料 | ✅ 只读底座 | `Self-cricket-clean_text_scorecard_v1_220_matches/` |
| R20/R22/R24 数据集 | ✅ 已发布 | `VETT_Cricket_v0.22_R16_Multisource_Dilemmas/` |
| R26.15 candidate v3 | ✅ 静态候选 | 同上 |
| R28 数据集（320+40） | ✅ 已交付 | `VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/` |
| R28 实验与判决 | ✅ 完成（零结果） | `R28_DECISION_REPORT.md`、`eval_runs/t19_e1e5_20261112/` |
| R28 独立验证/闭环 | ✅ PASS_WITH_CAVEAT / 10-10 | `04_verify/` |
| R28 学术包/论文骨架 | ⚠️ READY_WITH_BLOCKERS | `05_release/academic_package/`、`05_release/paper/` |
| 人工核验包 | ⚠️ `ready_to_annotate=false` | `04_verify/human_verification_kit/` |
| DeepTable V1 数据 | ✅ 18 场 / 72 卷宗 | `DEEP_T2T/data/` |
| DeepTable V1 评测 | ✅ 216/216，exit 0 | `DEEP_T2T/runs/`、`results.json` |
| DeepTable V1 报告 | ✅ 本轮完成 | `DEEP_T2T/REPORT_V1.md`、`analysis.json` |
| D4 可靠性 | ⬜ 未做 | — |
| D5 memo / go-no-go | ⬜ 未写 | — |

## 7. 下一步（按性价比排序）

| 优先级 | 事项 | 依据 | 预计 |
|---|---|---|---|
| P0 | **D5 一页 memo**：按“G1/G2 过、G4 作废、C1/C3 未达”给出 go/no-go | 现有证据已足够 | 30 分钟 |
| P1 | **人工双标**（R28 的 t24 kit + DeepTable 抽 20 场） | 两处都构成发表阻断 | 2–3 人日 |
| P2 | **C2 重建**：让闭合 cell 先脱地板（给局部已闭合示例），再测版本陷阱 | 当前 0/36 正确率 | 54 次，约 30 分钟 |
| P3 | **C3 强化**：改为“删唯一决定性文档 → 必须弃权” | 当前只影响 4 cell | 需改 builder + 重算金标 |
| P4 | **D4 可靠性**：10 题 × 2 次，验证确定性与上下文边界 | `temperature=0` 已确定性，主要查边界 | 20 分钟 |

**不建议做**：继续加文档数/上下文长度/干扰数量——R28 已经证明这些呈现侧杠杆全部无效（E2/E3/E4）。

## 8. 附录

**文件索引**

| 用途 | 路径 |
|---|---|
| 本报告 | `VETT_COMPREHENSIVE_REPORT_20261113.md` |
| R28 判决 | `VETT_R28_DIFFICULTY_20261112/R28_DECISION_REPORT.md` |
| R28 数据集卡 | `VETT_R28_DIFFICULTY_20261112/03_build/dataset_r28/DATASET_CARD.md` |
| R28 数据集索引 | 同上 `build_index.json`（360 项，320 public + 40 held-out） |
| DeepTable 设计 | `DEEP_T2T/PLAN_V1.md` |
| DeepTable 报告 | `DEEP_T2T/REPORT_V1.md` |
| DeepTable 指标 | `DEEP_T2T/analysis.json`、`results.json` |
| DeepTable 原始输出 | `DEEP_T2T/runs/*.jsonl`（216 行） |

**复现**
```bash
PY="C:/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"
cd D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017
"$PY" DEEP_T2T/build_deep20.py --limit 20   # 构建（幂等）
"$PY" DEEP_T2T/eval_deep.py                  # 全量评测（按 match_id 去重可续跑）
```

---

*本报告所有 R28 数字引自 `R28_DECISION_REPORT.md`；所有 DeepTable 数字由脚本从 216 行原始输出重算（`analysis.json`）。任何未执行项均标 UNTESTED/未做，不含估计值。*


---

## 附录 A2：审稿人判决与最低成本提升路线

> 原文件：REVIEW_20261113/REVIEWER_JUDGMENT_AND_PLAN.md（321 行）

# VETT-R28 审稿人判决与最低成本提升路线（2026-11-13）

> 依据（只读）：`VETT_R28_DIFFICULTY_20261112/` 下的 `R28_DECISION_REPORT.md`、
> `eval_runs/t19_e1e5_20261112/`（`e1_raw.jsonl`、`e4_raw.jsonl`、`analysis*.json`）、
> `05_release/paper/`、`05_release/academic_package/`、`PROPOSAL_VETT_R28_...md`、
> `VETT_UPGRADE_STRATEGY_V2_20261112.md`。
>
> 复算：`REVIEW_20261113/per_field_check.py`（只读原始 jsonl，不改任何冻结产物），
> 结果 `REVIEW_20261113/per_field_recheck.json`。本文件里标「复算」的数字都来自它。

---

## 0. 一句话

**你不缺数据，也不缺工程量；你缺一个正确的因变量。**
你的原始输出里已经躺着一个比「难度不成立」好得多的结果：
**这个 7B 模型「会判规则、不会算账」**。主指标把这两件事平均成了一个
59.56%，于是既有的一切操纵都显得「没用」。

---

## 1. 判决：按三种定位分别打分

| 定位 | 现稿 | 修完本文 P0（约 2 周、¥0） | 说明 |
|---|---|---|---|
| 主会（ACL/NeurIPS/ICLR 正刊） | **Reject** | 仍 Reject | 单模型、半合成、无人工金标、任务窄；这是另一篇 R29 |
| NeurIPS D&B / ACL Resource | **Weak Reject** | **Borderline → 有机会** | 差三件便宜事：面板、人工上界、许可 |
| LREC / 诊断与负结果 workshop | **Borderline** | **Accept 面较大** | 现有证据链已经够，只差重写 |

按审稿表打分（现稿）：

| 维度 | 分 | 理由 |
|---|---|---|
| Novelty | 2/5 | 「又一个规则基准」；真正新的东西（证书、双渲染、预注册负结果）被埋在审计文档里 |
| Soundness（方法） | 3.5/5 | 复现、门、冻结链是真好；但统计单位与主张不匹配 |
| Soundness（主张） | 2/5 | 「难度不成立」被自己的数据否掉；「解释忠实」已撤回；「区分度」UNTESTED |
| Data quality | 2.5/5 | 构造干净，但 320 题、单球 solver、11 种合法 dismissal、半合成 |
| Reproducibility | **5/5** | 这是全场最强项，很多正刊论文做不到 |
| Clarity / positioning | 2/5 | 读起来像内部审计报告，不像论文 |

---

## 2. 审稿人一定会打的七枪（按杀伤力排序）

| # | 问题 | 现状 | 最便宜的补法 | 成本 |
|---|---|---|---|---|
| 1 | **一个模型不叫 benchmark** | E5=UNTESTED，只有 qwen2.5-7b-Q4 | 本机 3–4 个开源模型，逐题 arm | ¥0，约 1 天 |
| 2 | **金标没人工验证** | solver 金标，t24 kit 没执行 | 60 题双标，同时当「人工上界」实验 | 2–3 人日 |
| 3 | **半合成，无真实锚点** | 220 场只有局级聚合 | Cricsheet 20–40 个真实 delivery 接入 | ¥0，3–5 天 |
| 4 | **主指标只比先验高 4.5pp** | 59.56% vs 55.03%；record-exact 0.78% | 换逐字段 + skill；别再报 12 字段宏平均 | ¥0（已复算） |
| 5 | **你的因变量本身是噪声** | V0=0.125，87.5% 答案会变 | 先做 test-retest，把「顺序敏感」和「采样噪声」分开 | ¥0，80 次调用 |
| 6 | **定位不清**：cricket？审计？benchmark？ | 三个都像，三个都不彻底 | 改成「证据受限规则应用的诊断仪器」 | ¥0，写作 |
| 7 | **许可**：MCC 全文在包里 | B7 未闭环 | 删全文，换成自写规则摘要；数据 CC BY 4.0 | ¥0，1 天 |

第 5 枪是新的，也是最重要的：**你的 V0 结果现在不可解释**。
同一 prompt 跑两遍会不会也翻 87.5%？没人知道。这个混杂不解决，
「模型不读证据」这个 headline 就站不住；反过来，解决了它，无论结果哪边都能写。

---

## 3. 我复算了你的原始输出：三张被主指标埋掉的表

复算口径：`e1_raw.jsonl` 含 `e1`+`e1_rerun`，按 (item, arm) 取最后一行，
两臂都 parse_ok → **n=319 对**；`e4_raw.jsonl` 的 base 取同 item 的 published 答案。
与你们报告对得上的：record-exact 5/638、drop 0.557pp、V0 4/40（你们 5/40，差 1 条，基线选择差异）。

### 3.1 逐字段：12 个字段里 5 个高于常数众数、2 个恰好等于、5 个低于

| 字段 | hard | 该字段众数基线 | Δ vs 众数 | Δ hard−control |
|---|---:|---:|---:|---:|
| `delivery_status` | 0.809 | 0.517 | **+29.2** | +1.88 |
| `counts_in_over` | 0.796 | 0.533 | **+26.3** | **−13.48** |
| `ledger.PENALTY` | 0.784 | 0.520 | **+26.4** | +4.70 |
| `dismissal` | 0.574 | 0.386 | **+18.8** | +4.08 |
| `ledger.NO_BALL_EXTRA` | 0.850 | 0.687 | **+16.3** | +5.02 |
| `ledger.BYE` | 0.699 | 0.699 | 0.0 | 0.00 |
| `ledger.LEG_BYE` | 0.755 | 0.755 | 0.0 | 0.00 |
| `ledger.WIDE_EXTRA` | 0.799 | 0.834 | −3.5 | −2.19 |
| `total_runs` | **0.053** | 0.100 | −4.7 | −1.25 |
| `ledger.BATTER` | 0.715 | 0.765 | −5.0 | −2.82 |
| `bowler_runs` | **0.207** | 0.370 | −16.3 | +3.76 |
| `batter_runs` | 0.558 | 0.765 | **−20.7** | 0.00 |

三个读法（都可直接进论文）：

1. **能力是分裂的，不是「59.56%」。** 裁决类（status / counts / dismissal / penalty /
   no-ball）比众数高 16–29pp；数值类（batter / bowler / byes / total）等于或低于众数。
   `BYE` 与 `LEG_BYE` 的准确率**逐位等于众数**（0.699/0.699、0.755/0.755），
   数值上等价于模型全程输出 0——R28 把这三个常数字段改成非零了，
   但 BYE/LEG_BYE 上模型行为没变（`PENALTY` 有真实改善，+26pp）。
2. **`total_runs` 只有 5.3%**，比「永远输出 0」的 10% 还低。这不是「规则难」，
   这是**不会算账**：组件都对不上，合计自然崩。用模型自己的组件重算合计（算术闭包）
   也只有 6.1%，因为组件本身就错——所以别写「只是加法错」。
3. **主指标是这些方向的平均。** 9 个信息字段逐字段差相加 ÷ 9 = **−0.556pp**，
   正好等于你们的 drop 0.557pp。换句话说：**你的「零结果」主要是
   +5.02（no-ball）与 −13.48（counts_in_over）相抵后的净值**，不是「什么都没发生」。

### 3.2 顺序置换（V0）的逐字段翻转：不稳定全部集中在数值字段

| 字段 | 40 题里翻转数 | 字段 | 40 题里翻转数 |
|---|---:|---|---:|
| `total_runs` | **29** | `dismissal` | 8 |
| `batter_runs` | **26** | `ledger.NO_BALL_EXTRA` | 6 |
| `bowler_runs` | **25** | `counts_in_over` | 2 |
| `ledger.BATTER` | 15 | `ledger.WIDE_EXTRA` | 2 |
| `delivery_status` | 11 | `ledger.BYE` | 0 |
| `ledger.PENALTY` | 11 | `ledger.LEG_BYE` | 0 |

**结论要改口径**：`V0=0.125` 是「整条 12 字段记录一字不差」的比例；
逐字段看，裁决字段在顺序置换下基本稳定，翻的是计数。
所以你们 §1.5 写的「这个模型压根没在解题」**过强**——更准确的是
**「会判、不会算」**。这个说法更弱，但它是真的，而且更有意思。

### 3.3 唯一被呈现层推动的字段：`counts_in_over`，−13.5pp，方向相反

- hard 0.796 vs control 0.931；配对 McNemar **1 / 44**（精确二项 p<1e-11）。
- 这是 12 个字段里唯一一个 Bonferroni 后还显著的变化，而且是**变差**。
- 两种解释都必须排查：(a) 呈现剂量真的把这一格搞糊涂了；(b) 剂量渲染有 bug。
  抽 5 个翻转样本人工 diff 两版 prompt 就能定性，半天。

### 3.4 H1 已跑：同 prompt 重测 95% 稳定，换序 10% 稳定

2026-11-13，40 题 × 2 遍，`num_predict=640`，prompt sha 与 E1 published **40/40 一致**。

| 比较 | 整记录稳定 |
|---|---:|
| P1 vs P2（同 prompt 重测） | **38/40 = 0.95** |
| P1 vs V0（换序） | **4/40 = 0.10** |
| P1 vs E1（跨 420/640） | 35/40 = 0.875 |

- 重测底噪 5%，换序 90%，比值约 **18×** → **V0 是真实顺序效应，不是采样噪声**；headline 保住。
- 但 420→640 本身就会改 5/40（12.5%）记录：旧「E4 vs E1」比较有 max_tokens 混杂；
  用 P1 作基线后已消掉，这也说明这类实验必须钉死解码参数。
- 逐字段：重测翻转 0–2；换序翻转集中在 `total_runs` 28、`batter_runs` 26、`bowler_runs` 26、
  `ledger.BATTER` 15，而 `counts_in_over` 2、`WIDE_EXTRA` 3、`BYE`/`LEG_BYE` 0。
- 结论：「裁决稳、计数翻」的分裂在重测下更清楚，§3.2 的口径修正成立。

产物：`eval_runs/t19_retest_20261113/`（`retest_raw.jsonl`、`h1_result.json`），脚本 `REVIEW_20261113/h1_retest.py`。

### 3.5 H2 已跑：三个模型族都复现「裁决会、算账不会」

2026-11-13，3 模型 × 320 题（published 臂，`num_predict=640`，960 次调用，全部 `parse_ok`）。

| 模型 | info | record exact | law | law vs 众数 | count | count vs 众数 |
|---|---:|---:|---:|---:|---:|---:|
| qwen2.5:7b-Q4_K_M | 0.597 | 0.6% | 0.765 | **+23.5** | 0.543 | **−6.9** |
| llama3.1:8b-Q4_K_M | 0.679 | 0.9% | 0.836 | **+30.6** | 0.606 | **−0.6** |
| gemma2:9b-Q4_0 | 0.634 | 1.6% | 0.805 | **+27.5** | 0.549 | **−6.3** |

- **分裂可复现**：law 组三家全部高于众数 +23.5…+30.6pp，count 组三家全部等于或低于众数。
  这不是 qwen 的个例。
- **count 不是铁板一块**：`bowler_runs` 上 llama +23.1、gemma +8.4、qwen −15.6；
  但 `batter_runs`（−10.9…−22.2）、`ledger.BATTER`（−5.0…−27.2）、`total_runs`（绝对值 3.4–5.6%）
  三家全部差。准确说法是「**不会算击球手自己的账**」，不是「所有计数都不会」。
- `BYE`/`LEG_BYE` 三家准确率逐位等于众数（0.700/0.756）→ 三家都恒输出 0。
- **整记录 exact 0.6–1.6%**：没有模型接近解决，数据集仍有天花板空间。
- **面板跨度 8.2pp**（llama 0.679 − qwen 0.597），低于预注册的 25pp 区分度门；
  按 S2 仍**不宣称**「任务有区分度」，但「有 ≥2 模型面板」这一条已成立，E5 不再是 UNTESTED。
- qwen 640 vs E1 420：聚合 0.597 vs 0.596 几乎不动，但 **13% 的整记录会变**（278/319 相同）
  → 记录级 churn 大、聚合级稳定；这本身是「聚合指标掩盖记录不稳」的可靠性证据。

产物：`eval_runs/t19_panel_20261113/`（三个 `panel_*.jsonl` + `h2_result.json`），脚本 `REVIEW_20261113/h2_panel.py`。

---

## 4. 提升点到底在哪

### 4.1 换因变量，不换数据

| 旧主张 | 新主张 |
|---|---|
| R28 比 R26.15 更难 | 聚合准确率在规则类基准上不是合法因变量；要按字段类型分开报 |
| 模型不读证据 | 模型会判规则（顺序稳定、高于先验），不会算账（低于先验、顺序不稳定） |
| 证书证明解释忠实 | 证书是可机械重推的审计产物，不是模型解释 |
| 任务有区分度 | 待面板建立（现在撤回是对的） |

新题目可以是：
**"Law Is Learned, Accounting Is Not: A Per-Field Diagnostic of Evidence-Grounded Rule Application"**
（或更保守：*What Aggregate Accuracy Hides: A Per-Field, Pre-Registered Diagnostic Study*）

### 4.2 计划 A–G 的真实状态：只剩 C、E 和 F 的许可

| 阶段 | 状态 | 判决 |
|---|---|---|
| A 测量修复 | 大部分做完 | 缺「逐字段」这一刀（本文件 §3 已补） |
| B 因子归因 | 做完 | H3=false，**不用再碰 D1–D4** |
| **C 本地面板** | **已做（2026-11-13）** | 3 模型 × 320 题，law/count 分裂三族复现；E5 由 UNTESTED 变为「有面板、但 25pp 门未过」 |
| D 证据敏感性 | 做完但被混杂 | 补 test-retest，否则 V0 不可解释 |
| **E 人工审计** | **没做** | **发表阻断项，必须做；顺手变成「人工上界」** |
| F 发布工程 | 做完 | 只差 MCC 许可（1 天） |
| G 220 物化 | 没做 | **永远不做**；审稿人不数场次 |

**所以「计划提升的点」不是再加一个机制，而是把 C 和 E 做完，再把 A 的逐字段那一刀补上。**
A/B/D 已经给了否定答案；回到 D1–D4 就是重复给不可辨识的量做测量。

### 4.3 六个实验，每一个都「两边都能写」（这是省钱的关键）

| ID | 实验 | 规格 | 调用量 | 成本 | 结果 A（可写） | 结果 B（也可写） |
|---|---|---|---:|---:|---|---|
| H0 | 逐字段复算 | 已有 raw | 0 | ¥0 | 已完成（§3） | — |
| **H1** | **test-retest** | 40 题 × 同 prompt 重复 2 次 | 80 | ¥0，20 min | 重复稳定 → V0 的翻转是顺序效应 | 重复也翻 → V0 混淆采样噪声，headline 改写 |
| **H2** | **模型面板** | 3 个本地模型 × 320 题（published 臂） | 960 | ¥0，约 2–3 h | 面板复现「裁决 vs 算账」→ 普遍现象 | 某模型算账也对 → 区分度成立，有强基线 |
| **H3** | **无卷宗基线** | 3 模型 × 160 题，只给题面 | 480 | ¥0，约 1 h | 掉很多 → 卷宗确实在起作用 | 不掉 → 分数主要是先验，仪器读数要重写 |
| **H4** | **人工上界 + 金标审计** | 60 题分层，两人盲做 + 仲裁 | 人力 | 2–3 人日 | 人类高 → 任务可解，模型差得远 | 人类也低 → 卷宗欠定，修数据 |
| H5 | 证书消融 | 160 题 × 有/无 rule_path | 320 | ¥0，1 h | 证书有用 → 解释贡献 | 没用 → 证书只是审计，别当贡献卖 |
| H6 | 真实锚点 | Cricsheet 20–40 个 delivery | 少量 | ¥0，3–5 天 | 分布接近 → 外部效度 | 差很多 → 说明 R28 是构造分布（也诚实） |

合计：**约 1,840 次本地调用（≈5 小时 GPU）+ 60 题人工**。付费 API ¥0。

**H4 是性价比最高的一项**：它同时回答三个审稿问题——
金标对不对、任务可不可解、人类和模型的差距在哪。别把它当「合规作业」。

**H1 是必须先做的一项**：80 次调用、20 分钟，决定你的 headline 是「顺序敏感」
还是「采样噪声」。这是全项目信息/成本比最高的一次测量。

### 4.4 为什么这比「加难度」便宜且值钱

- 不生成新数据，不扩 solver，不碰 R26.15 字节。
- 每个实验的两种结果都能写，不存在「跑完发现白跑」。
- 面板 + 逐字段一旦成立，你的结论从「一个 7B 模型在一个数据集上没测出难度」
  变成「一类模型在规则类任务上普遍存在裁决/算账分裂」——后者才是审稿人认的。

---

## 5. 成本与工期

| 项 | 钱 | 人日 | 墙钟 |
|---|---:|---:|---:|
| H1 test-retest | ¥0 | 0.1 | 20 min |
| H2 面板（3 模型 × 320） | ¥0 | 1.0 | 2–3 h |
| H3 无卷宗（3 × 160） | ¥0 | 0.5 | 1 h |
| H4 人工（60 题双标） | ¥0 | 3.0 | 2–3 天 |
| H5 证书消融 | ¥0 | 0.5 | 1 h |
| H6 Cricsheet 锚点 | ¥0 | 2.0 | 3–5 天 |
| 许可/写作/图 | ¥0 | 6.0 | 1 周 |
| （可选）一个前沿模型锚点 | ¥10–30 | 0.2 | 1 h |
| **合计** | **≤¥30** | **≈13 人日** | **2–3 周** |

对照：再跑一轮 Pilot20 是 ¥5.6 且仍然不可辨识；物化 220 场是 20 GB 且不加分。

---

## 6. 不要做的事（省钱也省 token）

1. **不物化 220 场。** 没有审稿人按场次给分；320 题的诊断论文不需要它。
2. **不再跑 D1–D4 难度机制。** E2/E3 已经否掉；再跑是重复测量。
3. **不做 320 题全量双标。** 60 题分层审计足够回答「金标可不可信」。
4. **不写更多内部审计文档。** 44KB proposal + 22KB 决策报告已经超过审稿人阅读量的 10 倍；
   论文只有 8 页，先写论文。
5. **不做云端大扫描。** 至多一个前沿模型锚点，¥30 封顶。
6. **不改 R26.15 字节。** 冻结链是你的资产，不是障碍。
7. **不要为了「更难」扩 solver。** 那是 R29 的另一篇论文；这周做它等于把发表再推三个月。

---

## 7. 论文骨架（8 页，Resource/Diagnostic 路线）

1. **Intro（1 页）**：规则应用 = 版本化法规 + 冲突权威 + 精确数值；
   聚合准确率把「证据可见性 / 作用域 / 版本 / 计算」混成一个数。
2. **Task & data（1.5 页）**：320 题、确定性 solver 金标、逐题证书、
   双渲染、预注册、held-out 40。
3. **Protocol（0.75 页）**：逐字段 skill vs 边际众数；record-exact；
   重复测量；双渲染。
4. **Results（2.5 页）**：
   - 图 1：逐字段 skill 的双峰（裁决 +16…+29pp vs 算账 −4…−21pp）。
   - 表 1：聚合 59.56% 是混合，不是能力。
   - 图 2：V0 逐字段翻转 + test-retest 基线。
   - 表 2：呈现层操纵的净零与 `counts_in_over` −13.5pp。
   - 表 3：人工上界 vs 模型。
5. **Discussion（1 页）**：为什么难度阶梯在这类任务上不可辨识；
   基准报告建议（逐字段 + 重复测量 + 无卷宗基线）。
6. **Limitations（0.5 页）**：单数据集、小模型、半合成；如实写。
7. **Release（0.25 页）**：许可、数据卡、复现命令、held-out。

贡献四条：
(i) 一个带确定性金标与最小证明证书的诊断集；
(ii) 一个「裁决/算账」能力分裂的逐字段读数；
(iii) 一次顺序稳定性 + 重复测量的可靠性审计；
(iv) 一个预注册的呈现层零结果。

---

## 8. 投稿路线

| 目标 | 可行性 | 备注 |
|---|---|---|
| NeurIPS D&B | 中 | 修完 H1–H4 + 许可；强调「仪器 + 负结果 + 可靠性」 |
| ACL/EMNLP Resource & Evaluation | **较高** | 最匹配；8 页，负结果受欢迎 |
| LREC | 高 | 保底；数据卡与许可做好即可 |
| 主会正刊 | 低 | 需要 R29：扩 solver + 真实数据 + 前沿模型 |

时间上按 ARR 的月度窗口倒排；别等「全部做完」才写，先写 results memo。

---

## 9. 接下来 72 小时

**Day 1**
1. 跑 H1：40 题 × 同 prompt 两次（80 调用），比「同 prompt 翻转率」与「V0 翻转率」。
2. 用 `per_field_check.py` 的出图：逐字段 hard vs 众数（图 1 草稿）。
3. 把 §3.3 的 5 个 `counts_in_over` 翻转样本人工 diff prompt。

**Day 2**
4. 起 H2：3 个本地模型 × 320 题（published 臂），后台跑。
5. 做 60 题分层抽样包，找两位标注者（先做 20 题资格测试）。
6. 删 MCC 全文，换自写规则摘要；跑一次许可自检。

**Day 3**
7. H3 无卷宗基线（3 × 160）。
8. 写 2 页 results memo（不是论文）：逐字段表 + V0 表 + counts 异常。
9. 决定 headline：如果 H1 显示重复也翻，改成「可靠性审计」；否则保持「顺序敏感」。

---

## 10. 边界

- 本文所有复算数字来自 `e1_raw.jsonl` / `e4_raw.jsonl`，口径写在 §3；与你们报告不一致处已标出（V0 4/40 vs 5/40）。
- 逐字段众数是**该字段的边际众数**；9 个信息字段的众数平均是 55.08%，与 55.03% 的微平均先验一致；
  12 字段的众数平均是 57.7%，差 2.7pp 只是多算了 3 个 ledger 字段，不冲突。
- 我没有改任何冻结产物；`REVIEW_20261113/` 是新增目录。
- 「会判、不会算」是对 7B Q4 单模型的读数，不外推；这正是 H2 要检验的。


---

## 附录 A3：R28 决策报告

> 原文件：VETT_R28_DIFFICULTY_20261112/R28_DECISION_REPORT.md（289 行）

# R28 决策总报告（t11）

> **三个问题，只给数字与区间，不给安慰。**
> 团队：`vett-r27-opt` ｜ 作者：`measurement_auditor` ｜ 日期：2026-11-13
> 输入（只读）：`eval_runs/t19_e1e5_20261112/`（E1–E5）、`04_verify/`（t8/t20）、`04_verify/J_GATE.json`（t17 J 门）、`03_build/local/`（t14/t18/t21）、`05_release/academic_package/`（t9）、`05_release/paper/`（t23）、`05_pipeline/runs/live_full/gate_ledger.jsonl`（t13/t20）。
> 数字纪律：本报告只引用上述来源；不重算、不换指标、不事后改口径。所有 CI 均为 95%。付费 API：**¥0**；云端调用：**0**。

## 0. 三行结论

| 问题 | 判决 | 决定性证据 |
|---|---|---|
| **Q1 更难了吗** | **不成立（不成立就是“不成立”）** | E1 drop **0.557pp**，CI **[−0.801, +1.846]**（跨 0）；E2 剂量 **REJECTED**；E3 **H3=False**；且 E4 的 V0=0.125 证明模型不读证据——呈现侧加难在原理上无效 |
| **Q2 更有解释性吗** | **机械可验证性成立；模型“依赖证据”的解释忠实度不成立（S12 撤回）** | 证书 320/320、solver 重推 100%、`rule_path` 只含承载算子；但 V0 置换后 87.5% 答案改变，解释主张 `EXPLANATION_CLAIM_NOT_ESTABLISHED` |
| **Q3 更能发表吗** | **作为“能力基准”不可发表（四条限定缺一即 FAIL）；只能作为测量/零结果/验证装置论文发表** | T1 是词表匹配（余量 +0.125）；E5 UNTESTED 且区分度撤回；T3 n=12 仅描述；κ 全部 n<30 不估计；人工双标未执行、规则文本许可未闭环 |

---

## 1. Q1：更难了吗

### 1.1 E1 主端点（严格配对，n=319）

| 指标 | 值 | 来源 |
|---|---:|---|
| 配对 n | **319**（320 对中 1 对因 published 持久截断被排除；失败走 conformance） | `analysis.json#/E1` |
| 发布版信息字段准确率 | **59.56%**（1710/2871）Wilson95 [0.5775, 0.6134] | 同上 |
| 对照版信息字段准确率 | **60.12%**（1726/2871）Wilson95 [0.5831, 0.6189] | 同上 |
| **配对差 drop = control − hard** | **+0.557pp** | 同上 |
| 95% CI（按题 / 按族 bootstrap 两版取更保守下界） | **按题 [−0.801, +1.846]**；按族 [−0.766, +1.881]；保守下界 **−0.801pp（跨 0）** | `analysis.json#/E1/drop_pp_ci95_*` |
| 配对方向（逐题准确率比较） | control 更准 **69** / hard 更准 **47** / 并列 **203**；符号检验双侧 p=**0.0507** | `analysis.json#/E1/paired_accuracy_direction` |
| 9/9 信息字段全对 McNemar | b=2, c=1, 双侧 p=**1.0000** | `analysis.json#/E1/mcnemar_correct9` |
| **整记录 exact（12/12 字段）** | **5/638 = 0.78%**（hard 2/319、control 3/319；Wilson95 [0.34%, 1.82%]） | `analysis.json#/E1`、`e1_raw.jsonl` |
| 效应量 | Cohen's h=**−0.011368**；OR=**0.977077** | `05_release/paper/NUMBERS.json#/E1` |
| 预注册判定 | `primary_outcome=DIRECTION_ONLY`、`headline=DIRECTION_ONLY + DEGRADED`、`harder_claim_permitted=false` | `analysis.json#/claim` |

辅助一致性：ITT 敏感性（失败按 0）drop=0.833pp，CI [−0.590, +2.222]；空配对（四剂量全 0，n=72）drop=**−0.309pp**（两臂 prompt 全同，placebo 通过）；active 配对（n=247）drop=0.810pp。

### 1.2 E2 剂量-反应：**REJECTED**

| 指标 | 值 |
|---|---|
| DL 题数 | 192（D1–D4 × 剂量 0/1/2 × 16） |
| 信息字段准确率 dose 0/1/2 | **59.375% / 62.674% / 60.938%** |
| 相对 dose0 的 Δ | +3.299pp / +1.563pp（方向与“加难”相反） |
| OLS 斜率（逐题准确率，mechanism FE，HC1） | **+0.781pp/step**，CI **[−1.815, +3.402]**；单侧 p(β<0)=0.280 |
| 单调递减 | **False**；四机制支持数 **0/4** |
| 判决 | **HYP-R28-DOSE = REJECTED**（非单调 + 反向 + |效应|<10pp + CI 含 0，四条拒绝条件全部命中） |

来源：`analysis_e2.json`、`05_release/paper/NUMBERS.json#/E2`。

### 1.3 E3 机制归因：**H3=False**

| 主效应 | β(pp) | 95% CI | Holm p (m=4) |
|---|---:|---|---:|
| D1 证据跳数 | −1.18 | [−7.06, +4.70] | 1.000 |
| D2 修订链 | −1.87 | [−7.77, +4.03] | 1.000 |
| D3 权威裁决 | −2.22 | [−8.10, +3.66] | 1.000 |
| D4 干扰同构 | −6.11 | [−11.99, −0.24]（未校正名义显著） | **0.166** |

- **H3 不成立**：Holm 后无主效应；D4 名义 p=0.041，但 Holm 后 0.166。
- **交互模型 `NOT_ESTIMABLE_WITH_16x8`**：16 格 × 8 题无法识别 6 个二阶交互；不报推断结论。
- 来源：`analysis_e3.json#/coefficients`、`05_release/paper/NUMBERS.json#/E3`。

### 1.4 三条基线与 claim gates

| 基线（R28 同集） | 准确率 | 与 hard(59.56%) 的关系 | 门 |
|---|---:|---|---|
| 常数先验（LOFO） | **55.03%** | hard 更高（对“更难”方向不利） | G2 FAIL（skill_hard=**+0.1007**） |
| 只看题面 TF-IDF+LR | **54.76%** | hard 更高 | — |
| 族名众数（泄漏轴） | **53.16%**（值平衡 10.39%、lift −3.54pp、p=0.146） | — | HA10 PASS |
| anchor 众数（R26.15 参考 73.33% / exact 32%） | **NOT_MEASURABLE**（R28 无 anchor 字段） | 无法比较 | **G1/G1r = UNTESTED → DEGRADED** |

**G1 不可执行本身就是判决的一部分**：按预注册 `baseline_gate.fail_safe`，anchor 同集重测不可测 → G1=UNTESTED → **不允许任何 HARDER 宣告**。G2 又 FAIL（发布版反而高于常数先验 10.07 个百分点，skill=+0.1007）。来源：`01_measurement/baselines_same_set.json`、`analysis.json#/gates`。

### 1.5 Q1 的收束：E1 的零结果必须由 E4 解释（这是本节最重要的一段）

E4 的 V0 是“只把文档/span 顺序反转、文本多重集与 id 全部守恒、金标逐字节不变”的对照：

- **stability⁰ = 0.125（5/40）**，Wilson95 [0.055, 0.261] → **仅打乱文档顺序，87.5% 的情况下答案就变了**（门 ≥90%，FAIL）。
- stability⁻（改既有非决定性事实、金标不变，substitution n=32）= **0.500（16/32）**，CI [0.336, 0.664]（门 ≥80%，FAIL）。
- flip⁺（改决定性事实、金标改变）= **0.525（21/40）**，CI [0.375, 0.671]；**低于随机地板 0.875**（门 ≥2× 随机，FAIL）。

**因此，Q1 的正确表述是：**

> **E1 的 0.557pp 不是“数据集没变难”，而是“这个模型压根没在解题”。** 如果模型本来就不读证据（V0 单独就翻车），那么把证据呈现得更难当然不会让它更糟。**在模型不读证据的前提下，任何呈现侧的操纵都必然无效。**

这条单一机制同时解释：E1（无难度效应）、E2（非单调）、E3（无机制归因）、E4（三门全败）、record-exact 0.78%。**Q1 判决：不成立。**

---

## 2. Q2：更有解释性吗

### 2.1 正面：证书的机械可验证性成立

| 指标 | 值 | 来源 |
|---|---|---|
| 证书覆盖 | **320/320** | `04_verify/INDEPENDENT_VERIFICATION.md`、`BUILD_ACCEPTANCE` |
| 冻结 solver 重推金标 | **100%**（320/320） | 同上 |
| `rule_path` 只含承载算子 | **0 违规** | 同上 |
| 非承载算子登记 | **564** 条进入 `presentation_only_operators` / `mechanism_witness.presentation_only_registry` | 同上 |
| 双渲染隔离 | facts + record **320/320 逐字节相同**，仅呈现层不同 | t8 数据健康 PASS |

**机制归因硬约束**：只能对 `mechanism_witness.json` 中**未被标 PRESENTATION_ONLY** 的机制（D1–D4）归因；**564 条非承载算子只能计入呈现层，不得计入“更难”**。D1/D4 的机制可见性另见 §3.5（NOT_INSTRUMENTED）。

### 2.2 负向发现：31.6% 的规则引用是装饰性的（独立成节）

- 渲染规则 span 共 **1,546** 条，其中 **488 条（31.6%）从未承载**推导；
- **360/360 题**至少含一个非承载算子；
- `BAT_CREDIT` 渲染 **118** 次、`NB_COUNT` **100** 次、`WIDE_COUNT` **53** 次，**从未必要**；
- `COUNTS_IN_OVER` 仅 317/360 必要；`rule_path` 1199 条与必要算子 0 交集。

这直接推翻“多写规则文本 = 推导更深”的直觉；也是本计划最硬的负向测量结论之一。来源：`03_build/reports/derivation_depth_witness.json`、`mechanism_witness.json`、t9 数据卡 B3。

### 2.3 E4 三孪生：三条门全部 FAIL，`EXPLANATION_CLAIM_NOT_ESTABLISHED`

| 指标 | 实测 | 95% CI | 门 | 判定 |
|---|---:|---|---:|---|
| flip⁺ | **0.525**（21/40） | [0.375, 0.671] | ≥2× 随机地板（0.875） | **FAIL**（且低于地板） |
| stability⁻（substitution，n=32，主指标） | **0.500**（16/32） | [0.336, 0.664] | ≥80% | **FAIL** |
| stability⁻（introduced，n=8，单列不合并） | 0.125（1/8） | [0.022, 0.471] | 不合并 | 仅记录 |
| stability⁰（V0 顺序置换，n=40） | **0.125**（5/40） | [0.055, 0.261] | ≥90% | **FAIL** |

- V− 可用率（320 题机械判定）：substitution **271/320**、introduced **49/320**、none **0**；
- `S12=True` → **`EXPLANATION_CLAIM_NOT_ESTABLISHED`**：不得把证书当作“模型依赖证据”的证明；
- conformance：**120/120 `done_reason=stop`**、parse_ok 100%（num_predict 实际 640，未截断）。
- **append-only 说明**：E4 是 t19 完成后的补充实验（`supplemental_to_t19: true`，`generated_at_utc=2026-11-12T15:24:04Z`，输入 sha256 均已登记）；**原 t19 文件未改**（analysis.json / analysis_e1–e4.json / e1_raw.jsonl / E1_E5_REPORT.md 与 MANIFEST sha256 逐项一致）。
- 来源：`analysis_e4_supplemental.json`、`E4_SUPPLEMENTAL.md`、`e4_raw.jsonl`。

### 2.4 T2 偏好侧（辅助）

- 有效对 **317**（3 条 `INEFFECTIVE_CORRUPTION` 剔除：r28q_0067/0099/0159）；
- 序判定一致率 **0.9905（314/317）**，Wilson95 [0.9725, 0.9968]；t18 30 对校准 30/30；
- 绝对分只作描述，进阈值即 FAIL。

**Q2 判决：作为数据集属性，“证书可机械验证”成立；作为模型属性，“解释依赖证据”不成立（S12 撤回）。**

---

## 3. Q3：更能发表吗

**四条限定，缺一即 FAIL；四条全部命中 FAIL。**

### 3.1 限定一：T1 是词表/模式匹配倾向，不能当“读懂证据”的能力证据

| 指标 | 值 |
|---|---|
| 总体一致率 | **0.9750（312/320）**，Wilson95 [0.9515, 0.9873] |
| POS_OVERRIDE | **0.8333（40/48）**，Wilson95 [0.7042, 0.9130] |
| NEG_PLAIN / NEG_PROVENANCE_ADJACENT | 1.0 / 1.0 |
| 恒答 false 基线 | **0.8500（272/320）** → 总体余量仅 **+0.1250** |
| 错误集中度 | **8/8 错误全部落在 `authority_policy` 同一句式**；按 span role：`authority_policy` **0.7500（24/32）**，其余 role 1.0 |

**禁令（写入报告）**：**不得写“错集恰好等于词表不命中集 / 集合完全相同”**。verifier 实测：把 `controlling` 加入 `OVERRIDE_LEXICON` 后，词表不命中集变为 **0** 而错误仍是 **8**，等式即破（broad-semantic 变体同样 0/8）。该等式只是当时词表状态的偶然巧合，不能作为机制陈述。T1 可作标注劳动（过 0.85 门），但**不得**当作本地模型判断证据支持的能力证据。

### 3.2 限定二：E5 = UNTESTED，区分度主张已撤回

- 可执行模型数 **1**（仅 `qwen2.5:7b-instruct-q4_K_M`）；零付费硬约束禁止云端 1 + 云端锚点 1；
- 按预注册 S2：面板降级 → **DEGRADED/UNTESTED**、**撤回“任务有区分度”的主张**、不得判 PASS；
- **不得写成“E5 未跑”这种含糊表述**：这是已作出的否定性判决（E5 需要 ≥2 模型、最强−最弱 ≥25pp 才能建立区分度）。

### 3.3 限定三：T3 只有逐字段 verdict 可用（n=12 < 30，DESCRIPTIVE_ONLY）

| 指标 | 值 |
|---|---|
| 提报数 | 12（全部真错：overall=DEFECT 是平凡策略 12/12） |
| abstain / conformance | 12/12 PASS（**无区分度**） |
| 逐字段 verdict | **precision 0.9333（28/30）**；**recall 0.6087（28/46，漏 18）** |
| 云端自写 `correct_record` vs solver 金标 | **0.4514（65/144 字段）** → **模型输出绝不能当金标** |

### 3.4 限定四：κ 全部 n<30 → 不估计

- T1 R28 臂 n=**17**、T1 同刺激臂 n=**24**、T2 n=**16**：**均不估计**；
- 探索性合并（T1 两臂 n=41）：κ=0.8951，CI [0.7192, 1.0]，**只作量级、不得进主表**。

### 3.5 其他必报

| 项 | 值 / 状态 | 来源 |
|---|---|---|
| C_t14 跨实现一致性 | 仅 **17/24** 题同 span 可比（7 题不可比），**17/17 一致**；与同刺激臂合并 **2/41 = 4.88%**（<30%） | `J_GATE.md §3.1` |
| S1 span 主题 | **DESCRIPTIVE_ONLY**（R28 无机械主题真值；207 模型 + 96 机械回退 + 17 DEGRADED） | `J_GATE.md §2.3`、t14 |
| D1/D4 机制可见性 | **NOT_INSTRUMENTED**（T1v1 只筛修订/权威覆盖；false ≠ 剂量不可见） | t14 §3、`J_GATE.md` |
| J8 状态 | **PASS**、blocking=[]；内容摘要 `9b0f4d40…`；C1 账本 905/标注 320/变体 0；C2 raw 0/struct 0/unauditable 0；C4 71 缓存 0 错；C5 35 文件 0 生产引用 | `J_GATE.json/.md` |
| 协议终版 digest | PAMEND-004 后：`protocol.json` **1a87c316…c50c1293**、`PROTOCOL.md` **9758d0e1…7eb4300e**、`protocol_freeze.json` **ab18ee1b…0f0761697e**；`--check` **22/22 PASS**。任务书引用的 **a07463aa…02ff7a / 77caf7a0…e54475** 是 PAMEND-003 时值（PAMEND-004 扩了 r28* id 禁用模式） | `02_design/protocol_freeze.json`、`J_GATE.md §1` |
| R26.15 零漂移 | **165 文件 / 93,346,177 B / aggregate 343afde4…51bd**；总保护集 aggregate **66e108d8…a0433** | `INDEPENDENT_VERIFICATION.md §3` |
| R-R7 重放绑定 | 仅按当前解析器版本重放：**806/806 cache-key v2 独立复算**、旧模板 **0**、解析器不兼容 **0**；旧 `cost_ledger` 条目不计入 | `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json` D6、t13 |
| 数据健康 | 互异记录 320/320；恒定字段 0；BYE/LEG_BYE/PENALTY 96/78/153；status 166/100/53/1；合法 dismissal 10 + DEAD 1；solver 重推 0 失败；双渲染 0 失败；rule_path 0 违规 | t8 §5 |

**成本与耗时（全部本地、付费 API ¥0、云端 0 次）**

| 模块 | 调用/题数 | 墙钟 | 来源 |
|---|---:|---:|---|
| t18 能力矩阵 | 162 次全新调用 | 46.8s | t18 |
| t14 预标注 | **905** 次模型调用 | 195.836s | t14 REPORT |
| t19 E1 | 652 行（640 唯一对 + 12 重跑） | wall 合计 5,135.6s | `e1_raw.jsonl` |
| t19 E4 | 120 次 | wall 合计 466.5s | `e4_raw.jsonl` |
| t21 C1 | **2,835** 次 | 587.827s | t21 REPORT |
| t20 闭环验证 | 10/10 | **19.255s** | `CLOSED_LOOP_VERIFICATION.json` |

**DEGRADED / ESCALATED 清单（不掩盖）**

- 流水线 live_full：21 门 = **19 PASS / 2 DEGRADED**：`G_ANNOTATION_COVERAGE`（mode=mechanical_only，coverage=0.0）、`G_JUDGE_COMPARABILITY`（无 comparables）；
- t14：S1 **17 条 DEGRADED**（PARSE_FAILURE → 机械 PROVENANCE 回退）；
- t19：**1 条持久失败** `r28q_0117/published`（512 tokens 仍截断；双份保留，主分析排除该对）；
- t20 故障演练：D2 本地停服 → mechanical_only + **3 条 DEGRADED** + coverage 0；有界修复演示 **ESCALATED×1**（t13 单测/演练，非生产结论）；
- t8：`PASS_WITH_CAVEAT` 12 项 = 10 PASS + `PASS_WITH_DISCLOSURE`（时间戳回填）+ `PASS_WITH_CAVEAT`（GBK 复现，caveat 1 已由 t9 修复闭合；caveat 2 披露保留）。

**Q3 判决：作为“能力基准”不可发表（四条限定全 FAIL + 两项发表阻断）；作为测量/零结果/验证装置论文，证据链完整、可发表。**

### 3.6 四个发表阻断项 / 自纠固定段落

1. **人工双标未执行**：金标是 solver 生成的，t24 标注工具包 `ready_to_annotate=false`；这是发表阻断项，不是“待办”。
2. **MCC 规则文本许可未闭环**：数据 CC BY 4.0 / 代码 MIT 已定稿；规则摘要引用无再分发许可，发表前必须法律复核（B7）。
3. **审计产物时间戳曾回填**：`protocol_verify_result.checked_at` 曾被回填为 15:09:53Z，已在 `04_verify/PROTOCOL_VERIFY_RERUN_NOTE.json` 完整披露；规则已立：审计产物不得回填时间戳。t8 以 `PASS_WITH_DISCLOSURE` 记录，不掩盖。
4. **captain 两次同类错误（自纠）**：
   - “**剂量杠杆已验证**”——拿整级宏准确率 63.3/60.0/51.7 冒充同事实组配对比较；t3 逐对重算为 **5 降 / 4 升 / 1 平，均值 −3.3pp，符号 p=0.50**，断言错误；
   - “**S2 内容与 S1 相同**”——跨口径哈希比较（旧口径 `5d7efca5…` vs v2 `9b0f4d40…`）不可比，被 judge_architect 当场纠正。
   - **教训（写入验收规则）**：凡“看起来没变”或“看起来变难了”的主张，先问**这个比较能否被第二个人独立复算**；不能复算的比较不得进验收清单。

---

## 4. 零结果契约：哪些站得住、哪些被推翻

### 4.1 本报告直接写“不成立”的命题

| 命题 | 判决 | 原始数据路径 |
|---|---|---|
| R28 比 R26.15“更难” | **不成立**（drop 0.557pp，CI 跨 0；harder_claim_permitted=false） | `eval_runs/t19_e1e5_20261112/analysis.json` |
| 语义机制剂量↑ → 准确率单调↓（HYP-R28-DOSE） | **REJECTED** | `analysis_e2.json` |
| 机制可归因（H3） | **不成立**（H3=False；交互不可估） | `analysis_e3.json` |
| 模型依赖证据 / 证书可证明解释忠实度 | **不成立**（S12；解释主张撤回） | `analysis_e4_supplemental.json` |
| 任务有区分度 | **撤回**（E5 UNTESTED，S2） | `e5_availability.json`、`05_release/paper/NUMBERS.json#/E5` |
| 本地模型“读懂证据” | **不成立**（T1 词表匹配，余量 +0.125；D1/D4 NOT_INSTRUMENTED） | `03_build/local/t14/REPORT.md` |

### 4.2 Proposal 里被实测推翻的四条（必列）

1. **“呈现剂量已验证”** → 初稿据整级宏准确率 63.3/60.0/51.7 断言剂量杠杆有效；t3 同事实组逐对比较为 **5 降 / 4 升 / 1 平，p=0.50**。**该断言是错的。**
2. **“推导深度不可调”** → 初稿据此列为 REJECTED；t3 发现同事实组内 `rule_operators` 从 1→2→3→4 变化而金标逐字节相同；t5 逐算子消融证明 **1,546 条规则引用中 488 条（31.6%）非承载，BAT_CREDIT/NB_COUNT/WIDE_COUNT 从未必要**。**该断言也不对**（但换来了最硬的负向发现）。
3. **“记录空间接近上限”** → 初稿据 2 万次随机抽样只得 156 个互异记录，判断 160 题近天花板；t4 用分层定向枚举得到下界 **761**。**随机抽样不能估计可达空间。**
4. **“让数据集更难”** → 最初目标；实测本设计能操纵的是**呈现难度**，而呈现难度只值 **0.56pp**；且 E4 证明模型不读证据。**该目标在本设计下不成立。**

### 4.3 站得住的部分（同样要给证据）

| 资产 | 证据 |
|---|---|
| 金标可被确定性 solver 重推 | **320/320 = 100%** |
| 记录空间打开 | 互异记录 **320/320 = 1.0**（R26.15 为 16/100） |
| 族名捷径拆掉 | 值平衡 10.39%、lift −3.54pp、置换 p=0.146 |
| 证书可机械验证 | 320/320；rule_path 只含承载算子；564 条非承载登记 |
| 双渲染隔离 | facts + record 320/320 逐字节相同 |
| 闭环流水线 | 21 门、缓存可重放、熔断、降级、ESCALATED 均有实证（t20 10/10） |
| 统计修复可复算 | E2/E3 三个数值 bug 修前/修后表（E1_E5_REPORT §8），t8 独立复算一致 |

---

## 5. 下一步该改什么（R29+ 的前提）

1. **先换测量对象**：本轮所有呈现侧操纵（D1–D4）都在一个“不读证据”的 7B 上失效。R29 的第一个门槛应是**先找到一个对顺序置换稳定、对决定性事实敏感的模型**（V0 ≥90%、flip⁺ ≥2× 地板），再谈难度。
2. **难度必须来自事实/推导本身**：本设计的 `solver_facts` 与金标两臂逐字节相同，推导是同一个；只有扩求解器（多球累计、局内状态、后续击球顺序）才能让“更难”有可操纵空间。
3. **先做人工双标**：E 阶段不执行，任何“金标可信”的主张都是发表阻断项；t24 kit 已就绪。
4. **砍掉无效机制**：D1–D4 在本轮全部 UNTESTED→REJECTED（E2/E3/E4），文档数/上下文长度/bridge depth 早已 REJECTED；R29 不应再在这些机制上投入。
5. **报告口径固定**：主指标 = 信息字段 + 逐条件先验 skill；E1 配对 CI 必须报两版；record exact 单列；E5 缺面板就撤回区分度；T1 按 span role 分层披露。

---

## 6. 证据索引与复现

| 用途 | 路径 |
|---|---|
| E1–E5 全部数字 | `eval_runs/t19_e1e5_20261112/analysis.json`、`analysis_e1/e2/e3.json` |
| E4 补充（append-only） | `eval_runs/t19_e1e5_20261112/analysis_e4_supplemental.json`、`E4_SUPPLEMENTAL.md` |
| E1/E4 原始输出 | `eval_runs/t19_e1e5_20261112/e1_raw.jsonl`（652 行）、`e4_raw.jsonl`（120 行） |
| 独立验证 | `04_verify/INDEPENDENT_VERIFICATION.md`、`verification.json`（PASS_WITH_CAVEAT） |
| J 门（T1/T2/T3/κ/C_t14/S1/J8） | `04_verify/J_GATE.md`、`J_GATE.json` |
| 闭环验证 | `04_verify/t20_closed_loop/CLOSED_LOOP_VERIFICATION.json`（10/10，19.255s） |
| 本地模型预标注 | `03_build/local/t14/REPORT.md`、`t18/REPORT.md`、`t21/REPORT_T21.md` |
| 数据集/许可/复现 | `05_release/academic_package/`（`PACKAGE_STATUS.json` = READY_WITH_BLOCKERS） |
| 论文骨架与数字登记 | `05_release/paper/`（`NUMBERS.json`） |
| 流水线门账本 | `05_pipeline/runs/live_full/gate_ledger.jsonl`（19 PASS / 2 DEGRADED） |
| 冻结链 | `preregistration.json`（v1.2.0）、`02_contract/r28_contract.json`（v1.2.0）、`02_design/protocol_freeze.json` |

复现命令（离线、0 付费）：`python 05_release/academic_package/reproduce.py --check`；`cd 05_pipeline && python verify/run_closed_loop_verification.py --config r28.toml`（t9 修复后 vanilla GBK 控制台 **10/10**）。

---

## 7. 边界声明

- 单模型（7B Q4_K_M）、单数据集、单轮实验；结论不外推到前沿模型。
- 两臂 `solver_facts` 与金标逐字节相同：E1 只能测“呈现难度”，不能测“事实/推导难度”。
- R26.15 零字节改动（165 文件 / 93,346,177 B / 聚合 `343afde4…51bd`）；主项目文件未改；0 网络、0 付费 API、未读 `.secrets`。
- 人工双标与规则文本许可仍是发表阻断项；本报告不把它们写成“已完成”。


---

## 附录 A4：R28 新实验独立审计

> 原文件：VETT_R28_NEW_EXPERIMENTS_INDEPENDENT_AUDIT_20261113.md（721 行）

# VETT-Cricket 完整基础、R26.18、R28 与 DeepTable 独立总审计报告

> 审计日期：2026-11-13（Asia/Shanghai）  
> 审计对象：R20–R26.18 项目基础、正式 Sentinel5、R28 主交付、`REVIEW_20261113` 的 H1/H2、新增 `DEEP_T2T` 实验及综合报告  
> 审计方式：只读文件、原始 JSONL 复算、脚本静态检查；本次未调用任何模型或 provider，未读取密钥，未修改候选数据、代码、既有实验或报告  
> 本报告是本次审计唯一新增产物

---

## 1. 执行摘要

### 1.1 总判决

新增实验包含真实、可复用的进展，但尚不能支持“R28 已完成科学有效的数据集难度升级”这一总主张。

| 对象 | 工程状态 | 科学证据状态 | 本次判决 |
|---|---|---|---|
| R26.15 数据候选 + R26.18 评测协议 | 候选字节未改变；一次性授权 Sentinel5 已完成 | 5 场 25 题有效，主指标 66.3333%，服从率 92% | **当前生命周期 `SENTINEL5_COMPLETE_VALID`；经验状态带 conformance warnings** |
| H1 同提示重测/换序实验 | 80 条新调用完整，40 题两遍均可解析，Qwen digest 已钉住 | 同提示稳定 95%，换序稳定仅 10%，较强支持顺序效应 | **可保留，但只证明输出顺序敏感，不证明正确性或难度提升** |
| H2 三模型面板 | 960 条记录完整、每模型 320 个唯一 item、全部 `parse_ok`/`done_reason=stop` | 三模型的逐字段差异有信息量，但未过 25pp 区分度门，且模型 digest 绑定错误 | **探索性支持；不能作为严格冻结或确认性证据** |
| DeepTable V1 | 3 模型 × 4 条件 × 18 场 = 216 条调用完整 | 任务可识别性、gold 闭合、评分器和预注册解释均存在阻断缺陷 | **`ENGINEERING_RUN_COMPLETE / SCIENTIFIC_VALIDITY_BLOCKED`** |
| 综合总报告 | 汇总范围广，保留了不少负结果 | 将证据行比例解释成 cell 难度比例，并对 DeepTable 成功程度表述过强 | **需要降级主张后才能作为对外报告** |

### 1.2 最重要的新增发现

1. **H1 是本轮最可信的新结果。**同一 40 题、同一提示、同一模型、同一 `num_predict=640` 下，P1/P2 整记录一致 38/40；只改变证据顺序后，P1/V0 仅 4/40 一致。该差距不能再主要归因于温度或普通重测噪声。
2. **H2 很可能确实运行了三个模型，但原始证据没有正确绑定三个模型。**生成请求动态读取切换后的模型 tag；然而运行器调用了带静态默认参数的 `model_info()`，导致 Qwen、Llama、Gemma 三份 JSONL 全部记录同一个 Qwen digest。模型输出和性能明显不同，故不能断言“三次都跑成 Qwen”，但也不能把现有记录当作可独立复核的三模型冻结证据。
3. **DeepTable 的核心问题不是模型太弱，而是大量目标在输入中不可观测。**C0 没有 scorecard，只给本场解说、比赛摘要和两份其他比赛的完整解说；独立宽松词面核验显示，1,363 个 gold cell 中仅 424 个（31.1%）能在本场 D0+D1 中找到，数值 cell 仅 122/968（12.6%）。低准确率混合了推理失败、信息缺失、干扰混淆与猜测，不能直接解释为“深推理难度”。
4. **DeepTable 的 `table_exact=0` 是评分器强制产生的。**提示要求模型输出 `player_of_match`，gold/评分路径却叫 `pom`；正常输出永远取不到 `pom`，因此每张表至少错一格，`table_exact` 必然为 0。原报告用它通过 G2、证明“任务成立”，该证据无效。
5. **修订 gold 与比赛结果不闭合。**M2 文案称“两分记给了错误击球手”，代码却只给最高分手加 2 分，不从错误击球手扣回；随后又增加球队总分。`result` 没有重算。在 16 场有正式胜负结果的比赛中，C1/C2 的 16/16 结果或胜负分差均与修订后总分不一致；C3 为 13/16。
6. **“98,572 个 cell 中 68% 是 L2/L3”不成立。**98,572 是 scorecard 表格 cell 数；68% 来自另一个文件中 4,080 条证据行的 L2/L3 比例。审计脚本没有把证据行映射到 cell，DeepTable gold 也没有 L1/L2/L3 标签。这两个分母不能直接相乘或互换。

---

## 2. 项目基础、版本关系与当前权威状态

### 2.1 项目目标与不可混淆的三层对象

VETT-Cricket 的目标是构建 220 场、长上下文、事实有据但不易被表面捷径解决的板球文本到结构化决策/表格数据集，用于论文研究和模型能力缺陷评测。设计目标包括强模型事实宏准确率约 65% 以下、五级难度具有可辨别梯度、金标和证据链可审计、成本与复现受控。

当前必须区分三个层级：

| 层级 | 当前权威对象 | 含义 |
|---|---|---|
| 规范与长文本基础 | R20–R24，220 场 | 数据根、长文本、整表目标、证据和规则任务的历史基础 |
| 当前高难度数据候选 | `r26_15_content_dependency_candidate_v3` | 20 场、100 题的实际候选；220 场版本只有流式扩展计划，未最终物化发布 |
| 当前评测协议 | R26.18 `canonical_set_v2` | 评测与输出归因协议；没有修改 R26.15 的文本、题目或 gold |

R28 与 DeepTable 是后续独立升级/研究分支，不能回写或替代 R26.15 + R26.18 的权威候选—协议关系，也不能把分支实验结果合并成 R26.18 正式 Sentinel5 成绩。

### 2.2 从基础根到当前候选的演进

#### R20 规范根

- 220/220 实例通过机器发布门；
- 217 个独立根，3 个精确重复一致性控制；
- 历史交付报告登记 98,447 个源单元格，其中 91,555 个可靠单元格进入评分，6,892 个冲突相关单元格保留证据但不猜测、不计分；
- 公开集登记 9,260 篇文档、274,250 条真假混合声明，约 471.5 万词；
- 单场约 10,040–33,731 词。

DeepTable 的 `audit_corpus.py` 对另一个当前 scorecard 目录得到 98,572 个 Markdown 表格 cell。98,447 与 98,572 使用的工件/计数口径不同，差 125；在没有建立同版本同口径对账前，两者均应保留来源标签，不得互换为同一个“总 cell 数”。

#### R21–R24

- R21：20 场 pilot，引入语义定位和证据链联合评测；
- R22：扩展五级难度并覆盖 220 场，形成 91,555 个整表目标和 5,500 个证据探针；
- R23/R23.1：加入规则知识、开放解释与长文本中的规则线索；
- R24：覆盖 220 场，加入 1,100 道规则题和 1,100 道开放推理题，同时保持原长文本任务。

#### R25–R26

R25 把单值抽取升级为事实、状态、反事实组成的完整决策记录，并用 countermodel 检查决定性事实。R26 增加正证据、必须排除的冲突证据、类型边、事实—证据链联合指标、角色中立 span ID、来源/句式多样化，以及匹配锚点 Latin square。

### 2.3 R26.15 当前候选的实质

R26.15 在 R26.14 基础上新增“被反事实修改的事实 → 所有受影响规则”的内容依赖边，没有改写原有事实答案：

| 项目 | 当前证据 |
|---|---:|
| pilot | 20 场、100 题、25 个情景家族 |
| 候选文件 | 165 |
| 候选字节 | 93,346,177 |
| aggregate SHA-256 | `2cb1ea2c…9417` |
| pilot 新增内容依赖边 | 324 |
| 每题内容依赖边 | 1–7 |
| 220 场流式计划 | 1,100 题、3,564 条内容依赖边，通过预检但未最终物化 |

已报告的反捷径证据包括固定角色模板恢复完整图精确率从 100% 降至 0%，以及删除、反向、改关系、单边删除和伪边添加会被专项指标识别。它说明图指标具备敏感性，但不等于外部强模型已达到目标难度。

### 2.4 R26.16–R26.18 是评测层演进，不是数据版本

#### R26.16：未知证据引用归因

形状合法但不属于当前文档的 span ID 作为语义假阳性参与评分，不再让整批其他题失去分数；畸形 ID、非法节点、缺题、截断、非法 JSON 等仍是硬失败。

#### R26.17：题目身份覆盖

`exact_target_map_v3` 把五个题目 ID 变成对象的五个必需键，解决模型重复一个合法题目 ID、遗漏其他题目的问题。`match_0220` 单场 smoke 返回 5/5 题，证明结构性覆盖问题被消除，但单场不能冒充正式五场结果。

#### R26.18：集合语义与输出服从性分轨

- `evidence_spans` 按精确 span ID 集合评分；
- `evidence_edges` 按精确三元组集合评分；
- 完全相同的重复成员规范化，不获得额外信用；
- 重复仍单独记为 nonconformant；
- 非法/截断 JSON、缺题/多题、非法字段或关系、畸形/外来节点、原始数组超限与 provider 错误仍硬失败；
- 旧 `strict_unique_v1` 历史运行不追溯转正，后验回放永远不是正式成绩。

这一演进修复的是错误归因和测量可用性，不是把数据“加难”。

### 2.5 执行前准入：历史状态

冻结 `ADMISSION.json` 的状态是：

`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`

其含义是当时本地协议、Oracle、故障注入、成本和上下文门通过，但 provider 请求为 0，未来五场仍需单独授权。主要执行前证据：

- 全仓 202/202 测试通过；
- 五场 25 题 Oracle 与故障注入通过；
- 最大上下文利用率上界 26.4562%；
- 最小 Oracle 输出余量 1.551163 倍；
- 零缓存保守费用 1.0074 元，硬上限 1.4 元；
- 当时 `execution_authorized=false`。

该状态是正确的历史准入事实，但在 2026-11-12 正式 Sentinel5 完成后，不再是当前生命周期标签。

### 2.6 正式 R26.18 Sentinel5：当前权威实测

用户以 `AUTH-R26.18-S5-20261112-01` 一次性授权了冻结的五场执行，授权已消费，不能复用。

| 轨道 | 结果 |
|---|---|
| 覆盖 | 5 场、25 题、5 个 provider 请求、0 重试，全部完成 |
| 模型 | `zai-org/GLM-5.3-Flash` |
| 费用 | 0.649936 元，低于 1.4 元硬上限 |
| token | 输入 623,549；输出 53,963；合计 677,512 |
| 硬协议 | 5/5 batches OK；无截断、验证错误、JSON repair 或 parse error |
| 服从性 | 23/25 题通过；`match_0162` 两题各有一个完全重复项 |
| 语义可评分性 | 重复项规范化后不受影响 |

主要语义结果：

| 指标 | 值 |
|---|---:|
| 决策字段宏准确率（主指标） | 66.3333% |
| L1 / L2 / L3 / L4 / L5 | 100% / 56.6667% / 63.3333% / 60% / 51.6667% |
| 信息字段准确率 | 55.1111% |
| 事实整记录 exact | 28% |
| 反事实字段准确率 | 65% |
| 反事实整记录 exact | 12% |
| 最小证据 span F1 | 45.2247% |
| 排除证据 F1 | 43.0380% |
| 类型边 F1 | 29.9264% |
| 内容依赖边 F1 | 9.2308% |
| 事实 + 完整证据链 exact | 0% |

主指标比预注册 65% 上界高 1.3333pp，被归类为 `POSSIBLY_TOO_EASY_SCREEN_ONLY`。L1 为 100% 天花板，L2→L3 反向提升 6.6666pp，四个相邻差中只有两个达到 8pp。因每级仅 5 题，这一结果是正式筛选证据，不足以直接改数据。

### 2.7 当前状态、完成度与授权边界

当前权威状态应写为：

- 生命周期：`SENTINEL5_COMPLETE_VALID`；
- 经验状态：`SENTINEL5_COMPLETE_VALID_WITH_CONFORMANCE_WARNINGS`；
- readiness checkpoint：`SENTINEL5_ANALYSIS_AND_AUDIT_COMPLETE`；
- R26.15 候选无漂移；
- 只登记假设 `HYP-R26.18-S5-001`：整体略高于 65% 可能由 L1 天花板驱动；
- 下一外部决策是是否另行授权冻结 Pilot20 来证伪该假设。

当前没有以下授权：新增 provider/费用、重试、Pilot20、第二模型、数据修改、shadow 外测、220 场高难度候选物化或发布。R28 本地实验与 DeepTable 本地模型运行也不构成这些权限。

交付包对项目完成度的保守阶段估计为 75%–80%：220 场基础和 20 场高难度 pilot 较成熟，论文级经验校准仍缺 Pilot20、第二模型、稳定置信区间、正式人工双标与发布许可。该百分比只是项目管理估计，不是统计结论。

---

## 3. 审计范围、证据和方法

### 3.1 重点文件

- `REVIEW_20261113/h1_retest.py`
- `REVIEW_20261113/h2_panel.py`
- `REVIEW_20261113/REVIEWER_JUDGMENT_AND_PLAN.md`
- `VETT_R28_DIFFICULTY_20261112/eval_runs/t19_retest_20261113/*`
- `VETT_R28_DIFFICULTY_20261112/eval_runs/t19_panel_20261113/*`
- `DEEP_T2T/PLAN_V1.md`
- `DEEP_T2T/build_deep20.py`
- `DEEP_T2T/eval_deep.py`
- `DEEP_T2T/data/{dossiers,golds}.jsonl`
- `DEEP_T2T/runs/*.jsonl`
- `DEEP_T2T/{ANALYSIS_V1,REPORT_V1}.md`
- `VETT_COMPREHENSIVE_REPORT_20261113.md`

此前已经核实、此次继续承接的 R28 证据包括：数据构建 manifest、冻结协议/修订记录、E1–E5 原始运行、pipeline、academic package 与发布材料。

### 3.2 独立复算

本次从原始文件独立检查了：

- H1：行数、唯一 `(arm,item_id)`、解析状态、模型 tag/digest、解码参数、三个配对比较；
- H2：每模型行数、item 去重、解析/结束状态、模型 tag/digest、逐字段与聚合结果；
- DeepTable：12 个运行文件的 216 行完整性、实际 match 数、每条件 gold cell 总数、POM/result 评分、修订后结果闭合、输入中 gold 的宽松词面可见性；
- 脚本：模型绑定、resume、gold 构建、评分路径、closure 检查、manifest 与报告生成链。

词面可见性审计只是一个宽松诊断，不等于语义可推导性：数字按完整数字 token 匹配，文本忽略大小写，击球手名允许去除 `(c)/(wk)` 角色后缀。即便采用这一有利于任务的口径，数值 gold 的可见率仍只有 12.6%。

---

## 4. H1：同提示重测与顺序效应

### 4.1 完整性

| 检查项 | 结果 |
|---|---:|
| 样本 | 固定 E4 40 题 |
| 新调用 | 80（P1 40 + P2 40） |
| 唯一 `(arm,item)` | 80/80 |
| `parse_ok` | 80/80 |
| 模型 | `qwen2.5:7b-instruct-q4_K_M` |
| digest | `845dbda0…b697e`，脚本显式校验 |
| 参数 | temperature 0、seed 20261112、ctx 8192、predict 640 |
| P1 与原 E1 published prompt hash | 40/40 一致 |

### 4.2 结果与可接受解释

| 比较 | 整记录一致 | 翻转率 | 解释 |
|---|---:|---:|---|
| P1 vs P2，同提示重测 | 38/40 = 95.0% | 5.0% | 当前配置下的经验重测底噪 |
| P1 vs V0，同参数但证据顺序置换 | 4/40 = 10.0% | 90.0% | 强顺序敏感性 |
| P1 vs E1，predict 640 vs 420/512 | 35/40 = 87.5% | 12.5% | 仅作 max-token 敏感性参考 |

换序翻转集中在：`total_runs` 28/40、`batter_runs` 26/40、`bowler_runs` 26/40、`ledger.BATTER` 15/40；同提示重测的各字段翻转仅 0–2。现有证据支持：**Qwen 在这 40 题上的计数/账目输出对证据顺序高度敏感，远高于普通重测波动。**

以下更强说法仍不成立：

- 不能由稳定性推出答案正确；稳定错误同样可能存在。
- 不能由 40 题推出所有 320 题或所有模型都具有同等顺序效应。
- 不能把字段分组后的“会判、不会算”当作 R28 原预注册确认性结论；该分组和叙事是在结果后形成的。
- H1 没有修复 E1 的 ITT/失败处理违规，也不能恢复原 G9 的确认性 PASS。

### 4.3 判决

H1 可作为**有边界的新增实证发现**写入内部或论文探索性分析：

> 在固定的 Qwen 模型与解码参数下，40 个样本同提示两次运行有 95% 的整记录一致率；相同样本仅置换证据顺序后，一致率降至 10%，且翻转主要集中在数值账目字段。

不得改写为“R28 更难”“模型没有推理”“所有规则字段均稳定”或“顺序效应已跨模型复现”。

---

## 5. H2：三模型面板

### 5.1 原始运行完整性

| 模型文件 | 行数 | 唯一 item | parse_bad | done 非 stop |
|---|---:|---:|---:|---:|
| Qwen 2.5 7B | 320 | 320 | 0 | 0 |
| Llama 3.1 8B | 320 | 320 | 0 | 0 |
| Gemma 2 9B | 320 | 320 | 0 | 0 |

当前文件没有重复行，因此 `h2_panel.py` 汇总器“对所有 parse_ok 行直接求平均、未先按 item 去重”的潜在 resume 风险尚未污染本次结果，但应在下一版修复。

### 5.2 复算结果

| 模型 | informative acc | record exact | law 组 | counting 组 |
|---|---:|---:|---:|---:|
| Qwen 2.5 7B | 0.5969 | 0.63% | 0.7650 | 0.5429 |
| Llama 3.1 8B | 0.6792 | 0.94% | 0.8356 | 0.6063 |
| Gemma 2 9B | 0.6337 | 1.56% | 0.8050 | 0.5491 |

模型间 informative accuracy 最大跨度为 8.23pp，低于 R28 预注册的 25pp 区分度门。因此：

- “已执行多模型面板”成立；
- “任务已显示足够模型区分度”不成立；
- 原 E5 不能改判为通过，只能由 `UNTESTED` 更新为**已测试但区分度门失败**。

law/counting 分裂在三模型上方向相近，具有研究价值，但当前只能标记为探索性。理由是字段分组并非 R28 冻结主分析，且分组本身包含选择：`NO_BALL_EXTRA`、`PENALTY` 被放入 law，`BYE/LEG_BYE` 被放入 counting；后二者三模型均等于众数基线，说明至少部分结果来自恒输出 0，而不是实际算账。

### 5.3 模型身份绑定缺陷（P0 复现性问题）

三份原始面板 JSONL 的 `model_tag` 分别是 Qwen、Llama、Gemma，但 `model_digest` 全部为：

`845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`

这正是 Qwen digest。根因链如下：

1. `h2_panel.py` 在每轮设置 `service.config.MODEL_TAG = tag`，生成函数会动态读取该值，所以实际生成请求很可能确实切换了模型；
2. 脚本用 `service.model_info(tag)` 在控制台打印正确模型信息，但没有把该信息保存进面板 manifest；
3. `run_local.run()` 内部再次调用无参数的 `service.model_info()`；
4. `service.model_info(tag=config.MODEL_TAG)` 的默认参数在函数定义时已绑定为最初的 Qwen tag，不会随之后的配置赋值改变；
5. 因此 Llama/Gemma 行继承了 Qwen digest，`h2_result.json` 又完全未保存 digest。

模型输出和准确率存在明显差异，故现有证据更符合“模型切换成功、日志身份写错”，但严格审计不能用推测替代绑定。H2 若要进入冻结结果，必须用修复后的运行器重跑，逐行或逐 run 保存正确 tag、digest、quantization、prompt hash、参数和输入清单 hash。

### 5.4 判决

H2 可以支持以下探索性表述：

> 三个本地 7–9B 模型标签对应的运行均显示规则/状态类字段整体高于若干数值账目字段；但模型间总体跨度仅 8.2pp，未达到原区分度门，且当前运行的模型 digest 记录错误，需修复绑定后复现。

不应写成“三个模型族已严格复现”“E5 已通过”“该字段分裂已预注册”或“数据集已建立模型排行榜区分力”。

---

## 6. DeepTable V1：数据与任务设计审计

### 6.1 实际实验规模

| 项目 | 报告/manifest | 实际 |
|---|---:|---:|
| 计划匹配 | 20 | 20 个目录被选中 |
| 有效比赛 | manifest 写 20 | **18**；2 场因 innings 数不等于 2 被静默跳过 |
| 条件 | 4 | 4 |
| 模型 | 3 | 3 |
| 调用 | 240 计划值 | **216 = 18×4×3** |
| dossier | 72 | 72 |
| 每条件 gold cells | 报告按 18×76=1,368 | **1,363**；17 场 76，1 场 71 |

12 个运行文件均有 18 行，216 行均为唯一 `(model,condition,match)`，全部 `json_ok`、无 error、`done_reason=stop`。这是本实验最扎实的工程成果。

### 6.2 阻断一：任务输入不足以确定目标输出

C0 dossier 包含：

- D0：场地、掷币、球队、比赛结果、POM；
- D1：本场解说；
- X1/X2：两场其他比赛的完整解说；
- 不包含生成 gold 所使用的 `scorecard.md`。

但 gold 要求精确输出两局 summary、前三击球手的 runs/balls/fours/sixes、前三投球手的 overs/runs/wickets 等大量表格值。许多值没有出现在解说中，也无法从解说唯一重建。

独立宽松词面审计：

| 类型 | 在 D0+D1 中可找到 | 总数 | 比例 |
|---|---:|---:|---:|
| 全部 gold cells | 424 | 1,363 | 31.1% |
| 数值 cells | 122 | 968 | 12.6% |
| 文本 cells | 302 | 395 | 76.5% |

排除被 D0 直接给出的 `result`/`pom` 后，C0 核心 cell 在“词面可见/不可见”两组上的模型准确率为：

| 模型 | 可见组 | 不可见组 |
|---|---:|---:|
| Gemma | 0.421 | 0.212 |
| Llama | 0.428 | 0.257 |
| Qwen | 0.372 | 0.224 |

这不是说不可见组绝对不能推导；但它明确说明 0.27–0.31 的总体准确率无法单独归因于“深层闭合推理”。现有任务把至少四种因素混在一起：

1. 信息根本未提供；
2. 信息存在但需要推导；
3. 两份整场干扰解说造成检索混淆；
4. top-3 选择及排序规则未告诉模型。

因此，G1 的“低于 0.8，所以任务不浅”没有科学解释力。一个信息不完备、无法唯一求解的任务同样会得到低分。

### 6.3 阻断二：gold 修订语义和比赛结果不闭合

`build_deep20.py` 的 M2 文案是“两分记给了错误击球手”，语义上应为同队击球手之间的转记，球队总分不变。实际代码仅执行：

- 最高分击球手 `runs += 2`；
- 没有从“错误击球手”减 2；
- 重新按 batting sum + extras 计算球队总分。

同时 M1 再增加 2 个 byes，所以 C1/C2 的第一局总分通常比 C0 增加 4，而 `result` 和 POM 仍原样复制。按修订后的两局总分、第二局 wickets 与原结果复核：

| 条件 | 有正式胜负结果的比赛 | 结果/分差不一致 |
|---|---:|---:|
| C0 | 16 | 0 |
| C1 | 16 | **16** |
| C2 | 16 | **16** |
| C3 | 16 | **13** |

两个 `No Result` 样本未纳入上述胜负闭合分母。这个问题意味着 C1/C2/C3 gold 不是完整自洽的“最终比赛表”。更严重的是，D0 直接把原始 result 提供给模型，评分器也把同一个陈旧 result 当 gold，所以 result 表面正确率 204/216，并不能证明模型完成了修订后闭合。

### 6.4 阻断三：POM 键错位使 table exact 必然为 0

提示要求输出 `player_of_match`；模型确实按此键输出。gold 却把该字段命名为 `pom`，评分器用 `get_path(pred, "pom")` 查找，因此返回 `None`。

- 现评分器：POM 0/216；
- 独立按 `player_of_match` 对 gold POM：197/216 = 91.2%；
- 因每张表至少这一格必错，`table_exact=0` 是由 schema bug 保证的，不是模型能力发现。

因此，G2 中 `table_exact=0` 的部分完全无效。现有 raw output 可以在不调用模型的情况下修正评分器并重新评分，但修正后的结果仍不能解决输入不可识别和 gold 不闭合问题。

### 6.5 评分规范还存在两类系统偏差

#### 击球手名字角色后缀

gold 从 scorecard 原样保留 `(c)`、`(wk)`，提示却只要求 `name`，没有要求角色后缀。跨 216 份输出共有 1,284 个 top-batter name 评分项：

- 原评分正确 498；
- 去除 `(c)/(wk)` 后正确 675；
- **额外恢复 177 个本应视为匹配的名字**。

这说明原始 cell accuracy 被 schema/规范差异进一步压低。

#### top bowler 的定义未写入任务

builder 按 wickets 降序、runs 升序、overs 升序选择前三投球手；提示只说 `top_bowlers`，没有给选择和 tie-break 规则。大量比赛在 wickets 上并列，边界并列时存在多个合理集合/顺序。严格位置 exact-match 会把合理答案判错。

### 6.6 “closure” 没有实现计划书中的完整闭合

计划声称检查行和、列和、extras、bowling 账、wickets 和、overs 和。实际 `closure_violations()` 每局只检查：

1. `extras == byes + leg_byes + no_balls + wides`；
2. `total - extras >= 0`；
3. `bowling_runs == total - byes - leg_byes`；
4. `run_rate == total / overs`。

它没有检查：

- batting rows 之和是否等于 total-extras；
- bowling wickets 与 innings wickets；
- overs/balls 总和；
- wickets 总量或 FOW；
- top-3 表是否足以支持任何全局闭合。

输出本来只含 top-3，缺少全队明细，因而无法完成计划书声称的完整 batting/wickets/overs 闭合。把“closure violation 接近 1”解释为模型无法完成完整账目闭合，超过了评分器实际测量范围。

### 6.7 “68% L2/L3 cells”属于分母错配

`audit_corpus.py` 分别做了两件互不连接的计数：

- 从 `scorecard.md` 的所有 Markdown 表格计算 98,572 个 cell；
- 从 `evidence_chain.md` 中匹配 4,080 条以 `| L1 |`、`| L2 |`、`| L3 |` 开头的证据行，得到 L2+L3 = 67.9%。

脚本没有 `cell_id → evidence row → level` 映射，DeepTable 的 76/71 个 gold cell 也没有 level 标签。因此下列说法均没有得到现有数据支持：

- “98,572 个 cell 中 68% 是 L2/L3”；
- “DeepTable 把语料中 68% 的 L2/L3 cell 变成评分对象”；
- “当前 1,363 个 gold cell 的 75% 是 L2/L3”。

能够保留的准确表述只有：**scorecard 中共计 98,572 个表格 cell；evidence-chain 文件中被正则识别的 4,080 条证据行有 67.9% 标为 L2/L3。二者尚未建立逐项映射。**

### 6.8 计划与执行漂移

| 计划 | 实际 | 影响 |
|---|---|---|
| 约 79 cells，约 40 个 L2/L3 cells 进入评分 | 71/76 cells 全部等权评分，无 level 标签 | 无法按推理深度分层 |
| 包含 FOW chain | 输出和 gold 均无 FOW | 计划中的链式闭合未实现 |
| C2 同一事实在两版规则下答案不同 | C1/C2 gold 完全相同，只增加旧规则和覆盖声明 | 变成 lure 实验，已偏离原文字面设计 |
| G4 不足则重做文档 | 初版分析正确判为 FAIL；最终报告在见到结果后把原门称为“口径作废” | 结果后改门，不能回溯成为确认性成功 |
| D4 做 10 题两次可靠性 | 未见 DeepTable reliability 产物 | “变化只能来自提示”无直接证据 |
| 20 场切片 | 实际 18 场便利样本 | 代表性和分母均变化 |

尤其需要注意：`temperature=0 + 固定 seed` 不等于位级确定性；同目录下 H1 已经实测同提示仍有 5% 整记录翻转。DeepTable 报告中“预测变化只能来自提示变化”的表述应撤回。

### 6.9 条件设计中的混杂

- C0 并非纯“本场 commentary only”，而是本场解说加两场完整干扰解说；
- C1 相对 C0 同时改变 gold、添加修订 memo、添加规则文档并增加上下文长度；
- C2 再增加两份规则/条件文档；
- 四个条件按固定顺序执行，没有 counterbalancing；
- 18 场来自排序后的前 20 场，不是随机或分层抽样；
- 没有人类上界、符号求解器、scorecard-oracle、无干扰基线或缺失信息基线。

所以条件差异无法唯一归因于“修订跟随”“规则冲突”或“证据必要性”。

### 6.10 复现与冻结不足

DeepTable 运行文件只记录 model tag，没有 model digest、quantization、prompt hash、dossier hash、gold hash或代码版本。`eval_deep.py` 的 resume 只按 `match_id` 跳过，既不校验已有行的 condition/model，也不验证输入和提示字节；错误或过期行也会被当作已完成。

`build_manifest.json`：

- `n_matches=20`，但实际只有 18 个 match；
- `n_cells_per_dossier=76` 只取第一条 gold，未反映 1 个 71-cell 样本；
- 只哈希 dossiers 文件，没有哈希 gold、builder、源 scorecard 或配置。

目录中未发现从原始 runs 自动生成 `analysis.json`/最终报告的独立分析脚本。现阶段“机器复算”无法由第三方从一个固定入口完整重现。

### 6.11 能保留的积极资产

DeepTable V1 并非没有价值。可保留资产包括：

- 18 场 × 4 条件 × 3 模型的原始输出齐全，无失败、无重复；
- builder 与 evaluator 代码较短，问题可以定位并修复；
- C3 已具备同一比赛的配对结构雏形；
- 实验暴露了文本到表格任务中最关键的工程问题：目标可观察性、修订闭合、字段规范、模型身份绑定；
- 这些失败结果足以指导 V2，且不需要立即扩展到 220 场。

正确结论不是“DeepTable 方向失败”，而是：**V1 成功完成了工程探路，但尚未构造出可用于科学难度结论的有效测量工具。**

---

## 7. R28 主交付的独立审计结论

### 7.1 R28 做了什么

R28 是一条不修改 R26.15 的半合成难度/测量分支。它用确定性 solver、双渲染和证书系统生成 320 个主评测题及 40 个 held-out 题，试图把“呈现难度”拆成四类机制：

| 机制 | 设计目标 |
|---|---|
| D1 | 增加事实—证据绑定跳数 |
| D2 | 引入版本化修订链并要求按生效规则回放 |
| D3 | 多源冲突和权威裁决 |
| D4 | 同构/near-miss 干扰事件 |

构建包登记 360 题、约 2,769 个文件、约 65.7MB，公开、private、audit、variants 和 held-out 分层存放。正面工程资产包括：

- 320/320 主题决策记录互异；
- 320/320 证书可由冻结 solver 重推；
- published/control 两臂的 solver facts 与 gold 保持一致，只改变呈现；
- 67 层配额、16×8 因子核、12×16 剂量阶梯与 40 held-out 的结构已落盘；
- 证书把必要算子与 `PRESENTATION_ONLY` 算子分开；
- 本地 pipeline、缓存、熔断、降级和关闭环演练有较完整证据。

R28 自己也明确披露了半合成边界、31.6% 规则引用不承载推导、人工双标未完成以及许可未闭环。这些诚实边界应保留。

### 7.2 E1–E5 的实测结论

| 实验 | 问题 | 已报告结果 | 独立审计判决 |
|---|---|---|---|
| E1 | published 是否比 control 难 | 严格 319 对：drop 0.557pp，CI 跨 0 | **没有建立更难**；且主分析不符合冻结 ITT，确认性门无效 |
| E2 | dose 0→1→2 是否单调变难 | 59.375% / 62.674% / 60.938%，斜率方向为正，CI 跨 0 | **剂量假设 REJECTED** |
| E3 | D1–D4 是否可归因 | Holm 后均不显著，H3=False | **机制归因未建立** |
| E4 | 决定性/非决定性/顺序孪生 | 原补充结果顺序稳定 5/40；三门均失败 | **解释忠实性未建立**；H1 后续确认主要是账目字段顺序敏感 |
| E5 | 多模型区分度 | 原交付时 UNTESTED | H2 后续完成三标签面板，但跨度 8.23pp < 25pp，且 digest 绑定错误；**仍未通过** |

R28 报告的核心诚实结论可保留：

- “R28 比 R26.15 更难”不成立；
- 机械证书可验证，但不能证明模型真实依赖这些证据；
- 任务区分度未建立；
- 作为能力 benchmark 的发表主张不足，更适合测量、零结果或验证装置方向。

但 R28 决策报告把 E4 的低顺序稳定进一步解释为“模型压根没在解题”，表述过强。H1 表明同提示重测稳定 95%，换序后账目字段强翻转，较准确的说法是：**模型在规则/状态字段上有一定稳定能力，但数值账目推断高度依赖顺序；这既不是完全没解题，也不是可靠完成了完整决策记录。**

### 7.3 E1 的独立 ITT 修正

冻结协议要求 320 对全部纳入，失败调用的九个信息字段按错计入，不做排除；主跑参数也应一致。实际主分析：

- 排除了一个 published 持久截断样本，使用 n=319；
- 12 条失败调用以 `num_predict=512` 重跑，而主跑为 420；
- 两臂失败结构不对称；
- 报告把严格配对 319 对作为主结果，把 ITT 降为 sensitivity。

按冻结规则使用初始 640 条调用做 ITT，control 约 59.375%，published 约 57.986%，drop 约 1.389pp，区间仍跨 0；若采用最终修复后的 320 对并把持续失败计错，drop 约 0.833pp，区间也跨 0。三种口径的实质方向一致——仍不能证明更难——但冻结主估计量与 G9 PASS 不能用 n=319 的替代分析宣称确认性合规。

另外，预注册 point-estimate 的 b/c÷320 公式天然对应二元配对事件；实际主指标却是每题九字段平均准确率。9/9 全对的 McNemar b/c 不是连续字段准确率差的同一个估计量，协议文字与实现还需统一。

### 7.4 既有工程与治理阻断项

H1/H2 与 DeepTable 新增实验没有消除以下问题：

1. **R28 raw-byte manifest 不成立。**manifest 中 2,766 个文件的 raw SHA-256 在当前磁盘上 0 个匹配，LF 归一化后 2,766/2,766 匹配；实际是换行规范化 hash，不是字节级冻结。
2. **文件计数口径不一致。**manifest 自身登记的逐文件项为 2,766；当前目录除 manifest 外实际有 2,768 个文件，总计 2,769。后生成文件是否属于冻结集合没有单一权威口径。
3. **构建绑定旧协议。**build/config/manifest 仍绑定 contract/prereg v1.1，而当前冻结文本为 v1.2。
4. **build index 指纹存在时序漂移。**早期验收冻结的 index 与 t19 实际读取的当前 index digest 不同；t19 对当前文件的 prompt/gold 哈希可自洽，但早期构建验收并未冻结同一字节对象。
5. **AMEND-002 是见结果后的门调整。**原 family-only baseline 门失败后，修订采用新的组合条件使其通过；这可以透明披露为探索性修订，不能保留原确认性地位。`verify_build.py`/验收文本仍把 REQ3 描述成“informative-field accuracy ≤40%”，却用修订后的组合指标判 PASS，名称与实测不一致。
6. **E1 主分析违反冻结 ITT。**方向上仍未发现 R28 更难，但主效应和 G9 的确认性判定无效。
7. **E4 原设计的 random-floor 门不可达。**阈值要求 `flip+ ≥ 2×0.875 = 1.75`，而比例最大为 1。
8. **pipeline 有完整性缺陷。**twin check 比较对象自身；resume 对缺失 artifact 只记录“recomputed”仍继续跳过；run_id/path/clean 边界不足。
9. **academic package 的隐私/复现边界冲突。**复现脚本直接读取 private/heldout gold；若交付完整根目录则 heldout 泄露，若只给公开文件则脚本无法复现；heldout 还可能由公开生成器、配置与 seed 重建。评分器还返回逐字段分数和 error item ID，长期可被用作 held-out oracle。
10. **发布仍有人审与许可阻断。**人工双标尚未完成，MCC 规则文本许可未解决；发布包含 `__pycache__/*.pyc` 也应清理。

H1 只加强“顺序敏感性”这一局部解释；H2 只补充探索性多模型字段画像；DeepTable 是独立 V1 pilot。三者都不能把 R28 总状态升级为可公开发布或确认性通过。

---

## 8. 现有报告中可保留、需降级和应撤回的主张

### 8.1 可保留

- 220 场底层语料目录存在，scorecard 表格审计合计 98,572 cells；
- H1 的 40 题同提示 95% 稳定、换序 10% 稳定；
- H2 的 960 条调用文件完整，三标签结果的总体跨度约 8.2pp；
- DeepTable 有 216 条完整本地运行，三模型都能稳定输出 JSON；
- R28 没有证明“比 R26.15 更难”，因子操纵和解释忠实性主张应保持克制；
- 人工双标和许可仍是发布阻断项。

### 8.2 必须降级为探索性

- “law learned / accounting not learned”的字段分裂；
- H2 的跨模型复现；
- DeepTable 中修订、证据删除和版本 lure 的任何行为解释；
- 逐字段显著性结果，直至固定字段家族、报告效应量/置信区间并处理多重比较。

### 8.3 应撤回或重写

- “98,572 cells 中 68% 是 L2/L3”；
- “DeepTable 已把 68% L2/L3 cell 变成评分对象”；
- “C0 低分证明任务不是浅层任务”；
- “table exact=0/closure≈1 证明任务成立”；
- “temperature=0 后预测变化只能来自提示变化”；
- “POM/result 只有约随机水平”——POM 是键错误，result 又被 D0 直接泄漏；
- “G4 口径作废后可视为通过”——原门应保留 FAIL，新 lure 指标只能另立后续预注册。

---

## 9. 完整修复与升级路线

### 阶段 A：先修测量，不调用模型

目标：用现有 raw output 生成一份诚实的 V1 corrected audit，不改变原始文件。

1. 新建版本化 scorer，而不是覆盖 V1：
   - `pom ↔ player_of_match` 对齐；
   - 名字规范化去除 `(c)/(wk)`；
   - 明确定义 top-bowler 选择与并列评分（最好按集合而非位置）；
   - 对 71/76 cell 分母逐条计算，不写死 76。
2. 用现有 216 条 raw output 重算 corrected metrics；原指标保留并标记 superseded，禁止静默替换。
3. 单独列出 `answerable / not-observed / derivable / directly-present`，不可把未提供信息的 cell 当推理错误。
4. 对现有 gold 做全量一致性检查：球队总分、extras、batting sum、bowling runs、run rate、wickets、result margin、POM、top-k。
5. 输出机器可读 `V1_CORRECTED_AUDIT.json` 与单一生成脚本；所有输入和输出 raw-byte SHA-256 入 manifest。

阶段 A 的结果仍然只是“纠正 V1 读数”，不能把 V1 变成确认性实验。

### 阶段 B：重新定义可识别的 DeepTable V2

必须先二选一，不可继续混用：

#### 路线 B1：完整重建任务

如果要求输出完整或准完整 scorecard，则输入必须提供足以唯一恢复所有评分 cell 的事件账本/完整球级记录。每个 gold cell 都要有 provenance：来源事件、公式、依赖 cell、规则版本和闭合证书。

#### 路线 B2：证据受限纠错任务

如果输入继续只有 commentary/memos，则只评分由这些输入可以唯一推出的 cell；不可推出的字段必须允许 `UNKNOWN/ABSTAIN`，并单独测选择性准确率和覆盖率。

V2 条件建议：

- C0：本场材料，无干扰文档；
- C0-D：在完全相同 gold 上单独加入干扰文档，测干扰鲁棒性；
- C1：基于自洽 base table 的真正转记/补录，所有下游字段和 result 同步更新；
- C2：事先确定是“版本决定 gold”还是“旧版 lure”。若前者，改变生效版本并使目标 cell 真正改变；若后者，gold 不变并预注册 lure 命中率；
- C3：删除唯一决定性证据后，gold 变为 `ABSTAIN`，而不是要求模型猜回原值。

M2 若是“错记给另一击球手”，必须指定来源和目标击球手，执行 `A+2, B-2, team total unchanged`；若是漏记，应把文案改为“漏计 2 分”，并同步结果和分差。

### 阶段 C：建立正控、上界和完整 verifier

在再跑模型之前必须通过：

1. **符号求解器正控**：从 V2 输入机械恢复 gold，cell exact 100%；
2. **scorecard oracle 正控**：提供最终 scorecard 后，schema/scorer 应接近 100%；
3. **人类上界**：至少双人独立完成，报告 exact、分歧和耗时；
4. **缺失信息负控**：删掉关键证据后，正确行为应是 abstain，而不是随机数值；
5. **完整 closure verifier**：检查 batting sum、extras、bowling runs、wickets、overs/balls、result margin 及跨字段依赖；
6. **schema contract tests**：提示键、gold 键、parser 键、scorer 路径逐字段一一对应；
7. **provenance coverage**：100% 评分 cell 都有来源或推导证书。

如果正控无法达到接近 100%，禁止用模型低分声称任务难。

### 阶段 D：重新预注册小样本 pilot

1. 从 220 场按比赛类型、长度、结果类型、字段稀有度分层抽样，不再取排序前 20；
2. 先固定 20–30 场；所有条件采用同一场的严格配对结构；
3. 条件顺序随机化或 counterbalance；
4. 预注册主指标、字段家族、排除规则、失败处理、模型版本、token 上限、重复次数和多重比较；
5. 主指标优先使用 match-level paired effect 与 bootstrap CI，而不是只给 pooled micro average；
6. G2 不得再以“模型失败”为成功条件；门应包含正控通过、人类可解、模型非地板、条件效应方向和可靠性；
7. 任何见结果后的新指标进入 amendment，并明确降级为探索性，不覆盖原门。

### 阶段 E：修复运行与身份冻结

每个 run 必须保存：

- model tag、真实 digest、量化、服务版本；
- prompt bytes/hash、dossier/gold/代码/配置 hash；
- temperature、seed、ctx、predict、停止原因；
- run_id、开始/结束时间、机器环境；
- `(model,condition,match,prompt_hash)` 唯一键。

resume 只在上述唯一键和 artifact hash 全部一致时跳过；摘要器必须先按唯一键去重并对冲突行 fail closed。

H2 运行器应显式调用 `model_info(tag)`，并把返回值传入每条记录及 run manifest。修复后至少复跑一个小型身份 smoke test，再决定是否重跑全部 960 条。

### 阶段 F：扩展与发布

只有 V2 小样本通过下列准入门，才考虑扩展到 220 场：

| 门 | 最低要求 |
|---|---|
| 可识别性 | 100% 评分 cell 有 provenance；不可推出项显式 abstain |
| gold 闭合 | 全部机器约束 100% 通过，result/POM 与修订后表一致 |
| schema | contract tests 100% 通过，正控 table exact 接近 100% |
| 人类上界 | 双人可稳定完成，分歧有仲裁 |
| 非地板性 | 至少一个受控 baseline 明显高于随机/众数且低于饱和 |
| 可靠性 | 固定 prompt 重测率和条件效应均报告 CI；条件效应显著高于底噪 |
| 模型身份 | 每条记录 digest 正确且与 manifest 一致 |
| 统计 | 配对、按 match 聚类/自举、多重比较事先固定 |
| 冻结 | raw-byte manifest 全匹配，协议/构建版本一致 |
| 治理 | 人审、许可、heldout 与公开包边界全部解决 |

未通过时只迭代 pilot，不生成 220 场 DeepTable，不宣称发布就绪。

---

## 10. 问题优先级与处置表

| 优先级 | 问题 | 当前影响 | 处理 |
|---|---|---|---|
| P0 | DeepTable 输入无法唯一决定多数 gold | 低分不可解释 | 重定义任务/限制评分目标 |
| P0 | `pom`/`player_of_match` 键错位 | table exact 必为 0 | 版本化修复 scorer，重算现有 raw |
| P0 | 修订后 result/gold 不闭合 | gold 错误 | 修订语义重做，完整闭合验证 |
| P0 | H2 三模型 digest 全写成 Qwen | 模型身份不可冻结 | 修运行器并复跑身份受控面板 |
| P0 | 68% 证据行被写成 68% cells | 核心难度依据失真 | 建立逐 cell provenance 后再统计 |
| P1 | closure verifier 不完整 | 指标名与测量不一致 | 实现完整账目闭合 |
| P1 | C2/G4 结果后改口径 | 确认性失效 | 原门保留 FAIL，新门另预注册 |
| P1 | 18/20 与 1,363/1,368 分母漂移 | 报告数字错误 | manifest 从实际产物计算并校验 |
| P1 | top-k/角色后缀未规范 | 系统性误判 | 固定任务规范与集合评分 |
| P1 | 无正控/人类上界 | 无法区分难与不可解 | 阶段 C 先完成 |
| P1 | R28 E1 ITT、manifest、版本绑定 | 原确认性与发布仍受阻 | 保持阻断状态，单独修复 |
| P2 | convenience sample、固定顺序 | 外推和因果解释弱 | 分层抽样、随机化/counterbalance |
| P2 | resume/分析生成链不冻结 | 复现脆弱 | 唯一键、hash、单入口分析 |

---

## 11. 最终结论

这轮新增实验最有价值的成果不是证明“数据集已经更难”，而是把三个此前混在一起的问题拆开了：

1. H1 显示某些账目字段确有强烈的顺序敏感性；
2. H2 显示逐字段画像可能比单一平均准确率更有研究价值，但模型身份和预注册边界必须修复；
3. DeepTable V1 证明了多文档表格 pilot 的工程链可以跑通，同时也证明“低模型分数”在缺少可观察性、gold 闭合与正确评分器时没有难度解释力。

因此，当前最准确的项目状态是：

> **R26.15 仍是未改字节的当前数据候选，R26.18 仍是当前评测协议；正式 Sentinel5 已完成，因此当前生命周期是 `SENTINEL5_COMPLETE_VALID`，并带有输出服从性告警。该五场结果略高于目标上界且样本很小，只授权登记 L1 天花板假设，不授权改数据。R28 的负结果和局部诊断有价值，但确认性难度升级未成立；H1 可作为有限的新发现，H2 需修复模型身份绑定后复现；DeepTable V1 完成工程试跑但科学有效性被阻断。下一步应分别推进：R26.18 仅在新授权下做冻结 Pilot20；DeepTable 先修测量、gold 和可识别性，再做小型预注册 V2；不得自动扩展、改候选或升级发布状态。**



---

## 附录 A5：DeepTable V1 计划

> 原文件：DEEP_T2T/PLAN_V1.md（98 行）

# DeepTable：深度文本转表格 V1（2026-11-13）

> 合并对象：220 场记分卡语料（`Self-cricket-clean_text_scorecard_v1_220_matches`）
> × R28 机制层（版本化规则、冲突裁决、证据必要性、证书）。
> 目标口径：ACL/EMNLP Resource & Evaluation。周期：1 周最小可行切片。预算：¥0。

## 0. 一句话

把 220 场的“整场表”从**抄写任务**改造成**约束满足任务**：
输入一份约 25KB 的卷宗（解说 + 事件级修订备忘 + 版本化规则 + 干扰文档），
输出约 40 个**必须被推导**的 cell；每个 cell 有证据链/证书。

## 1. 审计事实（`corpus_audit.json`）

| 项 | 值 |
|---|---:|
| 场数 | 220 |
| 表格 cell 总数 | **98,572** |
| 每场平均 cell | **448.1** |
| batting / partnership / bowling / FOW / summary | 33,908 / 24,563 / 20,992 / 9,837 / 9,260 |
| evidence chain L1 / L2 / L3 | 32.1% / **40.9%** / **27.0%** |
| 文本均值 | commentary 6.4 KB、scorecard 5.2 KB、evidence 2.5 KB |

**关键读法**：语料本身不浅——68% 的证据目标是 L2/L3（闭合/综合），
浅的是“当前任务只问 L1 直取”。深度不是再造数据，是**把评分对象移到 L2/L3 的 cell 上**。

## 2. 三个硬约束（设计必须绕开）

1. **220 源只有局级聚合，没有逐球事实**（数据卡 B1）。不能在 220 场上直接注入 R28 单球；
   合并只能发生在“表格 cell + 事件级修订”这一层。
2. **本地 8K 上下文**：卷宗 ≤ ~25KB（约 6.5K token），输出 ≤ ~1K token。
   65KB 需要 32K/cloud，不在本周范围。
3. **1 周 + 只有作者 1 人**：本周不做人工双标；这是 feasibility 切片，不是最终论文。

## 3. 任务定义

**输入（~25KB 卷宗）**
- 解说原文（6.4KB，叙事）
- 3–5 条**事件级**修订备忘：写“某球发生了什么”，不写最终数字
- 2 份规则摘录（v2025 / v2026，其中一份被取代）
- 2 份干扰文档（另一场的数据）

**输出（紧凑记分卡表，~40 cells）**
- 两局 innings summary：total / extras / byes / leg-byes / no-balls / wides / RR / max partnership（16）
- 每局 top-3 batters ×（R, B, 4s, 6s）（24）
- 每局 top-3 bowlers ×（O, M, R, W）（24）
- FOW chain（10 + 5）（15）
（约 79 cells；实际进入评分的 ~40 个是 L2/L3 依赖 cell）

**cell 构成**
- 25% L1：直取（抄对即可）
- 50% L2：闭合（行和、列和、extras、bowling 账、wickets 和、overs 和）
- 25% L3：版本/跨文档（哪条规则生效、哪份修订在force、干扰文档是否被误用）

## 4. 四个条件

| 条件 | 操纵 | 回答 |
|---|---|---|
| **C0** | 只有解说 | 浅层基线：模型能抄多少 |
| **C1** | + 事件级修订备忘 | 修订后能否重算，而不是只读最后一条 |
| **C2** | + 规则版本冲突 | 同一事实在两版规则下答案不同，考“哪条生效” |
| **C3** | + 删一条决定性文档 | 证据必要性：答案必须变/必须弃权 |

## 5. 指标

- `cell_exact`（按 cell 类型分组）
- `table_exact`（整表全对）
- `closure_violation`（行和≠总、extras 和≠总、bowling 账≠总−byes/leg-byes、wickets 和≠10）
- `copy_rate`（cell 等于文中直接出现的数字 → 浅层抄写）
- `derivation_rate`（L2 cell 正确率）
- `version_sensitivity`（C2 vs C1 的 cell 变化率）
- `flip_rate`（C3 下答案改变率 = 证据必要性）

## 6. 预注册门（本周切片）

| 门 | 条件 | 不过怎么办 |
|---|---|---|
| G1 | C0 的 `cell_exact` > 0.80 | 太浅，加修订/冲突 |
| G2 | C1 的 `table_exact` = 0 且 `closure_violation` > 0.50 | 任务成立，继续 |
| G3 | 3 个模型都 `parse_fail` | 换输出 schema（JSON/grammar） |
| G4 | C2 的 `version_sensitivity` < 0.10 | 版本冲突没生效，重做文档 |

## 7. 一周排期

| 天 | 做什么 | 产出 |
|---|---|---|
| D1 | 20 场 builder：解析 scorecard → 选 cell → 注入修订 → 渲染卷宗 | `build_deep20.py` + 20 卷宗 |
| D2 | 证书/金标重算 + 泄漏筛查 | `gold/` + `CERT.json` |
| D3 | eval harness + 3 模型 × 4 条件（240 次） | `runs/` + 首张表 |
| D4 | 可靠性：10 题重复 2 次；C3 必要性 | `reliability.json` |
| D5 | 1 页 memo + go/no-go + 论文骨架 | `MEMO.md` |

## 8. 不做什么

- 不物化 220 进 R28；不合并成一篇 8 页。
- 不做 65KB/云端；本周只做 25KB 本地切片。
- 不做人工双标；论文必须写“作者自标/未独立验证”。
- 不在本周追“更难”的话术；只报读数。


---

## 附录 A6：DeepTable V1 首轮分析

> 原文件：DEEP_T2T/ANALYSIS_V1.md（123 行）

# DeepTable V1 — 首轮全量评测分析（2026-11-13）

> 数据来源：`DEEP_T2T/runs/*.jsonl`（216 行）+ `data/golds.jsonl`；机器读数，无手工填写。
> 评测矩阵：3 个本地模型 × 4 条件 × 18 场 = 216 次，全部本地 ollama，零付费、零外网。
> 生成物：`analysis.json`（本文件的机器版）。

## 0. 执行状态

`bash-c0513adb23da412a` exit 0，216/216 行齐全，`results.json` 已由全量重写。

## 1. 主表（cell_exact / table_exact / closure）

| 模型 | 条件 | n | cell_exact | table_exact | closure 违规率 | 违规数均值(满 8) |
|---|---|---:|---:|---:|---:|---:|
| gemma2:9b | C0 | 18 | 0.2788 | 0.00 | 1.00 | 2.17 |
| gemma2:9b | C1 | 18 | 0.2986 | 0.00 | 1.00 | 2.11 |
| gemma2:9b | C2 | 18 | 0.2905 | 0.00 | 1.00 | 2.11 |
| gemma2:9b | C3 | 18 | 0.2920 | 0.00 | 1.00 | 2.11 |
| llama3.1:8b | C0 | 18 | 0.3125 | 0.00 | 1.00 | 2 |
| llama3.1:8b | C1 | 18 | 0.3067 | 0.00 | 1.00 | 2.17 |
| llama3.1:8b | C2 | 18 | 0.3067 | 0.00 | 1.00 | 2.39 |
| llama3.1:8b | C3 | 18 | 0.2847 | 0.00 | 1.00 | 2.17 |
| qwen2.5:7b-instruct-q4_K_M | C0 | 18 | 0.2722 | 0.00 | 1.00 | 3.72 |
| qwen2.5:7b-instruct-q4_K_M | C1 | 18 | 0.2340 | 0.00 | 1.00 | 3.61 |
| qwen2.5:7b-instruct-q4_K_M | C2 | 18 | 0.2458 | 0.00 | 0.94 | 3.56 |
| qwen2.5:7b-instruct-q4_K_M | C3 | 18 | 0.2465 | 0.00 | 1.00 | 3.11 |

**整表全对：0 / 216。** 最好单场 0.526（gemma2:9b / match_0001 / C0）。

## 2. 按 cell 族拆解（cell_exact）

| 模型 | 条件 | 局汇总 | 击球手 | 投球手 | match(pom/result) |
|---|---|---:|---:|---:|---:|
| gemma2:9b | C0 | 0.297 | 0.252 | 0.280 | 0.472 |
| gemma2:9b | C1 | 0.286 | 0.295 | 0.299 | 0.472 |
| gemma2:9b | C2 | 0.272 | 0.299 | 0.280 | 0.472 |
| gemma2:9b | C3 | 0.300 | 0.286 | 0.278 | 0.472 |
| llama3.1:8b | C0 | 0.381 | 0.277 | 0.285 | 0.500 |
| llama3.1:8b | C1 | 0.275 | 0.314 | 0.308 | 0.500 |
| llama3.1:8b | C2 | 0.272 | 0.320 | 0.303 | 0.500 |
| llama3.1:8b | C3 | 0.278 | 0.267 | 0.294 | 0.500 |
| qwen2.5:7b-instruct-q4_K_M | C0 | 0.308 | 0.267 | 0.234 | 0.444 |
| qwen2.5:7b-instruct-q4_K_M | C1 | 0.192 | 0.273 | 0.204 | 0.444 |
| qwen2.5:7b-instruct-q4_K_M | C2 | 0.197 | 0.277 | 0.232 | 0.444 |
| qwen2.5:7b-instruct-q4_K_M | C3 | 0.214 | 0.284 | 0.211 | 0.444 |

三维模型在局汇总/击球/投球三族全部落在 0.19–0.38，只有 2 个 cell 的 `pom`/`result` 有 0.44–0.50（二分类运气成分高）。

## 3. 行为指标

| 模型 | 条件 | 数值 cell | copy_rate |
|---|---|---:|---:|
| gemma2:9b | C0 | 1062 | 0.702 |
| gemma2:9b | C1 | 1083 | 0.721 |
| gemma2:9b | C2 | 1079 | 0.713 |
| gemma2:9b | C3 | 1079 | 0.713 |
| llama3.1:8b | C0 | 1086 | 0.690 |
| llama3.1:8b | C1 | 1095 | 0.751 |
| llama3.1:8b | C2 | 1091 | 0.755 |
| llama3.1:8b | C3 | 1074 | 0.708 |
| qwen2.5:7b-instruct-q4_K_M | C0 | 1112 | 0.710 |
| qwen2.5:7b-instruct-q4_K_M | C1 | 1112 | 0.701 |
| qwen2.5:7b-instruct-q4_K_M | C2 | 1112 | 0.719 |
| qwen2.5:7b-instruct-q4_K_M | C3 | 1112 | 0.692 |

copy_rate 口径：预测出的数值在卷宗全文（含规则/干扰文档）中逐字出现。约 0.69–0.76 的数值预测是“原文里的某个数”，但 cell_exact 只有 0.23–0.31 —— 说明模型大量**从文中抄错数**，而不是老实闭合推导。

## 4. 条件操纵是否真的成立（关键）

| 比较 | 金标变化 cell 数 | 判定 |
|---|---:|---|
| C0 → C1（事件级修订） | 145 / 18 场（8 场/场） | 操纵成立 |
| C1 → C2（规则版本冲突） | **0 / 1368** | **操纵失败：金标完全没变** |
| C1 → C3（删决定性证据） | 72（4 场/场） | 操纵成立 |

### 4.1 修订跟随（C0→C1 的 145 个修订 cell）

| 模型 | 修订 cell | C0 时保留旧值率 | C1 时按新金标正确率 | 同模型 C1 整体 |
|---|---:|---:|---:|---:|
| gemma2:9b | 145 | 0.269 | 0.193 | 0.299 |
| llama3.1:8b | 145 | 0.352 | 0.152 | 0.307 |
| qwen2.5:7b-instruct-q4_K_M | 145 | 0.324 | 0.145 | 0.234 |

给了修订备忘（C1）后，模型在“被修订的 cell”上正确率只有 0.145–0.193，**低于自己的整体正确率**——修订不但没被跟上，还因为多了一份文档而更乱了。

### 4.2 证据必要性（C3 的 72 个变化 cell）

| 模型 | C1 在这些 cell 上 | C3 在这些 cell 上 | C1→C3 预测翻转率（全表） |
|---|---:|---:|---:|
| gemma2:9b | 0.306 | 0.250 | 0.264 |
| llama3.1:8b | 0.250 | 0.194 | 0.332 |
| qwen2.5:7b-instruct-q4_K_M | 0.264 | 0.306 | 0.346 |

删掉决定性文档后，模型在金标确实变化的 cell 上正确率 0.19–0.31，并没有系统性优于 C1；全表 26–35% 的预测发生翻转，更像采样噪声而非“识别到证据缺失”。

## 5. 预注册门判定

| 门 | 条件 | 读数 | 判定 |
|---|---|---|---|
| G1 | C0 cell_exact > 0.80 则太浅 | 最高 0.3125（llama3.1:8b） | **PASS**（任务不浅） |
| G2 | C1 table_exact = 0 且 closure > 0.50 | table_exact 0；closure 1.00 | **PASS**（任务成立） |
| G3 | 三个模型全 parse_fail | json_ok 1.000 | NOT_TRIGGERED |
| G4 | C2 version_sensitivity < 0.10 则重做文档 | 金标变化 0/1368（预测翻转 0.18–0.24 只是噪声） | **FAIL → 重做 C2** |

## 6. 结论（可直接写进 memo 的句子）

1. **任务不浅**：即使 C0（只有解说），三个 7–9B 模型 cell_exact 只有 0.27–0.31，整表全对 0/216，closure 违规率 1.00。"抄表"已经不能解决这张表。
2. **闭合推导是主要失败面**：局汇总/击球/投球三族全在 0.19–0.38；模型能把数值从文中取出，但算不对账（extras、bowling_runs、run_rate、total）。
3. **C2（规则版本冲突）当前无效**：金标一行没变，等于给模型加了一份无关文档。C2 的读数不能作为"版本敏感性"证据，必须重建文档后重跑。
4. **修订跟随不成立**：C1 的 145 个修订 cell 上正确率反而低于整体，说明"事件级修订"这一机制对 7–9B 模型没有形成可用信号。

## 7. 局限（必须与结果同时出现）

- 18 场单切片、每格 18 次，置信区间宽；未做 10 题重复的可靠性（D4 未做）。
- 本地 7–9B 量化模型，不代表云端强模型；无人工双标，金标为规则重算，非独立标注。
- copy_rate 是"数值在文中出现"的弱证据，不等于"抄对"；不应用于论文主张。
- C2 已判无效，本报告中 C2 列只作诊断，不作结论。

## 8. 下一步（按优先级）

1. **重建 C2 文档**：让"两版规则"在**同一事实**上给出两个不同金标（当前 builder 的版本冲突没进入金标），再重跑 C2（3 模型 × 18 = 54 次，约 25–35 分钟）。
2. **D4 可靠性**：抽 10 题重复 2 次，估 temperature 噪声，区分"翻转"与"噪声"。
3. **D5 memo**：按当前 G1/G2/G3 通过、G4 失败，写 1 页 go/no-go：可 go（切片成立），但 C2 与修订跟随两处必须先修，否则论文只能报 C0/C1/C3。


---

## 附录 A7：DeepTable V1 首轮报告

> 原文件：DEEP_T2T/REPORT_V1.md（231 行）

# DeepTable V1 首轮全量评测报告

**日期**：2026-11-13　**运行根**：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\DEEP_T2T`
**数据来源**：`runs/*.jsonl`（216 行）、`data/golds.jsonl`、`data/dossiers.jsonl`；本报告所有数字均由脚本从上述文件重算，见 `analysis.json`。

---

## 0. 摘要

1. **首轮评测已完成**：3 个本地模型 × 4 条件 × 18 场 = **216 次**，`json_ok` 全程 1.000，无解析失败，`exit 0`。
2. **任务不浅**：即使最弱的 C0（只给解说），cell 正确率也只有 0.272–0.313，**整表全对 0/216**。
3. **失败面是“闭合推导”而不是“抽取”**：约 70% 的数值预测能在原文找到出处，但只有 ~27% 落在正确 cell 上；closure 违规率接近 100%。
4. **预注册门 G1/G2 通过，G3 未触发，G4 口径作废**：C2 的“规则版本冲突”按设计不改变金标（在效规则已在卷宗内声明），原门的判据与设计不匹配。
5. **当前状态**：切片可行性成立，但有两个必须先修的点——C2 在该能力水平上无信号（bowling_runs 正确率 0–3%）、C1 的修订跟随不成立（修订 cell 正确率 0.145–0.193，低于整体）。

---

## 1. 背景：为什么有这条新线

R28（难度/可解释性）已收尾，判决为 `DIRECTION_ONLY + DEGRADED`、`harder_claim_permitted = False`——即**不得声称“更难”**。R28 报告给出的唯一前进路径是：**让难度来自事实与推导本身，而不是呈现方式**。

DeepTable V1 就是这条路径的最小可行切片：把“文本转表格”从**抄写任务**改造成**约束满足任务**——输入一份约 19KB 的卷宗（解说 + 事件级修订备忘 + 版本化规则 + 干扰文档），输出 76 个必须被推导的 cell，并允许用 closure（账目闭合）机械判错。

对应的发表口径：ACL/EMNLP Resource & Evaluation；硬约束：**零付费 API、零外网、不改动 R26.15 任何字节、不读 private/、不改冻结 packet**。本实验全部使用本机 ollama，成本 ¥0。

## 2. 数据与任务

### 2.1 语料审计（220 场）

| 项 | 值 |
|---|---:|
| 场数 | 220 |
| 表格 cell 总数 | 98,572 |
| 每场平均 cell | 448.1 |
| 证据层级 L1 / L2 / L3 | 32.1% / 40.9% / 27.0% |
| 文本均值（解说 / 记分卡 / 证据） | 6.4 / 5.2 / 2.5 KB |

读法：语料本身 68% 的证据目标在 L2/L3（闭合/综合），**浅的是“当前任务只问 L1 直取”**，所以深度不需要新造数据，只需要把评分对象移到 L2/L3 的 cell 上。

### 2.2 本次切片（18 场）

- 构建目标 20 场，实际进入评测 **18 场**：`match_0004`、`match_0011` 因记分卡解析出的 innings 数不等于 2 被 builder 跳过（`build_deep20.py` 第 308–309 行）。
- 每份卷宗 4 / 6 / 8 篇文档（C0/C1/C3/C2），平均输入 19265 字节（最小 15.9KB，最大 23.0KB），另有 2 份他场干扰文档。
- 输出 **76 个 cell**：2 局 ×（10 个汇总字段 + 3 击球手 × 5 字段 + 3 投球手 × 4 字段）+ `result` + `pom`。
- 构建清单 SHA256：`9dd7b31df5f6ed7ebfe284e6d519d426e7db9c748ee2e732c98903afe253378c`。

## 3. 四个条件的设计与操纵强度

| 条件 | 操纵 | 文档数 | 设计意图 | 金标实际变化 |
|---|---|---:|---|---:|
| C0 | 只有解说 + 设定 | 4 | 浅层基线 | — |
| C1 | + 2 条事件级修订备忘（M1 补给 byes、M2 修最高分 +2） | 6 | 修订后能否重算，而不是读旧数 | 145 cells（8/场） |
| C2 | + 在效规则 2026 + 被取代规则 2025（byes 计入投手）+ 冲突声明 | 8 | 两版规则答案不同，考“哪条生效” | **0（设计使然）** |
| C3 | 删掉 M2 备忘 | 6 | 证据必要性：该 cell 必须回到原值 | 72 cells（4/场） |

**关于 C2 的辨析（本报告修正前一轮口头结论）**：C2 的金标与 C1 完全相同，**不是 builder 的疏忽，而是设计本身**——卷宗里 D5 明确声明“2026 版在效并取代 2025 版”，所以正确答案仍按 2026 规则计算；2025 规则是**诱饵**，模型若误用，`bowling_runs` 会变成 `total − leg_byes`（与正确值相差 byes）。因此 C2 考察的是“会不会被失效规则带偏”，而不是“金标会变”。这也意味着预注册门 G4 用“金标变化率”作判据是**口径错误**，需要用陷阱命中率替代（见 §7）。

## 4. 评测协议

| 项 | 值 |
|---|---|
| 解码 | `temperature=0`、固定 `seed=20261112`（确定性解码） |
| 上下文 / 输出上限 | `num_ctx=8192` / `num_predict=900` |
| 模型 | `qwen2.5:7b-instruct-q4_K_M`、`llama3.1:8b`、`gemma2:9b`（均为本机 ollama） |
| 采样 | 每格 18 场单次；按 `match_id` 去重，可断点续跑 |
| 总调用 | 216 次（3 × 4 × 18） |
| 计费 | ¥0（本机 GPU，无云端） |
| 墙钟 | 12:41 启动 → 14:16 结束，约 **95 分钟**（gemma2:9b 最慢，约 60 s/次） |

## 5. 执行记录

| 时间 | 事件 |
|---|---|
| 11:07–11:17 | 首轮（旧会话）跑完 qwen 的 C0/C1/C2 各 18 场 |
| 12:32–12:33 | 旧会话启动续跑；**12:33:18 因会话 teardown 被终止**（exit 1），C3 停在 4 行 |
| 12:41 | 本会话重启为 `bash-c0513adb23da412a`，从 C3 第 5 行续跑 |
| 13:43 | 进度 184/216（gemma 的 C2 进行中） |
| 14:16 | **216/216 完成，exit 0**；`results.json` 由全量重写 |

## 6. 结果

### 6.1 主表

| 模型 | 条件 | n | cell_exact | table_exact | closure 违规率 | 违规均值(/8) |
|---|---|---:|---:|---:|---:|---:|
| gemma2:9b | C0 | 18 | 0.2788 | 0.00 | 1.00 | 2.17 |
| gemma2:9b | C1 | 18 | 0.2986 | 0.00 | 1.00 | 2.11 |
| gemma2:9b | C2 | 18 | 0.2905 | 0.00 | 1.00 | 2.11 |
| gemma2:9b | C3 | 18 | 0.2920 | 0.00 | 1.00 | 2.11 |
| llama3.1:8b | C0 | 18 | 0.3125 | 0.00 | 1.00 | 2.00 |
| llama3.1:8b | C1 | 18 | 0.3067 | 0.00 | 1.00 | 2.17 |
| llama3.1:8b | C2 | 18 | 0.3067 | 0.00 | 1.00 | 2.39 |
| llama3.1:8b | C3 | 18 | 0.2847 | 0.00 | 1.00 | 2.17 |
| qwen2.5:7b-instruct-q4_K_M | C0 | 18 | 0.2722 | 0.00 | 1.00 | 3.72 |
| qwen2.5:7b-instruct-q4_K_M | C1 | 18 | 0.2340 | 0.00 | 1.00 | 3.61 |
| qwen2.5:7b-instruct-q4_K_M | C2 | 18 | 0.2458 | 0.00 | 0.94 | 3.56 |
| qwen2.5:7b-instruct-q4_K_M | C3 | 18 | 0.2465 | 0.00 | 1.00 | 3.11 |

按模型平均：gemma2 0.2900；llama3.1 0.3026；qwen2.5 0.2496。整表全对 **0 / 216**。

### 6.2 按 cell 族

| 模型 | 条件 | 局汇总 | 击球手 | 投球手 | match(pom/result) |
|---|---|---:|---:|---:|---:|
| gemma2:9b | C0 | 0.297 | 0.252 | 0.280 | 0.472 |
| gemma2:9b | C1 | 0.286 | 0.295 | 0.299 | 0.472 |
| gemma2:9b | C2 | 0.272 | 0.299 | 0.280 | 0.472 |
| gemma2:9b | C3 | 0.300 | 0.286 | 0.278 | 0.472 |
| llama3.1:8b | C0 | 0.381 | 0.277 | 0.285 | 0.500 |
| llama3.1:8b | C1 | 0.275 | 0.314 | 0.308 | 0.500 |
| llama3.1:8b | C2 | 0.272 | 0.320 | 0.303 | 0.500 |
| llama3.1:8b | C3 | 0.278 | 0.267 | 0.294 | 0.500 |
| qwen2.5:7b-instruct-q4_K_M | C0 | 0.308 | 0.267 | 0.234 | 0.444 |
| qwen2.5:7b-instruct-q4_K_M | C1 | 0.192 | 0.273 | 0.204 | 0.444 |
| qwen2.5:7b-instruct-q4_K_M | C2 | 0.197 | 0.277 | 0.232 | 0.444 |
| qwen2.5:7b-instruct-q4_K_M | C3 | 0.214 | 0.284 | 0.211 | 0.444 |

三族（局汇总 / 击球 / 投球）全部落在 0.19–0.38；唯一像样的是只有 2 个 cell 的 `pom`/`result`（0.44–0.50，二分类运气成分高）。

### 6.3 copy_rate：抄得多，抄得对少

| 模型 | 条件 | 数值预测数 | copy_rate |
|---|---|---:|---:|
| gemma2:9b | C0 | 1062 | 0.702 |
| gemma2:9b | C1 | 1083 | 0.721 |
| gemma2:9b | C2 | 1079 | 0.713 |
| gemma2:9b | C3 | 1079 | 0.713 |
| llama3.1:8b | C0 | 1086 | 0.690 |
| llama3.1:8b | C1 | 1095 | 0.751 |
| llama3.1:8b | C2 | 1091 | 0.755 |
| llama3.1:8b | C3 | 1074 | 0.708 |
| qwen2.5:7b-instruct-q4_K_M | C0 | 1112 | 0.710 |
| qwen2.5:7b-instruct-q4_K_M | C1 | 1112 | 0.701 |
| qwen2.5:7b-instruct-q4_K_M | C2 | 1112 | 0.719 |
| qwen2.5:7b-instruct-q4_K_M | C3 | 1112 | 0.692 |

口径：预测出的数值在卷宗全文（含规则与干扰文档）中逐字出现。**0.69–0.76 的数值预测是“文中的某个数”**，但 cell 正确率只有 0.23–0.31 —— 模型大量**抄了错的数**（旧值、他人数值、干扰场数字），而不是老实闭合推导。这是“浅层抄写”在本数据上最直接的证据。

### 6.4 修订跟随：C1 的 145 个修订 cell

| 模型 | 修订 cell | C0 时保留旧值率 | C1 按新金标正确率 | 该模型 C1 整体 |
|---|---:|---:|---:|---:|
| gemma2:9b | 145 | 0.269 | 0.193 | 0.299 |
| llama3.1:8b | 145 | 0.352 | 0.152 | 0.307 |
| qwen2.5:7b-instruct-q4_K_M | 145 | 0.324 | 0.145 | 0.234 |

给了修订备忘后，模型在“被修订的 cell”上正确率反而**低于自己的整体水平**：多一份备忘没有变成修正信号，只增加了上下文负担。这是本轮最需要正视的负面结果。

### 6.5 证据必要性：C3 的 72 个变化 cell

| 模型 | C1 在这些 cell | C3 在这些 cell | C1→C3 全表预测变化率 |
|---|---:|---:|---:|
| gemma2:9b | 0.306 | 0.250 | 0.264 |
| llama3.1:8b | 0.250 | 0.194 | 0.332 |
| qwen2.5:7b-instruct-q4_K_M | 0.264 | 0.306 | 0.346 |

因解码为 `temperature=0` + 固定种子，预测变化只能来自提示变化，不是采样噪声。删掉 M2 后模型确实会改答案（26–35% 的 cell 变化），但在**金标该变的 72 个 cell 上没有变得更好**（0.19–0.31），说明变化是全表性的重排，而非“识别到证据缺失”。

### 6.6 C2 的版本陷阱：还没走到陷阱就已经错了

受影响 cell：每场 2 个 `bowling_runs`（共 36 个），其中 25 个的 2025 规则值与正确值不同（byes>0）。

| 模型 | 陷阱 cell | C1 正确 | C2 正确 | 落入 2025 陷阱 | 其他错法 | C1→C2 未变 |
|---|---:|---:|---:|---:|---:|---:|
| gemma2:9b | 36 | 0/36 | 0/36 | 0 | 36 | 72.2% |
| llama3.1:8b | 36 | 0/36 | 0/36 | 0 | 36 | 88.9% |
| qwen2.5:7b-instruct-q4_K_M | 36 | 1/36 | 1/36 | 0 | 35 | 55.6% |

**该条件在当前能力水平上无信号**：模型在 `bowling_runs` 上本来就只有 0–3% 正确率，根本走不到“该用哪版规则”这一步；落入 2025 陷阱的次数为 0。换句话说，C2 测不到版本敏感性——不是因为陷阱设计错，而是因为前置 cell 已经在地板上。

## 7. 预注册门判定

| 门 | 原判据 | 读数 | 判定 |
|---|---|---|---|
| G1 | C0 cell_exact > 0.80 则任务太浅 | 最高 0.3125 | **PASS** |
| G2 | C1 table_exact = 0 且 closure 违规 > 0.50 | table_exact 0；closure 1.00 | **PASS** |
| G3 | 三个模型全部 parse_fail | json_ok 1.000 | 未触发 |
| G4 | C2 version_sensitivity < 0.10 则重做文档 | 金标变化 0/1368；陷阱命中 0/36 | **口径作废，需改写** |

G4 的问题不在数据，在判据：C2 是“诱饵型”操纵（正确金标不变，错误答案才是版本敏感的），用“金标变化率”永远判不过。改写建议：G4 改为“陷阱命中率显著 > 0 且 `bowling_runs` 基线正确率 > 0.30”，否则该条件在本能力档位不可用。

## 8. 主要发现

1. **拼接式的表已经不能靠抄**：C0 只有 0.27–0.31，整表 0/216，closure 近乎全违规。这张表的最低门槛就是算术闭合，而 7–9B 模型过不去。
2. **错误类型是“选错数”，不是“写不出数”**：copy_rate ~0.70 却只有 ~27% 正确 → 模型在文中找到的是旧值/干扰值/他人值。这对数据设计是好消息：难度来自“必须推导”，不是来自“读不到”。
3. **修订机制（C1）当前是负收益**。145 个修订 cell 上正确率低于整体，说明备忘没有变成可执行约束；下一步应先做“修订链可回放性”检查（M1/M2 是否真的改变了模型看到的数值），而不是直接扩数据。
4. **证据必要性（C3）需要更强的操纵**：当前只删 1 条备忘、影响 4 个 cell，模型在金标变化处没有表现出差异性。建议改为“删掉唯一的决定性文档 + 让该 cell 变为必须弃权”，才能测到“识别缺失”。
5. **C2（版本冲突）在本档位不可用**：需要先让 `bowling_runs` 这类闭合 cell 的基线正确率脱离地板（例如给一个已闭合的局部示例），否则陷阱永远触发不到。

## 9. 局限

- 单切片：18 场 × 18 次/格，置信区间宽，未做重复采样（D4 未做）；不过 `temperature=0` 已保证确定性，重复主要用来验证确定性与上下文边界效应。
- 本地 7–9B 量化模型，不能外推到云端强模型；这正是 R28 已记录的 `E5 UNTESTED` 约束（零付费，禁止云端）。
- 金标是**规则重算**（solver 生成），不是人工独立标注；按 R28 纪律必须写明“作者自标、未独立验证”。
- `copy_rate` 是弱证据（数值在文中出现 ≠ 抄对），只用于诊断，不用于论文主张。
- C2 的结论受地板效应限制，只能写“本档位无信号”，不能写“版本冲突无效”。

## 10. 现状与下一步

| 事项 | 状态 | 说明 |
|---|---|---|
| 数据构建（18 场 / 72 卷宗 / 76 cells） | ✅ 完成 | `data/`，SHA256 已记录 |
| 全量评测 216 次 | ✅ 完成 | 14:16，exit 0 |
| 主表 + 分组 + 门判定 | ✅ 完成 | `analysis.json`、本报告 |
| D4 可靠性（10 题 × 2 次） | ⬜ 未做 | 约 20 分钟 |
| C2 条件重建（让闭合 cell 脱地板后重测） | ⬜ 待决 | 3 模型 × 18 = 54 次，约 25–35 分钟 |
| C3 强化（弃权型证据缺失） | ⬜ 待决 | 需改 builder + 重算金标 |
| D5 一页 memo / go-no-go | ⬜ 待写 | 依据本报告 §7–§8 |

**建议顺序**：先写 D5 memo（当前证据已足够支撑“切片可行”），再决定是否投入 C2 重建；D4 可靠性可并行插空跑。

## 11. 复现

```bash
PY="C:/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"
"$PY" DEEP_T2T/build_deep20.py --limit 20      # 构建（幂等）
"$PY" DEEP_T2T/eval_deep.py                     # 全量，按 match_id 去重可续跑
"$PY" DEEP_T2T/smoke_one.py                     # 单场冒烟
```

## 12. 附录：文件清单

| 文件 | 内容 |
|---|---|
| `DEEP_T2T/REPORT_V1.md` | 本报告 |
| `DEEP_T2T/ANALYSIS_V1.md` | 精简分析（表格版） |
| `DEEP_T2T/analysis.json` | 全部指标的机器可读版 |
| `DEEP_T2T/results.json` | 12 格 summary（脚本生成） |
| `DEEP_T2T/runs/*.jsonl` | 216 行原始输出（含 raw_output、逐 cell 判定） |
| `DEEP_T2T/data/dossiers.jsonl` `golds.jsonl` | 72 份卷宗 + 72 份金标 |
| `DEEP_T2T/PLAN_V1.md` | 设计与预注册门 |


---

## 附录 A8：2026-11-15 实验总报告

> 原文件：VETT_INTEGRATED_20261113/analysis/VETT_REPORT_20261115_FINAL.md（190 行）

# VETT 2026-11-15 实验总报告

日期：2026-11-15（北京时间）
范围：220 场发布版长文、R28、43 字段、本机 Qwen/Llama/Gemma
外部 API：0
状态：主体批次完成；U 第六批部分完成（35/72）

## 一、执行摘要

2026-11-15 的实验分为两段：

1. 夜间 D/T/U 主体：186 次既有 + 1476 次新增。
2. 证据升级抽样：U 前五批 432 次完成；第六批已发 35 次。

累计发出约 2129 次本地请求；失败 0、外部 API 0。

三条主结论：

- 证据呈现方式影响很大：D 的 O 44/54、M 50/54、E 54/54。
- 整表 locator 没有稳定收益：12 根 130/144→131/144，仅 +1 格。
- U 的瓶颈是语义绑定：全池 598/1311 两格全对；抽样中“旧只对 wickets”的 108 条只有 8 条恢复两格。

## 二、运行账本

| 批次 | 请求 | 结果 |
|---|---:|---|
| 既有 D/T/U | 186 | 保留 |
| U 全池 | 1311 | 两格 598/1311 |
| D+ 三个变体 | 129 | 41/54、34/45、27/30 |
| T 扩展与 locator | 36 | 62/72→63/72 |
| U 抽样 1–5 | 432 | 181/432 |
| U 抽样 6（部分） | 35 | 未完成 |
| 合计发出 | 约 2129 | 外部 API 0 |

## 三、U 全池复算

### 解析分层

| 层 | 数量 |
|---|---:|
| 服务发起 | 1311 |
| 收到响应 | 1311 |
| JSON 成功 | 1304 |
| 可评分 | 1304 |

旧报告“解析 1311/1311”错误；Qwen 7 条格式失败。

### 四组

| 组 | 数量 |
|---|---:|
| 两格都对 | 598 |
| 只对 runs | 67 |
| 只对 wickets | 101 |
| 两格都错 | 545 |

### 覆盖

- 437 局位、219 个独立比赛根。
- 缺 match_0004 两局、match_0066 第二局，共 3 局位。

## 四、U 抽样 1–5

| 批次 | 局位 | 响应 | 两格 |
|---|---:|---:|---:|
| 1 | 48 | 144 | 62 |
| 2 | 24 | 72 | 32 |
| 3 | 24 | 72 | 25 |
| 4 | 24 | 72 | 32 |
| 5 | 24 | 72 | 30 |
| 合计 | 144 | 432 | 181/432 |

按旧评分组：

| 组 | 本轮两格正确 |
|---|---:|
| 两格都对 | 103/108 |
| 只对 runs | 65/108 |
| 只对 wickets | 8/108 |
| 两格都错 | 5/108 |

分模型：Qwen 43/120、Llama 68/120、Gemma 70/120。

关键：旧只对 wickets 的样本很难恢复两格，问题集中在 runs 定位或字段绑定，不是 JSON 格式。

U 第六批：24 局位×3=72 次，已发 35 次，未完成。

## 五、D 与 D+ 配对

### D 基线 18 根

| 条件 | 正确 |
|---|---:|
| O 原文 | 44/54 |
| M 移位 | 50/54 |
| E 摘录 | 54/54 |

O→M：救回 8、改坏 2，净 +6。
O→E：救回 10、改坏 0。

### D+ 同根同模型配对

| 变体 | 配对数 | O | 变体 | 救回 | 改坏 | 净 |
|---|---:|---:|---:|---:|---:|---:|
| 移除局中比分 | 54 | 44 | 41 | 0 | 3 | −3 |
| 第二落点 | 45 | 37 | 34 | 1 | 4 | −3 |
| 移除另一局比分 | 30 | 28 | 27 | 0 | 1 | −1 |

三个 D+ 变体配对后均净负；绝对数不能直接比较干预优劣。

## 六、T 整表

| 批次 | 基线 | locator | 变化 |
|---|---:|---:|---:|
| 0100/0111/0120/0130/0140/0160 | 68/72 | 68/72 | 0 |
| 0183–0188 | 62/72 | 63/72 | +1 |
| 合计 | 130/144 | 131/144 | +1 |

唯一变化：match_0186，Qwen，inn2.total_wickets：基线 2，locator 1，金标 1。

结论：当前 locator 不足以形成整表方法收益；全 43 格未评分。

## 七、R28 与 43 字段

R28：

- v6：直接 11/18，v5 11/18。
- v7：直接 39/66，严格 42/66，按归属 51/66。
- 按归属多 12，但实际误转移 14、无法执行 1。
- 严格规则能拦截，但损失正确交付；仍是开发候选。

43 字段：

- 历史启发式 79/258：Qwen 33、Gemma 38、Llama 30。
- 人工固定 40 格：0/40 完成。
- 本轮 EVIDENCE_INDEX 96 条全部 pending_human_review。

## 八、结论

1. 证据呈现是强信号，但“提供证据”本身不等于整表收益。
2. D+ 配对后全部净负，说明简单的删除/移动不是稳定干预。
3. U 抽样显示“只对 wickets”组几乎无法恢复两格，下一步应查 runs 定位。
4. T locator 只多 1 格，且是单模型单格，不能写成方法。
5. R28 的误转移是真实行为，严格/归属两种规则各有代价。

## 九、未完成

- U 第六批剩余 37 次。
- R28 低旧值方向。
- D+ 剩余根与第二落点扩展。
- T 全 43 格证据掩码与退步评分。
- Robust/S 格式、等义题干、采样复现。
- U 缺证变体与等长删除对照。
- 人工复核 0/40。

## 十、文件

主目录：VETT_INTEGRATED_20261113/analysis/

- VETT_OVERNIGHT_CONSOLIDATED_REPORT_20261115.md
- vett_overnight_20261114/REPORT_FINAL.md
- vett_overnight_20261114/runs/u_full.jsonl
- vett_overnight_20261114/runs/dplus_remove.jsonl
- vett_overnight_20261114/runs/dplus_end.jsonl
- vett_overnight_20261114/runs/dplus_other.jsonl
- vett_overnight_20261114/runs/t_expand.jsonl
- vett_overnight_20261114/runs/t_expand_locator.jsonl
- vett_evidence_upgrade_20261115/CORRECTION.md
- vett_evidence_upgrade_20261115/SAMPLE_RESULTS.md
- vett_evidence_upgrade_20261115/U_RECALC.json
- vett_evidence_upgrade_20261115/DPLUS_PAIRED.json
- vett_evidence_upgrade_20261115/T_PAIRED.json
- vett_evidence_upgrade_20261115/RUNS/u_sample1..6

## 十一、复现

python u_full.py
python dplus_remove.py
python dplus_end.py
python dplus_other.py
python t_expand.py
python t_expand_locator.py
python score_u_full.py
python score_dplus.py
python score_dplus_end.py
python score_dplus_other.py
python score_t_expand.py
python score_t_expand_locator.py

全部按 match × condition × model 去重；外部 API 0。


---

## 附录 A9：2026-11-15 夜间合并报告

> 原文件：VETT_INTEGRATED_20261113/analysis/VETT_OVERNIGHT_CONSOLIDATED_REPORT_20261115.md（176 行）

# VETT 夜间本地实验合并报告

日期：2026-11-15（北京时间）
范围：220 场发布版长文、R28、43 字段与本地 Qwen/Llama/Gemma 诊断
外部 API：0
状态：已启动批次全部完成；无活跃推理；540 席全矩阵未完成

## 一、执行摘要

本次接管保留上一轮 186 次请求，又完成 1476 次本地请求：

- U 全池双局证据审计：1311 次
- D+ 三个干扰变体：129 次
- T 整表扩展与 locator：36 次

累计本地请求 1662 次；失败 0、重试 0、外部 API 0。

三条主要发现：

1. 证据呈现方式对同格答案影响很大。D 的 18 个根上，E 摘录 54/54、M 移位 50/54、O 原文 44/54；O→M 救回 8、改坏 2，O→E 救回 10、改坏 0。
2. 但“把证据句附到整表提示”没有稳定收益。T 两批 12 根：基线 130/144，locator 131/144，只多 1 格。
3. 全池证据审计并不容易：U 的 1311 行只有 598 行两格同时正确；模型常能找到句子，但把局中比分或另一局值当终局。

结论：证据位置/摘录是有效诊断信号；整表方法改动尚未成立；U 显示“有引文”不等于“终局语义正确”。

## 二、运行账本

| 批次 | 规模 | 行数 | 结果 |
|---|---|---:|---|
| 上一轮 D/T/U | 6 D + 6 T + 11 U | 186 | 保留 |
| U 全池 | 437 局位 ×3 模型 | 1311 | 两格 598/1311 |
| D+ 移除局中比分 | 18 根 ×3 | 54 | 41/54 |
| D+ 第二落点 | 15 根 ×3 | 45 | 34/45 |
| D+ 移除另一局比分 | 10 根 ×3 | 30 | 27/30 |
| T 0183–0188 基线 | 6 根 ×3 | 18 | 62/72 |
| T 0183–0188 locator | 6 根 ×3 | 18 | 63/72 |
| 合计新增 |  | 1476 | 失败 0 |

## 三、U 全池证据审计

- 覆盖：220 场中可解析的 437 个局位；每局 3 模型。
- 主指标：同一局 total_runs 与 total_wickets 同时正确。

| 模型 | 两格正确 | total_runs | total_wickets | 解析成功 |
|---|---:|---:|---:|---:|
| Qwen | 175/437 | 214 | 211 | 430/437 |
| Llama | 208/437 | 230 | 240 | 437/437 |
| Gemma | 215/437 | 221 | 248 | 437/437 |
| 合计 | 598/1311 | 665/1311 | 699/1311 | 1311/1311 |

- Qwen 有 7 条格式失败、2 条 UNKNOWN；Llama/Gemma 无 UNKNOWN。
- 错误形态：局中比分、另一局比分、字段对调、只答对一个字段。
- 该批为全池自然样本，不能把 598/1311 直接当作发布版长文任务的“模型能力上限”。

## 四、D 与 D+：位置和干扰

### D 基线（18 根）

| 条件 | 正确 |
|---|---:|
| O 原文 | 44/54 |
| M 移位 | 50/54 |
| E 摘录 | 54/54 |

- O→M：救回 8、改坏 2，净 +6。
- O→E：救回 10、改坏 0。
- 扩展 12 根单独：O 28/36、M 35/36、E 36/36。

### D+ 三个单项干扰

| 变体 | 行数 | 正确 | 备注 |
|---|---:|---:|---|
| 移除局中竞争比分 | 54 | 41/54 | 绝对低于 O 44/54 |
| 证据移到末尾 | 45 | 34/45 | 15 根有可移动证据 |
| 移除另一局比分 | 30 | 27/30 | 10 根有另一局比分 |

- 这三批尚未逐根同模型配对 O；只能作绝对数描述，不能直接写净收益。
- “移除另一局比分”目前最稳（27/30）；“移到末尾”最弱。
- 位置效应与“局中比分干扰”相关，但本轮不足以区分移动本身与干扰距离。

## 五、T 整表

| 批次 | 基线 | locator | 变化 |
|---|---:|---:|---:|
| 0100/0111/0120/0130/0140/0160 | 68/72 | 68/72 | 0 |
| 0183–0188 | 62/72 | 63/72 | +1 |
| 合计 12 根 | 130/144 | 131/144 | +1 |

- 目标格：两队两局的 total_runs 与 total_wickets。
- locator 只追加从原文找到的候选证据句，不读金标、记分表或测试结果。
- 结论：当前“附加证据句”不足以形成整表方法收益。
- 全 43 格、非目标有证据格的退步尚未评分；不能写“整表无退步”。

## 六、R28 改判支线（历史结果）

| 轮次 | 直接联合 | v5 严格 | v5 按归属 |
|---|---:|---:|---:|
| v6（6 场） | 11/18 | 11/18 | 11/18 |
| v7（22 场） | 39/66 | 42/66 | 51/66 |

- v6 配对：错→对 3、对→错 3、对→对 8、错→错 4；分通知 28/36 与 29/36。
- v7 按归属比直接多 12，但实际误转移 14、无法执行 1。
- Qwen 在 v7 中 12 条把“维持”读成“改判”；严格规则能拦住，但损失正确交付。
- 该支线仍是开发候选；低旧值方向尚未构建。

## 七、43 字段

- 历史启发式口径 79/258 未变。
- Qwen 33/79、Gemma 38/79、Llama 30/79。
- 固定 40 格人工复核仍为 0/40。
- 本轮未新增人工证据确认；U 的模型引文只作候选，不自动升级为人工金标。

## 八、结论

1. **证据呈现是强信号**：E 在 D 上 54/54，M 50/54，O 44/54。
2. **整表改动尚未成立**：T locator 12 根仅 +1，且全 43 格未评。
3. **U 的失败主要是语义绑定**：有引文不等于终局正确；598/1311 两格全对。
4. **R28 的误转移是真实行为**：按归属执行会放行错误转移；严格规则则损失正确交付。
5. **样本边界**：D 只覆盖有显式/半显式终局句的根；U 是全池但每局只问一次、每模型独立；T 只评 4 个目标格。

## 九、未完成与下一步

未跑：

- R28 低旧值方向构造与运行。
- D+ 剩余根、第二落点扩展。
- T 更多新根、全 43 格证据掩码与退步评分。
- Robust 格式/等义题干/采样复现。
- U 的去证版本与等长非证据删除对照。

下一步只做一个最小验证：

> 冻结“定位候选证据窗口”这一项改动，在 6–8 个未调试新根上，同时跑 O/M/E 与整表 T；目标格与其他已确认有证据的格都评。

判定标准：

- O→E 至少 2 个独立根救回、净为正；
- T 目标格净为正；
- 其他有证据格不退步；
- 证据语义人工复核通过。

## 十、文件

- 主目录：VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114/
- U 报告：REPORT_U_FULL.md
- 队列：QUEUE_STATUS.md
- 进度：PROGRESS.md
- 快照：MORNING_README.md
- 原始输出：
  - runs/u_full.jsonl（1311）
  - runs/dplus_remove.jsonl（54）
  - runs/dplus_end.jsonl（45）
  - runs/dplus_other.jsonl（30）
  - runs/t_expand.jsonl（18）
  - runs/t_expand_locator.jsonl（18）
- 清单：expansion_manifest.json、dplus_remove_manifest.json、dplus_end_manifest.json、dplus_other_manifest.json、t_expand_manifest.json、t_expand_locator_manifest.json
- 评分：score_u_full.py、score_dplus.py、score_dplus_end.py、score_dplus_other.py、score_t_expand.py、score_t_expand_locator.py

## 附录：复现命令

python u_full.py
python dplus_remove.py
python dplus_end.py
python dplus_other.py
python t_expand.py
python t_expand_locator.py

评分：
python score_u_full.py
python score_dplus.py
python score_dplus_end.py
python score_dplus_other.py
python score_t_expand.py
python score_t_expand_locator.py

说明：所有 runner 按 match × condition × model 去重续跑；外部 API 0。


---

## 附录 A10：夜间首轮 D/T 最终报告

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114/REPORT_FINAL.md（58 行）

# REPORT_FINAL：本地多场 D/T/U

日期：2026-11-15。新增 186 次本地请求；外部 API 0。

## 一、总量

- 首轮 D/T 27 + D 扩展 108 + T locator 18 + U 审计 33 = 186。
- 失败 0、重试 0；有效队列耗尽。

## 二、D 位置对照

### 首轮 6 根
O 16/18、M 15/18、E 18/18。

### 扩展 12 根
O 28/36、M 35/36、E 36/36。
- O→M：错→对 7、对→错 0、都对 28、都错 1；净 +7。
- O→E：错→对 8、对→错 0、都对 28、都错 0；净 +8。

### 合并 18 根
O 44/54、M 50/54、E 54/54。
- O→M 救回 8、改坏 2，净 +6。
- O→E 救回 10、改坏 0。

## 三、T 整表

- 6 根 ×3 模型 ×4 目标格：基线 68/72。
- locator 回投 18 次：68/72，无救回、无退步。
- 未冻结出可写进方法的改动。

## 四、U 证据审计

- 11 根 ×3 模型 = 33 次。
- 两格同时正确 **3/33**；每模型 1/11。
- 引文逐字有效 **30/33**。
- 说明：模型多能找到句子，但常把局中比分/另一局值当终局；该批覆盖终局句不完整的自然样本，低分不直接等于发布版长文整体能力。

## 五、关键结论

- 证据位置效应在扩展 12 根上稳定：M/E 明显优于 O，且改坏少。
- T 的“附加证据句”改动无收益，不能写成整表改进。
- U 显示“有引文”不等于“终局语义正确”，需要字段/局别绑定核验。

## 六、文件

- runs/expand.jsonl 108 条
- runs/t_locator.jsonl 18 条
- runs/u_audit.jsonl 33 条
- expansion_manifest.json、t_locator_manifest.json、u_manifest.json
- score_expand.py、score_t_locator.py、score_u.py
- MORNING_README.md、PROGRESS.md

## 七、限制

- 18 个 D 根均为发布版有显式/半显式终局句的样本，非随机全池。
- T 只回投一种 locator 改动；未评全 43 格。
- U 仅 11 根、33 次，不能代表 220 场整体。
- 未配置 08:00 独立定时快照。


---

## 附录 A11：220 场与 R28 两场联动试点

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_220_r28_link_pilot/REPORT.md（77 行）

# REPORT：220 场长文与 R28 两场联动试点

日期：2026-11-14。新增 36 次本地请求；6 个整表锚点复用旧预测；外部 API 0。

## 一、范围

- 两场：match_0003、match_0012，均第一局。
- 发布版 commentary 不含所需精确出局句、投手旧汇总和终局句；R28 使用 scorecard 重渲染全文。比赛与字段可追溯，输入证据与发布版不同。
- 发布版长文用于整表锚点；R28 结果不能归因于发布版长文能力。

## 二、字段映射

| 比赛 | 局 | 原投手 | 旧 | 新投手 | 旧 | 目标 | 保持 |
|---|---|---|---|---|---|---|---|
| 0003 | 1 | Evan Clarke | 4 | Connor Reed | 1 | 两人 wickets | total=8 |
| 0012 | 1 | Caleb Brooks | 4 | Lucas Vale | 2 | 两人 wickets | total=10 |

三条件：无通知、维持、正式改判；仅末尾通知不同。

## 三、表一：整表锚点

- Qwen 0003 第二名取到 Mason Cooper（非 Connor）；Gemma 0003 取到 Caleb Price（非 Connor）；Llama 0003/0012 的 bowling 行名称 null。
- Qwen 0012 第一名取到 Liam Frost（非 Caleb）。
- 只有 Gemma 0012 同时取到 Caleb 4、Lucas 2 和 total 10，形成 3 个可比格。
- 其余目标投手不在整表 top-2 行，不能把整表输出当作同一格结果。

## 四、表二：通知与方法

| 方法 | 无通知 | 维持 | 改判 | 联合（维持+改判） |
|---|---:|---:|---:|---:|
| A 直接 | 3/6 | 3/6 | 0/6 | 3/6 |
| B 抽取+程序 | 1/6 | 0/6 | 1/6 | 1/6 |

- 逐模型联合：A Qwen/Llama/Gemma 各 1/2；B 仅 Llama 1/2，Qwen/Gemma 0/2。
- 保持字段 total：A 三条件为 3/3/0；B 为 1/0/1。
- total 漂移例：A 的 0003 Llama 输出 164；B 的 0003 Qwen 输出 10。

## 五、表三：最早错误

| 模型 | 例子 | 最早错误 |
|---|---|---|
| Qwen | 0003 维持：A 4,2,total8；B 抽 3/1,total10 | 旧值读错 + total 错 |
| Llama | 0003 无通知：A total164 | 把球队总分当出局数 |
| Gemma | 0003 维持：B original=Connor、final=Evan，旧值 1/0 | 人物归属颠倒 + 旧值错 |
| Qwen | 0012 维持：B original=Caleb、final=Lucas，旧值 3/2 | 把维持读成改判 |
| Llama | 0012 改判：B 旧值 4/2，程序 3/3，total10 | 唯一 B 正确例 |

A 只有最终数对，不能区分读错旧值与算错；B 可定位旧值、归属或通知。

## 六、执行与错误

- A 改判 0/6：表现为旧值、单边更新或 total 错。
- B 联合 1/6：旧值错、total 错、人物颠倒、维持读成改判；部分因旧值/total 非法拒绝。
- 实际误转移：B 在 retain 至少 4 条把 original/final 写成 A→B 或 B→A，且最终值均错。
- 无空答；36/36 解析成功。

## 七、数据补丁

- 新增 evidence_map.jsonl：把两场 R28 事件、投手、目标字段、total 字段连到整表字段；标注发布版缺精确证据、使用重渲染。
- 新增三条件模板与评分：无通知/维持/改判，A/B 两法。
- 未改 220 场源池、金标、79/258 分母。
- 回滚：删除 vett_220_r28_link_pilot 目录。

## 八、六件事

1. 两场 0003/0012，均为 scorecard 重渲染；发布版原句缺事件与旧汇总。可回链格子是两人 wickets 和 total；发布版只有 0012 Gemma 的 2 个投手格可比。
2. 计划 42（36 聚焦 + 6 锚点），完成 36 新请求，6 锚点复用；失败 0；外部 API 0。模型 Qwen2.5-7B、Llama3.1-8B、Gemma2-9B。
3. Qwen 旧值+total 错；Llama 把总分当出局数；Gemma 人物归属颠倒。各至少 1 例，涉及 2 场。
4. A 联合 3/6，B 联合 1/6；B 少 2，无净收益；误转移至少 4，拒绝若干。
5. 补丁只加证据映射和三条件模板；同一输入支持的是重渲染文本内的关系，发布版只有比赛/字段映射。
6. 下一轮最值得验证发布版长文是否真的缺这些证据，并补不同旧值方向；自动核查已完成，人工待复核，新比赛待复验。

## 九、限制

- 发布版与重渲染输入不同，不能写成发布版长文错误。
- 两场、6 个模型—比赛对，描述性开发结果。
- 整表锚点多数目标投手不在 top-2 行，不能形成同格比较。


---

## 附录 A12：本地证据核对与长文联动

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_local_evidence_long_run/REPORT.md（78 行）

# REPORT：VETT 本地证据核对与长文联动

日期：2026-11-14。新增 60 次本地请求；外部 API 0。

## 一、旧 36 条复算

- 链接试点 A：无通知 3/6、维持 3/6、改判 0/6，合计 6/18；联合（维持+改判）**0/6**，三条件 0/6。
- B：无通知 1/6、维持 0/6、改判 1/6，合计 2/18；联合 **0/6**。
- **更正：此前报告写 A 联合 3/6，是按条件计数误当交集；按同一模型同一比赛取交集，A/B 均为 0/6。**
- 实际误转移：B 在维持中至少 4 条把 original/final 写成 A→B 或 B→A；均未得到正确最终值。
- 整表锚点 6 条：仅 Gemma 0012 的目标投手同时落入 top-2，形成 2 个投手格 + total 可比；其余目标投手不在 top-2 或名称为 null，不可比。

## 二、本阶段模型与规模

- Qwen2.5-7B、Llama3.1-8B、Gemma2-9B。
- 证据核对：8 场 × 1 局 × 3 模型 = **24 次**；每模型 4/8 同时答对总分和总出局。
- A/B/C 联动：4 场 × 3 模型 × 3 条件 = **36 次**。
- 合计 **60 次**；基础设施失败 0；未完成 0。
- 4 场：match_0002、0047、0102、0174；均为发布版 commentary 中有明确终局句的局。

## 三、发布版证据链接

- 8 场 × 1 局，每局 2 格（total_runs、total_wickets）= **16 个发布版同格链接**；总得分与总出局都由同一终局句直接支持。
- 自动逐字核对通过：8/8 局；模型没有找到证据的条目不能证明缺证。
- A/B/C 的 4 场是这 16 格中的**同一输入、同一句证据**的子集。
- R28 两场（0003/0012）只有比赛根与字段映射，正文为 scorecard 重渲染，发布版无精确事件/旧汇总。
- 79/258 历史口径未改。

## 四、证据核对结果

- 每模型 4/8 同时答对；错误包括把总分当出局数、把另一局比分当目标局、只答对一个字段。
- 声明 quotes 的条目中，逐字命中率不是 100%；部分模型引用句与目标局不匹配。
- 8 场中 4 场三模型一致且正确；其余存在分歧或错误，进入人工队列。

## 五、A/B/C 结果

| 模型 | A 全文 | B 证据 | C 全文+引用 |
|---|---:|---:|---:|
| Qwen | 2/4 | 4/4 | 2/4 |
| Llama | 2/4 | 3/4 | 2/4 |
| Gemma | 2/4 | 2/4 | 1/4 |
| 合计 | **6/12** | **9/12** | **5/12** |

- B 比 A 多 3（Qwen +2、Llama +1、Gemma 0），没有对→错。
- C 比 A 少 1（Gemma -1），没有错→对；Qwen/Llama 不变。
- C 的引用有效率 **10/12**；Gemma 2 条引用无法逐字回原文。
- C 的数值正确 5/12，说明“先引用”没有稳定改善两个字段。
- C 的额外长度/耗时：引用字段增加输出，但本轮未单独计时；token 记录已保存。

## 六、答案与错误分类

- A 错、B 对：Qwen 2 条、Llama 1 条，均为发布版终局句在长文中被忽略；B 提供该句后修复。
- A 错、B 也错：Gemma 1 条，仍把总分与出局数混淆。
- A 对、C 错：Gemma 1 条，引用有效但数值改为错值。
- 证据定位失败：若干；串局/字段混淆：Gemma 总分与出局数；仅数值错：Qwen C。
- 三模型一致不等于正确；有分歧样本进入人工队列。

## 七、数据补丁

- 新增 16 个发布版同格链接（8 局 × 2 字段）和 2 个 R28 字段映射（重渲染，仅比赛根/字段）。
- 新增 A/B/C 三条件模板与 4 场同输入评分。
- 未改 220 场、金标、79/258。
- 回滚：删除 vett_local_evidence_long_run 目录。

## 八、六件事

1. 旧 36 条复算：A 联合 0/6、B 联合 0/6（此前 A 3/6 是交集误算）；A 合计 6/18、B 2/18；B 维持实际误转移至少 4。
2. 三模型；证据 8 场 8 局，24 次；ABC 4 场，36 次；合计 60 次，失败 0，未完成 0；外部 API 0。
3. 发布版连上 8 场 8 局 16 格；同输入证据的 A/B/C 为 4 场；另有 R28 2 场仅比赛根/字段映射，重渲染输入。
4. 模型错误：总分当出局、串局、字段混淆、只答一个字段；Gemma 字段混淆 1 例、Qwen 串局/数值错若干；证据不足处标待核。
5. A6/12、B9/12、C5/12；B 多 3、无对→错；C 少 1、无错→对；C 引用无效 2/12（Gemma）。
6. 补丁为 16 格发布版链接 + 4 场 ABC + 2 条 R28 映射。下一轮优先验证“长文定位失败是否由证据句位置而非模型能力导致”，用 6–8 场未调试比赛，补低旧值方向和局中比分干扰；自动核查已完成，人工待复核，新比赛待复验。

## 九、限制

- 8 场证据任务只覆盖一局，未做双局；4 场 ABC 是开发子集。
- 发布版终局句与 scorecard 金额一致，但语义人工复核未完成。
- R28 两场为重渲染，不能与发布版同输入混报。


---

## 附录 A13：证据位置对照与整表回投

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_evidence_position_transfer/REPORT.md（75 行）

# REPORT：证据位置对照与整表回投

日期：2026-11-14。新增 45 次本地请求；外部 API 0。

## 一、旧结果复算（0 调用）

- 8 场证据任务：每模型 4/8 两格全对。
  - 三模型全对的根：0002、0047、0180、0209（4 场）。
  - 三模型全错的根：0102、0174、0175、0181（4 场）。
  - 口径一致，同一分母、同一两格全对定义。
- 旧 36 条联动：
  - A：无通知 3/6、维持 3/6、改判 0/6，合计 6/18；联合 0/6。
  - B：无通知 1/6、维持 0/6、改判 1/6，合计 2/18；联合 0/6。
  - 此前 A 联合 3/6 是交集误算；按同一模型同一比赛取交集为 0/6。
  - B 维持实际误转移至少 4 条；均有原始输出，未见缺记录。
- A/B/C：A 6/12、B 9/12、C 5/12；C 引用有效 10/12。

## 二、本阶段规模

- Qwen2.5-7B、Llama3.1-8B、Gemma2-9B。
- 5 场 × 1 局 × 3 模型 × 3 条件 = 45 次。
- 冒烟 0（直接核心）、重试 0、基础设施失败 0、未跑 0；外部 API 0。
- 5 场：0066、0085、0087、0096、0165；均为发布版原文有明确终局句的局。
- 原计划 6 场，0099 未找到可用终局句，实际 5 场。

## 三、O/M/E 结果

| 模型 | O 原文 | M 移位 | E 摘录 |
|---|---:|---:|---:|
| Qwen | 4/5 | 5/5 | 5/5 |
| Llama | 5/5 | 4/5 | 5/5 |
| Gemma | 4/5 | 4/5 | 5/5 |
| 合计 | **13/15** | **13/15** | **15/15** |

- O→M：错→对 1、对→错 1、都对 12、都错 1；净 0。
- O→E：错→对 2、对→错 0、都对 13、都错 0；净 +2。
- 所有变化都集中在 **match_0087**，只涉及 1 个独立比赛根。

## 四、可复核例子

- Qwen 0087 O 输出 196/6（金标 198/6）；M 与 E 均 198/6。O 取了局中 196，M/E 修复。
- Llama 0087 O 198/6 正确；M 输出 196/10。M 把证据句移到段首后，取了局中 196，并把出局数读成 10。
- Gemma 0087 O 196/10；M 仍 196/10；E 198/6。O/M 同时串了局中比分和出局数。
- 其余 4 场三条件均正确；没有第二个根出现位置效应。

## 五、整表回投

**未运行。** 预登记标准是 O→M 至少两个独立根有实际救回，或 E 在至少两个独立根有可指认的字段结构误读。

- O→M 只有 0087 一个根，净 0。
- O→E 只有 0087 一个根，净 +2。
- 因此没有冻结选择器，也没有回投改动；不把单场收益写成方法收益。

## 六、数据补丁

- 新增 5 场 × 2 字段 = **10 个发布版同输入证据链接**（O 原文、M 移位、E 摘录）。
- 新增 O/M/E 位置对照候选与逐条输入哈希；未改 220 场、金标、79/258。
- 未新增整表回投补丁。
- 回滚：删除 vett_evidence_position_transfer 目录。

## 七、六件事

1. 旧 8 场：三模型全对 4 场（0002/0047/0180/0209），全错 4 场（0102/0174/0175/0181）；旧 36 条 A/B 联合均 0/6，B 维持误转移至少 4，未确认缺记录。
2. 5 场 5 局 45 请求；冒烟 0、重试 0、失败 0、未跑 0；约 6 分钟；外部 API 0。
3. O 13/15、M 13/15、E 15/15；O→M 救回 1/改坏 1（仅 0087），O→E 救回 2/改坏 0（仅 0087）；只涉及 1 个独立根。
4. 例子：Qwen 0087 O 196/6→E 198/6（取局中比分）；Llama 0087 O 198/6→M 196/10（局中比分+出局数错）；Gemma 0087 O 196/10→E 198/6（字段混淆）。其他 4 场全对，无法归因。
5. 整表回投未做；未达两个独立根阈值，缺可冻结的选择器/字段说明改动。
6. 新增 10 条同输入证据链接、5 场 O/M/E 候选；版本 v1，路径本目录，回滚删除目录。下一轮最值得验证 0087 类“局中比分 vs 终局”是否跨根复现，需 6–8 场新根、局中/另一局相近比分样本；自动核查完成，人工待复核，回投待复验。

## 八、限制

- 实际 5 场而非 6；0099 无可用终局句。
- 位置收益只在 0087，无法判断是移动本身还是该场局中 196 的干扰。
- M 的字节级恢复检查未完成，只按句子移动构造；报告保留为待核。
- 整表回投未运行，不能报告其他格是否退步。


---

## 附录 A14：43 字段复核与真短证据

> 原文件：VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/COMPLETE_REPORT.md（519 行）

# VETT 43 字段复核 + 真短证据：完整报告

日期：2026-11-13  
范围：258 字段可答性复核、三模型同分母、match_0014/0016 真短证据  
调用：43 字段 0 次；短证据 18/18 次；外部 API 0。

## 0. 一页摘要

**43 字段**

- 旧规则确认可答 73/258（69 直接 + 4 可推导）；185 待核。
- 抽样 40 格（30 未确认 + 10 已确认），BLIND_REVIEW 已交付；人工复核**未返回**，V2 暂沿用 73 格。
- 同分母 73 格：Qwen 29/73（39.7%）、Gemma 32/73（43.8%）、Llama 26/73（35.6%）。
- 全字段：Qwen 73/258、Gemma 85/258、Llama 63/258（恢复 5/6，0008 空）。

**真短证据**

- B 正文 572/571 字符，A 5,314/4,313；B 只含六句证据，不再是标注全文。
- 2 场：A two 0/6、B two 0/6、C two 0/6；B−A=0。
- B 的总出局 3/6，A 0/6：短证据帮助读总数，但没有帮助两人更新。
- C 的抽取 6/6 无法执行；Python 更新 two 0/6，修对 0、改坏 0；正确输入正控通过。

## 1. 43 字段复核

旧启发式要求同一句同时出现人物/球队与值，容易漏掉跨句证据：

- 例：match_0014 的 total 7 在 “Harbor Peninsula XI closed on 226 for 7” 一句，不在投手汇总句；旧规则若只在汇总句找，会漏。
- 例：top-3 击球员的 runs 可能在一句、排名需跨行比较；旧规则只能确认“某人得了多少”，不能确认“他排第三”。

抽样 40 格已写入 BLIND_REVIEW；人工状态待完成。没有人工确认的新增可答格，也没有确认旧规则误收格。

## 2. 三模型同分母

| 模型 | 可答答对 | 分母 | 准确率 | 全字段 |
|---|---:|---:|---:|---:|
| Qwen | 29 | 73 | 39.7% | 73/258 |
| Gemma | 32 | 73 | 43.8% | 85/258 |
| Llama | 26 | 73 | 35.6% | 63/258 |

Llama 按 73 分母计，0008 空回答的相关格按错。

## 3. 真短证据

| 模型 | A two | B two | C two | B total |
|---|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0/2 | 1/2 |
| Llama | 0/2 | 0/2 | 0/2 | 1/2 |
| Gemma | 0/2 | 0/2 | 0/2 | 1/2 |

- B 的两人错误以“两人旧值”为主；Llama 一场只加新投手。
- C 的 extraction 6/6 缺字段，无法执行 Python 更新；正控（正确输入）两场 two/three 都对。
- B 与 C 正文逐字相同，C 只多分步要求。

## 4. 四句话

1. **原规则最容易漏掉跨句证据**：如 0014 的 total 7 在终局比分句，不在投手汇总句；top-3 的排名需要跨行比较，旧规则只能确认个人数值。
2. **258 格中确认可答 73 格**；Qwen 29/73、Gemma 32/73、Llama 26/73；**185 格仍待人工核验**，40 格抽样已交付但未返回。
3. **两场 B 确实是短证据**（572/571 字符 vs A 的 5,314/4,313）；B 的 two 0/6，与 A 相同，没有多答对；B 的总出局 3/6 好于 A 的 0/6。C 的抽取 6/6 无法执行，程序更新 0 修对、0 改坏。
4. **下一轮优先完成 40 格人工复核，再决定是否扩 43 字段基线**；短证据只在两场开发集上跑通，先修 C 的抽取协议，不要直接扩到新比赛或 220 场。

## 5. 缺口

- 40 格人工复核未返回，V2 的 73 格仍是启发式口径。
- 短证据只有 2 场开发比赛，不能作为跨比赛结论。
- Llama 的同分母逐场拆分未完成，只报 26/73。
- 闭合约束因 schema 缺字段仍不可检查。


---

# 附录 A：DESIGN

# DESIGN：43 字段复核 + 两场真短证据

日期：2026-11-13。历史 54 条 A/B/C 只读；43 字段复核 0 次调用；短证据补跑 18 次（上限 18）；外部 API 0。

## 固定历史口径

- 54 条请求，其中 B/C 36 条；哈希可重建提示。
- 实际 B/C 是标注全文；C 多分步要求。
- two_wickets：B 0/18、C 1/18（唯一正确是 Gemma 的 match_0013；该场 total 答 7，金标 8）。
- 258 字段；旧启发式直接 69 + 可推导 4 = 73；185 未确认。
- 全字段：Qwen 73/258、Gemma 85/258、Llama 展平 63/258；Llama 5 条嵌套 JSON 可恢复，match_0008 为空。

## 本轮 43 字段

- 从 185 未确认抽 30 格、从 73 已确认抽 10 格，种子 20261113，覆盖摘要/局汇总/击球/投手。
- BLIND_REVIEW.md 给人复核；无人工返回，人工状态=待完成。
- 不根据模型对错改可答性；V2 暂沿用 73 格，新增 40 格待核。

## 短证据

- 2 场 × 3 条件 × 3 模型 = 18。
- A 全文；B 六句摘录（572 字符左右）；C=B 正文 + 分步抽取。
- 终局：0014 226 for 7；0016 138 for 3。
- 检查：B 短于 A 的 50%，六个片段可定位回 A，含 Note、通知、正确终局；无更新后 figures。

---

# 附录 B：SCORECARD_RESCORE_V2

# SCORECARD_RESCORE_V2：258 字段复核与三模型同分母

日期：2026-11-13。0 次模型调用。

## 1. 可答性

- V1 启发式：直接 69、可推导 4，合计 **73/258（28.3%）**；未确认 185。
- 人工抽样：30 格来自未确认、10 格来自已确认；BLIND_REVIEW 已交付，**人工复核未返回**。
- 因此 V2 暂不扩大可答清单；73 格保持，185 格标为待核。若后续人工确认新依据，再更新分母。

### 抽样构成

| 层 | 抽样 | 状态 |
|---|---:|---|
| 未确认 | 30 | 待人工 |
| 已确认 | 10 | 待人工 |
| 合计 | 40 | — |

## 2. 三模型同分母（73 格）

| 模型 | 可答答对 | 可答分母 | 可答准确率 | 全字段 |
|---|---:|---:|---:|---:|
| Qwen | 29 | 73 | 39.7% | 73/258 |
| Gemma | 32 | 73 | 43.8% | 85/258 |
| Llama | 26 | 73 | 35.6% | 63/258（恢复 5/6） |

Llama 的可答分母按 73 计；0008 空回答，相关格按错计。

## 3. 逐场（可答/43）

| match | 可答 | Qwen | Gemma | Llama |
|---|---:|---:|---:|---:|
| 0003 | 16 | 10 | 10 | 未单列 |
| 0008 | 12 | 5 | 5 | 空 |
| 0010 | 12 | 1 | 3 | 未单列 |
| 0012 | 11 | 4 | 6 | 未单列 |
| 0015 | 11 | 5 | 3 | 未单列 |
| 0017 | 11 | 4 | 5 | 未单列 |

Llama 逐场未按同分母拆出，只报 26/73；下一轮补齐。

## 4. 格式与恢复

- Llama 旧协议 0/6 直接解析；嵌套 JSON 5/6 可恢复，0008 空；内容 63/258。
- Qwen/Gemma 6/6 解析，无缺行。
- 闭合约束：schema 缺 extras 合计与 bat_sum，记为不可检查。

## 5. 限制

- 73 格是启发式，不是人工确认；40 格抽样未返回。
- 可答准确率的分母固定 73；Llama 的 26/73 含 0008 的错计。

---

# 附录 C：SHORT_EVIDENCE_RESULTS

# SHORT_EVIDENCE_RESULTS：两场真短证据对照

日期：2026-11-13。18 次本地请求，外部 API 0。

## 1. 实际发送

| 项 | 0014 | 0016 |
|---|---|---|
| A 长度 | 5,314 | 4,313 |
| B/C 长度 | 572 | 571 |
| B 片段 | 6 | 6 |
| 终局 | Harbor Peninsula XI closed on 226 for 7 | Crestline XI closed on 138 for 3 |
| B=C 正文 | 是 | 是 |
| 更新后 figures 泄露 | 无 | 无 |

B 确实是短证据，不再是标注全文。18 条全部解析成功（A/B/C 三模型）。

## 2. 结果（2 场）

| 模型 | A two | B two | C two | B total | C total |
|---|---:|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0/2 | 1/2 | 2/2 |
| Llama | 0/2 | 0/2 | 0/2 | 1/2 | 0/2 |
| Gemma | 0/2 | 0/2 | 0/2 | 1/2 | 1/2 |

- B 的两名投手同时正确 **0/6**；A 也是 0/6；B−A=0。
- B 的总出局 3/6（每家 1/2），A 为 0/6；短证据帮助读总数，但没有帮助两人更新。
- C 的 two 0/6；Qwen C 总数 2/2，但两人仍错。

## 3. 错法

- B：Qwen/Gemma 两场都是两人旧值；Llama 一场旧值、一场只加新投手。
- C：Qwen 一场只减原投手、一场两人都改但错；Llama 一场格式/旧值、一场旧值；Gemma 两场格式失败。
- C 的 extraction：6/6 无法执行（每家 2/2 缺字段）；没有可执行的抽取。

## 4. 程序

- 用模型实际抽取做 Python 更新：two 0/6，three 0/6；修对 0、改坏 0、无法执行 6。
- 用正确结构化输入做正控：两场 two/three 都为 1（程序本身正确）。

## 5. 结论

真短证据在这两场上没有表现出“比全文更容易改对两人”：B 0/6。  
但 B 把总出局从 0/6 提到 3/6，说明短证据至少让总数可读；失败集中在“两人旧值/只改一侧”，不是终局定位。  
两场只能判断通路，不能作为跨比赛结论。

---

# 附录 D：BLIND_REVIEW（40 格抽样）

# BLIND_REVIEW：43 字段可答性抽查（40 格）

复核者先独立作答，再与 scorecard 对账。题面只给发布版 commentary 路径与相关句，不展示模型预测。

排名规则（旧任务）：按 scorecard 的 runs/wickets 降序；并列时按 scorecard 行序；旧提示未写并列规则，这一点需复核者判断。

## S01 match_0003 inn1.no_balls
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.no_balls；指定局别按字段名；金标不展示
- 相关句：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
  - Their 49-run stand was not huge in isolation, but it was huge in its position because it moved Ridgehaven from 80 for 4 to 129 for 5 and changed the chase from fragile to controllable.
  - Isaac Wells’ 3 for 25 had made the chase restart several times, Jordan Pike removed the launch batter, Gareth Bishop and Harvey Stone each found important wickets, and Cross’s earlier 81 had given them a real score to defend.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S02 match_0008 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S03 match_0010 inn2.bat3_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.bat3_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S04 match_0012 inn1.wides
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.wides；指定局别按字段名；金标不展示
- 相关句：
  - Chasing 248, Westmere needed to remove the early danger first, and Ethan Vale did that with a calm that became more damaging the longer he stayed.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S05 match_0015 inn2.wides
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.wides；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S06 match_0017 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S07 match_0003 inn2.byes
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn2.byes；指定局别按字段名；金标不展示
- 相关句：
  - The third-wicket stand of 70 did exactly what Brookmere needed because it changed the scoreboard from emergency repair into something with potential.
  - Lucas Bennett was still there, and his 37 had done a lot of the early work, but Jordan Pike removed him at 80 and that was the moment the chase could have turned properly awkward.
  - Their 49-run stand was not huge in isolation, but it was huge in its position because it moved Ridgehaven from 80 for 4 to 129 for 5 and changed the chase from fragile to controllable.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S08 match_0008 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S09 match_0010 inn1.bowl2_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn1.bowl2_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S10 match_0012 inn1.overs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.overs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S11 match_0015 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S12 match_0017 inn1.total_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.total_runs；指定局别按字段名；金标不展示
- 相关句：
  - Mason’s tiny but rapid contribution mattered, but Miles was the hand that moved the innings from nearly finished to genuinely defensible, carrying Ridgevale to 174 all out in the forty-fourth over.
  - Ridgevale advanced because they survived their weakest phase, made Sandmere chase more than they expected, and then used Miles Carter’s spell to make 174 feel less like a modest total and more like a trap that closed every time Sandmere tried to step through it.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S13 match_0003 inn1.bowl2_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.bowl2_wickets；指定局别按字段名；金标不展示
- 相关句：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
  - He bowled Felix, then removed Gareth Bishop almost at once, and that double hit at 137 froze what could have become a 175-type finish.
  - His 81 from 56 had both rescue and acceleration inside it, built from the early wobble, stretched through the middle, and then pushed hard when Brookmere needed the late lift.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S14 match_0008 inn1.total_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.total_runs；指定局别按字段名；金标不展示
- 相关句：
  - Coral Coast finished on 262 for eight, a total that felt less like a straight batting display than a repaired and rebuilt innings, shaped first by Lucas Hart’s patience, then by Adrian Blake’s acceleration, then by a final cluster of smaller but useful pushes.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S15 match_0010 inn2.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S16 match_0012 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S17 match_0015 inn2.byes
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.byes；指定局别按字段名；金标不展示
- 相关句：
  - Adrian Clarke threw a few late shots, Mason Reid helped drag the total further, but by then the match had turned from chase into resistance, and when Mason was run out at 279, Ridge Falcons had completed a 65-run win and advanced.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S18 match_0017 inn1.bat2_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.bat2_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S19 match_0003 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S20 match_0008 inn1.bat3_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.bat3_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S21 match_0010 inn1.bowl2_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn1.bowl2_wickets；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S22 match_0012 match.result
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：match.result；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S23 match_0015 inn2.no_balls
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.no_balls；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S24 match_0017 inn2.wides
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn2.wides；指定局别按字段名；金标不展示
- 相关句：
  - The margin of 68 runs makes the match look clearer than it had felt when Ridgevale were nine down, but that is the point of the story: Sandmere won most of the first innings and still lost the match because Miles Carter changed both halves.
  - His unbeaten 48 gave Ridgevale a total with teeth; his five wickets turned a chase that should have been manageable into a procession of restarts.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S25 match_0003 inn2.bowl2_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn2.bowl2_wickets；指定局别按字段名；金标不展示
- 相关句：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
  - He bowled Felix, then removed Gareth Bishop almost at once, and that double hit at 137 froze what could have become a 175-type finish.
  - His 81 from 56 had both rescue and acceleration inside it, built from the early wobble, stretched through the middle, and then pushed hard when Brookmere needed the late lift.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S26 match_0008 inn1.bowl1_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.bowl1_wickets；指定局别按字段名；金标不展示
- 相关句：
  - Coral Coast finished on 262 for eight, a total that felt less like a straight batting display than a repaired and rebuilt innings, shaped first by Lucas Hart’s patience, then by Adrian Blake’s acceleration, then by a final cluster of smaller but useful pushes.
  - Chasing 263, Ridgeview needed a calm opening and one serious middle-order partnership.
  - They were under pressure at 27 for two, rebuilt through Lucas Hart and Nathan Wells, sharpened through Adrian Blake and Marcus Shaw, then defended through a layered attack: Mason Hale for the first incision, Luke Barrett for the middle collapse, Evan Reed for the main repair stand, and Ryan Frost for the closing pressure.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S27 match_0010 inn2.overs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.overs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S28 match_0012 inn2.bat3_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn2.bat3_name；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S29 match_0015 inn1.bowl1_runs
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn1.bowl1_runs；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S30 match_0017 inn1.bat2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.bat2_name；指定局别按字段名；金标不展示
- 相关句：
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S31 match_0003 inn1.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.team；指定局别按字段名；金标不展示
- 相关句：
  - Seabank Cricket Ground in Stonehaven had that sharp feel from the first over, not quite evening yet but already narrow enough in the light for every fielder in the ring to look a little closer than he really was, and Ridgehaven’s decision to field first felt less like a gamble than a test of whether Brookmere’s top order could survive pressure before the ball softened.
  - He did not go hunting for magic, he just kept forcing Aiden Cole and Brandon Hale to play from uncomfortable positions, a length neither fully forward nor comfortably back, and Brookmere’s opening stand never really became a launch even though the score moved with a few early extras.
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start choosing risks.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S32 match_0008 inn2.bat1_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn2.bat1_name；指定局别按字段名；金标不展示
- 相关句：
  - Aiden Cole gave Ridgeview their one proper argument.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S33 match_0010 inn2.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn2.team；指定局别按字段名；金标不展示
- 相关句：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediately into uncomfortable batting rather than the clean first-use rhythm they would have wanted.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S34 match_0012 inn1.bowl2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn1.bowl2_name；指定局别按字段名；金标不展示
- 相关句：
  - Liam Frost removed Adrian, Lucas Vale pinned Caleb after he had started to settle, and the score was pushed back into repair mode again.
  - Lucas Vale’s two wickets gave Westmere important middle control, Noah Grant cut into the scoring sequence, and Zane Foster’s wicketless spell still mattered because it gave Westmere ten overs of dry pressure that denied Dune Harbor an easy acceleration phase.
  - Connor then fell after doing his structural work, and Lucas Vale was bowled before the finish, so the scorecard retained enough late movement to avoid looking like a stroll.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S35 match_0015 inn2.bowl2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0015/commentary.txt
- 目标字段：inn2.bowl2_name；指定局别按字段名；金标不展示
- 相关句：
  - Caleb Rourke arrived and changed the middle overs.
  - Noah Grant kept finding the wickets that mattered around the lower middle, Daniel Cross removed Zane before his burst could grow, and Caleb Rourke returned with the ball to close down the last organized resistance, first taking Connor with his own hands and then removing Evan when the late counterpunch still carried a little danger.
  - Caleb Rourke’s player-of-the-match award fits because his seventy-four made the first innings heavy at the exact time it might have slowed, and his two wickets later removed the last serious structure from Coastal’s reply.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S36 match_0017 inn1.bowl2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0017/commentary.txt
- 目标字段：inn1.bowl2_name；指定局别按字段名；金标不展示
- 相关句：
  - Zach Foster’s spell was the visible cutting edge through the middle-late section, not always perfectly cheap, but constantly dangerous, while Ethan Parker kept hitting the card in ways that stopped any repair from becoming a platform.
  - He trapped Aiden, then Liam Reed, then Ryan Cole, and the innings folded for 106 in the twenty-ninth over, Ethan Parker stranded at the end with only a small late touch.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S37 match_0003 inn1.total_wickets
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0003/commentary.txt
- 目标字段：inn1.total_wickets；指定局别按字段名；金标不展示
- 相关句：
  - By the time Caleb Price bowled Drake at 87, the innings had not fully broken free, but it had stopped bleeding.
  - His 81 from 56 had both rescue and acceleration inside it, built from the early wobble, stretched through the middle, and then pushed hard when Brookmere needed the late lift.
  - Harvey Stone and Isaac Wells still squeezed enough from the last few balls to drag Brookmere to 164 for 8, but the innings had been contained just enough.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S38 match_0008 inn1.bat2_name
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0008/commentary.txt
- 目标字段：inn1.bat2_name；指定局别按字段名；金标不展示
- 相关句：
  - Adrian Blake then arrived and shifted the tone.
  - Coral Coast finished on 262 for eight, a total that felt less like a straight batting display than a repaired and rebuilt innings, shaped first by Lucas Hart’s patience, then by Adrian Blake’s acceleration, then by a final cluster of smaller but useful pushes.
  - They were under pressure at 27 for two, rebuilt through Lucas Hart and Nathan Wells, sharpened through Adrian Blake and Marcus Shaw, then defended through a layered attack: Mason Hale for the first incision, Luke Barrett for the middle collapse, Evan Reed for the main repair stand, and Ryan Frost for the closing pressure.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S39 match_0010 inn1.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0010/commentary.txt
- 目标字段：inn1.team；指定局别按字段名；金标不展示
- 相关句：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediately into uncomfortable batting rather than the clean first-use rhythm they would have wanted.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

## S40 match_0012 inn2.team
- 原文：D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches\match_0012/commentary.txt
- 目标字段：inn2.team；指定局别按字段名；金标不展示
- 相关句：
  - At Eastbank Meadow Ground in Hillview, Westmere XI won the toss and chose to field, and the call had the feel of a side trusting the first hour rather than guessing at the day, because the surface looked playable from the rope but still carried enough early seam and uneven pace to make Dune Harbor XI work before they could score freely.
- 你的答案：____；证据位置：____；判定（直接/推导/不足/冲突）：____

---

# 附录 E：REPRODUCE

# REPRODUCE

## 抽样与只复算（0 次模型调用）

python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/sample.py
python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/score_short.py

## 短证据构建与补跑（18 次）

python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/build_short.py
python VETT_INTEGRATED_20261113/analysis/answerability_and_short_evidence/runner_short.py

## 输出

- short_samples.json、runs/short.jsonl
- short_scores.json
- sample.json、BLIND_REVIEW.md

本轮新增调用 18/18。


---

## 附录 A15：A/B/C 实际输入审计

> 原文件：VETT_INTEGRATED_20261113/analysis/input_and_score_audit/ACTUAL_INPUT_AUDIT.md（47 行）

# ACTUAL_INPUT_AUDIT：A/B/C 实际发送内容核对

日期：2026-11-13。0 次模型调用。逐请求明细见 requests.jsonl（54 条）。

## 0. 结论

- 54/54 条请求的当前 runner 重建提示 SHA-256 与 runs/dev.jsonl 保存的 prompt_sha256 完全一致：可确认实际发送的就是这套文本。
- **54/54 条 B、C 实际收到的是“全文 + 六个 [EVIDENCE] 标记”，不是设计所说的六句短证据。** B 去掉标记后与 A 逐字一致；C 的正文与 B 完全相同，区别只在提示多了分步 extraction 要求。
- 终局证据有 4/6 场属于错误局或非终局：0009 用第一局 96/5，0014 用第一局 212/7，0016 用第一局 34/3，0013 用“were 263/8, innings nearly done”。0018、0027 的终局句正确。
- 因此上一轮 B/C 的 0/18 是“标注全文 + 部分错误终局”的结果，不能当作短证据结论。

## 1. 逐请求

| 项目 | 结果 |
|---|---|
| 对齐 | 6 场 × 3 条件 × 3 模型 = 54 |
| 请求凭据 | runs/dev.jsonl 的 prompt_sha256 与重建 SHA 一致 54/54 |
| 文本 | B/C 长度 4,379–6,085 字符，A 4,313–6,019；B/C 是 A 加标记 |
| 标记 | 54/54 有 6 个 [EVIDENCE] |
| C 与 B | 54/54 C 正文 == B 正文 |
| 终局 | 4/6 错误（0009、0013、0014、0016）；0018、0027 正确 |
| 判定 | 条件发错：B/C 不是短证据；终局证据部分错误 |

## 2. 差异出在哪一层

1. **构建产物**：build_dev.py 把 B 构造成 A 逐句加标记，C=B；没有生成六句摘录。
2. **runner 选择**：runner 用 s["B"]/s["C"]，因此实际发送的就是标注全文。
3. **实际请求**：哈希证明发送文本与构建产物一致。
4. **盲审附件**：BLIND_REVIEW 同样展示 A 全文与 B 全文，没有短版。

结论：不是导出或报告单层错误，而是构建层就把 B/C 做成了标注全文；报告又把 B/C 描述成短证据。

## 3. 终局证据逐场

| match | 实际证据 | 问题 |
|---|---|---|
| 0009 | 96/5 | 第一局中途，正确应为 Coral Bay XI closed on 187 for 5 |
| 0013 | Silver Pearl XI were 263/8, innings nearly done | 非终局措辞 |
| 0014 | Canyon Stars XI were 212/7 | 第一局，正确应为 Harbor Peninsula XI closed on 226 for 7 |
| 0016 | Pearlbridge XI at 34/3 | 第一局，正确应为 Crestline XI closed on 138 for 3 |
| 0018 | Harborline XI closed on 252 for 10 | 正确 |
| 0027 | Highland Isle closed on 52 for 10 | 正确 |

## 4. 待核

- 没有保存原始 HTTP 消息，只有提示哈希与原始回答；哈希一致足以证明当前代码可重建发送文本，但不能证明运行环境没有其他系统消息注入。
- 0008 的 Llama 整表原始回答为空，无法恢复。


---

## 附录 A16：Attribution Followup 结果

> 原文件：VETT_INTEGRATED_20261113/analysis/attribution_followup/RESULTS.md（121 行）

# Attribution Followup 结果：新比赛上的改判更新

日期：2026-11-13。本地 Ollama 三模型，实际 120/120 次请求，外部 API 0。旧结果与原始语料未修改。

## 0. 结论

- **旧值保留在新比赛上复现**：全文推导版（旧汇总 + 改判通知）在 8/8 场比赛、3/3 模型上，三项绝对值同时正确为 **0/24**。
- **缩短证据帮助两个模型，但不帮助 llama**：短证据版三项同时正确 qwen **7/8**、gemma **7/8**、llama **1/8**；从 0/24 提升到 **15/24**。
- **程序更新没有多做对**：抽取+Python 更新在 qwen 0/8、llama 1/8、gemma 0/8；抽取值本身不可靠，未发现“程序更新引入新错”之外的收益。
- **题面有两个真实问题**：runs 字段名歧义（batting runs vs bowling runs conceded）；innings_total_wickets 被误读为总得分。已用修正字段名的小样本验证。

## 1. 设置

| 项 | 值 |
|---|---|
| 模型 | qwen2.5:7b-instruct-q4_K_M、llama3.1:8b、gemma2:9b |
| 解码 | temperature=0，seed=20261112，num_ctx=8192，num_predict=320 |
| 比赛 | match_0003、0008、0010、0012、0015、0017、0026、0030（8 场，均未用于前两轮） |
| 版本 | explicit / derivation / short |
| 字段 | A_wickets、A_runs、B_wickets、B_runs、innings_total_wickets |
| 主指标 | A_wickets、B_wickets、innings_total_wickets 三项同时正确 |
| 调用 | main 72 + Lina 9 + retest 6 + method 24 + smoke 1 + fix 8 = 120 |

样本为 scorecard 确定性重渲染（seed=0），是**基于比赛记录构造的改判**，不是真实赛果更正。每场一次命名出局：原记 A，改判 B；A 的 wickets −1、B +1，runs 与全队 total 不变。

## 2. 主结果：三项绝对值同时正确

| 模型 | explicit | derivation | short |
|---|---:|---:|---:|
| qwen2.5:7b | 4/8 | **0/8** | **7/8** |
| llama3.1:8b | 3/8 | **0/8** | 1/8 |
| gemma2:9b | 7/8 | **0/8** | **7/8** |

逐场：

| match | qwen E/D/S | llama E/D/S | gemma E/D/S |
|---|---|---|---|
| match_0003 | T/F/T | F/F/T | F/F/T |
| match_0008 | F/F/T | F/F/F | T/F/T |
| match_0010 | F/F/T | F/F/F | T/F/T |
| match_0012 | T/F/T | F/F/F | T/F/T |
| match_0015 | F/F/T | T/F/F | T/F/T |
| match_0017 | T/F/T | F/F/F | T/F/F |
| match_0026 | T/F/F | T/F/F | T/F/T |
| match_0030 | F/F/T | T/F/F | T/F/T |

## 3. 错法分类（三项绝对值）

| 模型 | 版本 | both_old | only_new_plus1 | only_orig_minus1 | both_updated_wrong |
|---|---|---:|---:|---:|---:|
| qwen | derivation | 3 | 1 | 0 | 4 |
| llama | derivation | 2 | 2 | 0 | 4 |
| gemma | derivation | 6 | 0 | 0 | 2 |
| qwen | short | 0 | 0 | 0 | 1 |
| llama | short | 5 | 0 | 0 | 2 |
| gemma | short | 0 | 0 | 0 | 1 |

读法：推导版的失败不是单一方向。gemma 以“两人都旧值”为主（6/8）；qwen/llama 更多是“都改了但值错”或“只加新投手”。

## 4. 题面问题：runs 与 total 的歧义

原始字段名是 A_runs / B_runs 与 innings_total_wickets；提示只把下划线换成空格。结果：

- 全文中 “Nora ... 4 for 6” 的 6 被部分模型读成击球得分；Lina 原题 qwen 输出 Nora_runs=92（Nora 的击球得分），不是失分 6。
- innings_total_wickets 被 llama 读成该局总得分：match_0003 输出 164、0008 输出 262、0010 输出 282、0012 输出 247、0017 输出 174。
- 因此 **explicit/derivation 的 runs 与 five 指标受污染**，不能作为“失分更新”结论；three-absolute 的 wickets 部分仍有效，但 total 对 llama 也受污染。

修正字段名的小样本（8 次，已计入 120）：

| 检查 | 结果 |
|---|---|
| Lina original（Nora_Vale_runs_conceded 等）qwen | 4/6、3/7、10 全对（五项） |
| Lina explicit qwen | 3/6、4/7、10 全对 |
| Lina derivation qwen | 仍 4/6、3/7、10（旧值） |
| Lina original/explicit/derivation gemma | 同 qwen：前两版全对，推导版旧值 |
| explicit match_0003 qwen（修正字段） | 3/28、2/28、8 全对 |
| explicit match_0003 llama（修正字段） | wickets/runs 对，total 仍输出 164 |

所以：
- runs 歧义可通过命名修复；修复后 qwen/gemma 的 runs 正确。
- **推导失败不是 runs 歧义造成的**：修正字段后，qwen/gemma 的推导版仍保留旧值。
- llama 的 total 歧义即使加 “not runs” 提示仍存在，属于模型侧的字段绑定错误。

## 5. Lina 开发样例（修正字段后）

| 版本 | qwen | gemma | 说明 |
|---|---|---|---|
| original | 4/6、3/7、10 五项全对 | 同 qwen | 正控 |
| explicit | 3/6、4/7、10 五项全对 | 同 qwen | 直接给新值 |
| derivation | 4/6、3/7、10（旧值） | 同 qwen | 只给旧值+通知，仍失败 |

llama 未在修正字段上重跑（预算耗尽）；其原始 Lina 行为与 qwen 一致（旧值）。

## 6. 方法对照：抽取 + Python 更新

- 抽取提示要求 batter、原/新投手、双方旧 wickets/runs、总出局。runner 按 fields 键判定 parse，导致 parse_ok=0/8，但实际 doc 多数有键。
- 抽取值本身不可靠：qwen match_0003 抽到 orig_wickets=2（gold 4）、orig_runs=17（28）、new_runs=102；llama 抽到 1/4、1/4；gemma 全 None。
- 三项同时正确：qwen 0/8、llama 1/8、gemma 0/8；与 short 版（7/1/7）相比没有收益。
- 结论：当前抽取程序不能作为“表格更新方法”的有效对照；它失败在证据抽取，不是 Python 更新。

## 7. 重测

- qwen：2 场 × 5 字段全部一致（5/5、5/5）。
- llama：5/5、5/5。
- gemma：match_0003 3/5（2 个字段漂移）、match_0017 5/5。
说明 qwen/llama 在该设置下稳定；gemma 有少量运行波动。

## 8. 四句话

1. **改判错误在 8/8 场新比赛、3/3 个模型上重现**：全文推导版三项同时正确 0/24；明确“两人都旧值”的场次为 qwen 3、llama 2、gemma 6。
2. **缩短证据后明显改善**：qwen 0→7/8、gemma 0→7/8、llama 0→1/8，总体 0→15/24；qwen/gemma 的瓶颈更像“全文里定位并关联旧记录与改判通知”，llama 连短证据也失败。
3. **程序更新没有多做对**：抽取+Python 在 qwen 0/8、llama 1/8、gemma 0/8；抽取值本身错误，未发现可归功于更新的新增正确场次，也没有在原本正确的字段上引入新错（因为它几乎不产出正确更新）。
4. **下一轮最值得验证的是证据定位/事件抽取，而不是继续加表格后处理**：先测模型能否从全文找出“哪次出局、原投手、新投手、改判前数值”，再决定是否做按事件记账；llama 需要单独检查字段绑定（total 被读成得分）。

## 9. 文件

- DESIGN.md、BLIND_REVIEW.md、ANSWER_KEY.md
- samples.json、lina.json
- runs/main.jsonl、lina.jsonl、retest.jsonl、method.jsonl、smoke.jsonl、fix.jsonl
- final_scores.json、fix_scores.json
- runner.py、score.py、finalize.py、build_samples.py、build_lina.py


---

## 附录 A17：证据标注跟进结果

> 原文件：VETT_INTEGRATED_20261113/analysis/attribution_evidence_followup/RESULTS.md（88 行）

# RESULTS：证据标注跟进（开发集 + 留出集）

日期：2026-11-13。本地 Ollama，实际 120/120，外部 API 0。历史结果只读。

## 0. 结论

- **只在全文中标出原句（B）没有帮助**：开发 8 场、留出 6 场、3 个模型，B−A 在“两名投手同时正确”上全部为 0；三项同时正确也全部为 0。
- C（摘出标记句）在“总出局数”上略好（gemma +1、llama +2、qwen +2 场），但两名投手仍 0/8；且 C 漏了“figures are the pre-revision record”的 Note，属于构建缺陷，不能作为“证据足够”的严格结论。
- Lina 修正字段后：gemma original/explicit 五项全对，derivation 仍旧值；qwen 出现字段名坍缩（输出 wickets_credited 等泛化键），协议失败。
- 重测 6/6 全一致。

## 1. 旧结果复算（详见 BASELINE_REANALYSIS.md）

- 三项同时正确 0/24；两名投手都旧值且总数正确 **11/24**；只要求两人旧值则 18/24。
- 推导→短证据 two_wickets：qwen 7 场错→对，gemma 7，llama 1；没有对→错。
- Llama 短证据 1/8：唯一正确的 match_0003 总数也正确；“两人已对但总数错”为 0；其余是 5 场两人旧值、2 场都改但值错。
- 旧 method 的 parse_ok=0/8 是 runner 用 fields 键误判；doc 实际 8/8 可解析，但抽取值错，Python 更新后 qwen 0/8、llama 1/8、gemma 1/8。

## 2. 开发集 A/B/C（8 场）

| 模型 | 条件 | two_wickets | total | three |
|---|---|---:|---:|---:|
| qwen | A | 0/8 | 2/8 | 0/8 |
| qwen | B | 0/8 | 2/8 | 0/8 |
| qwen | C | 0/8 | 4/8 | 0/8 |
| llama | A | 0/8 | 6/8 | 0/8 |
| llama | B | 0/8 | 6/8 | 0/8 |
| llama | C | 0/8 | 8/8 | 0/8 |
| gemma | A | 0/8 | 7/8 | 0/8 |
| gemma | B | 0/8 | 7/8 | 0/8 |
| gemma | C | 0/8 | 8/8 | 0/8 |

## 3. 留出集 A/B（6 场）

| 模型 | A two | B two | A total | B total |
|---|---:|---:|---:|---:|
| qwen | 0/6 | 0/6 | 3/6 | 2/6 |
| llama | 0/6 | 0/6 | 3/6 | 3/6 |
| gemma | 0/6 | 0/6 | 3/6 | 3/6 |

B−A 在 two_wickets 上为 0；total 上 qwen −1、llama 0、gemma 0。

## 4. 配对变化

- B−A（开发）：two_wickets 从错到对 0 场，从对到错 0 场；three 同样 0。
- B−A（留出）：two_wickets 0/0；total qwen 1 场从对到错，其余无变化。
- C−B（开发）：two_wickets 0/0；total gemma +1、llama +2、qwen +2；但 C 缺 pre-revision Note，收益不能归因于“证据足够”。

## 5. 错法

开发 A/B：

- gemma：both_old 7/8，both_updated_wrong 1/8。
- llama：both_old 4/8，only_new_plus1 2/8，both_updated_wrong 2/8。
- qwen：both_old 6/8，only_new_plus1 1/8，format 1/8（B 条件 format 2/8）。

留出 A/B：

- gemma：both_old 6/6。
- llama：A both_old 5、only_new 1；B both_old 4、only_new 1、both_updated_wrong 1。
- qwen：A both_old 3、both_updated_wrong 2、format 1；B both_old 4、both_updated_wrong 1、format 1。

典型样例：match_0008（Luke Barrett 3→2、Ryan Frost 3→4、total 10）。gemma A/B 都输出 3、3、10；qwen A/B 都输出 3、3、8；llama A 输出 4、4、10，B 输出 4、4、10；C 只有 llama 改成 3、4、10。标注没有让 gemma/qwen 更新。

## 6. Lina

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 字段名坍缩，协议失败 |
| explicit | 3/6、4/7、10 五项全对 | 同上 |
| derivation | 4/6、3/7、10 旧值 | 同上 |

gemma 能抄更新后的数字，但不能应用改判；qwen 的失败是输出键不合法，不能作为能力读数。

## 7. 重测

qwen/llama/gemma 在 match_0008、match_0017 的 A 条件均 5/5 一致。

## 8. 四句话

1. **同样的全文里只标出原句，在 0 场新比赛、0 个模型上有帮助**：开发 8 场和留出 6 场的 B−A 在两名投手同时正确上都是 0，三项同时正确也都是 0；B 与 A 的输出逐场相同或几乎相同。
2. **开发集里删掉其他正文（C）只多做对了总出局数（gemma +1、llama +2、qwen +2 场），两名投手仍是 0/8**；但 C 漏了“旧汇总是改判前记录”的 Note，这个收益不能当作“证据足够”的证据，需修正后重跑。
3. **剩余错误主要不是“找不到证据”**：A/B 全文相同、只多标记，模型仍以两人旧值为主（gemma 7/8、qwen 6/8、llama 4/8）；Lina 的 gemma 在明示版能抄 3/6、4/7，推导版回到 4/6、3/7，说明卡在“把改判应用到最终数值”，不是读不到数字。
4. **220 场整表评测还差三件**：原始解说与 scorecard 的字段映射、可靠计分范围（目前 28 个核心字段，完整表约 450 cell 需要分块输出）、以及输出预算/截断控制；下一轮最值得投入的是“改判应用/事件更新”的结构化对照，而不是继续加证据标注。

## 9. 构建缺陷的影响

C 未包含 A 中“the bowling figures above are the pre-revision record”的 Note，导致 C 的旧汇总没有状态标签。C 的 total 改善只能作为探索性观察；C 的 two_wickets 0/8 不能解释为“给了足够证据仍失败”，因为证据并不完整。A/B 的比较不受此影响。


---

## 附录 A18：修好的完整短证据与整表回投

> 原文件：VETT_INTEGRATED_20261113/analysis/attribution_update_and_full_table/ATTRIBUTION_RESULTS.md（71 行）

# ATTRIBUTION_RESULTS：修好的完整短证据能否救回改判

日期：2026-11-13。6 场开发比赛 × A/B/C × 3 模型 = 54 次；Lina 6 次；重测 6 次。历史 0/42 保留。

## 0. 结论

- **修好的完整短证据（B）仍未救回改判**：B 的两名投手同时正确 0/18；A 也是 0/18；B−A=0。
- C 的分步作答只有 gemma 在 match_0014 做对两名投手（1/6），其余 0/6。
- C 的抽取+Python 更新：0 场修对、0 场改坏、1 场无法执行（gemma/qwen 各 1 场缺字段）；抽取本身几乎都错。
- 主要错法仍是两人都旧值：A/B 中 gemma 6/6、qwen 6/6、llama 3/6（A）与 5/6（B）。

## 1. 开发集（6 场）

| 模型 | 条件 | two_wickets | total | three | runs | five |
|---|---|---:|---:|---:|---:|---:|
| qwen | A | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| qwen | B | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| qwen | C | 0/6 | 2/6 | 0/6 | 4/6 | 0/6 |
| llama | A | 0/6 | 4/6 | 0/6 | 6/6 | 0/6 |
| llama | B | 0/6 | 4/6 | 0/6 | 6/6 | 0/6 |
| llama | C | 0/6 | 2/6 | 0/6 | 6/6 | 0/6 |
| gemma | A | 0/6 | 3/6 | 0/6 | 6/6 | 0/6 |
| gemma | B | 0/6 | 3/6 | 0/6 | 6/6 | 0/6 |
| gemma | C | 1/6 | 3/6 | 0/6 | 6/6 | 0/6 |

B−A 在 two_wickets、total、three 上均为 0。C−B 只有 gemma 的 two +1。

## 2. 错法

A/B：

- gemma：both_old 6/6（A、B 都是）。
- qwen：both_old 6/6。
- llama：A both_old 3、only_new_plus1 1、both_updated_wrong 2；B both_old 5、only_new_plus1 1。

C：

- gemma：both_old 3、only_new 1、only_orig 1、both_updated_wrong 1（其中 match_0014 两人都对）。
- llama：both_old 4、only_new 1、both_updated_wrong 1。
- qwen：both_old 1、both_updated_wrong 3、format 2。

## 3. C 的同一输出：模型最终值 vs Python 更新

| 模型 | 程序更新三项正确 | 修对 | 改坏 | 同 | 无法执行 |
|---|---:|---:|---:|---:|---:|
| qwen | 0/6 | 0 | 0 | 5 | 1 |
| llama | 0/6 | 0 | 0 | 6 | 0 |
| gemma | 0/6 | 0 | 0 | 5 | 1 |

抽取值普遍错（人物或旧值），所以程序没有可执行的正确输入；没有“程序修好”的场次，也没有“程序改坏”的场次。

## 4. Lina 通路

| 版本 | gemma | qwen |
|---|---|---|
| original | 4/6、3/7、10 五项全对 | 4、3、9（two 对，total 错） |
| explicit | 3/6、4/7、10 五项全对 | 3、4、9（two 对，total 错） |
| derivation | 4/6、3/7、10 旧值 | 4、3、9（two 对，total 错） |

qwen 在 Lina 上能读对两人 wickets，但 total 恒定 9；gemma 明示版能抄，推导版回旧值。

## 5. 重测

qwen/llama/gemma 在 match_0014、match_0016 的 A 条件均 5/5 一致。

## 6. 四句话

1. **修好的完整短证据让 0 个模型、0 场多做对两名投手**：B 的 two_wickets 0/18，A 也 0/18，B−A=0；总出局数 B 与 A 相同（qwen 2/6、llama 4/6、gemma 3/6）。
2. **最常见错误是两人都旧值**（gemma 6/6、qwen 6/6、llama 3/6），其次是只加新投手、两人都改但值错；C 的分步作答只在 gemma 的 match_0014 修对两人，其余仍错。
3. **Python 用同一份抽取修好 0 场、改坏 0 场、1 场无法执行**；抽取本身几乎都错，程序没有正确输入可更新。
4. **下一轮应先修“抽取协议/人物绑定”**：让模型稳定输出 orig/new 两人的旧值和事件，再谈程序更新；否则分步作答只会增加格式负担。


---

## 附录 A19：小模型诊断 v1 完整报告

> 原文件：VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/COMPLETE_REPORT.md（480 行）

# VETT 小模型诊断 v1：完整报告

日期：2026-11-13  
范围：43 字段 V3 复核、两场抽取诊断、数据集升级  
调用：新增 6/24 次；外部 API 0。

## 0. 一页摘要

- 同一份 B 短证据：直接最终值 two **0/6**；纯抽取 6/6 全部正确（出局者、原/新投手、方向、两个旧 wicket）；用实际抽取做 Python 更新，**two 6/6**。
- 具体错误是**最终值更新**，不是读旧数、认人或弄反方向。
- 43 字段 V3 仍为 73/258；Qwen 29/73、Gemma 32/73、Llama 26/73；185 待核。
- 40 格盲审已升级为全文 + 段号 + 候选句；人工未返回。
- 数据集升级：新增“同一 B 文本 + 纯抽取”配对条件；C 拆成纯抽取；评分分 identity/direction/old/final/program 五步。

## 1. 诊断核心

| 环节 | 结果 |
|---|---|
| JSON 解析 | 6/6 |
| 五键齐全 | 6/6 |
| 出局者正确 | 6/6 |
| 原/新投手正确 | 6/6 |
| 方向正确 | 6/6 |
| 两个旧 wicket 正确 | 6/6 |
| 程序更新后 two | 6/6 |
| 直接最终值 two | 0/6 |

0014：Quinn 2→1、Frost 2→3；0016：Reed 2→1、Wells 1→2。  
同一文本、同一模型，抽取全对而最终值全错，说明模型知道事件，但不会把 −1/+1 落到最终答案。

## 2. 43 字段

- 73/258 可答（69 直接 + 4 可推导）；185 待核。
- 新增“同一句比分支持 total”规则，258 格变更 0。
- Qwen 29/73、Gemma 32/73、Llama 26/73；全字段 73/85/63。
- 40 格盲审全文已交付，人工未返回。

## 3. 四句话

1. **具体错误是最终值更新**：三个模型、两场比赛、6 条直接作答全部 two 错；同一文本纯抽取 6/6 正确。
2. **用同一 B 文本、同一模型做“直接最终值 vs 纯抽取”对照**，把“读证据”与“算最终值”分开；身份/方向/旧值全对而最终值全错，排除题面歧义和格式失败。
3. **数据集升级为配对条件**：保留直接输出，另加纯抽取 + Python 更新；C 不再一次要求 extraction+final；评分拆成五步。
4. **下一轮最值得验证“直接 vs 抽取+程序”在新比赛上的差异**：2 场 ×2 条件 ×3 模型 =12 次，需预先选 2 场干净比赛、冻结短证据与金标；同时等 40 格人工复核。

## 4. 缺口

- 40 格人工复核未返回；V3 73 格仍是启发式。
- 新比赛配对未跑（预算 18 剩余）；无改判正控未跑。
- 43 字段逐场 Llama 未拆同分母。
- 闭合约束仍不可检查。


---

# 附录 A：SMALL_MODEL_DIAGNOSTICS

# SMALL_MODEL_DIAGNOSTICS：改判错在哪一步

日期：2026-11-13。新增 6 次抽取请求（预算 24），外部 API 0。

## 0. 核心发现

同一份 B 短证据（572/571 字符）：

- 直接输出最终五项：两场 × 3 模型 = 6 条，**two_wickets 0/6**。
- 只要求抽取事实：6/6 全部 JSON 可解析、五键齐全、**出局者/原投手/新投手/方向/两个旧 wicket 数全部正确**。
- 用这 6 条实际抽取做 Python 更新：**6/6 两人最终绝对值同时正确**。

所以错误不在“读旧数、认人、弄反方向”，而在**把改判应用到最终数值**这一步；程序更新可以把 0/6 修到 6/6。

## 1. 逐条

| match | model | 出局者 | 原/新投手 | 旧 W | 程序 two |
|---|---|---|---|---|---|
| 0014 | Qwen | Elias Ward | Leo Quinn / Dylan Frost | 2 / 2 | 对 |
| 0014 | Llama | 同 | 同 | 2 / 2 | 对 |
| 0014 | Gemma | 同 | 同 | 2 / 2 | 对 |
| 0016 | Qwen | Adrian Clarke | Evan Reed / Connor Wells | 2 / 1 | 对 |
| 0016 | Llama | 同 | 同 | 2 / 1 | 对 |
| 0016 | Gemma | 同 | 同 | 2 / 1 | 对 |

金标：0014 Quinn 2→1、Frost 2→3；0016 Reed 2→1、Wells 1→2。  
程序更新：orig−1、new+1；6/6 得到正确 final。

## 2. 与直接作答对照

上一轮 B 直接作答：6 条 two 0/6；错法多为两人旧值，Llama 一场只加新投手。  
同一文本、同一模型、同一旧值，抽取全对而最终值全错，说明模型“知道发生了什么”，但不会把 −1/+1 落到最终答案。

## 3. C 的旧协议

上一轮 C 把 extraction 与 final fields 放在一个提示里，6/6 缺更新所需字段。  
本轮把任务拆成纯抽取后 6/6 成功，说明旧 C 的失败是**协议/输出结构**，不是事实不可得。

## 4. 格式与正控

- 抽取：6/6 解析、6/6 五键齐全、6/6 身份方向正确、6/6 旧值正确。
- 程序：6/6 two 正确；用正确结构化输入的正控 2/2 通过。
- 无改判正控未跑（预算保留）。

## 5. 结论

具体错误：**最终值更新**，不是证据读取或方向判断。  
这支持把“抽取 + Python 更新”作为独立条件，而不是继续让模型直接算最终五项。

---

# 附录 B：SCORECARD_RESCORE_V3

# SCORECARD_RESCORE_V3：258 字段复核与同分母成绩

日期：2026-11-13。0 次模型调用。

## 1. 可答性

- V3 仍为 **73/258**：直接 69 + 可推导 4；185 待核。
- 新增“同一句比分同时支持 total_runs 与 total_wickets”的规则；在 258 格上没有新增可答格（相关 total 字段已被旧规则覆盖或该句未匹配），变更 0 格。
- 40 格盲审已升级为全文本 + 段落编号（BLIND_REVIEW.md、texts/）；**人工结果未返回**。

## 2. 同分母 73

| 模型 | 可答答对 | 分母 | 准确率 | 全字段 |
|---|---:|---:|---:|---:|
| Qwen | 29 | 73 | 39.7% | 73/258 |
| Gemma | 32 | 73 | 43.8% | 85/258 |
| Llama | 26 | 73 | 35.6% | 63/258 |

Llama 5/6 嵌套 JSON 恢复，0008 空；相关格按错计。

## 3. 逐场

| match | 可答 | Qwen | Gemma | Llama |
|---|---:|---:|---:|---:|
| 0003 | 16 | 10 | 10 | — |
| 0008 | 12 | 5 | 5 | 0（空） |
| 0010 | 12 | 1 | 3 | — |
| 0012 | 11 | 4 | 6 | — |
| 0015 | 11 | 5 | 3 | — |
| 0017 | 11 | 4 | 5 | — |

Llama 只报总分 26/73；逐场未拆。

## 4. 分表与闭合

- 分表：比赛摘要、局汇总、击球行、投手行的覆盖与准确率沿用 43 字段预测；本轮未改变字段清单。
- 闭合：schema 缺 extras 合计与 bat_sum，记为不可检查。
- 格式：Qwen/Gemma 6/6；Llama 旧协议 0/6，展平后 5/6。

## 5. 限制

- 73 格是启发式，不是人工确认；40 格待返回。
- V3 规则未改变分母，不能宣称覆盖率提升。
- 缺答在 73 格中按错计。

---

# 附录 C：DATASET_CHANGELOG

# DATASET_CHANGELOG：从错例到下一版样本

## 1. 发现

| 错误 | 证据 | 出现范围 |
|---|---|---|
| 直接最终值不更新 | B 短证据 two 0/6 | 3 模型 × 2 场 |
| 抽取事实其实正确 | 抽取 6/6 身份/方向/旧值 | 同上 |
| 程序更新可修复 | 6/6 two 正确 | 同上 |
| 旧 C 协议缺字段 | 6/6 无法执行 | 3 模型 × 2 场 |

## 2. 修改

| 项 | 改法 | 核验 |
|---|---|---|
| 样本条件 | 新增“同一 B 文本 + 纯抽取”条件，与直接最终值配对 | 6/6 抽取成功 |
| 评分 | 分开 identity、direction、old values、final two、program two | 逐条记录 |
| C 协议 | 拆成纯抽取；不再要求一次输出 extraction+final | 6/6 可解析 |
| 可答性 | 新增同一句比分的 total 规则 | 258 格变更 0 |
| 盲审 | 全文 + 段号 + 候选句 | 40 格 |

## 3. 指标前后

- 直接 B：two 0/6 → 抽取后程序 two 6/6。
- C：旧协议 0/6 可执行 → 纯抽取 6/6 可执行。
- 43 字段：73/258 不变；Qwen 29/73、Gemma 32/73、Llama 26/73。

## 4. 还缺

- 40 格人工复核。
- 新比赛上的“直接 vs 抽取+程序”配对（2 场 ×2 条件 ×3 模型 =12）未跑。
- 无改判正控未跑。

---

# 附录 D：BLIND_REVIEW（40 格）

# BLIND_REVIEW：40 格可答性复核（全文本版）

复核者先只看原文和任务作答，再对 scorecard。每场完整解说见 texts/ 目录，段落编号可直接引用。

排名规则：旧任务按 runs/wickets 降序；并列按 scorecard 行序；旧提示未定义并列，属于旧任务歧义。

## S01 match_0003 / inn1.no_balls
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.no_balls；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S02 match_0008 / match.result
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S03 match_0010 / inn2.bat3_runs
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.bat3_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S04 match_0012 / inn1.wides
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.wides；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S05 match_0015 / inn2.wides
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.wides；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - A few wides arrived just when a quiet over was nearly secured, one no-ball smudged the rhythm, and the first stand grew into the sort of draining opening passage where a captain keeps feeling one mistake away from contro
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S06 match_0017 / match.result
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S07 match_0003 / inn2.byes
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn2.byes；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S08 match_0008 / inn1.total_wickets
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S09 match_0010 / inn1.bowl2_runs
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn1.bowl2_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S10 match_0012 / inn1.overs
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.overs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Mason took the longer route, not pretty every over but solid enough to make the middle overs matter, while Connor added the steadier scoring beside him, working gaps and punishing the loose ball without trying to turn th
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S11 match_0015 / inn1.total_wickets
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S12 match_0017 / inn1.total_runs
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.total_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S13 match_0003 / inn1.bowl2_wickets
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.bowl2_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S14 match_0008 / inn1.total_runs
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.total_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S15 match_0010 / inn2.total_wickets
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S16 match_0012 / inn1.total_wickets
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S17 match_0015 / inn2.byes
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.byes；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S18 match_0017 / inn1.bat2_runs
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.bat2_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S19 match_0003 / match.result
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S20 match_0008 / inn1.bat3_runs
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.bat3_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S21 match_0010 / inn1.bowl2_wickets
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn1.bowl2_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S22 match_0012 / match.result
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：match.result；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S23 match_0015 / inn2.no_balls
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.no_balls；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S24 match_0017 / inn2.wides
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn2.wides；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S25 match_0003 / inn2.bowl2_wickets
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn2.bowl2_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S26 match_0008 / inn1.bowl1_wickets
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.bowl1_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S27 match_0010 / inn2.overs
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.overs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Owen Hayes played the sharper opening role, Ethan Ward gave the first stand a steadier shape, and for a few overs Summit Vale had to work rather than wait.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S28 match_0012 / inn2.bat3_name
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn2.bat3_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S29 match_0015 / inn1.bowl1_runs
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn1.bowl1_runs；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S30 match_0017 / inn1.bat2_name
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.bat2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S31 match_0003 / inn1.team
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Seabank Cricket Ground in Stonehaven had that sharp feel from the first over, not quite evening yet but already narrow enough in the light for every fielder in the ring to look a little closer than he really was, and Rid
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S32 match_0008 / inn2.bat1_name
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn2.bat1_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Aiden Cole gave Ridgeview their one proper argument.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S33 match_0010 / inn2.team
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn2.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediat
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S34 match_0012 / inn1.bowl2_name
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn1.bowl2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Liam Frost removed Adrian, Lucas Vale pinned Caleb after he had started to settle, and the score was pushed back into repair mode again.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S35 match_0015 / inn2.bowl2_name
- 原文：[texts/match_0015.md](texts/match_0015.md)（段落编号见文件）
- 字段：inn2.bowl2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Caleb Rourke arrived and changed the middle overs.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S36 match_0017 / inn1.bowl2_name
- 原文：[texts/match_0017.md](texts/match_0017.md)（段落编号见文件）
- 字段：inn1.bowl2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Zach Foster’s spell was the visible cutting edge through the middle-late section, not always perfectly cheap, but constantly dangerous, while Ethan Parker kept hitting the card in ways that stopped any repair from becomi
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S37 match_0003 / inn1.total_wickets
- 原文：[texts/match_0003.md](texts/match_0003.md)（段落编号见文件）
- 字段：inn1.total_wickets；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Brandon followed soon after, again to Clarke, again with Cooper involved, and suddenly Brookmere were 17 for 2 with the innings already asking for repair before it had reached the part of a where batters usually start ch
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S38 match_0008 / inn1.bat2_name
- 原文：[texts/match_0008.md](texts/match_0008.md)（段落编号见文件）
- 字段：inn1.bat2_name；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - Adrian Blake then arrived and shifted the tone.
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S39 match_0010 / inn1.team
- 原文：[texts/match_0010.md](texts/match_0010.md)（段落编号见文件）
- 字段：inn1.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - At Northbank Meadow Ground in Hillview, Gulfstone XI won the toss and chose to field, and for a short while that call looked sharp enough to dictate the whole afternoon, because Summit Vale XI were pushed almost immediat
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

## S40 match_0012 / inn2.team
- 原文：[texts/match_0012.md](texts/match_0012.md)（段落编号见文件）
- 字段：inn2.team；局别按字段名；统计时点：该局结束时
- 候选句（可选索引，不替代全文）：
  - At Eastbank Meadow Ground in Hillview, Westmere XI won the toss and chose to field, and the call had the feel of a side trusting the first hour rather than guessing at the day, because the surface looked playable from th
- 答案：____；证据段号：____；可答性（直接/推导/不足/歧义/冲突）：____

---

# 附录 E：REPRODUCE

# REPRODUCE

## 45 字段复核（0 调用）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_v3.py

## 抽取诊断（6 调用）

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/run_extract.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/score_extract.py

## 盲审文本

python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_texts.py
python VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v1/make_blind.py

## 输出

- runs/extract.jsonl、extract_scores.json
- FIELD_ANSWERABILITY_V3.jsonl
- BLIND_REVIEW.md、texts/
- 本轮调用 6/24。


---

## 附录 A20：小模型诊断 v2 配对结果

> 原文件：VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v2/PAIRED_RESULTS.md（49 行）

# PAIRED_RESULTS：两场新比赛的配对结果

日期：2026-11-13。18 次请求（6 直接 + 6 抽取改判 + 6 抽取维持），外部 API 0。

## 0. 样本

- match_0031 第一局：Evan Vale 4/19 → 3/19；Leo Shaw 1/26 → 2/26。
- match_0019 第二局：Evan Turner 5/13 → 4/13；Liam Foster 1/15 → 2/15。
- 旧值对、正确值、旧值对调、反向更新四种有序对均不同，无答案碰撞。

## 1. 正式改判：直接 vs 抽取+程序

| 模型 | 直接 two | 抽取+程序 two |
|---|---:|---:|
| Qwen | 1/2 | 2/2 |
| Llama | 1/2 | 2/2 |
| Gemma | 2/2 | 2/2 |
| 合计 | 4/6 | 6/6 |

配对变化：错→对 2、对→错 0、对→对 4、错→错 0。

- Qwen 0019 直接给 4、1（只减原投手，未加新投手）；抽取+程序给 4、2。
- Llama 0031 直接值 3、2 正确，但键名写成下划线（Evan_Vale_wickets），严格键匹配判错；归一化则直接组 5/6，两步法收益 +1。
- Gemma 两场直接都对。

## 2. 维持原判

| 模型 | retain 识别 | 两人最终值同时正确 | 误更新 | 无法执行 |
|---|---:|---:|---:|---:|
| Qwen | 0/2 | 0/2 | 0 | 2 |
| Llama | 2/2 | 2/2 | 0 | 0 |
| Gemma | 2/2 | 0/2 | 0 | 2 |

- Qwen：识别成 reassign，但 final_bowler == original_bowler，决定与人物矛盾 → 程序拒绝执行，未误改。
- Gemma：识别成 retain，但旧值填 UNKNOWN → 无法执行，未误改。
- Llama：两场都正确保留原值。
- 误更新 0/6；4/6 无法执行，失败在决定标签或旧值完整性，不在擅自改数。

## 3. 程序正控

- 正确 reassign 输入：两人最终值正确。
- 正确 retain 输入：两人原值不变。
- 缺字段/UNKNOWN/方向矛盾：程序拒绝执行，未产生数值。

## 4. 结论

两场新比赛上，先抽取再由程序更新比直接给最终值多答对 2 场（严格键匹配 4/6→6/6），没有把原来对的改错。  
维持原判没有误更新；失败是决定标签矛盾或旧值 UNKNOWN，不是程序擅自加减。  
直接组这次只要求两个字段，已到 4/6；两步法收益是 +2，不是上一轮的 +6。


---

## 附录 A21：小模型诊断 v7 报告

> 原文件：VETT_INTEGRATED_20261113/analysis/VETT_SMALL_MODEL_DIAGNOSTICS_V7_REPORT.md（81 行）

# VETT_SMALL_MODEL_DIAGNOSTICS_V7_REPORT

日期：2026-11-14。后台完成；外部 API 0。

## 一、v6 修正

- 直接联合 11/18，v5 按归属联合 11/18；转移 3/3/8/4；分通知 28/36 与 29/36。
- Qwen 6 条维持：decision=reassign、原归属 A、最终归属 B，结构上合法但与 retain 通知相反。
- 严格 retain 规则因 decision 不是 retain 拒绝 6 条；按归属执行转移成错误值 6 条；实际误转移 6 条。
- 严格规则确实拦住了这 6 条误转移，但也拒绝 6 条本可正确交付。
- 详见 V6_CORRECTION.md。

## 二、后台运行

- PID 2076；日志 runner.log；进度 PROGRESS.md。
- 启动约 17:00，结束约 17:18，约 18 分钟。
- 完成 22 场、264/264 次请求；22 场全部是原投手旧值更高，低旧值方向 0 场（目标 24 场，缺口 2 场）。
- 每 2 场一批，共 11 批；无空批。

## 三、表一：两种通知能否同时答对

| 方法 | 正式 | 维持 | 联合 |
|---|---:|---:|---:|
| 直接 | 42/66 | 63/66 | **39/66** |
| v5 严格标签 | 65/66 | 42/66 | 42/66 |
| v5 按归属 | 65/66 | 51/66 | **51/66** |

- 直接→按归属：错→对 24、对→错 12、对→对 27、错→错 3。
- 按归属比直接多 12 条，比严格多 9 条；净收益来自 Llama（联合 7→22）与 Qwen 退步（13→10），Gemma 19 不变。
- 按模型：Qwen 直接 13/22、严格 13/22、按归属 10/22；Llama 7、22、22；Gemma 19、19、19。
- 旧值方向：高 22 场，低 0 场；高组联合为直接 39、按归属 51；低组无样本。

## 四、表二：程序拦住了什么

| 类别 | 计数 |
|---|---:|
| 严格拒绝、按归属恢复正确 | 9 |
| 严格拒绝、按归属输出错误 | 14 |
| 两种都拒绝/无法执行 | 1（Gemma 0086 空答） |
| 两种都执行但结果错误 | 1 |
| 维持实际误转移 | 14（Qwen 12 + Gemma 2） |
| 维持正确交付 | 51/66 |
| 维持无法执行 | 1/66 |

- 严格规则拦住 Qwen 12 条误转移，但损失 9 条本可正确交付。
- 按归属放行 14 条错误转移，换来 Llama 15 条联合提升；净 +12。
- Qwen 12 条是“结构一致但读错通知”：decision=reassign、A→B，旧值正确；其中 9 条 decision 与原/终归属矛盾，3 条与通知相反但结构自洽。

## 五、表三：最早错误

| 例子 | 事实 | 直接 | 抽取 | 程序 | 最早错误 |
|---|---|---|---|---|---|
| Qwen 0067 维持 | A 5、B 2，应 5/2 | 5,2 对 | decision reassign A→B，旧值 5/2 | 按归属 4,3 错 | 通知理解 |
| Llama 0067 维持 | 同上 | 5,2 对 | retain，旧值 5/2 | 5,2 对 | 无 |
| Gemma 0086 维持 | 4/2 | 4,2 对 | 空答 | 无法执行 | 格式/空答 |
| Qwen 正式 | A 5→4、B 2→3 | 常见错值 | decision reassign，旧值对 | 4,3 对 | 直接最终值 |
| Gemma 0075 维持 | 4/2 | 3,2 错（只改一侧） | retain，旧值对 | 4,2 对 | 直接单边 |

计数：事件归错 0；旧值错/漏抽 4（Gemma 3 + Qwen 1）；只更新一边直接错 3；通知判断错 Qwen 12；程序执行错 14；空答 1。

## 六、四件事

1. v6 修正：联合 11/18 与 11/18；转移 3/3/8/4；分通知 28/36、29/36。严格规则能拦住 6 条误转移，但同时拒绝 6 条本可正确交付，无净收益。
2. 后台约 18 分钟，完成 22 场、264 次请求；两种旧值方向为高 22、低 0。
3. v7 联合：直接 39/66、严格 42/66、按归属 51/66。按归属比直接多 12，少 12（错→对 24、对→错 12）。实际误转移 14，无法执行 1。
4. 值得写进 R28：**维持通知被读成改判**（Qwen 12/22），以及“严格拦截 vs 按归属放行”的取舍。样本限制：无低旧值方向、22 场而非 24、全部为构造改判。
5. 43 字段：新增 6 格自动 6/6、人工 0/6；40 格人工 0/40；79 分母不变，Qwen 33、Gemma 38、Llama 30。

## 七、下一步

- 把“同事件、只换通知”的 retain 诊断纳入 R28；要求最终归属=原归属，并在评分中分离“通知理解”和“程序一致性”。
- 补低旧值方向样本；本轮分层结论只覆盖高方向。
- 严格规则保留为保守执行；按归属作为候选，但必须报告 14 条误转移。
- 43 字段人工返回前，不改变 79 分母。

## 八、文件

- 后台：runs/paired.jsonl（264 条）、runner.log、PROGRESS.md、scores.json
- 修正：V6_CORRECTION.md
- 字段：ANSWERABILITY_AUDIT.md
- 复现：REPRODUCE.md


---

## 附录 A22：v6 修正

> 原文件：VETT_INTEGRATED_20261113/analysis/small_model_diagnostics_v7/V6_CORRECTION.md（31 行）

# V6_CORRECTION：从 72 条原始响应重算

日期：2026-11-14。0 次模型调用。

## 1. 配对变化

- 直接联合 11/18，v5 按归属联合 11/18。
- 直接→v5：错→对 3、对→错 3、对→对 8、错→错 4，四格和 18。
- 分通知正确数：直接 12+16=28/36；v5 18+11=29/36。
- 正式改判 Qwen 单模型分母 6；三模型合计 18。

## 2. Qwen 六条维持

六条都是 decision=reassign、原归属 A、最终归属 B，三者在结构上是合法 reassign，与通知 retain 相反。

- 严格规则按 retain 检查，要求 decision=retain，因此 6/6 拒绝；拒绝原因是 decision 不是 retain，不是人物或旧值缺失。
- 按归属执行：原归属 A≠最终归属 B，执行一次 A→B 转移；6/6 都执行成错误数对。
- 旧值：Qwen 6/6 两个旧值都正确；它不是漏抽，而是把维持读成改判。

## 3. 失败分类

| 类别 | 计数 |
|---|---:|
| 空答 | 1（Gemma 0086） |
| UNKNOWN/漏字段 | 1（同一空答） |
| 标签与归属矛盾 | 0（Qwen 是结构一致的 reassign） |
| 标签与归属一致但与通知相反 | 6（Qwen 维持） |
| 实际误转移 | 6（Qwen 维持） |
| 严格拒绝但本可正确交付 | 6（Qwen 维持；严格拦住了误转移） |

结论：严格规则拦住 6 条误转移，也拒绝 6 条本可正确交付；按归属执行放行 6 条错误转移。两者都没有净收益。


---

## 附录 A23：多维 A 开发批结果

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_multidimensional_20261116/A_DEV_RESULTS.md（13 行）

# A 开发批结果（20 根完成）

| 批次 | 根 | 行 | 目标四格 | 全 43 格 |
|---|---:|---:|---:|---:|
| dev1 | 8 | 24 | 84/90 | 272/792 |
| dev2 | 8 | 24 | 84/96 | 300/840 |
| dev3 | 4 | 12 | 41/48 | 127/420 |
| 合计 | 20 | 60 | 209/234（89.3%） | 699/2052（34.1%） |

- A 的 20 个开发根已全部完成。
- 目标四格接近 90%，不能用来证明整表方法。
- 全 43 格只有 34.1%，主要损失在非目标字段。
- 解析：实际 JSON 成功；runner 的 fields=None 仍导致 parse_ok 误报，按顶层键评分。


---

## 附录 A24：多维 B 最小批结果

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_multidimensional_20261116/B_MIN_RESULTS.md（19 行）

# B 证据与干扰：8 根最小批

- 37 个条件-根组 ×3 模型 = 111 行；0 失败。
- 两格同时正确：110/111。

| 条件 | 正确 |
|---|---:|
| O 原文 | 15/15 |
| P 前移 | 11/12 |
| L 后移 | 15/15 |
| E 摘录 | 15/15 |
| WI 删同局局中比分 | 15/15 |
| WIC 等长无关删除 | 15/15 |
| OI 删另一局比分 | 12/12 |
| OIC 等长无关删除 | 12/12 |

- 唯一退步：P 前移 1 条；O 对应子集 12/12。
- 删除类条件在这 8 根上没有造成退步，说明这些根对干扰不敏感，B 需要更多难根或更强干扰。
- P/L 条件数不等，因为部分证据已在段界，不能生成移动。


---

## 附录 A25：Pilot10 案例审计

> 原文件：VETT_INTEGRATED_20261113/analysis/pilot10_case_audit/CASES.md（388 行）

# Pilot-10 样本审计 v2（已更正）

日期：2026-11-13  
范围：只使用已有 Pilot-10 数据与输出；模型调用 0 次。  
新增产物目录：VETT_INTEGRATED_20261113/analysis/pilot10_case_audit/  
原始数据、旧报告、预注册文件未修改。

## 0. 更正日志：哪一层写错了

| 位置 | v1 说法 | 实际 | 出错层 |
|---|---|---|---|
| A 逐次出局 | “命名出局只有 5 次，与汇总不闭合” | inn1 命名 1 次；inn2 命名 5 次（Nora 3、Ruby 2），inn2 共 10 个 wicket，另有 5 个未命名。被转移的 wicket 属于未命名部分，所以无法定位到具体出局。 | 报告层（我漏了按局拆分与“未命名”说明） |
| C 缺证 | “剩余 sundries 说 8，与 gold 9 矛盾” | “sundries 8”是 **inn2** 的句子；C 的目标是 **inn1.total_extras**。inn1 剩余文本为 124 总分、115 击球和，仍可推出 9，但没有 inn1 的矛盾句。 | 报告层（把 inn2 句子当成 inn1） |
| D 缺证 | “剩余 sundries 说 10，与 gold 14 矛盾” | “sundries 10”是 **inn2** 的句子；D 的目标是 inn1 的 extras/wides/no_balls。inn1 剩余 136 总分、122 击球和，total_extras 可推出 14；wides/no_balls 才真正缺证。 | 报告层（同上） |
| F 10 vs 16 | “inn1.total_extras = 10” | fields.jsonl、gold.json、两模型两臂的输出全部是 **16**；只有 v1 报告写成 10。 | 报告层（转录错误），数据/金标/评分一致 |
| 32 vs 28 | 报告称“28 core 字段” | eval 实际按 32 字段计分：E.is_core 把任何以 wides 结尾的字段都算进来，多出 4 个投手 .wides。 | 评测层（is_core 判定） |
| revised_hard 双边 | 0.529 被当作“模型不会双边归属” | prompt 与 32 字段 scorer 只含 bowl1 figures，不含 bowl2/donor。 | 评测层（schema 缺口） |

## 1. 对齐与口径

- 六对样本按 (match, variant, system, model) 对齐；文本路径与 JSONL 行号逐对核对。
- direct 与 closure 是两次独立调用；closure 不是从 direct 输出后处理而来（这是旧实验的混杂，见第 10 节）。
- 所有文本是 scorecard 的确定性重渲染（seed=0），不是发布目录的原始 commentary。
- eval 行只保存 pred，未保存 raw_output；本文引用的是解析后的字段。
- closure 的 propagate() 只重写 inn{1,2}.total_extras、total_runs、bowling_runs_charged；重写前的 pred 未保存。

## 2. 总表

| 对 | 比赛 | 变体 | 关键字段 | qwen direct | llama direct | 处置 |
|---|---|---|---|---|---|---|
| A | match_0108 | control vs revised_hard | 两投手 figures；全队 wickets | 1/1 被提示的投手正确；第二名未提示 | 0/1（W/R 占位符）；第二名未提示 | 需修评测 + 需修样本 |
| B | match_0035 | control vs revised_hard | 首席投手 figures；全队 wickets | 1/1 正确；全队正确 | 1/1 正确；全队正确 | 证据待核（只验证汇总） |
| C | match_0167 | control vs missing | inn1.total_extras | 0 | 8 | 需修样本（gold 应为 9） |
| D | match_0091 | control vs missing | inn1.total_extras / wides / no_balls | 0/0/0 | 10/0/8 | 需修样本（total_extras 应为 14） |
| E | match_0092 | control vs shuffled | 9 个 C→W 字段 | 9 个 C→W；1 个是 figures 格式 | 3 个 C→W | 可保留（换序）+ 需修评测 |
| F | match_0203 | control vs shuffled | 4 个稳定字段 | 6 个 C→W | 0 个 C→W，24 个稳定正确 | 可保留（模型差异） |

---

## 3. Pair A：match_0108，归属更正（control vs revised_hard）

### A1. 模型看到了什么

- control 第 45 句（char 3336）："Bayview Royals Women's bowling effort was led by Nora Vale, whose 4 for 6 made the deepest incisions."
- control 第 46 句（char 3389）："Ruby North kept the pressure on with 3 for 7..."
- revised_hard 第 45 句：Nora 改为 "5 for 6"；第 46 句：Ruby 改为 "2 for 7"。
- 按局拆分：
  - inn1 只命名 1 次出局（Clara Moss → Farah Noor），与本对无关。
  - inn2 命名 5 次出局：Lina Fox → Nora（第 18 句）、Mira Khan → Ruby（第 22 句）、Zara Field → Ruby（第 26 句）、Hana Qureshi → Nora（第 30 句）、Sarah Pike → Nora（第 34 句）。
  - inn2.total_wickets = 10，因此另有 5 个 wicket 没有在叙述中命名。

路径：.../match_0108/variants/control/commentary.txt；.../revised_hard/commentary.txt。

### A2. 正确答案

| 字段 | control | revised_hard | 依据 |
|---|---:|---:|---|
| inn2.bowl1_Nora Vale.figures | 4/6 | 5/6 | Nora +1 |
| inn2.bowl2_Ruby North.figures | 3/7 | 2/7 | Ruby -1 |
| inn2.total_wickets | 10 | 10 | 全队不变 |

- 两名投手的汇总在文本中都出现（第 45、46 句）。
- 但“哪一次出局”无法确定：被转移的 wicket 属于 inn2 中未命名的 5 个；文本没有把它绑定到任何具体出局。
- 修订后 Nora 的命名出局仍是 3 次（Lina、Hana、Sarah），汇总 5；Ruby 命名 2 次（Mira、Zara），汇总 2。总命名 5 次，inn2 共 10 个 wicket，另有 5 个未命名；被转移的 wicket 属于未命名部分，因此无法从命名出局反推。

### A3. 模型实际答了什么

| 记录 | 字段 | 值 | 解析 | 评分 |
|---|---|---:|---|---|
| qwen direct，第 225 行 | bowl1 Nora | "5/6" | 正常 | 正确 |
| 同上 | bowl2 Ruby | 键不存在 | 正常 | 未评分（不在 32 字段） |
| qwen closure，第 226 行 | 同上 | "5/6" / 键不存在 | 正常 | 同上 |
| llama direct，第 225 行 | bowl1 Nora | "W/R" | 正常 | 错误（占位符） |
| 同上 | bowl2 Ruby | 键不存在 | 正常 | 未评分 |
| llama closure，第 226 行 | 同上 | "W/R" / 键不存在 | 正常 | 同上 |

对照 control：qwen 4/6（正确），llama 仍是 "W/R"（错误）。  
所以 llama 的占位符是修订前就存在的格式失败；qwen 正确跟踪了 Nora 的 4→5。

### A4. 能否用于下一轮

**需修评测 + 需修样本。**

- 已核实：bowl2 不在 prompt/scorer；“另一名投手”从未被问。
- 已核实：文本没有把被转移的 wicket 绑定到具体出局。
- 未核实：模型若被问到 bowl2 是否能答对；本轮未调用。

---

## 4. Pair B：match_0035，归属更正（control vs revised_hard）

### B1. 模型看到了什么

- control 第 32 句（char 2465）："Harborfield's bowling effort was led by Isaac Shaw, whose 3 for 35..."
- revised_hard 第 32 句：改为 "whose 4 for 35"。
- 第 24 句：Caleb Price → Isaac Shaw；第 33 句：Liam Foster 2/24 未变。
- 转移日志：Isaac 3→4，Luke Barrett 2→1；Luke 的名字在文本出现，但他的 figures 从未出现。
- inn1.total_wickets = 10，未变。

### B2. 正确答案

| 字段 | control | revised_hard | 依据 |
|---|---:|---:|---|
| inn1.bowl1_Isaac Shaw.figures | 3/35 | 4/35 | Isaac +1 |
| inn1.total_wickets | 10 | 10 | 全队不变 |

- 文本只写首席投手的汇总 +1，没有写 Luke 的 2→1，也没有命名被转移的出局。
- 因此只能验证“首席投手汇总更新 + 全队不变”，不能验证双边归属。

### B3. 模型实际答了什么

| 记录 | 字段 | 值 | 评分 |
|---|---|---:|---|
| qwen direct，第 217 行 | Isaac | "4/35" | 正确 |
| qwen closure，第 218 行 | Isaac | "4/35" | 正确；未重算 |
| llama direct，第 217 行 | Isaac | "4/35" | 正确 |
| llama closure，第 218 行 | Isaac | "4/35" | 正确 |
| 两模型 | inn1.total_wickets | 10 | 正确 |

对照 control：两模型都输出 3/35，说明确实读到了修订后的 4/35。

### B4. 能否用于下一轮

**证据待核。** 可作“汇总更新答对”的对照，但不能回答双边归属；donor 既不在文本也不在 schema。

---

## 5. Pair C：match_0167，缺证（control vs missing）

### C1. 模型看到了什么

- 被删句：control 第 23 句（char 1595）："The total included 9 extras, with 7 wides and 0 no-balls..."
- 剩余 inn1 证据：
  - "The batters themselves accounted for 115."
  - "The innings closed at 124 from 20.0 overs.."
  - "All told, the innings reached 124.."
- 注意：第 58 句 "The sundries column read 8..." 属于 **inn2**，不是本对的目标局。

### C2. 正确答案

gold：control inn1.total_extras = 9；missing 标为 UNKNOWN。

- inn1 仍可用 124 − 115 = 9 推出；删除的只是显式句。
- 因此该字段不是“无法唯一确定”；gold=UNKNOWN 与剩余证据冲突。
- inn2 的 sundries 8 与 inn1 无关，v1 把它当成矛盾是错的。

### C3. 模型实际答了什么

| 记录 | 值 | 字段存在 | 解析 | 评分 |
|---|---:|---|---|---|
| qwen direct，第 21 行 | 0 | 是 | 正常 | 错误 |
| qwen closure，第 22 行 | 0 | 是 | 正常 | 错误；未改 |
| llama direct，第 21 行 | 8 | 是 | 正常 | 错误 |
| llama closure，第 22 行 | 8 | 是 | 正常 | 错误；未改 |

无 UNKNOWN、无漏字段、无解析失败。

### C4. 能否用于下一轮

**需修样本。** 已核实：124−115=9；gold=UNKNOWN 错误。  
处理：把 gold 改为 9；若要制造真缺证，必须同时删除总分或击球和。

---

## 6. Pair D：match_0091，缺证（control vs missing）

### D1. 模型看到了什么

- 被删句：control 第 22 句（char 1608）："The total included 14 extras, with 11 wides and 1 no-ball..."
- 剩余 inn1：136 总分、122 击球和；"Another 0 byes and 2 leg-byes..."。
- 第 49 句 "The sundries column read 10..." 属于 **inn2**，与本对无关。

### D2. 正确答案

gold：inn1 total_extras=14、wides=11、no_balls=1；missing 三项都标 UNKNOWN。

- total_extras = 136 − 122 = 14，可唯一确定；gold 错标 UNKNOWN。
- wides / no_balls 没有独立剩余来源，确实不可唯一确定。
- 所以正确拆法是：total_extras=14；wides/no_balls=UNKNOWN。

### D3. 模型实际答了什么

| 记录 | total_extras | wides | no_balls | 解析 |
|---|---:|---:|---:|---|
| qwen direct，第 117 行 | 0 | 0 | 0 | 正常 |
| qwen closure，第 118 行 | 0 | 0 | 0 | 正常；未改 |
| llama direct，第 117 行 | 10 | 8 | 0 | 正常 |
| llama closure，第 118 行 | 10 | 8 | 0 | 正常；未改 |

### D4. 能否用于下一轮

**需修样本（部分）。** total_extras 可答为 14；wides/no_balls 可保留为 UNKNOWN。  
处理：拆分金标，不要把三项一起标 UNKNOWN。

---

## 7. Pair E：match_0092，换序（control vs shuffled）

### E1. 模型看到了什么

同局内重排，事实不变，时间线被打乱：
- "When Jonah Walker fell to Robert Mills for 3..." 被移到 shuffled 第 2 句（char 112），出现在 2/2、3/3 之前。
- "With George King scoring 9 and Brendan Young contributing 19..." 被移到第 15 句（char 1194）；control 第 9 句。
- "When Samuel Wright fell to Marcus Hale for 0..." control 第 4 句，shuffled 中后移。

### E2. 正确答案

gold 不变：inn1.leg_byes=2、inn1.batting_runs_sum=65、inn1.bowl1_Marcus Hale.figures="3/18"、inn2.total_extras=17、inn2.byes=1、inn2.leg_byes=4、inn2.wides=12、inn2.bowling_runs_charged=77。

### E3. 模型实际答了什么

qwen direct，第 75 行（closure 第 76 行）：

| 字段 | control | shuffled | gold | 评分 | 是否等于另一局同名字段 |
|---|---:|---:|---:|---|---|
| inn1.leg_byes | 2 | 4 | 2 | 错 | 是：inn2.leg_byes gold=4、control pred=4 |
| inn1.batting_runs_sum | 65 | 81 | 65 | 错 | 否 |
| inn1.bowl1_Marcus Hale.figures | "3/18" | "3 for 18" | "3/18" | 格式误判 | — |
| inn2.total_extras | 17 | 0 | 17 | 错 | 否 |
| inn2.byes | 1 | 0 | 1 | 错 | 否 |
| inn2.leg_byes | 4 | 0 | 4 | 错 | 否 |
| inn2.wides | 12 | 0 | 12 | 错 | 否 |
| inn2.bowling_runs_charged | 77 | 82 | 77 | 错 | 否 |

第 9 个 C→W 是 inn2.bowl1_Kieran Hall.figures（未展开）。  
closure 第 76 行的 figures 变成 "3/18" 是独立调用的输出，不是 propagate。

### E4. 能否用于下一轮

**可保留（换序不稳定）+ 需修评测。**

- 已核实：9 个 C→W 中 1 个是 figures 格式问题；其余包含 inn1.leg_byes 的跨局串值（4 = inn2 的 4）与 inn2 extras 的整体塌陷。
- 需修 value_match 的 figures 归一化，然后重算（见第 9 节）。

---

## 8. Pair F：match_0203，换序（control vs shuffled）

### F1. 模型看到了什么

- "The lower order flickered briefly..." 被移到 shuffled 第 2 句（char 111）。
- "When Ethan Wells fell to Ethan Shaw for 27..." 被移动。
- "Through the middle phase, Connor Hart held firm..." 被移动。

### F2. 正确答案

gold 不变：
- match.result = "Ridgeline Won by 5 Wickets"
- inn1.total_runs = 174
- inn1.total_wickets = 10
- inn1.total_extras = 16（不是 10）
- inn2.total_extras = 20

10 vs 16 的追查：fields.jsonl=16，gold.json=16，qwen/llama 两臂 pred 都是 16；只有 v1 报告写成 10。数据、金标、评分三层一致，错在报告层。

### F3. 模型实际答了什么

- llama direct，第 27 行：0 个 C→W、0 个 W→C、24 个字段两臂都正确；上述 4 个字段两臂均正确。
- qwen direct，第 27 行：6 个 C→W：inn1.max_partnership、inn2.total_extras、inn2.leg_byes、inn2.no_balls、inn2.wides、inn2.bowling_runs_charged；上述 4 个字段仍正确。

### F4. 能否用于下一轮

**可保留。** 同一换序操纵下 llama 完全稳定、qwen 6 个字段变错；是模型差异的干净对照。  
但不能用 v1 的 10 作为 gold；正确值是 16。

---

## 9. 换序复算（用已有输出，0 次调用）

### 9.1 figures 归一化

把 "3 for 18"、"3/18"、"3-18" 都归一为 (3,18) 比较。旧评分只接受 "W/R" 或 "W-R"。

### 9.2 28 字段 vs 32 字段

- 计划中的 28 字段：4 个比赛级 + 每局 10 个基础字段 + 每局 bat1 runs + 每局 bowl1 figures。
- 实际 32 字段：E.is_core 把任何以 wides 结尾的字段都算进来，额外包含 4 个投手 .wides（每局 2 个）。
- 结果（10 场 macro 平均）：

| 字段集 | 模型 | control（旧） | shuffled（旧） | control（新） | shuffled（新） |
|---|---|---:|---:|---:|---:|
| planned28 | qwen | 0.7678 | 0.6250 | 0.7678 | 0.6321 |
| actual32 | qwen | 0.6906 | 0.5625 | 0.6906 | 0.5688 |
| planned28 | llama | 0.8107 | 0.6928 | 0.8107 | 0.6928 |
| actual32 | llama | 0.7375 | 0.6312 | 0.7375 | 0.6312 |

读法：
- 32 字段把 control 准确率压低约 7.7pp（qwen 0.691 vs 0.768；llama 0.738 vs 0.811），因为多出的投手 wides 很难。
- figures 归一化只影响 qwen（+0.6pp shuffled），llama 没有 figures 错误。
- 旧结果保留在 analysis/pilot10_metrics.json，未覆盖。

### 9.3 换序错例的跨局串值检查

对每个 C→W 字段，比较 shuffled 的错误值是否等于“另一局同名字段”的 gold 或 control pred。只列有意义的（两局 gold 不同）：

| 模型 | 比赛 | 字段 | control | shuffled | gold | 另一局同名字段 | 另一局 gold | 另一局 control pred |
|---|---|---|---:|---:|---:|---|---:|---:|
| qwen | match_0092 | inn1.leg_byes | 2 | 4 | 2 | inn2.leg_byes | 4 | 4 |
| qwen | match_0108 | inn1.wides | 12 | 7 | 12 | inn2.wides | 7 | 7 |
| qwen | match_0007 | inn1.leg_byes | 3 | 2 | 3 | inn2.leg_byes | 2 | 0 |
| qwen | match_0090 | inn1.byes | 1 | 0 | 1 | inn2.byes | 0 | 0 |
| qwen | match_0007 | inn1.total_wickets | 8 | 10 | 8 | inn2.total_wickets | 10 | 10 |
| llama | match_0182 | inn2.batting_runs_sum | 154 | 295 | 154 | inn1.batting_runs_sum | 295 | 295 |
| llama | match_0182 | inn2.total_extras | 18 | 17 | 18 | inn1.total_extras | 17 | 17 |
| llama | match_0182 | inn2.wides | 9 | 12 | 9 | inn1.wides | 12 | 12 |
| llama | match_0182 | inn2.no_balls | 2 | 1 | 2 | inn1.no_balls | 1 | 1 |
| llama | match_0092 | inn1.leg_byes | 2 | 4 | 2 | inn2.leg_byes | 4 | 4 |
| llama | match_0108 | inn1.leg_byes | 2 | 0 | 2 | inn2.leg_byes | 0 | 0 |

结论：串值不是个例。llama 在 match_0182 把 inn1 的 bat_sum/extras/wides/no_balls 整块搬到 inn2；qwen 在 match_0092/0108 把另一局的 leg_byes/wides 搬过来。  
这支持“模型没有把证据绑定到正确的局”，比泛泛的“状态维护失败”更具体。

---

## 10. 归属更正：新样本 + 同一输出重算

### 10.1 新样本（可判输赢）

路径：analysis/pilot10_case_audit/attribution_case/  
基于 match_0108 control，显式改一次命名出局：

- 原文："The chase took a hit when Lina Fox fell to Nora Vale for 0."
- 新文："The chase took a hit when Lina Fox fell to Ruby North for 0."
- 同步汇总："Nora ... 4 for 6" → "3 for 6"；"Ruby ... 3 for 7" → "4 for 7"。
- 全队 inn2.total_wickets 保持 10。

gold：

| 字段 | control | attribution_named |
|---|---:|---:|
| inn2.bowl1_Nora Vale.figures | 4/6 | 3/6 |
| inn2.bowl2_Ruby North.figures | 3/7 | 4/7 |
| inn2.total_wickets | 10 | 10 |

评分三项同时检查（score_spec.json）：
1. Nora 比 control 少 exactly 1 个 wicket；
2. Ruby 比 control 多 exactly 1 个 wicket；
3. 全队 total_wickets 与 control 相同。

这样“哪次出局从 A 改给 B”在文本中可判定（Lina Fox），汇总与逐次描述一致。  
本轮未跑模型（预算 0）；下一轮可直接用它做 direct vs 记账的对照。

盲审回答已核对：3/3 正确（第二局 Lina Fox、Nora 3/6、Ruby 4/7、全队 10）；证据句与 char 位置见 attribution_case/ANSWER_KEY.md。注意样本用 batter + 比分定位，未写 over 号。

### 10.2 同一输出重算 closure

旧实验的 direct 与 closure 是两次独立调用，不能把差异归功于 propagate。  
对现有 direct 输出直接应用 propagate（0 次调用）后：

| 模型 | variant | direct | direct+propagate（同输出） | 旧 closure（独立调用） |
|---|---|---:|---:|---:|
| qwen | control | 0.6906 | 0.6687 | 0.6750 |
| qwen | shuffled | 0.5625 | 0.5156 | 0.5188 |
| qwen | revised | 0.6906 | 0.6937 | 0.6813 |
| qwen | missing | 0.5312 | 0.4719 | 0.4844 |
| llama | control | 0.7375 | 0.7438 | 0.7438 |
| llama | revised | 0.7500 | 0.7906 | 0.7750 |
| llama | missing | 0.6312 | 0.6062 | 0.5969 |

读法：
- 对同一份 direct 输出重算，qwen 的 control/shuffled/missing 反而下降（组件错，重算放大错误）；只有 revised 略升。
- llama 的 control/revised 有 +0.6~+4pp，missing 下降。
- 旧 closure 的数值与独立调用绑定，不能作为“propagate 的增益”。
- 下一轮必须用同一输出重算，再比较 direct vs closure。

---

## 附录 A：28 / 32 / 48 / 49 字段口径

- 49 = fields.jsonl 总数（5 个比赛级 + 每局 22 个）。
- 32 = eval 实际分母：E.is_core 把任何以 wides 结尾的字段算进来，额外含 4 个投手 .wides。
- 28 = 计划核心：4 比赛级 + 每局 12（10 基础 + bat1 runs + bowl1 figures）。
- 48 = 现有 schema/scorer 中不存在；只有“49 − match.result_type”才会得到 48，但没有任何代码路径使用它。本轮 6 对不受 48 影响。
- 影响：A 的 bowl2 不在 32/28；B 的 donor 不在 32/28；C/D/F 的目标字段都在 28 内；E 的 figures 受 value_match 影响。

## 附录 B：UNKNOWN 的接受情况

- Prompt：要求 UNKNOWN；JSON：无严格校验，接受；Scorer：value_match("UNKNOWN","UNKNOWN") 为真。
- 漏字段会被当空串判错，而不是 UNKNOWN。
- 本轮 missing 记录全部输出具体值，没有一条输出 UNKNOWN。

## 附录 C：对齐、缺口与未核实项

- 六对文本、JSONL 行号、变体名逐条核对；同一场比赛、同一变体。
- 未保存 raw_output：只能引用解析后的 pred。
- 未保存 closure 重算前的 pred：无法判断 propagate 覆盖了哪些字段。
- revised_hard 的 bowl2/donor 未进入 prompt/scorer；本轮无法回答“双边是否都改对”，除非重跑。
- 所有“模型为什么错”均区分已核实的输出事实与对原因的推测。


---

## 附录 A26：Pilot-Next 结果

> 原文件：VETT_INTEGRATED_20261113/analysis/pilot_next/RESULTS.md（167 行）

# Pilot-Next 结果：完整证据段换序、局号标注、归属更正

日期：2026-11-13。所有数字来自 runs/*.jsonl 与 scores.json；本地 Ollama，外部 API 0 次，实际请求 113/120。

## 0. 结论摘要

1. **完整证据段换序的破坏远小于旧句级打乱。** A→B 的净准确率变化为 −2.1 到 −12.5pp；旧句级 shuffled 是 −10.6 到 −12.8pp（qwen/llama，按实际 32 字段），且旧样本出现大面积跨局复制。
2. **跨局串值在这批样本里很少。** 每个条件 48 个可查字段，命中另一局同名字段只有 0–3 个；几乎全部是 inn1.leg_byes 的 0/1 碰撞。
3. **局号标注有效但不均匀。** B→D：gemma +12.5pp（3 个错值全部消失）、qwen +6.25pp、llama +2.1pp；qwen 在 A→C（原顺序加标签）反而比 D 更高，说明标签不是单调增益。
4. **Lina Fox：明示更新能抄，推导更新不能。** 给出改判后的 3/6、4/7 时，qwen/llama 能给出 3、4 个 wickets（但不写 runs），gemma 给出完整 figures；只给改判通知、不给新 figures 时，**三个模型都保留旧值 4/6、3/7**。
5. **重测零波动。** 2 场 × 3 模型 × A 条件共 6 次重测，6/6 逐字段完全一致。

## 1. 配置与预算

| 项 | 值 |
|---|---|
| 模型 | qwen2.5:7b-instruct-q4_K_M（Q4_K_M）、llama3.1:8b（Q4_K_M）、gemma2:9b（Q4_0） |
| 解码 | temperature=0，seed=20261112，num_ctx=8192，num_predict=300 |
| 主实验 | 8 场 × 4 条件 × 3 模型 = 96 |
| Lina | 3 题面 × 3 模型 = 9 |
| smoke | 2 |
| 重测 | 2 场 × 3 模型 = 6 |
| 合计 | 113 / 120 |

留出比赛：match_0201、0198、0065、0106、0043、0063、0052、0064。  
来源：220 场中 closure-clean、未参与 Pilot-10 / case audit、按 scorecard sha256 去重；文本为 scorecard 确定性重渲染（seed=0），不是发布 commentary。  
字段：每场 3 对（total_extras、wides、leg_byes），两局值不同，共 6 个目标字段。

## 2. 四条件主结果

### 2.1 字段准确率（每条件 48 字段）

| 模型 | A 原序 | B 换序 | C 原序+局号 | D 换序+局号 |
|---|---:|---:|---:|---:|
| qwen2.5:7b | 41/48 = 0.854 | 40/48 = 0.833 | 44/48 = 0.917 | 43/48 = 0.896 |
| llama3.1:8b | 43/48 = 0.896 | 42/48 = 0.875 | 43/48 = 0.896 | 43/48 = 0.896 |
| gemma2:9b | 48/48 = 1.000 | 42/48 = 0.875 | 48/48 = 1.000 | 48/48 = 1.000 |

逐场：

| match | qwen A/B/C/D | llama A/B/C/D | gemma A/B/C/D |
|---|---|---|---|
| match_0201 | .833/.833/.833/.833 | .833/.833/.833/.833 | 1/1/1/1 |
| match_0198 | .833/.833/1/1 | 1/.833/1/1 | 1/1/1/1 |
| match_0065 | .833/1/1/1 | 1/1/1/1 | 1/.667/1/1 |
| match_0106 | .833/.833/.833/.833 | .833/.833/.833/.833 | 1/1/1/1 |
| match_0043 | .833/.833/1/.833 | .833/.833/.833/.833 | 1/.667/1/1 |
| match_0063 | .833/.5/.833/.833 | .833/.833/.833/.833 | 1/.667/1/1 |
| match_0052 | .833/.833/.833/.833 | .833/.833/.833/.833 | 1/1/1/1 |
| match_0064 | 1/1/1/1 | 1/1/1/1 | 1/1/1/1 |

### 2.2 另一局同字段命中（分母 48）

| 模型 | A | B | C | D |
|---|---:|---:|---:|---:|
| qwen | 1 (0.021) | 2 (0.042) | 0 | 1 (0.021) |
| llama | 0 | 1 (0.021) | 0 | 0 |
| gemma | 0 | 3 (0.063) | 0 | 0 |

在数值错例中的比例：

| 模型 | A | B | C | D |
|---|---:|---:|---:|---:|
| qwen | 1/7 = .143 | 2/8 = .250 | 0 | 1/5 = .200 |
| llama | 0 | 1/6 = .167 | 0 | 0 |
| gemma | 0 | 3/6 = .500 | 0 | 0 |

全部命中都是 inn1.leg_byes，且值多为 0/1：

- gemma B：match_0065 pred 1（gold 2，另一局 1）；match_0043 pred 1（gold 2，另一局 1）；match_0063 pred 4（gold 2，另一局 4）。
- qwen B：match_0198 pred 0（gold 1，另一局 0）；match_0063 pred 4（gold 2，另一局 4）。
- qwen A/D：match_0198 pred 0；match_0043 pred 1。
- llama B：match_0198 pred 0。

注意：0 和 1 是高频默认值，这些“命中”不能单独证明跨局复制；match_0063 的 4（gold 2，另一局 4）是最强的一例。

### 2.3 换序后的正确性转移

| 模型 | 比较 | C→W | W→C | C→C | W→W | 净变化 |
|---|---|---:|---:|---:|---:|---:|
| qwen | A→B | 2 | 1 | 39 | 6 | −2.1pp |
| qwen | C→D | 1 | 0 | 43 | 4 | −2.1pp |
| llama | A→B | 1 | 0 | 42 | 5 | −2.1pp |
| llama | C→D | 0 | 0 | 43 | 5 | 0 |
| gemma | A→B | 6 | 0 | 42 | 0 | −12.5pp |
| gemma | C→D | 0 | 0 | 48 | 0 | 0 |

### 2.4 局号标注的效果

| 模型 | A→C（原序加标签） | B→D（换序加标签） | B→D 跨局命中变化 |
|---|---|---|---|
| qwen | +6.25pp | +6.25pp | 2 → 1 |
| llama | 0 | +2.1pp | 1 → 0 |
| gemma | 0 | +12.5pp | 3 → 0 |

## 3. Lina Fox 三题面

固定姓名，不使用 bowl1/bowl2。fields 要求 figures；qwen/llama 实际只输出 wickets（整数），gemma 输出 "W for R"。

| 题面 | 模型 | Nora | Ruby | 全队 | figures 三值同时正确 | wickets 三值同时正确 |
|---|---|---|---:|---:|---|---|
| original | qwen | 4 | 3 | 10 | 否（缺 runs） | 是 |
| original | llama | 4 | 3 | 10 | 否（缺 runs） | 是 |
| original | gemma | 4/6 | 3/7 | 10 | 是 | 是 |
| explicit | qwen | 3 | 4 | 10 | 否（缺 runs） | 是 |
| explicit | llama | 3 | 4 | 10 | 否（缺 runs） | 是 |
| explicit | gemma | 3/6 | 4/7 | 10 | 是 | 是 |
| derivation | qwen | 4 | 3 | 10 | 否 | 否（旧值） |
| derivation | llama | 4 | 3 | 10 | 否 | 否（旧值） |
| derivation | gemma | 4/6 | 3/7 | 10 | 否 | 否（旧值） |

读法：

- **明示版**：qwen/llama 的 wicket 数正确（3、4），但没有输出 runs；gemma 完整正确。
- **推导版**：三个模型都保留旧值 4/6、3/7，没有把 Lina Fox 的出局从 Nora 转给 Ruby。qwen 的 evidence 甚至写“Nora took 4 for 6”，说明它引用了旧汇总，未采纳改判通知。
- 全队 10 在所有题面、所有模型都正确。

## 4. 解析、覆盖、重测

| 项目 | 结果 |
|---|---|
| 主实验 | 96/96 parse_ok，0 漏字段 |
| Lina | 9/9 parse_ok，0 漏字段 |
| 重测 | 6/6 逐字段与 A 完全一致（2 场 × 3 模型） |
| 截断 | 无（eval_count 50–140，num_predict 300 足够） |

Lina 的 qwen/llama 输出裸整数是**协议偏差**（只给 wickets，不给 runs），不是 parse 失败；已单列。

## 5. 支持现象与例外

**支持现象（局号有效）**：gemma 在 B 条件丢了 6 个 cell（3 场各 2 个，都是 leg_byes），加上局号后 C/D 都恢复到 48/48；3 个跨局命中全部消失。qwen 的 B→D 也 +6.25pp，命中 2→1。

**例外 1（qwen 的标签不单调）**：qwen 在 A→C（原顺序加标签）是 41→44（+6.25pp），但在 C→D（换序加标签）是 44→43（−2.1pp）。也就是说，局号在原顺序下帮助更大，换序后反而引入 1 个新错。

**例外 2（llama 基本平）**：llama 的 A/B/C/D 都在 42–43/48，B→D 只 +1 个 cell；局号标注对它的作用很弱。

**例外 3（跨局串值很弱）**：与旧句级 shuffled 中 match_0182 整块搬运（bat_sum 295、extras 17、wides 12、no_balls 1）不同，本次完整证据段换序只出现 0–3 个命中，且多为 0/1 默认值。**旧现象对句级 scrambling 敏感，对完整段落移动不敏感。**

## 6. 通俗回答

**跨局错值出现在哪些比赛和模型？**  
主要出现在 inn1.leg_byes：gemma 在 match_0065/0043/0063 的 B 条件各有 1 个；qwen 在 match_0198（A/B/D）和 match_0063（B）各 1 个；llama 在 match_0198（B）1 个。没有出现 total_extras/wides 的跨局命中。

**标局号有没有帮助？**  
有，但不均匀。gemma 最明显：B 的 6 个错误在 C/D 全部恢复，3 个跨局命中全部消失；qwen 在换序后 +6.25pp、命中 2→1；llama 只有 +1 个 cell。qwen 在“原顺序加标签”比“换序加标签”更好，说明标签不能修复所有位置效应。

**下一轮最值得投入什么？**  
先不要扩大句级 scrambling；应该用**完整证据段**在更多独立比赛上复验，并固定 leg_byes 的 0/1 默认值控制。若跨局串值仍只有个位数，就把旧“串值”主张收窄为“句级打乱下的现象”；同时把 Lina 的推导版作为主题型——因为三个模型都在“只给改判通知、不给新 figures”时保留旧值，这是比泛泛的状态维护更具体、更可复现的失败。

## 7. 文件

- DESIGN.md：设计、样本清单、四条件差异、指标
- samples.json / lina.json：文本、字段、金标
- runs/main.jsonl、runs/lina.jsonl、runs/retest.jsonl：原始输出
- scores.json、lina_scores.json：逐字段评分
- runner.py、score.py、score_lina.py：可复算脚本

## 8. 复现命令

    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_samples.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/build_lina.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task main
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task lina
    python VETT_INTEGRATED_20261113/analysis/pilot_next/runner.py --task retest
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score.py
    python VETT_INTEGRATED_20261113/analysis/pilot_next/score_lina.py



---

## 附录 A27：证据升级更正

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_evidence_upgrade_20261115/CORRECTION.md（75 行）

# CORRECTION：已有结果零调用复算

日期：2026-11-15
旧输入：VETT_INTEGRATED_20261113/analysis/vett_overnight_20261114/

## 1. U 解析四层

| 层 | 数量 |
|---|---:|
| 服务发起 | 1311 |
| 收到响应 | 1311 |
| JSON 成功 | 1304 |
| 按字段协议可评分 | 1304 |

- 旧报告同时写“解析成功 1311/1311”是错的；Qwen 有 7 条 JSON/格式失败。
- 服务成功不等于可评分；后续主表应统一以 1304 为可评分分母，并另报 7 条格式失败。

## 2. U 四组

| 组 | 数量 |
|---|---:|
| 两格都对 | 598 |
| 只对 total_runs | 67 |
| 只对 total_wickets | 101 |
| 两格都未对 | 545 |
| 合计 | 1311 |

- 598+67+101+545=1311。
- 这 545 条只表示旧评分未对，不等于原文不可答。

## 3. 局位与比赛根

- 唯一局位：437。
- 独立比赛根：219。
- 缺失局位：3：
  - match_0004 第一局
  - match_0004 第二局
  - match_0066 第二局

原因需按记分表局数/解析情况逐条核实；不能把 437 局位或 1311 响应当成 437 场独立比赛。

## 4. D+ 与 O 同根同模型配对

| 变体 | 配对数 | O 正确 | 变体正确 | 救回 | 改坏 | 都对 | 都错 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 移除局中比分 | 54 | 44 | 41 | 0 | 3 | 41 | 10 |
| 第二落点 | 45 | 37 | 34 | 1 | 4 | 33 | 7 |
| 移除另一局比分 | 30 | 28 | 27 | 0 | 1 | 27 | 2 |

- 三个变体净变化均为负：−3、−3、−1。
- 旧报告写“移除另一局比分 27/30 最稳”只对绝对数成立；同根配对后它对 O 是 28→27，仍改坏 1。
- 不能用 27/30 与 34/45 直接比较干预优劣。

## 5. T 整表同格配对

新 6 根 0183–0188：

| 项 | 数量 |
|---|---:|
| 基线正确 | 62/72 |
| locator 正确 | 63/72 |
| 救回 | 1 |
| 改坏 | 0 |
| 都对 | 62 |
| 都错 | 9 |

- 唯一变化：match_0186，Qwen，inn2.total_wickets：基线 2，locator 1，金标 1。
- 加上旧 6 根 68→68，合计 130→131；收益只有 1 格，不能写成稳定方法。

## 6. 结论修正

- U 可评分分母 1304，不是 1311。
- D+ 三变体与 O 配对后均净负；此前绝对数比较会误导。
- T locator 只多 1 格且只涉及 1 个模型/1 个格。
- 旧“失败 0”只指基础设施；模型 JSON 失败 7 条必须单列。


---

## 附录 A28：自治工作流执行报告（11-17）

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/EXECUTION_REPORT_20261117.md（206 行）


# VETT 本地自治实验工作流执行报告

- 执行日期：2026-11-17
- 执行窗口：21:40:02 – 21:49:32（Asia/Shanghai）
- 报告整理：2026-11-18
- 最终状态：stopped（可 resume）
- 外部 API：0

## 1. 执行摘要

本次执行把 VETT 从“聊天里手动跑批”改造成可脱离会话的本地实验工作流，并完成实际启动与验收。

| 项目 | 结果 |
|---|---:|
| 已评分批次 | 10（B001–B010） |
| 已冻结待跑批次 | 1（B011，3 个任务） |
| 本地模型请求 / 结果行 | 54 / 54 |
| 任务行 / 唯一键 | 57 / 57 |
| 决策记录 | 11 |
| 使用比赛根 | 14 |
| 保留根越界 | 0 |
| 外部 API 调用 | 0 |
| 实验内容人工介入 | 0（验收的 kill/stop 为测试操作） |

验收结论：**通过**。12 项验收全部 PASS，详见第 7 节。

## 2. 环境与入口检查

实际执行并以真实输出为准：

    dsh --version
    0.2.2-rc.1

    dsh --help
    dsh web
    dsh headless "run the tests"
    dsh tui --resume <session>
    dsh plugin --profile tui add <package>

会话内另有 schedule_create / schedule_edit 定时任务工具。

判断：

- DSH 具备 CLI、一次性 headless、TUI 会话恢复与定时任务入口。
- 但 headless 与聊天入口都会驱动外部模型，无法满足“外部 API 0”。
- 因此实验执行器采用独立本地 Python 进程，直接调用 127.0.0.1:11434 的 Ollama；DSH 只保留交互与恢复入口。
- Python：C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe（3.12.14，sqlite 3.53.1）。系统 python 是 WindowsApps 占位，未使用。
- Ollama 0.40.16；Qwen2.5:7b-instruct-q4_K_M、Llama3.1:8b、Gemma2:9b 均在本地，digest 写入每条结果。

## 3. 交付物

工作目录：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117

    vettctl.py      启动、状态、暂停、恢复、停止、快照、报告
    supervisor.py   单实例调度、恢复、评分、决策、计时器
    worker.py       唯一 GPU 推理进程，一次一个请求
    planner.py      T1–T5 模板、资格检查、冻结、R0–R9 决策与回退
    scorer.py       批次评分、配对、反例、研究记忆
    reporting.py    15 分钟状态、小时快照、覆盖审计
    vettlib.py      SQLite、Ollama、条件变体、金标与评分基础库
    state/workflow.db
    batches/ runs/ reports/ logs/

状态库表：meta、batches、tasks、results、decisions、events、candidates。

请求唯一键：

    task_key = sha256(match | innings | model | cond | field_scope | prompt_sha)

领取使用 BEGIN IMMEDIATE + 条件更新，记录 claimed_by、claimed_at、attempts、recoveries；worker 死亡或心跳超 150 秒自动退回 queued；结果已落盘则标记 recovered_with_existing_result，避免重复推理。

## 4. 运行时间线（主要节点）

| 时间 | 事件 |
|---|---|
| 21:40:02 | start；supervisor 24948 / worker 24696；B001 冻结 |
| 21:40:38 | B001 评分 1.0，R1 冻结 B002 |
| 21:40:42 | 模拟中断：worker 24696 被杀；任务恢复，worker 9872 重启 |
| 21:41:06 | B002 0.8333，R4 冻结 B003 |
| 21:41:48 | B003 0.1667；WI 0.0 < OI 0.5，R5 冻结 B004 |
| 21:42:40 | B004 0.1938，R6 冻结 B005 |
| 21:42:54 | B005 0.8333，R4 冻结 B006 |
| 21:43:40 | stop，pids 清空 |
| 21:43:41 | restart；R8 冻结 B007 |
| 21:44:09 | B007 0.0，R9 冻结 B008 |
| 21:44:20 | stop，requeued_claimed=1 |
| 21:44:42 | restart，B008 继续 |
| 21:47:23 | B008 0.9167，R1F 回退冻结 B009；stop |
| 21:47:51 | B009 0.0，R9 冻结 B010 |
| 21:47:53 | stop |
| 21:48:49 | restart；21:48:50 强制快照；21:49:05 stop |
| 21:49:22 | restart；B010 评分 1.0；21:49:32 R1F 冻结 B011 并 stop |

最终 B011 的 3 个任务在 queued，state=stopped。

## 5. 批次结果

| 批次 | 模板 | 根 | 条件 | 请求 | 格正确 | 准确率 |
|---|---|---|---:|---:|---:|---:|
| B001 | T1 基线 | 0066, 0085 | O | 6 | 12/12 | 1.0000 |
| B002 | T2 困难摘录 | 0002, 0003 | E | 6 | 10/12 | 0.8333 |
| B003 | T3 配对删除 | 0002 | O/WI/OI | 9 | 3/18 | 0.1667 |
| B004 | T4 整表 | 0002 | O | 3 | 25/129 | 0.1938 |
| B005 | T2 困难摘录 | 0008 | E | 3 | 5/6 | 0.8333 |
| B006 | T3 配对删除 | 0008 | O（WI/OI 不可用） | 3 | 0/6 | 0.0000 |
| B007 | T5 困难全文 | 0009, 0010 | O | 6 | 0/12 | 0.0000 |
| B008 | T1 基线扩展 | 0087, 0096 | O | 6 | 11/12 | 0.9167 |
| B009 | T5 困难全文 | 0011, 0013 | O | 6 | 0/12 | 0.0000 |
| B010 | T1 基线扩展 | 0165, 0021 | O | 6 | 12/12 | 1.0000 |
| B011 | T5 困难全文 | 0015 | O | 3 待跑 | — | — |

批次差异：

- B001/B008/B010：开发根原文基线。
- B002/B005：困难根三句证据摘录。
- B003/B006：同根 O / 删同局局中比分 WI / 删另一局总分 OI 配对对照。
- B004：单根 43 字段整表。
- B007/B009/B011：无可用 E 时的困难根全文回退。

## 6. 决策链

| 时间 | 规则 | 选择 | 下一批 | 理由摘要 |
|---|---|---|---|---|
| 21:40:02 | R0 | T1 | B001 | 初始基线 |
| 21:40:38 | R1 | T2 | B002 | 基线 1.0 饱和 |
| 21:41:06 | R4 | T3 | B003 | 摘录仍 0.833 |
| 21:41:48 | R5 | T4 | B004 | WI 0.0 < OI 0.5，删除特异 |
| 21:42:40 | R6 | T2 | B005 | 整表完成，扩下一组困难根 |
| 21:42:54 | R4 | T3 | B006 | 摘录仍 0.833 |
| 21:43:41 | R8 | T5 | B007 | 无剩余困难根支持 E |
| 21:44:09 | R9 | T1 | B008 | 困难全文完成，扩剩余开发根 |
| 21:47:23 | R1F | T5 | B009 | T2 无合格任务，回退 T5 |
| 21:47:51 | R9 | T1 | B010 | 扩剩余开发根 |
| 21:49:32 | R1F | T5 | B011 | T2 无合格任务，回退 T5 |

每条决策的 observation、rationale、next_batch_id 在 decisions 表；RESEARCH_MEMORY.md 同步了可读版本。

## 7. 验收结论

| 验收项 | 结果 | 证据 |
|---|---|---|
| 无人工介入完成≥3 批差异实验 | PASS | 10 批已评分 |
| 上一批结果触发下一批并保存理由 | PASS | 11 条 decisions |
| 模拟可恢复中断并续跑 | PASS | 21:40:42 恢复，任务 attempts=2/recoveries=1，仅 1 条结果 |
| 关闭启动终端仍有响应落盘 | PASS | 21:40:02 启动；调用结束后 21:40:26 已 3 条完成 |
| stop 同时停派发与监督器重启 | PASS | 最终 21:49:32；12 秒内 results 54=54，pids 清空 |
| 单 GPU worker | PASS | PowerShell 1 worker / 1 supervisor；领取 pid 串行 |
| 15 分钟状态 / 小时快照 | PASS | 阈值测试 7/7；快照后 48→52 条结果 |
| 外部 API 0 | PASS | meta.external_api_calls=0；URL 全部 127.0.0.1 |
| 保留根隔离 | PASS | 14 根，0121–0160 越界 0 |
| 唯一键、工作锁、恢复记录 | PASS | 57/57 唯一键 |
| 43 字段整表复用 | PASS | B004 129 格，沿用 full_table.py 定义 |
| 研究记忆与原始路径 | PASS | RESEARCH_MEMORY.json/md，runs/B0xx.jsonl |

## 8. 主要发现

- 开发根目标格接近饱和：B001 12/12、B008 11/12、B010 12/12。
- 困难根加三句证据摘录仍只有 0.8333（B002 10/12、B005 5/6），不支持“失败完全由长上下文稀释造成”。
- B003 的 O 与 WI 都是 0.0，OI 为 0.5；删除另一局总分反而让 3 个格恢复，提示跨局比分干扰。样本仅 18 格，不能当作稳定结论。
- B004 目标两格 7/12（58.3%），但整表 25/129（19.4%），说明目标格饱和会掩盖整表损失。
- B007/B009 的困难根全文目标格 0%，与“文本没有明确总分句”的可答性缺口一致，不是单纯格式失败。

## 9. 问题与边界

- B011 未跑完（3 个 queued），当前实验结论只基于 B001–B010。
- B006 的 WI/OI 变体不可用，实际只生成 O 的 3 个请求；candidates 表记录了 variant_unavailable。
- 人工盲审 0/40；证据索引 96 条仍 pending_human_review，未并入自动结论。
- 15 分钟状态由“阈值 + 每次批次转移即写”共同保证；小时快照阈值由隔离测试验证，生产运行未连续等待 60 分钟，21:48:50 / 21:49:48 为显式快照。
- decisions.batch_id 统一记为 genesis，批次链条靠 next_batch_id 与 created_at 还原；不影响选择，但后续可改为上一批 id。
- B011 的批次状态仍为 running、任务为 queued，这是为 resume 保留的中断态。

## 10. 下一批任务（B011）

| 根 | 局 | 模型 | 条件 | 字段 |
|---|---:|---|---|---|
| match_0015 | 2 | qwen2.5:7b-instruct-q4_K_M | O | inn2.total_runs, inn2.total_wickets |
| match_0015 | 2 | llama3.1:8b | O | inn2.total_runs, inn2.total_wickets |
| match_0015 | 2 | gemma2:9b | O | inn2.total_runs, inn2.total_wickets |

## 11. 复现命令

    cd "D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117"
    PY="/c/Users/PC/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe"

    "$PY" vettctl.py start
    "$PY" vettctl.py status --md
    "$PY" vettctl.py pause
    "$PY" vettctl.py resume
    "$PY" vettctl.py stop
    "$PY" vettctl.py snapshot
    "$PY" vettctl.py report

## 12. 证据索引

- 验收日志：ACCEPTANCE.md
- 架构说明：README.md
- 操作命令：COMMANDS.md
- 最终状态：reports/STATUS.md
- 研究记忆：reports/RESEARCH_MEMORY.md
- 机器可读验收数据：reports/ACCEPTANCE_DATA.json
- 覆盖缺口：reports/COVERAGE_GAP.md
- 批次原始结果：runs/B001.jsonl … runs/B011.jsonl
- 批次评分：reports/B001_SCORE.json … reports/B010_SCORE.json
- 决策与事件：state/workflow.db 的 decisions、events 表
- 计时器测试：tests/test_timers.py


---

## 附录 A29：执行汇总（11-18 至 11-19）

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/DAILY_SUMMARY_20261118.md（93 行）

# VETT 执行汇总（2026-11-18 14:50 → 2026-11-19 09:10）

## 0. 结论

- 8 小时无人值守验收在 2026-11-19 08:24:45 达成，08:00 阶段报告已生成且推理继续。
- 运行在 09:09:18 后随主机重启（boot 09:10:15）终止，全程 8h44m；不是代码异常。
- 当前状态已修正为 stopped（stop_reason=host_reboot_20261119_0910），可 resume。

## 1. 关键数字

- 结果：3502；attempts：3453；批次：149；任务：3507
- 外部 API：0
- 小时报：14 份；08:00 阶段报告：1 份
- sweep_cursor：360/360；probe_cursor：172/360
- 人工复核：7 条记录 pending_human_review

## 2. 时间线

- 2026-11-18 14:50:24 启动旧连续段。
- 19:13:30 旧段死亡：主机休眠 + Ollama 停止；旧段 4h23m，不计入 8h。
- 2026-11-19 00:24:45 新连续段重启（keep-awake + Ollama watchdog）。
- 08:00 生成 STAGE_20261119_0800.md；08:24:45 达成 8 小时。
- 09:09:18 最后结果；09:10:15 主机重启，进程终止。

## 3. 批次结构

- S_coverage_sweep: 88 批，平均准确率 0.554
- P_field_sweep: 43 批，平均准确率 0.503
- T1_baseline_o: 4 批，平均准确率 0.9375
- T5_hard_fulltext: 3 批，平均准确率 0.0
- T3_matched_deletion: 3 批，平均准确率 0.1296
- T2_hard_excerpt: 2 批，平均准确率 0.8333
- C_adjudication: 2 批，平均准确率 0.95
- T4_full_table: 1 批，平均准确率 0.1938
- B_cross_innings: 1 批，平均准确率 0.0
- B2_matched_control: 1 批，平均准确率 0.0
- A_field_probe: 1 批，平均准确率 0.9167

- B001–B010：历史基线/摘录/删除/整表。
- B011–B015：v2 续跑与旧模板。
- B016–B106：S_coverage_sweep，1,959 results，cursor 360。
- B107–B149：P_field_sweep，probe_cursor 172。

## 4. 研究结论

- 覆盖组同根配对：E +75、OI +16（根依赖）、WI +3。
- E 的 10 个反例是 wickets 绑定/空答，不是缺证。
- B002/B005：runs 全对，wickets 4/6、2/3。
- B003：O 0/6、WI 0/6、OI 3/6；OI 收益未被长度匹配 NEI 复现，标为未定。
- B004：43 字段含两局，目标四格 7/12；全字段 25/129，可核实子集 24/105。
- B007/B009：加入英文数字词后 B009 6/6 有明确总分句，0% 不是缺证。
- 分支 C：C_change 12/24、C_maintain 23/24、C_no_notice 24/24；错误集中在改判后的 A−1/B+1 传播。
- P 字段探针前 266 条：runs 51.1%、wickets 44.9%、both 格 49.4%。

## 5. P 字段探针（当前累计）

- probe_both: 513 任务，任务准确率 0.4444，格准确率 0.5166
- probe_runs: 516 任务，任务准确率 0.5039，格准确率 0.5039
- probe_wickets: 514 任务，任务准确率 0.4689，格准确率 0.4689

## 6. 可靠性修复

- v2 任务身份、task_key_map、attempts 生命周期（sent/responded/persisted/accepted/uncertain）。
- 心跳独立于长请求；不再因单请求超过 150 秒判死。
- 状态区分 workflow/batch/task；stale running 已修正。
- S→P 接续修复：S 无合格任务时 cursor 置 360 并回退 P。
- Windows keep-awake（SetThreadExecutionState）与 Ollama watchdog。
- 主机重启无法由进程内机制防止；如需跨重启，需要 Windows 计划任务/服务自启动。

## 7. 验收

- 生产 1 小时：通过。
- 连续 2/3 小时：通过。
- 8 小时：通过（新段 00:24:45–08:24:45）。
- 08:00 阶段报告：通过，且推理继续。
- 48 小时有效队列：未达到。
- exactly-once：不宣称；结果持久化一次，尝试可多次。

## 8. 产物

- ACCEPTANCE_V2.md、MILESTONE_8H.md、SCIENCE_CORRECTIONS.md、BRANCH_C.md
- COVERAGE_GROUP/PAIRED/COUNTEREXAMPLES、PROBE_SWEEP_PARTIAL
- records/INDEX.json（7 条）、data_patches/（5 个）
- reports/HOURLY_*.md（{len(hourly)} 份）、STAGE_20261119_0800.md
- INCIDENT_20261118_1913.md、INCIDENT_20261119_0910.md

## 9. 未完成与下一阶段建议

1. 人工复核 7 条记录。
2. 48 小时有效队列仍有缺口；当前估算 10–18 小时不同任务。
3. 主机重启后自动恢复：需要 Windows 计划任务/服务，而不是仅 keep-awake。
4. 规划仍是 rule_template，未接通 DSH 自动分析。
5. 如继续 P_field_sweep：vettctl.py start，从 probe_cursor 172 继续。


---

## 附录 A30：科学结论修正（B002–B015）

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/SCIENCE_CORRECTIONS.md（136 行）


# B002–B015 原始输入/输出复核与科学结论修正

复核日期：2026-11-18。全部离线完成，未调用模型。来源：runs/B0xx.jsonl、batches/B0xx.json、scorecard.md、commentary.txt。

## 0. 先纠正三条口径

- 同一 task_key 有结果，只说明“结果已持久化”，不说明底层推理恰好发生一次。
- 模型全错不等于缺证；必须先核对原文是否有明确依据。
- 43 字段整表包含两局，目标子集是 4 格（每局 runs/wickets），不是每局只有 2 格就够。

## 1. B002 / B005：摘录逐字、终局、字段分裂

| 批次 | 摘录逐字 | 终局句 | runs | wickets |
|---|---|---:|---:|---:|
| B002 | 6/6 | 6/6 | 6/6 | 4/6 |
| B005 | 3/3 | 3/3 | 3/3 | 2/3 |

结论：摘录确实来自目标文本、属于目标局、包含终局总分；失败集中在 wickets，不是摘录定位失败，也不是 runs 抽取失败。B002/B005 的 0.8333 应解释为“wickets 字段绑定错误”，不能笼统写成“困难摘录失败”。

## 2. B003：删除内容逐字与配对

- WI 删除句：That wicket gave Crestview a real opening, because Ryan Cole was soon run out and Logan Shaw followed after a brief stay, leaving Harborfield at 133 for 4 ...
  - 这是同局局中比分，不是目标终局句；目标证据在 WI 中仍保留。
- OI 删除句：... by the time Harborfield closed on 252 for 8 from 36 overs ...
  - 这是另一局总分；目标局证据在 OI 中仍保留。
- 每个变体只删 1 句；O 6599 字符，WI 6329，OI 6234。
- 配对：O 0/6，WI 0/6，OI 3/6；OI 相对 O 净 +3 格。

结论：现有 B003 支持“跨局比分干扰”这一候选解释，但样本只有 18 格，不能当作稳定效应。需要补长度匹配的非证据删除对照（OIC/NEI），并按同根、同局、同模型、同字段配对。

## 3. B004：整表分母与可答子集

- 43 字段确实同时包含 inn1 与 inn2；目标子集为 inn1.total_runs、inn1.total_wickets、inn2.total_runs、inn2.total_wickets 四格。
- 全字段：25/129 = 19.38%。
- 金标字符串在原文中出现的 35 个字段子集：24/105 = 22.86%。
- 目标四格：7/12 = 58.33%。
- 8 个字段的金标字符串未在原文找到（match.result、match.toss、inn1.overs、inn1.wides、inn1.bowl2_runs、inn2.overs、inn2.bat3_name、inn2.bowl2_runs）。

结论：25/129 不是“已验证整表能力”，只是当前 43 格全分母读数。可答子集 24/105 仍低，说明非目标字段有真实损失；但 8 个未在原文找到的字段只能标为“文本未核实”，不能自动归入缺证。目标四格 7/12 与整表 19.38% 的落差成立。

## 4. B007 / B009：0 分不等于缺证

- 初次数字正则把 187 for five、132 for six 判为“无明确总分句”，这是检测器缺陷。
- 加入英文数字词后：B009 6/6 任务存在明确总分句；B007 3/6（match_0009 有，match_0010 无）。
- 因此 B009 的 0% 是“有明确证据但模型仍错”，不是缺证；B007 为混合组，必须逐任务分类。

结论：禁止用“模型全错”反推缺证。缺证判定必须来自原文核对，且要区分数字形式与英文数字词。

## 5. B011–B015 与字段探针

- B011 0.0：match_0015 inn2 全文。
- B012 0.9167：同句证据下 probe_runs 10/12、probe_wickets 12/12；qwen 在 match_0066 的 runs-only 与 both 返回 null，wickets 全对。
- B013 0.0：B 分支只生成 OIC 3 个任务，O/E/OI 因旧任务身份去重被跳过；这是去重正确、设计对照不完整，配对必须回连 B003 的 O。
- B014 0.8333：剩余开发根基线。
- B015 0.2222：T3 删除对照。

结论：B012 把“runs 缺失”和“wickets 正确”分开，支持字段绑定诊断；B013 的 0 分不能当作 OIC 条件效应，因为批内没有 O 基线。

## 6. 尝试账目

- 新代码运行后 attempts 表记录每次领取；当前结果行 98，attempts 47（legacy 54 条结果没有 attempt 记录）。
- 2 条 uncertain 来自受控 stop：任务已发送但未持久化，服务端是否执行未知。
- 因而不宣称 exactly-once；只宣称“结果持久化一次，尝试可能多次”。

## 7. 待补

- B013 与 B003 历史 O 的跨批配对。
- B004 可答字段的人工确认（当前只是字符串存在性检查）。
- 匹配长度非证据删除对照。
- 英文数字词的更广核对（不止 wickets）。


## 8. 长度匹配 NEI 对照（B021）

- OI 删除句 364 字；NEI_OI 删除 313 字，差 51。
- WI 删除句 269 字；NEI_WI 删除 251 字，差 18。
- B021 结果：NEI_OI 0/6，NEI_WI 0/6；B003 O 0/6、OI 3/6。
- 结论：删掉长度匹配的非证据句也会让模型全错，不能把 B003 的 OI +3 直接解释为“删另一局比分”的特异收益。该效应应标为未定，需更多匹配对照。


## 9. 覆盖组与诊断组分开（截至 15:51）

覆盖组（S_coverage_sweep，426 results）：

| 条件 | 格正确率 |
|---|---:|
| E | 0.9537 |
| OI | 0.7407 |
| WI | 0.6875 |
| O | 0.5458 |

诊断组（非 sweep，669 格）：0.6816。

- 覆盖组里 E 明显高于 O，说明短证据在广泛根上帮助很大；这是覆盖组结论，不与 B002–B022 的困难组混算。
- 条件样本不平衡：E 只在有明确总分句的根上可用，因此 O/E 的差距不能直接当作单一因果效应。
- 覆盖组保留单独报告：reports/COVERAGE_GROUP.md。


## 10. 覆盖组内同根配对（E/WI/OI vs O）

按同根、同局、同模型、同字段配对：

| 条件 | 配对数 | O 对 | V 对 | gain | loss | net |
|---|---:|---:|---:|---:|---:|---:|
| E | 264 | 166 | 241 | 85 | 10 | +75 |
| OI | 132 | 83 | 99 | 17 | 1 | +16 |
| WI | 84 | 47 | 50 | 5 | 2 | +3 |

- E 的提升在三个模型上都为正（qwen +18、llama +29、gemma +28）。
- OI 在覆盖组内也略正（+16），与 B020 的“OI 伤害”方向相反，说明 OI 效应依赖根。
- WI 几乎为零。
- E 仍受“只有明确总分句才可用”的限制，配对 n 与 OI/WI 不同。


## 11. 覆盖组反例：E 的 10 个 loss

- E 相对 O 共 264 对，gain 85、loss 10、net +75；loss 不是“摘录缺证据”造成的。
- 例 1：match_0001 inn1 llama，摘录含 “144 all out”，模型把 wickets 给成 35（疑似把 runs 当 wickets）。
- 例 2：match_0017 inn1 qwen，摘录含 “174 all out”，模型返回 null。
- 例 3：match_0049 inn2 qwen，摘录含 “96 all out”，模型返回 null。
- 结论：E 的失败集中在 wickets 字段绑定/空答，而不是证据不可用；与 B002/B005 的 wickets-only 失败一致。
- OI 的净效应集中在少数根：match_0001/0012 各 +4，match_0049 −1，多数根 0；进一步说明 OI 不是稳定单向效应。


## 12. P_field_sweep 部分结果（前 266 条）

| 问法 | 任务数 | 任务准确率 | 格准确率 |
|---|---:|---:|---:|
| 只问 runs | 90 | 0.5111 | 0.5111 |
| 只问 wickets | 89 | 0.4494 | 0.4494 |
| 同时问两者 | 87 | 0.4713 | 0.4943 |

- runs 比 wickets 略容易（51.1% vs 44.9%），与 B002/B005 的 wickets-only 失败一致。
- 同时问两者没有出现明显字段混淆惩罚：格准确率 49.4%，介于两者之间。
- 这是覆盖组的字段探针，不与 B002–B022 困难组混算；样本仍在增长。


---

## 附录 A31：验收日志 V2

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/ACCEPTANCE_V2.md（153 行）


# 验收口径修正（v2）

原“12 项全部 PASS”过于笼统。现拆为三类。

## A. 已通过短时实际验证

- 10 个历史批次（B001–B010）已评分；v2 后 B011–B015 继续评分。
- 受控 stop/start：pids 清空、claimed 退回 queued、不再派发。
- 恢复：claimed 任务写 uncertain 后重跑；results 只保留一条。
- 脱离终端：启动调用返回后仍落盘。
- 单 worker：PowerShell 计数 1/1。
- 外部 API 0。

## B. 已通过隔离测试

- 计时器阈值：tests/test_timers.py 7/7。
- v2 freeze：tests/test_v2_freeze.py，18 个 A 分支任务、身份列、task_key_map 全部写入。
- 离线审计：B002–B009 原文/金标复核，见 SCIENCE_AUDIT 与 AUDIT_FOLLOWUP。
- 去重：v2 任务身份与 task_key_map 能阻止旧任务整体重跑。

## C. 尚待长时间运行验证

- 连续 8 小时无人值守：尚未完成。此前 9 分 30 秒运行不算整夜验收。
- 生产环境连续 1 小时快照：尚未完成。阈值测试不等于生产已连续跑满一小时。
- 08:00 阶段报告：下一次 08:00 才触发；当前 14:50 启动。
- 48 小时有效队列：未达到，见 RUN_PLAN_48H.md。
- 分支 C：B019+B022 共 8 事件、72 任务；C_change 12/24，C_maintain 23/24，C_no_notice 24/24。错误集中在正式改判后的 A−1/B+1 传播。
- 底层推理 exactly-once：不宣称；attempts 记录 sent/responded/persisted/accepted 与 uncertain。

## D. 当前运行

- 启动：2026-11-18 14:50:24。
- 已启用 coverage sweep；sweep_cursor 从 0 开始，360 个 unit。
- 每小时写 HOURLY_<stamp>.md；08:00 写 STAGE_<date>_0800.md；两者都不停止推理。
- 状态报告区分 workflow_state / batch_state / task_state；stopped 时显示 interrupted_batch，不显示 running。

## E. 边界

- 人工复核 0；所有证据状态保持 pending_human_review。
- 规则模板驱动；planning_mode=rule_template。未接通 DSH 自动分析，不宣称自主提出研究假设。
- 外部 API 0；仅 127.0.0.1:11434。


## F. 首个小时报（生产验证）

- 文件：reports/HOURLY_20261118_155025.md
- 触发：14:50:24 启动，15:50:25 写盘，间隔 3601 秒。
- 1 小时：591 results / 541 attempts / 3 uncertain / 0 exceptions。
- 耗时拆分：load 3,012,266.9 ms；inference 438,800.8 ms；scoring 171.2 ms；planning 1,884.6 ms；waiting 估计 3,161,143.4 ms。
- 结论：Ollama 模型加载占首小时约 84%，是吞吐主瓶颈；推理本身只占约 12%。


## G. 覆盖组

- S_coverage_sweep 426 results：E 0.9537、OI 0.7407、WI 0.6875、O 0.5458。
- 与诊断组（0.6816）分开报告；不把覆盖组速率写成全池错误率。
- 文件：reports/COVERAGE_GROUP.md / .json。

## H. 字段探针覆盖

- P_field_sweep 已启用：360 unit × 3 变体 × 3 模型 = 3,240 任务；S + P 约 7,560 个不同任务位，估算 12.8 小时。
- 覆盖 8 小时里程碑，但仍不足以覆盖 48 小时。


## I. 连续 2 小时验证

- 15:50:25 与 16:50:26 连续两次小时报，间隔均为 3601 秒。
- 2 小时：851 results / 802 attempts / 4 uncertain / 0 exceptions。
- 耗时：load 6,157,691.8 ms；inference 627,030.1 ms；scoring 257.3 ms；planning 4,462.5 ms；waiting 估计 6,570,950.1 ms。
- 第 1 小时 591 条，第 2 小时 260 条；后半段全文本 O 提示更长，吞吐下降。
- 8 小时里程碑仍未到。


## J. 连续 3 小时验证

- 14:50:24 启动；15:50:25、16:50:26、17:50:27 连续三份小时报，间隔均 3601 秒。
- 3 小时：1,091 results / 1,042 attempts / 4 uncertain / 0 exceptions。
- load 9,385,650.3 ms；inference 781,754.1 ms；scoring 336.9 ms；planning 7,243.3 ms。
- 第 3 小时 240 条，延续全文本 O 的低吞吐；load 仍占约 86%。


## K. 夜间中断与重启

- 旧连续段 2026-11-18 14:50:24–19:13:30：4h23m，5 份小时报；**8 小时未达成**。
- 死因：主机空闲休眠导致 supervisor/worker 停止，同时 Ollama 服务停止；日志无异常，主机未重启。
- 修复：SetThreadExecutionState keep-awake；Ollama 每分钟 watchdog；新 segment_started_at。
- 新连续段：2026-11-19 00:24:45 起，supervisor 12068 / worker 26892；8 小时里程碑 **08:24:45**，08:00 阶段报告落在本段内。


## L. S→P 接续（2026-11-19 02:05）

- S_coverage_sweep 到 cursor 350 时剩余 unit 已无合格任务；旧逻辑仍返回 S，导致 no_eligible_tasks 并进入 idle。
- 修复：S 模板无任务时把 sweep_cursor 置 360，并回退 P_field_sweep。
- 结果：B107 P_field_sweep 自动冻结，36 任务，probe_cursor 4；S 共跑到 B106。
- 01:24:46 新段第一份小时报已验证（3601.2 秒）；8 小时里程碑仍为 08:24:45。


## M. 新段连续 2 小时

- 新段 00:24:45 起；01:24:46 与 02:24:47 两份小时报，间隔 3601 秒。
- 02:24 时结果 2,219；P_field_sweep 已到 probe_cursor 32。
- 8 小时里程碑仍为 08:24:45；08:00 阶段报告落在本段内。


## N. 新段连续 3 小时

- 00:24:45 起；00:24:45、01:24:46、02:24:47、03:24:49 连续四份小时报。
- 03:24 时结果 2,550；P_field_sweep 到 probe_cursor 68。
- 8 小时里程碑 08:24:45；08:00 阶段报告仍落在本段内。


## O. 新段连续 4 小时

- 00:24:45 起；00:24:45 / 01:24:46 / 02:24:47 / 03:24:49 / 04:24:51 连续五份小时报。
- 04:24 时结果 2,739；P_field_sweep 到 probe_cursor 88。
- 8 小时里程碑 08:24:45；08:00 阶段报告仍在本段内。


## P. 新段连续 5 小时

- 00:24:45 起；00:24:45 / 01:24:46 / 02:24:47 / 03:24:49 / 04:24:51 / 05:24:54 连续六份小时报。
- 05:24 时结果 2,909；P_field_sweep 到 probe_cursor 108。
- 8 小时里程碑 08:24:45；08:00 阶段报告将在约 2.5 小时后触发。


## Q. 新段连续 6 小时

- 00:24:45 起；连续七份小时报至 06:24:57。
- 06:24 时结果 3,073；P_field_sweep 到 probe_cursor 124。
- 8 小时里程碑 08:24:45；08:00 阶段报告约 1.5 小时后触发。


## R. 新段连续 7 小时

- 00:24:45 起；连续八份小时报至 07:24:59。
- 07:24 时结果 3,233；P_field_sweep 到 probe_cursor 144。
- 08:00 阶段报告约 35 分钟后触发；8 小时里程碑 08:24:45。


## S. 8 小时里程碑通过

- 新段 2026-11-19 00:24:45 起，08:24:45 达成 8 小时；最后结果 08:24:54。
- 9 份小时报连续；08:00 阶段报告 STAGE_20261119_0800.md 已生成，推理继续。
- 3,389 results / 3,340 attempts / 4 uncertain / 0 exceptions；external API 0。
- 48 小时有效队列仍未达到；人工复核仍 pending。


## T. 主机重启终止

- 8 小时里程碑已于 08:24:45 通过；09:09:18 最后结果，09:10:15 主机重启，进程终止。
- 全程 8h44m；不是代码异常。状态已修正为 stopped（host_reboot_20261119_0910）。
- 主机重启无法由 keep-awake 防止；跨重启自动恢复需 Windows 计划任务/服务。


---

## 附录 A32：8 小时里程碑

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/MILESTONE_8H.md（34 行）

# 8-hour unattended milestone

- Segment start: 2026-11-19T00:24:45+08:00
- Milestone reached: 2026-11-19T08:24:45+08:00
- Last result at check: 2026-11-19T08:24:54+08:00 (8h00m09s)
- Workflow state: running; supervisor 6872 / worker 5352
- Results: 3,389; attempts: 3,340; uncertain: 4; exceptions: 0
- Load: 39,503,026.9 ms; inference: 1,994,000.7 ms; scoring: 684.8 ms; planning: 19,147.3 ms
- External API: 0

## Hourly continuity

Nine hourly reports, one per hour:
00:24:45, 01:24:46, 02:24:47, 03:24:49, 04:24:51, 05:24:54, 06:24:57, 07:24:59, 08:25:00.

## 08:00 stage report

reports/STAGE_20261119_0800.md (13,261 bytes), generated at/after 08:00 while inference continued.
Results rose from 3,325 at 08:00:27 to 3,389 by 08:24:54; the workflow did not stop.

## What was verified

- 8h continuous unattended operation after the sleep/Ollama incident.
- keep-awake request and Ollama watchdog active.
- single supervisor / single worker for the whole segment.
- hourly reports and 08:00 stage report written without stopping inference.
- S_coverage_sweep completed; P_field_sweep continued (probe_cursor 160 at milestone).
- Branches A/B/C, audits, 7 traceable records and 5 rollbackable patches exist.

## Not achieved

- 48h valid-queue target: not met; estimated 10–18h of distinct valid work, documented in RUN_PLAN_48H.md.
- Human review: 7 records remain pending_human_review.
- Planning remains rule_template, not model-driven hypothesis generation.


---

## 附录 A33：48 小时覆盖估算与限制

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/RUN_PLAN_48H.md（56 行）


# 48 小时覆盖估算与限制

## 1. 当前有效队列

- sweep unit：360（180 个非保留根 × 2 局）。
- 每批 4 个 unit；每 unit 最多 4 条件（O/E/WI/OI）× 3 模型 = 12 请求。
- 每批最多 48 请求；360/4 = 90 批。
- 首小时实测 591 results/3602 秒 = 6.1 秒/结果；其中 load 3,012 秒、inference 439 秒，load 是主瓶颈。
- 按 591 results/小时估算：4,320 个任务位约 7.3 小时，接近 8 小时里程碑；48 小时约需 28,400 条，仍低于 33,200 的目标。

## 2. 与 48 小时目标的差距

- 48 小时按 5.2 秒/请求约需 33,200 次不同请求。
- 当前合法 sweep 只有约 4,320 个任务位（还会因去重/不可用减少）。
- 因此当前构建器只能覆盖约 7–8 小时，不能覆盖 48 小时。

## 3. 限制

- 保留根 0121–0160 冻结，不用于方法开发。
- 分支 C 已以 36 任务 dev 批（B019）接入，但只覆盖 4 个事件样本，远不足以补足 48 小时。
- E 变体仍受“明确总分句”限制；英文数字词已支持，但并非所有根都可生成。
- 不重复确定性调用；去重后不足的部分不会被硬凑。
- 未构建的理论组合不计入有效队列。

## 4. 下一步扩展

1. 接入 R28 分支 C 的三组条件（正式改判/维持/无通知）× 旧值高/等/低。
2. 为 sweep 增加分层抽样覆盖组与困难组分离报告。
3. 用 B004 可答子集与 B013 跨批配对结果决定是否扩展整表回投。
4. 48 小时目标需要额外的合法根/条件池；在未构建前如实列为未覆盖。


## 5. 字段探针覆盖（P_field_sweep）

- 360 个 unit × 3 变体（runs only / wickets only / both）× 3 模型 = 3,240 任务。
- 每批 4 unit = 36 任务；90 批。
- 与 S_coverage_sweep（最多 4,320）合计约 7,560 个不同任务位。
- 按首小时 591 results/小时估算：约 12.8 小时，足以覆盖 22:50 的 8 小时里程碑。
- 仍不足以覆盖 48 小时；48 小时约需 33,200 条。
- P 与 S 都是覆盖组，单独报告，不与 B002–B022 诊断组混算。


## 6. 两小时实测修正

- 第 1 小时 591 条，第 2 小时 260 条，两小时合计 851 条，平均 425.5 条/小时。
- 后段全文本 O 的提示更长，吞吐低于首小时。
- 按 425 条/小时估算：S 剩余 + P 3,240 条约需 10–18 小时，仍足以覆盖 22:50 的 8 小时里程碑。
- 48 小时仍不足；该估算会随条件组合变化。


## 7. S→P 实际接续

- S_coverage_sweep 于 2026-11-19 02:05 到 B106，累计 1,959 results，cursor 置 360。
- P_field_sweep 于 B107 自动接续，36 任务/批，probe_cursor 4。
- 计划中 P 的 3,240 任务位现在开始兑现；按每分钟约 6 条估算可覆盖到 08:24 之后。


---

## 附录 A34：事故：11-18 休眠与 Ollama 停止

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/INCIDENT_20261118_1913.md（32 行）

# Incident: overnight run died at 2026-11-18 19:13

## Symptom

- Last result and last event: 2026-11-18T19:13:30+08:00.
- Supervisor 26932 and worker 28832 were both dead by 2026-11-19 00:23.
- state meta still said running, with stale pids.
- Ollama endpoint 127.0.0.1:11434 was down (connection refused); no ollama.exe process and no Windows service.
- Logs empty (no traceback); host boot time 2026-11-18 09:08, so no reboot.
- Consistent with host idle sleep / Ollama stop, not a code exception.

## Impact

- Continuous segment 2026-11-18 14:50:24 to 19:13:30 = 4h23m, NOT 8h.
- Five hourly reports were produced (14:50, 15:50, 16:50, 17:50, 18:50).
- 8h milestone at 22:50 was NOT reached.
- 08:00 stage report did NOT run.

## Fix applied

1. Supervisor keep-awake thread: SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED) every 60s.
2. Ollama watchdog: supervisor pings /api/tags every 60s and restarts ollama serve if down.
3. Fresh continuous segment clock: segment_started_at set on start; 8h is measured from the new segment.
4. Restarted 2026-11-19 00:24:45 with supervisor 12068 / worker 26892; B083 resumed.
5. New 8h milestone: 2026-11-19 08:24:45; 08:00 stage report falls inside this segment.

## Evidence

- reports/HOURLY_20261118_145024.md ... HOURLY_20261118_185027.md
- state/workflow.db events: max event 2026-11-18T19:13:30
- logs/supervisor.log and logs/worker.log empty at death
- logs/ollama.log


---

## 附录 A35：事故：11-19 主机重启

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/INCIDENT_20261119_0910.md（9 行）

# Incident: host reboot at 2026-11-19 09:10

- Last result: 2026-11-19T09:09:18+08:00.
- Windows boot time: 2026-11-19T09:10:15+08:00.
- Supervisor 6872 / worker 5352 died with the host reboot; Ollama restarted later (PID 19372).
- This is not a code exception; logs show normal task completion at 09:09:18.
- The 8-hour milestone (08:24:45) had already been reached; the run had lasted 8h44m when the host rebooted.
- State corrected from stale running to stopped (stop_reason=host_reboot_20261119_0910).
- To resume: vettctl.py start (B149 has 4 queued tasks; probe_cursor 172).


---

## 附录 A36：覆盖缺口

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/reports/COVERAGE_GAP.md（24 行）

# Coverage gap

- generated: 2026-11-20T13:24:04+08:00
- reason: no_eligible_tasks

## Covered

- batches run: 199, scored: 199
- parsed positions available: 437
- U full responses: 1311 (JSON-scorable 1304)
- evidence index entries: 96, human confirmed: 0

## Not yet covered

- C missing-evidence matrix
- D R28 low-old-value direction
- E temperature/seed randomness
- F held-out full-table validation
- held-out roots reserved: 40
- unused hard positions: 0

## Conclusion

Exhaustion is claimed only if no builder can produce an eligible task. Otherwise the supervisor continues with the next eligible template.


---

## 附录 A37：阶段报告（11-21 08:00）

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/reports/STAGE_20261121_0800.md（208 行）

# VETT stage report 20261121 08:00

- run elapsed: 0.0 h (1.5 s)
- queue: {"claimed": 1, "done": 6370, "failed": 5, "queued": 1607}
- results: 6370; attempts: 7400; uncertain: 15
- load ms: 43954161.4; inference ms: 19577378.0; scoring ms: 2669.5
- planning ms: 22382.3; waiting ms est: 0.0
- exceptions: 2

## Decisions

- R0 None -> B001: Initial baseline: original text, development roots, target cells only.
- R1 B001 -> B002: Baseline saturated at 1.0; hard roots and a short excerpt are the next discriminator.
- R4 B002 -> B003: Excerpt still fails at 0.833; matched deletion controls on the failing hard root.
- R5 B003 -> B004: WI 0.0 < OI 0.5; deletion-specific damage, validate the full table on original text.
- R6 B004 -> B005: Full-table validation complete; expand coverage on the next unused hard roots.
- R4 B005 -> B006: Excerpt still fails at 0.833; matched deletion controls on the failing hard root.
- R8 B006 -> B007: No remaining hard root has an explicit total sentence for E; run full-text O on unused hard roots instead.
- R9 B007 -> B008: Hard full-text fallback complete; expand the baseline to the remaining unused development roots.
- R1F B008 -> B009: Baseline saturated at 0.917; hard roots and a short excerpt are the next discriminator. | fallback: T2_hard_excerpt produced no eligible task; executed T5_hard_fulltext.
- R9 B009 -> B010: Hard full-text fallback complete; expand the baseline to the remaining unused development roots.
- R1F B010 -> B011: Baseline saturated at 1.0; hard roots and a short excerpt are the next discriminator. | fallback: T2_hard_excerpt produced no eligible task; executed T5_hard_fulltext.
- R10 B011 -> B012: Hard full-text fallback complete; move to the field-probe branch on fixed evidence.
- R11 B012 -> B013: Field probe complete; move to cross-innings binding with explicit innings.
- R9 B013 -> B014: Cross-innings branch complete; expand the baseline to remaining development roots.
- R2 B014 -> B015: Baseline below 0.90 at 0.833; drill into the failing roots with matched deletion controls.
- R12 B015 -> B016: Stratified coverage sweep takes precedence while valid units remain.
- R12 B016 -> B017: Stratified coverage sweep takes precedence while valid units remain.
- R12 B017 -> B018: Stratified coverage sweep takes precedence while valid units remain.
- R12 B019 -> B020: Stratified coverage sweep takes precedence while valid units remain.
- R12 B022 -> B023: Stratified coverage sweep takes precedence while valid units remain.
- R12 B023 -> B024: Stratified coverage sweep takes precedence while valid units remain.
- R12 B024 -> B025: Stratified coverage sweep takes precedence while valid units remain.
- R12 B025 -> B026: Stratified coverage sweep takes precedence while valid units remain.
- R12 B026 -> B027: Stratified coverage sweep takes precedence while valid units remain.
- R12 B027 -> B028: Stratified coverage sweep takes precedence while valid units remain.
- R12 B028 -> B029: Stratified coverage sweep takes precedence while valid units remain.
- R12 B029 -> B030: Stratified coverage sweep takes precedence while valid units remain.
- R12 B030 -> B031: Stratified coverage sweep takes precedence while valid units remain.
- R12 B031 -> B032: Stratified coverage sweep takes precedence while valid units remain.
- R12 B032 -> B033: Stratified coverage sweep takes precedence while valid units remain.
- R12 B033 -> B034: Stratified coverage sweep takes precedence while valid units remain.
- R12 B034 -> B035: Stratified coverage sweep takes precedence while valid units remain.
- R12 B035 -> B036: Stratified coverage sweep takes precedence while valid units remain.
- R12 B036 -> B037: Stratified coverage sweep takes precedence while valid units remain.
- R12 B037 -> B038: Stratified coverage sweep takes precedence while valid units remain.
- R12 B038 -> B039: Stratified coverage sweep takes precedence while valid units remain.
- R12 B039 -> B040: Stratified coverage sweep takes precedence while valid units remain.
- R12 B040 -> B041: Stratified coverage sweep takes precedence while valid units remain.
- R12 B041 -> B042: Stratified coverage sweep takes precedence while valid units remain.
- R12 B042 -> B043: Stratified coverage sweep takes precedence while valid units remain.
- R12 B043 -> B044: Stratified coverage sweep takes precedence while valid units remain.
- R12 B044 -> B045: Stratified coverage sweep takes precedence while valid units remain.
- R12 B045 -> B046: Stratified coverage sweep takes precedence while valid units remain.
- R12 B046 -> B047: Stratified coverage sweep takes precedence while valid units remain.
- R12 B047 -> B048: Stratified coverage sweep takes precedence while valid units remain.
- R12 B048 -> B049: Stratified coverage sweep takes precedence while valid units remain.
- R12 B049 -> B050: Stratified coverage sweep takes precedence while valid units remain.
- R12 B050 -> B051: Stratified coverage sweep takes precedence while valid units remain.
- R12 B051 -> B052: Stratified coverage sweep takes precedence while valid units remain.
- R12 B052 -> B053: Stratified coverage sweep takes precedence while valid units remain.
- R12 B053 -> B054: Stratified coverage sweep takes precedence while valid units remain.
- R12 B054 -> B055: Stratified coverage sweep takes precedence while valid units remain.
- R12 B055 -> B056: Stratified coverage sweep takes precedence while valid units remain.
- R12 B056 -> B057: Stratified coverage sweep takes precedence while valid units remain.
- R12 B057 -> B058: Stratified coverage sweep takes precedence while valid units remain.
- R12 B058 -> B059: Stratified coverage sweep takes precedence while valid units remain.
- R12 B059 -> B060: Stratified coverage sweep takes precedence while valid units remain.
- R12 B060 -> B061: Stratified coverage sweep takes precedence while valid units remain.
- R12 B061 -> B062: Stratified coverage sweep takes precedence while valid units remain.
- R12 B062 -> B063: Stratified coverage sweep takes precedence while valid units remain.
- R12 B063 -> B064: Stratified coverage sweep takes precedence while valid units remain.
- R12 B064 -> B065: Stratified coverage sweep takes precedence while valid units remain.
- R12 B065 -> B066: Stratified coverage sweep takes precedence while valid units remain.
- R12 B066 -> B067: Stratified coverage sweep takes precedence while valid units remain.
- R12 B067 -> B068: Stratified coverage sweep takes precedence while valid units remain.
- R12 B068 -> B069: Stratified coverage sweep takes precedence while valid units remain.
- R12 B069 -> B070: Stratified coverage sweep takes precedence while valid units remain.
- R12 B070 -> B071: Stratified coverage sweep takes precedence while valid units remain.
- R12 B071 -> B072: Stratified coverage sweep takes precedence while valid units remain.
- R12 B072 -> B073: Stratified coverage sweep takes precedence while valid units remain.
- R12 B073 -> B074: Stratified coverage sweep takes precedence while valid units remain.
- R12 B074 -> B075: Stratified coverage sweep takes precedence while valid units remain.
- R12 B075 -> B076: Stratified coverage sweep takes precedence while valid units remain.
- R12 B076 -> B077: Stratified coverage sweep takes precedence while valid units remain.
- R12 B077 -> B078: Stratified coverage sweep takes precedence while valid units remain.
- R12 B078 -> B079: Stratified coverage sweep takes precedence while valid units remain.
- R12 B079 -> B080: Stratified coverage sweep takes precedence while valid units remain.
- R12 B080 -> B081: Stratified coverage sweep takes precedence while valid units remain.
- R12 B081 -> B082: Stratified coverage sweep takes precedence while valid units remain.
- R12 B082 -> B083: Stratified coverage sweep takes precedence while valid units remain.
- R12 B083 -> B084: Stratified coverage sweep takes precedence while valid units remain.
- R12 B084 -> B085: Stratified coverage sweep takes precedence while valid units remain.
- R12 B085 -> B086: Stratified coverage sweep takes precedence while valid units remain.
- R12 B086 -> B087: Stratified coverage sweep takes precedence while valid units remain.
- R12 B087 -> B088: Stratified coverage sweep takes precedence while valid units remain.
- R12 B088 -> B089: Stratified coverage sweep takes precedence while valid units remain.
- R12 B089 -> B090: Stratified coverage sweep takes precedence while valid units remain.
- R12 B090 -> B091: Stratified coverage sweep takes precedence while valid units remain.
- R12 B091 -> B092: Stratified coverage sweep takes precedence while valid units remain.
- R12 B092 -> B093: Stratified coverage sweep takes precedence while valid units remain.
- R12 B093 -> B094: Stratified coverage sweep takes precedence while valid units remain.
- R12 B094 -> B095: Stratified coverage sweep takes precedence while valid units remain.
- R12 B095 -> B096: Stratified coverage sweep takes precedence while valid units remain.
- R12 B096 -> B097: Stratified coverage sweep takes precedence while valid units remain.
- R12 B097 -> B098: Stratified coverage sweep takes precedence while valid units remain.
- R12 B098 -> B099: Stratified coverage sweep takes precedence while valid units remain.
- R12 B099 -> B100: Stratified coverage sweep takes precedence while valid units remain.
- R12 B100 -> B101: Stratified coverage sweep takes precedence while valid units remain.
- R12 B101 -> B102: Stratified coverage sweep takes precedence while valid units remain.
- R12 B102 -> B103: Stratified coverage sweep takes precedence while valid units remain.
- R12 B103 -> B104: Stratified coverage sweep takes precedence while valid units remain.
- R12 B104 -> B105: Stratified coverage sweep takes precedence while valid units remain.
- R12 B105 -> B106: Stratified coverage sweep takes precedence while valid units remain.
- R12F B106 -> B107: Stratified coverage sweep takes precedence while valid units remain. | fallback: S_coverage_sweep produced no eligible task; executed P_field_sweep.
- R13 B107 -> B108: Condition sweep exhausted; field-probe coverage takes over.
- R13 B108 -> B109: Condition sweep exhausted; field-probe coverage takes over.
- R13 B109 -> B110: Condition sweep exhausted; field-probe coverage takes over.
- R13 B110 -> B111: Condition sweep exhausted; field-probe coverage takes over.
- R13 B111 -> B112: Condition sweep exhausted; field-probe coverage takes over.
- R13 B112 -> B113: Condition sweep exhausted; field-probe coverage takes over.
- R13 B113 -> B114: Condition sweep exhausted; field-probe coverage takes over.
- R13 B114 -> B115: Condition sweep exhausted; field-probe coverage takes over.
- R13 B115 -> B116: Condition sweep exhausted; field-probe coverage takes over.
- R13 B116 -> B117: Condition sweep exhausted; field-probe coverage takes over.
- R13 B117 -> B118: Condition sweep exhausted; field-probe coverage takes over.
- R13 B118 -> B119: Condition sweep exhausted; field-probe coverage takes over.
- R13 B119 -> B120: Condition sweep exhausted; field-probe coverage takes over.
- R13 B120 -> B121: Condition sweep exhausted; field-probe coverage takes over.
- R13 B121 -> B122: Condition sweep exhausted; field-probe coverage takes over.
- R13 B122 -> B123: Condition sweep exhausted; field-probe coverage takes over.
- R13 B123 -> B124: Condition sweep exhausted; field-probe coverage takes over.
- R13 B124 -> B125: Condition sweep exhausted; field-probe coverage takes over.
- R13 B125 -> B126: Condition sweep exhausted; field-probe coverage takes over.
- R13 B126 -> B127: Condition sweep exhausted; field-probe coverage takes over.
- R13 B127 -> B128: Condition sweep exhausted; field-probe coverage takes over.
- R13 B128 -> B129: Condition sweep exhausted; field-probe coverage takes over.
- R13 B129 -> B130: Condition sweep exhausted; field-probe coverage takes over.
- R13 B130 -> B131: Condition sweep exhausted; field-probe coverage takes over.
- R13 B131 -> B132: Condition sweep exhausted; field-probe coverage takes over.
- R13 B132 -> B133: Condition sweep exhausted; field-probe coverage takes over.
- R13 B133 -> B134: Condition sweep exhausted; field-probe coverage takes over.
- R13 B134 -> B135: Condition sweep exhausted; field-probe coverage takes over.
- R13 B135 -> B136: Condition sweep exhausted; field-probe coverage takes over.
- R13 B136 -> B137: Condition sweep exhausted; field-probe coverage takes over.
- R13 B137 -> B138: Condition sweep exhausted; field-probe coverage takes over.
- R13 B138 -> B139: Condition sweep exhausted; field-probe coverage takes over.
- R13 B139 -> B140: Condition sweep exhausted; field-probe coverage takes over.
- R13 B140 -> B141: Condition sweep exhausted; field-probe coverage takes over.
- R13 B141 -> B142: Condition sweep exhausted; field-probe coverage takes over.
- R13 B142 -> B143: Condition sweep exhausted; field-probe coverage takes over.
- R13 B143 -> B144: Condition sweep exhausted; field-probe coverage takes over.
- R13 B144 -> B145: Condition sweep exhausted; field-probe coverage takes over.
- R13 B145 -> B146: Condition sweep exhausted; field-probe coverage takes over.
- R13 B146 -> B147: Condition sweep exhausted; field-probe coverage takes over.
- R13 B147 -> B148: Condition sweep exhausted; field-probe coverage takes over.
- R13 B148 -> B149: Condition sweep exhausted; field-probe coverage takes over.
- R13 B149 -> B150: Condition sweep exhausted; field-probe coverage takes over.
- R13 B151 -> B152: Condition sweep exhausted; field-probe coverage takes over.
- R13 B152 -> B153: Condition sweep exhausted; field-probe coverage takes over.
- R13 B153 -> B154: Condition sweep exhausted; field-probe coverage takes over.
- R13 B154 -> B155: Condition sweep exhausted; field-probe coverage takes over.
- R13 B155 -> B156: Condition sweep exhausted; field-probe coverage takes over.
- R13 B156 -> B157: Condition sweep exhausted; field-probe coverage takes over.
- R13 B157 -> B158: Condition sweep exhausted; field-probe coverage takes over.
- R13 B158 -> B159: Condition sweep exhausted; field-probe coverage takes over.
- R13 B159 -> B160: Condition sweep exhausted; field-probe coverage takes over.
- R13 B160 -> B161: Condition sweep exhausted; field-probe coverage takes over.
- R13 B161 -> B162: Condition sweep exhausted; field-probe coverage takes over.
- R13 B162 -> B163: Condition sweep exhausted; field-probe coverage takes over.
- R13 B163 -> B164: Condition sweep exhausted; field-probe coverage takes over.
- R13 B164 -> B165: Condition sweep exhausted; field-probe coverage takes over.
- R13 B165 -> B166: Condition sweep exhausted; field-probe coverage takes over.
- R13 B166 -> B167: Condition sweep exhausted; field-probe coverage takes over.
- R13 B167 -> B168: Condition sweep exhausted; field-probe coverage takes over.
- R13 B168 -> B169: Condition sweep exhausted; field-probe coverage takes over.
- R13 B169 -> B170: Condition sweep exhausted; field-probe coverage takes over.
- R13 B170 -> B171: Condition sweep exhausted; field-probe coverage takes over.
- R13 B171 -> B172: Condition sweep exhausted; field-probe coverage takes over.
- R13 B172 -> B173: Condition sweep exhausted; field-probe coverage takes over.
- R13 B173 -> B174: Condition sweep exhausted; field-probe coverage takes over.
- R13 B174 -> B175: Condition sweep exhausted; field-probe coverage takes over.
- R13 B175 -> B176: Condition sweep exhausted; field-probe coverage takes over.
- R13 B176 -> B177: Condition sweep exhausted; field-probe coverage takes over.
- R13 B177 -> B178: Condition sweep exhausted; field-probe coverage takes over.
- R13 B178 -> B179: Condition sweep exhausted; field-probe coverage takes over.
- R13 B179 -> B180: Condition sweep exhausted; field-probe coverage takes over.
- R13 B180 -> B181: Condition sweep exhausted; field-probe coverage takes over.
- R13 B181 -> B182: Condition sweep exhausted; field-probe coverage takes over.
- R13 B182 -> B183: Condition sweep exhausted; field-probe coverage takes over.
- R13 B183 -> B184: Condition sweep exhausted; field-probe coverage takes over.
- R13 B184 -> B185: Condition sweep exhausted; field-probe coverage takes over.
- R13 B185 -> B186: Condition sweep exhausted; field-probe coverage takes over.
- R13 B186 -> B187: Condition sweep exhausted; field-probe coverage takes over.
- R13 B187 -> B188: Condition sweep exhausted; field-probe coverage takes over.
- R13 B188 -> B189: Condition sweep exhausted; field-probe coverage takes over.
- R13 B189 -> B190: Condition sweep exhausted; field-probe coverage takes over.
- R13 B190 -> B191: Condition sweep exhausted; field-probe coverage takes over.
- R13 B191 -> B192: Condition sweep exhausted; field-probe coverage takes over.
- R13 B192 -> B193: Condition sweep exhausted; field-probe coverage takes over.
- R13 B193 -> B194: Condition sweep exhausted; field-probe coverage takes over.
- R13 B194 -> B195: Condition sweep exhausted; field-probe coverage takes over.
- R13 B195 -> B196: Condition sweep exhausted; field-probe coverage takes over.
- R13 B196 -> B197: Condition sweep exhausted; field-probe coverage takes over.

## Note

- Inference continues; this report is a snapshot, not a stop condition.


---

## 附录 A38：小时报告（11-21 09:44）

> 原文件：VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117/reports/HOURLY_20261121_094456.md（228 行）

# VETT hourly report 20261121_094456

- run elapsed: 1.0 h (3602.7 s)
- queue: {"claimed": 1, "done": 6591, "failed": 8, "queued": 1383}
- results: 6591; attempts: 7627; uncertain: 18
- load ms: 44044399.2; inference ms: 22852838.9; scoring ms: 3423.3
- planning ms: 22382.3; waiting ms est: 0.0
- exceptions: 2

## Workflow

- state: running
- worker pid: 2724
- supervisor pid: 13076

## Batches

- B001 T1_baseline_o scored 1.0
- B002 T2_hard_excerpt scored 0.8333
- B003 T3_matched_deletion scored 0.1667
- B004 T4_full_table scored 0.1938
- B005 T2_hard_excerpt scored 0.8333
- B006 T3_matched_deletion scored 0.0
- B007 T5_hard_fulltext scored 0.0
- B008 T1_baseline_o scored 0.9167
- B009 T5_hard_fulltext scored 0.0
- B010 T1_baseline_o scored 1.0
- B011 T5_hard_fulltext scored 0.0
- B012 A_field_probe scored 0.9167
- B013 B_cross_innings scored 0.0
- B014 T1_baseline_o scored 0.8333
- B015 T3_matched_deletion scored 0.2222
- B016 S_coverage_sweep scored 0.8125
- B017 S_coverage_sweep scored 0.7667
- B018 S_coverage_sweep scored 0.85
- B019 C_adjudication scored 0.9778
- B020 S_coverage_sweep scored 0.7708
- B021 B2_matched_control scored 0.0
- B022 C_adjudication scored 0.9222
- B023 S_coverage_sweep scored 0.8167
- B024 S_coverage_sweep scored 0.8667
- B025 S_coverage_sweep scored 0.6458
- B026 S_coverage_sweep scored 0.6389
- B027 S_coverage_sweep scored 0.619
- B028 S_coverage_sweep scored 0.5
- B029 S_coverage_sweep scored 0.5
- B030 S_coverage_sweep scored 0.4583
- B031 S_coverage_sweep scored 0.5
- B032 S_coverage_sweep scored 0.5
- B033 S_coverage_sweep scored 0.5
- B034 S_coverage_sweep scored 0.5417
- B035 S_coverage_sweep scored 0.5
- B036 S_coverage_sweep scored 0.5
- B037 S_coverage_sweep scored 0.4583
- B038 S_coverage_sweep scored 0.75
- B039 S_coverage_sweep scored 0.5714
- B040 S_coverage_sweep scored 0.641
- B041 S_coverage_sweep scored 0.5833
- B042 S_coverage_sweep scored 0.6667
- B043 S_coverage_sweep scored 0.6333
- B044 S_coverage_sweep scored 0.5417
- B045 S_coverage_sweep scored 0.5
- B046 S_coverage_sweep scored 0.625
- B047 S_coverage_sweep scored 0.4167
- B048 S_coverage_sweep scored 0.5833
- B049 S_coverage_sweep scored 0.7222
- B050 S_coverage_sweep scored 0.5
- B051 S_coverage_sweep scored 0.5
- B052 S_coverage_sweep scored 0.5
- B053 S_coverage_sweep scored 0.5667
- B054 S_coverage_sweep scored 0.5333
- B055 S_coverage_sweep scored 0.5
- B056 S_coverage_sweep scored 0.4583
- B057 S_coverage_sweep scored 0.5
- B058 S_coverage_sweep scored 0.4583
- B059 S_coverage_sweep scored 0.6786
- B060 S_coverage_sweep scored 0.6111
- B061 S_coverage_sweep scored 0.375
- B062 S_coverage_sweep scored 0.375
- B063 S_coverage_sweep scored 0.5
- B064 S_coverage_sweep scored 0.625
- B065 S_coverage_sweep scored 0.5
- B066 S_coverage_sweep scored 0.6667
- B067 S_coverage_sweep scored 0.381
- B068 S_coverage_sweep scored 0.6
- B069 S_coverage_sweep scored 0.4167
- B070 S_coverage_sweep scored 0.25
- B071 S_coverage_sweep scored 0.4167
- B072 S_coverage_sweep scored 0.5
- B073 S_coverage_sweep scored 0.5
- B074 S_coverage_sweep scored 0.5
- B075 S_coverage_sweep scored 0.5
- B076 S_coverage_sweep scored 0.5
- B077 S_coverage_sweep scored 0.5417
- B078 S_coverage_sweep scored 0.625
- B079 S_coverage_sweep scored 0.6667
- B080 S_coverage_sweep scored 0.7222
- B081 S_coverage_sweep scored 0.6389
- B082 S_coverage_sweep scored 0.7083
- B083 S_coverage_sweep scored 0.6282
- B084 S_coverage_sweep scored 0.6146
- B085 S_coverage_sweep scored 0.6667
- B086 S_coverage_sweep scored 0.5972
- B087 S_coverage_sweep scored 0.6167
- B088 S_coverage_sweep scored 0.2083
- B089 S_coverage_sweep scored 0.4167
- B090 S_coverage_sweep scored 0.4583
- B091 S_coverage_sweep scored 0.4167
- B092 S_coverage_sweep scored 0.4583
- B093 S_coverage_sweep scored 0.5417
- B094 S_coverage_sweep scored 0.5
- B095 S_coverage_sweep scored 0.4167
- B096 S_coverage_sweep scored 0.4583
- B097 S_coverage_sweep scored 0.5417
- B098 S_coverage_sweep scored 0.375
- B099 S_coverage_sweep scored 0.5208
- B100 S_coverage_sweep scored 0.6667
- B101 S_coverage_sweep scored 0.625
- B102 S_coverage_sweep scored 0.5
- B103 S_coverage_sweep scored 0.5833
- B104 S_coverage_sweep scored 0.7273
- B105 S_coverage_sweep scored 0.4167
- B106 S_coverage_sweep scored 0.5
- B107 P_field_sweep scored 0.4583
- B108 P_field_sweep scored 0.5
- B109 P_field_sweep scored 0.5208
- B110 P_field_sweep scored 0.4583
- B111 P_field_sweep scored 0.5
- B112 P_field_sweep scored 0.4583
- B113 P_field_sweep scored 0.5
- B114 P_field_sweep scored 0.4583
- B115 P_field_sweep scored 0.4792
- B116 P_field_sweep scored 0.4375
- B117 P_field_sweep scored 0.4792
- B118 P_field_sweep scored 0.5
- B119 P_field_sweep scored 0.4583
- B120 P_field_sweep scored 0.4792
- B121 P_field_sweep scored 0.4583
- B122 P_field_sweep scored 0.5
- B123 P_field_sweep scored 0.5417
- B124 P_field_sweep scored 0.5
- B125 P_field_sweep scored 0.5
- B126 P_field_sweep scored 0.4583
- B127 P_field_sweep scored 0.625
- B128 P_field_sweep scored 0.5
- B129 P_field_sweep scored 0.6042
- B130 P_field_sweep scored 0.5625
- B131 P_field_sweep scored 0.5
- B132 P_field_sweep scored 0.5417
- B133 P_field_sweep scored 0.5417
- B134 P_field_sweep scored 0.4583
- B135 P_field_sweep scored 0.5833
- B136 P_field_sweep scored 0.4375
- B137 P_field_sweep scored 0.5208
- B138 P_field_sweep scored 0.6042
- B139 P_field_sweep scored 0.7292
- B140 P_field_sweep scored 0.5
- B141 P_field_sweep scored 0.4792
- B142 P_field_sweep scored 0.3958
- B143 P_field_sweep scored 0.5208
- B144 P_field_sweep scored 0.3958
- B145 P_field_sweep scored 0.5208
- B146 P_field_sweep scored 0.5
- B147 P_field_sweep scored 0.4583
- B148 P_field_sweep scored 0.5
- B149 P_field_sweep scored 0.4792
- B150 P_field_sweep scored 0.375
- B151 ACC_llama_p320 scored 0.6667
- B152 P_field_sweep scored 0.3125
- B153 P_field_sweep scored 0.5417
- B154 P_field_sweep scored 0.5
- B155 P_field_sweep scored 0.5417
- B156 P_field_sweep scored 0.5
- B157 P_field_sweep scored 0.4167
- B158 P_field_sweep scored 0.5208
- B159 P_field_sweep scored 0.25
- B160 P_field_sweep scored 0.2917
- B161 P_field_sweep scored 0.4583
- B162 P_field_sweep scored 0.4792
- B163 P_field_sweep scored 0.5208
- B164 P_field_sweep scored 0.5417
- B165 P_field_sweep scored 0.5435
- B166 P_field_sweep scored 0.4792
- B167 P_field_sweep scored 0.3958
- B168 P_field_sweep scored 0.6667
- B169 P_field_sweep scored 0.4792
- B170 P_field_sweep scored 0.4375
- B171 P_field_sweep scored 0.5833
- B172 P_field_sweep scored 0.5833
- B173 P_field_sweep scored 0.375
- B174 P_field_sweep scored 0.5
- B175 P_field_sweep scored 0.5
- B176 P_field_sweep scored 0.5417
- B177 P_field_sweep scored 0.4792
- B178 P_field_sweep scored 0.4167
- B179 P_field_sweep scored 0.3958
- B180 P_field_sweep scored 0.3958
- B181 P_field_sweep scored 0.5
- B182 P_field_sweep scored 0.4583
- B183 P_field_sweep scored 0.4375
- B184 P_field_sweep scored 0.5625
- B185 P_field_sweep scored 0.4167
- B186 P_field_sweep scored 0.4375
- B187 P_field_sweep scored 0.375
- B188 P_field_sweep scored 0.5
- B189 P_field_sweep scored 0.3125
- B190 P_field_sweep scored 0.4792
- B191 P_field_sweep scored 0.5833
- B192 P_field_sweep scored 0.4583
- B193 P_field_sweep scored 0.4583
- B194 P_field_sweep scored 0.4583
- B195 P_field_sweep scored 0.4167
- B196 P_field_sweep scored 0.3958
- B197 P_field_sweep scored 0.3333
- B198 T4_full_table_scale scored 0.2677
- B199 T4_full_table_scale2 scored 0.2358
- B200 T4_full_table_O_scale scored 0.1299
- B201 T4_full_table_O_scale failed None
- B202 T4_full_table_O_scale failed None
- B203 T4_full_table_O_scale failed None
- B204 T4_full_table_E_scale failed None
- B205 T4_full_table_E_scale failed None
- B206 T4_full_table_OI_scale failed None
- B207 T4_full_table_E_used scored 0.1081
- B208 T4_full_table_OI_used running None
- B209 B_cross_innings_scale running None
- B210 P_E_probe running None
- B211 P_OI_probe running None
