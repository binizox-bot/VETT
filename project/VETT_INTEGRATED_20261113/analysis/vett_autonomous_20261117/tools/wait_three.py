
import json, sqlite3, time
DB = "state/workflow.db"
def con():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
for i in range(120):
    c = con()
    rows = c.execute("SELECT batch_id,seq,template,status,accuracy FROM batches ORDER BY seq").fetchall()
    done3 = any(r["seq"] >= 3 and r["status"] == "scored" for r in rows)
    c.close()
    if done3:
        break
    time.sleep(3)
c = con()
print("BATCHES", json.dumps([dict(r) for r in c.execute("SELECT batch_id,seq,template,status,accuracy,cost_json FROM batches ORDER BY seq")], ensure_ascii=False))
print("DECISIONS", json.dumps([dict(r) for r in c.execute("SELECT batch_id,rule_id,action,next_batch_id,rationale FROM decisions ORDER BY id")], ensure_ascii=False, indent=1)[:2500])
print("QUEUE", json.dumps({r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}))
for b in c.execute("SELECT batch_id FROM batches WHERE status='scored' ORDER BY seq"):
    bid = b["batch_id"]
    try:
        sc = json.load(open("reports/" + bid + "_SCORE.json", encoding="utf-8"))
        pa = json.load(open("reports/" + bid + "_PAIRED.json", encoding="utf-8"))
        print("SCORE", bid, "accuracy", sc["accuracy"], "tasks", sc["task_correct"], "/", sc["n_tasks"],
              "by_cond", {k: v["accuracy"] for k, v in sc["by_condition"].items()},
              "failing", sc["failing_positions"][:4])
        print("PAIRED", bid, json.dumps({k: {kk: vv[kk] for kk in ("n","gain","loss","net")} for k, vv in (pa.get("by_condition") or {}).items()}))
    except Exception as e:
        print("SCORE_ERR", bid, type(e).__name__, e)
print("NEXT", json.dumps([dict(r) for r in c.execute("SELECT batch_id,match,innings,model,cond,field_scope FROM tasks WHERE status='queued' ORDER BY batch_id,rowid LIMIT 12")], ensure_ascii=False))
