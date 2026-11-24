import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"
fa=[json.loads(l) for l in (P/"input_and_score_audit"/"FIELD_ANSWERABILITY.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
samp=json.loads((P/"answerability_and_short_evidence"/"sample.json").read_text(encoding="utf-8"))
ids={x["match"]+"|"+x["field"]:x["sample_id"] for x in samp}
out=[]
for x in fa:
    y=dict(x); y["v2_status"]=x["status"]; y["review_status"]="pending_human"; y["sample_id"]=ids.get(x["match"]+"|"+x["field"])
    out.append(y)
(P/"answerability_and_short_evidence"/"FIELD_ANSWERABILITY_V2.jsonl").write_text("\n".join(json.dumps(y,ensure_ascii=False) for y in out)+"\n",encoding="utf-8")
print(len(out),"sampled",sum(1 for y in out if y["sample_id"]))
