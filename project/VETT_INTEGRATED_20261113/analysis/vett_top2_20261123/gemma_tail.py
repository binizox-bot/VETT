import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
r=c.execute("SELECT raw_output,parsed_json FROM results WHERE batch_id='B257' AND model LIKE 'gemma%'").fetchone()
print("LEN",len(r[0]),"PARSED",r[1]); print("TAIL",r[0][-300:])
c.close()
