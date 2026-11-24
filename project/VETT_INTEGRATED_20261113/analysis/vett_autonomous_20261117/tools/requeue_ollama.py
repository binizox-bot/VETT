
import sys, json
sys.path.insert(0,".")
import vettlib as V
c=V.init_db()
n=c.execute("UPDATE tasks SET status='queued' WHERE status='failed' AND task_key NOT IN (SELECT task_key FROM results)").rowcount
c.commit()
V.event("requeued_after_ollama_outage", {"count": n, "reason": "Ollama connection refused 17:35; no result persisted"}, c)
print(json.dumps({"requeued": n, "queue": {r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}}, ensure_ascii=False))
