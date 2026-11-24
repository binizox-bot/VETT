import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"
fa=[json.loads(l) for l in (P/"small_model_diagnostics_v1"/"FIELD_ANSWERABILITY_V3.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for x in fa:
    if x["match"]=="match_0008" and "total_wickets" in x["field"]: print(x)
out=[]
for x in fa:
    y=dict(x); y["v4_status"]=x["v3_status"]; y["review_status"]="pending_human"; y["change_reason_v4"]="no new verified rule; V4 preserves 73"
    out.append(y)
(P/"small_model_diagnostics_v2"/"FIELD_ANSWERABILITY_V4.jsonl").write_text("\n".join(json.dumps(y,ensure_ascii=False) for y in out)+"\n",encoding="utf-8")
print("v4",len(out),"answerable",sum(1 for y in out if y["v4_status"] in ("direct","derived")))
