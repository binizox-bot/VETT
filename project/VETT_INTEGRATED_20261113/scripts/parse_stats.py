import json
from pathlib import Path
from collections import Counter
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
R = ROOT/"VETT_INTEGRATED_20261113/runs/eval_pilot10"
for p in sorted(R.glob("*.jsonl")):
    c=Counter(); n=Counter()
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        r=json.loads(line); s=r["system"]; n[s]+=1
        if not r.get("pred"): c[s]+=1
    print(p.name, {s: f"{c[s]}/{n[s]} empty" for s in n})
