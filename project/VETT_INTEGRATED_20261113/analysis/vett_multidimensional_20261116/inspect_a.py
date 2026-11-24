import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_multidimensional_20261116"
R=[json.loads(l) for l in (P/"RUNS"/"a_dev.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
r=R[0]; print(r.keys()); print(type(r.get("parsed")), r.get("parsed")); print(type(r.get("fields")))
