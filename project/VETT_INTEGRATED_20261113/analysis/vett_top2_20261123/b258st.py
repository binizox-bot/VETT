import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("B258",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B258' GROUP BY status")])
c.close()
