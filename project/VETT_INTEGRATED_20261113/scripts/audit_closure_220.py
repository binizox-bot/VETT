import sys, json
from pathlib import Path
from collections import Counter
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT / "VETT_INTEGRATED_20261113" / "scripts"))
import pilot_lib as L
DS = L.DATASET
rows, defects = [], Counter()
unsupported = []
for d in sorted(DS.glob("match_*")):
    try:
        md = L.parse_scorecard_full((d/"scorecard.md").read_text(encoding="utf-8"), d.name)
    except Exception as exc:
        unsupported.append({"match": d.name, "error": f"{type(exc).__name__}: {exc}"}); continue
    if len(md.innings) < 2:
        unsupported.append({"match": d.name, "error": f"innings={len(md.innings)}", "result": md.result}); continue
    cs = L.closure(md)
    bad = [c for c in cs if not c["ok"]]
    for c in bad:
        defects[c["id"].split(".")[-1]] += 1
    rows.append({"match": d.name, "n_inn": len(md.innings), "n_bad": len(bad),
                 "bad": [c["id"] for c in bad], "result": md.result,
                 "tokens": (d/"commentary.txt").stat().st_size // 4,
                 "L2L3": 0})
out = {"n": len(rows), "unsupported": unsupported, "defect_counts": dict(defects),
       "clean": sum(1 for r in rows if r["n_bad"] == 0), "rows": rows}
(ROOT/"VETT_INTEGRATED_20261113"/"analysis"/"closure_audit_220.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("parsed:", len(rows), "unsupported:", len(unsupported))
print("defect counts:", dict(defects))
print("clean:", out["clean"], "/", len(rows))
print("unsupported sample:", unsupported[:8])
bad_rows = [r for r in rows if r["n_bad"]][:8]
for r in bad_rows: print("  bad:", r["match"], r["bad"])
