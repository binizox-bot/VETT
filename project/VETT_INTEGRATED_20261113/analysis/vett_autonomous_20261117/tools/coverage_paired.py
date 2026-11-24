
import json, sqlite3, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
rows = con.execute("SELECT r.match,r.innings,r.model,t.cond,r.score_json FROM results r "
                   "JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id "
                   "WHERE b.template='S_coverage_sweep'").fetchall()
cellmap = defaultdict(dict)
for r in rows:
    sc = json.loads(r["score_json"])
    for f, c in sc.get("cells", {}).items():
        cellmap[(r["match"], r["innings"], r["model"], f)][r["cond"]] = bool(c["ok"])
out = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
       "pairs": {}, "by_model": {}, "note": "within-root/model/field paired against O"}
for cond in ("E", "WI", "OI"):
    agg = {"n": 0, "O": 0, "V": 0, "gain": 0, "loss": 0, "both": 0, "neither": 0}
    by_model = defaultdict(lambda: {"n": 0, "gain": 0, "loss": 0})
    for (m, i, model, f), d in cellmap.items():
        if "O" not in d or cond not in d:
            continue
        o, v = d["O"], d[cond]
        agg["n"] += 1; agg["O"] += int(o); agg["V"] += int(v)
        agg["gain"] += int(v and not o); agg["loss"] += int(o and not v)
        agg["both"] += int(o and v); agg["neither"] += int(not o and not v)
        bm = by_model[model]; bm["n"] += 1; bm["gain"] += int(v and not o); bm["loss"] += int(o and not v)
    agg["net"] = agg["gain"] - agg["loss"]
    out["pairs"][cond] = agg
    out["by_model"][cond] = {k: dict(v, net=v["gain"] - v["loss"]) for k, v in by_model.items()}
Path("reports/COVERAGE_PAIRED.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
lines = ["# Coverage paired effects (within root/model/field, vs O)", "",
         "- generated: " + out["generated_at"], ""]
for cond in ("E", "WI", "OI"):
    a = out["pairs"][cond]
    lines.append("- " + cond + " vs O: n=" + str(a["n"]) + " O=" + str(a["O"]) + " V=" + str(a["V"]) +
                 " gain=" + str(a["gain"]) + " loss=" + str(a["loss"]) + " net=" + str(a["net"]) +
                 " both=" + str(a["both"]) + " neither=" + str(a["neither"]))
lines += ["", "Note: E is only available on roots with an explicit total sentence; paired n differs by condition."]
Path("reports/COVERAGE_PAIRED.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(out["pairs"], ensure_ascii=False))
print(json.dumps(out["by_model"], ensure_ascii=False)[:1200])
