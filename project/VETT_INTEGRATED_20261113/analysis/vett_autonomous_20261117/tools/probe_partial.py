
import json, sqlite3, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
rows = con.execute("SELECT r.model,t.field_scope,r.score_json FROM results r JOIN tasks t USING(task_key) "
                   "JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep'").fetchall()
agg = defaultdict(lambda: {"tasks": 0, "task_ok": 0, "cells": 0, "cell_ok": 0})
by_model = defaultdict(lambda: {"tasks": 0, "task_ok": 0, "cells": 0, "cell_ok": 0})
for r in rows:
    sc = json.loads(r["score_json"])
    for d, key in ((agg, r["field_scope"]), (by_model, r["model"])):
        a = d[key]
        a["tasks"] += 1; a["task_ok"] += int(sc["task_correct"])
        a["cells"] += sc["total"]; a["cell_ok"] += sc["correct"]
for d in (agg, by_model):
    for a in d.values():
        a["task_accuracy"] = round(a["task_ok"] / a["tasks"], 4) if a["tasks"] else 0
        a["cell_accuracy"] = round(a["cell_ok"] / a["cells"], 4) if a["cells"] else 0
out = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
       "n_results": len(rows), "by_scope": dict(agg), "by_model": dict(by_model)}
Path("reports/PROBE_SWEEP_PARTIAL.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
lines = ["# P field-probe partial", "", "- results: " + str(len(rows)), "- generated: " + out["generated_at"], "",
         "## By scope", "", "| scope | tasks | task acc | cells | cell acc |", "|---|---:|---:|---:|---:|"]
for k, a in sorted(agg.items()):
    lines.append("| " + k + " | " + str(a["tasks"]) + " | " + str(a["task_accuracy"]) + " | " +
                 str(a["cells"]) + " | " + str(a["cell_accuracy"]) + " |")
lines += ["", "## By model", "", "| model | tasks | task acc | cell acc |", "|---|---:|---:|---:|"]
for k, a in sorted(by_model.items()):
    lines.append("| " + k + " | " + str(a["tasks"]) + " | " + str(a["task_accuracy"]) + " | " + str(a["cell_accuracy"]) + " |")
lines += ["", "Note: partial data; probe_both vs single-field is the main comparison."]
Path("reports/PROBE_SWEEP_PARTIAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(out, ensure_ascii=False)[:2500])
