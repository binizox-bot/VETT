import sys, json
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT/"VETT_INTEGRATED_20261113"/"scripts"))
import pilot_lib as L
mid = "match_0090"
md = L.parse_scorecard_full((L.DATASET/mid/"scorecard.md").read_text(encoding="utf-8"), mid)
v = L.build_variants(md, 0)
print("variants:", list(v))
rv = v.get("revision_inline")
print("edit:", rv["edit"])
print("changed:", rv["changed_fields"])
print("gold pom:", rv["gold"]["match.pom"]["value"], "| control pom:", md.player_of_match)
print("tail:", rv["text"][-180:])
print("closure base ok:", all(c["ok"] for c in L.closure(md)))
