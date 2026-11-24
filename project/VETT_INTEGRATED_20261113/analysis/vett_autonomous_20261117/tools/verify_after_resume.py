
import json, sqlite3, time
from collections import defaultdict
from pathlib import Path
c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row
time.sleep(6)
print("BATCHES", [dict(r) for r in c.execute("SELECT batch_id,template,status,accuracy FROM batches ORDER BY seq DESC LIMIT 3")])
print("QUEUE", {r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})

# P triple completeness
rows = c.execute("SELECT r.match,r.innings,r.model,t.field_scope,r.parse_ok FROM results r JOIN tasks t USING(task_key) "
                 "JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep'").fetchall()
key = defaultdict(set)
for r in rows:
    key[(r["match"], r["innings"], r["model"])].add(r["field_scope"])
complete = sum(1 for v in key.values() if {"probe_runs", "probe_wickets", "probe_both"} <= v)
missing = [(k, sorted({"probe_runs", "probe_wickets", "probe_both"} - v)) for k, v in key.items() if not {"probe_runs", "probe_wickets", "probe_both"} <= v]
print("P_TRIPLES", {"keys": len(key), "complete": complete, "missing": len(missing), "examples": missing[:5]})

# load comparison: old vs new segment
new = c.execute("SELECT model,COUNT(*) n,AVG(load_ms) load,AVG(inference_ms) inf,AVG(duration_ms) dur FROM results WHERE created_at>='2026-11-19T15:42:34' GROUP BY model").fetchall()
old = c.execute("SELECT COUNT(*) n,AVG(load_ms) load,AVG(inference_ms) inf,AVG(duration_ms) dur FROM results WHERE created_at<'2026-11-19T15:42:34'").fetchone()
print("NEW_SEG", [dict(r) for r in new])
print("OLD_ALL", dict(old))

# B004 43-field check
for r in c.execute("SELECT r.model,r.parse_ok,r.correct,r.response_meta_json,t.num_predict FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B004'"):
    m = json.loads(r["response_meta_json"] or "{}")
    print("B004", r["model"], "parse", r["parse_ok"], "correct", r["correct"],
          "done", m.get("done_reason"), "eval", m.get("eval_count"), "np", r["num_predict"],
          "prompt_eval", m.get("prompt_eval_count"))

# classify length / parse failures
bad = c.execute("SELECT r.match,r.model,t.cond,t.field_scope,r.parse_ok,r.response_meta_json,t.num_predict "
                "FROM results r JOIN tasks t USING(task_key) WHERE r.parse_ok=0").fetchall()
print("PARSE_FAIL", [dict(x) for x in bad[:15]])
