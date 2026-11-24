import sys,json,hashlib
from pathlib import Path
WF=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0,str(WF))
import vettlib as V, v2, scorer
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_night_20261121")
con=V.connect(); fixed=0; batches=0
for bid in ["B228","B229","B230","B231","B232","B233","B234","B235"]:
    mp=V.BATCHES/(bid+".json")
    if not mp.exists(): continue
    man=json.loads(mp.read_text(encoding="utf-8"))
    changed=False
    for t in man["tasks"]:
        if not t["cond"].startswith("N1"): continue
        b=V.load_bundle(t["match"]); g=V.gold43(b["md"])
        t["gold"]=g; changed=True
        con.execute("UPDATE tasks SET gold_json=? WHERE task_key=?",(json.dumps(g,ensure_ascii=False),t["task_key"]))
        fixed+=1
    if changed:
        mp.write_text(json.dumps(man,ensure_ascii=False,indent=1),encoding="utf-8")
        msha=V.sha256_text(mp.read_text(encoding="utf-8"))
        con.execute("UPDATE batches SET manifest_sha=?, updated_at=? WHERE batch_id=?",(msha,V.now_iso(),bid))
        con.commit()
        scorer.score_batch(con,bid); batches+=1
V.event("ft_gold_repaired",{"tasks":fixed,"batches":batches,"reason":"N1 fulltable gold was adjusted to new values by mistake; offline rescore only"},con)
con.commit(); con.close()
(ROOT/"INCIDENT_FT_GOLD.md").write_text("# 整表 N1 金标错误与离线修复\n\n- 时间：2026-11-21 23:35。\n- 现象：full-table 的 N1（维持）与 N2（改判）共用同一份“新值”金标，导致维持条件被按改判评分。\n- 影响：B228–B235 的 N1_F_fulltable 任务。模型输入正确，仅金标/评分错误。\n- 处理：把 N1 金标恢复为原始 score_v1 gold43，更新 tasks.gold_json 与批次 manifest，调用 scorer.score_batch 离线重算；未重跑模型。\n",encoding="utf-8")
print(json.dumps({"fixed":fixed,"rescored_batches":batches}))
