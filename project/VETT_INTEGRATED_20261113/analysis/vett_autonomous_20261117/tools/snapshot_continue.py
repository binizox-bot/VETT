
import json, sqlite3, subprocess, time
PY = r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
def con():
    c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row; return c
r=subprocess.run([PY,"vettctl.py","start"],capture_output=True,text=True)
print("START", (r.stdout or "").strip().replace("\n"," "))
for i in range(30):
    c=con(); n=c.execute("SELECT COUNT(*) n FROM tasks WHERE status='claimed'").fetchone()["n"]; c.close()
    if n>=1: break
    time.sleep(1)
c=con(); before=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]; c.close()
snap=subprocess.run([PY,"vettctl.py","snapshot"],capture_output=True,text=True)
print("SNAPSHOT", (snap.stdout or "").strip().replace("\n"," "))
time.sleep(15)
c=con()
after=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
last=c.execute("SELECT MAX(created_at) m FROM results").fetchone()["m"]
c.close()
stop=subprocess.run([PY,"vettctl.py","stop"],capture_output=True,text=True)
print("STOP", (stop.stdout or "").strip().replace("\n"," "))
time.sleep(8)
c=con()
meta={k:c.execute("SELECT value FROM meta WHERE key=?",(k,)).fetchone()["value"] for k in ("state","supervisor_pid","worker_pid")}
final_n=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
c.close()
print("VERDICT", json.dumps({"results_before_snapshot":before,"results_15s_after":after,
  "new_results_after_snapshot":after-before,"last_result_at":last,
  "inference_continued_after_snapshot":after>before,"final_results":final_n,"meta":meta},ensure_ascii=False,indent=1))
