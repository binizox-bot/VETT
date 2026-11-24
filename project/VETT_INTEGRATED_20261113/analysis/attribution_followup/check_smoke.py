import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_followup"
r=[json.loads(l) for l in (P/"runs"/"smoke.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()][0]
s=json.loads((P/"samples.json").read_text(encoding="utf-8"))[0]
print("gold",s["fields"]); print("pred",r["fields"])
