"""Third pass: targeted metric extraction from ANALYSIS.json + predictions schema."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(os.path.dirname(ROOT), "VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
EVAL = os.path.join(
    BASE, "eval_runs", "r26_18_s5_20261112", "r26_18_glm53_canonical_set_sentinel5"
)
with open(os.path.join(EVAL, "ANALYSIS.json"), encoding="utf-8") as f:
    an = json.load(f)
s = an["protocol_evaluation"]["scores"]
for key in (
    "answer_prior_reference",
    "decision_field_accuracy_by_level",
    "decision_informative_field_accuracy_by_level",
    "full_record_exact_by_level",
    "full_record_exact_counts_by_level",
    "conditional_edge_link_f1_by_level",
    "minimal_evidence_edge_f1_by_level",
    "content_dependency_edge_f1_by_level",
    "content_dependency_gold_opportunity",
    "observed_informative_field_value_cells" if "observed_informative_field_value_cells" in s else "decision_informative_field_accuracy",
):
    if key in s:
        print(f"== {key} ==")
        print(json.dumps(s[key], ensure_ascii=False)[:1600])
        print()
print("scores keys:", sorted(s.keys()))
print()
print("== predictions line 1 (structure, truncated) ==")
with open(os.path.join(EVAL, "predictions.jsonl"), encoding="utf-8") as f:
    p = json.loads(f.readline())


def skel(o, d=0, maxd=3):
    pad = "  " * d
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                print(f"{pad}{k}: {type(v).__name__}[{len(v)}]")
                if d < maxd:
                    skel(v, d + 1, maxd)
            else:
                sv = str(v).replace("\n", "\\n")
                print(f"{pad}{k}: {type(v).__name__} = {sv[:90]}")
    elif isinstance(o, list) and o:
        print(f"{pad}[0] ->")
        skel(o[0], d + 1, maxd)


skel(p)
print()
print("== n lines / confidence distribution ==")
confs = []
n = 0
with open(os.path.join(EVAL, "predictions.jsonl"), encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        n += 1
        if "confidence" in r:
            confs.append(r["confidence"])
print("lines:", n, "conf n:", len(confs), "min/max:", min(confs) if confs else None, max(confs) if confs else None)
print("first 8 confidences:", [round(c, 4) for c in confs[:8]])
print("unique rounded:", sorted(set(round(c, 3) for c in confs))[:20])
