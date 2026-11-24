import sys,json
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
c=V.connect()
r=c.execute("SELECT t.decode_json,r.request_json FROM tasks t JOIN results r USING(task_key) WHERE t.batch_id='B209Z' LIMIT 1").fetchone()
print("TASK_DEC",r[0]); print("REQ",r[1]); c.close()
