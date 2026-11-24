import hashlib, json
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
INT = ROOT/"VETT_INTEGRATED_20261113"
files = [INT/"PILOT_PREREGISTRATION.md", INT/"pilot10"/"selection.json",
         INT/"pilot10"/"validation.json", INT/"analysis"/"closure_audit_220.json"]
entries = []
for f in files:
    b = f.read_bytes()
    entries.append({"path": str(f.relative_to(INT)).replace("\\","/"), "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)})
doc = {"schema": "vett.integrated.pilot10.prereg_freeze.v1", "files": entries}
(INT/"prereg_freeze.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(doc, indent=1))
