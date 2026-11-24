import subprocess,sys,os,time
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
PY=r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
pidf=ROOT/"watcher.pid"
def alive(pid):
    try:
        os.kill(pid,0); return True
    except Exception: return False
if pidf.exists():
    try:
        pid=int(pidf.read_text().strip())
        if alive(pid):
            print("already_running",pid); sys.exit(0)
    except Exception: pass
flags=0x00000008|0x00000200|0x01000000
log=open(ROOT/"NIGHT_WATCH.log","ab",buffering=0)
p=subprocess.Popen([PY,str(ROOT/"night_watch.py")],cwd=str(ROOT),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=flags,close_fds=True)
pidf.write_text(str(p.pid),encoding="utf-8")
print("started",p.pid)
