import json
from pathlib import Path
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"attribution_evidence_followup"
dev={s["match"]:s for s in json.loads((P/"dev.json").read_text(encoding="utf-8"))}
rows=[json.loads(l) for l in (P/"runs/dev.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for r in rows:
    if r["match"]=="match_0008" and r["condition"] in "ABC":
        print(r["model"].split(":")[0],r["condition"],r.get("fields"))
print("\nC text:",dev["match_0008"]["C"][:900])
print("\nA has note:", "pre-revision" in dev["match_0008"]["A"], "C has note:", "pre-revision" in dev["match_0008"]["C"])
