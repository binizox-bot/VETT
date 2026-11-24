import sys,json,time,subprocess,datetime,os
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
PY=r"C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
sys.path.insert(0,str(WF))
import vettlib as V
TZ=datetime.timezone(datetime.timedelta(hours=8))
MORNING_AT=datetime.datetime(2026,11,22,8,0,tzinfo=TZ)
LOG=ROOT/"NIGHT_WATCH.log"; DONE=ROOT/".morning_done"

def log(msg):
    with open(LOG,"a",encoding="utf-8") as f:
        f.write(datetime.datetime.now(TZ).isoformat(timespec="seconds")+" "+msg+"\n")

def counts():
    c=V.connect()
    q={r[0]:r[1] for r in c.execute("SELECT status,COUNT(*) FROM tasks GROUP BY status")}
    rows=[r[0] for r in c.execute("SELECT created_at FROM results ORDER BY rowid DESC LIMIT 400").fetchall()]
    state=V.meta_get(c,"state",""); stop=V.meta_get(c,"stop_reason",""); c.close()
    now=datetime.datetime.now(TZ); recent=0; last=None
    for ts in rows:
        if last is None: last=ts
        try: t=datetime.datetime.fromisoformat(ts)
        except Exception: continue
        if (now-t).total_seconds()<=900: recent+=1
    return q,last,recent,state,stop

def extend():
    for args in (["ft_ordinary","--n","10"],["fallback","--n","40"]):
        try:
            p=subprocess.run([PY,str(ROOT/"night_more.py")]+args,cwd=str(ROOT),capture_output=True,text=True,timeout=300)
            out=(p.stdout or "")[:300].replace("\n"," ")
            log("extend "+" ".join(args)+" rc="+str(p.returncode)+" out="+out)
            if '"tasks": 0' not in (p.stdout or ""): return
        except Exception as e:
            log("extend_err "+type(e).__name__+": "+str(e))

def ensure_alive(state,stop):
    if state in ("running","paused","starting","idle_no_valid_tasks"): return
    if state=="stopped" and stop=="user_stop": return
    try:
        p=subprocess.run([PY,str(WF/"vettctl.py"),"start"],cwd=str(WF),capture_output=True,text=True,timeout=120)
        log("restart rc="+str(p.returncode)+" out="+(p.stdout or "")[:200].replace("\n"," "))
    except Exception as e:
        log("restart_err "+str(e))

def progress():
    q,last,recent,state,stop=counts()
    rate=max(recent/15.0,0.3)
    eta=(q.get("queued",0)+q.get("claimed",0))/rate/60.0
    now=datetime.datetime.now(TZ)
    lines=["# 夜间进度","", "- 时间："+now.isoformat(timespec="seconds"),
           "- 状态："+state+"；队列："+json.dumps(q,ensure_ascii=False),
           "- 最近结果："+str(last)+"；近15分钟结果："+str(recent),
           "- 预计队列可跑："+str(round(eta,1))+" 小时",
           "- 08:00 报告："+("已生成" if DONE.exists() else "待生成"),""]
    (ROOT/"NIGHT_PROGRESS.md").write_text("\n".join(lines),encoding="utf-8")
    with open(ROOT/"NIGHT_HOURLY.md","a",encoding="utf-8") as f:
        f.write("- "+now.isoformat(timespec="seconds")+" "+json.dumps(q,ensure_ascii=False)+" last="+str(last)+" recent15="+str(recent)+" eta_h="+str(round(eta,1))+"\n")
    return eta

last_extend=0
log("watch_start_v2")
while True:
    try:
        now=datetime.datetime.now(TZ)
        q,last,recent,state,stop=counts()
        eta=progress()
        before_morning=now<MORNING_AT
        if before_morning and (q.get("queued",0)+q.get("claimed",0)==0 or eta<5) and (time.time()-last_extend)>600:
            extend(); last_extend=time.time()
        if now>=MORNING_AT and not DONE.exists():
            p=subprocess.run([PY,str(ROOT/"night_report.py"),"--morning"],cwd=str(ROOT),capture_output=True,text=True,timeout=300)
            log("morning rc="+str(p.returncode)+" "+(p.stdout or "")[:200])
            if p.returncode==0: DONE.write_text(now.isoformat(),encoding="utf-8")
        ensure_alive(state,stop)
        time.sleep(60)
    except Exception as e:
        log("loop_err "+type(e).__name__+": "+str(e)); time.sleep(60)
