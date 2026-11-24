import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v6"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
for k,v in sc["per"].items():
    m,model=k.split("|")
    print(m,model.split(":")[0],"D",v["reassign"]["direct_num"],v["retain"]["direct_num"],"A",v["reassign"]["attr_ok"],v["retain"]["attr_ok"],"S",v["reassign"]["strict_ok"],v["retain"]["strict_ok"])
