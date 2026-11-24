import json
from pathlib import Path
R = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113/runs/eval_pilot10"
for p in R.glob("*.jsonl"):
    keep=[l for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and json.loads(l).get("system")!="guided"]
    p.write_text("\n".join(keep)+("\n" if keep else ""), encoding="utf-8")
    print(p.name, "kept", len(keep))
