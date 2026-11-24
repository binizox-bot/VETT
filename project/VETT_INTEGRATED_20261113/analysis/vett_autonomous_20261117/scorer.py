
"""Scoring, paired comparisons, counterexamples, and research memory."""
from __future__ import annotations

import json
from collections import defaultdict

import vettlib as V


def _load_results(con, batch_id: str) -> list:
    rows = con.execute("SELECT r.*, t.fields_json FROM results r JOIN tasks t USING(task_key) "
                       "WHERE r.batch_id=? ORDER BY r.created_at", (batch_id,)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["parsed"] = json.loads(d["parsed_json"]) if d.get("parsed_json") else None
        d["fields"] = json.loads(d["fields_json"]) if d.get("fields_json") else []
        out.append(d)
    return out


def score_batch(con, batch_id: str) -> dict:
    batch = con.execute("SELECT * FROM batches WHERE batch_id=?", (batch_id,)).fetchone()
    if batch is None:
        raise SystemExit("unknown batch " + batch_id)
    manifest = V.load_manifest(batch_id)
    gold_by_key = {t["task_key"]: t["gold"] for t in manifest["tasks"]}
    design = json.loads(batch["design_json"])
    results = _load_results(con, batch_id)
    cells_total = cells_correct = 0
    task_correct = 0
    by_model = defaultdict(lambda: {"tasks": 0, "correct": 0, "cells": 0, "cells_correct": 0})
    by_cond = defaultdict(lambda: {"tasks": 0, "correct": 0, "cells": 0, "cells_correct": 0})
    by_field = defaultdict(lambda: {"n": 0, "correct": 0})
    errors = []
    parse_failures = []
    failing = set()
    cell_map = {}
    for r in results:
        gold = gold_by_key.get(r["task_key"], {})
        sc = V.score_cells(gold, r["parsed"], r["fields"])
        con.execute("UPDATE results SET score_json=?, correct=? WHERE task_key=?",
                    (json.dumps(sc, ensure_ascii=False), int(sc["task_correct"]), r["task_key"]))
        cells_total += sc["total"]
        cells_correct += sc["correct"]
        task_correct += int(sc["task_correct"])
        m = by_model[r["model"]]
        m["tasks"] += 1; m["correct"] += int(sc["task_correct"]); m["cells"] += sc["total"]; m["cells_correct"] += sc["correct"]
        c = by_cond[r["cond"]]
        c["tasks"] += 1; c["correct"] += int(sc["task_correct"]); c["cells"] += sc["total"]; c["cells_correct"] += sc["correct"]
        for f, cell in sc["cells"].items():
            by_field[f]["n"] += 1
            by_field[f]["correct"] += int(cell["ok"])
            if not cell["ok"]:
                errors.append({"task_key": r["task_key"], "match": r["match"], "innings": r["innings"],
                               "model": r["model"], "cond": r["cond"], "field": f,
                               "gold": cell["gold"], "pred": cell["pred"]})
        if not sc["task_correct"]:
            failing.add((r["match"], r["innings"]))
        if not r["parse_ok"]:
            parse_failures.append({"task_key": r["task_key"], "match": r["match"], "model": r["model"],
                                   "cond": r["cond"], "reason": "json_parse_failed"})
        cell_map[(r["match"], r["innings"], r["model"], r["cond"])] = sc["cells"]
    accuracy = round(cells_correct / cells_total, 4) if cells_total else 0.0
    task_accuracy = round(task_correct / len(results), 4) if results else 0.0
    failing_positions = [{"match": m, "innings": i} for (m, i) in sorted(failing)]
    score = {
        "batch_id": batch_id, "template": batch["template"], "n_tasks": len(results),
        "task_correct": task_correct, "task_accuracy": task_accuracy,
        "cells_correct": cells_correct, "cells_total": cells_total, "accuracy": accuracy,
        "by_model": {k: dict(v, accuracy=round(v["cells_correct"] / v["cells"], 4) if v["cells"] else 0.0)
                     for k, v in by_model.items()},
        "by_condition": {k: dict(v, accuracy=round(v["cells_correct"] / v["cells"], 4) if v["cells"] else 0.0)
                         for k, v in by_cond.items()},
        "by_field": {k: dict(v, accuracy=round(v["correct"] / v["n"], 4) if v["n"] else 0.0)
                     for k, v in by_field.items()},
        "failing_positions": failing_positions,
        "errors": errors[:200],
        "parse_failures": parse_failures,
        "result_rows": len(results),
        "raw_path": str(V.RUNS / (batch_id + ".jsonl")),
        "external_api_calls": int(V.meta_get(con, "external_api_calls", "0")),
        "scored_at": V.now_iso(),
    }
    (V.REPORTS / (batch_id + "_SCORE.json")).write_text(json.dumps(score, ensure_ascii=False, indent=1), encoding="utf-8")
    paired = pair_conditions(design, cell_map)
    (V.REPORTS / (batch_id + "_PAIRED.json")).write_text(json.dumps(paired, ensure_ascii=False, indent=1), encoding="utf-8")
    (V.REPORTS / (batch_id + "_COUNTEREXAMPLES.md")).write_text(render_counterexamples(batch_id, score, paired), encoding="utf-8")
    con.execute("UPDATE batches SET status='scored', score_json=?, accuracy=?, updated_at=? WHERE batch_id=?",
                (json.dumps(score, ensure_ascii=False), accuracy, V.now_iso(), batch_id))
    con.commit()
    V.event("batch_scored", {"batch_id": batch_id, "accuracy": accuracy, "tasks": len(results),
                             "raw_path": score["raw_path"]}, con)
    write_research_memory(con)
    return {"batch_id": batch_id, "accuracy": accuracy, "task_accuracy": task_accuracy,
            "cells": str(cells_correct) + "/" + str(cells_total), "paired": paired}


def pair_conditions(design: dict, cell_map: dict) -> dict:
    conds = design.get("conditions") or []
    if len(conds) < 2:
        return {"baseline": conds[0] if conds else None, "pairs": 0, "by_condition": {},
                "note": "single-condition batch; no paired comparison"}
    base = "O" if "O" in conds else conds[0]
    by_cond = {}
    detail = []
    for cond in conds:
        if cond == base:
            continue
        agg = {"n": 0, "O_correct": 0, "V_correct": 0, "gain": 0, "loss": 0, "both": 0, "neither": 0}
        for (m, i, model, c), cells in cell_map.items():
            if c != cond:
                continue
            base_cells = cell_map.get((m, i, model, base))
            if not base_cells:
                continue
            for f, cell in cells.items():
                if f not in base_cells:
                    continue
                o = bool(base_cells[f]["ok"])
                v = bool(cell["ok"])
                agg["n"] += 1; agg["O_correct"] += int(o); agg["V_correct"] += int(v)
                agg["gain"] += int(v and not o); agg["loss"] += int(o and not v)
                agg["both"] += int(o and v); agg["neither"] += int(not o and not v)
                if o != v:
                    detail.append({"match": m, "innings": i, "model": model, "field": f,
                                   "baseline": o, "variant": v})
        agg["net"] = agg["gain"] - agg["loss"]
        by_cond[cond] = agg
    return {"baseline": base, "pairs": sum(v["n"] for v in by_cond.values()),
            "by_condition": by_cond, "changed": detail[:100]}


def render_counterexamples(batch_id: str, score: dict, paired: dict) -> str:
    lines = ["# " + batch_id + " counterexamples", "",
             "- accuracy: " + str(score["accuracy"]) + " (" + str(score["cells_correct"]) + "/" + str(score["cells_total"]) + ")",
             "- task accuracy: " + str(score["task_accuracy"]), ""]
    lines += ["## Errors", "", "| match | inn | model | cond | field | gold | pred |", "|---|---:|---|---|---|---|---|"]
    for e in score["errors"][:60]:
        lines.append("| " + str(e["match"]) + " | " + str(e["innings"]) + " | " + str(e["model"]).split(":")[0] +
                     " | " + str(e["cond"]) + " | " + str(e["field"]) + " | " + str(e["gold"]) +
                     " | " + str(e["pred"]) + " |")
    lines += ["", "## Paired", ""]
    if paired.get("by_condition"):
        for cond, agg in paired["by_condition"].items():
            lines.append("- " + cond + " vs " + str(paired["baseline"]) + ": n=" + str(agg["n"]) +
                         " gain=" + str(agg["gain"]) + " loss=" + str(agg["loss"]) + " net=" + str(agg["net"]))
    else:
        lines.append("- " + str(paired.get("note")))
    if score.get("parse_failures"):
        lines += ["", "## Parse failures", ""]
        for p in score["parse_failures"]:
            lines.append("- " + str(p["match"]) + " " + str(p["model"]).split(":")[0] + " " + str(p["cond"]))
    return "\n".join(lines) + "\n"


def write_research_memory(con) -> dict:
    batches = [dict(r) for r in con.execute("SELECT * FROM batches ORDER BY seq").fetchall()]
    decisions = [dict(r) for r in con.execute("SELECT * FROM decisions ORDER BY id").fetchall()]
    findings = []
    for b in batches:
        if b["status"] != "scored":
            continue
        sc = json.loads(b["score_json"] or "{}")
        findings.append({
            "batch_id": b["batch_id"], "template": b["template"],
            "accuracy": b["accuracy"], "task_accuracy": sc.get("task_accuracy"),
            "conditions": list((sc.get("by_condition") or {}).keys()),
            "failing_positions": sc.get("failing_positions"),
            "raw_path": sc.get("raw_path"),
            "report": str(V.REPORTS / (b["batch_id"] + "_SCORE.json")),
        })
    mem = {
        "project": V.CONFIG["project"],
        "method_version": V.CONFIG["method_version"],
        "goal": V.CONFIG["goal"],
        "data_links": V.CONFIG["data"],
        "models": V.MODELS,
        "split": V.CONFIG["split"],
        "gold_source": "scorecard.md parsed by pilot_lib.parse_scorecard_full; 43-field schema reused from attribution_update_and_full_table/full_table.py",
        "human_confirmation": {"confirmed": V.CONFIG["coverage_baseline"]["human_confirmed"],
                               "evidence_index_entries": V.CONFIG["coverage_baseline"]["evidence_entries"],
                               "status": "pending_human_review"},
        "legacy_results": {"a_dev": "209/234 target cells (89.3%), 699/2052 full-table cells",
                           "u_full": "1311 service / 1304 JSON-scorable, 598 both, 67 runs-only, 101 wickets-only, 545 neither",
                           "b_min": "110/111 paired-correct; deletion conditions did not bite on those roots",
                           "legacy_43field": V.CONFIG["coverage_baseline"]["legacy_43field_accuracy"]},
        "findings": findings,
        "decisions": [{k: d[k] for k in ("batch_id", "rule_id", "action", "next_batch_id", "rationale")}
                      for d in decisions],
        "hypotheses": [
            "H1: target cells on dev roots are near ceiling under original text.",
            "H2: hard-root failures are context-dilution failures, recoverable by a 3-sentence evidence excerpt.",
            "H3: if H2 fails, failures are field binding/localisation rather than long-context dilution.",
            "H4: deleting the same-innings mid-score hurts more than a matched unrelated deletion.",
            "H5: target-cell saturation can coexist with large 43-field collateral loss.",
        ],
        "external_api_calls": int(V.meta_get(con, "external_api_calls", "0")),
        "updated_at": V.now_iso(),
    }
    (V.REPORTS / "RESEARCH_MEMORY.json").write_text(json.dumps(mem, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# Research memory", "", "- project: " + mem["project"], "- method: " + mem["method_version"],
             "- external API calls: " + str(mem["external_api_calls"]), "", "## Findings", ""]
    for f in findings:
        lines.append("- " + f["batch_id"] + " " + f["template"] + ": accuracy " + str(f["accuracy"]) +
                     ", conditions " + ",".join(f["conditions"]) + ", raw " + str(f["raw_path"]))
    lines += ["", "## Decisions", ""]
    for d in mem["decisions"]:
        lines.append("- " + str(d["batch_id"]) + " " + str(d["rule_id"]) + " -> " + str(d["action"]) +
                     " (" + str(d["next_batch_id"]) + "): " + str(d["rationale"]))
    (V.REPORTS / "RESEARCH_MEMORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return mem
