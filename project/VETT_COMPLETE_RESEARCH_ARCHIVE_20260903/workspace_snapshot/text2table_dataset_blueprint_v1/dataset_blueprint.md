# VETT-Bench：可验证证据解析型 Text-to-Table 数据集构造蓝图 v1.0

> 暂定名：VETT-Bench（Versioned Evidence Text-to-Table Benchmark）  
> 目标：建立一个覆盖抽取、聚合、schema归纳、多源证据裁决、非单调修订和长程状态推理的Text-to-Table基准，而不是为某几个方法定制失败样本。

## 1. 最终判断

这项工作有形成顶会/顶刊数据集论文的潜力，但必须改变当前“让T³、Map&Make和CoT错误率超过60%”的单一目标。该目标只适合早期压力测试，不适合作为正式数据集的采样标准。正式benchmark应回答：

1. 模型在什么能力上失败；
2. 难度由哪些可控结构因素产生；
3. 输出是否唯一、可验证并逐cell有证据；
4. 模型进步后，benchmark是否仍能区分能力；
5. 结果能否推广到不同domain、style、schema和operator组合。

现有LiveSum重点测试从赛事直播文本进行事件识别和数值聚合；T³使用Text→Tuple→Table流水线改进信息整合。[T³/LiveSum](https://aclanthology.org/2024.emnlp-main.523/) Map&Make进一步通过原子命题、schema归纳和逐statement更新生成表格，并在Rotowire、LiveSum和Wiki40B上测试。[Map&Make](https://aclanthology.org/2025.acl-long.1460/) VETT-Bench应与它们形成互补：把研究瓶颈推进到“多个mention如何被裁决为最终、可追溯的事件状态”。

## 2. 建议的核心论文主张

论文不要主张“现有方法都不行”，而应主张：

> Text-to-Table不只是从文本事实到表格cell的映射。真实输入中，mention可能重复、冲突、过期、越界或相互修订；表格是经过证据裁决后的潜在事件图的投影。现有benchmark对这一层覆盖不足。

数据集的实质贡献应包括：

1. 一个统一的versioned evidence event graph标注层；
2. 多domain、多style、可组合operator的数据生成与人工自然化流程；
3. fixed-schema、latent-schema和evidence-audit三个任务track；
4. 每个gold cell的证据与推导路径；
5. 基于结构轴、人工表现和IRT共同标定的难度；
6. 面向组合泛化、反事实敏感性和非单调状态解析的评价协议；
7. 可重复生成新private test的动态benchmark机制。

## 3. 形式化任务定义

一个样本定义为：

\[
\mathcal{I}=(D,q,G,T,P,R)
\]

其中：

- \(D\)：一个或多个文本document/stream；
- \(q\)：输出任务和scope说明；
- \(G\)：隐藏的versioned evidence event graph；
- \(T\)：一组gold tables；
- \(P\)：cell-level provenance与推导式；
- \(R\)：private operator recipe和生成元数据。

隐藏事件图：

\[
G=(E,M,L,C,S)
\]

- \(E\)：canonical events；
- \(M\)：文本mentions；
- \(L\)：`same-event`、`duplicate-of`、`revises`、`contradicts`、`out-of-scope`等边；
- \(C\)：数值、顺序、source和跨表一致性约束；
- \(S\)：source状态及必要的状态转移。

最终表格是事件图的确定性投影：

\[
T=\Pi(G)
\]

主测试集必须满足唯一可解：

\[
\left|\{G':G'\models D,q,C,S\}\right|=1
\]

不唯一的输入不能悄悄给一个任意gold。它们要么被修复/删除，要么进入单独的“ambiguity and abstention”研究track。

## 4. 三个任务track

### Track A：Fixed-schema evidence aggregation

输入给定目标schema，重点测：

- mention抽取；
-scope；
-重复与event identity；
-版本裁决；
-顺序恢复；
-数值聚合；
-跨表一致性。

这是与LiveSum和T³最可比的主track。

### Track B：Latent-schema multi-table generation

不给完整schema，模型需要推断：

-需要几张表；
-row/column定义；
-实体层级；
-定量与定性字段；
-不同表的关联键。

该track与Map&Make和Struc-Bench关注的schema/format能力互补。Struc-Bench已经指出结构化输出应从coverage、formatting、reasoning、comprehension、pragmatics和hallucination等维度分析，因此本数据集不能只报告一个字符串相似度。[Struc-Bench](https://aclanthology.org/2024.naacl-short.2/)

### Track C：Evidence-audit table

除了最终业务表，还要求输出：

-被接受的claim；
-被拒绝claim及原因；
-event/version链接；
-每个cell对应的event和mention；
-必要时给出置信度或abstention。

这能区分“碰巧算对总数”和“真正恢复了事件状态”。

## 5. Domain和style设计

首版只选择能建立可靠确定性world model、许可清晰、可由专家复核的domain：

| Domain | 可验证的潜在状态 | 典型输出 |
| --- | --- | --- |
| Sports competition | 事件流、比分、球员状态 | summary、player、team、FOW/partnership |
| Logistics operations | 订单、库存、运输和修订状态 | inventory、shipment、exception、SLA |
| Public finance | 公告、restatement、期间和单位 | period summary、line items、restatement audit |

暂不把临床文本作为首版主domain。它需要额外伦理、隐私和专业验证，容易使数据集论文被高风险问题分散。

每个潜在事件图至少支持四种surface style：

1. live commentary；
2. narrative report；
3. threaded messages/email；
4. mixed bulletins/logs。

同一个graph可以生成多个style，但所有paraphrase siblings必须进入同一split，绝不能一份在train、另一份在test。

## 6. Operator能力矩阵

operator不是固定模板，而是对event graph或mention graph的可验证变换。完整定义见`operator_catalog.json`。

| 能力 | 关键operator | 主要失败模式 |
| --- | --- | --- |
| Linguistic variation | paraphrase、entity alias | 表面匹配失败 |
| Event identity | duplicate、merge/split | 重复计数或漏计 |
| Scope | same-entity shadow stream | 干扰事实进入表格 |
| Versioning | revision、withdrawal、stale reappearance | first/last update错误 |
| Ordering | shuffled arrival、delayed report | FOW/partnership错位 |
| Provenance | conditional source reliability | 固定来源或多数投票失败 |
| Global consistency | overlapping constraints | 局部合理但全表不一致 |
| Normalization | unit conversion | 数值和单位错误 |
| Schema | latent/multi-table schema | 漏行、漏列、错表 |
| Long-horizon state | recursive transition | 一步错误持续传播 |
| Causal sensitivity | counterfactual pair | 忽略关键证据变化 |

operator必须具有：

-明确输入前提；
-对隐藏图和文本的变换定义；
-预期影响的gold cells；
-可逆或可检查的validation；
-与其他operator的prerequisite和conflict；
-至少两种独立render families。

## 7. 难度不能只用Easy/Medium/Hard

每个样本记录八个结构轴，范围为0–1：

1. length；
2. scope；
3. versioning；
4. ordering；
5. constraint topology；
6. schema entropy；
7. linguistic variation；
8. arithmetic。

结构轴只说明“为什么可能困难”，最终难度要由三部分共同标定：

\[
d_i=\alpha d_i^{struct}+\beta d_i^{human}+\gamma d_i^{IRT}
\]

-结构生成参数；
-人工正确率和耗时；
-基于多模型、多人的item response theory难度参数。

建议五级：

| Tier | 构造原则 | 目的 |
| --- | --- | --- |
| 0 Sanity | clean、单source、短输入 | 检查格式与基本抽取 |
| 1 Local | 一个局部operator | 单能力诊断 |
| 2 Interaction | 两到三个已知operator | 常见组合 |
| 3 Global | 全局约束、版本链或latent schema | 非局部推理 |
| 4 Compositional | 未见组合、递归状态、跨domain迁移 | 组合泛化 |

Tier 4不是简单“更多噪声”。它必须包含训练中见过的基础operator，但测试它们的新组合。这一设计借鉴组合泛化benchmark通过系统性train–test gaps测试结构泛化的思想。[COGS](https://aclanthology.org/2020.emnlp-main.731/)

## 8. 完整生成流水线

### Step 1：生成或导入latent world

- 从确定性的domain simulator生成canonical events；
- 或从有许可的真实结构化记录导入；
- 分配稳定entity IDs、event IDs、scope和时间；
- 先投影得到无噪声gold tables。

禁止先写复杂文本、再由LLM猜gold。gold必须来自latent world。

### Step 2：应用evidence operators

- 将canonical event渲染成一个或多个mentions；
-加入duplicate、revision、scope shadow、source冲突等；
-记录所有mention→event和version关系；
-应用operator后重新运行唯一性检查。

### Step 3：生成factual skeleton

先生成不追求自然性的受控事实骨架，确保：

-所有需要的证据出现；
-所有干扰事实有明确隐藏scope；
-没有额外事实；
-指代链和时间线可解析；
-每个cell都有derivation。

### Step 4：多通道surface rendering

每个样本随机选择render route：

1. domain模板；
2.不同LLM family的受约束paraphrase；
3.人类从事实骨架重写；
4.真实文本style guide下的编辑。

LLM只能改变表达，不能直接决定gold或operator recipe。

### Step 5：blind human naturalization

重写者看到事实约束和style目标，但看不到：

-目标方法名称；
-baseline结果；
-difficulty标签；
-需要“骗过”哪个模型；
-测试集gold table。

这样可减少针对某一方法的人为痕迹。

### Step 6：双重验证

1. symbolic oracle从隐藏图投影table；
2.独立validator从标注mention graph重建并投影；
3.两者必须byte-level一致；
4.求解器必须返回唯一解；
5.每个cell的provenance coverage必须100%。

### Step 7：模型和人工pilot

-运行多类baseline；
-由至少三名annotator独立完成子集；
-只用于标定难度和发现坏样本；
-不得只保留“让当前模型失败”的样本。

### Step 8：冻结与发布

-公开train/dev和public test；
-private test保留文本或至少保留gold；
-版本化generator、operator catalog和schema；
-每年或每个major model generation刷新private challenge。

## 9. 如何降低“人工构造痕迹”

目标不是隐瞒合成来源，而是让surface form不泄露答案和operator。

### 必做的artifact audits

1. **Operator classifier**  
   用bag-of-words、小型Transformer和长度特征预测operator/difficulty。控制domain和长度后，macro-F1不得明显高于随机基线。

2. **Synthetic-vs-natural discriminator**  
   在humanized子集上训练判别器。建议AUC目标不高于0.65；若过高，说明语言仍有明显生成器指纹。

3. **Answer-position leakage**  
   检测claim位置、source名称、段落顺序是否能预测gold。每个source、claim position和surface label的正确率必须平衡。

4. **Template overlap**  
   用MinHash、n-gram、embedding clustering检查train/test。graph siblings、render siblings和高相似模板不得跨split。

5. **Counterfactual/invariance pairs**  
   - counterfactual：一个关键证据变化，应改变已知cell集合；
   - invariance：只换表达，应保持table不变。

6. **Generator detection red-team**  
   让未参与构造的annotator猜哪些句子属于revision、distractor或高难度。如果仅凭固定短语即可猜出，样本退回重写。

不能在输入中统一使用“Final ruling”“stale replay”“different match”等标签。真实style中可以偶尔自然出现，但其位置、措辞和可靠性必须随机化和平衡。

## 10. 标注与质量门槛

每个实例应包含：

-documents；
-canonical events；
-mentions；
-mention→event edges；
-version/revision edges；
-scope labels；
-source metadata；
-constraints；
-gold tables；
-cell provenance；
-operator recipe（private）；
-validation certificate。

建议acceptance gates：

| 检查 | 最低标准 |
| --- | ---: |
| Oracle solutions | 恰好1个 |
| Oracle vs gold | 100%一致 |
| Cell provenance | 100%覆盖 |
| Mention factual fidelity | ≥99.5% |
| Unsupported gold cells | 0 |
| Human naturalness | 平均≥4/5，无低于3 |
| Expert cell accuracy | Tier 0–3 ≥95% |
| Expert cell accuracy | Tier 4 ≥90%（允许工具） |
| Synthetic discriminator AUC | humanized subset ≤0.65 |
| Operator surface classifier | 随机基线+10个百分点以内 |

Map&Make论文报告其在Rotowire测试集中发现文本和ground truth不一致，并逐样本人工验证row、column和cell归因。这说明cell provenance和人工验证不是附加项，而是数据集可信度的核心。[Map&Make fidelity analysis](https://aclanthology.org/2025.acl-long.1460.pdf)

## 11. Split设计

随机按实例切分是不够的。必须同时隔离：

-graph family；
-entity/name pools；
-render family；
-paraphrase siblings；
-source lexicons；
-operator compositions；
-真实事件或原始document；
-generator seed family。

建议发布：

1. **IID test**：同operator组合、不同graph；
2. **Style-OOD**：新render family；
3. **Domain-OOD**：新domain或新schema；
4. **Composition-OOD**：基础operator见过，但组合没见过；
5. **Private refresh test**：论文提交后生成，降低contamination。

COGS表明，普通IID高分并不意味着系统能处理未见结构组合；因此主结果必须把IID与composition-OOD分开报告。[COGS](https://aclanthology.org/2020.emnlp-main.731/)

## 12. 推荐规模

### Phase A：严格pilot

- 3 domains × 4 styles × 5 tiers × 20 = 1,200实例；
-每个operator至少100次；
-20%进行双人重写；
-100%自动验证；
-30%双人事实复核；
-10%专家adjudication。

### Phase B：论文版

建议总量6,000–10,000，而不是一开始追求十万：

-train：3,000–5,000；
-dev：600–1,000；
-public test：900–1,500；
-private compositional test：900–1,500；
-humanized natural holdout：600–1,000。

样本数量要服务于operator/domain/style分层置信区间。若预算不足，宁可减少domain，也不要降低gold质量。

## 13. 评价指标

### 13.1 固定schema主指标

-Cell Exact Match；
-Macro Cell F1；
-Numeric Error / RMSE；
-Table Exact Match；
-Valid structured output rate；
-Worst-group cell accuracy。

### 13.2 Schema指标

-row/column precision、recall、F1；
-table count accuracy；
-entity-key alignment；
-missing/extra rows and columns。

### 13.3 Event/evidence指标

-mention extraction F1；
-event coreference/link F1；
-scope F1；
-revision edge F1；
-accepted-claim accuracy；
-canonical order Kendall \(\tau\)；
-constraint violation rate；
-cell provenance F1。

### 13.4 Robustness指标

-counterfactual consistency；
-invariance consistency；
-selective risk/coverage；
-operator-wise error；
-operator-composition interaction；
-domain/style OOD gap。

开放schema可以使用语义对齐作为辅助指标，但主数值cell和evidence指标必须是确定性计算，不能把LLM judge作为唯一评价。

报告bootstrap 95% confidence intervals，并以实例为重采样单位。多seed模型输出应报告均值、方差和最差值。

## 14. Baseline矩阵

所有prompting方法尽可能使用相同backbone、上下文预算、temperature和输出schema。

### 直接与推理baseline

-Direct zero-shot；
-paper-style CoT；
-few-shot CoT；
-self-consistency；
-Program-of-Thought/code execution；
-tool-using agent。

### Text-to-Table baseline

-T³ official prompt/pipeline；
-T³ with provenance-enhanced tuples；
-Map&Make unified；
-Map&Make 3-step；
-Map&Make with versioned event state；
-schema-only和oracle-schema。

### Diagnostic oracle

-oracle scope；
-oracle mention→event links；
-oracle ordering；
-oracle version edges；
-oracle schema；
-complete event graph oracle。

oracle ablation能够回答性能瓶颈在哪一层，而不只是给一个总分。

## 15. 防止benchmark变成“定向攻击”

正式数据集组成建议：

-50% capability-balanced常规样本；
-30% operator-compositional样本；
-20% model-in-the-loop challenge样本。

model-in-the-loop部分可参考Dynabench，让人针对多个不同架构发现失败，但必须由另一组人验证可解性和自然性。[Dynabench](https://aclanthology.org/2021.naacl-main.324/) 同时保留从未用于筛选当前baseline的blind holdout，防止数据集只反映被攻击模型的特定弱点。

不要删除所有模型都能答对的样本。CheckList强调把能力和测试类型系统化，而不是只用单一accuracy描述系统；本数据集也应保留sanity、invariance和minimum-functionality tests。[CheckList](https://aclanthology.org/2020.acl-main.442/)

## 16. 当前三代pilot的可行性证据

| Pilot | 主要结构 | T³ | Map&Make | CoT | Oracle |
| --- | --- | ---: | ---: | ---: | ---: |
| v0.3 | clean order + global reconciliation | 0.00% | 34.86% | 未测 | 0.00% |
| v0.4 | explicit versioned events | 86.24% | 76.15% | 0.00% | 0.00% |
| v0.5 | shuffled conflict + recursive state | 97.73% | 64.99% | 64.99% | 0.00% |

这个梯度很有价值：

-v0.3说明T³并非被数据集无条件压制；
-v0.4区分“保留全文状态的CoT”和丢失版本信息的表示；
-v0.5测试长程证据状态和跨表传播；
-所有oracle均为0%错误，说明样本可解。

这比只展示“三个方法都错”更有论文说服力，因为数据集能形成可解释的能力剖面。

当前自测仍只是process diagnostics，不是作者代码/API复现。它证明构造框架可行，不证明正式模型的最终排名。

## 17. 已执行的蓝图自测

当前附件实现了：

-15个operator及其依赖关系；
-JSON instance schema；
-3 domains × 4 styles × 5 tiers × 每格4个配方；
-共240个recipe manifests；
-16项自动检查。

自测检查：

-domain/style/tier覆盖；
-60个设计单元格完全平衡；
-operator prerequisites；
-operator conflicts；
-全部operator被覆盖；
-难度轴均值随tier增加；
-operator标签不进入public input；
-三个pilot oracle均为0；
-包含非对抗校准样本；
-v0.4具有方法区分性；
-v0.5三个代理和核心109字段均超过60%错误。

执行结果：**16/16 PASS**。

这证明schema、operator系统和难度网格在工程上可执行；还没有证明人类自然化、跨domain renderer和正式API评测已经完成。

## 18. 顶会审稿人最可能的攻击与应对

| 质疑 | 必须给出的证据 |
| --- | --- |
| 只是针对三个方法造题 | capability-balanced数据、blind holdout、多模型baseline |
| 合成文本不自然 | humanized holdout、自然度评分、synthetic discriminator |
| gold可能错 | unique solver、双重投影、100% provenance、人工核验 |
| 难度只是文本长 |长度匹配对照、结构轴回归、operator消融 |
| 新增audit列抬高错误率 | 单独报告传统业务表和audit表 |
| train/test模板泄漏 | graph/render/operator composition split |
| 只对体育有效 | logistics、public finance及domain-OOD |
| LLM judge不可靠 | 确定性cell/evidence主指标 |
| 强工具模型能解决 | Program-of-Thought和tool-agent baseline |
| 数据很快被污染 | private refresh test、版本化生成器 |
| 没有社会/数据说明 | Datasheet、Data Statement、许可和annotator说明 |

数据发布时应提供Datasheet，记录动机、组成、构造、用途和限制；语言与标注人群信息应按Data Statements说明，不能为了“看不出怎么生成”而隐瞒来源。[Datasheets for Datasets](https://arxiv.org/abs/1803.09010) [Data Statements for NLP](https://aclanthology.org/Q18-1041/)

## 19. 论文实验最小充分集合

至少包含：

1. Direct、CoT、self-consistency、Program-of-Thought；
2. T³和Map&Make官方实现/提示；
3.统一backbone对比；
4.至少一个开源模型和两个强闭源模型；
5.固定schema和latent schema；
6.每个operator和tier的分组结果；
7.传统表与audit表分开结果；
8.完整oracle ladder；
9.自然化与模板版本对比；
10. artifact classifier结果；
11.人类上限；
12.至少30个独立seed或足以形成稳定置信区间的样本。

## 20. Go / No-Go门槛

进入正式大规模构造前必须同时满足：

-三domain至少各完成50个高质量pilot；
-unique solver通过率≥99%，失败样本全部排除；
-人工事实一致性≥99.5%；
-人类Tier 4 cell accuracy≥90%；
-至少两种强模型在不同operator上出现不同能力曲线；
-Program-of-Thought不能把所有Tier 4都直接饱和；
-artifact classifier不能从表面特征可靠预测operator或答案；
-核心业务表上的难度梯度成立；
-所有文本来源、许可和annotator流程可写入datasheet。

如果Program-of-Thought在Tier 4接近100%，不要继续堆随机噪声；应增加真实的scope、版本、跨document和schema问题。如果人类也无法稳定解决，则说明样本不是“难”，而是“不清楚”。

## 21. 推荐的下一步

1. 先把现有cricket generator重构为统一event graph接口；
2.实现logistics renderer和public-finance renderer；
3.按240配方网格各生成一个机器版本；
4.抽取60个做blind human rewrite；
5.完成artifact audit；
6.运行正式Direct/CoT/T³/Map&Make/Program-of-Thought；
7.依据结构轴和人类表现标定Tier，而不是根据目标模型错误率倒推；
8.达到Go门槛后扩展到1,200实例pilot。

这条路线的真正贡献不是“造出更难的体育文字”，而是把Text-to-Table重新定义为一个可验证的证据解析、事件状态维护与表格投影问题。
