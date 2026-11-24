import json
from collections import defaultdict
from pathlib import Path

rel = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas\r26_15_content_dependency_candidate_v3")
summary = json.loads((rel / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))

by_record = defaultdict(list)
answers = []
for m in summary["match_ids"]:
    g = json.loads((rel / "private" / m / "private_gold.json").read_text(encoding="utf-8"))
    for a in g["decision_answers"]:
        answers.append((m, a))
        key = json.dumps(a["decision_record_flat"], sort_keys=True)
        by_record[key].append((a["level"], a["scenario_family"], a["question_id"]))

print("total questions:", len(answers))
print("distinct factual records:", len(by_record))
print()
print("=== records shared by more than one family ===")
collisions = {k: v for k, v in by_record.items() if len({x[1] for x in v}) > 1}
print("colliding records:", len(collisions))
for key, rows in sorted(collisions.items(), key=lambda kv: -len(kv[1])):
    fams = sorted({r[1] for r in rows})
    lvls = sorted({r[0] for r in rows})
    print(f"\n  shared by {len(fams)} families, levels {lvls}:")
    for f in fams:
        print("     ", f)
    rec = json.loads(key)
    print("      record:", {k: v for k, v in rec.items() if k in ("batter_runs", "bowler_runs", "delivery_status", "dismissal", "total_runs", "ledger.NO_BALL_EXTRA", "ledger.WIDE_EXTRA", "ledger.BATTER")})

print()
print("=== families per distinct record, by level ===")
for level in ["L1", "L2", "L3", "L4", "L5"]:
    keys = {json.dumps(a["decision_record_flat"], sort_keys=True) for m, a in answers if a["level"] == level}
    fams = {a["scenario_family"] for m, a in answers if a["level"] == level}
    print(f"  {level}: {len(fams)} families -> {len(keys)} distinct records")

print()
print("=== does the counterfactual differ where the factual record does not? ===")
for key, rows in collisions.items():
    cf_keys = set()
    for level, fam, qid in rows:
        for m, a in answers:
            if a["question_id"] == qid:
                cf_keys.add(json.dumps(a["counterfactual"]["decision_record_flat"], sort_keys=True))
    print(f"  record shared by {sorted({r[1] for r in rows})} -> {len(cf_keys)} distinct counterfactual records")
