# 220场板球 Text-to-Table 数据总览与正式构造路线

版本：v1.0  
审计对象：`Self-cricket-clean_text_scorecard_v1_220_matches.zip`  
建议数据集名称：**VETT-Cricket（Versioned Evidence Text-to-Table for Cricket）**

## 一、结论

这220场数据适合作为数据集的**候选根数据（candidate roots）**，目前不适合作为可直接发布和评测的金标准。

原因有四个：

1. 220个目录中只有217个独立比分卡，存在3组整场重复。
2. 自动规则检查在220场中的113场发现至少一项待核问题；排除击球手球数口径这一较弱检查后，仍有约66场存在更明确的算术、身份或结构异常。
3. 当前文本大多是长篇赛后叙述，完整比分卡中的大量单元格没有在文本中出现。模型无法唯一恢复这些字段。
4. `evidence_chain.md`大量使用目标比分卡本身作为证据，并包含改名、重构、比分指纹变化等生成说明。它不能充当独立证据，也不能作为模型输入。

因此，正确路线是：

> 将220场作为原始候选根 → 去重和裁决得到规范比赛账本 → 为每个目标单元格标注文本证据与推导程序 → 分别建立自然支持轨、证据完备轨、状态修订轨和多源冲突轨 → 按根比赛隔离切分 → 再运行T³、Map&Make与CoT等基线。

如果直接把当前 `commentary.txt` 输入模型、把完整 `scorecard.md` 当作目标，得到很高的错误率也无法证明方法不足。评审者可以合理指出：许多目标值根本没有被输入文本支持。

## 二、全量审计结果

### 2.1 文件与结构

| 项目 | 结果 |
| --- | ---: |
| 比赛目录 | 220 |
| 四类文件完整的目录 | 220 |
| 解析出的有效局数 | 440 |
| 去除比赛编号后的独立比分卡 | 217 |
| 完全重复比赛组 | 3组 |
| 明确泄露构造过程的文本 | 3场 |
| 使用目标表作为证据的 evidence 文件 | 144场 |

三组完全重复比赛为：

- `match_0037` 与 `match_0038`
- `match_0118` 与 `match_0119`
- `match_0197` 与 `match_0200`

建议保留每组编号较小者，排除 `match_0038`、`match_0119`、`match_0200`。正式数据集应按217个根比赛统计样本独立性。

`match_0162`、`match_0163`、`match_0164`的正文直接出现了类似“anonymized”“source game”“scorecard fingerprint”的构造过程表述。这三场必须重写正文或排除。

### 2.2 文本形态

| 项目 | 结果 |
| --- | ---: |
| 文本字符数 | 3,489–9,808 |
| 中位字符数 | 6,535.5 |
| 文本词数 | 623–1,665 |
| 中位词数 | 1,111 |
| 单段文本 | 216/220 |
| 以 “At” 开头 | 152/220 |
| 含列表结构 | 0/220 |
| 数字字符中位数 | 0 |
| 完全没有阿拉伯数字的文本 | 139/220 |

当前风格高度集中于英文长篇赛后叙述。它不能代表直播逐球文本、短消息线程、裁判修正、记分员公告、混合来源报道和结构松散的现场文本。数据集若仅保留这一风格，方法可以通过叙述模板和固定位置形成捷径，跨风格贡献有限。

### 2.3 比分卡内部一致性

自动检查共执行8,313项，发现204项待核，涉及113场。这里的“待核”表示需要人工或原始来源确认，不等价于204项全部已经确定错误。

| 检查项 | 待核局数/次数 | 说明 |
| --- | ---: | --- |
| 击球手球数与局合法球数 | 101/440 | 已同时容许“合法球数”与“合法球数+无球”两种常见数据口径，仍不一致；需要来源级核查 |
| 击球得分+额外分=总分 | 8/440 | 强算术冲突 |
| 投球手球数=局合法球数 | 1/440 | 强算术冲突 |
| 出局记录与投球手 wickets | 9/440 | 人员身份或wicket归属冲突 |
| 投球失分与局总分核对 | 19/440 | 已扣除byes和leg-byes |
| 最大搭档分 | 25/440 | 摘要字段与搭档表冲突 |
| 搭档双方贡献+extras | 27/440 | 搭档内部算术冲突 |
| 搭档累计与FOW | 5/428 | 累积路径冲突 |
| FOW格式/顺序 | 4项 | 含0 wicket特殊编码和1项非单调问题 |
| Player of the Match身份 | 2场 | POM未出现在任何击球或投球表中 |

自动状态建议：

| 建议状态 | 场数 | 后续动作 |
| --- | ---: | --- |
| `AUTO_PASS_NEEDS_SUPPORT_AUDIT` | 104 | 内部规则暂未发现问题，仍需做文本证据审计 |
| `REVIEW_BALL_ACCOUNTING` | 46 | 重点核对球数、无球和来源记分口径 |
| `REPAIR_SCORECARD` | 64 | 至少存在一项较明确的非球数冲突 |
| `REWRITE_INPUT_CONSTRUCTION_LEAK` | 3 | 清除正文中的构造过程泄露，并重新核验 |
| `EXCLUDE_DUPLICATE` | 3 | 从独立根比赛中排除 |

每场的具体状态、失败检查和建议动作见 `results/per_match_audit.csv`；每一个检查的细节见 `results/check_details.csv`。

### 2.4 文本对完整表格的可恢复性

下列结果是宽松的词法支持代理：只要某个数值以数字或英文数词形式出现在球员姓名附近，就算“可能受支持”。它比严格语义蕴含更乐观。

| 单元格类型 | 宽松支持率 |
| --- | ---: |
| 有实际上场记录的击球手姓名 | 98.37% |
| 击球得分 | 30.84% |
| 面对球数 | 19.93% |
| 四分球数 | 23.53% |
| 六分球数 | 12.44% |
| 投球手姓名 | 93.27% |
| 投球 wickets | 42.80% |
| 投球失分 | 9.71% |
| 局总分 | 93.18% |
| 小数形式overs | 10.68% |

这说明当前文本通常可以恢复比赛结果、主要球员、局总分和少数关键表现，无法恢复完整 batting、bowling、partnership、FOW 表。

当前数据最适合先构造“文本支持子表”，完整比分卡则作为规范账本和规则校验来源。若要评测完整比分卡生成，需要为缺失字段补充自然、可追踪的文本证据。

## 三、正式任务定义

建议把任务从简单的“文章生成完整表格”升级为以下形式：

\[
D \rightarrow M \rightarrow E \rightarrow G \rightarrow T
\]

其中：

- \(D\)：一个或多个文本文件；
- \(M\)：文本中的mention与证据span；
- \(E\)：经过实体链接、作用域判定、版本裁决后的事件；
- \(G\)：规范比赛事件图或账本；
- \(T\)：从规范事件图投影出的目标表。

每个金标准单元格必须记录：

```json
{
  "cell_id": "match_0001.I1.batting.ethan_drake.runs",
  "value": 49,
  "support_type": "DIRECT",
  "evidence_spans": ["doc_01#span_0042"],
  "derivation": null,
  "scope": {"match": "match_0001", "innings": 1},
  "version": 1,
  "status": "valid"
}
```

推导值必须记录可执行程序：

```json
{
  "cell_id": "match_0001.I1.total",
  "value": 144,
  "support_type": "DERIVED_GLOBAL",
  "evidence_spans": ["doc_01#span_0011", "doc_02#span_0007"],
  "derivation": "sum(batter_runs) + total_extras",
  "dependencies": [
    "match_0001.I1.batting.*.runs",
    "match_0001.I1.extras.total"
  ]
}
```

### 单元格证据标签

| 标签 | 含义 | 是否计入主轨 |
| --- | --- | --- |
| `DIRECT` | 文本直接表达值 | 是 |
| `DERIVED_LOCAL` | 由局部证据做简单换算或规范化 | 是 |
| `DERIVED_GLOBAL` | 需要跨句、跨表、跨文档聚合 | 独立全局推理轨 |
| `TEXT_CONFLICT` | 文本内部有冲突，需要版本或来源裁决 | 冲突轨 |
| `TABLE_CONFLICT` | 当前比分卡内部冲突 | 修复前不计分 |
| `TABLE_ONLY` | 只在表中存在，输入文本不支持 | 主轨屏蔽 |
| `AMBIGUOUS` | 存在多个合法答案 | 不计分或单独报告 |
| `NOT_APPLICABLE` | 该字段在当前比赛中不适用 | 不计分 |

## 四、VETT-Cricket的四条评测轨

### Track A：Natural Supported Table

输入使用现有自然化赛后叙述。目标只包含 `DIRECT` 和 `DERIVED_LOCAL` 单元格。

用途：

- 检验基本事实抽取；
- 检验人物、比赛阶段和表结构映射；
- 防止模型因无法恢复文本未提供的信息而被错误惩罚。

### Track B：Evidence-Complete Reconstruction

在规范比赛账本上构造证据完备文本，使完整目标表中每个计分单元格都有直接证据或唯一推导路径。

文本可以分散在多个文档中：

- 逐球播报；
- 赛后报道；
- 记分员摘要；
- 球员表现简报；
- 天气或DLS公告。

这一轨真正检验T³的全局tuple整合能力、Map&Make的原子命题与schema生成能力，以及CoT模型的长程数值推理能力。

### Track C：Versioned State and Correction

输入包含合法的新增、重复、修订、撤销和范围限定：

- 早期播报写错球员，稍后记分员修正；
- 同一wicket被多个来源重复报道；
- 无球导致早期“出局”无效；
- DLS目标更新；
- 某条更正只作用于第一局；
- 替补接球者与投球手身份分离。

模型必须输出最终有效状态，并给出每个单元格的证据和版本。

### Track D：Latent Schema and Multi-Table Projection

不给固定列名，要求模型根据文本推断需要的表及层级：

- Match Summary；
- Innings Summary；
- Batting；
- Bowling；
- Partnerships；
- Fall of Wickets；
- Revision Log。

该轨针对Map&Make的schema推断优势，同时检验方法能否在层级、多表、作用域和版本关系下保持一致。

## 五、难度构造方式

难度应来自可解释、可验证的能力维度，不能只靠拉长文本或故意写得含糊。

| 维度 | L0 | L1 | L2 | L3 | L4 |
| --- | --- | --- | --- | --- | --- |
| 证据距离 | 同句 | 相邻句 | 跨段 | 跨文档 | 跨文档+版本 |
| 数值推理 | 直接复制 | 单步换算 | 多项求和 | 约束联立 | 修订后重算 |
| 实体 | 全名唯一 | 代词/简称 | 同姓 | 角色变化 | 跨局同名冲突 |
| 事件状态 | 单次事件 | 重复 | 修正 | 撤销 | 局部作用域修正 |
| 来源 | 单来源 | 两来源一致 | 来源缺失 | 来源冲突 | 可靠性+时间联合裁决 |
| schema | 固定单表 | 固定多表 | 缺省列 | 潜在schema | 层级schema变化 |
| 文本风格 | 规范摘要 | 赛后报道 | 直播日志 | 消息线程 | 混合文档 |
| 噪声 | 无 | 拼写变化 | 断句/ASR | 顺序扰动 | 噪声与修订叠加 |

每个实例保存完整 `recipe`，但不把recipe暴露给模型。论文和datasheet公开构造机制、比例与质量控制，不在文本表面留下固定模板标记。

## 六、从217个独立根生成多风格实例

建议每个根比赛生成4个视图，总计约868个实例：

| View | 核心内容 | 主要风格 |
| --- | --- | --- |
| V0 | 现有文本的支持子表 | 自然化赛后叙述 |
| V1 | 证据完备的固定schema表 | 报道+记分员摘要 |
| V2 | 重复、修订、撤销和跨局状态 | 直播流+更正通知 |
| V3 | 多来源冲突与潜在schema | 消息线程+公告+报道 |

风格从下列集合分层抽样：

1. ball-by-ball live feed；
2. radio-style commentary；
3. post-match report；
4. scorer correction bulletin；
5. threaded messages；
6. mixed-source dossier。

当前220场缺少真实逐球事件。V1–V3必须明确标为“基于规范账本的受控半合成文本”。论文中公开这一点，同时通过人工编辑、模板检测、来源追踪和唯一可解验证控制质量。不能把受控生成文本描述成自然采集直播文本。

## 七、避免构造痕迹和捷径

当前数据已经暴露了几个明显捷径：216场是单段文本、152场以“At”开头、部分正文直接提到source game和scorecard fingerprint。

正式生成需执行以下检查：

1. 开头模板、结尾模板、段落数和句长分布控制；
2. 人名、球队、比分不能与难度标签或数据切分相关；
3. 同一生成模板不得跨训练集和测试集；
4. 对文本做5-gram重叠、TF-IDF近邻和语义近邻检查；
5. 训练一个“自然文本/受控生成文本”判别器；若简单分类器明显高于随机水平，继续人工改写；
6. 扫描 `source game`、`fingerprint`、`anonymized`、`original score` 等构造泄露；
7. 删除固定的“最终”“修正版”等机械标签，使用自然记分员语言表达修订；
8. 保留完整生成recipe和审计日志供作者复现，但不放入模型输入。

## 八、唯一可解与质量控制

每个实例进入正式测试集前必须通过六道门：

### Gate 1：规范账本一致

- batter runs + extras = innings total；
- extras分解一致；
- legal balls与overs一致；
- bowler conceded与byes/leg-byes规则一致；
- dismissals与bowler wickets一致；
- partnerships、FOW和final total一致；
- result、margin、DLS或innings规则一致。

### Gate 2：单元格证据完整

每个计分单元格至少有一个有效support set，或有可执行且依赖完整的derivation。

### Gate 3：唯一答案

从文本和规则执行器中只能得到一个规范值。如果两个独立标注者能给出两个不同且都合理的值，该单元格标为 `AMBIGUOUS`。

### Gate 4：反事实删除

删除某个关键证据span后，相应单元格应变为不可解或改变。这用于发现“证据标错但答案仍由目标泄露”的情况。

### Gate 5：双人标注与专家裁决

- calibration和测试集全部双标；
- 开发集至少30%双标；
- 类别标签报告Cohen’s kappa；
- 数值单元格报告精确一致率；
- 所有分歧由熟悉板球记分规则的专家裁决。

### Gate 6：人工可解基线

至少两名人类标注者在隐藏测试样本上达到高一致率。人类也无法稳定恢复的样本不能用于证明模型不足。

## 九、数据切分

去除3个重复副本后，以217个根比赛为单位切分：

| Split | 根比赛 | 4视图实例数 | 用途 |
| --- | ---: | ---: | --- |
| Calibration | 20 | 80 | 固定prompt、schema和解析器 |
| Development | 40 | 160 | 方法开发 |
| Public Test | 57 | 228 | 可复现实验 |
| Private Test | 100 | 400 | 防止针对测试集调参 |
| 合计 | 217 | 868 |  |

必须满足：

- 同一根比赛的所有视图只能属于一个split；
- 同源比分卡或近重复文本只能属于一个split；
- 人名池、球队池、文本模板和operator recipe按split隔离；
- private test不公开完整recipe和gold；
- 如果某根比赛在裁决后不可用，应从独立新来源补充，不能复制已有根。

## 十、评测指标

只报告一个“错误率”不够。建议至少报告：

1. **Cell Exact Match / Cell-F1**：规范化后单元格级正确率；
2. **Row-F1**：整行实体与字段同时正确；
3. **Table Exact Match**：整表完全正确比例；
4. **Omission Rate**：应生成但为空的单元格比例；
5. **Hallucination Rate**：无支持或不存在的单元格比例；
6. **Numeric Constraint Violation Rate**：违反板球算术约束的比例；
7. **Evidence Attribution F1**：生成值是否指向正确证据；
8. **Revision Resolution Accuracy**：最终状态是否正确；
9. **Schema F1 / Tree Edit Distance**：潜在schema质量；
10. **Worst-group Score**：按难度维度报告最弱组，而非只给平均值。

建议将“错误率”明确定义为：

\[
ER_{cell}=1-\frac{\#\text{正确且受支持的gold cells}}
{\#\text{计分gold cells}}
\lambda\frac{\#\text{hallucinated cells}}
{\#\text{计分gold cells}}
\]

同时单独报告错误和幻觉，避免一个复合分数掩盖方法行为。

## 十一、T³、Map&Make和CoT基线协议

T³论文将任务分解为全局tuple抽取、程序化信息整合和tuple-to-table；Map&Make采用原子命题化、schema推断和迭代表生成。两者原始prompt与数据域并非完整板球比分卡，应保留原方法结构，增加公开的cricket-adapted版本。

公平评测要求：

1. 使用相同的模型backbone；
2. 相同输入文本、最大上下文和输出token预算；
3. temperature固定为0；非确定采样时报告3个seed；
4. 保存完整prompt、prompt hash、模型版本与运行日期；
5. 同时报告 `paper_original` 和 `cricket_adapted`；
6. 输出解析器只修复格式，不修复数值；
7. T³使用“text → global tuples → code integration → table”；
8. Map&Make使用“proposition atomization → schema extraction → iterative table”；
9. CoT使用同一schema和规则说明，不额外提供gold字段；
10. 先在20场calibration集固定prompt，测试集禁止继续调prompt。

现阶段不建议运行正式错误率。当前gold仍有内部冲突和不可支持单元格，任何高错误率都可能同时包含模型错误与数据标注错误。

## 十二、实际执行顺序

### Phase 0：冻结原始层

- 原ZIP只读保存；
- 为每个文件记录SHA-256；
- 不直接覆盖原始文本和表格；
- 所有修复写入revision log。

### Phase 1：清理根比赛

1. 排除3个重复副本；
2. 重写3个构造泄露正文；
3. 优先裁决64场明确比分卡异常；
4. 核对46场球数口径；
5. 复查104场自动通过样本；
6. 最终生成217个或更少的规范根账本。

### Phase 2：20场试点

从四类状态中分层抽20场：

- 5场自动通过；
- 5场比分卡冲突；
- 5场低文本覆盖；
- 5场特殊赛制、DLS、多局或中止比赛。

完成全量cell provenance、4类view、人工双标和T³/Map&Make/CoT试跑。试点通过后冻结schema和标注手册。

### Phase 3：全量生产

- 批量解析；
- 人工裁决；
- 生成多风格文本；
- 证据对齐；
- 唯一可解验证；
- 泄露与近重复检查；
- root-level split。

### Phase 4：盲测与扩展

在private roots上运行基线，按错误类型补充能力覆盖。不能依据某个具体模型的错误反复修改同一测试集；新增困难样本应进入新的隐藏扩展集，并保留版本号。

## 十三、当前数据能否支撑论文

可以，但论文贡献应建立在以下三点：

1. **单元格证据与唯一可解机制**：解决Text-to-Table数据集普遍存在的目标不可支持问题；
2. **版本化状态与多源裁决**：检验静态tuple或原子命题方法在重复、修订、撤销和作用域上的不足；
3. **板球规则约束的多表生成**：把抽取、全局聚合、schema推断和规则一致性放在同一基准中。

不能使用的论证方式：

- “我们故意做得很难，因此T³和Map&Make错误率超过60%”；
- “现有模型留空很多，所以方法失败”；
- “模型没有恢复完整比分卡，所以模型不会推理”。

可成立的论证方式：

- 每个错误都对应一个被明确标注的能力维度；
- 每个目标单元格都有独立证据或唯一推导程序；
- 人类能够稳定求解；
- 模型错误集中在版本状态、跨文档整合、数值约束或schema投影；
- 同一模型在简单层表现正常，随难度维度上升出现系统性退化。

## 十四、审计范围与限制

本轮审计完成了文件完整性、Markdown解析、重复检测、内部算术检查、人物身份检查和宽松文本支持代理。

本轮审计没有访问每场比赛的原始官方网页或逐球来源，因此不能确认被改写前的真实比赛事实。自动检查通过只说明当前文件内部暂未触发规则，不代表其来源真实或文本完整。击球手球数检查还受数据提供方对无球的统计口径影响，已作为人工复核项处理。

## 参考方法

- [T³ / LiveSum, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.523/)
- [Map&Make, ACL 2025](https://aclanthology.org/2025.acl-long.1460/)
- [CheckList: Behavioral Testing of NLP Models, ACL 2020](https://aclanthology.org/2020.acl-main.442/)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [MCC Law 21: No ball](https://www.lords.org/mcc/the-laws/no-ball)

