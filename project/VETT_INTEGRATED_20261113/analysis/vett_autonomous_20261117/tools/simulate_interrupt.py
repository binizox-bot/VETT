
import json, sqlite3, subprocess, time, sys
DB = "state/workflow.db"
def con():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
killed = None
pre = None
for i in range(240):
    c = con()
    batches = c.execute("SELECT batch_id, seq, template, status, accuracy FROM batches ORDER BY seq").fetchall()
    second = [b for b in batches if b["seq"] == 2]
    if second:
        b = second[0]
        rows = c.execute("SELECT task_key, model, cond, status, claimed_by, attempts FROM tasks WHERE batch_id=? AND status='claimed'", (b["batch_id"],)).fetchall()
        if rows:
            r = rows[0]
            pre = {"batch": b["batch_id"], "template": b["template"], "task_key": r["task_key"],
                   "model": r["model"], "cond": r["cond"], "claimed_by": r["claimed_by"],
                   "attempts": r["attempts"], "batches": [dict(x) for x in batches]}
            killed = r["claimed_by"]
            break
    c.close()
    time.sleep(1)
if not killed:
    print(json.dumps({"ok": False, "reason": "no claimed B002 task within timeout", "batches": [dict(x) for x in con().execute("SELECT batch_id,status,accuracy FROM batches").fetchall()]}))
    sys.exit(1)
print("PRE_KILL " + json.dumps(pre, ensure_ascii=False))
res = subprocess.run(["taskkill", "/F", "/PID", str(killed)], capture_output=True, text=True)
print("KILL_RC", res.returncode, (res.stdout or "").strip().replace("\n", " | "), (res.stderr or "").strip())
time.sleep(18)
c = con()
print("POST_STATE " + json.dumps({
  "batches": [dict(x) for x in c.execute("SELECT batch_id,seq,template,status,accuracy FROM batches ORDER BY seq")],
  "queue": {r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")},
  "recovered_task": [dict(x) for x in c.execute("SELECT task_key,status,attempts,recoveries,claimed_by FROM tasks WHERE task_key=?", (pre["task_key"],))],
  "events": [dict(x) for x in c.execute("SELECT ts,kind,payload FROM events WHERE kind IN ('worker_died','task_recovered','worker_spawned','worker_started','task_claimed','task_done') ORDER BY id DESC LIMIT 10")],
}, ensure_ascii=False, default=str))
