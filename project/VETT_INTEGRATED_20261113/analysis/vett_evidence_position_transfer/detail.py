import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"
P=INT/"analysis"/"vett_evidence_position_transfer"; sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
for k,v in sc["per"].items():
    if v["O"]["ok"]!=v["M"]["ok"] or v["O"]["ok"]!=v["E"]["ok"]:
        print(k,"O",v["O"],"M",v["M"],"E",v["E"])
# old evidence all-3-correct set
S=json.loads((INT/"analysis"/"vett_local_evidence_long_run"/"scores.json").read_text(encoding="utf-8"))
ev=S["evidence"]
ms=set(k.split("|")[0] for k in ev)
for m in sorted(ms):
    ok=[v["ok"] for k,v in ev.items() if k.startswith(m+"|")]
    print("EV",m,ok)
