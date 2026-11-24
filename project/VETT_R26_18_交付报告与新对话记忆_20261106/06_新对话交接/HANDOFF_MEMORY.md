# 新对话交接记忆

> 新对话必须先完整阅读本文件，再查看`../00_总览/README.md`。在确认当前状态前，
> 不要重新生成数据、改协议或调用任何付费模型。

## 1. 工作位置

- 工作区：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017`
- 原项目：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas`
- 本交付包：`D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_R26_18_交付报告与新对话记忆_20261106`

原项目不是以本交付包为替代品；代码、数据和运行证据仍以原项目为准。

## 2. 用户的核心目标

构建220场、长上下文、事实有据但隐蔽、无简单规律的板球文本转结构化表格数据集，
用于论文和现有模型能力缺陷评测。优先级为：

1. 足够难且能区分强模型；
2. 金标与证据链可靠；
3. 可复现、可解释、费用受控。

经验目标：强模型事实答案宏准确率约65%以下，五个等级相邻差希望平均至少约8个
百分点。该目标尚未被完整外测证实，不能写成已经达到的结果。

## 3. 当前冻结对象

| 层级 | 当前对象 | 结论 |
| --- | --- | --- |
| 规范根 | R20，220场 | 220/220机器门通过；217独立根+3重复控制 |
| 当前高难度数据候选 | `r26_15_content_dependency_candidate_v3/` | 20场、100题、25情景家族 |
| 全量可扩展性 | R26.15流式计划 | 220场、1,100题、3,564内容边通过预检，尚未最终物化发布 |
| 当前评测协议 | R26.18 `canonical_set_v2` | 本地准入通过，外部执行阻断 |
| 当前配置 | `eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json` | 不得直接用于付费执行 |

重要：R26.16–R26.18都是评测层演进，没有修改R26.15数据字节或金标。

## 4. R26.18解决了什么

R26.17已经用`exact_target_map_v3`解决“同一题目ID重复、其他题缺失”。新的单场输出
虽然5/5题齐全，却在两个题目中重复完全相同的证据边。R26.18将其拆成：

- 集合语义：完全相同的span ID或边三元组按集合计分；
- 输出服从性：重复仍记为nonconformant；
- 联合指标：要求证据语义和不重复同时成立。

非法JSON、缺题、非法关系、畸形/外来节点、原始数组超限和provider错误仍为硬失败。
旧`strict_unique_v1`行为没有改变，历史运行没有追溯转正。

## 5. 已完成的实现与证据

关键代码：

- `src/vett_eval/runner.py`
- `src/vett_eval/analysis.py`
- `src/vett_r26/protocol_analysis.py`
- `src/vett_r26/sentinel_preflight.py`
- `src/vett_r26/canonical_set_replay.py`
- `src/vett_r26/canonical_set_admission.py`

关键规范与工件：

- `docs/R26_18_CANONICAL_SET_CONFORMANCE.md`
- `design/r26_18_canonical_set_metric_addendum.json`
- `design/r26_18_canonical_set_request_contract.json`
- `analysis/r26_18_canonical_set/ZERO_REQUEST_PREFLIGHT.json`
- `analysis/r26_18_canonical_set/ADMISSION.json`
- `analysis/r26_18_canonical_set_replay_match0021/CANONICAL_SET_REPLAY.json`

冻结结果：

- 202/202全仓测试通过；
- 后验回放证明规范化前后集合语义评分字典逐项一致；
- 五场预检25题通过Oracle、未知引用和重复故障注入；
- 最大上下文利用率上界26.4562%；
- 最小Oracle输出余量1.551163倍；
- 保守费用估算1.0074元，硬上限1.4元；
- R26.18 provider请求数0；
- 准入状态`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`。

## 6. 外部实验必须保持的边界

### R26.16

计划5场，实际5场、6次请求、5个计费响应，只有4场20题可评分；费用0.635277元。
四场子集：事实整记录20%、12字段71.67%、信息字段62.22%、值平衡38.83%、
内容依赖边17.39%、事实+完整链0%。分级为100% / 64.58% / 75% / 70.83% /
47.92%，存在L2→L3倒置，但不是完整匹配结果。

### R26.17单场烟雾

`match_0220`返回5/5题，无截断和验证错误；费用0.157785元，证明精确题目键有效。
单场结果只能诊断，不能冒充五场。

### R26.17新五场尝试

首次第一场503且0费用；授权续跑后`match_0021`返回5/5题，但两题有7组重复边、
31个冗余副本、最大17次，费用0.12499元，后四场没有请求。原批次保持
`PROTOCOL_INVALID_STOPPED_EARLY`。

### R26.18回放

只用保存响应做本地回放：5/5题可规范化，2/5不服从，题级服从率60%。这是
`NON_OFFICIAL_POST_HOC_REPLAY`，不能作为正式模型成绩。

## 7. 下一步的正确决策

在没有新用户授权时：只允许阅读、审计、运行本地测试和零请求预检。

若用户明确授权一次新五场：

1. 从阻断配置复制新配置；
2. 只修改授权位和全新空输出目录；
3. 再跑测试与零请求预检；
4. 保持零重试、防重复请求、首个硬失败停止和1.4元硬上限；
5. 执行同一匹配Sentinel5；
6. 先冻结原始工件，再做错误分析；
7. 根据预注册门决定是否Pilot20，不要自动扩测。

完整五场前，不要继续盲目增加难度。若结果在45%–65%且曲线足够单调，优先扩统计
覆盖而不是继续加难；若高于65%，只增强模型确实解决的机制；若低于45%，检查是否
过难或规范负担过重。

## 8. 本地复现

```powershell
Set-Location 'D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas'
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m vett_r26.sentinel_preflight --config eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json --output-dir analysis/r26_18_canonical_set
python -m vett_r26.canonical_set_admission --config eval_configs/r26_18_glm53_canonical_set_sentinel5_blocked.json --output-dir analysis/r26_18_canonical_set
```

完整说明见`../04_代码与复现/REPRODUCTION.md`。

## 9. 严格禁止遗忘的事项

- 不得在消息、报告、commit或交付包中复制API密钥；
- 不得因为本地存在密钥而推定用户授权付费请求；
- 不得合并不同协议、不同场次覆盖或后验回放的成绩；
- 不得把协议错误记成语义零分；
- 不得把后验规范化改写成历史正式通过；
- 不得称220场R26.15已经最终物化或人工双标；
- 不得声称≤65%和五级8个百分点目标已经实现；
- 不得重新实现已经完成的R26.18，除非发现可复现回归。

## 10. 新对话的第一项动作

先确认以下三件事并向用户简短汇报：

1. 已读取本文件和交付包总览；
2. 原项目、冻结配置和`ADMISSION.json`仍存在；
3. 当前不会触发任何provider请求。

然后等待用户选择：只做论文/数据交付整理，还是明确授权冻结的五场外测。

## 11. 2026-11-12 Sentinel5执行后权威更新

本节覆盖上文所有“R26.18 provider请求0、Sentinel5未授权/未执行”的执行前历史描述。

- 用户已明确授权一次R26.18 Sentinel5模型调用，授权ID为`AUTH-R26.18-S5-20261112-01`；
- SiliconFlow `zai-org/GLM-5.3-Flash`完成5场25题，5个批次均`OK`，没有重试；
- 实际费用0.649936元，输入623,549 token、输出53,963 token；
- 请求哈希逐批匹配预检，无截断、验证错误、JSON修复或解析错误；
- 冻结主指标66.3333%，L1–L5为100% / 56.6667% / 63.3333% / 60% / 51.6667%；
- 事实整记录exact 28%，反事实整记录exact 12%，完整事实证据链exact 0%，内容依赖边F1 9.2308%；
- 输出服从率92%；`match_0162`两题各有1个完全重复项，按`canonical_set_v2`规范化，语义可评分性不受影响；
- R26.15候选仍为165文件、93,346,177字节，逐文件与阶段0一致，没有数据修改；
- 当前生命周期为`SENTINEL5_COMPLETE_VALID`，经验状态为`SENTINEL5_COMPLETE_VALID_WITH_CONFORMANCE_WARNINGS`；
- 历史`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`只描述执行前准入，不再是当前生命周期标签。

只登记一个主假设`HYP-R26.18-S5-001`：整体略高于65%可能由L1天花板驱动。下一步若要外测，
必须由用户单独授权冻结Pilot20来证伪。当前没有Pilot20、第二模型、重试、数据修改、shadow外测、
220场物化或发布权限，不能自动继续调用provider。

新对话应先读：

1. `analysis/r26_18_sentinel5_execution_20261112/SENTINEL5_RESULT.json`；
2. `analysis/r26_18_sentinel5_execution_20261112/FOUR_TRACK_REPORT.md`；
3. `analysis/r26_18_sentinel5_execution_20261112/ERROR_HYPOTHESIS_REGISTRY.json`；
4. `analysis/r26_18_sentinel5_execution_20261112/PROJECT_STATE.json`。
