import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
r=c.execute("SELECT design_json FROM batches WHERE batch_id='B258'").fetchone()
print(json.dumps(json.loads(r[0])["positions"],ensure_ascii=False))
c.close()
