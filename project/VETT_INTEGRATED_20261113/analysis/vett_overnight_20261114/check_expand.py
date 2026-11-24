from pathlib import Path
import json,os
P=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")/"VETT_INTEGRATED_20261113"/"analysis"/"vett_overnight_20261114"
print("manifest", (P/"expansion_manifest.json").exists())
if (P/"expansion_manifest.json").exists():
    M=json.loads((P/"expansion_manifest.json").read_text(encoding="utf-8")); print("roots",len(M),[x["match"] for x in M])
r=P/"runs"/"expand.jsonl"; print("rows",len(r.read_text(encoding="utf-8").splitlines()) if r.exists() else 0)
print("log", (P/"expand.log").read_text(encoding="utf-8")[-300:] if (P/"expand.log").exists() else "none")
