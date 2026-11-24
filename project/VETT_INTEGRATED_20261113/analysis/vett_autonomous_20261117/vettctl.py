
"""Control CLI: start, status, pause, resume, stop, snapshot, report, coverage."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

import vettlib as V
import v2
import planner
import reporting


def sup_pid() -> int:
    p = V.STATE / "supervisor.pid"
    if p.exists():
        try:
            return int(p.read_text(encoding="utf-8").strip())
        except Exception:
            pass
    con = V.init_db()
    try:
        return int(V.meta_get(con, "supervisor_pid", "0") or 0)
    finally:
        con.close()


def _print(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def cmd_start(args) -> int:
    con = V.init_db()
    pid = sup_pid()
    if pid and V.pid_alive(pid):
        _print({"ok": False, "error": "already_running", "supervisor_pid": pid})
        return 1
    ready = V.readiness()
    if not ready["ok"]:
        _print({"ok": False, "error": "ollama_not_ready", "ready": ready})
        return 2
    V.meta_set(con, "stop_requested", "0")
    V.meta_set(con, "paused", "0")
    V.meta_set(con, "state", "starting")
    V.meta_set(con, "stop_reason", "")
    if not V.meta_get(con, "run_started_at", ""):
        V.meta_set(con, "run_started_at", V.now_iso())
    old_sup = int(V.meta_get(con, "supervisor_pid", "0") or 0)
    if old_sup and not V.pid_alive(old_sup):
        V.event("stale_supervisor_detected", {"pid": old_sup, "state_before": V.meta_get(con, "state", "")}, con)
    V.meta_set(con, "segment_started_at", V.now_iso())
    V.event("segment_started", {"at": V.now_iso(), "note": "fresh continuous segment"}, con)
    V.meta_set(con, "planning_mode", V.meta_get(con, "planning_mode", "rule_template"))
    con.commit()
    V.event("start_requested", {"ready": ready["digests"], "foreground": bool(args.foreground)}, con)
    con.close()
    if args.foreground:
        import supervisor
        return supervisor.main()
    log = open(V.LOGS / "supervisor.log", "ab", buffering=0)
    flags = 0x00000008 | 0x00000200 | 0x01000000
    cmd = [str(V.PYTHON), str(V.WF / "supervisor.py")]
    try:
        proc = subprocess.Popen(cmd, cwd=str(V.WF), stdin=subprocess.DEVNULL, stdout=log,
                                stderr=subprocess.STDOUT, creationflags=flags, close_fds=True)
    except OSError:
        flags = 0x00000008 | 0x00000200
        proc = subprocess.Popen(cmd, cwd=str(V.WF), stdin=subprocess.DEVNULL, stdout=log,
                                stderr=subprocess.STDOUT, creationflags=flags, close_fds=True)
    for _ in range(40):
        time.sleep(0.25)
        if V.pid_alive(proc.pid) and (V.STATE / "supervisor.heartbeat").exists():
            break
    alive = V.pid_alive(proc.pid)
    con = V.init_db()
    s = reporting.status_dict(con)
    _print({"ok": alive, "supervisor_pid": proc.pid, "detached": True,
            "log": str(V.LOGS / "supervisor.log"), "state": s["state"],
            "worker_pid": s["worker"]["pid"], "queue": s["queue"],
            "external_api_calls": s["external_api_calls"]})
    con.close()
    return 0 if alive else 3


def cmd_status(args) -> int:
    con = V.init_db()
    s = reporting.status_dict(con)
    if args.md:
        print(reporting.render_status_md(s))
    else:
        _print(s)
    con.close()
    return 0


def cmd_pause(args) -> int:
    con = V.init_db()
    V.meta_set(con, "paused", "1")
    V.meta_set(con, "state", "paused")
    con.commit()
    V.event("paused_by_user", {}, con)
    _print({"ok": True, "paused": True})
    con.close()
    return 0


def cmd_resume(args) -> int:
    con = V.init_db()
    pid = int(V.meta_get(con, "supervisor_pid", "0") or 0)
    if not V.pid_alive(pid):
        _print({"ok": False, "error": "supervisor_not_running", "supervisor_pid": pid})
        con.close()
        return 1
    V.meta_set(con, "paused", "0")
    V.meta_set(con, "stop_requested", "0")
    V.meta_set(con, "state", "running")
    con.commit()
    V.event("resumed_by_user", {}, con)
    _print({"ok": True, "paused": False, "supervisor_pid": pid})
    con.close()
    return 0


def cmd_stop(args) -> int:
    con = V.init_db()
    V.meta_set(con, "stop_requested", "1")
    V.meta_set(con, "state", "stopping")
    con.commit()
    spid = int(V.meta_get(con, "supervisor_pid", "0") or 0)
    wpid = int(V.meta_get(con, "worker_pid", "0") or 0)
    if spid:
        V.kill_tree(spid)
    if wpid:
        V.kill_tree(wpid)
    for _ in range(40):
        if not V.pid_alive(spid) and not V.pid_alive(wpid):
            break
        time.sleep(0.25)
    for row in con.execute("SELECT task_key FROM tasks WHERE status='claimed'").fetchall():
        v2.mark_uncertain(con, row["task_key"], "user stop before persistence; server-side execution unknown")
    cur = con.execute("UPDATE tasks SET status='queued', claimed_by=NULL, claimed_at=NULL, "
                      "recoveries=recoveries+1, updated_at=? WHERE status='claimed'", (V.now_iso(),))
    con.commit()
    V.meta_set(con, "state", "stopped")
    V.meta_set(con, "stop_reason", "user_stop")
    V.meta_set(con, "supervisor_pid", "")
    V.meta_set(con, "worker_pid", "")
    V.meta_set(con, "stop_requested", "0")
    con.commit()
    V.event("stopped_by_user", {"supervisor_pid": spid, "worker_pid": wpid,
                                "requeued_claimed": cur.rowcount, "stop_reason": "user_stop"}, con)
    try:
        (V.STATE / "supervisor.pid").unlink()
    except Exception:
        pass
    s = reporting.status_dict(con)
    _print({"ok": True, "stopped": True, "supervisor_alive": s["supervisor"]["alive"],
            "worker_alive": s["worker"]["alive"], "requeued_claimed": cur.rowcount,
            "queue": s["queue"]})
    con.close()
    return 0


def cmd_snapshot(args) -> int:
    con = V.init_db()
    path = reporting.write_snapshot(con)
    _print({"ok": True, "snapshot": path})
    con.close()
    return 0


def cmd_tick(args) -> int:
    con = V.init_db()
    s = reporting.write_status(con)
    _print({"ok": True, "status": str(V.REPORTS / "STATUS.json"), "ts": s["ts"]})
    con.close()
    return 0


def cmd_coverage(args) -> int:
    con = V.init_db()
    data = reporting.coverage_audit(con, args.reason or "manual audit")
    _print(data)
    con.close()
    return 0


def cmd_report(args) -> int:
    con = V.init_db()
    batches = con.execute("SELECT * FROM batches ORDER BY seq").fetchall()
    decisions = con.execute("SELECT * FROM decisions ORDER BY id").fetchall()
    next_tasks = con.execute("SELECT batch_id, match, innings, model, cond, field_scope FROM tasks "
                             "WHERE status='queued' ORDER BY batch_id, rowid LIMIT 30").fetchall()
    out = {"batches": [], "decisions": [], "next_tasks": [dict(r) for r in next_tasks],
           "external_api_calls": int(V.meta_get(con, "external_api_calls", "0"))}
    for b in batches:
        sc = json.loads(b["score_json"] or "{}")
        out["batches"].append({"batch_id": b["batch_id"], "template": b["template"], "status": b["status"],
                               "accuracy": b["accuracy"], "cells": [sc.get("cells_correct"), sc.get("cells_total")],
                               "raw_path": sc.get("raw_path"), "hypothesis": b["hypothesis"]})
    for d in decisions:
        out["decisions"].append({"batch": d["batch_id"], "rule": d["rule_id"], "action": d["action"],
                                 "next": d["next_batch_id"], "rationale": d["rationale"]})
    _print(out)
    con.close()
    return 0


def cmd_rescore(args) -> int:
    import scorer
    con = V.init_db()
    out = []
    for b in con.execute("SELECT batch_id FROM batches WHERE status='scored' ORDER BY seq").fetchall():
        try:
            r = scorer.score_batch(con, b["batch_id"])
            con.execute("UPDATE results SET scoring_version='score-v1-offline' WHERE batch_id=?", (b["batch_id"],))
            con.execute("UPDATE batches SET scoring_version='score-v1-offline' WHERE batch_id=?", (b["batch_id"],))
            con.commit()
            out.append({"batch_id": b["batch_id"], "accuracy": r.get("accuracy"), "cells": r.get("cells")})
        except Exception as e:
            out.append({"batch_id": b["batch_id"], "error": type(e).__name__ + ": " + str(e)})
    V.event("offline_rescore", {"batches": out}, con)
    _print({"ok": True, "rescored": out, "note": "no model calls; existing raw outputs only"})
    con.close()
    return 0


def cmd_reset(args) -> int:
    if not args.yes:
        _print({"ok": False, "error": "pass --yes to reset state"})
        return 1
    pid = sup_pid()
    if pid and V.pid_alive(pid):
        _print({"ok": False, "error": "supervisor_running", "pid": pid})
        return 1
    con = V.init_db()
    con.close()
    errors = []
    for p in (V.DB_PATH, V.STATE / (V.DB_PATH.name + "-wal"), V.STATE / (V.DB_PATH.name + "-shm")):
        try:
            if p.exists():
                p.unlink()
        except Exception as e:
            errors.append(str(p) + ": " + type(e).__name__)
    if V.DB_PATH.exists():
        _print({"ok": False, "error": "db_still_present", "errors": errors})
        return 1
    for folder in (V.BATCHES, V.RUNS, V.REPORTS):
        for p in folder.glob("*"):
            try:
                p.unlink()
            except Exception as e:
                errors.append(str(p) + ": " + type(e).__name__)
    for name in ("supervisor.pid", "worker.pid", "supervisor.heartbeat", "worker.heartbeat"):
        try:
            (V.STATE / name).unlink()
        except Exception:
            pass
    V.init_db().close()
    _print({"ok": True, "reset": True, "db_exists": V.DB_PATH.exists(), "errors": errors})
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="VETT autonomous workflow control")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("--foreground", action="store_true")
    p.set_defaults(fn=cmd_start)
    p = sub.add_parser("status")
    p.add_argument("--md", action="store_true")
    p.set_defaults(fn=cmd_status)
    sub.add_parser("pause").set_defaults(fn=cmd_pause)
    sub.add_parser("resume").set_defaults(fn=cmd_resume)
    sub.add_parser("stop").set_defaults(fn=cmd_stop)
    sub.add_parser("snapshot").set_defaults(fn=cmd_snapshot)
    sub.add_parser("tick").set_defaults(fn=cmd_tick)
    p = sub.add_parser("coverage")
    p.add_argument("--reason", default="")
    p.set_defaults(fn=cmd_coverage)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    sub.add_parser("rescore").set_defaults(fn=cmd_rescore)
    p = sub.add_parser("reset")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(fn=cmd_reset)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
