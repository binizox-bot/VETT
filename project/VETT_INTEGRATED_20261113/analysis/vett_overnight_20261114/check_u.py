from pathlib import Path
import json
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
for f in ["runs/u_full.jsonl","U_PROGRESS.md","U_STATE.json","u_full.log"]:
    p=P/f
    print(f, p.exists(), (p.stat().st_size if p.exists() else 0))
    if p.exists() and f.endswith(".jsonl"):
        print(" rows",len(p.read_text(encoding="utf-8").splitlines()))
    if p.exists() and f=="U_STATE.json":
        print(p.read_text(encoding="utf-8"))
