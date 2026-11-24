"""DeepTable eval: 3 local models x 4 conditions x 18 matches.

Reads DEEP_T2T/data/dossiers.jsonl + golds.jsonl, renders each dossier,
calls the frozen local service, parses the JSON table, and scores cells.

Outputs:
  DEEP_T2T/runs/<model>_<cond>.jsonl
  DEEP_T2T/results.json

Run:
  python DEEP_T2T/eval_deep.py --models qwen2.5:7b-instruct-q4_K_M --matches match_0001
  python DEEP_T2T/eval_deep.py            # full run, resumable
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOCAL = os.path.join(ROOT, "VETT_R28_DIFFICULTY_20261112", "03_build", "local")
sys.path.insert(0, LOCAL)

from local_inference import service  # noqa: E402

MODELS = ["qwen2.5:7b-instruct-q4_K_M", "llama3.1:8b", "gemma2:9b"]
CONDS = ["C0", "C1", "C2", "C3"]
NUM_CTX = 8192
NUM_PREDICT = 900
RUNS = os.path.join(HERE, "runs")


def load_jsonl(name: str) -> list[dict]:
    with open(os.path.join(HERE, "data", name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def render(row: dict) -> str:
    parts = [
        "You are a cricket scoring adjudicator. Read the dossier and complete the final match table.",
        "",
    ]
    for doc in row["documents"]:
        parts.append(f"=== {doc['doc_id']}: {doc['title']} ===")
        parts.append(doc["text"])
        parts.append("")
    parts.append("QUESTION\n" + row["question"])
    parts.append("\nJSON:\n")
    return "\n".join(parts)


def parse_json(raw: str):
    if not raw:
        return None
    txt = raw.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```[a-zA-Z]*\n?", "", txt)
        txt = re.sub(r"\n?```$", "", txt)
    try:
        return json.loads(txt)
    except Exception:
        pass
    start = txt.find("{")
    if start < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(txt[start:])
        return obj
    except Exception:
        return None


def get_path(obj, key: str):
    cur = obj
    for part in key.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(cur, dict):
            if part not in cur:
                return None
            cur = cur[part]
        else:
            return None
    return cur


def same(key: str, pred, gold) -> bool:
    if pred is None:
        return False
    if key.endswith("run_rate"):
        try:
            return abs(float(pred) - float(gold)) <= 0.05
        except (TypeError, ValueError):
            return False
    if isinstance(gold, (int, float)) and not isinstance(gold, bool):
        try:
            return float(pred) == float(gold)
        except (TypeError, ValueError):
            return False
    return str(pred).strip().lower() == str(gold).strip().lower()


def overs_decimal(o) -> float:
    s = str(o).strip()
    if "." not in s:
        try:
            return float(s)
        except ValueError:
            return 0.0
    whole, balls = s.split(".", 1)
    try:
        return int(whole) + int(balls) / 6.0
    except ValueError:
        return 0.0


def closure_violations(tbl) -> int:
    v = 0
    if not isinstance(tbl, dict):
        return 8
    inns = tbl.get("innings")
    if not isinstance(inns, list):
        return 8
    for inn in inns[:2]:
        if not isinstance(inn, dict):
            v += 4
            continue
        try:
            ex = sum(int(inn.get(k, 0)) for k in ["byes", "leg_byes", "no_balls", "wides"])
            if ex != int(inn.get("extras", -1)):
                v += 1
            total = int(inn.get("total_runs", 0))
            if total - ex < 0:
                v += 1
            if int(inn.get("bowling_runs", -1)) != total - int(inn.get("byes", 0)) - int(inn.get("leg_byes", 0)):
                v += 1
            od = overs_decimal(inn.get("overs", "0"))
            if od > 0 and abs(float(inn.get("run_rate", 0)) - total / od) > 0.05:
                v += 1
        except (TypeError, ValueError):
            v += 4
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--matches", nargs="*", default=None)
    ap.add_argument("--conds", nargs="*", default=None)
    args = ap.parse_args()

    models = args.models or MODELS
    conds = args.conds or CONDS
    dossiers = load_jsonl("dossiers.jsonl")
    golds = {(g["match_id"], g["condition"]): g for g in load_jsonl("golds.jsonl")}
    if args.matches:
        dossiers = [d for d in dossiers if d["match_id"] in set(args.matches)]
    dossiers = [d for d in dossiers if d["condition"] in conds]
    os.makedirs(RUNS, exist_ok=True)

    for tag in models:
        if tag not in {m.get("name") for m in service.list_models()}:
            print(f"SKIP {tag}: not pulled", flush=True)
            continue
        service.config.MODEL_TAG = tag
        for cond in conds:
            out_path = os.path.join(RUNS, f"{tag.replace(':', '_')}_{cond}.jsonl")
            done = set()
            if os.path.exists(out_path):
                for line in open(out_path, encoding="utf-8"):
                    try:
                        done.add(json.loads(line)["match_id"])
                    except Exception:
                        pass
            todo = [d for d in dossiers if d["condition"] == cond and d["match_id"] not in done]
            print(f"[{tag} {cond}] todo={len(todo)}", flush=True)
            with open(out_path, "a", encoding="utf-8", newline="\n") as fh:
                for d in todo:
                    prompt = render(d)
                    err = None
                    try:
                        gen = service.generate(prompt, num_ctx=NUM_CTX, num_predict=NUM_PREDICT)
                        raw = gen.get("raw_output") or ""
                        done_reason = gen.get("done_reason")
                    except Exception as exc:  # noqa: BLE001
                        raw, done_reason, err = "", None, f"{type(exc).__name__}: {exc}"
                    pred = parse_json(raw)
                    gold = golds[(d["match_id"], cond)]["cells"]
                    cells = {}
                    for k, gv in gold.items():
                        pv = get_path(pred, k) if pred else None
                        cells[k] = {"correct": same(k, pv, gv), "pred": pv, "gold": gv}
                    row = {
                        "match_id": d["match_id"], "condition": cond, "model": tag,
                        "prompt_chars": len(prompt), "raw_output": raw,
                        "done_reason": done_reason, "error": err,
                        "json_ok": pred is not None,
                        "cells": cells,
                        "cell_exact": sum(1 for c in cells.values() if c["correct"]) / len(cells),
                        "table_exact": all(c["correct"] for c in cells.values()),
                        "closure_violations": closure_violations(pred),
                    }
                    fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                    fh.flush()
                    print(f"  {d['match_id']} {cond} json={row['json_ok']} "
                          f"cell={row['cell_exact']:.3f} closure={row['closure_violations']}", flush=True)

    # summary
    summary = {}
    for tag in models:
        for cond in conds:
            path = os.path.join(RUNS, f"{tag.replace(':', '_')}_{cond}.jsonl")
            if not os.path.exists(path):
                continue
            rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
            if not rows:
                continue
            n = len(rows)
            ex = [c for r in rows for c in r["cells"].values()]
            summary[f"{tag}|{cond}"] = {
                "n": n,
                "json_ok": round(sum(1 for r in rows if r["json_ok"]) / n, 4),
                "cell_exact": round(sum(1 for c in ex if c["correct"]) / len(ex), 4),
                "table_exact": round(sum(1 for r in rows if r["table_exact"]) / n, 4),
                "closure_violation_rate": round(sum(1 for r in rows if r["closure_violations"] > 0) / n, 4),
                "closure_violations_mean": round(sum(r["closure_violations"] for r in rows) / n, 2),
            }
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump({"schema": "vett.deep_t2t.results.v1", "summary": summary}, fh, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
