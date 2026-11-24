
import sys
sys.path.insert(0,".")
import vettlib as V, planner
con=V.init_db(); models=V.MODELS
units=[]
for m in planner.SWEEP_ROOTS:
    for inn in (1,2):
        try: b=V.build_conditions(m,inn)
        except Exception: continue
        if "E" in b["variants"]: units.append((m,inn))
units=units[:68]
tasks,rejects=[],[]
for m,inn in units:
    variants=[("probe_runs",["inn"+str(inn)+".total_runs"]),
              ("probe_wickets",["inn"+str(inn)+".total_wickets"]),
              ("probe_both",["inn"+str(inn)+".total_runs","inn"+str(inn)+".total_wickets"])]
    tasks += planner.make_probe_tasks(con,m,inn,"E",models,variants,rejects,num_predict=200)
print("units",len(units),"tasks",len(tasks),"rejects",len(rejects))
if tasks:
    d=planner._design("P_E_probe","Field probes on the sufficient evidence excerpt: does localization reduce runs/wickets field confusion?",
        "Buffer after full-table queue; E-only probes on 68 units.",
        con,tasks,["probe_runs","probe_wickets","probe_both"],models,["commentary.txt (excerpt)","scorecard.md"],
        "exact integer match per field; compare with O probes on the same unit/model")
    print("frozen",planner.freeze_batch(con,d,tasks,rejects,plan_ms=5.0))
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
print("QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
