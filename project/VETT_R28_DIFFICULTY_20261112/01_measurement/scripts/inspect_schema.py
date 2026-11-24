"""Structural inspection of R26.15 / R26.18 artifacts (stdlib only, no network).

Prints key trees with types/sizes and heavily truncated leaf samples so that
nothing large is materialised into the caller's context.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(
    os.path.dirname(ROOT),
    "VETT_Cricket_v0.22_R16_Multisource_Dilemmas",
)
DS = os.path.join(BASE, "r26_15_content_dependency_candidate_v3")
EVAL = os.path.join(
    BASE, "eval_runs", "r26_18_s5_20261112", "r26_18_glm53_canonical_set_sentinel5"
)

MAXLINES = 200
_out = []


def emit(line: str = "") -> None:
    _out.append(line)


def trunc(v, n=110):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[: n - 3] + "..."


def walk(obj, prefix="", depth=0, maxdepth=3):
    if depth > maxdepth:
        emit(f"{prefix} {type(obj).__name__} (maxdepth)")
        return
    if isinstance(obj, dict):
        emit(f"{prefix} dict[{len(obj)}] keys={list(obj)[:14]}")
        for k, v in list(obj.items())[:14]:
            walk(v, prefix + "." + str(k), depth + 1, maxdepth)
    elif isinstance(obj, list):
        emit(f"{prefix} list[{len(obj)}]")
        if obj:
            walk(obj[0], prefix + "[0]", depth + 1, maxdepth)
    else:
        emit(f"{prefix} {type(obj).__name__} = {trunc(obj)}")


def section(title):
    emit("")
    emit("=" * 4 + " " + title)


def main():
    pub = os.path.join(DS, "public", "match_0021", "public_instance.json")
    with open(pub, "r", encoding="utf-8") as f:
        p = json.load(f)
    section("PUBLIC INSTANCE TOP")
    walk(p, "pub", maxdepth=2)
    section("DECISION QUESTION SCHEMA [0]")
    walk(p["decision_question_schema"][0], "dq0", maxdepth=2)
    section("TARGET SCHEMA")
    walk(p["target_schema"], "ts", maxdepth=2)
    section("DOCUMENTS[0]")
    walk(p["documents"][0], "doc0", maxdepth=1)
    section("TASK")
    walk(p["task"], "task", maxdepth=2)

    gold = os.path.join(DS, "private", "match_0021", "private_gold.json")
    with open(gold, "r", encoding="utf-8") as f:
        g = json.load(f)
    section("PRIVATE GOLD TOP")
    walk(g, "gold", maxdepth=2)
    sec = g.get("answers") or g.get("records") or g.get("questions")
    if isinstance(sec, list) and sec:
        section("PRIVATE GOLD answers[0]")
        walk(sec[0], "ans0", maxdepth=3)
    elif isinstance(sec, dict):
        k = next(iter(sec))
        section("PRIVATE GOLD answers key " + k)
        walk(sec[k], "ans", maxdepth=3)

    ev = os.path.join(DS, "private", "match_0021", "private_evidence.json")
    with open(ev, "r", encoding="utf-8") as f:
        e = json.load(f)
    section("PRIVATE EVIDENCE TOP")
    walk(e, "ev", maxdepth=2)

    an = os.path.join(EVAL, "ANALYSIS.json")
    with open(an, "r", encoding="utf-8") as f:
        a = json.load(f)
    section("ANALYSIS TOP")
    walk(a, "an", maxdepth=2)

    ss = os.path.join(EVAL, "SEMANTIC_SCORES.json")
    with open(ss, "r", encoding="utf-8") as f:
        s = json.load(f)
    section("SEMANTIC_SCORES TOP")
    walk(s, "ss", maxdepth=2)

    with open(os.path.join(EVAL, "predictions.jsonl"), "r", encoding="utf-8") as f:
        line = f.readline()
    pr = json.loads(line)
    section("PREDICTIONS LINE 1")
    walk(pr, "pr", maxdepth=2)
    section("PREDICTIONS LINES")
    n = sum(1 for _ in open(os.path.join(EVAL, "predictions.jsonl"), encoding="utf-8"))
    emit(f"predictions.jsonl lines = {n}")
    with open(os.path.join(EVAL, "SEMANTIC_PREDICTIONS.jsonl"), encoding="utf-8") as f:
        pl = json.loads(f.readline())
    section("SEMANTIC PREDICTIONS LINE 1")
    walk(pl, "sp", maxdepth=2)

    sec2 = os.path.join(EVAL, "SEMANTIC_SCORES.json")
    with open(sec2, encoding="utf-8") as f:
        s2 = json.load(f)
    if "per_question" in s2:
        section("SEMANTIC_SCORES per_question[0]")
        walk(s2["per_question"][0], "pq", maxdepth=2)

    print("\n".join(_out[:MAXLINES]))
    if len(_out) > MAXLINES:
        print(f"... [{len(_out) - MAXLINES} lines elided]")


if __name__ == "__main__":
    main()
