import sys
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
for r in c.execute("SELECT template,COUNT(*) n FROM batches GROUP BY template ORDER BY n DESC"): print(r[0],r[1])
print("USED_ROOTS",[r[0] for r in c.execute("SELECT COUNT(DISTINCT match) FROM tasks t JOIN batches b USING(batch_id) WHERE b.template LIKE '%ordinary%'")])
c.close()
