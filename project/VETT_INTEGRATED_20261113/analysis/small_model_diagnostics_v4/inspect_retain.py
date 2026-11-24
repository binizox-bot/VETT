import json
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017"); INT=ROOT/"VETT_INTEGRATED_20261113"; V4=INT/"analysis"/"small_model_diagnostics_v4"
R=[json.loads(l) for l in (V4/"runs"/"no_decision.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for r in R:
    if r["notice"]=="retain" and r["match"] in ("match_0042","match_0044"):
        print(r["match"],r["model"].split(":")[0],r.get("parsed"))
# V5 copy of V4 fields with 6 verified
src=INT/"analysis"/"small_model_diagnostics_v2"/"FIELD_ANSWERABILITY_V4.jsonl"
rows=[json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
new={"match_0008|inn1.total_runs","match_0008|inn1.total_wickets","match_0010|inn1.total_runs","match_0010|inn1.total_wickets","match_0012|inn2.total_runs","match_0012|inn2.total_wickets"}
out=[]
for x in rows:
    y=dict(x); y["v5_status"]=x["v4_status"]; y["human_status"]="not_reviewed"
    if x["match"]+"|"+x["field"] in new: y["verification"]="auto_verified_sentence"; y["verified_by"]="script"
    out.append(y)
(V4/"FIELD_ANSWERABILITY_V5.jsonl").write_text("\n".join(json.dumps(y,ensure_ascii=False) for y in out)+"\n",encoding="utf-8")
print("v5",len(out),"answerable",sum(1 for y in out if y["v5_status"] in ("direct","derived")))
