# R26.18 集合语义与输出服从性双轨协议

## 为什么需要重构

R26.17已经用`exact_target_map_v3`把每个题目ID变成必需对象键，成功消除了“重复一个题目、漏掉其余题目”的身份覆盖问题。但新的五场尝试显示，SiliconFlow返回的结构化输出没有可靠执行数组上的`uniqueItems=true`：`match_0021`完整返回5/5题、正常停止且没有截断，却在两个答案中重复完全相同的证据边。

把整场判为不可评分虽然严格，却同时丢掉了完整事实答案和本来具有集合语义的证据图测量。反过来，静默去重又会掩盖模型没有遵守输出要求。R26.18因此采用双轨报告，而不是在二者之间任选其一。

## 冻结的双轨规则

第一轨是语义质量。`evidence_spans`按精确span ID集合评分，`evidence_edges`按精确`(source_id, relation, target_id)`三元组集合评分。同一题内完全相同的成员只保留首次出现，重复副本不获得额外信用。

第二轨是输出服从性。任何被规范化的重复都会使对应题目成为nonconformant，并报告受影响题数、题级服从率、重复组、冗余副本、最大重复次数和字段来源。新增`evidence_chain_conformant_joint_exact`与`factual_evidence_chain_conformant_joint_exact`，只有语义正确且没有重复的题目才能命中。

下列情况仍然硬失败，不能被集合规范化修复：非法或截断JSON、缺题/多题/冲突身份、缺少必需字段、错误字段类型、非法标准值、畸形证据ID、外来query或decision节点、非法关系、原始数组超过冻结上限，以及provider/传输错误。数组上限在去重前检查，所以不能靠重复项绕过上限。未知但形状合法的span仍按R26.16作为语义假阳性，不会被删除。

## 历史兼容边界

- `strict_unique_v1`仍是旧运行默认值；重复证据继续导致`INVALID_OUTPUT`。
- `canonical_set_v2`只能与`r26_decision + edge_derived_v3 + exact_target_map_v3 + semantic_false_positive_v2`组合。
- 新协议使用`R26-C3-EDGE-9-CANONICAL-SET-CONFORMANCE`合同和新请求哈希。
- R26.17已付费响应保持`INVALID_OUTPUT`，后验回放永远是非官方诊断。
- 新旧协议运行不能合并成一个正式Sentinel5。

## 本地验证

故障注入同时覆盖重复span、重复边、原始49边超限和非法协议组合：完全相同的重复项被稳定规范化并生成服从性告警；49边仍硬失败；旧严格协议仍拒绝重复。命令适配器端到端测试证明，含重复的完整输出可以保持`status=OK`参与语义评分，同时写入`conformance_status=FAIL_CANONICALIZED`。干净Oracle保持100%语义分数和`conformance_status=PASS`。

对已保存的`match_0021`响应进行零请求回放后：

- 五题全部可按集合语义评分；去重前后完整评分字典逐项一致。
- 2/5题不服从，题级服从率60%。
- 共7个重复组、31个冗余副本，最大同边重复17次。
- 非官方诊断：事实字段71.67%、信息字段62.22%、值平衡信息字段51.72%、整记录20%、span F1 44.14%、排除证据F1 12.50%、typed-edge F1 27.95%、内容依赖edge F1 11.76%、事实+完整链exact 0%。
- 一题仍含未知证据引用；这些引用保留为语义假阳性，没有被规范化删除。

这些数值只证明评分归因可用，不能追溯成为正式模型成绩。

## 五场零请求预检

冻结的未来配置仍为原五场和同一匹配锚点Latin square，但使用全新run/cohort ID。25题Oracle、未知引用故障、重复集合故障、精确题目键、关系词表、上下文和输出余量全部通过。最大上下文利用率上界26.4562%，最小Oracle输出余量1.551163倍，零缓存保守估价1.0074元，低于1.4元硬上限。

当前准入状态是`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`。R26.18没有发起provider请求，`execution_authorized=false`。R26.15文本、题目、事实、金标证据和难度向量全部不变；本地回放不足以授权数据加难。

## 复现

```powershell
$env:PYTHONPATH = 'src'
python -m vett_r26.canonical_set_replay --release r26_15_content_dependency_candidate_v3 --source-run eval_runs\r26_17_exact_map_sentinel5_continuation\r26_17_exact_map_sentinel5_continuation --instance-id match_0021 --output analysis\r26_18_canonical_set_replay_match0021
python -m vett_r26.sentinel_preflight --config eval_configs\r26_18_glm53_canonical_set_sentinel5_blocked.json --contract design\r26_18_canonical_set_request_contract.json --output analysis\r26_18_canonical_set\ZERO_REQUEST_PREFLIGHT.json
python -m vett_r26.canonical_set_admission --preflight analysis\r26_18_canonical_set\ZERO_REQUEST_PREFLIGHT.json --replay analysis\r26_18_canonical_set_replay_match0021\CANONICAL_SET_REPLAY.json --blocked-config eval_configs\r26_18_glm53_canonical_set_sentinel5_blocked.json --metric-addendum design\r26_18_canonical_set_metric_addendum.json --request-contract design\r26_18_canonical_set_request_contract.json --output analysis\r26_18_canonical_set\ADMISSION.json
```
