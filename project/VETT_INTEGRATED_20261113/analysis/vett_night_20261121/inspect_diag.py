import sys,json
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
c=V.connect()
for cond in ("q1_batter","q4_old"):
    print("==",cond)
    for r in c.execute("SELECT r.match,r.model,r.parsed_json,r.raw_output FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_diag' AND r.cond=? LIMIT 8",(cond,)):
        print(" ",r[0],r[1].split(":")[0],r[2], "|RAW",r[3].replace(chr(10)," ")[:100])
print("B248",[dict(x) for x in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B248' GROUP BY status")])
print("Q",[dict(x) for x in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
c.close()
