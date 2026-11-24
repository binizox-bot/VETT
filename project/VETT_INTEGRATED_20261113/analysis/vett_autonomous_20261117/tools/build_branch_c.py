
import sys, json
sys.path.insert(0, ".")
import vettlib as V, planner
con = V.init_db()
design, tasks, rejects = planner.build_c(con, {"rationale": "branch C dev batch before coverage sweep continues"})
print("built", len(tasks), "rejects", len(rejects))
if tasks:
    bid = planner.freeze_batch(con, design, tasks, rejects, plan_ms=5.0)
    print("batch", bid)
    print("scopes", [r["field_scope"] for r in con.execute("SELECT DISTINCT field_scope FROM tasks WHERE batch_id=?", (bid,))])
    print("conds", [dict(r) for r in con.execute("SELECT cond,COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY cond", (bid,))])
    row = con.execute("SELECT task_key,cond,fields_json,gold_json FROM tasks WHERE batch_id=? LIMIT 1", (bid,)).fetchone()
    print("sample", dict(row))
