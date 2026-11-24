import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
print("BY_BATCH",[dict(r) for r in c.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE fields_json LIKE '%bowlers%' GROUP BY batch_id")])
print("BY_PROMPT",[dict(r) for r in c.execute("SELECT batch_id,COUNT(*) n FROM tasks WHERE prompt LIKE '%top two rows%' GROUP BY batch_id")])
print("BY_COND",[dict(r) for r in c.execute("SELECT cond,COUNT(*) n FROM tasks WHERE cond LIKE 'T2_%' GROUP BY cond")])
print("QUEUE",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
print("META",{k:V.meta_get(c,k,"") for k in ("state","exhausted")})
cur={m:V.model_digest(m) for m in V.MODELS}
bad=0
for m,mod,dg in c.execute("SELECT r.match,r.model,t.model_digest FROM tasks t JOIN results r USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_top2_membership'"):
    if cur.get(mod)!=dg: bad+=1
print("DIGEST_BAD",bad)
c.close()
