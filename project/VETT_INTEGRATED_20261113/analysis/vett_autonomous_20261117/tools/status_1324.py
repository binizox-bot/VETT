
import sqlite3
from pathlib import Path
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
rows=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
q={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
txt="# 状态快照（2026-11-20 13:24）\n\n"
txt+="- workflow: idle_no_valid_tasks；T4 分支已完成。\n"
txt+="- B198: 180/180 done；B199: 180/180 done。\n"
txt+="- 最后结果：2026-11-20T10:38:58+08:00；之后无新任务。\n"
txt+="- results: "+str(rows)+"；queue: "+str(q)+"；failed: 0；external API: 0。\n"
txt+="- supervisor 19680 / worker 12220 / watchdog 1，均存活；worker 空闲心跳较旧属正常。\n"
txt+="- 本段 8 小时节点：2026-11-20T17:07:00+08:00，只写快照。\n"
txt+="- 下一次小时报：13:41；明日 08:00 阶段报告只写快照。\n"
Path("reports/STATUS_20261120_1324.md").write_text(txt,encoding="utf-8")
print(txt)
