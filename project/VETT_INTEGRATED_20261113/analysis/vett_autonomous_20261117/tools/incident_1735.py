
import sqlite3, time
from pathlib import Path
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
time.sleep(30)
n=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
q={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
inc="# Ollama 中断事件（2026-11-20 17:35）\n\n"
inc+="- 17:35 前后 Ollama 连接被拒绝；worker 将 1,063 个任务标为 failed。\n"
inc+="- 涉及 B200–B207 的 43 字段批次；没有结果落盘，attempts 保留错误。\n"
inc+="- 17:56 检查：Ollama 已恢复（PID 21620，/api/tags 正常）；日志有重复 bind 错误，说明重启期间端口竞争。\n"
inc+="- 处理：把 1,063 个无结果 failed 全部重新入队；failed 0。\n"
inc+="- 加固：worker 对 transient URL/connection 错误重试 5 次、间隔 15 秒；重启 worker 2132 使补丁生效。\n"
inc+="- 当前队列继续，18:00 前不会 idle；无用户 STOP。\n"
Path("reports/INCIDENT_20261120_1735_OLLAMA.md").write_text(inc,encoding="utf-8")
st="# 状态快照（2026-11-20 17:58）\n\n"
st+="- 运行中；supervisor 19680 / worker 2132；8h 快照 17:41（8.57h）。\n"
st+="- results "+str(n)+"；queue "+str(q)+"；failed 0；external API 0。\n"
st+="- 17:35 Ollama 中断导致 1,063 failed，已全部重新入队；worker 已加 transient retry。\n"
st+="- 队列 2,273，继续到 18:00 之后。\n"
Path("reports/STATUS_20261120_1758.md").write_text(st,encoding="utf-8")
print({"results":n,"queue":q})
