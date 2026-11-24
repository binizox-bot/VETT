
import sys, json
sys.path.insert(0, ".")
import vettlib as V, planner
con=V.init_db()
units=planner.sweep_units()
print("total_units",len(units),"cursor",V.meta_get(con,"probe_cursor","0"))
for m,inn in units[357:]:
    variants=[("probe_runs",["inn"+str(inn)+".total_runs"]),
              ("probe_wickets",["inn"+str(inn)+".total_wickets"]),
              ("probe_both",["inn"+str(inn)+".total_runs","inn"+str(inn)+".total_wickets"])]
    rej=[]
    tasks=planner.make_probe_tasks(con,m,inn,"O",V.MODELS,variants,rej,num_predict=200)
    print(m,inn,"tasks",len(tasks),"rejects",rej[:4])
