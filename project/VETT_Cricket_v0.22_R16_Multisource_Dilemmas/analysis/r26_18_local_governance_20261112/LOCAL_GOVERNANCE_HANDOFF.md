# 本地治理包交接

## 当前对象

- 候选：`r26_15_content_dependency_candidate_v3`
- 聚合SHA-256：`2cb1ea2c62d1b8d57b6c20bbc3c22ed7ad0440ca73f68946d24fcbf0ebab9417`
- 协议：R26.18 `canonical_set_v2`
- 准入：`LOCAL_PROTOCOL_PASS_EXTERNAL_EXECUTION_BLOCKED`

## 必须保留的事实

- 100题Pilot和324条内容依赖边静态闭环；
- 220场流式计划为1,100题、3,564条内容依赖边，尚未物化；
- 内容机会量等级比3.0；
- 省略全部内容边时总体边F1仍为0.93896，但内容边F1和联合链exact均为0；
- 静态结构与Oracle正确性不能替代强模型经验难度；
- 人工规范仍是待批准草案。

## 下一模型动作

先读`GOVERNANCE_CONTINUATION_AUDIT.md`、`RISK_REGISTER.json`和上一阶段`PROJECT_STATE.json`。没有新授权时只做本地工作，不得调用provider、修改数据或物化220场。

