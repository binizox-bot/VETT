
import json, sqlite3, sys
sys.path.insert(0, ".")
import vettlib as V, planner
con = V.init_db()
models = V.MODELS
gemma = "gemma2:9b"
llama = "llama3.1:8b"

# 1) missing P probe_both for match_0089 inn1 gemma
tasks, rejects = [], []
tasks += planner.make_probe_tasks(con, "match_0089", 1, "O", [gemma],
                                  [("probe_both", ["inn1.total_runs", "inn1.total_wickets"])],
                                  rejects, num_predict=200)
if tasks:
    design = planner._design("P_field_fill",
        "Fill the single missing P triple (probe_both) for match_0089 inn1 gemma.",
        "P triple audit found 1 missing cell among 518 keys.",
        con, tasks, ["probe_both"], [gemma], ["commentary.txt", "scorecard.md"],
        "exact integer match per field")
    bid = planner.freeze_batch(con, design, tasks, rejects, plan_ms=2.0)
    print("fill frozen", bid, "tasks", len(tasks))
else:
    print("fill none", rejects)

# 2) isolated llama P320 trial on 3 reproducible length failures
fails = con.execute("SELECT DISTINCT r.match,t.innings FROM results r JOIN tasks t USING(task_key) "
                    "WHERE r.model=? AND r.parse_ok=0 AND t.field_scope='probe_wickets' LIMIT 3", (llama,)).fetchall()
print("trial positions", [dict(x) for x in fails])
trial, trej = [], []
for x in fails:
    trial += planner.make_probe_tasks(con, x["match"], int(x["innings"]), "O", [llama],
                                      [("probe_wickets_p320", ["inn" + str(x["innings"]) + ".total_wickets"])],
                                      trej, num_predict=320)
if trial:
    design = planner._design("ACC_llama_p320",
        "Isolated config trial: llama probe_wickets with num_predict=320 instead of 200 to test the reproducible length cap.",
        "10 llama probe_wickets results hit done_reason=length at eval_count=200.",
        con, trial, ["probe_wickets_p320"], [llama], ["commentary.txt", "scorecard.md"],
        "exact integer match; compare parse/length against the frozen 200-budget results")
    bid = planner.freeze_batch(con, design, trial, trej, plan_ms=2.0)
    print("trial frozen", bid, "tasks", len(trial))
else:
    print("trial none", trej)
