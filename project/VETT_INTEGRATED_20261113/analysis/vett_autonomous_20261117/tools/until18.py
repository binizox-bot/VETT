
import json, sqlite3, time, sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V, reporting
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
now=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
def snap(tag):
    s=reporting.status_dict(c); n=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
    q={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
    Path("reports/UNTIL18_SNAPSHOT_"+tag+".md").write_text(
        "# UNTIL18 SNAPSHOT "+tag+"\n\n- time: "+now()+"\n- state: "+s["workflow_state"]+"\n- supervisor: "+str(s["supervisor"]["pid"])+"\n- worker: "+str(s["worker"]["pid"])+" heartbeat="+str(s["worker"]["heartbeat_age_seconds"])+"s\n- results: "+str(n)+"\n- queue: "+json.dumps(q)+"\n", encoding="utf-8")
    return s,n,q
s1,n1,q1=snap("1")
time.sleep(65)
s2,n2,q2=snap("2")
rows=c.execute("SELECT batch_id,template,COUNT(*) n FROM tasks WHERE status='done' AND batch_id>='B200' GROUP BY batch_id,template ORDER BY batch_id").fetchall()
doc="# 执行到 18:00 的排程（2026-11-20）\n\n"
doc+="- 目标：至少持续到 18:00，不因报告/8h 停。\n"
doc+="- 队列：B200–B210，共 1,980 个新任务。\n"
doc+="- T4 剩余 O：4 批 708；E：2 批 198；OI：1 批 156；已用单元 E/OI：144/93。\n"
doc+="- B209 跨局缓冲：87；B210 E 字段探针：594。\n"
doc+="- 预计：全表约 4.4 条/分钟，短任务更快；总时约 5–6.5 小时，预计 18:30–20:00 之间完成。\n"
doc+="- 8 小时节点 17:07、明日 08:00 阶段报告只写快照，不停止。\n"
doc+="- 外部 API 0；不新增下载/升级；held-out 不碰。\n"
doc+="- 快照："+str(n1)+" → "+str(n2)+"（+"+str(n2-n1)+"）。\n"
Path("reports/RUN_UNTIL_1800_20261120.md").write_text(doc, encoding="utf-8")
print(json.dumps({"n1":n1,"n2":n2,"delta":n2-n1,"queue":q2,"pids":[s2["supervisor"]["pid"],s2["worker"]["pid"]]},ensure_ascii=False))
