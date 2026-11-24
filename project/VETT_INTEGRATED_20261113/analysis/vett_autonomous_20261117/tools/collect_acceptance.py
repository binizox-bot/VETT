
import json, sqlite3
from pathlib import Path
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
c=con()
batches=[]
for b in c.execute("SELECT * FROM batches ORDER BY seq"):
    sc=json.loads(b["score_json"] or "{}")
    design=json.loads(b["design_json"] or "{}")
    n=c.execute("SELECT COUNT(*) n FROM tasks WHERE batch_id=?",(b["batch_id"],)).fetchone()["n"]
    batches.append({"batch_id":b["batch_id"],"seq":b["seq"],"template":b["template"],"status":b["status"],
                    "accuracy":b["accuracy"],"tasks":n,"conditions":design.get("conditions"),
                    "positions":design.get("positions"),"cells":[sc.get("cells_correct"),sc.get("cells_total")],
                    "raw_path":sc.get("raw_path"),"hypothesis":b["hypothesis"],"rationale":b["rationale"]})
decisions=[dict(x) for x in c.execute("SELECT batch_id,rule_id,action,next_batch_id,rationale,created_at FROM decisions ORDER BY id")]
rec=[dict(x) for x in c.execute("SELECT ts,kind,payload FROM events WHERE kind IN ('worker_died','task_recovered','worker_spawned','worker_started','recovered_with_existing_result','worker_hung_killed') ORDER BY id")]
stop=[dict(x) for x in c.execute("SELECT ts,kind,payload FROM events WHERE kind IN ('stopped_by_user','start_requested','supervisor_started','supervisor_stopped') ORDER BY id")]
next_tasks=[dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status='queued' ORDER BY batch_id,rowid LIMIT 20")]
meta={k:c.execute("SELECT value FROM meta WHERE key=?",(k,)).fetchone()["value"] for k in ("state","external_api_calls","worker_restarts","method_version","last_status_at","last_snapshot_at")}
queue={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
c.close()
data={"generated_at":__import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
      "meta":meta,"queue":queue,"batches":batches,"decisions":decisions,
      "recovery_events":rec,"lifecycle_events":stop,"next_tasks":next_tasks}
Path("reports/ACCEPTANCE_DATA.json").write_text(json.dumps(data,ensure_ascii=False,indent=1),encoding="utf-8")
print(json.dumps({"batches":len(batches),"scored":sum(1 for b in batches if b["status"]=="scored"),
                  "next":len(next_tasks),"queue":queue,"recovery":len(rec),"decisions":len(decisions)},ensure_ascii=False))
for b in batches:
    print(b["batch_id"],b["template"],b["status"],b["accuracy"],b["cells"],b["conditions"],[p["match"] for p in (b["positions"] or [])])
