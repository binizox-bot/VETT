
import sys
sys.path.insert(0,".")
import vettlib as V, planner
con=V.init_db(); models=V.MODELS
units=[]
for m in planner.SWEEP_ROOTS:
    for inn in (1,2):
        try: b=V.build_conditions(m,inn)
        except Exception: continue
        if "OI" in b["variants"]: units.append((m,inn))
units=units[:52]
tasks,rejects=[],[]
for m,inn in units:
    variants=[("probe_runs",["inn"+str(inn)+".total_runs"]),
              ("probe_wickets",["inn"+str(inn)+".total_wickets"]),
              ("probe_both",["inn"+str(inn)+".total_runs","inn"+str(inn)+".total_wickets"])]
    tasks += planner.make_probe_tasks(con,m,inn,"OI",models,variants,rejects,num_predict=200)
print("units",len(units),"tasks",len(tasks),"rejects",len(rejects))
if tasks:
    d=planner._design("P_OI_probe","Field probes with the other-innings total deleted: does cross-innings context change runs/wickets binding?",
        "Extra buffer after full-table and E-probe queue.",
        con,tasks,["probe_runs","probe_wickets","probe_both"],models,["commentary.txt (OI)","scorecard.md"],
        "exact integer match per field; compare with O probes on the same unit/model")
    print("frozen",planner.freeze_batch(con,d,tasks,rejects,plan_ms=5.0))
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
print("QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
