# 数据结构、评分契约与证据等级

## 工程主要对象

| 对象 | 常见位置 | 意义 |
| --- | --- | --- |
| 原始比赛文本/记分卡 | `workspace_snapshot/cricket_220_extracted/match_*/` | 每场commentary、scorecard、meta、evidence_chain |
| 规范比赛根 | `vett_cricket_pilot_v1/data/canonical_roots_217.jsonl` | 去重后的源表、元数据、事件和审核状态 |
| 公开实例 | 各实验`public*.json`、`instance/*public.json` | 允许盲测模型看到的文本/模式 |
| 私有金标 | `private_gold*`、`*private_gold*` | 每轮自己的规范答案与计分位 |
| 私有证据 | `private_evidence*`、`*evidence_graph*` | 候选归属、裁决标签、证据跨度、依赖关系 |
| 模型预测与阶段产物 | `runs/`、`runs_gpt55/` | 实验产物；需与run记录、冻结哈希一起引用 |
| 机械Oracle/消融 | `selftest/`、`ablations/`、`*SELFTEST*` | 检查构造和评分器；不能登记成新模型推理结果 |
| 失败/准入/迭代 | `*ITERATION*`、`*AUDIT*`、`*DECISION*` | 解释淘汰原因、版本状态和准入限制 |

上表除原始路径外均相对`workspace_snapshot/`。不同版本schema有演化，必须加载同版本公开模式、金标与评分器，禁止混用。

## 各阶段预测接口

- 早期全库：参考`schemas/`、`baselines/prompt_templates.json`和`score_predictions.py`。
- R10：完整`tables`预测；按表身份、行位置、列名及冻结scored-cell集合对应。使用`v0.15_mainstream_method_check/score_r10_predictions.py`，金标与证据来自`v0.14.../instance/`。
- R12：`instances`内各实例的`tables`；字段ID组合为`table_id.row_key.field`。有两个不计分的空金标结构位，详见`R12_SCORING_EXCLUSIONS.json`。
- R13-C/R14：`tables`或`target_tables`，行字典含`row_key`。评分器以私有组件分组报告有效决策准确率。
- R15：扁平`cells`字典，键格式为`table_id|entity|field`。公开表中`null`需要填写，`—`是不计分结构位。68个计分ID在同版本私有金标中显式列出。

R15输入示意（仅展示格式，不含真实答案）：

```json
{"cells":{"I1_batting|Example Player|runs":12}}
```

## 统计口径陷阱

1. R10结果JSON的`cell_error_rate`采用0–1比例；R12结果JSON的同名字段采用0–100百分数。跨版本合并时建议从错误数/分母重新计算。
2. R10公开338个空位，其中336计分；R12公开319个空位，其中317计分。不要用空位数量自动代替正式分母。
3. 规范值错误、严格JSON类型错误、事实内容错误要分栏。R12的大量严格类型错误不能解释成同等规模事实错误。
4. 宽松内容规范化可能删除标点、符号和大小写。若未来加入负数、符号有语义的ID或区间，旧规范化可能错误地合并不同事实；先补测试再复用。
5. 一组错误决策会污染多个单元格。同时报告cell、component、row、table和root；不要把68个错误格等同68个独立推理失败。
6. `AUTO_CHECK_PASS`、`READY_FOR_GENERATED_VIEWS`、`RELEASE_CANDIDATE`具有机械含义，不能自动升级为人工证据支持已通过。

## 证据分级

| 标签 | 允许说明什么 | 不允许推出什么 |
| --- | --- | --- |
| `HISTORICAL_MODEL_RUN` | 原件记录为模型运行，预测/阶段产物可定位 | 当前归档程序无法重新证明模型身份与历史隔离强度 |
| `FROZEN_PREDICTION_RESCORE` | 已冻结预测与评分器重跑一致 | 新一次模型生成、跨模型泛化 |
| `DETERMINISTIC_MECHANISM_TEST` | 指定故障策略或状态选择的影响 | 主流方法的真实错误率 |
| `CONSTRUCTION_ORACLE` | 在规定构造表示中恢复金标 | 自然文本最小证据充分性与盲测难度 |
| `SCORER_SELFTEST` | 空白/金标回灌/突变被正确计分 | 数据来源真实性、人工唯一解 |
| `SYNTHETIC_EVENT_LEDGER` | 记分卡约束下的合成顺序与聚合闭合 | 观测到的逐球日志 |
| `PENDING` | 计划/入口已准备 | 已完成的成绩 |

## 盲测最低规范

仅将经审核的公开文本、空表、允许的通用工具和该方法冻结提示交给求解环境。完整本归档含私有资料，不能用作盲测上下文。每方法每轮独立目录，记录模型可核验标识、时间、输入和提示哈希、参数、工具权限、截断/重试、阶段输出及费用（如有）。

预测写完后冻结SHA-256；再由单独评分过程读取金标。修改任何预测都应产生新run_id，不能覆盖原结果。异常解析、超时和无输出应计入正式运行记录。通过开发集改难后，需要未见根的保留测试集来估计泛化。
