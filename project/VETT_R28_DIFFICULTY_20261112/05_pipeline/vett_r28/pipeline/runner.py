"""Pipeline runner: stage graph, gate loop, bounded repair, resume, exit codes.

Exit codes
----------
0  OK (all executed gates PASS; non-blocking degradations recorded)
2  usage/config error
3  blocking gate failure (no repair path / stage error)
4  frozen input violation (R26.15, protected paths, prereg/contract/protocol)
5  BUDGET_STOP
6  ESCALATED (still FAIL after 2 repairs)
7  HUMAN_GATE_REQUIRED
"""

from __future__ import annotations

import os
import pathlib
import tempfile
import time
from datetime import datetime, timezone
from typing import Any

from .budget import BudgetLedger
from .cache import ContentAddressedCache
from .config import Config
from .context import PipelineContext
from .degrade import DegradationManager
from .errors import (BudgetStop, CloudForbidden, ConfigError, Escalated, FrozenViolation,
                     GateFailure, HumanGateRequired, LocalFirstViolation, PipelineError,
                     UsageError)
from .events import read_jsonl
from .gates import (PRE_STAGE_GATES, REGISTRY, STAGE_GATES, registry_snapshot,
                    validate_registry)
from .human import HumanGate
from .repairs import REPAIRS, registry_snapshot as repair_snapshot, repair_ids
from .stages import ALL_STAGES, PUBLISH_STAGE, STAGE_FUNCS, VERSION

MAX_REPAIRS = 2  # hard contract: initial FAIL + two repairs = three attempts


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class RunResult:
    def __init__(self, *, status: str, exit_code: int, run_dir: pathlib.Path,
                 manifest: dict[str, Any] | None = None, error: str | None = None):
        self.status = status
        self.exit_code = exit_code
        self.run_dir = run_dir
        self.manifest = manifest or {}
        self.error = error

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"RunResult(status={self.status!r}, exit_code={self.exit_code}, run_dir={self.run_dir})"


def resolve_stages(requested: str) -> list[str]:
    if requested == "all":
        return list(ALL_STAGES)
    if requested == PUBLISH_STAGE:
        return list(ALL_STAGES) + [PUBLISH_STAGE]
    if requested in ALL_STAGES:
        index = ALL_STAGES.index(requested)
        return list(ALL_STAGES[: index + 1])
    raise UsageError(f"unknown stage {requested!r}; known: all, {', '.join(ALL_STAGES)}, {PUBLISH_STAGE}")


# ---------------------------------------------------------------------------
# gate execution with bounded repair
# ---------------------------------------------------------------------------
def run_gate(ctx: PipelineContext, gate_id: str) -> dict[str, Any]:
    spec = REGISTRY[gate_id]
    attempt = 0
    while True:
        result = spec.fn(ctx)
        verdict = result["verdict"]
        ctx.record_gate(gate_id, spec.stage, verdict, result["evidence"], attempt, spec.blocking)
        if verdict == "PASS":
            return result
        if not spec.blocking:
            return result
        if spec.exit_code == 4:
            raise FrozenViolation(
                f"{gate_id} failed and is a frozen-input gate (exit 4): "
                f"{result['evidence']}"
            )
        if spec.repair_id is None or attempt >= MAX_REPAIRS:
            ctx.record_gate(gate_id, spec.stage, "ESCALATED", {
                "reason": "still failing after the bounded repair rounds",
                "attempts": attempt + 1,
                "last_evidence": result["evidence"],
            }, attempt, True)
            escalation = {
                "schema": "vett-r28-pipeline-escalation/v1",
                "gate": gate_id,
                "stage": spec.stage,
                "attempts": attempt + 1,
                "max_repairs": MAX_REPAIRS,
                "last_evidence": result["evidence"],
                "action_required": "human review; no further automatic retry",
            }
            ctx.write_json("ESCALATED.json", escalation)
            ctx.exit_status = "ESCALATED"
            raise Escalated(f"{gate_id} escalated after {attempt + 1} attempts")
        repair = REPAIRS[spec.repair_id]
        repair_result = repair.fn(ctx)
        ctx.state.setdefault("repairs", []).append({
            "gate": gate_id,
            "repair_id": repair.repair_id,
            "attempt": attempt + 1,
            "ok": bool(repair_result.get("ok")),
            "action": repair_result.get("action"),
            "evidence": repair_result.get("evidence"),
        })
        attempt += 1


def _hydrate(ctx: PipelineContext, name: str) -> None:
    """Reload a skipped stage's in-memory output from its persisted artefact."""
    try:
        if name == "annotate":
            ctx.annotations = ctx.read_json("annotations.json")
        elif name == "judge":
            ctx.judged = ctx.read_json("judge.json")
        elif name == "aggregate":
            ctx.aggregated = ctx.read_json("aggregate.json")
    except FileNotFoundError:  # pragma: no cover - artefact was listed as done
        ctx.notes.append(f"resume: {name} artefact missing; stage will be recomputed")


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------
def _previous_artifact_hashes(run_dir: pathlib.Path) -> dict[str, str]:
    path = run_dir / "ARTIFACT_HASHES.json"
    if not path.is_file():
        return {}
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
        return dict(payload.get("artifacts") or {})
    except Exception:  # noqa: BLE001 - a corrupt previous manifest is simply ignored
        return {}


def _load_state(run_dir: pathlib.Path) -> dict[str, Any]:
    path = run_dir / "state.json"
    if not path.is_file():
        return {}
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def run(*, config: Config, stage: str = "all", dry_run: bool = False,
        resume: bool = False, fault: str | None = None,
        allow_human_gate: bool = False, run_id: str | None = None,
        limit_instances: int | None = None, sample_instances: int | None = None,
        verbose: bool = True) -> RunResult:
    started = time.time()
    problems = config.validate()
    if problems:
        raise ConfigError("; ".join(problems))
    if limit_instances is not None:
        config.data.setdefault("generate", {})["limit_instances"] = int(limit_instances)
    if sample_instances is not None:
        config.data.setdefault("annotation", {})["sample_instances"] = int(sample_instances)

    registry_problems = validate_registry(repair_ids())
    if registry_problems:
        raise ConfigError("; ".join(registry_problems))

    run_id = run_id or str(config.get("pipeline.default_run_id", "r28-main"))
    run_root = config.run_root()
    if dry_run:
        run_dir = run_root / "_dryrun" / run_id
    else:
        run_dir = run_root / run_id
    fallback_dir: pathlib.Path | None = None
    if fault == "disk":
        fallback_dir = pathlib.Path(tempfile.mkdtemp(prefix="vett_r28_pipeline_fallback_"))
        run_dir = fallback_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    state = _load_state(run_dir) if resume else {}
    ctx = PipelineContext(
        config=config,
        run_dir=run_dir,
        dry_run=dry_run,
        resume=resume,
        fault=fault,
        allow_human_gate=allow_human_gate,
        run_id=run_id,
        cache=ContentAddressedCache(run_dir / "cache"),
        budget=BudgetLedger(run_dir, config.budget_settings()),
        degrade=DegradationManager(run_dir),
        human=HumanGate(allow=allow_human_gate, run_dir=run_dir,
                        r26_15_root=config.r26_15_root()),
        gate_ledger=run_dir / "gate_ledger.jsonl",
        state={"stages": dict(state.get("stages") or {}),
               "repairs": list(state.get("repairs") or [])},
        previous_artifacts=_previous_artifact_hashes(run_dir),
    )
    ctx.write_json("GATE_REGISTRY.json", registry_snapshot())
    ctx.write_json("REPAIR_REGISTRY.json", repair_snapshot())
    if fallback_dir is not None:
        ctx.degrade.emit(stage="bootstrap", reason_code="DISK_UNAVAILABLE",
                         fallback="write to temporary fallback directory",
                         evidence={"fallback_run_dir": str(run_dir)}, source="pipeline")
    if fault == "cloud":
        ctx.degrade.emit(stage="bootstrap", reason_code="CLOUD_RULER_UNAVAILABLE",
                         fallback="descriptive-only; no cloud sampling", source="pipeline")

    requested = resolve_stages(stage)
    resumed: list[str] = []

    def _done(name: str) -> bool:
        entry = (ctx.state.get("stages") or {}).get(name) or {}
        return bool(resume and entry.get("status") == "done"
                    and entry.get("config_digest") == config.digest())

    resume_flags = {name: _done(name) for name in requested}
    # ``generate`` is memory-only: if a later stage will execute, the in-memory
    # dataset must exist, so regenerate instead of skipping.  No model call is
    # involved and the rebuild is deterministic.
    for index, name in enumerate(requested):
        if name == "generate" and resume_flags.get(name):
            if any(not resume_flags.get(later) for later in requested[index + 1:]):
                resume_flags[name] = False
    try:
        for name in requested:
            ctx.state["current_stage"] = name
            entry = (ctx.state.get("stages") or {}).get(name) or {}
            if resume_flags.get(name):
                resumed.append(name)
                _hydrate(ctx, name)
                for artifact_name, artifact_sha in (entry.get("artifacts") or {}).items():
                    ctx.artifacts.setdefault(artifact_name, {
                        "path": "", "bytes": 0, "sha256": artifact_sha})
                for gate_entry in (entry.get("gates") or []):
                    ctx.gate_results.append(gate_entry)
                ctx.stage_results[name] = {**entry, "resumed": True}
                ctx.log(f"stage {name}: resumed from state.json (no recompute)")
                continue
            stage_started = time.time()
            gate_start = len(ctx.gate_results)
            for gate_id in PRE_STAGE_GATES.get(name, []):
                run_gate(ctx, gate_id)
            output = STAGE_FUNCS[name](ctx)
            for gate_id in STAGE_GATES[name]:
                run_gate(ctx, gate_id)
            stage_gates = list(ctx.gate_results[gate_start:])
            elapsed = round(time.time() - stage_started, 3)
            ctx.stage_results[name] = {
                "status": "done",
                "resumed": False,
                "elapsed_s": elapsed,
                "config_digest": config.digest(),
                "output": output,
                "gates": stage_gates,
                "artifacts": {key: info["sha256"] for key, info in ctx.artifacts.items()},
            }
            ctx.state.setdefault("stages", {})[name] = ctx.stage_results[name]
            ctx.save_state()
            ctx.log(f"stage {name}: done in {elapsed}s ({len(STAGE_GATES[name])} gates)")
            if fault and fault.startswith("kill_after_"):
                target = fault[len("kill_after_"):]
                if name == target:
                    ctx.write_json("KILLED_AT.json", {
                        "schema": "vett-r28-pipeline-killed/v1",
                        "stage": name,
                        "reason": f"injected kill_after_{target} (simulated process death)",
                        "artifacts": {key: info["sha256"]
                                      for key, info in ctx.artifacts.items()},
                    })
                    ctx.save_state()
                    os._exit(9)
        ctx.exit_status = "OK"
        exit_code = 0
    except BudgetStop as exc:
        ctx.exit_status = "BUDGET_STOP"
        exit_code = exc.exit_code
        ctx.notes.append(str(exc))
    except FrozenViolation as exc:
        ctx.exit_status = "FROZEN_VIOLATION"
        exit_code = exc.exit_code
        ctx.notes.append(str(exc))
    except LocalFirstViolation as exc:
        # Routing-card violations are governance failures (exit 4), never a
        # silent per-task degradation.
        ctx.exit_status = "FROZEN_VIOLATION"
        exit_code = exc.exit_code
        ctx.notes.append(str(exc))
    except Escalated as exc:
        ctx.exit_status = "ESCALATED"
        exit_code = exc.exit_code
        ctx.notes.append(str(exc))
    except HumanGateRequired as exc:
        ctx.exit_status = "HUMAN_GATE_REQUIRED"
        exit_code = exc.exit_code
        ctx.notes.append(str(exc))
    except PipelineError as exc:
        ctx.exit_status = "ERROR"
        exit_code = exc.exit_code
        ctx.notes.append(str(exc))
    except Exception as exc:  # noqa: BLE001 - never die without a manifest
        ctx.exit_status = "ERROR"
        exit_code = 1
        ctx.notes.append(f"{type(exc).__name__}: {exc}")

    elapsed = round(time.time() - started, 3)
    manifest = {
        "schema": "vett-r28-pipeline-run-manifest/v1",
        "run_id": run_id,
        "mode": "dry_run" if dry_run else "live",
        "pipeline_version": VERSION,
        "config_digest": config.digest(),
        "stages_requested": requested,
        "resumed_stages": resumed,
        "stage_results": ctx.stage_results,
        "gate_results": ctx.gate_results,
        "repairs": ctx.state.get("repairs") or [],
        "cache": ctx.cache.stats(),
        "budget": ctx.budget.totals(),
        "degradation": ctx.degrade.summary(),
        "exit_status": ctx.exit_status,
        "exit_code": exit_code,
        "notes": ctx.notes,
        "run_dir": str(run_dir),
        "dry_run": dry_run,
        "fault": fault,
        "fallback_dir": str(fallback_dir) if fallback_dir else None,
        "started_utc": utc_now(),
        "elapsed_s": elapsed,
        "artifact_hashes": {name: info["sha256"] for name, info in ctx.artifacts.items()},
    }
    ctx.write_json("run_manifest.json", manifest)
    if verbose:
        print("=" * 78)
        print(f"[pipeline] run_id={run_id} mode={manifest['mode']} status={ctx.exit_status} "
              f"exit={exit_code} elapsed={elapsed}s")
        print(f"[pipeline] cache: {ctx.cache.stats()}")
        print(f"[pipeline] budget: {ctx.budget.totals()}")
        print(f"[pipeline] degraded events: {ctx.degrade.summary()}")
        for note in ctx.notes:
            print(f"[pipeline] note: {note}")
    return RunResult(status=ctx.exit_status, exit_code=exit_code, run_dir=run_dir,
                     manifest=manifest, error="; ".join(ctx.notes) or None)


__all__ = ["run", "resolve_stages", "run_gate", "RunResult", "MAX_REPAIRS"]
