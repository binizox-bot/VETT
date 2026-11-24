
import json, sqlite3, subprocess, time
PY = r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
r=subprocess.run([PY,"vettctl.py","start"],capture_output=True,text=True)
print("START", (r.stdout or "").strip().replace("\n"," "))
for i in range(120):
    c=con()
    b10=c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B010'").fetchone()
    b11=c.execute("SELECT batch_id,template,status FROM batches WHERE batch_id='B011'").fetchone()
    c.close()
    if b10 and b10["status"]=="scored" and b11: break
    time.sleep(2)
c=con()
print("B010", dict(c.execute("SELECT batch_id,template,status,accuracy FROM batches WHERE batch_id='B010'").fetchone()))
b11=c.execute("SELECT batch_id,template,status FROM batches WHERE batch_id='B011'").fetchone()
print("B011", dict(b11) if b11 else None)
print("DECISION", json.dumps([dict(x) for x in c.execute("SELECT rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id DESC LIMIT 1")],ensure_ascii=False))
c.close()
stop=subprocess.run([PY,"vettctl.py","stop"],capture_output=True,text=True)
print("STOP", (stop.stdout or "").strip().replace("\n"," "))
time.sleep(8)
c=con()
print("FINAL", json.dumps({
 "queue":{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")},
 "next":[dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status='queued' ORDER BY batch_id,rowid LIMIT 12")],
 "meta":{k:c.execute("SELECT value FROM meta WHERE key=?",(k,)).fetchone()["value"] for k in ("state","supervisor_pid","worker_pid","external_api_calls")}
},ensure_ascii=False,indent=1))
