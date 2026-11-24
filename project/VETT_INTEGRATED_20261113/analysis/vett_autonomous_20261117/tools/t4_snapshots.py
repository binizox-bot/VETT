
import json, sqlite3, time, sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V, reporting
c=sqlite3.connect("state/workflow.db"); c.row_factory=sqlite3.Row
now=lambda: datetime.now().astimezone().isoformat(timespec="seconds")
def snap(tag):
    s=reporting.status_dict(c); n=c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
    q={r["status"]:r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
    txt="# T4 SNAPSHOT "+tag+"\n\n- time: "+now()+"\n- state: "+s["workflow_state"]+"\n- supervisor: "+str(s["supervisor"]["pid"])+" alive="+str(s["supervisor"]["alive"])+"\n- worker: "+str(s["worker"]["pid"])+" alive="+str(s["worker"]["alive"])+" heartbeat="+str(s["worker"]["heartbeat_age_seconds"])+"s\n- results: "+str(n)+"\n- queue: "+json.dumps(q)+"\n"
    Path("reports/T4_SNAPSHOT_"+tag+".md").write_text(txt,encoding="utf-8")
    return s,n,q
s1,n1,q1=snap("1")
time.sleep(60)
s2,n2,q2=snap("2")
doc="# 新分支：T4 full-table scale（2026-11-20）\n\n"
doc+="- 授权：用户授权新分支/扩大合法任务位。\n"
doc+="- 假设：43 字段整表的附带字段损失与 JSON 失败不只在 match_0002；在覆盖组上可复现。\n"
doc+="- 设计：同一 O 全文、full43、num_predict=900；60+60 个 coverage unit ×3 模型 = 360 任务。\n"
doc+="- 批次：B198（60 unit，180 任务）、B199（60 unit，180 任务）；started 09:14-09:16。\n"
doc+="- 根：SWEEP_ROOTS，排除 held-out 0121-0160；不改源数据。\n"
doc+="- 评分：逐字段精确匹配；同时记录 parse、done_reason、43 字段准确率与 target 子集。\n"
doc+="- 外部 API：0；本机三模型。\n"
doc+="- C 扩展尝试：all 8 samples 的 72 个任务全部 duplicate_existing_task；说明 C 已覆盖全部样本，无新增。\n"
doc+="- 预计：360 请求，约 20-30 秒/条，约 2-3 小时；实际以运行数据为准。\n"
doc+="- 快照："+str(n1)+" → "+str(n2)+"（+"+str(n2-n1)+"）。\n"
Path("reports/NEW_BRANCH_T4_20261120.md").write_text(doc,encoding="utf-8")
print(json.dumps({"n1":n1,"n2":n2,"delta":n2-n1,"queue":q2,"pids":[s2["supervisor"]["pid"],s2["worker"]["pid"]]},ensure_ascii=False))
