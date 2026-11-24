import sys,json,shutil,os
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
q=ROOT/"quarantine"; q.mkdir(exist_ok=True)
con=V.connect()
bad=["B214","B215","B216","B217","B218","B219","B220"]
for bid in bad:
    nres=con.execute("SELECT COUNT(*) FROM results WHERE batch_id=?",(bid,)).fetchone()[0]
    nt=con.execute("SELECT COUNT(*) FROM tasks WHERE batch_id=?",(bid,)).fetchone()[0]
    con.execute("DELETE FROM results WHERE batch_id=?",(bid,))
    con.execute("DELETE FROM tasks WHERE batch_id=?",(bid,))
    con.execute("DELETE FROM task_key_map WHERE batch_id=?",(bid,))
    con.execute("DELETE FROM batches WHERE batch_id=?",(bid,))
    for p in (WF/"runs"/(bid+".jsonl"), WF/"batches"/(bid+".json")):
        if p.exists(): shutil.move(str(p),str(q/p.name))
    print("REMOVED",bid,"tasks",nt,"results",nres)
V.meta_set(con,"state","paused"); V.meta_set(con,"exhausted","0")
V.event("batch_quarantined",{"batches":bad,"reason":"innings field parsed as 1 for inn2 events; prompts said Innings: 1"},con)
con.commit(); con.close()
(ROOT/"INCIDENT_WRONG_INNINGS.md").write_text("# 故障与隔离：核心批次 innings 解析错误\n\n- 时间：2026-11-21 21:58。\n- 现象：attribution_followup/samples.json 的 innings 字段是字符串 inn1/inn2；night_build 第一版用 1 覆盖，导致 B214–B220 的提示写成 Innings: 1。\n- 影响：B213（match_0003，本为 inn1）不受影响；B214–B220 已删除并入隔离目录 quarantine/（B214 已完成 5 条结果，一并作废）。\n- 处理：暂停派发、删除受影响任务/结果/批次、修复解析后用新批次号重建。\n- 保留：B213 的 18 条结果。\n",encoding="utf-8")
print("DONE")
