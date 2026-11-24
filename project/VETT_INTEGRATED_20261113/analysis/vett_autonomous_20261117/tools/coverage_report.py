
import json, sqlite3, sys, collections
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
rows = con.execute("SELECT r.match,r.innings,r.model,t.cond,t.field_scope,r.score_json,t.fields_json "
                   "FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id "
                   "WHERE b.template='S_coverage_sweep'").fetchall()
out = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
       "group": "coverage_sweep", "n_results": len(rows),
       "by_cond": {}, "by_model": {}, "by_field": {}, "by_root": {}}
def add(d, k, ok, n):
    a = d.setdefault(k, {"cells": 0, "ok": 0})
    a["cells"] += n; a["ok"] += ok
for r in rows:
    sc = json.loads(r["score_json"]); cells = sc.get("cells", {})
    ok = sc.get("correct", 0); n = sc.get("total", 0)
    add(out["by_cond"], r["cond"], ok, n)
    add(out["by_model"], r["model"], ok, n)
    add(out["by_root"], r["match"], ok, n)
    for f, c in cells.items():
        add(out["by_field"], f, int(c["ok"]), 1)
for section in ("by_cond", "by_model", "by_root"):
    for k, v in out[section].items():
        v["accuracy"] = round(v["ok"] / v["cells"], 4) if v["cells"] else 0.0
for k, v in out["by_field"].items():
    v["accuracy"] = round(v["ok"] / v["cells"], 4) if v["cells"] else 0.0

# diagnostic group (non-sweep) for contrast
diag = con.execute("SELECT r.score_json FROM results r JOIN batches b ON b.batch_id=r.batch_id "
                   "WHERE b.template!='S_coverage_sweep'").fetchall()
d_ok = d_n = 0
for r in diag:
    sc = json.loads(r["score_json"]); d_ok += sc.get("correct", 0); d_n += sc.get("total", 0)
out["diagnostic_group"] = {"cells": d_n, "ok": d_ok, "accuracy": round(d_ok / d_n, 4) if d_n else 0.0}

Path("reports/COVERAGE_GROUP.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
lines = ["# Coverage group report (separate from diagnostic group)", "",
         "- generated: " + out["generated_at"],
         "- sweep results: " + str(out["n_results"]),
         "- sweep cells: " + str(sum(v["cells"] for v in out["by_cond"].values())),
         "- sweep accuracy: " + str(round(sum(v["ok"] for v in out["by_cond"].values()) / max(1, sum(v["cells"] for v in out["by_cond"].values())), 4)),
         "- diagnostic cells: " + str(d_n) + "; accuracy: " + str(out["diagnostic_group"]["accuracy"]), "",
         "## By condition", ""]
for k, v in sorted(out["by_cond"].items()):
    lines.append("- " + k + ": " + str(v["ok"]) + "/" + str(v["cells"]) + " = " + str(v["accuracy"]))
lines += ["", "## By model", ""]
for k, v in sorted(out["by_model"].items()):
    lines.append("- " + k + ": " + str(v["ok"]) + "/" + str(v["cells"]) + " = " + str(v["accuracy"]))
lines += ["", "## Worst roots (>=6 cells)", ""]
for k, v in sorted(out["by_root"].items(), key=lambda kv: kv[1]["accuracy"])[:12]:
    if v["cells"] >= 6:
        lines.append("- " + k + ": " + str(v["ok"]) + "/" + str(v["cells"]) + " = " + str(v["accuracy"]))
lines += ["", "## Note", "",
          "- This is a coverage group, not a hard-case group; do not merge its rate with B002–B022.",
          "- E/O/OI/WI availability differs by root, so condition rates are not balanced samples."]
Path("reports/COVERAGE_GROUP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"n": out["n_results"], "by_cond": {k: v["accuracy"] for k, v in out["by_cond"].items()},
                  "diag": out["diagnostic_group"]}, ensure_ascii=False))
