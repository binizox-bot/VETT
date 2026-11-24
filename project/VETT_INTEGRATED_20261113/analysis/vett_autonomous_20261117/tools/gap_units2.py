
import sys, sqlite3
sys.path.insert(0,".")
import vettlib as V, planner
con=V.init_db()
for m,inn in [("match_0004",1),("match_0004",2),("match_0066",2)]:
    variants=[("probe_runs",["inn"+str(inn)+".total_runs"]),
              ("probe_wickets",["inn"+str(inn)+".total_wickets"]),
              ("probe_both",["inn"+str(inn)+".total_runs","inn"+str(inn)+".total_wickets"])]
    rej=[]
    tasks=planner.make_probe_tasks(con,m,inn,"O",V.MODELS,variants,rej,num_predict=200)
    print(m,inn,"new",len(tasks),"rejects",rej[:6])
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
print("EXISTING",[dict(r) for r in c.execute("SELECT batch_id,field_scope,status,COUNT(*) n FROM tasks WHERE match IN ('match_0004','match_0066') GROUP BY batch_id,field_scope,status")])
print("P_RESULTS",c.execute("SELECT COUNT(*) n FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep' AND r.match IN ('match_0004','match_0066')").fetchone()['n'])
