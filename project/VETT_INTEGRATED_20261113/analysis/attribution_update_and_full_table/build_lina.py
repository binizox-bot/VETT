import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); P=ROOT/"VETT_INTEGRATED_20261113"/"analysis"
old=json.loads((P/"attribution_evidence_followup"/"lina.json").read_text(encoding="utf-8"))["cases"]
(P/"attribution_update_and_full_table"/"lina.json").write_text(json.dumps({"cases":old},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("lina",len(old))
