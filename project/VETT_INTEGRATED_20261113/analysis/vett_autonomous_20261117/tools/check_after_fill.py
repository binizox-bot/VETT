
import sqlite3, json
from collections import defaultdict
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
print("BATCHES",[dict(r) for r in c.execute("SELECT batch_id,template,status,accuracy FROM batches ORDER BY seq DESC LIMIT 4")])
print("QUEUE",{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
print("RESULTS",c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"])
print("P_MISSING_TASK",[dict(r) for r in c.execute("SELECT task_key,status,batch_id,model FROM tasks WHERE match='match_0089' AND innings=1 AND field_scope='probe_both'")])
print("TRIAL",[dict(r) for r in c.execute("SELECT r.model,t.field_scope,r.parse_ok,r.correct,r.response_meta_json FROM results r JOIN tasks t USING(task_key) WHERE t.field_scope='probe_wickets_p320'")])
rows=c.execute("SELECT r.match,r.innings,r.model,t.field_scope FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep'").fetchall()
key=defaultdict(set)
for r in rows: key[(r["match"],r["innings"],r["model"])].add(r["field_scope"])
comp=sum(1 for v in key.values() if {"probe_runs","probe_wickets","probe_both"} <= v)
miss=[(k,sorted({"probe_runs","probe_wickets","probe_both"}-v)) for k,v in key.items() if not {"probe_runs","probe_wickets","probe_both"} <= v]
print("P_TRIPLES",{"keys":len(key),"complete":comp,"missing":len(miss),"examples":miss[:3]})
print("PIDS",{k:c.execute("SELECT value FROM meta WHERE key=?",(k,)).fetchone()["value"] for k in ("supervisor_pid","worker_pid","state","probe_cursor")})
