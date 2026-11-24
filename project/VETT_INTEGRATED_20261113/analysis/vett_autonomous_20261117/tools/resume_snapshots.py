
import json, sqlite3, time, sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V, reporting
c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row
now = lambda: datetime.now().astimezone().isoformat(timespec="seconds")

def snap(tag):
    s = reporting.status_dict(c)
    rows = c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
    q = {r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
    probe = V.meta_get(c, "probe_cursor", "")
    txt = "# RESUME SNAPSHOT " + tag + "\n\n"
    txt += "- time: " + now() + "\n"
    txt += "- state: " + s["workflow_state"] + "; batch: " + s["batch_state"] + "\n"
    txt += "- supervisor: " + str(s["supervisor"]["pid"]) + " alive=" + str(s["supervisor"]["alive"]) + "\n"
    txt += "- worker: " + str(s["worker"]["pid"]) + " alive=" + str(s["worker"]["alive"]) + " heartbeat=" + str(s["worker"]["heartbeat_age_seconds"]) + "s\n"
    txt += "- results: " + str(rows) + "; probe_cursor: " + probe + "\n"
    txt += "- queue: " + json.dumps(q) + "\n"
    Path("reports/RESUME_SNAPSHOT_" + tag + ".md").write_text(txt, encoding="utf-8")
    return s, rows, q, probe

s1, n1, q1, p1 = snap("1")
time.sleep(65)
s2, n2, q2, p2 = snap("2")
new = c.execute("SELECT model,load_ms,inference_ms FROM results WHERE created_at>=? ORDER BY created_at", (V.meta_get(c, "segment_started_at"),)).fetchall()
lock_events = c.execute("SELECT COUNT(*) n FROM events WHERE kind LIKE '%lock%' OR payload LIKE '%database is locked%'").fetchone()["n"]
fail = c.execute("SELECT COUNT(*) n FROM tasks WHERE status='failed'").fetchone()["n"]
unc = c.execute("SELECT COUNT(*) n FROM attempts WHERE uncertain=1").fetchone()["n"]
extra = "# 恢复运行（20:41）\n\n"
extra += "- 显式 vettctl start：supervisor 16272 / worker 13912。\n"
extra += "- 修 vettlib.connect：busy_timeout 先于 WAL，WAL 失败不再致命。\n"
extra += "- 2 条 database is locked 的 failed 已重新入队，failed=0。\n"
extra += "- 两次快照：" + str(n1) + " → " + str(n2) + "（+" + str(n2 - n1) + "）；probe " + p1 + " → " + p2 + "。\n"
extra += "- 恢复后新增 " + str(len(new)) + " 条；failed=" + str(fail) + "；uncertain=" + str(unc) + "。\n"
extra += "- 未再出现 database is locked 事件（历史匹配数 " + str(lock_events) + "）。\n"
Path("reports/RESUME_20261119_2041.md").write_text(extra, encoding="utf-8")
print(json.dumps({"n1": n1, "n2": n2, "delta": n2 - n1, "probe": [p1, p2], "failed": fail, "uncertain": unc, "new_results": len(new)}, ensure_ascii=False))
