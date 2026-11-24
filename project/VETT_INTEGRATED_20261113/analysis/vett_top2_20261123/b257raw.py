import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("B257",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B257' GROUP BY status")])
for r in c.execute("SELECT r.model,r.parsed_json,r.raw_output FROM results r WHERE r.batch_id='B257'"):
    print("MODEL",r[0].split(":")[0]); print("PARSED",r[1]); print("RAW",(r[2] or "")[:400].replace(chr(10)," ")); print()
c.close()
