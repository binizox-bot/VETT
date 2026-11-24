# 事故：单字段抽取输出 schema 错误

- 时间：2026-11-22 08:02。
- 现象：B251/B252 的 prompt 写“Field: - Evan Clarke_wickets”，模型返回 {"field": "Evan Clarke_wickets"}，而不是 {"Evan Clarke_wickets": 3}。
- 影响：480+240 条单字段结果不能用于能力判断；已从 MORNING_ACCEPTANCE 的能力结论中排除。
- 处理：不重跑，不把 0/3 当作模型失败；保留原始输出与任务 ID。若下轮需要，改 prompt 为“返回 {<字段id>: <整数>}”并新建版本。
