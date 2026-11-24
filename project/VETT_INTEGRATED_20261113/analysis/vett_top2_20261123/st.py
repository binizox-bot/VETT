import sys
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
for b in ("B254","B255"): print(b,[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY status",(b,))])
print("META",{k:V.meta_get(c,k,"") for k in ("state","worker_pid","supervisor_pid")})
c.close()
