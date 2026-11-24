import sys,json
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("STATE", {k:V.meta_get(c,k,"") for k in ("state","worker_pid","supervisor_pid")})
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
print("QBY",[dict(r) for r in c.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE status='queued' GROUP BY batch_id ORDER BY batch_id")])
print("B209Z",tuple(c.execute("SELECT status,accuracy FROM batches WHERE batch_id='B209Z'").fetchone()))
tot=[0,0]
for r in c.execute("SELECT score_json FROM results WHERE batch_id='B209Z'"):
    s=json.loads(r[0]); tot[0]+=s.get("cells_correct",0); tot[1]+=s.get("cells_total",0)
print("NEW_CELLS",tot)
reuse=[json.loads((V.BATCHES/"B209Z_REUSE.json").read_text(encoding="utf-8"))]
for r in reuse[0]:
    rr=c.execute("SELECT score_json FROM results WHERE task_key=?", (r["task_key"],)).fetchone()
    s=json.loads(rr[0]); print("REUSE",r["cond"],r["model"],s.get("cells_correct"),s.get("cells_total"))
c.close()
