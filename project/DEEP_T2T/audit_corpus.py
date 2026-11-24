"""Corpus audit for the deep text-to-table merge (220-match scorecard corpus).

Read-only. Counts table cells per match, evidence-chain levels, and text sizes.
Outputs DEEP_T2T/corpus_audit.json.

Run: python DEEP_T2T/audit_corpus.py
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict

BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Self-cricket-clean_text_scorecard_v1_220_matches",
)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus_audit.json")


def md_tables(text: str) -> list[list[list[str]]]:
    tables, cur = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            cur.append(line)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    out = []
    for t in tables:
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in t]
        rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
        if rows:
            out.append(rows)
    return out


def table_kind(header: list[str]) -> str:
    h = " ".join(header).lower()
    if "field" in h and "value" in h:
        return "summary"
    if h.startswith("batter"):
        return "batting"
    if h.startswith("bowler"):
        return "bowling"
    if h.startswith("partnership"):
        return "partnership"
    if h.startswith("wkt"):
        return "fow"
    return "other"


def main() -> int:
    matches = sorted(d for d in os.listdir(BASE) if d.startswith("match_"))
    per_match = []
    totals = Counter()
    kinds = Counter()
    levels = Counter()
    text_bytes = Counter()
    for m in matches:
        d = os.path.join(BASE, m)
        sc_path = os.path.join(d, "scorecard.md")
        ev_path = os.path.join(d, "evidence_chain.md")
        cm_path = os.path.join(d, "commentary.txt")
        if not (os.path.exists(sc_path) and os.path.exists(ev_path)):
            continue
        sc = open(sc_path, encoding="utf-8").read()
        ev = open(ev_path, encoding="utf-8").read()
        cm = open(cm_path, encoding="utf-8").read() if os.path.exists(cm_path) else ""
        tables = md_tables(sc)
        cells = 0
        for t in tables:
            header, body = t[0], t[1:]
            kind = table_kind(header)
            kinds[kind] += 1
            n = len(body) * len(header)
            totals[kind] += n
            cells += n
        lv = Counter()
        for line in ev.splitlines():
            mm = re.match(r"\|\s*(L[123])\s*\|", line)
            if mm:
                lv[mm.group(1)] += 1
                levels[mm.group(1)] += 1
        text_bytes["scorecard"] += len(sc.encode("utf-8"))
        text_bytes["evidence"] += len(ev.encode("utf-8"))
        text_bytes["commentary"] += len(cm.encode("utf-8"))
        per_match.append(
            {
                "match": m,
                "tables": len(tables),
                "cells": cells,
                "batting_rows": sum(len(t) - 1 for t in tables if table_kind(t[0]) == "batting"),
                "bowling_rows": sum(len(t) - 1 for t in tables if table_kind(t[0]) == "bowling"),
                "evidence": {k: lv.get(k, 0) for k in ("L1", "L2", "L3")},
            }
        )

    n = len(per_match)
    summary = {
        "schema": "vett.deep_t2t.corpus_audit.v1",
        "n_matches": n,
        "cells_total": sum(p["cells"] for p in per_match),
        "cells_mean": round(sum(p["cells"] for p in per_match) / n, 1) if n else 0,
        "cells_by_kind": dict(totals),
        "tables_by_kind": dict(kinds),
        "evidence_rows": dict(levels),
        "evidence_share": {k: round(levels[k] / sum(levels.values()), 3) for k in ("L1", "L2", "L3")}
        if sum(levels.values())
        else {},
        "text_kb_mean": {k: round(v / n / 1024, 1) for k, v in text_bytes.items()} if n else {},
        "per_match_first5": per_match[:5],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "per_match": per_match}, fh, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
