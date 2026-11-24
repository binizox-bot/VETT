import json, sys, shutil
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT / "VETT_INTEGRATED_20261113" / "scripts"))
import build_one

AUDIT = json.loads((ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"dataset_audit.json").read_text(encoding="utf-8"))
CLOS = json.loads((ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"closure_audit_220.json").read_text(encoding="utf-8"))
per = {p["match"]: p for p in AUDIT["per_match"]}
clean = {r["match"]: r for r in CLOS["rows"] if r["n_bad"] == 0}
OUT = ROOT / "VETT_INTEGRATED_20261113" / "pilot10"

def terciles(vals):
    s = sorted(vals); n = len(s)
    return s[n//3], s[2*n//3]

pool = [p for m, p in per.items()
        if m in clean and p["innings_sections"] >= 2
        and "abandon" not in p["result"].lower() and "no result" not in p["result"].lower()]
lt1, lt2 = terciles([p["commentary_tokens"] for p in pool])
ct1, ct2 = terciles([p["L2"] + p["L3"] for p in pool])

def lbin(v): return 0 if v <= lt1 else (1 if v <= lt2 else 2)
def cbin(v): return 0 if v <= ct1 else (1 if v <= ct2 else 2)
def rbin(r):
    r = (r or "").lower()
    if "runs" in r: return "runs"
    if "wickets" in r: return "wickets"
    return "other"

for p in pool:
    p["lb"], p["cb"], p["rb"] = lbin(p["commentary_tokens"]), cbin(p["L2"] + p["L3"]), rbin(p["result"])

used, selected = set(), []
for lb in range(3):
    for cb in range(3):
        cand = [p for p in pool if p["lb"] == lb and p["cb"] == cb and p["match"] not in used]
        if not cand: continue
        seen = {p["rb"] for p in selected}
        cand.sort(key=lambda p: (p["rb"] in seen, abs(p["commentary_tokens"] - (1200 if lb == 0 else 1700 if lb == 1 else 2200))))
        used.add(cand[0]["match"]); selected.append(cand[0])
while len(selected) < 10:
    seen = {p["rb"] for p in selected}
    rest = [p for p in pool if p["match"] not in used]
    rest.sort(key=lambda p: (p["rb"] in seen, abs(p["commentary_tokens"] - 1700)))
    used.add(rest[0]["match"]); selected.append(rest[0])
selected = selected[:10]

selection = {"schema": "vett.integrated.pilot10.selection.v2",
             "rule": "closure-clean (n_bad=0), >=2 innings, playable result; stratified by commentary length x L2+L3 x result",
             "strata": {"length_terciles": [lt1, lt2], "complexity_terciles": [ct1, ct2]},
             "n": len(selected),
             "matches": [{k: p[k] for k in ("match","commentary_tokens","L2","L3","result","lb","cb","rb")} for p in selected]}
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"selection.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# rebuild cleanly
if OUT.exists() and OUT.name == "pilot10":
    for child in OUT.iterdir():
        if child.is_dir() and child.name.startswith("match_"):
            shutil.rmtree(child)
print("selected:", [(p["match"], p["commentary_tokens"], p["L2"]+p["L3"], p["rb"]) for p in selected])
rows = []
for p in selected:
    m = build_one.build(p["match"], OUT)
    rows.append({"match": p["match"], "fields": m["n_fields"], "closure_ok": m["closure_all_ok"],
                 "variants": {k: v["edit"].get("type") for k, v in m["variants"].items()},
                 "changed": len(m["variants"]["revised"].get("changed_fields", [])),
                 "unknown": len(m["variants"]["missing"].get("unknown_fields", []))})
    print(f"  {p['match']}: fields={m['n_fields']} closure={m['closure_all_ok']} "
          f"changed={rows[-1]['changed']} unknown={rows[-1]['unknown']}")
summary = {"schema": "vett.integrated.pilot10.build.v2", "rows": rows,
           "n_built": len(rows), "all_closure_ok": all(r["closure_ok"] for r in rows),
           "all_six_variants": all(len(r["variants"]) == 6 for r in rows)}
(OUT/"build_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("summary:", {k: summary[k] for k in ("n_built","all_closure_ok","all_six_variants")})
