import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"small_model_diagnostics_v3"
sc=json.loads((P/"scores.json").read_text(encoding="utf-8"))
for k,d in sc["per"].items():
    er=d.get("extract_retain") or {}
    if not er.get("ok"):
        print("FAIL",k,"doc",er.get("doc"),"exec",er.get("exec"),"prog",er.get("prog"))
cross={"direct":0,"extract":0}; n=0
for k,d in sc["per"].items():
    n+=1
    if d["direct_reassign"].get("value") and d["direct_retain"].get("value"): cross["direct"]+=1
    if d["extract_reassign"].get("ok") and d["extract_retain"].get("ok"): cross["extract"]+=1
print("cross",cross,"n",n)
