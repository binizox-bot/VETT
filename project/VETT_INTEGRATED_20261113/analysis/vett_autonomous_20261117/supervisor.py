
"""Supervisor: owns the single GPU worker, advances the batch loop, writes timers."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import urllib.request
import sys
import time

import vettlib as V
import v2
import planner
import reporting
import scorer

STOP = {"flag": False}
_WORKER = {"proc": None, "log": None}


def _keep_awake() -> None:
    """Prevent Windows idle sleep while this supervisor is alive."""
    try:
        import ctypes
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        while not STOP["flag"]:
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
            except Exception:
                pass
            time.sleep(60)
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        except Exception:
            pass
    except Exception:
        pass


_OLLAMA = {"checked": 0.0}


def ensure_ollama(con) -> None:
    now = time.time()
    if now - _OLLAMA["checked"] < 60:
        return
    _OLLAMA["checked"] = now
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3).read()
        return
    except Exception as e:
        V.event("ollama_unavailable", {"error": type(e).__name__ + ": " + str(e)}, con)
        exe = shutil.which("ollama") or r"C:\Users\PC\AppData\Local\Programs\Ollama\ollama.exe"
        try:
            log = open(V.LOGS / "ollama.log", "ab", buffering=0)
            flags = 0x00000008 | 0x00000200 | 0x01000000
            try:
                p = subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, creationflags=flags, close_fds=True)
            except OSError:
                flags = 0x00000008 | 0x00000200
                p = subprocess.Popen([exe, "serve"], stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, creationflags=flags, close_fds=True)
            V.event("ollama_restarted", {"pid": p.pid}, con)
        except Exception as e2:
            V.event("ollama_restart_failed", {"error": type(e2).__name__ + ": " + str(e2)}, con)


def _spawn_worker(con):
    log = open(V.LOGS / "worker.log", "ab", buffering=0)
    proc = subprocess.Popen([str(V.PYTHON), str(V.WF / "worker.py")], cwd=str(V.WF),
                            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            creationflags=0x00000200)
    _WORKER["proc"] = proc
    _WORKER["log"] = log
    V.meta_set(con, "worker_pid", proc.pid)
    V.meta_set(con, "worker_started_at", V.now_iso())
    V.meta_set(con, "worker_restarts", int(V.meta_get(con, "worker_restarts", "0")) + 1)
    con.commit()
    V.event("worker_spawned", {"pid": proc.pid}, con)
    return proc.pid


def ensure_worker(con) -> None:
    pid = int(V.meta_get(con, "worker_pid", "0") or 0)
    if pid and V.pid_alive(pid):
        return
    if pid:
        V.event("worker_died", {"pid": pid}, con)
    _spawn_worker(con)


def recover(con) -> int:
    rows = con.execute("SELECT * FROM tasks WHERE status='claimed'").fetchall()
    heart = v2.heartbeat_age(con)
    recovered = 0
    for r in rows:
        owner = r["claimed_by"]
        if owner and V.pid_alive(owner):
            # A long request is not a death. Only a stale independent heartbeat is.
            if heart >= 0 and heart > 300:
                V.event("worker_hung_killed", {"pid": owner, "heartbeat_age": heart,
                                               "policy": "independent_heartbeat_300s"}, con)
                V.kill_tree(owner)
            else:
                continue
        if con.execute("SELECT 1 FROM results WHERE task_key=?", (r["task_key"],)).fetchone():
            con.execute("UPDATE tasks SET status='done', error='recovered_duplicate_result', updated_at=? "
                        "WHERE task_key=?", (V.now_iso(), r["task_key"]))
            V.event("recovered_with_existing_result", {"task_key": r["task_key"], "owner": owner}, con)
        else:
            v2.mark_uncertain(con, r["task_key"],
                              "worker died before persistence; server-side execution unknown, exactly-once not claimed")
            con.execute("UPDATE tasks SET status='queued', claimed_by=NULL, claimed_at=NULL, "
                        "recoveries=recoveries+1, updated_at=? WHERE task_key=?",
                        (V.now_iso(), r["task_key"]))
            recovered += 1
            V.event("task_recovered", {"task_key": r["task_key"], "previous_owner": owner,
                                       "recoveries": int(r["recoveries"] or 0) + 1,
                                       "attempts": int(r["attempts"] or 0),
                                       "uncertain_server_state": True}, con)
    if recovered:
        con.commit()
    return recovered


def advance(con) -> None:
    running = con.execute("SELECT * FROM batches WHERE status='running' ORDER BY seq LIMIT 1").fetchone()
    if running:
        counts = V.queue_counts(con)
        # count only this batch
        rows = con.execute("SELECT status, COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY status",
                           (running["batch_id"],)).fetchall()
        by = {r["status"]: r["n"] for r in rows}
        if by.get("queued", 0) + by.get("claimed", 0) > 0:
            return
        nres = con.execute("SELECT COUNT(*) n FROM results WHERE batch_id=?", (running["batch_id"],)).fetchone()["n"]
        if nres == 0:
            con.execute("UPDATE batches SET status='failed', updated_at=? WHERE batch_id=?",
                        (V.now_iso(), running["batch_id"]))
            con.commit()
            V.event("batch_failed_no_results", {"batch_id": running["batch_id"]}, con)
            return
        try:
            scorer.score_batch(con, running["batch_id"])
        except Exception as e:
            con.execute("UPDATE batches SET status='failed', updated_at=? WHERE batch_id=?",
                        (V.now_iso(), running["batch_id"]))
            con.commit()
            V.event("batch_score_failed", {"batch_id": running["batch_id"],
                                           "error": type(e).__name__ + ": " + str(e)}, con)
            _plan_next(con)
            return
        reporting.write_status(con)
        if V.meta_get(con, "stop_requested", "0") == "1":
            return
        _plan_next(con)
        return
    if V.meta_get(con, "exhausted", "0") == "1":
        # Keep the process alive and re-check builders periodically; exhaustion is not a stop condition.
        if _due(con, "last_plan_attempt_at", 900):
            V.meta_set(con, "last_plan_attempt_at", V.now_iso())
            con.commit()
            _plan_next(con)
        return
    if con.execute("SELECT 1 FROM batches WHERE status IN ('running','frozen')").fetchone():
        return
    _plan_next(con)


def _plan_next(con) -> None:
    if con.execute("SELECT 1 FROM batches WHERE status IN ('running','frozen')").fetchone():
        return
    try:
        r = planner.plan_and_freeze(con)
    except Exception as e:
        V.event("planner_error", {"error": type(e).__name__ + ": " + str(e)}, con)
        (V.LOGS / "supervisor_errors.log").open("a", encoding="utf-8").write(
            V.now_iso() + " planner_error " + type(e).__name__ + ": " + str(e) + "\n")
        return
    if r.get("ok"):
        V.meta_set(con, "exhausted", "0")
        con.commit()
        reporting.write_status(con)
        return
    cov = reporting.coverage_audit(con, r.get("reason", "no_eligible_tasks"))
    V.meta_set(con, "exhausted", "1")
    V.meta_set(con, "state", "idle_no_valid_tasks")
    con.commit()
    V.event("exhausted", {"reason": r.get("reason"), "coverage": cov.get("unbuilt_directions")}, con)


def _due(con, key: str, interval: int) -> bool:
    ts = V.meta_get(con, key, "")
    if not ts:
        return True
    try:
        from datetime import datetime
        return (time.time() - datetime.fromisoformat(ts).timestamp()) >= interval
    except Exception:
        return True


def main() -> int:
    V.ensure_dirs()
    con = V.init_db()
    pid = os.getpid()
    old = int(V.meta_get(con, "supervisor_pid", "0") or 0)
    if old and old != pid and V.pid_alive(old):
        print("supervisor already running:", old)
        con.close()
        return 1
    (V.STATE / "supervisor.pid").write_text(str(pid), encoding="utf-8")
    V.meta_set(con, "supervisor_pid", pid)
    V.meta_set(con, "supervisor_started_at", V.now_iso())
    if not V.meta_get(con, "run_started_at", ""):
        V.meta_set(con, "run_started_at", V.now_iso())
    V.meta_set(con, "long_run_target_hours", "8")
    if V.meta_get(con, "stop_requested", "0") == "1":
        V.meta_set(con, "stop_requested", "0")
    if V.meta_get(con, "paused", "0") == "1":
        V.meta_set(con, "state", "paused")
    else:
        V.meta_set(con, "state", "running")
    if not V.meta_get(con, "last_snapshot_at", ""):
        V.meta_set(con, "last_snapshot_at", V.now_iso())
    con.commit()
    V.event("supervisor_started", {"pid": pid}, con)

    def _stop(signum, frame):
        STOP["flag"] = True

    try:
        signal.signal(signal.SIGINT, _stop)
        signal.signal(signal.SIGTERM, _stop)
    except Exception:
        pass

    import threading
    threading.Thread(target=_keep_awake, daemon=True, name="keep-awake").start()
    V.event("keep_awake_started", {"policy": "SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED)"}, con)
    timers = V.CONFIG["timers"]
    try:
        while not STOP["flag"]:
            con = V.connect()
            try:
                if V.meta_get(con, "stop_requested", "0") == "1":
                    V.meta_set(con, "state", "stopping")
                    con.commit()
                    break
                if V.meta_get(con, "paused", "0") == "1":
                    V.meta_set(con, "state", "paused")
                    con.commit()
                else:
                    recover(con)
                    ensure_ollama(con)
                    ensure_worker(con)
                    advance(con)
                    if V.meta_get(con, "paused", "0") != "1" and V.meta_get(con, "exhausted", "0") != "1":
                        V.meta_set(con, "state", "running")
                        con.commit()
                if _due(con, "last_status_at", int(timers["status_interval_seconds"])):
                    reporting.write_status(con)
                if _due(con, "last_snapshot_at", int(timers["snapshot_interval_seconds"])):
                    reporting.write_snapshot(con)
                if _due(con, "last_hourly_report_at", 3600):
                    v2.write_hourly(con)
                from datetime import datetime as _dt
                _today = _dt.now().strftime("%Y%m%d")
                if _dt.now().hour == 8 and V.meta_get(con, "last_stage_report_date", "") != _today:
                    v2.write_stage(con)
            except Exception as e:
                V.event("supervisor_error", {"error": type(e).__name__ + ": " + str(e)}, con)
                with (V.LOGS / "supervisor_errors.log").open("a", encoding="utf-8") as fh:
                    fh.write(V.now_iso() + " supervisor_error " + type(e).__name__ + ": " + str(e) + "\n")
            finally:
                try:
                    con.close()
                except Exception:
                    pass
            try:
                (V.STATE / "supervisor.heartbeat").write_text(V.now_iso(), encoding="utf-8")
            except Exception:
                pass
            time.sleep(int(timers["supervisor_poll_seconds"]))
    finally:
        con = V.connect()
        wpid = V.meta_get(con, "worker_pid", "0")
        if wpid and V.pid_alive(wpid):
            V.kill_tree(wpid)
        V.meta_set(con, "worker_pid", "")
        V.meta_set(con, "supervisor_pid", "")
        V.meta_set(con, "state", "stopped")
        if not V.meta_get(con, "stop_reason", ""):
            V.meta_set(con, "stop_reason", "user_stop")
        con.commit()
        V.event("supervisor_stopped", {"pid": pid, "stopped": True}, con)
        try:
            (V.STATE / "supervisor.pid").unlink()
        except Exception:
            pass
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
