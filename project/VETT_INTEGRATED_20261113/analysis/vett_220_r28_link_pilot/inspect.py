import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_220_r28_link_pilot"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
for k,v in sc["per"].items():
    if k.endswith("|retain") or k.endswith("|reassign"):
        print(k,"A",v["A"],"Bok",v["B_ok"],"Bexec",v["B_exec"],"Bdoc",v.get("B"))
print("---anchor---")
for line in (P/"anchor.jsonl").read_text(encoding="utf-8").splitlines():
    x=json.loads(line); print(x["match"],x["model"].split(":")[0],x["target"],x["pred"])
