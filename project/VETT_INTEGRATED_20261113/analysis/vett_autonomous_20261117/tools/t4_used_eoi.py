
import sys
sys.path.insert(0,".")
import vettlib as V, planner
con=V.init_db(); models=V.MODELS
used=sorted({(r["match"],int(r["innings"])) for r in con.execute("SELECT DISTINCT match,innings FROM tasks WHERE field_scope='full43'")})
def chunks(xs,n):
    for i in range(0,len(xs),n): yield xs[i:i+n]
total=0
configs=[
 ("E","T4_full_table_E_used","Full table under the sufficient excerpt on units already full-tabled under O: does localization reduce collateral loss?"),
 ("OI","T4_full_table_OI_used","Full table with the other-innings total deleted on units already full-tabled under O: does cross-innings context change collateral loss?"),
]
for cond,tpl,hyp in configs:
    units=[]
    for m,inn in used:
        try: b=V.build_conditions(m,inn)
        except Exception: continue
        if cond in b["variants"]: units.append((m,inn))
    units=units[:100]
    print(cond,"units",len(units))
    for chunk in chunks(units,60):
        tasks,rejects=[],[]
        for m,inn in chunk:
            tasks += planner.make_tasks(con,m,inn,[cond],"full43",models,rejects,allow_reuse=True,num_predict=900)
        if not tasks: continue
        d=planner._design(tpl,hyp,"Extend the authorized full-table scale to the E/OI contrast on already used units.",
                          con,tasks,[cond],models,["commentary.txt variants","scorecard.md"],
                          "exact match per field; paired by unit/model against the O full table")
        bid=planner.freeze_batch(con,d,tasks,rejects,plan_ms=5.0)
        total+=len(tasks); print("frozen",bid,"tasks",len(tasks),"rejects",len(rejects))
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); con.commit()
print("ADDED",total,"QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
