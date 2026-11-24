
import json, sqlite3, glob, os
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, ".")
import vettlib as V
import v2

con = V.init_db()
s = v2.run_stats(con)
q = {r["status"]: r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
scored = con.execute("SELECT COUNT(*) n FROM batches WHERE status='scored'").fetchone()["n"]
running = con.execute("SELECT batch_id,template FROM batches WHERE status='running' ORDER BY seq LIMIT 1").fetchone()
hourly = sorted(glob.glob("reports/HOURLY_*.md"))
now = datetime.now().astimezone().isoformat(timespec="seconds")
lines = ["# VETT long-run report", "", "- generated: " + now,
         "- run started: " + V.meta_get(con, "run_started_at", ""),
         "- workflow state: " + V.meta_get(con, "state", ""),
         "- external API calls: " + V.meta_get(con, "external_api_calls", "0"),
         "- supervisor: " + V.meta_get(con, "supervisor_pid", ""),
         "- worker: " + V.meta_get(con, "worker_pid", ""), "",
         "## Run stats", "",
         "- elapsed: " + str(s["elapsed_hours"]) + " h",
         "- results: " + str(s["results"]) + "; attempts: " + str(s["attempts"]) +
         "; uncertain: " + str(s["uncertain_attempts"]),
         "- load/inference/scoring ms: " + str(s["load_ms"]) + " / " + str(s["inference_ms"]) +
         " / " + str(s["scoring_ms"]),
         "- planning/waiting ms: " + str(s["plan_ms"]) + " / " + str(s["waiting_ms_est"]),
         "- exceptions: " + str(s["exceptions"]),
         "- queue: " + json.dumps(q), "",
         "## Batches", "",
         "- scored: " + str(scored),
         "- running: " + (running["batch_id"] + " " + running["template"] if running else "none"),
         "- sweep cursor: " + V.meta_get(con, "sweep_cursor", "0") + "/360",
         "- probe cursor: " + V.meta_get(con, "probe_cursor", "0") + "/360", "",
         "## Hourly reports", ""]
for f in hourly:
    lines.append("- " + os.path.basename(f) + " (" + str(os.path.getsize(f)) + " bytes)")
lines += ["", "## Research artifacts", "",
          "- SCIENCE_CORRECTIONS.md (B002–B015, coverage paired, E counterexamples)",
          "- COVERAGE_GROUP.md / COVERAGE_PAIRED.md / COVERAGE_COUNTEREXAMPLES.md",
          "- BRANCH_C.md (B019+B022, 8 events)",
          "- records/INDEX.json (" + str(len(glob.glob('records/CASE_*.json'))) + " records)",
          "- data_patches/ (" + str(len(glob.glob('data_patches/*.json'))) + " patches)", "",
          "## Pending", "",
          "- 8h milestone at 22:50; 08:00 stage report next day.",
          "- 48h queue target not met; S + P estimated ~10–18h at observed throughput.",
          "- Human review remains pending for all records.",
          "- Planning is rule_template, not model-driven hypothesis generation."]
Path("LONG_RUN_REPORT_20261118.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"elapsed_h": s["elapsed_hours"], "results": s["results"], "attempts": s["attempts"],
                  "scored": scored, "running": dict(running) if running else None, "hourly": len(hourly),
                  "queue": q}, ensure_ascii=False))
