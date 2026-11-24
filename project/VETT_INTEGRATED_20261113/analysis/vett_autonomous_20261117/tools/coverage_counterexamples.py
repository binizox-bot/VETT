
import json, sqlite3, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
rows = con.execute("SELECT r.match,r.innings,r.model,t.cond,r.score_json,r.parsed_json,t.prompt "
                   "FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id "
                   "WHERE b.template='S_coverage_sweep'").fetchall()
cellmap = defaultdict(dict)
resmap = {}
for r in rows:
    sc = json.loads(r["score_json"])
    for f, c in sc.get("cells", {}).items():
        cellmap[(r["match"], r["innings"], r["model"], f)][r["cond"]] = bool(c["ok"])
    resmap[(r["match"], r["innings"], r["model"], r["cond"])] = r

losses = []
for (m, i, model, f), d in cellmap.items():
    if d.get("O") is True and d.get("E") is False:
        e = resmap.get((m, i, model, "E"))
        excerpt = ""
        if e and "Commentary:\n" in e["prompt"]:
            excerpt = e["prompt"].split("Commentary:\n", 1)[1].rsplit("\n\nJSON:", 1)[0]
        pred = json.loads(e["parsed_json"]) if e and e["parsed_json"] else {}
        losses.append({"match": m, "innings": i, "model": model, "field": f,
                       "E_pred": pred.get(f), "excerpt_chars": len(excerpt), "excerpt": excerpt[:600]})
oi_by_root = defaultdict(lambda: {"n": 0, "gain": 0, "loss": 0, "O": 0, "V": 0})
for (m, i, model, f), d in cellmap.items():
    if "O" in d and "OI" in d:
        a = oi_by_root[m]
        a["n"] += 1; a["O"] += int(d["O"]); a["V"] += int(d["OI"])
        a["gain"] += int(d["OI"] and not d["O"]); a["loss"] += int(d["O"] and not d["OI"])
for a in oi_by_root.values():
    a["net"] = a["gain"] - a["loss"]
out = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
       "E_losses": losses, "OI_by_root": dict(oi_by_root)}
Path("reports/COVERAGE_COUNTEREXAMPLES.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
lines = ["# Coverage counterexamples", "", "- generated: " + out["generated_at"],
         "- E losses vs O: " + str(len(losses)), ""]
for x in losses[:12]:
    lines.append("- " + x["match"] + " inn" + str(x["innings"]) + " " + x["model"].split(":")[0] +
                 " " + x["field"] + " E_pred=" + str(x["E_pred"]))
lines += ["", "## OI by root (top net)", ""]
for m, a in sorted(oi_by_root.items(), key=lambda kv: kv[1]["net"], reverse=True)[:8]:
    lines.append("- " + m + ": n=" + str(a["n"]) + " net=" + str(a["net"]) + " O=" + str(a["O"]) + " OI=" + str(a["V"]))
lines += ["", "## OI by root (bottom net)", ""]
for m, a in sorted(oi_by_root.items(), key=lambda kv: kv[1]["net"])[:8]:
    lines.append("- " + m + ": n=" + str(a["n"]) + " net=" + str(a["net"]) + " O=" + str(a["O"]) + " OI=" + str(a["V"]))
Path("reports/COVERAGE_COUNTEREXAMPLES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"E_losses": len(losses), "examples": losses[:3],
                  "OI_top": sorted(oi_by_root.items(), key=lambda kv: kv[1]["net"], reverse=True)[:3],
                  "OI_bottom": sorted(oi_by_root.items(), key=lambda kv: kv[1]["net"])[:3]}, ensure_ascii=False)[:3000])
