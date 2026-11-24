# R26.13 五场哨兵请求就绪与止损协议

> **已阻断（2026-10-20）**：答案先验审计失败后，本配置状态为`NOT_READY`，不得发起provider请求。原成本与协议编译记录只保留作历史对照；可用的后继零请求合同见`design/r26_14_sentinel5_request_contract.json`及`analysis/r26_14_answer_blind/SENTINEL5_ZERO_REQUEST_PREFLIGHT.json`。

## 当前判定

`NOT_READY`：成本、容量与失败归因仍可复现，但公开题面可预测私有事实答案，新的硬门已在读取密钥和调用provider前阻断。本轮没有发起请求，也没有产生provider费用。

这不是难度达标结论。它只说明下一次付费实验已经被约束为一个有明确决策价值的最小动作。

## 冻结实验单元

- 模型：`zai-org/GLM-5.3-Flash`；
- 输入：只用 `uniform` 正式形式；
- 场次：`match_0021`、`match_0066`、`match_0067`、`match_0162`、`match_0220`；
- 请求：每场一批、每批五题，共五个可独立恢复和归因的请求；
- 输出：`request_bound_v2` 包络、`edge_derived_v3` 证据角色、严格 JSON Schema；
- 重试：0；任何批次失败即停止，终态失败不会在恢复时自动重复付费；
- 生成参数：`temperature=0.1`、`top_p=0.95`、thinking budget 2,048、最大输出16,384 token。

模型目录记录1,024K上下文；价格合同按缓存输入/普通输入/输出每百万token分别0.23/0.8/2.8元冻结，并标注核验日期。动态来源分别为[SiliconFlow模型目录](https://www.siliconflow.cn/models)和[SiliconFlow价格说明](https://www.siliconflow.cn/news/ok5ja7brf921kgf1644yyedz)。正式执行前仍应复核价格是否变化。

## 本地上界

- 五场零缓存保守费用估计：0.9399元；硬上限：1.20元；
- 最大上下文占用上界：24.956%，合同上限40%；
- Oracle完整结构化响应加thinking预算后的最小输出余量：1.315倍，合同下限1.25倍；
- 五个语义请求哈希互不相同，且请求中未出现私有金标键；
- 当前输出目录必须不存在，防止把旧R26.12响应误当成R26.13结果。

费用是按配置和保守token近似得到的准入估计，不是provider账单。若模型实际分词、隐藏推理计费或服务端价格规则不同，账单可能变化，因此硬费用门仍由runner在执行前再次检查。

## 错误分层

当前通用故障矩阵包含12个单点注入：

- 协议层6类：缺题、重复span、未知中立span、超长解释、实例ID不匹配、反事实字段不完整；
- 语义层4类：事实总分错误、缺支持边、同端点错误关系、缺排除边；
- 传输/包络层2类：`finish_reason=length`和JSON闭合修复。

12类均被归到预期层。传输或协议失败不计入语义准确率，避免把超时、截断或格式问题伪装成数据集难度。

## 花钱后的分支规则

1. 五场 `uniform` 协议不完整：立即停止，只修协议，不做难度结论。
2. 仅当有效 `uniform` 满足以下任一条件时，才批准同五场 `proof_only`：事实字段宏准确率不高于65%、最小证据边F1低于65%、事实+完整链exact低于50%。
3. 仅当 `proof_only-uniform` 至少在事实字段提高10个百分点、边F1提高15个百分点或联合链提高20个百分点时，才运行 `middle`。
4. 仅当 `middle` 相对 `uniform` 的事实字段绝对差至少10个百分点或联合链绝对差至少20个百分点时，才运行 `head/tail`。
5. 五场只用于筛查；论文级五级差和65%目标仍需20场、至少两个强模型家族。

这样每一次新增费用都对应一个预注册问题：协议是否有效、瓶颈是检索还是合成、位置是否真的造成可测差异。没有达到分支阈值时停止，而不是把所有变体机械跑完。

## 可复核入口

- 请求合同：`design/r26_13_sentinel5_request_contract.json`
- 诊断升级合同：`design/r26_13_diagnostic_escalation_contract.json`
- 阻断配置：`eval_configs/r26_13_glm53_flash_uniform_sentinel5_blocked.json`
- 零请求编译：`analysis/r26_13_request_readiness/SENTINEL5_ZERO_REQUEST_PREFLIGHT.json`
- 故障矩阵：`analysis/r26_13_request_readiness/PROTOCOL_FAULT_MATRIX.json`
- 当前决策：`analysis/r26_13_request_readiness/NEXT_ACTION.json`

