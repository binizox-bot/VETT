
import json, sqlite3, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
now = datetime.now().astimezone().isoformat(timespec="seconds")
rows = con.execute("SELECT r.task_key,r.match,r.model,r.parsed_json,r.score_json,t.cond,t.gold_json,t.fields_json "
                   "FROM results r JOIN tasks t USING(task_key) WHERE r.batch_id='B019'").fetchall()
from collections import defaultdict
agg = defaultdict(lambda: {"n": 0, "ok": 0})
for r in rows:
    sc = json.loads(r["score_json"]); cells = sc["cells"]
    prim = [k for k in cells if k.endswith("_wickets") and k != "innings_total_wickets"] + ["innings_total_wickets"]
    ok = all(cells[k]["ok"] for k in prim)
    a = agg[r["cond"]]; a["n"] += 1; a["ok"] += int(ok)
print("PRIMARY3", {k: dict(v) for k, v in agg.items()})

r = con.execute("SELECT r.*,t.cond,t.gold_json,t.fields_json FROM results r JOIN tasks t USING(task_key) "
                "WHERE r.batch_id='B019' AND r.match='match_0003' AND t.cond='C_change' AND r.model='qwen2.5:7b-instruct-q4_K_M'").fetchone()
rec = {
  "case_id": "CASE_B019_0003_C_CHANGE",
  "match_root": "match_0003",
  "source_version": "attribution-followup-v1",
  "source_type": "scorecard_rerender",
  "innings": 1,
  "entity_ids": ["match_0003", "Brandon Hale", "Evan Clarke", "Connor Reed"],
  "field_ids": json.loads(r["fields_json"]),
  "evidence_spans": [],
  "answerability_status": "explicit_record_with_formal_notice",
  "diagnostic_variant_ids": ["C_change", "C_maintain", "C_no_notice"],
  "observed_failure": {"gold": json.loads(r["gold_json"]), "pred": json.loads(r["parsed_json"]),
                       "error": "A_wickets not decremented (4 vs 3) after formal reassignment"},
  "verification_status": "auto_checked_against_task_gold",
  "candidate_patch": "none_for_data; record as notification-to-figure propagation failure",
  "full_task_validation": "B019 176/180 cells; C_change 56/60; C_maintain and C_no_notice 60/60 each",
  "created_at": now,
}
Path("records").mkdir(exist_ok=True)
Path("records/CASE_B019_0003_C_CHANGE.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
patch = {
  "patch_id": "P20261118_02",
  "created_at": now,
  "type": "diagnostic_record_patch",
  "base": "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117",
  "records": ["CASE_B019_0003_C_CHANGE"],
  "changes": [{"action": "add", "path": "records/CASE_B019_0003_C_CHANGE.json", "source_data_modified": False}],
  "rollback": "delete records/CASE_B019_0003_C_CHANGE.json and data_patches/P20261118_02.json",
  "validation": "auto_checked; human review pending",
  "human_review_status": "pending_human_review",
  "external_api_calls": 0,
}
Path("data_patches").mkdir(exist_ok=True)
Path("data_patches/P20261118_02.json").write_text(json.dumps(patch, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote CASE_B019_0003_C_CHANGE and P20261118_02")
print(json.dumps(rec["observed_failure"], ensure_ascii=False))
