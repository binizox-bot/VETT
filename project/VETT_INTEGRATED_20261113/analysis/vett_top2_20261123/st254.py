import sys
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("META",{k:V.meta_get(c,k,"") for k in ("state","exhausted","supervisor_pid","worker_pid")})
print("B254",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B254' GROUP BY status")])
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
c.close()
