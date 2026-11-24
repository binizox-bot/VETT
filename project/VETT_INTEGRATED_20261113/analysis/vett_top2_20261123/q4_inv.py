import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("CONDS",[dict(r) for r in c.execute("SELECT t.batch_id,t.cond,COUNT(*) n FROM tasks t JOIN batches b USING(batch_id) WHERE b.template='X_night_diag' AND t.cond LIKE '%q4%' GROUP BY t.batch_id,t.cond")])
print("BATCHES",[dict(r) for r in c.execute("SELECT batch_id,seq,template FROM batches WHERE template LIKE 'X_night%diag%' ORDER BY seq")])
print("CONDS_ALL",[dict(r) for r in c.execute("SELECT t.batch_id,t.cond,COUNT(*) n FROM tasks t JOIN batches b USING(batch_id) WHERE b.template='X_night_diag' GROUP BY t.batch_id,t.cond ORDER BY t.cond")])
c.close()
