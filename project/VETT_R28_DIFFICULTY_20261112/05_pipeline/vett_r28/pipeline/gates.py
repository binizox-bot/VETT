"""Gate registry: small pure functions returning ``{verdict, evidence}``.

Contract
--------
* ``PASS``           -> continue
* ``FAIL``           -> bounded repair, otherwise escalate (or freeze-abort)
* ``DEGRADED``       -> only allowed for ``blocking=False`` gates: continue and
                        surface the gap in the report
* ``UNTESTED``       -> recorded, never silently treated as PASS (blocking gates
                        treat it as FAIL)

A gate must be a pure function of the run context: it may read files but may not
write, mutate the context or perform model calls.
"""

from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Callable

from .canonical import canon, digest, sha256_file, sha256_text
from .errors import FrozenViolation

VERDICTS = ("PASS", "FAIL", "DEGRADED", "UNTESTED")


@dataclass(frozen=True)
class GateSpec:
    gate_id: str
    stage: str
    description: str
    blocking: bool
    repair_id: str | None
    exit_code: int
    fn: Callable[[Any], dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "stage": self.stage,
            "description": self.description,
            "blocking": self.blocking,
            "repair_id": self.repair_id,
            "exit_code": self.exit_code,
            "predicate": f"{self.fn.__module__}.{self.fn.__name__}",
        }


REGISTRY: dict[str, GateSpec] = {}


def gate(gate_id: str, *, stage: str, description: str, blocking: bool = True,
         repair: str | None = None, exit_code: int = 3):
    def decorator(fn: Callable[[Any], dict[str, Any]]):
        if gate_id in REGISTRY:
            raise RuntimeError(f"duplicate gate id {gate_id}")
        REGISTRY[gate_id] = GateSpec(gate_id=gate_id, stage=stage, description=description,
                                     blocking=blocking, repair_id=repair,
                                     exit_code=exit_code, fn=fn)
        return fn

    return decorator


def registry_snapshot() -> dict[str, Any]:
    return {
        "schema": "vett-r28-pipeline-gate-registry/v1",
        "gate_count": len(REGISTRY),
        "gates": [REGISTRY[key].as_dict() for key in sorted(REGISTRY)],
    }


def _result(verdict: str, evidence: Any) -> dict[str, Any]:
    if verdict not in VERDICTS:
        raise ValueError(f"invalid verdict {verdict!r}")
    return {"verdict": verdict, "evidence": evidence}


def _load(path: pathlib.Path) -> Any:
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def _freeze_check(base: pathlib.Path, entries: dict[str, Any]) -> dict[str, Any]:
    rows = []
    mismatches = []
    for name, expected in sorted(entries.items()):
        path = (base / name).resolve()
        if not path.is_file():
            rows.append({"file": name, "status": "missing"})
            mismatches.append(name)
            continue
        actual_sha = sha256_file(path)
        actual_bytes = path.stat().st_size
        ok = actual_sha == expected.get("sha256") and actual_bytes == expected.get("bytes")
        rows.append({"file": name, "bytes": actual_bytes, "sha256": actual_sha,
                     "expected_sha256": expected.get("sha256"),
                     "expected_bytes": expected.get("bytes"), "ok": ok})
        if not ok:
            mismatches.append(name)
    return {"files": rows, "mismatches": mismatches, "ok": not mismatches}


# ---------------------------------------------------------------------------
# bootstrap gates: frozen inputs + R26.15 zero drift
# ---------------------------------------------------------------------------
@gate("G_PREREG_FROZEN", stage="bootstrap", exit_code=4,
      description="preregistration.json + PREREGISTRATION.md match prereg_freeze.json")
def g_prereg_frozen(ctx) -> dict[str, Any]:
    freeze_path = ctx.config.path("prereg_freeze")
    freeze = _load(freeze_path)
    result = _freeze_check(ctx.config.path("prereg").parent, freeze["files"])
    result.update({"freeze": str(freeze_path), "version": freeze.get("version"),
                   "freeze_sha256": sha256_file(freeze_path),
                   "endpoint_registry_sha256": freeze.get("endpoint_registry_sha256")})
    return _result("PASS" if result["ok"] else "FAIL", result)


@gate("G_CONTRACT_FROZEN", stage="bootstrap", exit_code=4,
      description="r28_contract.json + R28_CONTRACT.md match contract_freeze.json")
def g_contract_frozen(ctx) -> dict[str, Any]:
    freeze_path = ctx.config.path("contract_freeze")
    freeze = _load(freeze_path)
    run_root = ctx.config.pipeline_root.parent
    entries: dict[str, Any] = {}
    file_info = freeze.get("file") or {}
    if file_info.get("path"):
        entries[str((run_root / str(file_info["path"])).resolve())] = {
            "sha256": file_info["sha256"], "bytes": file_info["bytes"]}
    for name, info in (freeze.get("doc_files") or {}).items():
        entries[str((freeze_path.parent / str(name)).resolve())] = info
    result = _freeze_check(pathlib.Path("/"), entries) if entries else {
        "files": [], "mismatches": ["no entries"], "ok": False}
    result.update({"freeze": str(freeze_path), "version": freeze.get("version"),
                   "freeze_sha256": sha256_file(freeze_path),
                   "contract_digests": freeze.get("digests", {})})
    return _result("PASS" if result["ok"] else "FAIL", result)


@gate("G_PROTOCOL_FROZEN", stage="bootstrap", exit_code=4,
      description="judge protocol artefacts match protocol_freeze.json")
def g_protocol_frozen(ctx) -> dict[str, Any]:
    freeze_path = ctx.config.path("protocol_freeze")
    freeze = _load(freeze_path)
    ws = ctx.config.pipeline_root.parent.parent  # workspace root
    run_root = ctx.config.pipeline_root.parent
    entries: dict[str, Any] = {}
    for key, info in sorted((freeze.get("artifacts") or {}).items()):
        raw = str(info.get("path") or "")
        if not raw:
            continue
        candidate = pathlib.Path(raw)
        if not candidate.is_absolute():
            candidate = (ws / candidate) if raw.startswith(run_root.name) else (run_root / candidate)
        entries[str(candidate.resolve())] = {"sha256": info.get("sha256"), "bytes": info.get("bytes")}
    rows = []
    mismatches = []
    for name, expected in entries.items():
        path = pathlib.Path(name)
        if not path.is_file():
            rows.append({"file": name, "status": "missing"})
            mismatches.append(name)
            continue
        actual_sha = sha256_file(path)
        actual_bytes = path.stat().st_size
        ok = actual_sha == expected["sha256"] and actual_bytes == expected["bytes"]
        rows.append({"file": name, "bytes": actual_bytes, "sha256": actual_sha, "ok": ok})
        if not ok:
            mismatches.append(name)
    evidence = {"files": rows, "mismatches": mismatches, "ok": not mismatches,
                "freeze": str(freeze_path), "freeze_sha256": sha256_file(freeze_path),
                "protocol_digests": freeze.get("digests", {}),
                "freeze_artifacts": sorted(
                    str(pathlib.Path(name).name) for name in entries),
                "excluded_derived": ["02_design/protocol_verify_result.json"],
                "exclusion_reason": (
                    "protocol_verify_result.json is a derived output rewritten by every "
                    "--check run; it is intentionally NOT part of the 7 frozen artifacts, "
                    "so hashing it would create a false PROTOCOL_DRIFT alarm.")}
    if any("protocol_verify_result" in str(name) for name in entries):
        evidence["ok"] = False
        evidence["mismatches"] = list(evidence["mismatches"]) + [
            "protocol_verify_result.json must not be in the frozen artifact set"]
    return _result("PASS" if evidence["ok"] else "FAIL", evidence)


def _import_r28gen(ctx):
    build = ctx.config.pipeline_root.parent / "03_build"
    if str(build) not in sys.path:
        sys.path.insert(0, str(build))
    import r28gen  # noqa: F401
    return build


@gate("G_SOLVER_PIN", stage="bootstrap", exit_code=4,
      description="frozen vett_r25 solver + scenarios still match their pinned sha256")
def g_solver_pin(ctx) -> dict[str, Any]:
    _import_r28gen(ctx)
    from r28gen.solver_bridge import solver_provenance

    record = solver_provenance(strict=False)
    return _result("PASS" if record.get("matches_pinned") else "FAIL", record)


@gate("G_R26_15_ZERO_DRIFT", stage="bootstrap", exit_code=4,
      description="live R26.15 candidate is byte-identical to the t1 frozen copy (165 files / 93,346,177 B)")
def g_r26_15_zero_drift(ctx) -> dict[str, Any]:
    _import_r28gen(ctx)
    from r28gen.verify import verify_r26_15_against_backup

    result = verify_r26_15_against_backup()
    ok = (bool(result.get("ok")) and result.get("file_count") == 165
          and result.get("total_bytes") == 93346177 and not result.get("mismatches"))
    result["expected"] = {"file_count": 165, "total_bytes": 93346177}
    return _result("PASS" if ok else "FAIL", result)


@gate("G_PROTECTED_PATHS", stage="bootstrap", exit_code=4,
      description="all 338 protected files and their tree aggregate still match PROTECTED_PATHS.json")
def g_protected_paths(ctx) -> dict[str, Any]:
    _import_r28gen(ctx)
    from r28gen.verify import verify_protected_paths

    result = verify_protected_paths()
    r26_group = next((group for group in result.get("groups", [])
                      if group.get("id") == "r26_15_candidate"), {})
    ok = (bool(result.get("ok")) and result.get("file_count") == 338
          and r26_group.get("file_count") == 165
          and r26_group.get("aggregate_ok") is True)
    result["expected"] = {"file_count": 338, "r26_15_files": 165}
    return _result("PASS" if ok else "FAIL", {
        "ok": ok,
        "file_count": result.get("file_count"),
        "r26_15_file_count": result.get("r26_15_file_count"),
        "r26_15_total_bytes": result.get("r26_15_total_bytes"),
        "r26_15_aggregate_sha256": result.get("r26_15_aggregate_sha256"),
        "groups": [{"id": group["id"], "ok": group["ok"],
                    "files": group["file_count"]} for group in result.get("groups", [])],
        "mismatch_count": sum(len(group.get("mismatches", [])) for group in result.get("groups", [])),
    })


@gate("G_BUDGET_CONFIG", stage="bootstrap",
      description="budget caps are sane and the paid-cloud path is disabled")
def g_budget_config(ctx) -> dict[str, Any]:
    settings = ctx.config.budget_settings()
    problems = []
    if float(settings["hard_cap_cny"]) <= 0:
        problems.append("hard cap must be > 0")
    if bool(settings["cloud_enabled"]):
        problems.append("cloud_enabled must be false (zero paid API)")
    if int(settings["cloud_calls_hard_cap"]) > 80:
        problems.append("cloud call cap > 80 (t12 protocol)")
    if float(settings["soft_cap_cny"]) > float(settings["hard_cap_cny"]):
        problems.append("soft cap > hard cap")
    return _result("PASS" if not problems else "FAIL",
                   {"settings": settings, "problems": problems})


# ---------------------------------------------------------------------------
# generate gates: dataset integrity recomputed by the pipeline (HA subset)
# ---------------------------------------------------------------------------
@gate("G_FAMILY_UNIT", stage="generate",
      description="evaluation set has at most one question per family and one record per question")
def g_family_unit(ctx) -> dict[str, Any]:
    summary = (ctx.dataset or {}).get("summary") or {}
    unit = summary.get("family_unit") or {}
    checks = {
        "one_question_per_family": unit.get("one_question_per_family") is True,
        "one_record_per_question": unit.get("one_record_per_question") is True,
        "distinct_records_equal_questions": unit.get("distinct_records") == unit.get("question_count"),
        "family_bootstrap_eligible": unit.get("family_bootstrap_eligible") is True,
    }
    return _result("PASS" if all(checks.values()) else "FAIL",
                   {"checks": checks, "family_unit": unit,
                    "max_questions_per_family": unit.get("max_questions_per_family")})


@gate("G_CONFIG_VALID", stage="generate",
      description="build config validates and matches the frozen build config file")
def g_config_valid(ctx) -> dict[str, Any]:
    dataset = ctx.dataset or {}
    problems = list(dataset.get("config_problems") or [])
    actual = sha256_file(ctx.config.path("build_config"))
    expected = dataset.get("build_config_sha256")
    ok = not problems and expected == actual
    return _result("PASS" if ok else "FAIL",
                   {"config_problems": problems, "build_config_sha256": actual,
                    "used_build_config_sha256": expected, "mode": dataset.get("mode")})


@gate("G_DATASET_COUNTS", stage="generate",
      description="built instance counts match the configured N (dry-run: synthetic count)")
def g_dataset_counts(ctx) -> dict[str, Any]:
    dataset = ctx.dataset or {}
    summary = dataset.get("summary") or {}
    expected = dataset.get("expected_count")
    ok = summary.get("question_count") == expected and expected is not None
    return _result("PASS" if ok else "FAIL",
                   {"expected": expected, "question_count": summary.get("question_count"),
                    "published": summary.get("published"), "held_out": summary.get("held_out"),
                    "mode": dataset.get("mode")})


@gate("G_DATASET_INTEGRITY", stage="generate",
      description="records are distinct, no constant field, twins share facts, prompt budget respected")
def g_dataset_integrity(ctx) -> dict[str, Any]:
    dataset = ctx.dataset or {}
    summary = dataset.get("summary") or {}
    limited = "limited" in str(dataset.get("mode") or "")
    checks = {
        "distinct_ratio_is_one": summary.get("distinct_ratio") == 1.0,
        "twin_mismatch_empty": not summary.get("twin_mismatch"),
        "prompt_budget": int(summary.get("max_published_tokens") or 0) <= 7000,
    }
    evidence = {"checks": checks, "summary": summary, "limited_run": limited}
    if limited:
        # A smoke build (explicit --limit) cannot say anything about constant
        # fields: with 2-3 records every field is trivially "constant".  The
        # full-run check stays mandatory for the real N.
        evidence["constant_fields_check"] = "deferred_limited_smoke_run"
    else:
        checks["no_constant_fields"] = summary.get("constant_field_count") == 0
        checks["families_distinct"] = bool(summary.get("families_distinct"))
    ok = all(checks.values())
    return _result("PASS" if ok else "FAIL", evidence)


@gate("G_DATASET_DETERMINISM", stage="generate",
      description="rebuilt sample of instances is byte-identical to the first build")
def g_dataset_determinism(ctx) -> dict[str, Any]:
    determinism = (ctx.dataset or {}).get("determinism") or {}
    ok = bool(determinism.get("ok"))
    return _result("PASS" if ok else "FAIL", determinism)


# ---------------------------------------------------------------------------
# annotate gates
# ---------------------------------------------------------------------------
BYPASS_PATTERNS = (
    "service.generate(",
    "urllib.request",
    "urllib.error",
    "http.client",
    "requests.get",
    "requests.post",
    "socket.socket",
)


def _scan_local_bypass() -> dict[str, Any]:
    """Static scan: no module may call the model or the network outside the
    sanctioned ``adapters.LocalJudge`` -> ``local_inference.api.annotate`` path."""
    package = pathlib.Path(__file__).resolve().parents[1]  # vett_r28/pipeline
    violations: list[dict[str, Any]] = []
    scanned = 0
    for path in sorted(package.glob("*.py")):
        if path.name.startswith("_"):
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in BYPASS_PATTERNS:
                if pattern in line:
                    violations.append({"file": path.name, "line": index,
                                       "pattern": pattern, "code": stripped[:160]})
            if "api.annotate(" in line and path.name != "adapters.py":
                violations.append({"file": path.name, "line": index,
                                   "pattern": "api.annotate( outside adapters.py",
                                   "code": stripped[:160]})
    return {"scanned_files": scanned, "violations": violations,
            "allowed_annotation_path": "adapters.py -> local_inference.api.annotate",
            "patterns": list(BYPASS_PATTERNS)}


@gate("G_ROUTING_CARD", stage="annotate", exit_code=4,
      description="ALLOW/DENY come from routing_card.json (no hardcoded list, no bypass call)")
def g_routing_card(ctx) -> dict[str, Any]:
    from . import routes

    card_path = ctx.config.path("routing_card")
    verdicts = routes.task_verdicts(card_path)
    whitelist = sorted(task for task, verdict in verdicts.items() if verdict == "ALLOW")
    denied = sorted(task for task, verdict in verdicts.items() if verdict == "DENY")
    tasks = ctx.config.annotation_settings()["tasks"]
    problems: list[str] = []
    if not verdicts:
        problems.append("routing_card.json missing/unparsable -> fail-safe DENY")
    not_allowed = [task for task in tasks if verdicts.get(task) != "ALLOW"]
    if not_allowed:
        problems.append(f"configured annotation tasks not ALLOW in routing card: {not_allowed}")
    judge_routes: dict[str, Any] = {}
    try:
        scripts = str(ctx.config.path("judge_protocol_scripts"))
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import judge_protocol  # type: ignore

        for task in tasks:
            route = judge_protocol.local_route_at_judge_time(task)
            judge_routes[task] = {"verdict": route.get("verdict"),
                                  "reason_code": route.get("reason_code"),
                                  "template_version": route.get("template_version")}
        if any(row["verdict"] != "ALLOW" for row in judge_routes.values()):
            problems.append("judge-time route denied one of the configured tasks")
        card_allow = set(whitelist)
        if set(tasks) - card_allow:
            problems.append("configured tasks bypass the routing card ALLOW set")
    except Exception as exc:  # noqa: BLE001 - fail-safe
        problems.append(f"judge_protocol routing check failed: {type(exc).__name__}: {exc}")
    scan = _scan_local_bypass()
    if scan["violations"]:
        problems.append(f"{len(scan['violations'])} bypass call(s) detected in pipeline source")
    evidence = {
        "routing_card": str(card_path),
        "allow_tasks": whitelist,
        "deny_tasks": denied,
        "configured_tasks": tasks,
        "judge_time_routes": judge_routes,
        "static_scan": scan,
        "problems": problems,
    }
    return _result("PASS" if not problems else "FAIL", evidence)


@gate("G_LOCAL_ROUTE", stage="annotate", exit_code=4,
      description="each requested judge task is ALLOW on the frozen routing card (fail-safe DENY)")
def g_local_route(ctx) -> dict[str, Any]:
    tasks = ctx.config.annotation_settings()["tasks"]
    try:
        run_root = ctx.config.pipeline_root.parent
        judge_dir = run_root / "02_design" / "scripts"
        if str(judge_dir) not in sys.path:
            sys.path.insert(0, str(judge_dir))
        import judge_protocol  # type: ignore

        rows = {}
        for task in tasks:
            route = judge_protocol.local_route_at_judge_time(task)
            rows[task] = {"verdict": route.get("verdict"),
                          "reason_code": route.get("reason_code"),
                          "template_version": route.get("template_version")}
        ok = all(row["verdict"] == "ALLOW" for row in rows.values())
    except Exception as exc:  # noqa: BLE001
        rows = {"error": f"{type(exc).__name__}: {exc}"}
        ok = False
    return _result("PASS" if ok else "FAIL", {"routes": rows, "dry_run": ctx.dry_run})


@gate("G_ANNOTATION_CACHE_KEY", stage="annotate",
      description="cache keys follow the v2 recipe (input + params + template + model digest)")
def g_annotation_cache_key(ctx) -> dict[str, Any]:
    from .cache import cache_key

    annotations = ctx.annotations or {}
    rows = annotations.get("records") or []
    bad = []
    for row in rows:
        expected = cache_key(
            task=row["task"],
            input_text=row["input_text"],
            params=row["params"],
            prompt_template_version=row["prompt_template_version"],
            model_digest=row["model_digest"],
        )
        if expected != row["cache_key"]:
            bad.append(row["sample_id"])
    return _result("PASS" if not bad else "FAIL",
                   {"checked": len(rows), "mismatched": bad[:20],
                    "mismatched_count": len(bad)})


@gate("G_ANNOTATION_COVERAGE", stage="annotate", blocking=False, repair="retry_annotation",
      description="share of successful (non-DEGRADED) annotations reaches the configured floor")
def g_annotation_coverage(ctx) -> dict[str, Any]:
    metrics = (ctx.annotations or {}).get("metrics") or {}
    coverage = float(metrics.get("coverage") or 0.0)
    floor = float(ctx.config.annotation_settings()["min_coverage"])
    mode = metrics.get("mode")
    evidence = {"coverage": coverage, "floor": floor, "mode": mode,
                "expected": metrics.get("expected"), "ok": metrics.get("ok"),
                "degraded": metrics.get("degraded")}
    if mode == "mechanical_only":
        return _result("DEGRADED", evidence)
    return _result("PASS" if coverage >= floor else "FAIL", evidence)


@gate("G_LOCAL_FIRST", stage="annotate", exit_code=4,
      description="zero cloud calls and no cloud route for any local-first task")
def g_local_first(ctx) -> dict[str, Any]:
    totals = ctx.budget.totals()
    annotations = ctx.annotations or {}
    cloud_routes = [row["sample_id"] for row in annotations.get("records") or []
                    if row.get("route") == "cloud"]
    ok = totals.get("cloud_calls") == 0 and not cloud_routes
    return _result("PASS" if ok else "FAIL",
                   {"cloud_calls": totals.get("cloud_calls"),
                    "cloud_routed_samples": cloud_routes[:20], "adapter": annotations.get("mode")})


# ---------------------------------------------------------------------------
# judge gates
# ---------------------------------------------------------------------------
@gate("G_JUDGE_SCHEMA", stage="judge",
      description="every annotation record has a valid envelope schema and status")
def g_judge_schema(ctx) -> dict[str, Any]:
    judged = ctx.judged or {}
    problems = list(judged.get("schema_problems") or [])
    return _result("PASS" if not problems else "FAIL",
                   {"problems": problems, "records": judged.get("record_count")})


@gate("G_JUDGE_COMPARABILITY", stage="judge", blocking=False, repair="rescore_judge",
      description="mechanical references exist for comparable tasks and metrics are recomputable")
def g_judge_comparability(ctx) -> dict[str, Any]:
    judged = ctx.judged or {}
    tasks = judged.get("tasks") or {}
    comparable_tasks = [task for task in ("T1_factor_visibility",
                                          "C1_cert_sentence_consistency")
                        if task in tasks]
    missing = [task for task in comparable_tasks
               if (tasks[task].get("comparable_ok", 0) + tasks[task].get("comparable_degraded", 0))
               == 0]
    evidence = {"ok": judged.get("ok"), "tasks": tasks,
                "tasks_without_comparables": missing,
                "computed_from": judged.get("computed_from"),
                "mode": judged.get("mode")}
    if judged.get("mode") == "mechanical_only":
        return _result("DEGRADED", evidence)
    ok = bool(judged.get("ok")) and not missing
    return _result("PASS" if ok else "FAIL", evidence)


@gate("G_ENDPOINT_UNSCORED", stage="judge",
      description="no endpoint is claimed: paired_accuracy_drop stays NOT_RUN without model answers")
def g_endpoint_unscored(ctx) -> dict[str, Any]:
    endpoints = ((ctx.judged or {}).get("endpoints")) or {}
    primary = endpoints.get("paired_accuracy_drop") or {}
    ok = primary.get("status") == "NOT_RUN" and primary.get("claim") is False
    return _result("PASS" if ok else "FAIL",
                   {"primary": primary, "all_statuses": {
                       name: value.get("status") for name, value in endpoints.items()}})


# ---------------------------------------------------------------------------
# aggregate / report gates
# ---------------------------------------------------------------------------
@gate("G_BUDGET_WITHIN_CAP", stage="aggregate",
      description="cumulative spend and cloud call count stay under the hard caps")
def g_budget_within_cap(ctx) -> dict[str, Any]:
    totals = ctx.budget.totals()
    ok = (totals["cost_cny"] <= totals["hard_cap_cny"]
          and totals["cloud_calls"] <= totals["cloud_calls_hard_cap"])
    return _result("PASS" if ok else "FAIL", totals)


@gate("G_ARTIFACTS_DETERMINISTIC", stage="report", repair="rewrite_artifact_hashes",
      description="ARTIFACT_HASHES matches the files on disk and a replay reproduces every hash")
def g_artifacts_deterministic(ctx) -> dict[str, Any]:
    hashes = ctx.read_json("ARTIFACT_HASHES.json")
    rows = []
    mismatched = []
    for name, expected in sorted((hashes.get("artifacts") or {}).items()):
        path = ctx.run_dir / name
        if not path.is_file():
            mismatched.append(name)
            continue
        actual = sha256_file(path)
        rows.append({"artifact": name, "sha256": actual, "expected": expected,
                     "ok": actual == expected})
        if actual != expected:
            mismatched.append(name)
    replay = {}
    replay_path = ctx.run_dir / "REPLAY_CHECK.json"
    if replay_path.is_file():
        replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay_ok = (not replay.get("previous_present", False)) or bool(replay.get("identical", False))
    ok = not mismatched and replay_ok
    return _result("PASS" if ok else "FAIL",
                   {"artifacts": rows, "mismatched": mismatched, "replay": replay})


@gate("G_REPORT_COMPLETE", stage="report", repair="rebuild_report",
      description="REPORT.md carries every mandatory section and no endpoint claim")
def g_report_complete(ctx) -> dict[str, Any]:
    report_path = ctx.run_dir / "REPORT.md"
    if not report_path.is_file():
        return _result("FAIL", {"error": "REPORT.md missing"})
    text = report_path.read_text(encoding="utf-8")
    required = [
        "## 1. 概览", "## 2. 冻结输入与零漂移", "## 3. 数据集", "## 4. 标注",
        "## 5. 判分", "## 6. 端点状态", "## 7. 门与修复", "## 8. 预算",
        "## 9. 降级", "## 10. 复现", "## 11. 产物哈希",
    ]
    missing = [section for section in required if section not in text]
    forbidden = []
    if "paired_accuracy_drop" in text and "NOT_RUN" not in text:
        forbidden.append("endpoint claim without NOT_RUN")
    if "vs 0.25" in text:
        forbidden.append("forbidden 'vs 0.25' baseline phrasing")
    ok = not missing and not forbidden and "R26.15" in text
    return _result("PASS" if ok else "FAIL",
                   {"missing_sections": missing, "forbidden": forbidden,
                    "bytes": len(text.encode("utf-8"))})


# Stage -> gate ids.  Order matters: bootstrap first, report last.
STAGE_GATES: dict[str, list[str]] = {
    "bootstrap": [
        "G_PREREG_FROZEN", "G_CONTRACT_FROZEN", "G_PROTOCOL_FROZEN", "G_SOLVER_PIN",
        "G_R26_15_ZERO_DRIFT", "G_PROTECTED_PATHS", "G_BUDGET_CONFIG",
    ],
    "generate": ["G_FAMILY_UNIT", "G_CONFIG_VALID", "G_DATASET_COUNTS",
                 "G_DATASET_INTEGRITY", "G_DATASET_DETERMINISM"],
    "annotate": ["G_LOCAL_ROUTE", "G_ANNOTATION_CACHE_KEY",
                 "G_ANNOTATION_COVERAGE", "G_LOCAL_FIRST"],
    "judge": ["G_JUDGE_SCHEMA", "G_JUDGE_COMPARABILITY", "G_ENDPOINT_UNSCORED"],
    "aggregate": ["G_BUDGET_WITHIN_CAP"],
    "report": ["G_ARTIFACTS_DETERMINISTIC", "G_REPORT_COMPLETE"],
    "publish": [],
}

# Gates that must pass *before* a stage may execute (governance/preflight).
PRE_STAGE_GATES: dict[str, list[str]] = {
    "annotate": ["G_ROUTING_CARD"],
}


def validate_registry(repair_ids: set[str]) -> list[str]:
    problems = []
    pre_ids = {gid for ids in PRE_STAGE_GATES.values() for gid in ids}
    for gate_id, spec in REGISTRY.items():
        if spec.stage not in STAGE_GATES:
            problems.append(f"{gate_id}: unknown stage {spec.stage}")
        elif gate_id not in STAGE_GATES[spec.stage] and gate_id not in pre_ids:
            problems.append(f"{gate_id}: stage {spec.stage} does not list it in STAGE_GATES")
        if spec.repair_id and spec.repair_id not in repair_ids:
            problems.append(f"{gate_id}: unknown repair {spec.repair_id}")
    for stage, gate_ids in STAGE_GATES.items():
        for gate_id in gate_ids:
            if gate_id not in REGISTRY:
                problems.append(f"{stage}: unregistered gate {gate_id}")
    for stage, gate_ids in PRE_STAGE_GATES.items():
        for gate_id in gate_ids:
            if gate_id not in REGISTRY:
                problems.append(f"{stage}: unregistered pre-stage gate {gate_id}")
    return problems


__all__ = ["GateSpec", "REGISTRY", "STAGE_GATES", "PRE_STAGE_GATES", "gate",
           "registry_snapshot", "validate_registry", "VERDICTS"]
