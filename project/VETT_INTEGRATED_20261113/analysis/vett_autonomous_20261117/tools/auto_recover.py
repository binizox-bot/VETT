
"""Logon/boot recovery entry for the VETT supervisor.

Respects an explicit user STOP, a disabled flag, and the single-instance lock.
Waits for Ollama, starting it if needed, then calls the validated vettctl start.
"""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

WF = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WF))
import vettlib as V

LOG = WF / "logs" / "auto_recover.log"


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(V.now_iso() + " " + msg + "\n")


def ollama_ready():
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3).read()
        return True
    except Exception:
        return False


def start_ollama():
    import shutil
    exe = shutil.which("ollama") or r"C:\Users\PC\AppData\Local\Programs\Ollama\ollama.exe"
    try:
        logf = open(WF / "logs" / "ollama.log", "ab", buffering=0)
        flags = 0x00000008 | 0x00000200 | 0x01000000
        try:
            p = subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=logf,
                                 stderr=subprocess.STDOUT, creationflags=flags, close_fds=True)
        except OSError:
            flags = 0x00000008 | 0x00000200
            p = subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=logf,
                                 stderr=subprocess.STDOUT, creationflags=flags, close_fds=True)
        log("started ollama pid=" + str(p.pid))
    except Exception as e:
        log("ollama start failed: " + type(e).__name__ + ": " + str(e))


def main():
    con = V.init_db()
    pid = int(V.meta_get(con, "supervisor_pid", "0") or 0)
    if pid and V.pid_alive(pid):
        log("already running pid=" + str(pid) + "; skip")
        return 0
    if V.meta_get(con, "stop_reason", "") == "user_stop":
        log("user_stop present; skip")
        return 0
    if V.meta_get(con, "auto_start_disabled", "0") == "1":
        log("auto_start_disabled=1; skip")
        return 0
    if V.meta_get(con, "paused", "0") == "1":
        log("paused=1; skip")
        return 0
    for i in range(60):
        if ollama_ready():
            break
        if i == 6:
            log("ollama not ready; attempting start")
            start_ollama()
        time.sleep(5)
    if not ollama_ready():
        log("ollama still not ready; skip")
        return 1
    r = subprocess.run([str(V.PYTHON), str(WF / "vettctl.py"), "start"], cwd=str(WF),
                       capture_output=True, text=True, timeout=120)
    log("vettctl start rc=" + str(r.returncode) + " out=" + (r.stdout or "").strip()[:500])
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
