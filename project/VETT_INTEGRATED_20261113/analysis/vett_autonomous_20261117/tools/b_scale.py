
import sys
sys.path.insert(0,".")
import vettlib as V, planner
con=V.init_db(); models=V.MODELS
units=[]
for m in planner.SWEEP_ROOTS:
    if len(units)>=30: break
    for inn in (1,2):
        if len(units)>=30: break
        try: b=V.build_conditions(m,inn)
        except Exception: continue
        if "OI" in b["variants"]: units.append((m,inn))
tasks,rejects=[],[]
for m,inn in units:
    b=V.build_conditions(m,inn)
    conds=[c for c in ("O","E","OI","OIC") if c in b["variants"]]
    tasks += planner.make_tasks(con,m,inn,conds,"target2",models,rejects,allow_reuse=True,num_predict=300)
print("units",len(units),"tasks",len(tasks),"rejects",len(rejects))
if tasks:
    d=planner._design("B_cross_innings_scale",
        "Cross-innings O/E/OI/OIC on 30 coverage units: test whether deleting the other-innings score changes target cells after explicit innings.",
        "Buffer after the full-table queue; controlled, evidence-varying diagnostics.",
        con,tasks,["O","E","OI","OIC"],models,["commentary.txt variants","scorecard.md"],
        "exact integer match per field; paired by unit/model against O")
    print("frozen",planner.freeze_batch(con,d,tasks,rejects,plan_ms=5.0))
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
print("QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
