# R26.18 阶段1准备范围与授权边界

## 本轮授权

本轮只授权本地读取、哈希、测试、零请求预检、准入复验、审计记录和文档模板准备。

## 明确未授权

- provider/API 请求；
- 读取、打印、复制或验证 API 密钥；
- 任何费用；
- 修改或覆盖 `r26_15_content_dependency_candidate_v3`；
- 重新生成 220 场；
- Sentinel5、自动重试、Pilot20、第二模型、shadow 外测或自动扩测；
- 发布、公开上传或外部分发。

## 本轮实际动作

1. 对冻结候选逐文件与阶段0基线比较；
2. 运行 202 项本地回归测试；
3. 使用阻断配置生成零请求预检；
4. 使用本地回放工件生成本地准入；
5. 建立项目状态、配置差异、暴露账本、分析模板、异常手册与交接报告。

## 状态解释

`STAGE1_ZERO_REQUEST_READINESS_PASS` 只表示阶段1的本地前置准备通过，不表示 Sentinel5 已获授权或已经执行。机器可读准入状态仍由 `ADMISSION.json` 给出：

`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`

