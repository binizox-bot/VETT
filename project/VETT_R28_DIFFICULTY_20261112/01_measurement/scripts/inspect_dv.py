"""Inventory difficulty_vector / difficulty_graph / state keys across all 100 questions."""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(os.path.dirname(ROOT), "VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
DS = os.path.join(BASE, "r26_15_content_dependency_candidate_v3")

with open(os.path.join(DS, "RELEASE_SUMMARY.json"), encoding="utf-8") as f:
    summary = json.load(f)
matches = list(map(str, summary["match_ids"]))
print("matches:", len(matches), matches)

dv_keys = Counter()
dv_types = defaultdict(set)
dv_vals = defaultdict(set)
dg_keys = Counter()
dg_vals = defaultdict(set)
state_keys = Counter()
state_vals = defaultdict(set)
scen = Counter()
anchor = Counter()
levels = Counter()
n_q = 0
distractors = Counter()
minspan = Counter()
for mid in matches:
    with open(os.path.join(DS, "private", mid, "private_gold.json"), encoding="utf-8") as f:
        g = json.load(f)
    for a in g["decision_answers"]:
        n_q += 1
        levels[a["level"]] += 1
        scen[a.get("scenario_family")] += 1
        anchor[a.get("cross_level_anchor_family")] += 1
        distractors[len(a.get("distractor_spans", []))] += 1
        minspan[len(a.get("minimum_evidence_spans", []))] += 1
        for k, v in a.get("difficulty_vector", {}).items():
            dv_keys[k] += 1
            dv_types[k].add(type(v).__name__)
            if len(dv_vals[k]) < 25 and not isinstance(v, (list, dict)):
                dv_vals[k].add(str(v))
        for k, v in a.get("difficulty_graph", {}).items():
            dg_keys[k] += 1
            if len(dg_vals[k]) < 25 and not isinstance(v, (list, dict)):
                dg_vals[k].add(str(v))
        for k, v in a.get("state", {}).items():
            state_keys[k] += 1
            if len(state_vals[k]) < 25:
                state_vals[k].add(str(v))
print(f"\nquestions={n_q} levels={dict(levels)}")
print(f"\nscenario_family distinct={len(scen)} counts={sorted(scen.values())}")
for s, c in sorted(scen.items()):
    print(f"  {s}: {c}")
print(f"\ncross_level_anchor_family distinct={len(anchor)}")
for s, c in sorted(anchor.items()):
    print(f"  {s}: {c}")
print(f"\ndistractor_spans count hist={dict(sorted(distractors.items()))}")
print(f"minimum_evidence_spans count hist={dict(sorted(minspan.items()))}")
print("\n== difficulty_vector keys (count/100, types) ==")
for k in sorted(dv_keys):
    vals = sorted(dv_vals[k])
    print(f"  {k}: n={dv_keys[k]} types={sorted(dv_types[k])} vals={vals[:18]}")
print("\n== difficulty_graph keys ==")
for k in sorted(dg_keys):
    print(f"  {k}: n={dg_keys[k]} vals={sorted(dg_vals[k])[:18]}")
print("\n== state keys ==")
for k in sorted(state_keys):
    print(f"  {k}: n={state_keys[k]} vals={sorted(state_vals[k])}")
