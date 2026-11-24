import sys
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("B212", tuple(c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B212'").fetchone()))
print("RESULTS", c.execute("SELECT COUNT(*) FROM results WHERE batch_id='B212'").fetchone()[0])
print("QUEUE", {k:V.meta_get(c,k,"") for k in ("state","exhausted")})
print("Q", [dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
c.close()
