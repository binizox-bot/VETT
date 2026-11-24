
import sys
sys.path.insert(0, ".")
import vettlib as V, planner
con=V.init_db(); models=V.MODELS
used={(r["match"],int(r["innings"])) for r in con.execute("SELECT DISTINCT match,innings FROM tasks WHERE field_scope='full43'")}
def chunks(xs,n):
    for i in range(0,len(xs),n): yield xs[i:i+n]
def build_units(cond):
    out=[]
    for m in planner.SWEEP_ROOTS:
        for inn in (1,2):
            if (m,inn) in used: continue
            try: b=V.build_conditions(m,inn)
            except Exception: continue
            if cond in b["variants"]: out.append((m,inn))
    return out
configs=[
 ("O","T4_full_table_O_scale","Remaining coverage full tables under original text: replicate collateral field loss and format failure.", "O"),
 ("E","T4_full_table_E_scale","Full table under the sufficient evidence excerpt: does localization reduce collateral loss?", "E"),
 ("OI","T4_full_table_OI_scale","Full table with the other-innings total deleted: does cross-innings context change collateral loss?", "OI"),
]
total=0
for cond,tpl,hyp,_ in configs:
    units=build_units(cond)
    print(cond,"units",len(units))
    for chunk in chunks(units,60):
        tasks,rejects=[],[]
        for m,inn in chunk:
            tasks += planner.make_tasks(con,m,inn,[cond],"full43",models,rejects,allow_reuse=True,num_predict=900)
        if not tasks: continue
        d=planner._design(tpl,hyp,"Continue the authorized full-table scale with remaining coverage units.",
                          con,tasks,[cond],models,["commentary.txt","scorecard.md"],
                          "exact match per field; report parse, done_reason, 43-field accuracy and target subset")
        bid=planner.freeze_batch(con,d,tasks,rejects,plan_ms=5.0)
        total += len(tasks)
        print("frozen",bid,"units",len(chunk),"tasks",len(tasks),"rejects",len(rejects))
V.meta_set(con,"exhausted","0"); V.meta_set(con,"state","running"); V.meta_set(con,"last_plan_attempt_at",""); con.commit()
print("TOTAL",total,"QUEUE",{r["status"]:r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
