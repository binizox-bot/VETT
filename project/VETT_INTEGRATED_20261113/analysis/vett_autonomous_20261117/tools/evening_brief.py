
import json, sqlite3, time, sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V, reporting, v2
c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row
now = lambda: datetime.now().astimezone().isoformat(timespec="seconds")

def snap(tag):
    s = reporting.status_dict(c)
    p = reporting.write_snapshot(c)
    rows = c.execute("SELECT COUNT(*) n FROM results").fetchone()["n"]
    q = {r["status"]: r["n"] for r in c.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
    txt = "# EVENING SNAPSHOT " + tag + "\n\n"
    txt += "- time: " + now() + "\n"
    txt += "- workflow: " + s["workflow_state"] + "; batch: " + s["batch_state"] + "\n"
    txt += "- supervisor: " + str(s["supervisor"]["pid"]) + " alive=" + str(s["supervisor"]["alive"]) + "\n"
    txt += "- worker: " + str(s["worker"]["pid"]) + " alive=" + str(s["worker"]["alive"]) + " heartbeat=" + str(s["worker"]["heartbeat_age_seconds"]) + "s\n"
    txt += "- results: " + str(rows) + "\n"
    txt += "- queue: " + json.dumps(q) + "\n"
    txt += "- probe_cursor: " + V.meta_get(c, "probe_cursor", "") + "; sweep_cursor: " + V.meta_get(c, "sweep_cursor", "") + "\n"
    txt += "- snapshot: " + str(p) + "\n"
    Path("reports/EVENING_SNAPSHOT_" + tag + ".md").write_text(txt, encoding="utf-8")
    return s, rows, q, p

s1, n1, q1, p1 = snap("1")
time.sleep(75)
s2, n2, q2, p2 = snap("2")

# new results detail
new = c.execute("SELECT model,load_ms,inference_ms,duration_ms FROM results WHERE created_at>='2026-11-19T15:42:34'").fetchall()
agg = defaultdict(lambda: {"n": 0, "load": 0, "inf": 0, "big": 0, "small": 0})
for r in new:
    a = agg[r["model"]]; a["n"] += 1; a["load"] += r["load_ms"]; a["inf"] += r["inference_ms"]
    a["big"] += int(r["load_ms"] > 1000); a["small"] += int(r["load_ms"] < 100)
for a in agg.values():
    a["load_avg"] = round(a["load"] / a["n"], 1) if a["n"] else 0
    a["inf_avg"] = round(a["inf"] / a["n"], 1) if a["n"] else 0

# P triples
rows = c.execute("SELECT r.match,r.innings,r.model,t.field_scope FROM results r JOIN tasks t USING(task_key) JOIN batches b ON b.batch_id=r.batch_id WHERE b.template='P_field_sweep'").fetchall()
key = defaultdict(set)
for r in rows: key[(r["match"], r["innings"], r["model"])].add(r["field_scope"])
complete = sum(1 for v in key.values() if {"probe_runs", "probe_wickets", "probe_both"} <= v)
missing = len(key) - complete

trial = c.execute("SELECT r.match,r.parse_ok,r.correct,r.response_meta_json FROM results r JOIN tasks t USING(task_key) WHERE t.field_scope='probe_wickets_p320'").fetchall()

brief = "# VETT 晚间简报（2026-11-19）\n\n"
brief += "绝对路径：" + str(V.WF) + "\n\n"
brief += "## 当前状态\n\n"
brief += "- workflow: " + s2["workflow_state"] + "；batch: " + s2["batch_state"] + "\n"
brief += "- supervisor " + str(s2["supervisor"]["pid"]) + " / worker " + str(s2["worker"]["pid"]) + "；worker heartbeat " + str(s2["worker"]["heartbeat_age_seconds"]) + " 秒\n"
brief += "- 结果 " + str(n2) + "；queue " + json.dumps(q2) + "\n"
brief += "- 两次快照结果增量：" + str(n2 - n1) + "（" + str(n1) + " → " + str(n2) + "）\n\n"
brief += "## 本次新增与配对\n\n"
brief += "- 恢复后新增结果：" + str(len(new)) + "\n"
brief += "- P 三元组：" + str(complete) + "/" + str(len(key)) + " 完整；缺 " + str(missing) + "\n"
brief += "- B151 llama P320 试验：" + str(len(trial)) + " 条，parse/correct " + str(sum(1 for x in trial if x["parse_ok"])) + "/" + str(sum(1 for x in trial if x["correct"])) + "\n\n"
brief += "## 每模型吞吐与加载（恢复后）\n\n"
for k, a in sorted(agg.items()):
    brief += "- " + k + ": n=" + str(a["n"]) + "，load_avg=" + str(a["load_avg"]) + " ms，inference_avg=" + str(a["inf_avg"]) + " ms，load>1s=" + str(a["big"]) + "，load<100ms=" + str(a["small"]) + "\n"
brief += "\n"
brief += "## GPU / CPU\n\n"
brief += "- RTX 3070 8192 MiB；/api/ps 中 qwen size_vram=5,148,633,988，context=8192；单模型全量 VRAM，无 CPU 拆分。\n"
brief += "- 派发已改为同模型连续：每个模型每批只加载一次，块内 load≈5ms。\n\n"
brief += "## 失败与恢复\n\n"
brief += "- 09:10:15 主机重启终止旧进程；15:42 用 auto_recover 恢复，非代码异常。\n"
brief += "- uncertain 计数：" + V.meta_get(c, "uncertain", "见 attempts") + "\n"
brief += "- llama probe_wickets 在 num_predict=200 有 10 条 length；B151 改 320 后 2/3 parse，match_0027 仍 length。\n"
brief += "- gemma2 B004 43 字段 JSON 不合法，done_reason=stop，非截断。\n\n"
brief += "## 余额与续航\n\n"
brief += "- probe_cursor " + V.meta_get(c, "probe_cursor", "") + "/360；剩余 unit 约 " + str(max(0, 360 - int(V.meta_get(c, "probe_cursor", "0") or 0))) + "，每 unit 最多 9 任务。\n"
brief += "- 按新分组吞吐（约 600–700 条/小时）估算 2–3 小时；按旧 240 条/小时估算 6–7 小时。\n"
brief += "- B152 正在运行，后续任务可继续领取。\n\n"
brief += "## 案例卡\n\n"
brief += "- 发布版关联：" + str(V.REPORTS / "CASE_CARD_PUBLICATION.md") + "\n"
brief += "- 反例：" + str(V.REPORTS / "CASE_CARD_COUNTEREXAMPLE.md") + "\n"
Path("reports/EVENING_BRIEF_20261119.md").write_text(brief, encoding="utf-8")

trialdoc = "# llama P320 隔离试验（B151）\n\n"
trialdoc += "- 配置：llama3.1:8b，probe_wickets，num_predict=320，field_scope=probe_wickets_p320。\n"
trialdoc += "- 3 任务，parse_ok " + str(sum(1 for x in trial if x["parse_ok"])) + "/3，correct " + str(sum(1 for x in trial if x["correct"])) + "/3。\n"
for x in trial:
    m = json.loads(x["response_meta_json"] or "{}")
    trialdoc += "- " + x["match"] + ": parse=" + str(x["parse_ok"]) + " correct=" + str(x["correct"]) + " done=" + str(m.get("done_reason")) + " eval=" + str(m.get("eval_count")) + "\n"
trialdoc += "\n- 结论：320 改善但未完全消除 length；冻结主流仍用 200，不静默改配置。\n"
Path("reports/LLAMA_P320_TRIAL.md").write_text(trialdoc, encoding="utf-8")

autodoc = "# 跨重启恢复入口\n\n"
autodoc += "- schtasks ONLOGON 创建被拒绝（Access is denied），未强行提升权限。\n"
autodoc += "- 改用当前用户 Startup 文件夹：" + r"C:\Users\PC\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\VETT_AutoRecover.cmd" + "\n"
autodoc += "- 触发：用户登录（ONLOGON），不是开机服务。\n"
autodoc += "- 目标：tools/auto_recover.py；检查单实例、user_stop、auto_start_disabled，等待/启动 Ollama，再调用 vettctl start。\n"
autodoc += "- 测试：停止时启动成功（supervisor 15312）；运行中再次执行记录 already running pid=15312; skip。\n"
Path("reports/AUTO_START_ENTRY.md").write_text(autodoc, encoding="utf-8")
print(json.dumps({"n1": n1, "n2": n2, "delta": n2 - n1, "p_triples": [complete, len(key)], "trial": len(trial), "queue": q2}, ensure_ascii=False))
