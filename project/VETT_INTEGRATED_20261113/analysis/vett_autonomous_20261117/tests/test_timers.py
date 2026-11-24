
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V
tmp = Path(tempfile.mkdtemp(prefix="vett_timer_"))
V.DB_PATH = tmp / "timer.db"
V.STATE = tmp
V.REPORTS = tmp
con = V.init_db()
import supervisor, reporting
V.meta_set(con, "last_status_at", V.now_iso(-901))
V.meta_set(con, "last_snapshot_at", V.now_iso(-3601))
con.commit()
checks = {}
checks["status_due_at_901s"] = supervisor._due(con, "last_status_at", 900) is True
checks["snapshot_due_at_3601s"] = supervisor._due(con, "last_snapshot_at", 3600) is True
reporting.write_status(con)
checks["status_file"] = (tmp / "STATUS.json").exists()
checks["status_not_due_after_write"] = supervisor._due(con, "last_status_at", 900) is False
reporting.write_snapshot(con)
checks["snapshot_file"] = (tmp / "SNAPSHOT_LATEST.md").exists()
checks["snapshot_not_due_after_write"] = supervisor._due(con, "last_snapshot_at", 3600) is False
V.meta_set(con, "last_status_at", V.now_iso(-10))
con.commit()
checks["status_not_due_at_10s"] = supervisor._due(con, "last_status_at", 900) is False
print(json.dumps({"ok": all(checks.values()), "checks": checks, "tmp": str(tmp)}, ensure_ascii=False, indent=1))
