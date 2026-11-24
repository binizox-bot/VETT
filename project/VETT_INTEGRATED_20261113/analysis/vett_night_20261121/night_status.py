import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("STATE",{k:V.meta_get(c,k,"") for k in ("state","supervisor_pid","worker_pid","batch_seq","exhausted")})
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
print("LAST",tuple(c.execute("SELECT created_at,batch_id,match FROM results ORDER BY rowid DESC LIMIT 1").fetchone()))
print("BYTEMPLATE")
for r in c.execute("SELECT b.template,COUNT(DISTINCT r.task_key) n FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template LIKE 'X_night%' GROUP BY b.template"): print(" ",dict(r))
print("BATCHES")
for r in c.execute("SELECT batch_id,template,status,accuracy FROM batches WHERE template LIKE 'X_night%' ORDER BY seq"): print(" ",dict(r))
print("QBY",[dict(r) for r in c.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE status='queued' GROUP BY batch_id ORDER BY batch_id")])
c.close()
