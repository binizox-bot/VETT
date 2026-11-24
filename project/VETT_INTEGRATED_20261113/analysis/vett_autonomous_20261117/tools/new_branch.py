
import json, sys
sys.path.insert(0, ".")
import vettlib as V, planner

con = V.init_db()
models = V.MODELS
tasks, rejects = [], []
units = 0
for m in planner.SWEEP_ROOTS:
    for inn in (1, 2):
        if units >= 60:
            break
        before = len(tasks)
        tasks += planner.make_tasks(con, m, inn, ["O"], "full43", models, rejects,
                                    allow_reuse=True, num_predict=900)
        if len(tasks) > before:
            units += 1
    if units >= 60:
        break
print("T4 units", units, "tasks", len(tasks), "rejects", len(rejects))
if tasks:
    d = planner._design("T4_full_table_scale",
        "Full 43-field accuracy on 60 coverage units tests whether collateral field loss and JSON failure replicate beyond match_0002.",
        "Scale the validated single-root full-table check to a controlled coverage sample.",
        con, tasks, ["O"], models, ["commentary.txt", "scorecard.md"],
        "exact match per field; report 43-field accuracy, target-cell subset, parse and done_reason")
    bid = planner.freeze_batch(con, d, tasks, rejects, plan_ms=5.0)
    print("T4 frozen", bid)

ctasks, crejects = planner.build_c(con, {"all_samples": True,
    "rationale": "Expand adjudication to all attribution samples; same event, formal change / maintain / no notice."})
print("C tasks", len(ctasks), "rejects", len(crejects))
if ctasks:
    cbid = planner.freeze_batch(con, crejects and {} or planner._design("C_adjudication_scale",
        "All attribution samples under formal change, maintained original, and no notice.",
        "Expand the C branch from the selected samples to all 8 events.",
        con, ctasks, ["C_change", "C_maintain", "C_no_notice"], models,
        ["attribution_followup/samples.json"], "exact integer match per field; change gold=new, maintain/no_notice gold=old"),
        ctasks, crejects, plan_ms=5.0)
    print("C frozen", cbid)

V.meta_set(con, "exhausted", "0")
V.meta_set(con, "state", "running")
V.meta_set(con, "last_plan_attempt_at", "")
con.commit()
print("queue", {r["status"]: r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
