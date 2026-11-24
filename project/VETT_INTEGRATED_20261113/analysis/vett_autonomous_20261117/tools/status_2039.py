
import sqlite3, json
from pathlib import Path
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
q={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
rows=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
att=c.execute("SELECT COUNT(*) n FROM attempts").fetchone()["n"]
unc=c.execute("SELECT COUNT(*) n FROM attempts WHERE uncertain=1").fetchone()["n"]
txt = "# 当前状态快照（2026-11-19 20:39）\n\n"
txt += "- workflow: stopped；stop_reason: user_stop；停止时间 16:14:21\n"
txt += "- 最后结果：2026-11-19T16:11:36+08:00\n"
txt += "- 本段：15:42:22 → 16:14:21，约 32 分钟\n"
txt += "- results: " + str(rows) + "；attempts: " + str(att) + "；uncertain: " + str(unc) + "\n"
txt += "- queue: " + json.dumps(q) + "\n"
txt += "- batches: " + str(c.execute("SELECT COUNT(*) n FROM batches").fetchone()["n"]) + "；probe_cursor: " + c.execute("SELECT value FROM meta WHERE key='probe_cursor'").fetchone()["value"] + "\n"
txt += "- external API: 0；supervisor/worker 均无活动进程\n"
txt += "- 失败：2 条 B165 match_0116（llama/gemma），错误 database is locked；对应 attempts 为 uncertain\n"
txt += "- 因 user_stop，auto_recover 不会自动覆盖；需要显式 start 才恢复派发\n"
Path("reports/STATUS_20261119_2039.md").write_text(txt, encoding="utf-8")
print(txt)
