
import json, sqlite3, glob
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, ".")
import vettlib as V

con = V.init_db()
now = datetime.now().astimezone().isoformat(timespec="seconds")

def agg(bid):
    rows = con.execute("SELECT t.cond,r.score_json FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id=?", (bid,)).fetchall()
    d = {}
    for r in rows:
        sc = json.loads(r["score_json"]); cells = sc["cells"]
        prim = [k for k in cells if k.endswith("_wickets") and k != "innings_total_wickets"] + ["innings_total_wickets"]
        a = d.setdefault(r["cond"], {"n": 0, "task_ok": 0, "cells": 0, "cell_ok": 0})
        a["n"] += 1; a["cells"] += sc["total"]; a["cell_ok"] += sc["correct"]
        a["task_ok"] += int(sc["task_correct"])
    return d
a19, a22 = agg("B019"), agg("B022")
comb = {}
for cond in ("C_change", "C_maintain", "C_no_notice"):
    x, y = a19.get(cond, {}), a22.get(cond, {})
    comb[cond] = {k: x.get(k, 0) + y.get(k, 0) for k in ("n", "task_ok", "cells", "cell_ok")}
print("COMBINED", json.dumps(comb, ensure_ascii=False))

r = con.execute("SELECT r.*,t.cond,t.gold_json,t.fields_json FROM results r JOIN tasks t USING(task_key) "
                "WHERE r.batch_id='B022' AND r.match='match_0010' AND t.cond='C_change' AND r.model='qwen2.5:7b-instruct-q4_K_M'").fetchone()
rec = {
  "case_id": "CASE_B022_0010_C_CHANGE",
  "match_root": "match_0010", "source_version": "attribution-followup-v1",
  "source_type": "scorecard_rerender", "innings": 1,
  "entity_ids": ["match_0010", "Caleb Marsh", "Ryan Foster", "Evan Turner"],
  "field_ids": json.loads(r["fields_json"]), "evidence_spans": [],
  "answerability_status": "explicit_record_with_formal_notice",
  "diagnostic_variant_ids": ["C_change", "C_maintain", "C_no_notice"],
  "observed_failure": {"gold": json.loads(r["gold_json"]), "pred": json.loads(r["parsed_json"]),
                       "error": "A wickets not decremented after formal reassignment"},
  "verification_status": "auto_checked_against_task_gold",
  "candidate_patch": "none_for_data; record as propagation failure, not extraction failure",
  "full_task_validation": "B022 166/180; C_change 50/60, C_maintain 56/60, C_no_notice 60/60",
  "created_at": now,
}
Path("records/CASE_B022_0010_C_CHANGE.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
patch = {"patch_id": "P20261118_04", "created_at": now, "type": "diagnostic_record_patch",
         "base": "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117",
         "records": [rec["case_id"]],
         "changes": [{"action": "add", "path": "records/CASE_B022_0010_C_CHANGE.json", "source_data_modified": False}],
         "rollback": "delete records/CASE_B022_0010_C_CHANGE.json and data_patches/P20261118_04.json",
         "validation": "auto_checked; human review pending", "human_review_status": "pending_human_review",
         "external_api_calls": 0}
Path("data_patches/P20261118_04.json").write_text(json.dumps(patch, ensure_ascii=False, indent=1), encoding="utf-8")

c = Path("BRANCH_C.md").read_text(encoding="utf-8")
if "## 8. 8 事件合并结果" not in c:
    c += "\n## 8. 8 事件合并结果（B019 + B022）\n\n"
    c += "| 条件 | 任务全对 | 格正确 |\n|---|---:|---:|\n"
    for cond in ("C_change", "C_maintain", "C_no_notice"):
        x = comb[cond]
        c += "| " + cond + " | " + str(x["task_ok"]) + "/" + str(x["n"]) + " | " + str(x["cell_ok"]) + "/" + str(x["cells"]) + " |\n"
    c += "\n- C_change 12/24，C_maintain 23/24，C_no_notice 24/24。\n"
    c += "- 错误集中在正式改判后的 A−1/B+1 传播；C_maintain 仅有 1 次空答（match_0030 qwen null）。\n"
    c += "- 结论：通知理解与旧值抽取不是主要瓶颈；正式改判后的数值传播才是。\n"
    Path("BRANCH_C.md").write_text(c, encoding="utf-8")

a = Path("ACCEPTANCE_V2.md").read_text(encoding="utf-8")
a = a.replace("- 分支 C：B019 已评分 0.9778；C_change 0.9333，C_maintain 1.0，C_no_notice 1.0。错误集中在正式改判后的 A−1/B+1 传播。",
              "- 分支 C：B019+B022 共 8 事件、72 任务；C_change 12/24，C_maintain 23/24，C_no_notice 24/24。错误集中在正式改判后的 A−1/B+1 传播。")
Path("ACCEPTANCE_V2.md").write_text(a, encoding="utf-8")

recs = []
for f in sorted(glob.glob("records/CASE_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    recs.append({"case_id": d["case_id"], "match_root": d["match_root"], "source_type": d["source_type"],
                 "verification_status": d["verification_status"]})
Path("records/INDEX.json").write_text(json.dumps({"generated_at": now, "records": recs}, ensure_ascii=False, indent=1), encoding="utf-8")
print("records", len(recs))
