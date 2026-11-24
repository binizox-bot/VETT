
import sqlite3, json
from pathlib import Path
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
unc=c.execute("SELECT COUNT(*) n FROM attempts WHERE uncertain=1").fetchone()["n"]
batch=c.execute("SELECT batch_id,template,status FROM batches WHERE status='running' ORDER BY seq LIMIT 1").fetchone()
b = (batch["batch_id"] + " " + batch["template"]) if batch else "none"
p=Path("reports/EVENING_BRIEF_20261119.md")
t=p.read_text(encoding="utf-8")
t=t.replace("- uncertain 计数：见 attempts", "- uncertain attempts：" + str(unc) + "；主机重启与受控 stop 的未确认请求已保留")
t=t.replace("- B152 正在运行，后续任务可继续领取。", "- 当前运行批次：" + b + "；后续任务可继续领取。")
p.write_text(t, encoding="utf-8")
print(json.dumps({"uncertain": unc, "running": b}, ensure_ascii=False))
