import sys,json
sys.path.insert(0,r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
import vettlib as V
c=V.connect()
rows=c.execute("SELECT r.model,t.prompt,r.parsed_json FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='X_night_fulltable' AND r.match='match_0003' AND r.cond='N1_F_fulltable'").fetchall()
for m,p,parsed in rows:
    print("MODEL",m.split(":")[0]); print("PROMPT_HEAD",p[:600]); print("PARSED",parsed); print()
c.close()
