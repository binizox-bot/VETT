
import sys
sys.path.insert(0, ".")
import vettlib as V, planner
con=V.init_db()
models=V.MODELS
existing={(r["match"],int(r["innings"])) for r in con.execute("SELECT DISTINCT match,innings FROM tasks WHERE field_scope='full43'")}
tasks,rejects=[],[]; units=0
for m in planner.SWEEP_ROOTS:
    for inn in (1,2):
        if units>=60: break
        if (m,inn) in existing: continue
        before=len(tasks)
        tasks += planner.make_tasks(con,m,inn,["O"],"full43",models,rejects,allow_reuse=True,num_predict=900)
        if len(tasks)>before: units+=1
    if units>=60: break
print("B199 units",units,"tasks",len(tasks),"rejects",len(rejects))
if tasks:
    d=planner._design("T4_full_table_scale2",
        "Second independent full-table sample: replicate collateral field loss and format failure on another 60 coverage units.",
        "Continue the full-table scale after the first 60 units were exhausted.",
        con,tasks,["O"],models,["commentary.txt","scorecard.md"],
        "exact match per field; report parse, done_reason, 43-field accuracy and target subset")
    print("frozen",planner.freeze_batch(con,d,tasks,rejects,plan_ms=5.0))
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
print("QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
