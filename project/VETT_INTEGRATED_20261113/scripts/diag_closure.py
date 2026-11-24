import json, sys, traceback
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT / "VETT_INTEGRATED_20261113" / "scripts"))
import pilot_lib as L, build_one
for mid in ("match_0103", "match_0139", "match_0209", "match_0146"):
    c = json.loads((ROOT/"VETT_INTEGRATED_20261113"/"pilot10"/mid/"closure.json").read_text(encoding="utf-8"))
    print(mid, "failed:", c["failed"])
    for x in c["constraints"]:
        if not x["ok"]:
            print("   ", x["id"], "|", x["formula"], "|", x["lhs"], "vs", x["rhs"])
try:
    build_one.build("match_0004", ROOT/"VETT_INTEGRATED_20261113"/"pilot10")
except Exception:
    traceback.print_exc()
