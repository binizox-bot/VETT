import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
for bid in ["B213","B214","B215","B216","B217","B218","B219","B220"]:
    rows=[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY status",(bid,))]
    res=c.execute("SELECT COUNT(*) FROM results WHERE batch_id=?",(bid,)).fetchone()[0]
    print(bid,rows,"results",res)
c.close()
