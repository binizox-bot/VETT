import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
R=[json.loads(l) for l in (P/"runs"/"all.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for r in R:
    if r["phase"]=="T":
        print(r["match"],r["model"].split(":")[0],"parsed",r.get("parsed"),"raw",repr(r["raw_output"][:300])); break
