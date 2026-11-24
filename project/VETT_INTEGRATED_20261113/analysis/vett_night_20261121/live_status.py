import sys,json,datetime
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
q={r[0]:r[1] for r in c.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status")}
last=c.execute("SELECT created_at,batch_id,match FROM results ORDER BY rowid DESC LIMIT 1").fetchone()
night=c.execute("SELECT COUNT(*) FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template LIKE 'X_night%'").fetchone()[0]
print("META",{k:V.meta_get(c,k,"") for k in ("state","supervisor_pid","worker_pid","batch_seq","exhausted")})
print("Q",q,"LAST",tuple(last),"NIGHT_RESULTS",night)
print("QBY",[dict(r) for r in c.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE status='queued' GROUP BY batch_id ORDER BY seq")][:8])
c.close()
