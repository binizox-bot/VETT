import sys,json
from pathlib import Path
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("TOP2 TASKS",c.execute("SELECT COUNT(*) FROM tasks WHERE template='X_top2_membership'").fetchone()[0] if False else "n/a")
print("RES",c.execute("SELECT COUNT(*) FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership'").fetchone()[0])
print("ROOTS",[r[0] for r in c.execute("SELECT DISTINCT match FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership' ORDER BY match")])
print("BYCOND",[dict(r) for r in c.execute("SELECT r.cond,COUNT(*) n FROM results r JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership' GROUP BY r.cond")])
print("M3N1")
for r in c.execute("SELECT r.model,r.parsed_json,t.gold_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership' AND r.match='match_0003' AND r.cond='T2_N1' ORDER BY r.model"):
    print(" ",r[0],r[1],r[2])
# text/decode consistency with core
bad_text=0; bad_dec=0; n=0
rows=c.execute("SELECT r.match,r.model,r.cond,t.text_sha,t.decode_json,t.model_digest FROM tasks t JOIN results r USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership'").fetchall()
for m,mod,cond,ts,dec,dg in rows:
    arm=cond.replace("T2_","")
    core=c.execute("SELECT t.text_sha,t.decode_json FROM tasks t JOIN results r USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_core_event' AND r.match=? AND r.model=? AND r.cond=?",(m,mod,arm+"_F")).fetchone()
    if core:
        n+=1
        if core[0]!=ts: bad_text+=1
        if core[1]!=dec: bad_dec+=1
print("COMPARE",n,"TEXT_MISMATCH",bad_text,"DECODE_MISMATCH",bad_dec)
print("DECODES",{d for d, in c.execute("SELECT DISTINCT decode_json FROM tasks WHERE field_scope='top2'")})
c.close()
