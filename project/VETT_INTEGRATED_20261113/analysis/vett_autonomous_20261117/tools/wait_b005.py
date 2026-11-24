
import json, sqlite3, time
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
for i in range(150):
    c=con(); b=c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B005'").fetchone(); c.close()
    if b and b["status"]=="scored": break
    time.sleep(2)
c=con()
print("B005", dict(c.execute("SELECT batch_id,status,accuracy FROM batches WHERE batch_id='B005'").fetchone()))
sc=json.load(open("reports/B005_SCORE.json",encoding="utf-8"))
print("B005 accuracy", sc["accuracy"], "by_cond", {k:v["accuracy"] for k,v in sc["by_condition"].items()}, "failing", sc["failing_positions"])
print("DECISION", json.dumps([dict(x) for x in c.execute("SELECT rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id DESC LIMIT 1")], ensure_ascii=False))
print("NEXT", json.dumps([dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status IN ('queued','claimed') ORDER BY batch_id,rowid LIMIT 12")], ensure_ascii=False))
