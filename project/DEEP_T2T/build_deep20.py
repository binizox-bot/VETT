"""DeepTable builder: 220-match scorecards -> 20 deep text-to-table dossiers.

For each match, parse scorecard.md into a compact gold table, inject
event-level scoring corrections (extras / batter runs), and render four
conditions:

  C0  commentary only (shallow baseline)
  C1  + correction memos + in-force 2026 circular
  C2  + superseded 2025 circular (version conflict)
  C3  C1 with one decisive memo removed (evidence-necessity test)

Output (append-only, new dir):
  DEEP_T2T/data/dossiers.jsonl   one row per (match, condition)
  DEEP_T2T/data/golds.jsonl      one row per (match, condition)
  DEEP_T2T/data/build_manifest.json

Run:
  python DEEP_T2T/build_deep20.py --limit 20
  python DEEP_T2T/build_deep20.py --limit 1 --only match_0001
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter

BASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Self-cricket-clean_text_scorecard_v1_220_matches",
)
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CONDITIONS = ("C0", "C1", "C2", "C3")

SUMMARY_FIELDS = [
    "total_runs", "wickets", "overs", "extras", "byes", "leg_byes",
    "no_balls", "wides", "run_rate", "bowling_runs",
]
BAT_FIELDS = ["name", "runs", "balls", "fours", "sixes"]
BOWL_FIELDS = ["name", "overs", "runs", "wickets"]


# ---------------------------- parsing ------------------------------------
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


def as_int(v, default=0):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return default


def as_float(v, default=0.0):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return default


def overs_decimal(o) -> float:
    s = str(o).strip()
    if "." not in s:
        return as_float(s)
    whole, balls = s.split(".", 1)
    return as_int(whole) + as_int(balls) / 6.0


def parse_match_info(tables):
    info = {}
    for t in tables:
        head, body = t[0], t[1:]
        if len(head) == 2 and head[0].lower() == "field":
            for row in body:
                if len(row) >= 2:
                    info[row[0]] = row[1]
    return info


def parse_innings(heading: str, tables) -> dict:
    team = heading.split(" - ")[0].strip()
    summary, batting, bowling = {}, [], []
    for t in tables:
        head, body = t[0], t[1:]
        h = " ".join(head).lower()
        if head and head[0].lower() == "field":
            for row in body:
                if len(row) >= 2:
                    summary[row[0]] = row[1]
        elif h.startswith("batter"):
            for row in body:
                if len(row) < 7:
                    continue
                batting.append({
                    "name": row[0], "dismissal": row[1],
                    "runs": as_int(row[2]), "balls": as_int(row[3]),
                    "fours": as_int(row[4]), "sixes": as_int(row[5]),
                })
        elif h.startswith("bowler"):
            for row in body:
                if len(row) < 8:
                    continue
                bowling.append({
                    "name": row[0], "overs": row[1], "maidens": as_int(row[2]),
                    "runs": as_int(row[3]), "wickets": as_int(row[4]),
                })
    total_txt = summary.get("Total", "")
    m = re.match(r"(\d+)/(\d+)\s*\(([\d.]+)\s*Overs?\)", total_txt)
    runs, wkts, overs = (int(m.group(1)), int(m.group(2)), m.group(3)) if m else (0, 0, "0")
    extras = as_int(summary.get("Total Extras"))
    byes = as_int(summary.get("Byes"))
    leg_byes = as_int(summary.get("Leg Byes"))
    no_balls = as_int(summary.get("No Balls"))
    wides = as_int(summary.get("Wides"))
    rr = as_float(summary.get("Run Rate"))
    max_part = as_int(summary.get("Max Partnership"))
    return {
        "team": team, "total_runs": runs, "wickets": wkts, "overs": overs,
        "extras": extras, "byes": byes, "leg_byes": leg_byes,
        "no_balls": no_balls, "wides": wides, "run_rate": rr,
        "max_partnership": max_part,
        "batting": batting, "bowling": bowling,
        "bowling_runs": runs - byes - leg_byes,
    }


def parse_scorecard(text: str) -> dict:
    lines = text.splitlines()
    idx = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), len(lines))
    info = parse_match_info(md_tables("\n".join(lines[:idx])))
    innings = []
    heads = [i for i, ln in enumerate(lines) if ln.startswith("## ")]
    for k, start in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        innings.append(parse_innings(lines[start][3:].strip(), md_tables("\n".join(lines[start:end]))))
    return {"info": info, "innings": innings}


def top_batters(rows, k=3):
    rows = [r for r in rows if r["balls"] > 0 or r["dismissal"]]
    rows.sort(key=lambda r: (-r["runs"], r["balls"], r["name"]))
    return [{f: r[f] for f in BAT_FIELDS} for r in rows[:k]]


def top_bowlers(rows, k=3):
    rows.sort(key=lambda r: (-r["wickets"], r["runs"], overs_decimal(r["overs"])))
    return [{f: r[f] for f in BOWL_FIELDS} for r in rows[:k]]


# ---------------------------- amendments --------------------------------
def amend(table: dict, drop: str | None = None) -> tuple[dict, list[str]]:
    """Apply deterministic event-level corrections; return (new_table, memos)."""
    import copy

    t = copy.deepcopy(table)
    inn0, inn1 = t["innings"][0], t["innings"][1]
    memos = []

    # A1: 2 byes were omitted in innings 0
    inn0["byes"] += 2
    memos.append(
        f"M1 in the {inn0['team']} innings: two deliveries that passed the keeper were "
        f"signalled as byes but were not entered on the scorecard. Add them."
    )

    # A2: top scorer's individual score corrected +2
    scorers = sorted([b for b in inn0["batting"] if b["balls"] > 0],
                     key=lambda b: (-b["runs"], b["name"]))
    if scorers:
        b = scorers[0]
        if drop != "M2":
            b["runs"] += 2
            memos.append(
                f"M2 in the {inn0['team']} innings: {b['name']}'s score was corrected from "
                f"{b['runs'] - 2} to {b['runs']}; two runs were credited to the wrong batter."
            )

    # A3: one wide in innings 1 was a no-ball
    if inn1["wides"] > 0:
        inn1["wides"] -= 1
        inn1["no_balls"] += 1
        memos.append(
            f"M3 in the {inn1['team']} innings: one delivery recorded as a wide was in fact "
            f"a no-ball; no runs were scored off the bat."
        )

    for inn in (inn0, inn1):
        batting = sum(b["runs"] for b in inn["batting"])
        inn["extras"] = inn["byes"] + inn["leg_byes"] + inn["no_balls"] + inn["wides"]
        inn["total_runs"] = batting + inn["extras"]
        inn["bowling_runs"] = inn["total_runs"] - inn["byes"] - inn["leg_byes"]
        inn["run_rate"] = round(inn["total_runs"] / overs_decimal(inn["overs"]), 2)
        for b in inn["batting"]:
            b["sr"] = round(100 * b["runs"] / b["balls"], 2) if b["balls"] else 0.0

    t["innings"][0]["top_batters"] = top_batters(t["innings"][0]["batting"])
    t["innings"][1]["top_batters"] = top_batters(t["innings"][1]["batting"])
    t["innings"][0]["top_bowlers"] = top_bowlers(t["innings"][0]["bowling"])
    t["innings"][1]["top_bowlers"] = top_bowlers(t["innings"][1]["bowling"])
    return t, memos


def finish(table: dict) -> dict:
    import copy

    t = copy.deepcopy(table)
    for inn in t["innings"]:
        inn["top_batters"] = top_batters(inn["batting"])
        inn["top_bowlers"] = top_bowlers(inn["bowling"])
    return t


# ---------------------------- cells -------------------------------------
def cells(table: dict) -> dict:
    c = {}
    for i, inn in enumerate(table["innings"]):
        for f in SUMMARY_FIELDS:
            c[f"innings.{i}.{f}"] = inn[f]
        for j, b in enumerate(inn["top_batters"]):
            for f in BAT_FIELDS:
                c[f"innings.{i}.top_batters.{j}.{f}"] = b[f]
        for j, b in enumerate(inn["top_bowlers"]):
            for f in BOWL_FIELDS:
                c[f"innings.{i}.top_bowlers.{j}.{f}"] = b[f]
    c["result"] = table["info"].get("Result", "")
    c["pom"] = table["info"].get("Player of the Match", "")
    return c


# ---------------------------- dossier -----------------------------------
def doc(doc_id: str, title: str, text: str) -> dict:
    return {"doc_id": doc_id, "title": title, "text": text}


def build_dossier(match: str, table: dict, cond: str, memos: list[str], distractors: list[tuple[str, str]]) -> dict:
    info = table["info"]
    i0, i1 = table["innings"]
    docs = [
        doc("D0", "Match setting", f"Venue: {info.get('Venue', '')}\nToss: {info.get('Toss', '')}\n"
            f"Teams: {i0['team']} vs {i1['team']}\nResult: {info.get('Result', '')}\n"
            f"Player of the Match: {info.get('Player of the Match', '')}"),
        doc("D1", "Match commentary", open(os.path.join(BASE, match, "commentary.txt"), encoding="utf-8").read()),
    ]
    if cond != "C0":
        body = "\n\n".join(memos) if memos else "(no corrections)"
        docs.append(doc("D2", "Scoring correction memos", body))
        docs.append(doc("D3", "Scoring circular 2026 (in force)",
                        "Law 17.3 (2026): byes and leg byes are not charged to any bowler. "
                        "Run rate is total runs divided by overs (balls/6)."))
        if cond == "C2":
            docs.append(doc("D4", "Scoring circular 2025 (superseded)",
                            "Law 17.3 (2025): byes are charged to the bowler's analysis; "
                            "leg byes are not charged."))
            docs.append(doc("D5", "Match conditions memo",
                            "For this match the 2026 scoring circular is in force and supersedes the 2025 circular."))
    for k, (m, text) in enumerate(distractors):
        docs.append(doc(f"X{k+1}", f"Reference match {m} (different match, not this one)", text))
    question = (
        "Complete the final match table for THIS match after applying every in-force correction. "
        "Rules: totals must close (batting runs + extras = total; extras = byes + leg byes + no balls + wides; "
        "bowling runs = total - byes - leg byes); run rate = total / (overs + balls/6). "
        "Use only documents about this match; ignore reference matches. "
        "Output ONE JSON object with keys: match_id, innings (two objects with team, total_runs, wickets, "
        "overs, extras, byes, leg_byes, no_balls, wides, run_rate, bowling_runs, top_batters "
        "[3 x {name, runs, balls, fours, sixes}], top_bowlers [3 x {name, overs, runs, wickets}]), "
        "result, player_of_match. Numbers only; no prose."
    )
    return {"schema": "vett.deep_t2t.dossier.v1", "match_id": match, "condition": cond,
            "documents": docs, "question": question,
            "input_bytes": sum(len(d["text"].encode("utf-8")) for d in docs)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--only", default=None)
    ap.add_argument("--distractors", type=int, default=2)
    args = ap.parse_args()

    matches = sorted(d for d in os.listdir(BASE) if d.startswith("match_"))
    if args.only:
        matches = [m for m in matches if m == args.only]
    matches = matches[: args.limit]

    os.makedirs(OUT_DIR, exist_ok=True)
    dossiers, golds = [], []
    for idx, m in enumerate(matches):
        sc = open(os.path.join(BASE, m, "scorecard.md"), encoding="utf-8").read()
        table = parse_scorecard(sc)
        if len(table["innings"]) != 2:
            continue
        base = finish(table)
        amended, memos = amend(table)
        c3, memos3 = amend(table, drop="M2")

        gold_by_cond = {"C0": cells(base), "C1": cells(amended), "C2": cells(amended), "C3": cells(c3)}

        distr = []
        for k in range(args.distractors):
            dm = matches[(idx + 1 + k) % len(matches)]
            if dm == m:
                continue
            distr.append((dm, open(os.path.join(BASE, dm, "commentary.txt"), encoding="utf-8").read()))

        for cond in CONDITIONS:
            if cond == "C3":
                dd = build_dossier(m, base, cond, memos3, distr)
            else:
                dd = build_dossier(m, base, cond, memos, distr) if cond != "C0" else build_dossier(m, base, cond, [], distr)
            dossiers.append(dd)
            golds.append({"schema": "vett.deep_t2t.gold.v1", "match_id": m, "condition": cond,
                          "cells": gold_by_cond[cond]})

    with open(os.path.join(OUT_DIR, "dossiers.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for d in dossiers:
            f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(OUT_DIR, "golds.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for g in golds:
            f.write(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n")

    manifest = {
        "schema": "vett.deep_t2t.build_manifest.v1",
        "n_matches": len(matches),
        "n_dossiers": len(dossiers),
        "conditions": list(CONDITIONS),
        "distractors": args.distractors,
        "input_bytes_mean": round(sum(d["input_bytes"] for d in dossiers) / len(dossiers), 1) if dossiers else 0,
        "input_bytes_by_cond": {
            c: round(sum(d["input_bytes"] for d in dossiers if d["condition"] == c) /
                     max(1, sum(1 for d in dossiers if d["condition"] == c)), 1)
            for c in CONDITIONS
        },
        "n_cells_per_dossier": len(golds[0]["cells"]) if golds else 0,
        "sha256": hashlib.sha256(
            open(os.path.join(OUT_DIR, "dossiers.jsonl"), "rb").read()
        ).hexdigest(),
    }
    with open(os.path.join(OUT_DIR, "build_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
