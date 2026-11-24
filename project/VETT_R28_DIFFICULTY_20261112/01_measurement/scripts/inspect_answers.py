"""Second structural pass: decision answers, difficulty vectors, ANALYSIS metrics."""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(os.path.dirname(ROOT), "VETT_Cricket_v0.22_R16_Multisource_Dilemmas")
DS = os.path.join(BASE, "r26_15_content_dependency_candidate_v3")
EVAL = os.path.join(
    BASE, "eval_runs", "r26_18_s5_20261112", "r26_18_glm53_canonical_set_sentinel5"
)
out = []


def emit(s=""):
    out.append(s)


def trunc(v, n=100):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[: n - 3] + "..."


def flat_leaves(obj, prefix="", maxdepth=3, depth=0):
    if isinstance(obj, dict):
        if depth >= maxdepth:
            emit(f"{prefix} dict[{len(obj)}] keys={list(obj)[:10]}")
            return
        for k, v in obj.items():
            flat_leaves(v, f"{prefix}.{k}", maxdepth, depth + 1)
    elif isinstance(obj, list):
        emit(f"{prefix} list[{len(obj)}] sample={trunc(obj[:3])}")
    else:
        emit(f"{prefix} {type(obj).__name__} = {trunc(obj)}")


with open(os.path.join(DS, "private", "match_0021", "private_gold.json"), encoding="utf-8") as f:
    g = json.load(f)
da = g["decision_answers"]
emit(f"decision_answers n={len(da)}")
for i, a in enumerate(da):
    emit(f"[{i}] level={a.get('level')} keys={list(a.keys())}")
emit("")
emit("== decision_answers[0] diff-vector / level / record ==")
for k in ("level", "difficulty_vector", "difficulty_graph", "cross_level_anchor_family",
          "evidence_graph_contract", "content_dependency_edge_count", "content_dependency_design_revision"):
    emit(f"-- {k}: {trunc(da[0].get(k), 700)}")
emit("")
emit("== decision_record[0] ==")
flat_leaves(da[0]["decision_record"], "rec", maxdepth=3)
emit("")
emit("== decision_record_flat[0] ==")
flat_leaves(da[0]["decision_record_flat"], "flat", maxdepth=2)
emit("")
emit("== counterfactual[0] ==")
flat_leaves(da[0]["counterfactual"], "cf", maxdepth=2)
emit("")
emit("== all levels/difficulty vectors of the 5 answers ==")
for i, a in enumerate(da):
    emit(f"[{i}] {a.get('level')} dv={trunc(a.get('difficulty_vector'), 500)}")

emit("")
emit("== ANALYSIS.json ==")
with open(os.path.join(EVAL, "ANALYSIS.json"), encoding="utf-8") as f:
    an = json.load(f)
flat_leaves(an, "an", maxdepth=3)

emit("")
emit("== predictions.jsonl line 1 ==")
with open(os.path.join(EVAL, "predictions.jsonl"), encoding="utf-8") as f:
    p1 = json.loads(f.readline())
flat_leaves(p1, "pr", maxdepth=3)

emit("")
emit("== SEMANTIC_SCORES.json ==")
with open(os.path.join(EVAL, "SEMANTIC_SCORES.json"), encoding="utf-8") as f:
    ss = json.load(f)
flat_leaves(ss, "ss", maxdepth=3)

print("\n".join(out[:200]))
if len(out) > 200:
    print(f"... [{len(out) - 200} lines elided]")
