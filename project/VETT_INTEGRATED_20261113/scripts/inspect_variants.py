import json, sys, difflib
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT / "VETT_INTEGRATED_20261113" / "scripts"))
import pilot_lib as L
d = ROOT / "VETT_INTEGRATED_20261113" / "pilot10" / "match_0001"
ctrl = (d/"variants/control/commentary.txt").read_text(encoding="utf-8")
rev = (d/"variants/revised/commentary.txt").read_text(encoding="utf-8")
mis = (d/"variants/missing/commentary.txt").read_text(encoding="utf-8")
shf = (d/"variants/shuffled/commentary.txt").read_text(encoding="utf-8")
print("sha equal ctrl/rev:", L.sha256(ctrl) == L.sha256(rev), "| ctrl/shf:", L.sha256(ctrl) == L.sha256(shf))
for name, txt in (("control", ctrl), ("revised", rev), ("missing", mis)):
    s = L.find_extras_sentence(txt)
    print(f"\n[{name}] extras sentence: {s}")
print("\nrevised edit log:", json.loads((d/"variants/revised/gold.json").read_text())["edit"])
print("changed:", json.loads((d/"variants/revised/gold.json").read_text())["changed_fields"])
# sentence-level diff between control and revised
a, b = L.sentences(ctrl), L.sentences(rev)
print("\nsentence counts:", len(a), len(b))
for i, (x, y) in enumerate(zip(a, b)):
    if x != y:
        print(f"  diff@{i}:\n    C: {x[:200]}\n    R: {y[:200]}")
