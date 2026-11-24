
import json, sqlite3, subprocess, time
PY = r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
for i in range(90):
    c=con()
    b9=c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B009'").fetchone()
    b10=c.execute("SELECT batch_id FROM batches WHERE batch_id='B010'").fetchone()
    c.close()
    if b9 and b9["status"]=="scored" and b10: break
    time.sleep(2)
c=con()
print("B009", dict(c.execute("SELECT batch_id,template,status,accuracy FROM batches WHERE batch_id='B009'").fetchone()))
try:
    sc=json.load(open("reports/B009_SCORE.json",encoding="utf-8"))
    print("B009 cells", sc["cells_correct"], "/", sc["cells_total"])
except Exception as e: print("B009 score missing", e)
b10=c.execute("SELECT batch_id,template,status FROM batches WHERE batch_id='B010'").fetchone()
print("B010", dict(b10) if b10 else None)
print("DECISION", json.dumps([dict(x) for x in c.execute("SELECT rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id DESC LIMIT 1")], ensure_ascii=False))
before_results=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
before_queue={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
c.close()
r=subprocess.run([PY,"vettctl.py","stop"],capture_output=True,text=True)
time.sleep(10)
c=con()
after_results=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
after_queue={r2["status"]:r2["n"] for r2 in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
meta={k:c.execute("SELECT value FROM meta WHERE key=?",(k,)).fetchone()["value"] for k in ("state","supervisor_pid","worker_pid","external_api_calls")}
next_tasks=[dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status='queued' ORDER BY batch_id,rowid LIMIT 20")]
c.close()
print("STOP", (r.stdout or "").strip().replace("\n"," "))
print("VERDICT", json.dumps({
  "before_results":before_results,"after_results":after_results,"no_new_results":before_results==after_results,
  "before_queue":before_queue,"after_queue":after_queue,"meta":meta,"next_tasks":next_tasks
}, ensure_ascii=False, indent=1))
