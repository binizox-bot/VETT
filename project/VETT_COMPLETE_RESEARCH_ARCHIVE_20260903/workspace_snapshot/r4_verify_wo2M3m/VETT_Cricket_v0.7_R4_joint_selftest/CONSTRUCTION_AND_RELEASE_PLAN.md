# VETT-Cricket 完整构造与发布路线

## 当前完成情况

1. 审计 220 场原始包，去除 3 个精确重复，保留 217 个 canonical root。
2. 统一表结构、稳定 cell ID、事件记录、证据 span 和文件哈希。
3. 每个 root 生成 V0–V3，共 868 个候选实例。
4. 高强度复核后，99 个内部一致 root 开放 V1–V3，共 297 个
   `RELEASE_CANDIDATE`；其余保持 blocked，不伪造 gold。
5. 冻结 62/18/19 train/dev/test 划分。
6. V3 包含多来源、版本冲突、乱序、隐式 schema、八类可执行推导，以及
   同 split、不同场地的跨比赛干扰文档。
7. 536,634 项构造校验、11,494 项板球不变量校验、标准 JSON Schema
   校验、1,586 项泄漏/作用域校验全部通过。
8. 私有 ID oracle 和无 ID 语义 oracle 均在 125,070 个单元上达到
   100%；48 个故障注入断言全部
   通过；核心数据从源文件重建后逐字节一致。
9. 高强度复核隔离了 5 个此前被宽松规则放过的 root，并修复 0 wicket
   FOW 哨兵、±0.011 容差漏洞、重复 batter identity 和 5 个同场地 V3
   目标歧义。
10. 已生成 36 个 pilot 模型自然化任务、一个当前模型参与的校准样本，
    以及 T³、MapMake、Direct-CoT 的统一提示与输出协议。

## 必须完成的发布门槛

### A. 事实根裁决

- 68 场 `BLOCKED_SCORECARD_CONFLICT`：两名标注者独立定位冲突，再由板球
  专家裁决；不能用模型投票决定事实。
- 46 场 `NEEDS_BALL_ACCOUNTING`：逐局验证合法球数、overs、总分、
  extras、bowling conceded runs、FOW 和 partnerships。
- 3 场 `BLOCKED_CONSTRUCTION_LEAK`：重写输入并重跑泄漏扫描。
- 所有修订必须保留版本记录并重新运行全部校验。

### B. V0 支持性标注

- 99 场 eligible V0 现有 6,237 个 direct 候选和 35,453 个 table-only
  候选。
- 两名标注者判断 `DIRECT / DERIVED / TABLE_ONLY / AMBIGUOUS` 并标 exact
  span，第三人裁决 disagreement。
- V0 只评分文本支持或唯一可推导单元，不能把表中存在但文本未给出的值
  当作 gold。
- 报告 span F1、支持类型一致率和 Krippendorff α；未达到预注册门槛就
  返工。

### C. 模型辅助自然化

对 36 个 pilot job 依次使用互相隔离的角色：

1. discourse planner 只规划事实分配；
2. verbalizer 只改写表达，不得改动事实；
3. inverse extractor 在独立上下文中只看生成文本并反抽事实；
4. adversarial critic 查歧义、模板指纹、泄漏和多解；
5. symbolic validator 重验 span、公式、版本和作用域；
6. 人类板球语言审核后才能升级为 `HUMAN_VERIFIED`。

禁止同一次模型回答同时生成和验收。记录模型、prompt 哈希、温度、上下文
长度和日期。pilot 通过后再扩展至全部 297 个候选。

### D. 去模板化与反构造痕迹

- 建立新闻、赛后分析、直播更新、官方更正、统计笔记、简短公告等文体池。
- 独立采样句法、段落长度、事实顺序、来源数量和数字表达，不能让 match ID
  或难度标签直接选择固定模板。
- 用 unseen split 的“自然文本/构造文本”诊断分类器检查 construction
  fingerprint；显著高于随机时必须分析线索并返工。
- 当前 V3 repeated-sentence rate 为 92.66%，高于 60% 发布阈值，是明确
  阻断项。

### E. 基线与现代模型评测

- 在相同 backbone、温度、上下文和输出预算下运行 T³、MapMake、
  Direct-CoT，并加入 direct prompting、强指令模型和开放权重模型。
- 严格限制中间阶段可见信息，避免 tuple/atom 阶段偷看原文或 gold schema。
- 冻结数据后盲跑，报告 V1→V2→V3 变化以及 scope、version、ordering、
  derivation、latent schema、distractor 消融。
- 指标至少包括 cell accuracy/error、micro/macro F1、table exact、
  schema F1、row alignment、hallucination、omission、revision accuracy、
  derived-cell accuracy 和 target-scope accuracy。
- 不能以“让某方法错误率超过 60%”作为反向调题准则；否则容易被审稿人
  判定为针对基线过拟合。

### F. 论文级有效性

- 两名以上板球计分人员完成人类上限实验，报告准确率与耗时。
- 验证 V1、V2、V3 的难度趋势，并证明人类仍可稳定完成。
- 更换模型家族、prompt 和解析器后，结论方向应保持。
- 做公开语料近重复与污染检查。
- 盲测主榜中同一事实根只保留一个视图，其他视图用于受控 robustness。

## 当前可主张与不可主张

可以主张：候选构造管线、gold/证据/难度算子的机械一致性，以及三种机制
诊断器能分别暴露推导、版本和作用域失败。

不能主张：已经形成最终公开 benchmark，或 T³、MapMake、CoT 已达到某个
真实错误率。

统一门禁为机械层 8/8 通过、科学发布层 0/7 通过，总状态
`NOT_READY_FOR_PUBLIC_RELEASE`。
