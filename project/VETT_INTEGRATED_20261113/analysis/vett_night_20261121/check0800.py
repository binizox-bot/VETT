import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("STATE",{k:V.meta_get(c,k,"") for k in ("state","exhausted","supervisor_pid","worker_pid")})
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
print("LAST",tuple(c.execute("SELECT created_at,batch_id,match FROM results ORDER BY rowid DESC LIMIT 1").fetchone()))
print("NIGHT",c.execute("SELECT COUNT(*) FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template LIKE 'X_night%'").fetchone()[0])
for r in c.execute("SELECT batch_id,status,accuracy FROM batches WHERE seq>=248 ORDER BY seq"): print(" ",dict(r))
c.close()
