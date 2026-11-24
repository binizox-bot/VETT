
import json, sqlite3
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, ".")
import vettlib as V

con = V.init_db()
rows = con.execute("SELECT r.match,r.innings,r.model,r.parsed_json,t.prompt FROM results r JOIN tasks t USING(task_key) "
                   "WHERE r.match='match_0001' AND r.innings=1 AND r.model='llama3.1:8b' AND t.cond='E'").fetchall()
print("candidates", len(rows))
for x in rows:
    print(x["innings"], x["model"], (x["parsed_json"] or "")[:200])
row = rows[0]
gold = V.gold_target(V.load_bundle("match_0001")["md"], 1)
pred = json.loads(row["parsed_json"]) if row["parsed_json"] else {}
rec = json.loads(Path("records/CASE_COV_0001_LLAMA_E_WICKETS.json").read_text(encoding="utf-8"))
rec["observed_failure"] = {"gold": gold, "pred": pred,
                           "error": "excerpt contains '144 all out' but the model's wickets value is wrong; not an excerpt-availability failure"}
rec["verification_status"] = "auto_checked_source_explicit"
rec["full_task_validation"] = "coverage E vs O: this cell O correct, E wrong; 10 such E losses overall"
rec["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
Path("records/CASE_COV_0001_LLAMA_E_WICKETS.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
print("gold", gold, "pred", pred)
