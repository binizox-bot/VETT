
import json, sqlite3, time
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
for i in range(180):
    c=con()
    b7=c.execute("SELECT status FROM batches WHERE batch_id='B007'").fetchone()
    b8=c.execute("SELECT batch_id,template,status FROM batches WHERE batch_id='B008'").fetchone()
    c.close()
    if b7 and b7["status"]=="scored" and b8:
        break
    time.sleep(2)
c=con()
print("B007", dict(c.execute("SELECT batch_id,template,status,accuracy FROM batches WHERE batch_id='B007'").fetchone()))
try:
    sc=json.load(open("reports/B007_SCORE.json",encoding="utf-8"))
    print("B007 accuracy", sc["accuracy"], "by_cond", {k:v["accuracy"] for k,v in sc["by_condition"].items()}, "failing", sc["failing_positions"])
except Exception as e:
    print("B007 score pending", e)
print("B008", dict(c.execute("SELECT batch_id,template,status FROM batches WHERE batch_id='B008'").fetchone()) if c.execute("SELECT 1 FROM batches WHERE batch_id='B008'").fetchone() else None)
print("DECISIONS", json.dumps([dict(x) for x in c.execute("SELECT rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id DESC LIMIT 3")], ensure_ascii=False, indent=1))
print("NEXT", json.dumps([dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status IN ('queued','claimed') ORDER BY batch_id,rowid LIMIT 15")], ensure_ascii=False))
print("META", {k:c.execute('SELECT value FROM meta WHERE key=?',(k,)).fetchone()['value'] for k in ('state','exhausted','external_api_calls')})
