import json, sys
from pathlib import Path
ROOT = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017")
sys.path.insert(0, str(ROOT/"VETT_INTEGRATED_20261113"/"scripts"))
import pilot_lib as L

P = ROOT/"VETT_INTEGRATED_20261113"/"pilot10"
sel = json.loads((P/"selection.json").read_text(encoding="utf-8"))
report = {"schema": "vett.integrated.pilot10.validation.v1", "matches": [], "checks": {}}
allok = True

def ok(cond, name, detail=""):
    global allok
    if not cond: allok = False
    return {"check": name, "ok": bool(cond), "detail": detail}

for s in sel["matches"]:
    mid = s["match"]; d = P/mid
    md = L.parse_scorecard_full((d/"source/scorecard.md").read_text(encoding="utf-8"), mid)
    roster = L.target_roster(md)
    c0 = L.closure(md)
    m2, log = L.mutate_extras_swap(md, 2)
    c2 = L.closure(m2)
    g0 = L.target_fields(md, roster); g2 = L.target_fields(m2, roster)
    changed = sorted(k for k in g0 if g0[k]["value"] != g2[k]["value"])
    man = json.loads((d/"manifest.json").read_text(encoding="utf-8"))
    texts = {v: (d/"variants"/v/"commentary.txt").read_text(encoding="utf-8") for v in man["variants"]}
    checks = [
        ok(all(c["ok"] for c in c0), "closure_base"),
        ok(all(c["ok"] for c in c2), "closure_revised"),
        ok(len(man["variants"]) >= 6, "six_variants", str(list(man["variants"]))),
        ok(("revision_inline" not in man["variants"])
           or (json.loads((d/"variants/revision_inline/gold.json").read_text(encoding="utf-8"))["gold"]["match.pom"]
               != g0["match.pom"]["value"]), "inline_revision_changes_pom"),
        ok(L.sha256(texts["control"]) != L.sha256(texts["revised"]), "control_ne_revised"),
        ok(L.sha256(texts["control"]) != L.sha256(texts["shuffled"]), "control_ne_shuffled"),
        ok(changed == man["variants"]["revised"]["changed_fields"], "changed_fields_match", str(changed)),
        ok(len(changed) >= 3, "revised_multi_field", str(len(changed))),
        ok(not man["variants"]["control"]["leak_tokens"], "no_leak_control"),
        ok(all(not v["leak_tokens"] for v in man["variants"].values()), "no_leak_all"),
        ok(any(L.mentioned(texts["revised"], k, g2[k]["value"]) for k in changed), "revised_change_is_expressed"),
    ]
    # determinism
    t1 = L.render(md, 0); t2 = L.render(md, 0)
    checks.append(ok(t1 == t2, "deterministic_render"))
    # gold identity across non-revised variants
    g_ctrl = json.loads((d/"variants/control/gold.json").read_text(encoding="utf-8"))["gold"]
    for v in ("shuffled", "conflict", "distractor"):
        gv = json.loads((d/"variants"/v/"gold.json").read_text(encoding="utf-8"))["gold"]
        checks.append(ok(gv == g_ctrl, f"gold_equal_{v}", v))
    if not all(c["ok"] for c in checks):
        allok = False
    report["matches"].append({"match": mid, "checks": checks,
                              "n_fields": len(g0), "n_changed": len(changed),
                              "unknown": man["variants"]["missing"]["unknown_fields"]})

report["checks"]["all_matches_ok"] = allok
report["checks"]["n_matches"] = len(report["matches"])
(P/"validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

fails = [(m["match"], [c for c in m["checks"] if not c["ok"]]) for m in report["matches"]]
print("matches:", len(report["matches"]), "all_ok:", allok)
for mid, bad in fails:
    if bad:
        print("  FAIL", mid, [(c["check"], c["detail"]) for c in bad])
for m in report["matches"]:
    print(f"  {m['match']}: fields={m['n_fields']} changed={m['n_changed']} unknown={m['unknown']}")
