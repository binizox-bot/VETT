import sys
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
for bid in ("B243","B244","B245","B246","B247"):
    print(bid, c.execute("SELECT COUNT(*) FROM tasks WHERE batch_id=?",(bid,)).fetchone()[0], [dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY status",(bid,))])
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
c.close()
