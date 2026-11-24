import sys
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT/"VETT_INTEGRATED_20261113"/"scripts"))
import pilot_lib as L
for mid in ("match_0090","match_0167","match_0203"):
    md = L.parse_scorecard_full((L.DATASET/mid/"scorecard.md").read_text(encoding="utf-8"), mid)
    v = L.build_variants(md,0)["revised_hard"]
    print(mid, v["edit"].get("type"), v["edit"].get("innings"), "changed:", v["changed_fields"],
          "closure_ok:", all(c["ok"] for c in L.closure(md)))
