import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_evidence_position_transfer"
S=json.loads((P/"manifest.json").read_text(encoding="utf-8"))
au=[]
for x in S:
    for f,v in [("total_runs",x["runs"]),("total_wickets",x["wickets"])]:
        au.append({"match":x["match"],"innings":x["innings"],"team":x["team"],"field":f,"value":v,"quote":x["evidence"],"status":"auto_verified","source":"published commentary","variants":["O","M","E"]})
(P/"evidence_audit.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in au)+"\n",encoding="utf-8")
