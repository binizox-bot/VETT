import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
raw=c.execute("SELECT raw_output FROM results WHERE batch_id='B257' AND model LIKE 'gemma%'").fetchone()[0]
try:
    p=json.loads(raw); print("OK",p.get("fields",{}).get("inn1.bowl1_name"),p.get("fields",{}).get("inn1.bowl2_name"),p.get("fields",{}).get("inn1.bowl2_wickets"),p.get("fields",{}).get("inn1.bowl2_runs"))
except Exception as e:
    print("ERR",e)
    i=int(str(e).split("char ")[-1].split()[0]) if "char " in str(e) else 0
    print("CTX",raw[max(0,i-120):i+80])
c.close()
