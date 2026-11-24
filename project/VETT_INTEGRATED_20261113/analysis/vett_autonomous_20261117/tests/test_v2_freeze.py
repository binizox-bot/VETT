
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
tmp = Path(tempfile.mkdtemp(prefix="vett_v2_"))
os.environ["VETT_DB_PATH"] = str(tmp / "workflow.db")
import vettlib as V
import planner
con = V.init_db()
design, tasks, rejects = planner.build_a(con, {"rationale": "smoke test branch A"})
print("built", len(tasks), "rejects", len(rejects))
if tasks:
    bid = planner.freeze_batch(con, design, tasks, rejects, plan_ms=12.3)
    print("batch", bid)
    print("tasks", con.execute("SELECT COUNT(*) n FROM tasks").fetchone()["n"])
    row = con.execute("SELECT task_key,model_digest,decode_json,replicate_id,legacy_task_key,identity_status,field_scope FROM tasks LIMIT 1").fetchone()
    print("task", dict(row))
    print("map", con.execute("SELECT COUNT(*) n FROM task_key_map").fetchone()["n"])
    print("batchrow", dict(con.execute("SELECT batch_id,scoring_version,manifest_version,plan_ms FROM batches").fetchone()))
    print("scopes", [r["field_scope"] for r in con.execute("SELECT DISTINCT field_scope FROM tasks")])
print("OK")
