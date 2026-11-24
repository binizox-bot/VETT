import sys
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("B256",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B256' GROUP BY status")])
print("QUEUE",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
c.close()
