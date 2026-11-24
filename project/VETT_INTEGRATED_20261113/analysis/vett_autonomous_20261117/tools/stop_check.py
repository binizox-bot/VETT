
import json, sqlite3, subprocess, time, sys
PY = r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
def con():
    c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row; return c
def alive(pid):
    try:
        pid = int(pid)
    except Exception:
        return False
    if pid <= 0: return False
    import ctypes
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
    if not h: return False
    code = ctypes.c_ulong(); ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    ctypes.windll.kernel32.CloseHandle(h)
    return bool(ok) and code.value == 259
def snap():
    c = con()
    s = {k: c.execute("SELECT value FROM meta WHERE key=?", (k,)).fetchone()["value"]
         for k in ("state", "supervisor_pid", "worker_pid", "worker_restarts", "stop_requested", "paused", "external_api_calls")}
    s["queue"] = {r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
    s["results"] = c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
    s["last_result_at"] = c.execute("SELECT MAX(created_at) m FROM results").fetchone()["m"]
    s["batches"] = [dict(r) for r in c.execute("SELECT batch_id,status,accuracy FROM batches ORDER BY seq")]
    s["sup_alive"] = alive(s["supervisor_pid"]); s["worker_alive"] = alive(s["worker_pid"])
    s["claimed_by"] = [dict(r) for r in c.execute("SELECT task_key,claimed_by,attempts,recoveries FROM tasks WHERE status='claimed'")]
    c.close(); return s
before = snap()
r = subprocess.run([PY, "vettctl.py", "stop"], capture_output=True, text=True)
print("STOP_RECEIPT", (r.stdout or "").strip().replace("\n", " "), "rc", r.returncode)
time.sleep(12)
after = snap()
c = con()
events = [dict(x) for x in c.execute("SELECT ts,kind,payload FROM events ORDER BY id DESC LIMIT 6")]
c.close()
print("VERDICT", json.dumps({
  "before": before, "after": after,
  "no_new_results_after_stop": before["results"] == after["results"],
  "supervisor_stopped": not after["sup_alive"],
  "worker_stopped": not after["worker_alive"],
  "dispatch_stopped": after["queue"].get("claimed", 0) == 0,
  "restart_stopped": after["worker_restarts"] == before["worker_restarts"],
  "events": events,
}, ensure_ascii=False, indent=1, default=str))
