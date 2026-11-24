import sys,json,sqlite3
sys.path.insert(0,r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117")
import vettlib as V
con=V.connect()
print("B209Z_BATCH", con.execute("SELECT COUNT(*) FROM batches WHERE batch_id='B209Z'").fetchone()[0])
print("B209Z_TASKS", con.execute("SELECT COUNT(*) FROM tasks WHERE batch_id='B209Z'").fetchone()[0])
rows=[json.loads(l) for l in open(r"D:/Download/VETT_Cricket_Complete_Delivery_R19_20261017/VETT_INTEGRATED_20261113/analysis/codex_exchange/PILOT_B209Z/tasks.jsonl",encoding="utf-8")]
out=[]
for r in rows:
    k=r["task_key"]
    t=con.execute("SELECT batch_id,status FROM tasks WHERE task_key=?",(k,)).fetchone()
    rr=con.execute("SELECT batch_id,parse_ok,correct FROM results WHERE task_key=?",(k,)).fetchone()
    out.append((r["cond"],r["model"].split(":")[0], "task:"+str(t[0]) if t else "-", "res:"+str(rr[0]) if rr else "-"))
from collections import Counter
print("DUP", Counter([(o[0],o[1]) for o in out if o[2]!="-"]))
print("DUP_ROWS", [o for o in out if o[2]!="-"])
print("HAS_RESULT", sum(1 for o in out if o[3]!="-"), "of", len(out))
con.close()
