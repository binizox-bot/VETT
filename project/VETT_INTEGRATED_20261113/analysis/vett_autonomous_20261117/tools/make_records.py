
import json, sqlite3, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vettlib as V

con = V.init_db()
now = datetime.now().astimezone().isoformat(timespec="seconds")
outdir = Path("records"); outdir.mkdir(exist_ok=True)

def find_result(bid, match, scope, model):
    r = con.execute("SELECT r.*, t.fields_json, t.cond FROM results r JOIN tasks t USING(task_key) "
                    "WHERE r.batch_id=? AND r.match=? AND t.field_scope=? AND r.model=?",
                    (bid, match, scope, model)).fetchone()
    return dict(r) if r else None

# CASE 1: B012 qwen runs-only null
m = "match_0066"; inn = 1
built = V.build_conditions(m, inn)
ev = built["evidence_idx"]
ss = V.L.sentences(V.load_bundle(m)["text"])
excerpt = built["variants"]["E"]
r1 = find_result("B012", m, "probe_runs", "qwen2.5:7b-instruct-q4_K_M")
r2 = find_result("B012", m, "probe_wickets", "qwen2.5:7b-instruct-q4_K_M")
case1 = {
  "case_id": "CASE_B012_0066_QWEN_RUNS",
  "match_root": m, "source_version": "commentary-v1", "source_type": "published_commentary",
  "innings": inn, "entity_ids": [m], "field_ids": ["inn1.total_runs"],
  "evidence_spans": [{"sentence_index": ev, "text": ss[ev] if ev is not None else excerpt}],
  "answerability_status": "explicit_total_present",
  "diagnostic_variant_ids": ["probe_runs", "probe_wickets", "probe_both"],
  "observed_failure": {"probe_runs_pred": json.loads(r1["parsed_json"]).get("inn1.total_runs") if r1 and r1["parsed_json"] else None,
                       "probe_wickets_pred": json.loads(r2["parsed_json"]).get("inn1.total_wickets") if r2 and r2["parsed_json"] else None,
                       "runs_only_correct": bool(r1 and r1["correct"]), "wickets_only_correct": bool(r2 and r2["correct"])},
  "verification_status": "auto_checked_source_explicit",
  "candidate_patch": "none_for_data; record as model field-binding failure (runs null, wickets correct)",
  "full_task_validation": "B012 22/24 cells; runs 10/12, wickets 12/12",
  "created_at": now,
}
# CASE 2: B003 cross-innings deletion
audit = json.load(open("reports/AUDIT_B003.json", encoding="utf-8"))
wi = next(d for d in audit["deletions"] if d["cond"] == "WI")
oi = next(d for d in audit["deletions"] if d["cond"] == "OI")
b3 = con.execute("SELECT score_json FROM batches WHERE batch_id='B003'").fetchone()
sc3 = json.loads(b3["score_json"])
case2 = {
  "case_id": "CASE_B003_0002_CROSS_INNINGS",
  "match_root": "match_0002", "source_version": "commentary-v1", "source_type": "controlled_rewrite",
  "innings": 2, "entity_ids": ["match_0002"], "field_ids": ["inn2.total_runs", "inn2.total_wickets"],
  "evidence_spans": [{"sentence_index": None, "text": d["deleted"][0]} for d in (wi, oi)],
  "answerability_status": "explicit_total_present_in_all_variants",
  "diagnostic_variant_ids": ["O", "WI", "OI"],
  "observed_failure": {"O": sc3["by_condition"]["O"], "WI": sc3["by_condition"]["WI"], "OI": sc3["by_condition"]["OI"],
                       "wi_deleted": wi["deleted"], "oi_deleted": oi["deleted"]},
  "verification_status": "auto_checked_source_diff",
  "candidate_patch": "add length-matched non-evidence deletion (OIC/NEI); pair OIC against B003 O across batches",
  "full_task_validation": "43-field validation not run for this root",
  "created_at": now,
}
# CASE 3: B004 full table
a4 = json.load(open("reports/AUDIT_FOLLOWUP.json", encoding="utf-8"))["B004"]
b4 = con.execute("SELECT score_json FROM batches WHERE batch_id='B004'").fetchone()
sc4 = json.loads(b4["score_json"])
case3 = {
  "case_id": "CASE_B004_0002_FULL_TABLE",
  "match_root": "match_0002", "source_version": "commentary-v1", "source_type": "published_commentary",
  "innings": "both", "entity_ids": ["match_0002"], "field_ids": list(sc4["by_field"].keys()),
  "evidence_spans": [],
  "answerability_status": "partial_text_verified_35_of_43",
  "diagnostic_variant_ids": ["T4_full_table"],
  "observed_failure": {"full": a4["full"], "text_verified_subset": a4["string_verified_subset"],
                       "target_four": a4["target_four"],
                       "unverified_fields": [f for f, ok in json.load(open("reports/AUDIT_B004.json", encoding="utf-8"))["full_table"]["string_present"].items() if not ok]},
  "verification_status": "auto_checked_string_presence_only",
  "candidate_patch": "do_not_promote_to_validated_full_table; request human review of unverified fields",
  "full_task_validation": "pending; 25/129 is not a validated full-table reading",
  "created_at": now,
}
records = [case1, case2, case3]
for rec in records:
    (outdir / (rec["case_id"] + ".json")).write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
index = {"generated_at": now, "records": [{"case_id": r["case_id"], "match_root": r["match_root"],
                                          "source_type": r["source_type"], "verification_status": r["verification_status"]}
                                         for r in records]}
(outdir / "INDEX.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
patch = {
  "patch_id": "P20261118_01",
  "created_at": now,
  "type": "diagnostic_record_patch",
  "base": "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117",
  "records": [r["case_id"] for r in records],
  "changes": [{"action": "add", "path": "records/" + r["case_id"] + ".json", "source_data_modified": False} for r in records],
  "rollback": "delete records/ and data_patches/P20261118_01.json; no 220-match source or R28 file was modified",
  "validation": "auto_checked; human review pending; full-task validation pending for cases 2 and 3",
  "human_review_status": "pending_human_review",
  "external_api_calls": 0,
}
Path("data_patches").mkdir(exist_ok=True)
Path("data_patches/P20261118_01.json").write_text(json.dumps(patch, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"records": [r["case_id"] for r in records], "patch": "P20261118_01"}, ensure_ascii=False))
print("case1", json.dumps(case1["observed_failure"], ensure_ascii=False))
print("case2", json.dumps(case2["observed_failure"]["O"], ensure_ascii=False), json.dumps(case2["observed_failure"]["OI"], ensure_ascii=False))
print("case3", json.dumps(a4, ensure_ascii=False)[:400])
