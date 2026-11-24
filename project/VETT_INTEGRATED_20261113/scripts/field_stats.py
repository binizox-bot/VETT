import json, sys
from pathlib import Path
from collections import Counter
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
P = ROOT/"VETT_INTEGRATED_20261113"/"pilot10"
sel = json.loads((P/"selection.json").read_text(encoding="utf-8"))
tot = Counter(); per_match = []
unmentioned = Counter()
for s in sel["matches"]:
    rows = [json.loads(l) for l in (P/s["match"]/"fields.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    c = Counter(r["answerability"] for r in rows)
    tot.update(c)
    no_ev = [r["field_id"] for r in rows if r["answerability"] == "underdetermined"]
    for f in no_ev: unmentioned[f.split(".")[-1]] += 1
    per_match.append((s["match"], dict(c), len(no_ev)))
print("totals:", dict(tot), "of", sum(tot.values()))
for m,c,n in per_match: print(" ", m, c, "underdetermined=", n)
print("underdetermined suffixes:", unmentioned.most_common(10))
