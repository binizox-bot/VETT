
import json, os, shutil, subprocess, time, urllib.request
from pathlib import Path

exe = shutil.which("ollama") or r"C:\Users\PC\AppData\Local\Programs\Ollama\ollama.exe"
log = open("logs/ollama.log", "ab", buffering=0)
flags = 0x00000008 | 0x00000200 | 0x01000000
try:
    p = subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                         creationflags=flags, close_fds=True)
except OSError:
    flags = 0x00000008 | 0x00000200
    p = subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                         creationflags=flags, close_fds=True)
ready = False
last = ""
for i in range(40):
    time.sleep(1)
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as r:
            body = json.loads(r.read().decode("utf-8"))
        ready = True
        models = [m["name"] for m in body.get("models", [])]
        break
    except Exception as e:
        last = type(e).__name__ + ": " + str(e)
print(json.dumps({"pid": p.pid, "ready": ready, "models": models if ready else [], "last_error": last}, ensure_ascii=False))
