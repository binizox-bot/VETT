import time,json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
while True:
    now=time.localtime(); target=time.mktime((now.tm_year,now.tm_mon,now.tm_mday,8,0,0,0,0,-1))
    if now.tm_hour>=8: target+=86400
    time.sleep(max(1,target-time.time()))
    rows=0
    for f in ["runs/u_full.jsonl","runs/expand.jsonl","runs/u_audit.jsonl"]:
        p=P/f
        if p.exists(): rows+=len(p.read_text(encoding="utf-8").splitlines())
    (P/"MORNING_README.md").write_text(f"# MORNING_README\n\n状态：后台 U 全池审计运行中。\n\n- 已落盘总行 {rows}\n- 08:00 快照\n- 详见 U_PROGRESS.md / REPORT_FINAL.md\n",encoding="utf-8")
