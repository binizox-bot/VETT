# R26.17 输出协议可靠性与四场诊断

R26.17是本地评测改进层，不创建新数据候选，也不修改R26.15的公开文本、题目、答案、证据成员或图边。它解决Edge7五场中已经实测出现的重复题目ID失败，并把四场有效结果整理为不能触发数据改写的诊断账本。本轮provider请求为0。

## 重复ID根因

`request_bound_v2`把五个预测表示成长度固定为5的数组，并把每个`question_id`限制在五个允许值中。JSON Schema的这一组合不能表达“每个允许ID恰好出现一次”：同一个合法ID重复五次仍可能满足provider结构约束，之后才会被本地规范化器判为重复四次、缺失四题。这正是`match_0220`的失败形态。

`exact_target_map_v3`把`decision_predictions`改成对象，五个精确题目ID分别是五个必需属性，`additionalProperties=false`，每个属性值不再重复输出`question_id`。因此重复、漏题和陌生题目键在严格结构层即可被阻止；本地规范化仍保留二次防线。旧协议与历史运行不追溯修改。

## 本地验证

- Oracle端到端运行通过，5/5题恢复到标准预测格式。
- 实测重复ID数组、缺少目标键、陌生目标键、内部冗余ID和冲突比赛ID均被协议拒绝。
- 合法键之间交换事实载荷不会被冒充协议错误，而是继续作为语义错误被冻结评分器扣分。
- 形状合法但不存在的证据ID继续按Edge7语义假阳性处理。
- 五场零请求预检通过，所有请求哈希唯一，最大上下文利用率上界26.4428%，最小Oracle输出余量1.551倍。
- 五场零缓存保守估计为1.0069元，比旧协议0.9699元增加0.0370元；增加来自精确键Schema，不重复输入比赛文本。
- 所有配置保持`execution_authorized=false`，provider请求为0。

## 四场结果的正确解释

四场协议完整子集的冻结12字段主指标为71.67%，信息字段准确率为62.22%，信息字段值平衡准确率为38.83%。原始主指标比信息字段高9.44个百分点，说明恒零账本字段和多数值先验会抬高“局部字段正确”的表观结果。冻结主指标不能事后更换，但也不能把71.67%全部解释成模型读懂了文档，更不能据此全局加难。

20题中最常出错的事实字段是`bowler_runs`（12题）、`dismissal`和`total_runs`（各11题）、`batter_runs`与`ledger.BATTER`（各8题）。证据图方面，缺失最多的是`authorizes`、`governs_decision`、`supports_decision`和`conditions_rule`，说明主要瓶颈确实位于权限—事实—规则—决策链，而不只是证据ID抄录。

L2到L3的10.42个百分点倒置主要与总分、击球手/投球手归账、交付状态和No-ball/Wide extras有关；但四场子集中每个等级都缺少一个匹配锚点单元，等级差异与情景组成混杂。因此这些字段只能登记为候选机制，不能立即修改L2或L3文本。

## 当前决策

- 不进行全局加难。
- 不修改冻结R26.15数据字节。
- 采用`exact_target_map_v3`进入本地协议候选。
- 用户随后只授权`match_0220`的新run ID协议烟雾测试。唯一一次请求在207.870秒后成功：5/5题、`finish_reason=stop`、无截断、无验证错误、无未知证据警告；输入161,290 token、输出10,269 token，实际费用0.157785元，低于0.2453元保守估计和0.35元硬上限。
- 单场附带诊断的字段主指标53.33%、信息字段37.78%、值平衡信息字段29.01%、整记录20%、span F1 54.68%、typed-edge F1 42.80%、内容依赖edge F1 10.53%、事实+完整链exact 0%。这些数值只能诊断协议成功后的评分通路，不能与历史`request_bound_v2`四场合并成正式Sentinel5。
- 新协议已经通过provider实测，因此下一项可能有决策价值的实验是全新run ID的五场`exact_target_map_v3`；保守费用1.0069元。但它仍需单独授权，只有完整五场复制字段偏易或等级倒置，才允许建立局部数据修改候选。

用户随后明确授权该全新五场配置。第一场`match_0021`在0.997秒后返回HTTP 503 / provider code 50508（系统繁忙），没有模型输出、token或费用。运行器遵守零重试和失败即停：后四场均未提交，五场语义覆盖率为0%。这只是一项供应方可用性失败，不反驳此前已经成功的单场协议烟雾，也不产生任何难度证据。

新的可用性续跑已冻结为`execution_authorized=false`，仍包含原五场，因为本次没有任何成功响应；逐场请求哈希与原零请求预检完全一致，保守费用仍为1.0069元。它需要新的明确授权，不能把“执行五场”的已消费授权解释为无限重试许可。

用户再次明确授权后，只把冻结配置的`execution_authorized`翻转为`true`。`match_0021`一次请求在261.821秒后完整返回5/5题，`finish_reason=stop`且未截断；输入119,085、输出10,615 token，实际费用0.12499元。响应仍违反证据边集合唯一性：两个答案含完全重复边，共7个重复组、31个冗余副本，最大同一边重复17次。Schema原本已声明`uniqueItems=true`，提示词也明确禁止重复，所以该批保留为`INVALID_OUTPUT`，运行器立即停止，后四场没有提交。

这次结果不能产生正式事实或证据分数。由于五个事实对象本身完整，本地只登记非官方事实诊断：冻结12字段宏准确率71.67%、整记录20%；不计算或发布官方证据指标，不与任何历史子集合并，也不据此改写数据。它表明`exact_target_map_v3`已经消除了重复题目ID，但provider并未可靠执行数组`uniqueItems`。下一步应先预注册“协议服从性与集合语义证据质量分轨报告”的本地规则，而不是继续付费重跑。

## 复现

```powershell
$env:PYTHONPATH = 'src'
python -m vett_r26.exact_target_map_audit --release r26_15_content_dependency_candidate_v3 --instance-id match_0220 --output analysis\r26_17_exact_target_map
python -m vett_r26.sentinel_preflight --config eval_configs\r26_17_glm53_flash_exact_target_map_sentinel5_blocked.json --contract design\r26_17_exact_target_map_request_contract.json --output analysis\r26_17_exact_target_map\ZERO_REQUEST_PREFLIGHT.json
python -m vett_r26.edge7_subset_diagnostic --release r26_15_content_dependency_candidate_v3 --cohort-report analysis\r26_16_edge7_sentinel5_cohort\COHORT_ANALYSIS.json --predictions analysis\r26_16_edge7_sentinel5_cohort\COHORT_PREDICTIONS.jsonl --ledger analysis\r26_9_difficulty_ledger\PRIVATE_DIFFICULTY_FEATURE_LEDGER.jsonl --output analysis\r26_17_edge7_subset_diagnostic
python -m vett_r26.protocol_smoke_outcome --blocked-config eval_configs\r26_17_glm53_flash_match0220_exact_target_map_smoke_blocked.json --authorized-config eval_configs\r26_17_glm53_flash_match0220_exact_target_map_smoke_authorized.json --run eval_runs\r26_17_glm53_match0220_exact_map_smoke\r26_17_glm53_match0220_exact_map_smoke --preflight analysis\r26_17_exact_target_map\ZERO_REQUEST_PREFLIGHT.json --output analysis\r26_17_match0220_exact_map_smoke
```
