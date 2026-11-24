import sys,json
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
con=V.connect()
print("META", {k:V.meta_get(con,k,"") for k in ("state","worker_heartbeat_at","worker_pid","supervisor_pid")})
for r in con.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B209Z' GROUP BY status"): print("B209Z",dict(r))
print("RESULTS",con.execute("SELECT COUNT(*) FROM results WHERE batch_id='B209Z'").fetchone()[0])
for r in con.execute("SELECT match,innings,model,cond,correct,parse_ok,substr(raw_output,1,80) raw FROM results WHERE batch_id='B209Z' ORDER BY created_at DESC LIMIT 4"):
    print("RES",dict(r))
print("QBY", [dict(x) for x in con.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE status='queued' GROUP BY batch_id ORDER BY batch_id").fetchall()])
con.close()
