# R26.16 未知证据归因与引用稳定性协议

## 结论

R26.16不创建新数据版本。当前数据仍是R26.15的20场、100题候选；本次改动只修复评测层把“引用了不存在的证据ID”误判为“整批输出不可解析”的问题。全量本地审计没有发现文本、事实、金标或证据链需要修改，因此保留候选字节和既有难度。

本地准入状态为`LOCAL_PROTOCOL_AND_CITATION_PASS_EMPIRICAL_EDGE7_BLOCKED`。它表示协议、指标、引用完整性和五场请求编译已通过，不表示强模型难度目标已经实测，也不授权外部请求。

## 为什么旧行为不合理

Edge6的`match_0066`响应完整返回5题、JSON结构正确且未截断，但L3使用了一个形状正确、实际不存在的`s_<24hex>`引用。旧规范化器因此把整批标成`INVALID_OUTPUT`，同时丢掉另外4题的可评分事实和证据结果。

这混淆了两个不同能力：

1. 传输与协议服从：能否返回完整、可解析、属于当前请求的问题集合；
2. 证据 grounding：能否从长文本精确选择并复制真实存在的证据节点。

模型编造一个看似合法的引用，本身正是数据集要测的证据错误，不应被包装成网络或JSON失败；但也不能自动纠正，否则会替模型完成精确grounding任务。

## Edge7冻结规则

只有同时满足以下条件的未知节点才进入语义计分：

- 任务是`r26_decision`；
- 证据角色协议是`edge_derived_v3`；
- 响应包协议是`request_bound_v2`；
- 节点匹配`^s_[0-9a-f]{24}$`；
- 节点不在同一场公开`documents[].spans[].span_id`集合中。

处理方式：

- 原字符串逐字保留；
- 正证据或排除证据中的未知引用按假阳性处理；
- 接触未知节点的类型边按假阳性处理，遗漏的金标边仍是假阴性；
- 受影响问题的证据集合精确匹配和完整链精确匹配失败；
- 该问题的事实、状态和反事实字段照常计分；
- 同一批其他问题照常计分；
- 不模糊匹配、不删前缀、不替换、不静默忽略。

畸形节点、外来问题节点、外来决策节点、重复或缺失问题、非法关系、非法结构、JSON解析失败、截断、超时与provider错误仍属于协议或传输失败。

## 指标

主事实和证据指标不变。R26.16新增以下诊断，并必须同时报告原始计数与分母：

- 未知span的不同ID数；
- 未知span在正/排除列表中的引用次数；
- 接触未知span的预测边数；
- 含未知证据的问题数与问题率；
- 未知span引用率；
- 未知边率；
- 上述错误的L1–L5分解。

这些指标只描述证据grounding或抄录失败，不能替代事实宏准确率、信息字段指标、span/edge F1、内容依赖指标和事实+完整链exact。

## 数据稳定性检查

本地引用审计结果：

- 20场、100题；
- 28,574个公开span ID；
- 1,528个唯一金标引用span；
- 550,080个金标ID的单十六进制字符替换；
- 替换后与真实公开ID碰撞数为0；
- 金标ID到同场其他公开ID的最小Hamming距离为15；
- 所有金标span与edge端点均存在于对应公开材料；
- 所有公开ID形状中立且场内唯一。

L1–L5平均引用span数为10.8、16.2、18.8、21.6、24.4；平均引用字符数为280.8、421.2、488.8、561.6、634.4。引用负担整体随等级增加，因此不会通过短别名、schema枚举、删文档、删干扰项或缩短链条来掩盖模型抄录错误。

## 历史结果与未来请求

Edge6历史结果保持`INVALID_OUTPUT`，不追溯升级为官方分数。保存的原始响应仅做`COUNTERFACTUAL_POLICY_DIAGNOSTIC_ONLY`回放，用于验证新归因路径；不得与未来Edge7结果合并或写成正式模型成绩。

未来五场哨兵必须使用`r26_16_glm53_flash_uniform_sentinel5_edge7`新run ID和新请求哈希。阻断配置规定每场5题一批、零重试、失败即停、结构化输出、20,480输出token上限和显式授权。零请求预检的保守结果是0.9699元、最大上下文占用25.5625%、最小oracle输出余量1.547倍。

在用户对该精确配置重新明确授权前，不允许调用provider。即便五场完成，也只能筛查协议与大效应；论文级五层难度结论仍需要预注册Pilot20、至少两个强模型家族、匹配锚点分析和不确定性区间。

## Edge7实际运行结果

用户随后明确授权冻结的五场配置。`match_0021`和`match_0066`均只请求一次并完整返回5题；两批均为`finish_reason=stop`，没有截断、验证错误或未知证据警告。第三场`match_0067`在3.83秒后返回HTTP 503和provider code 50508，未返回目标、token或可计费用量。运行器按合同立即停止且没有重试，`match_0162`和`match_0220`没有提交。

实际记录费用为0.227339元。两个成功场次共10题：事实整记录宏准确率20%，字段准确率75.83%，信息字段准确率67.78%，正证据span F1 55.80%，排除证据F1 70.27%，类型边F1 47.47%，内容依赖边F1 19.51%，事实加完整证据链exact为0。两场均没有未知证据引用。

这些指标证明任务能区分字段局部正确、整记录正确、证据选择和图构造，但只覆盖原计划的40%，匹配锚点矩阵不完整，不能用于确认最终五场难度、65%目标或相邻8个百分点差。

为防止部分结果被误报，分析报告现在必须在指标前显示计划、已尝试、可评分场数、按原计划覆盖率和停止原因。三场可用性续跑先冻结为`sentinel5_collection`，只含失败/未尝试场次，不重复两场成功请求，请求哈希与原预检一致；用户随后对此精确续跑另行授权。

续跑中`match_0067`和`match_0162`各一次完整成功。`match_0220`的响应完整、`finish_reason=stop`且没有截断，但五个对象都使用同一个目标ID，造成四个重复ID错误及其余四题缺失；因此整场为`INVALID_OUTPUT`。冻结协议禁止自动改ID、拆取唯一一题、把缺题记作事实零分或为了改善覆盖率自动重试。

两段运行合并后，5/5个预定场次均尝试过，共6次provider请求、5个计费响应；4/5场和20/25题协议完整，总记录费用0.635277元。四场子集的事实整记录宏准确率20%，冻结的12字段主指标71.67%，信息字段准确率62.22%，信息字段值平衡准确率38.83%，正证据span F1 54.23%，排除证据F1 64.71%，类型边F1 41.69%，内容依赖边F1 17.39%，事实加完整证据链exact为0；未知证据引用率仍为0。

字段主指标的四场描述值高于冻结45%–65%目标区间。等级字段准确率为100%/64.58%/75%/70.83%/47.92%，L2到L3倒置10.42个百分点；虽然四场子集有三个正向相邻下降且平均下降13.02个百分点，它不是完整Sentinel5，不能通过正式门禁，也不能触发针对文本难度的修改或220场扩展。有效结论仅是：局部字段提取仍偏容易，而整记录和证据链联合构造明显更难；五级稳定性仍未建立。

## 可复现入口

```powershell
$env:PYTHONPATH = 'src'
python -m vett_r26.citation_stability_audit --release r26_15_content_dependency_candidate_v3 --contract design\r26_16_citation_stability_audit_contract.json --output analysis\r26_16_citation_stability
python -m vett_r26.unknown_evidence_replay --release r26_15_content_dependency_candidate_v3 --run eval_runs\r26_15_glm53_flash_span_id_gate\r26_15_glm53_flash_match0066_span_id_gate_edge6 --instance-id match_0066 --output analysis\r26_16_unknown_evidence_replay
python -m vett_r26.sentinel_preflight --config eval_configs\r26_16_glm53_flash_uniform_sentinel5_edge7_blocked.json --contract design\r26_16_sentinel5_request_contract.json --output analysis\r26_16_protocol_and_citation\SENTINEL5_ZERO_REQUEST_PREFLIGHT.json
python -m vett_r26.protocol_citation_admission --release r26_15_content_dependency_candidate_v3 --prereg design\r26_16_unknown_evidence_preregistration.json --metric-addendum design\r26_16_unknown_evidence_metric_addendum.json --citation-audit analysis\r26_16_citation_stability\CITATION_STABILITY_AUDIT.json --replay analysis\r26_16_unknown_evidence_replay\COUNTERFACTUAL_EDGE7_REPLAY.json --preflight analysis\r26_16_protocol_and_citation\SENTINEL5_ZERO_REQUEST_PREFLIGHT.json --blocked-config eval_configs\r26_16_glm53_flash_uniform_sentinel5_edge7_blocked.json --output analysis\r26_16_protocol_and_citation\ADMISSION.json
python -m vett_r26.edge7_sentinel_cohort --release r26_15_content_dependency_candidate_v3 --parent-run eval_runs\r26_16_glm53_flash_uniform_sentinel5_edge7\r26_16_glm53_flash_uniform_sentinel5_edge7 --continuation-run eval_runs\r26_16_edge7_cont3\r26_16_edge7_cont3 --original-preflight analysis\r26_16_protocol_and_citation\SENTINEL5_ZERO_REQUEST_PREFLIGHT.json --output analysis\r26_16_edge7_sentinel5_cohort
```
