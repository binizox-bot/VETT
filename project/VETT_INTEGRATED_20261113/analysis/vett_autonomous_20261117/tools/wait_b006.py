
import json, sqlite3, time
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
for i in range(180):
    c=con(); b=c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B006'").fetchone(); c.close()
    if b and b["status"]=="scored": break
    time.sleep(2)
c=con()
b=c.execute("SELECT batch_id,seq,template,status,accuracy FROM batches ORDER BY seq").fetchall()
print("BATCHES", json.dumps([dict(x) for x in b], ensure_ascii=False))
sc=json.load(open("reports/B006_SCORE.json",encoding="utf-8"))
print("B006 accuracy", sc["accuracy"], "by_cond", {k:v["accuracy"] for k,v in sc["by_condition"].items()}, "failing", sc["failing_positions"])
print("DECISION", json.dumps([dict(x) for x in c.execute("SELECT rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id DESC LIMIT 1")], ensure_ascii=False))
print("NEXT", json.dumps([dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status IN ('queued','claimed') ORDER BY batch_id,rowid LIMIT 15")], ensure_ascii=False))
