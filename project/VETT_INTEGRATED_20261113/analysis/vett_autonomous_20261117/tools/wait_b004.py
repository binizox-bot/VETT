
import json, sqlite3, time
DB="state/workflow.db"
def con():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
for i in range(150):
    c=con()
    b=c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B004'").fetchone()
    c.close()
    if b and b["status"]=="scored":
        break
    time.sleep(2)
c=con()
b=c.execute("SELECT batch_id,seq,template,status,accuracy FROM batches ORDER BY seq").fetchall()
print("BATCHES", json.dumps([dict(x) for x in b], ensure_ascii=False))
d=c.execute("SELECT rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id DESC LIMIT 2").fetchall()
print("LAST_DECISIONS", json.dumps([dict(x) for x in d], ensure_ascii=False, indent=1))
try:
    sc=json.load(open("reports/B004_SCORE.json",encoding="utf-8"))
    print("B004 accuracy", sc["accuracy"], "cells", sc["cells_correct"], "/", sc["cells_total"])
    print("B004 by_model", {k:v["accuracy"] for k,v in sc["by_model"].items()})
    tf=[f for f in sc["by_field"] if f.endswith("total_runs") or f.endswith("total_wickets")]
    print("B004 target fields", {f:sc["by_field"][f] for f in tf})
    print("B004 errors", len(sc["errors"]), "parse_failures", len(sc["parse_failures"]))
except Exception as e:
    print("NO_B004_SCORE", type(e).__name__, e)
print("NEXT", json.dumps([dict(x) for x in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status IN ('queued','claimed') ORDER BY batch_id,rowid LIMIT 15")], ensure_ascii=False))
