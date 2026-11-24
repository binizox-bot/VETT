
import sqlite3, json
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
print("B198",{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks WHERE batch_id='B198' GROUP BY status")})
print("RESULTS",c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"])
for r in c.execute("SELECT r.match,r.model,r.parse_ok,r.correct,r.response_meta_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B198' ORDER BY r.created_at DESC LIMIT 3"):
    m=json.loads(r["response_meta_json"] or "{}")
    print("SAMPLE",r["match"],r["model"],"parse",r["parse_ok"],"correct",r["correct"],"done",m.get("done_reason"),"eval",m.get("eval_count"),"prompt",m.get("prompt_eval_count"))
print("QUEUE",{r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")})
