
"""Continuous supervisor watchdog (60s).

Starts the supervisor after an unexpected death, but never overrides an
explicit user stop, a pause, or the auto_start_disabled flag.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

WF = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WF))
import vettlib as V

LOG = WF / "logs" / "auto_watch.log"
LOCK = WF / "state" / "auto_watch.pid"


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(V.now_iso() + " " + msg + "\n")


def main():
    if LOCK.exists():
        try:
            old = int(LOCK.read_text(encoding="utf-8").strip())
        except Exception:
            old = 0
        if old and old != os.getpid() and V.pid_alive(old):
            log("already running pid=" + str(old) + "; exit duplicate")
            return 0
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    log("watchdog start pid=" + str(os.getpid()))
    while True:
        try:
            con = V.init_db()
            reason = V.meta_get(con, "stop_reason", "")
            paused = V.meta_get(con, "paused", "0")
            disabled = V.meta_get(con, "auto_start_disabled", "0")
            pid = int(V.meta_get(con, "supervisor_pid", "0") or 0)
            con.close()
            if disabled == "1" or paused == "1" or reason == "user_stop":
                time.sleep(60)
                continue
            if not (pid and V.pid_alive(pid)):
                log("supervisor down (pid=" + str(pid) + ", reason=" + str(reason) + "); invoking auto_recover")
                r = subprocess.run([str(V.PYTHON), str(WF / "tools" / "auto_recover.py")],
                                   cwd=str(WF), capture_output=True, text=True, timeout=180)
                tail = ((r.stdout or "") + (r.stderr or "")).strip().replace("\n", " ")[:300]
                log("auto_recover rc=" + str(r.returncode) + " " + tail)
                time.sleep(90)
            else:
                time.sleep(60)
        except Exception as e:
            log("watchdog loop error: " + type(e).__name__ + ": " + str(e))
            time.sleep(60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
