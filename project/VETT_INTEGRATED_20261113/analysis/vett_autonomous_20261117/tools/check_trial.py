
import sqlite3, json, time
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
time.sleep(40)
print("BATCHES",[dict(r) for r in c.execute("SELECT batch_id,template,status,accuracy FROM batches ORDER BY seq DESC LIMIT 4")])
print("QUEUE",{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
print("RESULTS",c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"])
tr=c.execute("SELECT r.match,r.model,t.field_scope,r.parse_ok,r.correct,r.response_meta_json,r.parsed_json FROM results r JOIN tasks t USING(task_key) WHERE t.field_scope='probe_wickets_p320'").fetchall()
print("TRIAL",[dict(x) for x in tr])
rows=c.execute("SELECT r.match,r.innings,r.model,t.field_scope FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep'").fetchall()
key={}
for r in rows: key.setdefault((r["match"],r["innings"],r["model"]),set()).add(r["field_scope"])
comp=sum(1 for v in key.values() if {"probe_runs","probe_wickets","probe_both"}<=v)
print("P_TRIPLES",{"keys":len(key),"complete":comp,"missing":len(key)-comp})
print("PIDS",{k:c.execute("SELECT value FROM meta WHERE key=?",(k,)).fetchone()["value"] for k in ("state","supervisor_pid","worker_pid","probe_cursor")})
