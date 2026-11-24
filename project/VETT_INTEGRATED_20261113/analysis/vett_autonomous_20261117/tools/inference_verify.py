
import json, sqlite3, time, urllib.request
from pathlib import Path
from datetime import datetime

c = sqlite3.connect("state/workflow.db"); c.row_factory = sqlite3.Row
for k, v in (("dispatch_order", "model_grouped"), ("auto_start_entry", "startup_folder_logon")):
    c.execute("INSERT INTO meta(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, v))
c.commit()
c.execute("INSERT INTO events(ts,kind,payload) VALUES (?,?,?)",
          (datetime.now().astimezone().isoformat(timespec="seconds"), "dispatch_order_changed",
           json.dumps({"order": "batch_id, model, rowid", "reason": "reduce Ollama reloads"}, ensure_ascii=False)))
c.commit()

ps = {}
for i in range(12):
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/ps", timeout=3) as r:
            ps = json.loads(r.read().decode())
    except Exception as e:
        ps = {"error": str(e)}
    if ps.get("models"):
        break
    time.sleep(2)

rows = c.execute("SELECT r.*, t.num_predict FROM results r JOIN tasks t USING(task_key)").fetchall()
max_prompt = 0; max_match = None
done = {}
parse_fail = 0; empty = 0; length_hits = []
for r in rows:
    meta = json.loads(r["response_meta_json"] or "{}")
    pe = meta.get("prompt_eval_count") or 0
    if pe > max_prompt:
        max_prompt = pe; max_match = (r["match"], r["model"], r["cond"])
    dr = meta.get("done_reason") or "none"
    done[dr] = done.get(dr, 0) + 1
    if not r["parse_ok"]:
        parse_fail += 1
    if not (r["raw_output"] or "").strip():
        empty += 1
    if (meta.get("eval_count") or 0) >= int(r["num_predict"] or 300) - 1:
        length_hits.append({"match": r["match"], "model": r["model"], "cond": r["cond"],
                            "eval_count": meta.get("eval_count"), "num_predict": r["num_predict"],
                            "done_reason": meta.get("done_reason")})
out = {"ps": ps, "results": len(rows), "max_prompt_eval_count": max_prompt,
       "max_prompt_match": max_match, "done_reasons": done, "parse_failures": parse_fail,
       "empty_raw": empty, "length_hits": length_hits[:20], "length_hits_count": len(length_hits)}
Path("reports/INFERENCE_VERIFICATION_20261119.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False)[:3000])
