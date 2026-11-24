
import sys, json
sys.path.insert(0, ".")
import vettlib as V, planner
con=V.init_db()
cdesign, ctasks, crejects = planner.build_c(con, {"all_samples": True,
    "rationale": "Expand adjudication to all attribution samples; same event, formal change / maintain / no notice."})
print("C tasks", len(ctasks), "rejects", len(crejects))
if ctasks:
    cbid = planner.freeze_batch(con, cdesign, ctasks, crejects, plan_ms=5.0)
    print("C frozen", cbid)
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); V.meta_set(con,"last_plan_attempt_at","")
con.commit()
print("BATCHES",[dict(r) for r in con.execute("SELECT batch_id,template,status FROM batches ORDER BY seq DESC LIMIT 3")])
print("QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
