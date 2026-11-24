# R26.18 阶段1零请求准备与优化审计报告

## 结论

本轮完成了计划书允许的全部阶段1本地准备，结果为：

`STAGE1_ZERO_REQUEST_READINESS_PASS_EXTERNAL_EXECUTION_BLOCKED`

数据内容没有被改写。原因不是工作未开始，而是冻结调整权限要求：完整 Sentinel5 之前不得调难，Sentinel5 自身也只能选择待 Pilot20 验证的假设。当前机器可读准入仍为：

`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`

## 已完成的优化

本轮优化的是执行与治理闭环，而不是绕过证据门直接改题：

- 建立独立阶段1输入manifest和关键工件哈希；
- 复核R26.15逐文件完整性，无缺失、无新增、无字节变化；
- 重跑全量本地回归测试；
- 重建零请求预检和本地准入，并验证与冻结工件逐字节一致；
- 固化双轴项目状态，区分准入状态与生命周期准备状态；
- 建立配置白名单diff、一次性授权模板和暴露账本；
- 建立Sentinel四轨分析模板与问题处置手册；
- 明确shadow候选的触发门、禁止动作和异常重入路径。

## 数据完整性

| 项目 | 结果 |
| --- | --- |
| 候选 | `r26_15_content_dependency_candidate_v3` |
| 文件数 | 165 |
| 总字节 | 93,346,177 |
| 阶段0聚合SHA-256 | `2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417` |
| 缺失文件 | 0 |
| 新增文件 | 0 |
| 字节/哈希变化文件 | 0 |
| 状态 | `PASS_NO_DRIFT` |

逐文件比较见 `CANDIDATE_INTEGRITY_COMPARISON.json`。

## 回归测试

```text
Ran 202 tests in 176.626s
OK
```

测试日志SHA-256：

`5639142973816f73e8a7304bc22d56b99c0c56208b97a1f8d1b414d165a52100`

## 零请求预检

| 项目 | 结果 |
| --- | --- |
| 状态 | `REQUEST_READY_BLOCKED_BY_AUTHORIZATION` |
| 场次/题目 | 5 / 25 |
| 错误 | 0 |
| provider请求 | 0 |
| `execution_authorized` | `false` |
| 冻结合同的零缓存估算 | 1.0074 CNY |
| 配置估算上限 | 1.4 CNY |
| 最大上下文利用率上界 | 26.4562% |
| 最小Oracle输出余量 | 1.551163倍 |

新预检SHA-256为 `538b25f91fdc1bcbdea6379323f056f9238b5f8e29db195f2ed1e6c7698d0f81`，与冻结预检逐字节一致。

注意：`pricing_matches_verified_contract=true` 只说明配置与2026-10-19冻结合同一致，不等于2026-11-12官方价格仍已复核。真正执行前必须重新核实模型可用性、官方价格、上下文和接口兼容性；变化时必须新建合同并重新预检。

## 本地准入

| 项目 | 结果 |
| --- | --- |
| 状态 | `LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED` |
| provider请求 | 0 |
| 外部执行授权 | `false` |
| 数据变更授权 | `false` |
| 新准入SHA-256 | `ad3bf09453b262a90214b9287faeefcf84ba9f8591ae5dbb41d3e4088bef340c` |

新准入与冻结准入逐字节一致。

## 授权和费用审计

- 未调用provider；
- 未读取或展示API密钥；
- 实际费用为0；
- 未创建授权配置；
- 阻断配置没有变化，SHA-256仍为 `bf0384875b8c4cf7b3599dc630a22512109af63e9a8ab234d25e13755e0ae01b`；
- 没有授权重试、Pilot20、第二模型、shadow、220场或发布。

## 难度与准确度的当前结论

### 可以声明

- R26.15字节冻结且本轮无漂移；
- R26.18 `canonical_set_v2` 本地协议门通过；
- 五场请求在本地可以构造、哈希唯一、容量与冻结成本合同门通过；
- 阶段1的文档、审计和分析框架已经就绪。

### 不能声明

- 不能声明R26.15在强模型上达到45%–65%目标区间；
- 不能声明L1–L5相邻下降稳定；
- 不能声明数据已经完成难度优化；
- 不能从历史不完整/无效输出拼接正式Sentinel；
- 不能建立、晋升或外测shadow；
- 不能启动Pilot20、220场物化或发布。

## 后续合法决策路径

1. 用户若不授权外部执行：停留在当前状态，只能继续本地审计、文档与人工规范准备。
2. 用户若单独授权冻结Sentinel5：先完成官方模型/价格/上下文/API核实，再生成白名单授权副本和全新空目录；任何非白名单diff均阻断。
3. Sentinel5完整有效后：先冻结四轨报告，再登记一个主假设；不得改数据。
4. 第一强模型家族Pilot20另行授权。只有同一预注册机制至少影响4题、至少2锚点、全部batch为OK且锚点平衡时，才可建立不可晋升的shadow。
5. shadow晋升还需第二强模型家族在未改R26.15上同向确认、无禁止性地板效应并通过fresh shadow Sentinel；每一阶段独立授权。

## 本轮工件

- `INPUT_MANIFEST.json`：输入身份与哈希；
- `CANDIDATE_INTEGRITY_COMPARISON.json`：逐文件冻结比较；
- `TEST_LOG.txt`：202项测试日志；
- `ZERO_REQUEST_PREFLIGHT.json`：零请求预检；
- `ADMISSION.json`：本地准入；
- `PROJECT_STATE.json`：双轴项目状态与授权位；
- `CONFIG_DIFF.json`：当前未创建授权配置及未来白名单；
- `EXPOSURE_LEDGER.jsonl`：本地零请求暴露记录；
- `SCOPE_AND_AUTHORIZATION.md`：本轮范围边界；
- `AUTHORIZATION_TEMPLATE.md`：一次性Sentinel授权模板；
- `SENTINEL5_ANALYSIS_TEMPLATE.md`：四轨冻结分析模板；
- `ISSUE_RESPONSE_PLAYBOOK.md`：异常与优化重入手册；
- `HANDOFF_UPDATE.md`：后续模型交接。

## 唯一下一决策点

是否由用户提供一份完整的一次性R26.18 Sentinel5 provider/费用授权。没有该授权时，项目应保持当前阻断状态。

