
import json, sqlite3, glob
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, ".")
import vettlib as V

con = V.init_db()
now = datetime.now().astimezone().isoformat(timespec="seconds")
r = con.execute("SELECT r.*,t.gold_json,t.fields_json FROM results r JOIN tasks t USING(task_key) "
                "WHERE r.batch_id='B0' || '' AND 0").fetchone() if False else None
row = con.execute("SELECT r.*,t.gold_json,t.fields_json,t.prompt FROM results r JOIN tasks t USING(task_key) "
                  "WHERE r.match='match_0001' AND r.model='llama3.1:8b' AND t.cond='E' "
                  "ORDER BY r.created_at DESC LIMIT 1").fetchone()
gold = json.loads(row["gold_json"]) if row and row["gold_json"] else {}
pred = json.loads(row["parsed_json"]) if row and row["parsed_json"] else {}
excerpt = row["prompt"].split("Commentary:\n", 1)[1].rsplit("\n\nJSON:", 1)[0] if row and "Commentary:\n" in row["prompt"] else ""
rec = {
  "case_id": "CASE_COV_0001_LLAMA_E_WICKETS",
  "match_root": "match_0001", "source_version": "commentary-v1", "source_type": "published_commentary",
  "innings": 1, "entity_ids": ["match_0001"], "field_ids": ["inn1.total_wickets"],
  "evidence_spans": [{"text": "Stoneford eventually reached 144 all out in 35.3 overs"}],
  "answerability_status": "explicit_total_present",
  "diagnostic_variant_ids": ["O", "E"],
  "observed_failure": {"gold": gold, "pred": pred,
                       "error": "excerpt contains '144 all out' but model gave 35; not an excerpt-availability failure"},
  "verification_status": "auto_checked_source_explicit",
  "candidate_patch": "none_for_data; record as wickets-vs-runs field binding failure under a sufficient excerpt",
  "full_task_validation": "coverage E vs O: this cell O correct, E wrong; 10 such E losses overall",
  "created_at": now,
}
Path("records/CASE_COV_0001_LLAMA_E_WICKETS.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
patch = {"patch_id": "P20261118_05", "created_at": now, "type": "diagnostic_record_patch",
         "base": "VETT_INTEGRATED_20261113/analysis/vett_autonomous_20261117",
         "records": [rec["case_id"]],
         "changes": [{"action": "add", "path": "records/CASE_COV_0001_LLAMA_E_WICKETS.json", "source_data_modified": False}],
         "rollback": "delete records/CASE_COV_0001_LLAMA_E_WICKETS.json and data_patches/P20261118_05.json",
         "validation": "auto_checked; human review pending", "human_review_status": "pending_human_review",
         "external_api_calls": 0}
Path("data_patches/P20261118_05.json").write_text(json.dumps(patch, ensure_ascii=False, indent=1), encoding="utf-8")

sci = Path("SCIENCE_CORRECTIONS.md")
t = sci.read_text(encoding="utf-8")
add = """

## 11. 覆盖组反例：E 的 10 个 loss

- E 相对 O 共 264 对，gain 85、loss 10、net +75；loss 不是“摘录缺证据”造成的。
- 例 1：match_0001 inn1 llama，摘录含 “144 all out”，模型把 wickets 给成 35（疑似把 runs 当 wickets）。
- 例 2：match_0017 inn1 qwen，摘录含 “174 all out”，模型返回 null。
- 例 3：match_0049 inn2 qwen，摘录含 “96 all out”，模型返回 null。
- 结论：E 的失败集中在 wickets 字段绑定/空答，而不是证据不可用；与 B002/B005 的 wickets-only 失败一致。
- OI 的净效应集中在少数根：match_0001/0012 各 +4，match_0049 −1，多数根 0；进一步说明 OI 不是稳定单向效应。
"""
if "## 11. 覆盖组反例" not in t:
    sci.write_text(t + add, encoding="utf-8")
recs = []
for f in sorted(glob.glob("records/CASE_*.json")):
    d = json.load(open(f, encoding="utf-8"))
    recs.append({"case_id": d["case_id"], "match_root": d["match_root"], "source_type": d["source_type"],
                 "verification_status": d["verification_status"]})
Path("records/INDEX.json").write_text(json.dumps({"generated_at": now, "records": recs}, ensure_ascii=False, indent=1), encoding="utf-8")
print("records", len(recs), "gold", gold, "pred", pred)
