import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_evidence_upgrade_20261115"
S=json.loads((P/"U_SAMPLE_MANIFEST.json").read_text(encoding="utf-8"))
idx=[]; dm=[]
for x in S:
    dm.append({"match":x["match"],"innings":x["innings"],"team":x["team"],"group":x["group"],"text_sha256":x["sha"],"variants":["O"],"status":"ready"})
    for f,v in [("total_runs",x["runs"]),("total_wickets",x["wickets"])]:
        idx.append({"match":x["match"],"innings":x["innings"],"team":x["team"],"field":f,"value":v,"source":"scorecard/published commentary","status":"pending_human_review","auto_rule":"none","r28_id":None})
(P/"EVIDENCE_INDEX.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in idx)+"\n",encoding="utf-8")
(P/"DIAGNOSTIC_MANIFEST.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in dm)+"\n",encoding="utf-8")
print("idx",len(idx),"dm",len(dm))
