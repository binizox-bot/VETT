
import sys, json
sys.path.insert(0, ".")
import vettlib as V, planner
con = V.init_db()
design, tasks, rejects = planner.build_c(con, {"all_samples": True, "rationale": "full 8-event C batch after 4-event dev batch"})
print("built", len(tasks), "rejects", len(rejects))
if tasks:
    bid = planner.freeze_batch(con, design, tasks, rejects, plan_ms=6.0)
    print("frozen", bid)
    print("conds", [dict(r) for r in con.execute("SELECT cond,COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY cond", (bid,))])
