# Ollama 中断事件（2026-11-20 17:35）

- 17:35 前后 Ollama 连接被拒绝；worker 将 1,063 个任务标为 failed。
- 涉及 B200–B207 的 43 字段批次；没有结果落盘，attempts 保留错误。
- 17:56 检查：Ollama 已恢复（PID 21620，/api/tags 正常）；日志有重复 bind 错误，说明重启期间端口竞争。
- 处理：把 1,063 个无结果 failed 全部重新入队；failed 0。
- 加固：worker 对 transient URL/connection 错误重试 5 次、间隔 15 秒；重启 worker 2132 使补丁生效。
- 当前队列继续，18:00 前不会 idle；无用户 STOP。
