
import sqlite3
from pathlib import Path
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
n=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
q={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
doc="# 执行到 18:00 的排程（2026-11-20）\n\n"
doc+="- 目标：至少持续到 18:00，不因报告、8h 或 08:00 停止。\n"
doc+="- 队列：B200–B210，共约 1,980 个新任务；当前 results "+str(n)+"，queue "+str(q)+"。\n"
doc+="- T4 剩余 O：708（B200–B203）；E：198（B204–B205）；OI：156（B206）；已用单元 E/OI：144/93（B207–B208）。\n"
doc+="- B209 跨局缓冲：87；B210 E 字段探针：594。\n"
doc+="- 预计：全表约 4.4 条/分钟，短任务更快；总时约 5–6.5 小时，预计 18:30–20:00 完成。\n"
doc+="- 若提前跑完，B209/B210 提供额外缓冲；合法队列用尽才进入 idle。\n"
doc+="- 8 小时节点 17:07、明日 08:00 阶段报告只写快照，不停止任务。\n"
doc+="- 外部 API 0；不新增下载/升级；held-out 不碰。\n"
Path("reports/RUN_UNTIL_1800_20261120.md").write_text(doc,encoding="utf-8")
print(doc)
