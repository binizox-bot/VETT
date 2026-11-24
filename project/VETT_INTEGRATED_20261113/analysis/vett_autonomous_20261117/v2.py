
"""v2 reliability layer: schema migration, task identity, attempts, timings, reports."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from datetime import datetime

import vettlib as V

SCHEMA_VERSION = "2"
SCORING_VERSION = "score-v1"
INPUT_VERSION = "commentary-v1"
PROMPT_VERSION = "p1"
RULE_VERSION = "r2"
REPLICATE_ID = "r0"


def _cols(con, table):
    return [r["name"] for r in con.execute("PRAGMA table_info(" + table + ")").fetchall()]


def _add(con, table, name, ddl):
    if name not in _cols(con, table):
        con.execute("ALTER TABLE " + table + " ADD COLUMN " + name + " " + ddl)


def decode_config(num_predict) -> dict:
    return {"temperature": V.OLLAMA["temperature"], "seed": V.OLLAMA["seed"],
            "num_ctx": V.OLLAMA["num_ctx"], "num_predict": int(num_predict),
            "top_p": 1.0}


def decode_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode("utf-8")).hexdigest()


def key_v2(match, innings, model, digest, decode_json, input_version, prompt_version,
           replicate_id, scope, prompt_sha) -> str:
    raw = "|".join([match, str(innings), model, digest or "nodigest", decode_hash(json.loads(decode_json)),
                    input_version, prompt_version, replicate_id, scope, prompt_sha])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _meta(con, key, default=""):
    r = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default


def ensure_schema(con) -> None:
    # tasks identity
    for name, ddl in [
        ("model_digest", "TEXT"), ("decode_json", "TEXT"), ("input_version", "TEXT"),
        ("prompt_version", "TEXT"), ("replicate_id", "TEXT"), ("legacy_task_key", "TEXT"),
        ("identity_status", "TEXT"), ("worker_heartbeat_at", "TEXT"), ("gold_json", "TEXT"),
    ]:
        _add(con, "tasks", name, ddl)
    # results
    for name, ddl in [
        ("scoring_version", "TEXT"), ("attempt_id", "TEXT"), ("model_digest", "TEXT"),
        ("decode_json", "TEXT"), ("input_version", "TEXT"), ("prompt_version", "TEXT"),
        ("legacy_task_key", "TEXT"), ("load_ms", "REAL"), ("inference_ms", "REAL"),
        ("scoring_ms", "REAL"),
    ]:
        _add(con, "results", name, ddl)
    # decisions
    for name, ddl in [
        ("source_batch_id", "TEXT"), ("source_result_ids", "TEXT"),
        ("rule_version", "TEXT"), ("trigger_metrics_json", "TEXT"),
    ]:
        _add(con, "decisions", name, ddl)
    # batches
    for name, ddl in [
        ("scoring_version", "TEXT"), ("manifest_version", "TEXT"),
        ("template_version", "TEXT"), ("plan_ms", "REAL"),
    ]:
        _add(con, "batches", name, ddl)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS attempts (
      attempt_id TEXT PRIMARY KEY, task_key TEXT, batch_id TEXT, attempt_no INTEGER,
      pid INTEGER, state TEXT, sent_at TEXT, response_at TEXT, persisted_at TEXT,
      accepted_at TEXT, duration_ms REAL, load_ms REAL, inference_ms REAL,
      scoring_ms REAL, request_json TEXT, response_meta_json TEXT, error TEXT,
      uncertain INTEGER DEFAULT 0, notes TEXT, created_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_attempts_task ON attempts(task_key);
    CREATE INDEX IF NOT EXISTS idx_attempts_state ON attempts(state);
    CREATE TABLE IF NOT EXISTS task_key_map (
      old_key TEXT PRIMARY KEY, new_key TEXT, batch_id TEXT, match TEXT,
      innings INTEGER, model TEXT, cond TEXT, replicate_id TEXT,
      created_at TEXT, reason TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_keymap_new ON task_key_map(new_key);
    """)
    defaults = {
        "schema_version": "0",
        "run_started_at": "",
        "segment_started_at": "",
        "long_run_target_hours": "8",
        "last_hourly_report_at": "",
        "last_stage_report_date": "",
        "stop_reason": "",
        "worker_heartbeat_at": "",
        "last_plan_attempt_at": "",
        "planning_mode": "rule_template",
    }
    for k, v in defaults.items():
        con.execute("INSERT OR IGNORE INTO meta(key, value) VALUES (?,?)", (k, v))
    con.commit()
    if _meta(con, "schema_version") != SCHEMA_VERSION:
        backfill(con)
        con.execute("INSERT INTO meta(key,value) VALUES ('schema_version',?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (SCHEMA_VERSION,))
        con.commit()


def backfill(con) -> None:
    now = V.now_iso()
    for t in con.execute("SELECT * FROM tasks").fetchall():
        if t["model_digest"]:
            continue
        digest = V.model_digest(t["model"])
        dec = decode_config(t["num_predict"] or 300)
        dec_json = json.dumps(dec, sort_keys=True)
        con.execute("UPDATE tasks SET model_digest=?, decode_json=?, input_version=?, prompt_version=?, "
                    "replicate_id=?, legacy_task_key=?, identity_status='legacy' WHERE task_key=?",
                    (digest, dec_json, INPUT_VERSION, PROMPT_VERSION, REPLICATE_ID,
                     t["task_key"], t["task_key"]))
        new_key = key_v2(t["match"], t["innings"], t["model"], digest, dec_json,
                         INPUT_VERSION, PROMPT_VERSION, REPLICATE_ID, t["field_scope"], t["prompt_sha"])
        con.execute("INSERT OR IGNORE INTO task_key_map(old_key,new_key,batch_id,match,innings,model,cond,"
                    "replicate_id,created_at,reason) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (t["task_key"], new_key, t["batch_id"], t["match"], t["innings"], t["model"],
                     t["cond"], REPLICATE_ID, now, "v2_migration"))
    for r in con.execute("SELECT * FROM results").fetchall():
        if r["scoring_version"]:
            continue
        meta = {}
        try:
            meta = json.loads(r["response_meta_json"] or "{}")
        except Exception:
            pass
        tm = lambda k: round(float(meta.get(k) or 0) / 1e6, 1)
        rt = con.execute("SELECT * FROM tasks WHERE task_key=?", (r["task_key"],)).fetchone()
        digest = (rt["model_digest"] if rt else "") or (meta.get("model_digest") or V.model_digest(r["model"]))
        dec_json = (rt["decode_json"] if rt else "") or json.dumps(decode_config(300), sort_keys=True)
        con.execute("UPDATE results SET scoring_version='score-v1-legacy', attempt_id=?, model_digest=?, "
                    "decode_json=?, input_version=?, prompt_version=?, legacy_task_key=?, "
                    "load_ms=?, inference_ms=? WHERE task_key=?",
                    ("legacy-" + r["task_key"][:12], digest, dec_json, INPUT_VERSION, PROMPT_VERSION,
                     r["task_key"], tm("load_duration"), tm("eval_duration"), r["task_key"]))
    for d in con.execute("SELECT * FROM decisions").fetchall():
        if d["rule_version"]:
            continue
        src = None
        nb = d["next_batch_id"] or ""
        if nb.startswith("B") and nb[1:].isdigit():
            n = int(nb[1:])
            if n > 1:
                cand = "B" + str(n - 1).zfill(3)
                if con.execute("SELECT 1 FROM batches WHERE batch_id=?", (cand,)).fetchone():
                    src = cand
        con.execute("UPDATE decisions SET source_batch_id=?, source_result_ids='[]', "
                    "rule_version='r1-historical', trigger_metrics_json=? WHERE id=?",
                    (src, json.dumps({"observation": d["observation"]}, ensure_ascii=False), d["id"]))
    for b in con.execute("SELECT * FROM batches").fetchall():
        if b["scoring_version"]:
            continue
        con.execute("UPDATE batches SET scoring_version='score-v1', manifest_version='v1', "
                    "template_version='v1' WHERE batch_id=?", (b["batch_id"],))
    con.commit()


def task_identity(task) -> dict:
    dec_json = task["decode_json"] or json.dumps(decode_config(task["num_predict"] or 300), sort_keys=True)
    return {"model_digest": task["model_digest"] or V.model_digest(task["model"]),
            "decode_json": dec_json,
            "input_version": task["input_version"] or INPUT_VERSION,
            "prompt_version": task["prompt_version"] or PROMPT_VERSION,
            "replicate_id": task["replicate_id"] or REPLICATE_ID}


def new_attempt(con, task, pid: int) -> str:
    import uuid
    attempt_id = uuid.uuid4().hex
    no = int(task["attempts"] or 1)
    con.execute("INSERT INTO attempts(attempt_id,task_key,batch_id,attempt_no,pid,state,created_at) "
                "VALUES (?,?,?,?,?,?,?)",
                (attempt_id, task["task_key"], task["batch_id"], no, pid, "claimed", V.now_iso()))
    con.commit()
    return attempt_id


def attempt_set(con, attempt_id: str, state: str, **kw) -> None:
    fields = ["state=?"]
    vals = [state]
    for k, v in kw.items():
        fields.append(k + "=?")
        vals.append(v)
    vals.append(attempt_id)
    con.execute("UPDATE attempts SET " + ", ".join(fields) + " WHERE attempt_id=?", vals)
    con.commit()


def latest_attempt(con, task_key: str):
    return con.execute("SELECT * FROM attempts WHERE task_key=? ORDER BY attempt_no DESC, created_at DESC LIMIT 1",
                       (task_key,)).fetchone()


def mark_uncertain(con, task_key: str, note: str) -> None:
    a = latest_attempt(con, task_key)
    if a and a["state"] in ("sent", "responded", "claimed"):
        con.execute("UPDATE attempts SET state='uncertain', uncertain=1, notes=? WHERE attempt_id=?",
                    (note, a["attempt_id"]))
        con.commit()
        V.event("attempt_uncertain", {"task_key": task_key, "attempt_id": a["attempt_id"], "note": note}, con)


def heartbeat_age(con=None) -> float:
    ts = ""
    if con is not None:
        ts = _meta(con, "worker_heartbeat_at", "")
    if ts:
        try:
            return round(time.time() - datetime.fromisoformat(ts).timestamp(), 1)
        except Exception:
            pass
    p = V.STATE / "worker.heartbeat"
    if not p.exists():
        return -1.0
    return round(time.time() - p.stat().st_mtime, 1)


def run_stats(con) -> dict:
    started = _meta(con, "segment_started_at", "") or _meta(con, "run_started_at", "")
    elapsed = 0.0
    if started:
        try:
            elapsed = round(time.time() - datetime.fromisoformat(started).timestamp(), 1)
        except Exception:
            pass
    q = {r["status"]: r["n"] for r in con.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")}
    sums = con.execute("SELECT COUNT(*) n, COALESCE(SUM(load_ms),0) load, COALESCE(SUM(inference_ms),0) inf, "
                       "COALESCE(SUM(scoring_ms),0) score, COALESCE(SUM(duration_ms),0) total "
                       "FROM results").fetchone()
    plan = con.execute("SELECT COALESCE(SUM(plan_ms),0) p FROM batches").fetchone()["p"]
    exc = con.execute("SELECT COUNT(*) n FROM events WHERE kind IN ('task_exception','supervisor_error',"
                      "'planner_error','batch_score_failed')").fetchone()["n"]
    uncertain = con.execute("SELECT COUNT(*) n FROM attempts WHERE uncertain=1").fetchone()["n"]
    attempts = con.execute("SELECT COUNT(*) n FROM attempts").fetchone()["n"]
    return {"elapsed_seconds": elapsed, "elapsed_hours": round(elapsed / 3600.0, 2),
            "queue": q, "results": sums["n"], "load_ms": round(sums["load"], 1),
            "inference_ms": round(sums["inf"], 1), "scoring_ms": round(sums["score"], 1),
            "request_total_ms": round(sums["total"], 1), "plan_ms": round(plan, 1),
            "waiting_ms_est": round(max(0.0, elapsed * 1000 - sums["inf"] - sums["score"] - plan), 1),
            "exceptions": exc, "attempts": attempts, "uncertain_attempts": uncertain}


def _render_stats(s: dict) -> str:
    return "\n".join([
        "- run elapsed: " + str(s["elapsed_hours"]) + " h (" + str(s["elapsed_seconds"]) + " s)",
        "- queue: " + json.dumps(s["queue"], ensure_ascii=False),
        "- results: " + str(s["results"]) + "; attempts: " + str(s["attempts"]) +
        "; uncertain: " + str(s["uncertain_attempts"]),
        "- load ms: " + str(s["load_ms"]) + "; inference ms: " + str(s["inference_ms"]) +
        "; scoring ms: " + str(s["scoring_ms"]),
        "- planning ms: " + str(s["plan_ms"]) + "; waiting ms est: " + str(s["waiting_ms_est"]),
        "- exceptions: " + str(s["exceptions"]),
    ])


def write_hourly(con) -> str:
    s = run_stats(con)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lines = ["# VETT hourly report " + stamp, "", _render_stats(s), "",
             "## Workflow", "", "- state: " + _meta(con, "state", ""),
             "- worker pid: " + _meta(con, "worker_pid", ""),
             "- supervisor pid: " + _meta(con, "supervisor_pid", ""), "",
             "## Batches", ""]
    for b in con.execute("SELECT batch_id,template,status,accuracy FROM batches ORDER BY seq"):
        lines.append("- " + b["batch_id"] + " " + b["template"] + " " + b["status"] + " " + str(b["accuracy"]))
    path = V.REPORTS / ("HOURLY_" + stamp + ".md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    V.meta_set(con, "last_hourly_report_at", V.now_iso())
    con.commit()
    V.event("hourly_report", {"path": str(path), "elapsed_hours": s["elapsed_hours"]}, con)
    return str(path)


def write_stage(con) -> str:
    s = run_stats(con)
    stamp = datetime.now().strftime("%Y%m%d")
    lines = ["# VETT stage report " + stamp + " 08:00", "", _render_stats(s), "",
             "## Decisions", ""]
    for d in con.execute("SELECT rule_id,source_batch_id,next_batch_id,rationale FROM decisions ORDER BY id"):
        lines.append("- " + str(d["rule_id"]) + " " + str(d["source_batch_id"]) + " -> " +
                     str(d["next_batch_id"]) + ": " + str(d["rationale"]))
    lines += ["", "## Note", "", "- Inference continues; this report is a snapshot, not a stop condition."]
    path = V.REPORTS / ("STAGE_" + stamp + "_0800.md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    V.meta_set(con, "last_stage_report_date", stamp)
    con.commit()
    V.event("stage_report", {"path": str(path)}, con)
    return str(path)
