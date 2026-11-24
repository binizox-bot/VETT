
"""Single GPU inference worker (v2): one task, one attempt, independent heartbeat."""
from __future__ import annotations

import json
import os
import sys
import threading
import time

import vettlib as V
import v2


def beat(con=None) -> None:
    try:
        (V.STATE / "worker.heartbeat").write_text(V.now_iso(), encoding="utf-8")
    except Exception:
        pass
    if con is not None:
        try:
            V.meta_set(con, "worker_pid", os.getpid())
            V.meta_set(con, "worker_heartbeat_at", V.now_iso())
            con.commit()
        except Exception:
            pass


def heartbeat_loop(stop_event: threading.Event) -> None:
    while not stop_event.wait(5.0):
        try:
            c = V.connect()
            V.meta_set(c, "worker_heartbeat_at", V.now_iso())
            c.commit()
            c.close()
        except Exception:
            pass
        try:
            (V.STATE / "worker.heartbeat").write_text(V.now_iso(), encoding="utf-8")
        except Exception:
            pass


def claim(con, pid: int):
    con.execute("BEGIN IMMEDIATE")
    row = con.execute("SELECT * FROM tasks WHERE status='queued' ORDER BY batch_id, model, rowid LIMIT 1").fetchone()
    if row is None:
        con.commit()
        return None
    now = V.now_iso()
    cur = con.execute("UPDATE tasks SET status='claimed', claimed_by=?, claimed_at=?, attempts=attempts+1, "
                      "updated_at=? WHERE task_key=? AND status='queued'",
                      (pid, now, now, row["task_key"]))
    con.commit()
    if cur.rowcount != 1:
        return None
    d = dict(row)
    d["attempts"] = int(d.get("attempts") or 0) + 1
    d["attempt_id"] = v2.new_attempt(con, d, pid)
    return d


def append_row(batch_id: str, row: dict) -> None:
    path = V.RUNS / (batch_id + ".jsonl")
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def process(task: dict) -> None:
    con = V.connect()
    attempt_id = task["attempt_id"]
    sent = False
    stop_event = threading.Event()
    hb = threading.Thread(target=heartbeat_loop, args=(stop_event,), daemon=True)
    hb.start()
    try:
        if con.execute("SELECT 1 FROM results WHERE task_key=?", (task["task_key"],)).fetchone():
            v2.attempt_set(con, attempt_id, "duplicate_skipped", notes="result already exists")
            con.execute("UPDATE tasks SET status='done', error='duplicate_result_ignored', updated_at=? WHERE task_key=?",
                        (V.now_iso(), task["task_key"]))
            con.commit()
            V.event("duplicate_result_ignored", {"task_key": task["task_key"], "attempt_id": attempt_id}, con)
            return
        ident = v2.task_identity(task)
        now = V.now_iso()
        v2.attempt_set(con, attempt_id, "sent", sent_at=now)
        sent = True
        gen = None
        last_exc = None
        for attempt_i in range(5):
            try:
                gen = V.ollama_generate(task["model"], task["prompt"], task["num_predict"])
                break
            except Exception as exc:
                last_exc = exc
                msg = str(exc).lower()
                transient = any(k in msg for k in ("urlopen", "connection", "refused", "timed out", "timeout", "reset", "eof"))
                if attempt_i < 4 and transient:
                    V.event("ollama_retry", {"task_key": task["task_key"], "attempt": attempt_i + 1,
                                             "error": str(exc)[:200]}, con)
                    time.sleep(15)
                    continue
                raise
        if gen is None:
            raise last_exc
        meta = gen.get("meta") or {}
        load_ms = round(float(meta.get("load_duration") or 0) / 1e6, 1)
        inference_ms = round(float(meta.get("eval_duration") or 0) / 1e6, 1)
        if gen.get("error"):
            err = str(gen["error"])
            uncertain = any(k in err.lower() for k in ("timed out", "timeout", "connection", "reset", "broken pipe", "eof"))
            state = "uncertain" if uncertain else "failed"
            v2.attempt_set(con, attempt_id, state, response_at=V.now_iso(), duration_ms=gen["duration_ms"],
                           load_ms=load_ms, inference_ms=inference_ms,
                           request_json=json.dumps(gen["request"], ensure_ascii=False),
                           response_meta_json=json.dumps(meta, ensure_ascii=False),
                           error=err[:800], uncertain=1 if uncertain else 0,
                           notes="server-side execution unknown" if uncertain else "service error")
            max_attempts = int(V.CONFIG["limits"].get("max_attempts", 3))
            if uncertain and int(task["attempts"]) < max_attempts:
                con.execute("UPDATE tasks SET status='queued', claimed_by=NULL, claimed_at=NULL, error=?, updated_at=? "
                            "WHERE task_key=?", ("uncertain_requeued: " + err[:400], V.now_iso(), task["task_key"]))
                V.event("attempt_uncertain_requeued", {"task_key": task["task_key"], "attempt_id": attempt_id,
                                                       "attempts": task["attempts"], "error": err[:300]}, con)
            else:
                con.execute("UPDATE tasks SET status='failed', error=?, updated_at=? WHERE task_key=?",
                            (err[:800], V.now_iso(), task["task_key"]))
                V.event("task_failed", {"task_key": task["task_key"], "attempt_id": attempt_id, "error": err[:300]}, con)
            con.commit()
            return
        t_score = time.time()
        parsed = V.parse_json_object(gen["raw"])
        parse_ok = isinstance(parsed, dict)
        bundle = V.load_bundle(task["match"])
        if task.get("gold_json"):
            gold = json.loads(task["gold_json"])
        elif task["field_scope"] == "full43":
            gold = V.gold43(bundle["md"])
        else:
            gold = V.gold_target(bundle["md"], int(task["innings"]))
        fields = json.loads(task["fields_json"])
        sc = V.score_cells(gold, parsed, fields)
        scoring_ms = round((time.time() - t_score) * 1000, 1)
        now = V.now_iso()
        con.execute("INSERT OR REPLACE INTO results(task_key, batch_id, match, innings, model, cond, raw_output, "
                    "parsed_json, parse_ok, score_json, correct, duration_ms, request_json, response_meta_json, "
                    "created_at, error, scoring_version, attempt_id, model_digest, decode_json, input_version, "
                    "prompt_version, legacy_task_key, load_ms, inference_ms, scoring_ms) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (task["task_key"], task["batch_id"], task["match"], int(task["innings"]), task["model"],
                     task["cond"], gen["raw"], json.dumps(parsed, ensure_ascii=False) if parsed is not None else None,
                     int(parse_ok), json.dumps(sc, ensure_ascii=False), int(sc["task_correct"]),
                     gen["duration_ms"], json.dumps(gen["request"], ensure_ascii=False),
                     json.dumps(meta, ensure_ascii=False), now, None, v2.SCORING_VERSION, attempt_id,
                     ident["model_digest"], ident["decode_json"], ident["input_version"], ident["prompt_version"],
                     task["task_key"], load_ms, inference_ms, scoring_ms))
        v2.attempt_set(con, attempt_id, "persisted", response_at=now, persisted_at=now,
                       duration_ms=gen["duration_ms"], load_ms=load_ms, inference_ms=inference_ms, scoring_ms=scoring_ms,
                       request_json=json.dumps(gen["request"], ensure_ascii=False),
                       response_meta_json=json.dumps(meta, ensure_ascii=False))
        con.execute("UPDATE tasks SET status='done', error=NULL, updated_at=? WHERE task_key=?",
                    (now, task["task_key"]))
        v2.attempt_set(con, attempt_id, "accepted", accepted_at=now)
        con.commit()
        append_row(task["batch_id"], {
            "phase": "workflow_v2", "batch_id": task["batch_id"], "task_key": task["task_key"],
            "attempt_id": attempt_id, "match": task["match"], "innings": int(task["innings"]),
            "model": task["model"], "cond": task["cond"], "field_scope": task["field_scope"],
            "model_digest": ident["model_digest"], "decode": json.loads(ident["decode_json"]),
            "input_version": ident["input_version"], "prompt_version": ident["prompt_version"],
            "replicate_id": ident["replicate_id"], "text_sha256": task["text_sha"],
            "prompt_sha256": task["prompt_sha"], "raw_output": gen["raw"], "parsed": parsed,
            "parse_ok": parse_ok, "score": sc, "done_reason": meta.get("done_reason"),
            "eval_count": meta.get("eval_count"), "prompt_eval_count": meta.get("prompt_eval_count"),
            "duration_ms": gen["duration_ms"], "load_ms": load_ms, "inference_ms": inference_ms,
            "scoring_ms": scoring_ms, "attempts": gen["attempts"], "created_at": now,
        })
        V.event("task_done", {"task_key": task["task_key"], "attempt_id": attempt_id, "parse_ok": parse_ok,
                              "correct": sc["task_correct"], "cells": str(sc["correct"]) + "/" + str(sc["total"]),
                              "duration_ms": gen["duration_ms"], "load_ms": load_ms,
                              "inference_ms": inference_ms, "scoring_ms": scoring_ms}, con)
    except Exception as e:
        try:
            err = type(e).__name__ + ": " + str(e)
            v2.attempt_set(con, attempt_id, "uncertain" if sent else "failed", error=err[:800],
                           uncertain=1 if sent else 0,
                           notes="exception after send; server-side state unknown" if sent else "exception before send")
            con.execute("UPDATE tasks SET status='failed', error=?, updated_at=? WHERE task_key=?",
                        (err[:800], V.now_iso(), task["task_key"]))
            con.commit()
            V.event("task_exception", {"task_key": task["task_key"], "attempt_id": attempt_id, "error": err[:400]}, con)
        except Exception:
            pass
    finally:
        stop_event.set()
        hb.join(timeout=1.0)
        con.close()


def main() -> int:
    V.ensure_dirs()
    con = V.init_db()
    pid = os.getpid()
    prev = int(V.meta_get(con, "worker_pid", "0") or 0)
    if prev and prev != pid and V.pid_alive(prev):
        V.event("worker_refused_duplicate", {"previous": prev, "self": pid}, con)
        con.close()
        return 0
    V.meta_set(con, "worker_pid", pid)
    V.meta_set(con, "worker_started_at", V.now_iso())
    V.meta_set(con, "worker_heartbeat_at", V.now_iso())
    con.commit()
    V.event("worker_started", {"pid": pid, "code_version": "v2"}, con)
    beat()
    while True:
        con = V.connect()
        try:
            if V.meta_get(con, "stop_requested", "0") == "1":
                break
            if V.meta_get(con, "paused", "0") == "1":
                beat(con)
                con.close()
                time.sleep(2)
                continue
            task = claim(con, pid)
        except Exception as e:
            V.event("worker_claim_error", {"error": type(e).__name__ + ": " + str(e)}, con)
            task = None
        finally:
            try:
                con.close()
            except Exception:
                pass
        if task is None:
            beat()
            time.sleep(2)
            continue
        beat()
        V.event("task_claimed", {"task_key": task["task_key"], "attempt_id": task["attempt_id"],
                                 "batch": task["batch_id"], "model": task["model"], "cond": task["cond"],
                                 "attempt": task["attempts"]})
        process(task)
    V.event("worker_stopped", {"pid": pid})
    return 0


if __name__ == "__main__":
    if "--once" in sys.argv:
        V.ensure_dirs()
        c = V.init_db()
        pid = os.getpid()
        t = claim(c, pid)
        c.close()
        if t:
            process(t)
        sys.exit(0)
    sys.exit(main())
