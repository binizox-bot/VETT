import json,hashlib
from pathlib import Path
ROOT=Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_dataset_independent_scoring_20261121")
ex=ROOT/"export_to_codex_v1"; s=json.loads((ex/"RUN_MANIFEST.json").read_text(encoding="utf-8"))
lines=["# Codex v1_frozen 首批运行报告（B212）","", "- 运行目录："+str(ROOT/"run_dsh_v1"),"- 批次：B212（独立运行目录 run_dsh_v1；工作流队列 0，批次边界接入）","- 冻结版本：v1_frozen_20261121；FROZEN_MANIFEST sha256："+s["frozen_manifest_sha256"],"","## 5 个输入","","| sample_id | 比赛 | 局 | 任务 | 文本版本 | 配对 |","|---|---|---:|---|---|---|"]
for sid,g in [("vett-dev-v1-0001-c00","match_0047"),("vett-dev-v1-0001-c01","match_0047"),("vett-dev-v1-0002-c10","match_0003"),("vett-dev-v1-0002-c11","match_0003"),("vett-dev-v1-0002-c12","match_0003")]:
    pass
rows=[json.loads(l) for l in (ROOT/"run_dsh_v1"/"positions.jsonl").read_text(encoding="utf-8").splitlines()]
pairmap={"c00":"长文-窗口配对（全文）","c01":"长文-窗口配对（同源窗口）","c10":"三臂（正式改判）","c11":"三臂（维持）","c12":"三臂（无通知）"}
for p in rows:
    lines.append("| "+p["sample_id"]+" | "+p["match"]+" | "+str(p["innings"])+" | "+p["condition"]+" | 发布版/scorecard 冻结输入 | "+pairmap.get(p["sample_id"][-3:],"-")+" |")
lines+=["","## 计数","","| 计划 | 复用 | 新增 | 收到响应 | 可评分 | 缺失 | 完整配对 |","|---:|---:|---:|---:|---:|---:|---|","| 15 | 0 | 15 | "+str(s["responses"])+" | "+str(s["scorable"])+" | "+str(s["missing"])+" | 3 长文配对 + 3 三臂组 |","","- 任务全对："+str(round(s["task_accuracy"]*15))+"/15；字段正确："+str(s["field_accuracy"][0])+"/"+str(s["field_accuracy"][1])+"。","- 截断："+str(s["checks"]["truncated"])+"；done_reason=stop："+str(s["checks"]["done_stop"])+"/15。","- prompt_sha 不符："+str(s["checks"]["prompt_sha_bad"])+"；模型名不符："+str(s["checks"]["model_bad"])+"；digest 不符："+str(s["checks"]["digest_bad"])+"；decode 不符："+str(s["checks"]["decode_bad"])+"。","","## 导出","", "- "+str(ex/"frozen_v1_B212_export.zip"),"- raw.jsonl / scores.jsonl / RUN_MANIFEST.json / SHA256SUMS.txt",""]
out=ROOT.parent/"vett_autonomous_20261117"/"reports"/"FROZEN_V1_RUN_20261121.md"
out.write_text("\n".join(lines),encoding="utf-8")
print(json.dumps({"report":str(out),"zip":str(ex/"frozen_v1_B212_export.zip")}))
