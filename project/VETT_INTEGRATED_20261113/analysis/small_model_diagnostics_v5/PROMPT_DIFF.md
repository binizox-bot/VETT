# PROMPT_DIFF：v5 只改两个旧值字段说明

## 变更

- 保留 schema 与 decision 字段。
- 只把 original_bowler_wickets_before 的说明改为 A 的复核前 wicket 数；
  other_bowler_wickets_before 的说明改为 B 的复核前 wicket 数。
- 明确两种通知都回答这两个字段，均取复核生效前的值。
- 其余字段、事件身份、原/终归属、UNKNOWN 规则不变。

## 核对

- 24 条请求正文哈希与 v3 正文一致。
- 只新增字段说明，无答案或示例数字。
- 逐场 A/B 姓名来自题面指定投手。
