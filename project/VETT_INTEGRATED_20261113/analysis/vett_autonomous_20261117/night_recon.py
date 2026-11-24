import sys,json,re
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
c=V.connect()
print("META",{k:V.meta_get(c,k,"") for k in ("state","supervisor_pid","worker_pid","last_status_at","last_snapshot_at","exhausted")})
print("Q",[dict(r) for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")])
last=c.execute("SELECT created_at,batch_id,match FROM results ORDER BY rowid DESC LIMIT 1").fetchone()
print("LAST_RESULT",tuple(last) if last else None)
print("FAILS")
for r in c.execute("SELECT r.match,r.model,t.gold_json,r.parsed_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id IN ('B019','B022') AND r.cond='C_change' AND r.correct=0"):
    print(" ",dict(r))
c.close()
samples=json.loads((WF.parent/"attribution_followup"/"samples.json").read_text(encoding="utf-8"))
base=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\Self-cricket-clean_text_scorecard_v1_220_matches")
for s in samples:
    txt=(base/s["match"]/"commentary.txt").read_text(encoding="utf-8",errors="replace")
    a=s["A"]; b=s["B"]; bat=s["batter"]
    ha=txt.count(a); hb=txt.count(b); hbat=txt.count(bat)
    pats=[m.group(0) for m in re.finditer(re.escape(a)+r"[^.]{0,40}for\s+\d+",txt)][:2]
    pats2=[m.group(0) for m in re.finditer(re.escape(b)+r"[^.]{0,40}for\s+\d+",txt)][:2]
    print("EV",s["match"],s["innings"],"len",len(txt),"A",ha,"B",hb,"batter",hbat,"Afig",pats,"Bfig",pats2)
