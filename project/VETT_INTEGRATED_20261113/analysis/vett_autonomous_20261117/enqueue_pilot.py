"""Enqueue the two-match pilot as B209Z, reusing verifiable identical historical results."""
import json, sys
from pathlib import Path
WF = Path(r"D:\Download\VETT_Cricket_Complete_Delivery_R19_20261017\VETT_INTEGRATED_20261113\analysis\vett_autonomous_20261117")
sys.path.insert(0, str(WF))
import vettlib as V
import v2
import codex_bridge as CB

design, groups = CB.build_pilot()
tasks = [t for g in groups for t in (g if isinstance(g, list) else [g])]
con = V.connect()
if con.execute("SELECT 1 FROM batches WHERE batch_id='B209Z'").fetchone():
    print(json.dumps({"ok": False, "error": "B209Z exists"})); sys.exit(0)
new, reused, pending = [], [], []
for t in tasks:
    rr = con.execute("SELECT batch_id, parse_ok, correct, raw_output FROM results WHERE task_key=?", (t["task_key"],)).fetchone()
    if rr:
        reused.append({"cond": t["cond"], "model": t["model"], "match": t["match"], "innings": t["innings"],
                       "task_key": t["task_key"], "source_batch": rr[0], "parse_ok": rr[1],
                       "correct": rr[2], "raw_output": rr[3]})
        continue
    if con.execute("SELECT 1 FROM tasks WHERE task_key=?", (t["task_key"],)).fetchone():
        pending.append({"cond": t["cond"], "model": t["model"], "task_key": t["task_key"]})
        continue
    new.append(t)
batch_id, seq, NOW = "B209Z", 209, V.now_iso()
design["cost"]["requests"] = len(new)
design["reused_results"] = len(reused)
design["pending_duplicates"] = len(pending)
manifest = {"batch_id": batch_id, "seq": seq, "template": design["template"], "created_at": NOW,
            "design": design, "schema_version": v2.SCHEMA_VERSION, "scoring_version": v2.SCORING_VERSION,
            "tasks": [{k: t[k] for k in ("task_key","legacy_task_key","match","innings","model","cond",
                                         "field_scope","fields","prompt","prompt_sha","text_sha",
                                         "num_predict","gold","model_digest","decode_json",
                                         "input_version","prompt_version","replicate_id")} for t in tasks],
            "reused": reused, "rejected": pending}
mpath = V.BATCHES / (batch_id + ".json")
mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
msha = V.sha256_text(mpath.read_text(encoding="utf-8"))
con.execute("INSERT INTO batches(batch_id, seq, template, created_at, hypothesis, rationale, design_json, manifest_path, manifest_sha, status, parent_batch_id, trigger_json, cost_json, updated_at, scoring_version, manifest_version, template_version, plan_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (batch_id, seq, design["template"], NOW, design["hypothesis"], design["rationale"],
             json.dumps(design, ensure_ascii=False), str(mpath), msha, "running", None,
             json.dumps({"rule_id": "X1", "note": "codex pilot; reuses " + str(len(reused)) + " identical historical results"}, ensure_ascii=False),
             json.dumps(design["cost"], ensure_ascii=False), NOW, v2.SCORING_VERSION, "v2", "v2", 0.0))
for t in new:
    con.execute("INSERT INTO tasks(task_key, batch_id, match, innings, model, cond, field_scope, fields_json, prompt, prompt_sha, text_sha, num_predict, status, attempts, created_at, updated_at, model_digest, decode_json, input_version, prompt_version, replicate_id, legacy_task_key, identity_status, gold_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (t["task_key"], batch_id, t["match"], t["innings"], t["model"], t["cond"], t["field_scope"],
                 json.dumps(t["fields"]), t["prompt"], t["prompt_sha"], t["text_sha"], t["num_predict"],
                 "queued", 0, NOW, NOW, t["model_digest"], t["decode_json"], t["input_version"],
                 t["prompt_version"], t["replicate_id"], t["legacy_task_key"], "v2", json.dumps(t["gold"], ensure_ascii=False)))
    con.execute("INSERT OR IGNORE INTO task_key_map(old_key,new_key,batch_id,match,innings,model,cond,replicate_id,created_at,reason) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (t["legacy_task_key"], t["task_key"], batch_id, t["match"], t["innings"], t["model"], t["cond"], t["replicate_id"], NOW, "v2_new_task"))
con.commit()
V.event("batch_frozen", {"batch_id": batch_id, "template": design["template"], "tasks": len(new),
                         "reused": len(reused), "pending": len(pending), "rejected": 0,
                         "manifest_sha": msha, "note": "codex pilot, priority seq 209"}, con)
con.commit()
(Path(V.BATCHES) / (batch_id + "_REUSE.json")).write_text(json.dumps(reused, ensure_ascii=False, indent=1), encoding="utf-8")
con.close()
print(json.dumps({"ok": True, "batch_id": batch_id, "new": len(new), "reused": len(reused),
                  "pending": len(pending), "manifest": str(mpath), "manifest_sha": msha,
                  "reused_detail": [(r["cond"], r["model"].split(":")[0], r["source_batch"], r["correct"]) for r in reused]}))
