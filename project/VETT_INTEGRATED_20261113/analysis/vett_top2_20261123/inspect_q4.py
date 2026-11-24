import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("B243 q4 raw")
for r in c.execute("SELECT r.match,r.model,r.parsed_json,r.raw_output FROM results r WHERE r.batch_id='B243' AND r.cond='q4_old'"):
    p=json.loads(r[2] or "{}")
    print(r[0],r[1].split(":")[0],p)
print("CORE N2_F sample")
for r in c.execute("SELECT r.match,r.model,r.parsed_json,r.raw_output FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event' AND r.cond='N2_F' LIMIT 3"):
    print(r[0],r[1].split(":")[0],r[2],"RAW",r[3][:120])
c.close()
