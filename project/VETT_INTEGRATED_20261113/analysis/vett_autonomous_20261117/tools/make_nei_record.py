
import json, sqlite3, glob
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, ".")
import vettlib as V

con = V.init_db()
now = datetime.now().astimezone().isoformat(timespec="seconds")

def cells(bid, cond):
    rows = con.execute("SELECT r.model,r.score_json,t.cond FROM results r JOIN tasks t USING(task_key) "
                       "WHERE r.batch_id=? AND t.cond=?", (bid, cond)).fetchall()
    return {r["model"]: json.loads(r["score_json"]) for r in rows}

b3o = cells("B003", "O"); b3oi = cells("B003", "OI")
b21 = {"NEI_OI": cells("B021", "NEI_OI"), "NEI_WI": cells("B021", "NEI_WI")}
def total(d):
    c = t = 0
    for sc in d.values():
        c += sc["correct"]; t += sc["total"]
    return c, t
rec = {
  "case_id": "CASE_B021_0002_NEI_CONTROL",
  "match_root": "match_0002", "source_version": "commentary-v1",
  "source_type": "controlled_rewrite", "innings": 2,
  "entity_ids": ["match_0002"], "field_ids": ["inn2.total_runs", "inn2.total_wickets"],
  "evidence_spans": [],
  "answerability_status": "explicit_total_present_in_all_variants",
  "diagnostic_variant_ids": ["O", "WI", "OI", "NEI_OI", "NEI_WI"],
  "observed_failure": {
     "O": total(b3o), "OI": total(b3oi),
     "NEI_OI": total(b21["NEI_OI"]), "NEI_WI": total(b21["NEI_WI"]),
     "deleted_chars": {"WI": 269, "OI": 364, "NEI_OI": 313, "NEI_WI": 251},
     "interpretation": "length-matched non-evidence deletion also fails; B003 OI +3 gain is not reproduced by NEI, so deletion-specificity is not established"
  },
  "verification_status": "auto_checked_source_diff",
  "candidate_patch": "do_not_claim_OI_specific_effect; retain as null/ambiguous and expand matched controls",
  "full_task_validation": "B021 0/6 cells; B003 O 0/6, OI 3/6",
  "created_at": now,
}
Path("records/CASE_B021_0002_NEI_CONTROL.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
patch = {"patch_id": "P20261118_03", "created_at": now, "type": "diagnostic_record_patch",
         "base": "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117",
         "records": [rec["case_id"]],
         "changes": [{"action": "add", "path": "records/CASE_B021_0002_NEI_CONTROL.json", "source_data_modified": False}],
         "rollback": "delete records/CASE_B021_0002_NEI_CONTROL.json and data_patches/P20261118_03.json",
         "validation": "auto_checked; human review pending", "human_review_status": "pending_human_review",
         "external_api_calls": 0}
Path("data_patches/P20261118_03.json").write_text(json.dumps(patch, ensure_ascii=False, indent=1), encoding="utf-8")

sci = Path("SCIENCE_CORRECTIONS.md").read_text(encoding="utf-8")
add = """

## 8. 长度匹配 NEI 对照（B021）

- OI 删除句 364 字；NEI_OI 删除 313 字，差 51。
- WI 删除句 269 字；NEI_WI 删除 251 字，差 18。
- B021 结果：NEI_OI 0/6，NEI_WI 0/6；B003 O 0/6、OI 3/6。
- 结论：删掉长度匹配的非证据句也会让模型全错，不能把 B003 的 OI +3 直接解释为“删另一局比分”的特异收益。该效应应标为未定，需更多匹配对照。
"""
if "## 8. 长度匹配 NEI 对照" not in sci:
    Path("SCIENCE_CORRECTIONS.md").write_text(sci + add, encoding="utf-8")

c = Path("BRANCH_C.md").read_text(encoding="utf-8")
if "B022" not in c:
    c += "\n## 7. 全样本批 B022\n\n- 其余 4 个事件 × 3 条件 × 3 模型 = 36 任务，已冻结并在 B019 之后运行；与 B019 合计覆盖 8 个事件。\n"
    Path("BRANCH_C.md").write_text(c, encoding="utf-8")

recs = []
for f in sorted(glob.glob("records/CASE_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    recs.append({"case_id": d["case_id"], "match_root": d["match_root"], "source_type": d["source_type"],
                 "verification_status": d["verification_status"]})
Path("records/INDEX.json").write_text(json.dumps({"generated_at": now, "records": recs}, ensure_ascii=False, indent=1), encoding="utf-8")
print("records", len(recs), "NEI", rec["observed_failure"]["NEI_OI"], rec["observed_failure"]["NEI_WI"])
