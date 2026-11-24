# 故障与隔离：核心批次 innings 解析错误

- 时间：2026-11-21 21:58。
- 现象：attribution_followup/samples.json 的 innings 字段是字符串 inn1/inn2；night_build 第一版用 1 覆盖，导致 B214–B220 的提示写成 Innings: 1。
- 影响：B213（match_0003，本为 inn1）不受影响；B214–B220 已删除并入隔离目录 quarantine/（B214 已完成 5 条结果，一并作废）。
- 处理：暂停派发、删除受影响任务/结果/批次、修复解析后用新批次号重建。
- 保留：B213 的 18 条结果。
