
"""Status, snapshots, and coverage reporting."""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import vettlib as V


def _age_seconds(ts: str) -> float:
    if not ts:
        return -1.0
    try:
        return round(time.time() - datetime.fromisoformat(ts).timestamp(), 1)
    except Exception:
        return -1.0


def _heartbeat_age() -> float:
    p = V.STATE / "worker.heartbeat"
    if not p.exists():
        return -1.0
    return round(time.time() - p.stat().st_mtime, 1)


def status_dict(con) -> dict:
    sup_pid = V.meta_get(con, "supervisor_pid", "")
    wk_pid = V.meta_get(con, "worker_pid", "")
    wf = V.meta_get(con, "state", "unknown")
    batches = []
    for b in con.execute("SELECT * FROM batches ORDER BY seq").fetchall():
        sc = json.loads(b["score_json"] or "{}")
        batches.append({"batch_id": b["batch_id"], "seq": b["seq"], "template": b["template"],
                        "status": b["status"], "accuracy": b["accuracy"],
                        "cells": (str(sc.get("cells_correct")) + "/" + str(sc.get("cells_total"))) if sc else None,
                        "raw_path": sc.get("raw_path"),
                        "created_at": b["created_at"]})
    running = con.execute("SELECT * FROM batches WHERE status='running' ORDER BY seq LIMIT 1").fetchone()
    progress = None
    interrupted = None
    if running:
        rows = con.execute("SELECT status, COUNT(*) n FROM tasks WHERE batch_id=? GROUP BY status",
                           (running["batch_id"],)).fetchall()
        item = {"batch_id": running["batch_id"], "template": running["template"],
                "tasks": {r["status"]: r["n"] for r in rows}}
        if wf in ("running", "paused", "stopping", "starting"):
            progress = item
        else:
            interrupted = dict(item, note="workflow is " + wf + "; batch is interrupted, not inferring")
    task_state = V.queue_counts(con)
    queued = con.execute("SELECT batch_id, COUNT(*) n FROM tasks WHERE status='queued' GROUP BY batch_id").fetchall()
    next_tasks = con.execute("SELECT task_key, batch_id, match, innings, model, cond, field_scope "
                             "FROM tasks WHERE status='queued' ORDER BY batch_id, rowid LIMIT 12").fetchall()
    events = con.execute("SELECT ts, kind, payload FROM events ORDER BY id DESC LIMIT 12").fetchall()
    last_status = V.meta_get(con, "last_status_at", "")
    last_snap = V.meta_get(con, "last_snapshot_at", "")
    timers = V.CONFIG["timers"]
    try:
        import v2
        run = v2.run_stats(con)
        hb = v2.heartbeat_age(con)
        schema_version = V.meta_get(con, "schema_version", "")
    except Exception:
        run = {}
        hb = _heartbeat_age()
        schema_version = ""
    batch_state = "running" if progress else ("interrupted" if interrupted else
                  ("frozen" if con.execute("SELECT 1 FROM batches WHERE status='frozen'").fetchone() else "idle"))
    return {
        "ts": V.now_iso(),
        "workflow_state": wf,
        "batch_state": batch_state,
        "task_state": task_state,
        "state": wf,
        "paused": V.meta_get(con, "paused", "0") == "1",
        "stop_requested": V.meta_get(con, "stop_requested", "0") == "1",
        "stop_reason": V.meta_get(con, "stop_reason", ""),
        "exhausted": V.meta_get(con, "exhausted", "0") == "1",
        "schema_version": schema_version,
        "planning_mode": V.meta_get(con, "planning_mode", "rule_template"),
        "external_api_calls": int(V.meta_get(con, "external_api_calls", "0")),
        "method_version": V.meta_get(con, "method_version", ""),
        "run": run,
        "supervisor": {"pid": int(sup_pid) if sup_pid else None, "alive": V.pid_alive(sup_pid),
                       "started_at": V.meta_get(con, "supervisor_started_at", "")},
        "worker": {"pid": int(wk_pid) if wk_pid else None, "alive": V.pid_alive(wk_pid),
                   "heartbeat_age_seconds": hb,
                   "restarts": int(V.meta_get(con, "worker_restarts", "0")),
                   "started_at": V.meta_get(con, "worker_started_at", "")},
        "queue": task_state,
        "queued_by_batch": {r["batch_id"]: r["n"] for r in queued},
        "running_batch": progress,
        "interrupted_batch": interrupted,
        "batches": batches,
        "next_tasks": [dict(r) for r in next_tasks],
        "timers": {
            "status_interval_seconds": timers["status_interval_seconds"],
            "snapshot_interval_seconds": timers["snapshot_interval_seconds"],
            "last_status_at": last_status,
            "last_snapshot_at": last_snap,
            "last_hourly_report_at": V.meta_get(con, "last_hourly_report_at", ""),
            "last_stage_report_date": V.meta_get(con, "last_stage_report_date", ""),
            "status_age_seconds": _age_seconds(last_status),
            "snapshot_age_seconds": _age_seconds(last_snap),
        },
        "recent_events": [{"ts": e["ts"], "kind": e["kind"], "payload": json.loads(e["payload"] or "{}")}
                          for e in events],
    }


def render_status_md(s: dict) -> str:
    run = s.get("run") or {}
    lines = ["# VETT workflow status", "",
             "- time: " + s["ts"],
             "- workflow state: " + s["workflow_state"] + (" (paused)" if s["paused"] else "") +
             (" stop_reason=" + s["stop_reason"] if s.get("stop_reason") else ""),
             "- batch state: " + s["batch_state"],
             "- task state: " + json.dumps(s["task_state"], ensure_ascii=False),
             "- schema: " + str(s.get("schema_version")) + "; planning: " + str(s.get("planning_mode")),
             "- external API calls: " + str(s["external_api_calls"]),
             "- supervisor: " + str(s["supervisor"]["pid"]) + " alive=" + str(s["supervisor"]["alive"]),
             "- worker: " + str(s["worker"]["pid"]) + " alive=" + str(s["worker"]["alive"]) +
             " heartbeat=" + str(s["worker"]["heartbeat_age_seconds"]) + "s restarts=" + str(s["worker"]["restarts"]),
             "- queue: " + json.dumps(s["queue"]), ""]
    if run:
        lines += ["- run elapsed: " + str(run.get("elapsed_hours")) + " h",
                  "- load/inference/scoring ms: " + str(run.get("load_ms")) + " / " +
                  str(run.get("inference_ms")) + " / " + str(run.get("scoring_ms")),
                  "- plan/wait ms: " + str(run.get("plan_ms")) + " / " + str(run.get("waiting_ms_est")),
                  "- attempts: " + str(run.get("attempts")) + "; uncertain: " + str(run.get("uncertain_attempts")), ""]
    if s.get("running_batch"):
        lines.append("- running batch: " + s["running_batch"]["batch_id"] + " " + s["running_batch"]["template"] +
                     " " + json.dumps(s["running_batch"]["tasks"]))
        lines.append("")
    if s.get("interrupted_batch"):
        lines.append("- interrupted batch: " + s["interrupted_batch"]["batch_id"] + " " +
                     s["interrupted_batch"]["template"] + " " + json.dumps(s["interrupted_batch"]["tasks"]) +
                     " (" + s["interrupted_batch"]["note"] + ")")
        lines.append("")
    lines += ["## Batches", "", "| batch | template | status | accuracy | cells | raw |", "|---|---|---|---:|---|---|"]
    for b in s["batches"]:
        lines.append("| " + b["batch_id"] + " | " + b["template"] + " | " + str(b["status"]) + " | " +
                     str(b["accuracy"]) + " | " + str(b["cells"]) + " | " + str(b["raw_path"]) + " |")
    lines += ["", "## Next queued tasks", ""]
    if s["next_tasks"]:
        for t in s["next_tasks"]:
            lines.append("- " + t["batch_id"] + " " + t["match"] + " inn" + str(t["innings"]) + " " +
                         t["cond"] + " " + t["model"] + " " + t["field_scope"])
    else:
        lines.append("- none")
    lines += ["", "## Recent events", ""]
    for e in s["recent_events"]:
        lines.append("- " + e["ts"] + " " + e["kind"] + " " + json.dumps(e["payload"], ensure_ascii=False)[:220])
    return "\n".join(lines) + "\n"


def write_status(con) -> dict:
    s = status_dict(con)
    (V.REPORTS / "STATUS.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    (V.REPORTS / "STATUS.md").write_text(render_status_md(s), encoding="utf-8")
    V.meta_set(con, "last_status_at", V.now_iso())
    con.commit()
    V.event("status_written", {"batches": len(s["batches"]), "queue": s["queue"]}, con)
    return s


def write_snapshot(con) -> str:
    s = status_dict(con)
    mem_path = V.REPORTS / "RESEARCH_MEMORY.json"
    mem = json.loads(mem_path.read_text(encoding="utf-8")) if mem_path.exists() else {}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lines = ["# VETT snapshot " + stamp, "", "## Status", "", render_status_md(s), "## Research memory", ""]
    for f in mem.get("findings", []):
        lines.append("- " + f["batch_id"] + " " + f["template"] + " accuracy=" + str(f["accuracy"]) +
                     " raw=" + str(f["raw_path"]))
    lines += ["", "## Decisions", ""]
    for d in mem.get("decisions", []):
        lines.append("- " + str(d["batch_id"]) + " " + str(d["rule_id"]) + " -> " + str(d["action"]) +
                     ": " + str(d["rationale"]))
    lines += ["", "## External API", "", "- " + str(s["external_api_calls"]) + " calls"]
    path = V.REPORTS / ("SNAPSHOT_" + stamp + ".md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (V.REPORTS / "SNAPSHOT_LATEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    V.meta_set(con, "last_snapshot_at", V.now_iso())
    con.commit()
    V.event("snapshot_written", {"path": str(path)}, con)
    return str(path)


def coverage_audit(con, reason: str) -> dict:
    batches = [dict(r) for r in con.execute("SELECT * FROM batches ORDER BY seq").fetchall()]
    scored = [b for b in batches if b["status"] == "scored"]
    hard = V.CONFIG["pools"]["hard"]
    used = {(r["match"], r["innings"]) for r in con.execute("SELECT DISTINCT match, innings FROM tasks").fetchall()}
    unused_hard = [p for p in hard if (p["match"], p["innings"]) not in used]
    cov = V.CONFIG["coverage_baseline"]
    data = {
        "generated_at": V.now_iso(), "reason": reason,
        "matches_total": V.CONFIG["data"]["matches"],
        "parsed_positions": V.CONFIG["data"]["parsed_positions"],
        "u_full": {"responses": cov["u_responses"], "json_scorable": cov["u_json_scorable"],
                   "missing_positions": cov["u_missing_positions"]},
        "evidence_index": {"entries": cov["evidence_entries"], "human_confirmed": cov["human_confirmed"]},
        "heldout_roots": cov["heldout_roots"],
        "batches_run": len(batches), "batches_scored": len(scored),
        "unused_hard_positions": len(unused_hard),
        "unbuilt_directions": ["C missing-evidence matrix", "D R28 low-old-value direction",
                               "E temperature/seed randomness", "F held-out full-table validation"],
        "external_api_calls": int(V.meta_get(con, "external_api_calls", "0")),
    }
    lines = ["# Coverage gap", "", "- generated: " + data["generated_at"], "- reason: " + reason, "",
             "## Covered", "",
             "- batches run: " + str(len(batches)) + ", scored: " + str(len(scored)),
             "- parsed positions available: " + str(data["parsed_positions"]),
             "- U full responses: " + str(cov["u_responses"]) + " (JSON-scorable " + str(cov["u_json_scorable"]) + ")",
             "- evidence index entries: " + str(cov["evidence_entries"]) + ", human confirmed: " + str(cov["human_confirmed"]),
             "", "## Not yet covered", ""]
    for d in data["unbuilt_directions"]:
        lines.append("- " + d)
    lines += ["- held-out roots reserved: " + str(cov["heldout_roots"]),
              "- unused hard positions: " + str(len(unused_hard)), "",
              "## Conclusion", "",
              "Exhaustion is claimed only if no builder can produce an eligible task. Otherwise the supervisor continues with the next eligible template."]
    (V.REPORTS / "COVERAGE_GAP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (V.REPORTS / "COVERAGE_GAP.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    V.event("coverage_audit", data, con)
    return data
