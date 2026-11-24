import json
from pathlib import Path

rel = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_Cricket_v0.22_R16_Multisource_Dilemmas\r26_15_content_dependency_candidate_v3")
summary = json.loads((rel / "RELEASE_SUMMARY.json").read_text(encoding="utf-8"))

targets = ["L2_NB_BAT_FOUR", "L1_LEGAL_FOUR", "L2_NB_BOWLED", "L1_LEGAL_BOWLED", "L3_CATCH_BOUNDARY", "L4_REVIEW_CATCH_CONTROL"]
seen = {}
for m in summary["match_ids"]:
    g = json.loads((rel / "private" / m / "private_gold.json").read_text(encoding="utf-8"))
    for a in g["decision_answers"]:
        fam = a["scenario_family"]
        if fam in targets and fam not in seen:
            seen[fam] = (m, a)

for fam in targets:
    if fam not in seen:
        continue
    m, a = seen[fam]
    print("=" * 90)
    print(f"{fam}   ({m} / {a['question_id']})  level={a['level']}")
    print("  scenario:", a.get("scenario_family"))
    print("  factual   :", json.dumps({k: v for k, v in a["decision_record_flat"].items()}, sort_keys=True))
    print("  state     :", json.dumps(a["state"], sort_keys=True))
    cf = a["counterfactual"]
    print("  changed   :", cf["changed_field"], ":", cf["old_value"], "->", cf["new_value"])
    print("  cf record :", json.dumps({k: v for k, v in cf["decision_record_flat"].items()}, sort_keys=True))
    print("  cf state  :", json.dumps(cf["state"], sort_keys=True))
    print("  required facts:", a.get("required_fact_fields"))
    print("  rule keys:", a.get("rule_keys"))
    print("  solver facts:", json.dumps(a.get("solver_facts"), sort_keys=True))
