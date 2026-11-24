import json
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT/"VETT_INTEGRATED_20261113"
a = json.loads((INT/"analysis"/"closure_audit_220.json").read_text(encoding="utf-8"))
defects = [{"match": r["match"], "bad": r["bad"]} for r in a["rows"] if r["n_bad"]]
doc = {"schema": "vett.integrated.gold_defects.v1",
       "n_clean": a["clean"], "n_parsed": a["n"],
       "defects": defects, "unsupported": a["unsupported"],
       "policy": "excluded from gradeable pilot unless repaired; mark gold_defect in release"}
(INT/"pilot10"/"gold_defects.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print("defects:", len(defects), "unsupported:", len(a["unsupported"]))
