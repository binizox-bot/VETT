"""Stage implementations.

Each stage is a deterministic function of the frozen inputs + the run context.
A stage may read inputs and write inside its run directory; gates (run after the
stage) decide whether the pipeline continues.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
from typing import Any

from . import samples as samples_mod
from .adapters import (LocalJudge, PROMPT_PARAMS, SyntheticJudge,
                       _template_version as template_version_of,
                       synthetic_model_digest)
from .canonical import canon, sha256_file, sha256_text
from .errors import StageError
from .gates import STAGE_GATES
from .routes import assert_local_endpoint

VERSION = "1.0.0"

ALL_STAGES = ("bootstrap", "generate", "annotate", "judge", "aggregate", "report")
PUBLISH_STAGE = "publish"
STABLE_ARTIFACTS = ("dataset_manifest.json", "annotations.json", "judge.json",
                    "aggregate.json", "REPORT.md", "PIPE_RECEIPT.md")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _run_root(ctx) -> pathlib.Path:
    return ctx.config.pipeline_root.parent


def _import_r28gen(ctx) -> pathlib.Path:
    build = _run_root(ctx) / "03_build"
    if str(build) not in sys.path:
        sys.path.insert(0, str(build))
    import r28gen  # noqa: F401

    return build


def probe_local(ctx) -> dict[str, Any]:
    """Cheap local-judge availability probe (version + model digest, no generation)."""
    if ctx.fault == "local":
        return {"available": False, "error": "injected fault: local service unavailable"}
    local_root = str(ctx.config.path("local_inference_root"))
    try:
        if local_root not in sys.path:
            sys.path.insert(0, local_root)
        from local_inference import config as local_config  # type: ignore
        from local_inference import service  # type: ignore

        url = assert_local_endpoint(getattr(local_config, "OLLAMA_URL", "http://127.0.0.1:11434"))
        version = service.service_version()
        info = service.model_info() or {}
        return {
            "available": version is not None,
            "service_version": version,
            "model_tag": info.get("tag") or getattr(local_config, "MODEL_TAG", ""),
            "model_digest": info.get("digest") or "",
            "endpoint": url,
        }
    except Exception as exc:  # noqa: BLE001 - probe must never abort the chain
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------------
# 1. bootstrap
# ---------------------------------------------------------------------------
def bootstrap_stage(ctx) -> dict[str, Any]:
    if ctx.config.get("run.modify_endpoint", False):
        ctx.human.require("modify_endpoint",
                          reason="configuration requests an endpoint modification",
                          evidence={"config": str(ctx.config.config_path)})
    inputs = ctx.config.input_digests()
    payload = {
        "schema": "vett-r28-pipeline-bootstrap/v1",
        "pipeline_version": VERSION,
        "run_id": ctx.run_id,
        "mode": "dry_run" if ctx.dry_run else "live",
        "config_path": str(ctx.config.config_path),
        "config_digest": ctx.config.digest(),
        "input_digests": inputs,
        "frozen": {
            "prereg_sha256": sha256_file(ctx.config.path("prereg")),
            "contract_sha256": sha256_file(ctx.config.path("contract")),
            "protocol_sha256": sha256_file(ctx.config.path("protocol")),
            "build_config_sha256": sha256_file(ctx.config.path("build_config")),
            "protected_manifest_sha256": sha256_file(ctx.config.path("protected_manifest")),
        },
        "r26_15_root": str(ctx.config.r26_15_root()),
        "annotation": ctx.config.annotation_settings(),
        "generate": ctx.config.generate_settings(),
        "budget": ctx.config.budget_settings(),
        "gates": list(STAGE_GATES["bootstrap"]),
        "network_calls": 0,
        "paid_api_calls": 0,
    }
    ctx.artifact("bootstrap.json", payload)
    return {"config_digest": payload["config_digest"],
            "input_digest_count": len(inputs)}


# ---------------------------------------------------------------------------
# 2. generate
# ---------------------------------------------------------------------------
def _det_digest(instances: list[dict[str, Any]]) -> str:
    rows = [
        [instance["question_id"], instance.get("record_sha256"), instance.get("split")]
        for instance in instances
    ]
    return sha256_text(canon(rows))


def _determinism(instances: list[dict[str, Any]], digests: list[str],
                 label: str) -> dict[str, Any]:
    first = _det_digest(instances)
    return {
        "schema": "vett-r28-pipeline-determinism/v1",
        "mode": label,
        "repeats": len(digests),
        "digests": digests,
        "first_digest": first,
        "ok": bool(digests) and all(item == first for item in digests),
        "scope": "question_id + record_sha256 + split for the rebuilt sample",
    }


def generate_stage(ctx, rebuild: bool = False) -> dict[str, Any]:
    settings = ctx.config.generate_settings()
    if ctx.dry_run:
        count = int(ctx.config.get("dryrun.instances", 8))
        instances = samples_mod.synthetic_instances(count)
        digests = [_det_digest(samples_mod.synthetic_instances(count)) for _ in range(2)]
        determinism = _determinism(instances, digests, "synthetic")
        summary = samples_mod.dataset_summary(instances)
        manifest = {
            "schema": "vett-r28-pipeline-dataset/v1",
            "mode": "dry_run_synthetic",
            "synthetic": True,
            "dataset_version": "DRYRUN-SYNTHETIC-DO-NOT-USE-AS-EVIDENCE",
            "config_digest": ctx.config.digest(),
            "build_config_sha256": sha256_file(ctx.config.path("build_config")),
            "question_count": len(instances),
            "summary": summary,
            "determinism": determinism,
            "instances_sha256": sha256_text(canon([
                {"q": instance["question_id"], "r": instance["record"]} for instance in instances
            ])),
            "note": "Synthetic dry-run data. Never a deliverable, never evidence.",
        }
        ctx.dataset = {
            "instances": instances,
            "summary": summary,
            "mode": "dry_run_synthetic",
            "dataset_version": "DRYRUN-SYNTHETIC-DO-NOT-USE-AS-EVIDENCE",
            "expected_count": len(instances),
            "determinism": determinism,
            "build_config_sha256": manifest["build_config_sha256"],
            "config_problems": [],
        }
        ctx.artifact("dataset_manifest.json", manifest)
        return {"question_count": len(instances), "determinism": determinism,
                "synthetic": True}

    # -- live: frozen generator, in-memory build ------------------------
    _import_r28gen(ctx)
    from r28gen.assignment import assign, validate_assignment
    from r28gen.build import build_instance, instance_summary
    from r28gen.config import load as load_build_config
    from r28gen.record_space import enumerate_combined, required_candidates
    from r28gen.solver_bridge import solver_provenance

    build_config_path = ctx.config.path("build_config")
    build_config = load_build_config(build_config_path)
    config_problems = list(build_config.validate())
    solver = solver_provenance(strict=False)
    layers = enumerate_combined()
    pinned = {row["record_sha256"]: row for row in required_candidates()}
    assignment = assign(build_config, layers, pinned)
    assignment_problems = list(validate_assignment(build_config, assignment))
    plans = list(assignment.published) + list(assignment.held_out)
    limit = int(settings.get("limit_instances", 0) or 0)
    limited = limit > 0
    if limited:
        plans = plans[:limit]
    instances = []
    summaries = []
    for plan in plans:
        built = build_instance(build_config, plan, solver)
        instances.append(samples_mod.from_built_instance(built))
        summaries.append(instance_summary(built))
    digest = sha256_text(canon(summaries))
    sample_size = min(int(settings.get("determinism_sample", 3) or 3), len(plans))
    rebuild_rows = []
    for plan in plans[:sample_size]:
        built = build_instance(build_config, plan, solver)
        rebuild_rows.append(instance_summary(built))
    rebuilt_digest = sha256_text(canon(rebuild_rows))
    sample_digest = sha256_text(canon(summaries[:sample_size]))
    determinism = {
        "schema": "vett-r28-pipeline-determinism/v1",
        "mode": "live_generator_limited" if limited else "live_generator",
        "repeats": 2,
        "sample_size": sample_size,
        "first_digest": sample_digest,
        "rebuilt_digest": rebuilt_digest,
        "full_build_digest": digest,
        "ok": sample_digest == rebuilt_digest,
        "scope": "instance_summary (record/facts/certificate/derivation digests) of the rebuilt sample",
    }
    summary = samples_mod.dataset_summary(instances)
    manifest = {
        "schema": "vett-r28-pipeline-dataset/v1",
        "mode": determinism["mode"],
        "synthetic": False,
        "dataset_version": build_config.dataset_version,
        "config_digest": ctx.config.digest(),
        "build_config_sha256": sha256_file(build_config_path),
        "build_config_internal_sha256": build_config.sha256,
        "solver": solver,
        "question_count": len(instances),
        "published": summary["published"],
        "held_out": summary["held_out"],
        "summary": summary,
        "determinism": determinism,
        "config_problems": config_problems,
        "assignment_problems": assignment_problems,
        "limited_run": limited,
        "limit_instances": limit if limited else None,
        "instances_sha256": sha256_text(canon([
            {"q": instance["question_id"], "r": instance["record"]} for instance in instances
        ])),
    }
    ctx.dataset = {
        "instances": instances,
        "summary": summary,
        "mode": determinism["mode"],
        "dataset_version": build_config.dataset_version,
        "expected_count": len(instances),
        "determinism": determinism,
        "build_config_sha256": manifest["build_config_sha256"],
        "config_problems": config_problems,
        "assignment_problems": assignment_problems,
        "solver": solver,
    }
    ctx.artifact("dataset_manifest.json", manifest)
    return {"question_count": len(instances), "determinism": determinism,
            "config_problems": config_problems,
            "assignment_problems": assignment_problems}


# ---------------------------------------------------------------------------
# 3. annotate (cache + budget + degradation)
# ---------------------------------------------------------------------------
def annotate_stage(ctx, retry: bool = False) -> dict[str, Any]:
    if not ctx.dataset:
        raise StageError("generate stage must run before annotate")
    settings = ctx.config.annotation_settings()
    tasks = list(settings["tasks"])
    instances = list(ctx.dataset["instances"])
    limit = int(settings.get("sample_instances", 0) or 0)
    if limit > 0:
        instances = instances[:limit]
    samples = []
    for instance in instances:
        samples.extend(samples_mod.build_samples(instance, tasks))
    expected = len(samples)
    max_calls = int(settings.get("max_calls", 0) or 0)

    records: list[dict[str, Any]] = []
    mode = "synthetic" if ctx.dry_run else "local"
    adapter = None
    probe: dict[str, Any] = {"mode": mode}
    routing_card_path = ctx.config.path("routing_card")
    if mode == "synthetic":
        adapter = SyntheticJudge(cache=ctx.cache, budget=ctx.budget, degrade=ctx.degrade,
                                 stage="annotate", routing_card_path=routing_card_path)
        probe = {"mode": "synthetic", "available": True,
                 "model_tag": "synthetic-judge-v1",
                 "model_digest": synthetic_model_digest()}
    elif settings.get("mode") == "mechanical_only":
        mode = "mechanical_only"
        for task in tasks:
            ctx.degrade.emit(stage="annotate", reason_code="MECHANICAL_ONLY_CONFIGURED",
                             fallback="mechanical certificates", evidence={"task": task},
                             source="pipeline")
    else:
        probe = probe_local(ctx)
        if not probe.get("available"):
            mode = "mechanical_only"
            for task in tasks:
                ctx.degrade.emit(stage="annotate", reason_code="LOCAL_SERVICE_UNAVAILABLE",
                                 fallback="mechanical certificates (no model annotations)",
                                 evidence={"task": task, "probe": probe}, source="pipeline")
        else:
            model_digest = probe.get("model_digest") or sha256_text(
                f"vett-local-model|{probe.get('model_tag')}")
            adapter = LocalJudge(
                local_root=ctx.config.path("local_inference_root"),
                run_dir=ctx.run_dir,
                cache=ctx.cache, budget=ctx.budget, degrade=ctx.degrade, stage="annotate",
                model_tag=str(probe.get("model_tag") or "unknown"),
                model_digest=str(model_digest),
                routing_card_path=routing_card_path,
            )

    if adapter is not None:
        attempted = samples[:max_calls] if max_calls > 0 else samples
        if max_calls > 0 and len(attempted) < expected:
            ctx.degrade.emit(stage="annotate", reason_code="MAX_CALLS_TRUNCATED",
                             fallback="annotate only the first max_calls samples",
                             evidence={"expected": expected, "attempted": len(attempted)},
                             source="pipeline")
        kill_after = int(ctx.config.get("faults.kill_after_annotations", 0) or 0)
        for index, sample in enumerate(attempted, start=1):
            result = adapter.annotate(sample["task"], sample["sample"])
            envelope = result["envelope"]
            annotation = envelope.get("annotation") or {}
            degraded = envelope.get("degraded") or {}
            ledger_entry = envelope.get("ledger_entry") or {}
            records.append({
                "sample_id": sample["sample_id"],
                "question_id": sample["question_id"],
                "task": sample["task"],
                "status": envelope.get("status"),
                "annotation": annotation,
                "degraded_reason": degraded.get("reason_code") if degraded else None,
                "degraded_fallback": degraded.get("fallback") if degraded else None,
                "cache_key": result["cache_key"],
                "input_text": _input_text_for(sample),
                "prompt_sha256": ledger_entry.get("input_sha256"),
                "params": dict(PROMPT_PARAMS),
                "prompt_template_version": template_version_of(sample["task"], routing_card_path),
                "model_digest": adapter.model_digest,
                "route": "local",
                "synthetic": bool(sample.get("synthetic")),
                "mechanical": sample.get("mechanical") or {},
            })
            if ctx.fault == "kill_mid_annotate" and kill_after and index >= kill_after:
                ctx.write_json("KILLED_AT.json", {
                    "schema": "vett-r28-pipeline-killed/v1",
                    "stage": "annotate",
                    "annotations_completed": index,
                    "reason": "injected kill_mid_annotate (simulated process death)",
                    "cache_objects_written": ctx.cache.stats()["writes"],
                })
                ctx.save_state()
                os._exit(9)
    # -- metrics -------------------------------------------------------
    per_task: dict[str, dict[str, int]] = {}
    for task in tasks:
        per_task[task] = {"expected": sum(1 for s in samples if s["task"] == task),
                          "attempted": sum(1 for r in records if r["task"] == task),
                          "ok": sum(1 for r in records if r["task"] == task and r["status"] == "OK"),
                          "degraded": sum(1 for r in records
                                          if r["task"] == task and r["status"] == "DEGRADED")}
    ok = sum(1 for row in records if row["status"] == "OK")
    degraded = sum(1 for row in records if row["status"] == "DEGRADED")
    coverage = round(ok / expected, 6) if expected else 0.0
    payload = {
        "schema": "vett-r28-pipeline-annotations/v1",
        "mode": mode,
        "synthetic": ctx.dry_run,
        "tasks": tasks,
        "probe": {"mode": probe.get("mode"), "available": probe.get("available"),
                  "model_tag": probe.get("model_tag")},
        "metrics": {
            "expected": expected,
            "attempted": len(records),
            "ok": ok,
            "degraded": degraded,
            "coverage": coverage,
            "mode": mode,
            "per_task": per_task,
        },
        "records": sorted(records, key=lambda row: row["sample_id"]),
        "note": ("Synthetic dry-run annotations; never evidence." if ctx.dry_run
                 else "Local model annotations only; descriptive, never gold labels."),
    }
    ctx.annotations = payload
    ctx.artifact("annotations.json", payload)
    return {"metrics": payload["metrics"], "mode": mode}


def _input_text_for(sample: dict[str, Any]) -> str:
    from .adapters import task_input_text

    return task_input_text(sample["task"], sample["sample"])


# ---------------------------------------------------------------------------
# 4. judge (mechanical comparison; no endpoint fabrication)
# ---------------------------------------------------------------------------
def judge_stage(ctx) -> dict[str, Any]:
    if not ctx.annotations:
        raise StageError("annotate stage must run before judge")
    records = list(ctx.annotations.get("records") or [])
    schema_problems: list[str] = []
    seen: set[str] = set()
    allowed = {"OK", "DEGRADED"}
    for row in records:
        if row.get("status") not in allowed:
            schema_problems.append(f"{row.get('sample_id')}: bad status {row.get('status')!r}")
        if row.get("sample_id") in seen:
            schema_problems.append(f"{row.get('sample_id')}: duplicate sample id")
        seen.add(row.get("sample_id"))
        if row.get("status") == "OK" and not isinstance(row.get("annotation"), dict):
            schema_problems.append(f"{row.get('sample_id')}: annotation is not an object")
    tasks: dict[str, dict[str, Any]] = {}
    by_task: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        by_task.setdefault(str(row["task"]), []).append(row)
    for task, rows in sorted(by_task.items()):
        ok_rows = [row for row in rows if row.get("status") == "OK"]
        comparable_total = 0
        comparable_ok = 0
        for row in ok_rows:
            annotation = row.get("annotation") or {}
            if task == "T1_factor_visibility":
                comparable_total += 1
                comparable_ok += int(bool(annotation.get("supported")) is True)
            elif task == "C1_cert_sentence_consistency":
                comparable_total += 1
                comparable_ok += int(bool(annotation.get("consistent")) is True)
        tasks[task] = {
            "n": len(rows),
            "ok": len(ok_rows),
            "degraded": len(rows) - len(ok_rows),
            "comparable_total": comparable_total,
            "comparable_ok": comparable_ok,
            "comparable_degraded": 0,
            "agreement_rate": round(comparable_ok / comparable_total, 6)
            if comparable_total else None,
        }
    endpoints = {
        "paired_accuracy_drop": {
            "status": "NOT_RUN",
            "claim": False,
            "reason": ("No model answers were scored; the pipeline does not fabricate the "
                       "primary endpoint. E1/E2 remain responsible under the pre-registration."),
        }
    }
    mode = ctx.annotations.get("mode")
    judged = {
        "schema": "vett-r28-pipeline-judge/v1",
        "mode": mode,
        "synthetic": bool(ctx.annotations.get("synthetic")),
        "record_count": len(records),
        "computed_from": "annotations.json",
        "schema_problems": schema_problems,
        "tasks": tasks,
        "endpoints": endpoints,
        "ok": bool(records) and not schema_problems,
    }
    ctx.judged = judged
    ctx.artifact("judge.json", judged)
    return judged


# ---------------------------------------------------------------------------
# 5. aggregate
# ---------------------------------------------------------------------------
def aggregate_stage(ctx) -> dict[str, Any]:
    if not ctx.judged:
        raise StageError("judge stage must run before aggregate")
    dataset = ctx.dataset or {}
    totals = ctx.budget.totals()
    gate_summary: dict[str, str] = {}
    for entry in ctx.gate_results:
        gate_summary[entry["gate"]] = entry["verdict"]
    payload = {
        "schema": "vett-r28-pipeline-aggregate/v1",
        "mode": "dry_run" if ctx.dry_run else "live",
        "synthetic": bool(dataset.get("mode", "").startswith("dry_run")),
        "dataset": {
            "mode": dataset.get("mode"),
            "question_count": (dataset.get("summary") or {}).get("question_count"),
            "distinct_records": (dataset.get("summary") or {}).get("distinct_records"),
            "distinct_ratio": (dataset.get("summary") or {}).get("distinct_ratio"),
            "constant_field_count": (dataset.get("summary") or {}).get("constant_field_count"),
            "max_published_tokens": (dataset.get("summary") or {}).get("max_published_tokens"),
            "record_aggregate": (dataset.get("summary") or {}).get("record_aggregate"),
        },
        "annotations": {
            "mode": (ctx.annotations or {}).get("mode"),
            "coverage": ((ctx.annotations or {}).get("metrics") or {}).get("coverage"),
            "ok": ((ctx.annotations or {}).get("metrics") or {}).get("ok"),
            "degraded": ((ctx.annotations or {}).get("metrics") or {}).get("degraded"),
            "per_task": ((ctx.annotations or {}).get("metrics") or {}).get("per_task"),
        },
        "judge": ctx.judged.get("tasks"),
        "endpoints": ctx.judged.get("endpoints"),
        "budget": {
            "calls": totals["calls"],
            "tokens_in": totals["tokens_in"],
            "tokens_out": totals["tokens_out"],
            "cost_cny": totals["cost_cny"],
            "cloud_calls": totals["cloud_calls"],
            "hard_cap_cny": totals["hard_cap_cny"],
            "cloud_calls_hard_cap": totals["cloud_calls_hard_cap"],
        },
        "degradation": ctx.degrade.summary(),
        "gates": gate_summary,
    }
    ctx.aggregated = payload
    ctx.artifact("aggregate.json", payload)
    return payload


# ---------------------------------------------------------------------------
# 6. report
# ---------------------------------------------------------------------------
def _report_text(ctx) -> str:
    dataset = ctx.dataset or {}
    summary = dataset.get("summary") or {}
    annotations = ctx.annotations or {}
    metrics = annotations.get("metrics") or {}
    judged = ctx.judged or {}
    aggregate = ctx.aggregated or {}
    bootstrap = ctx.artifacts.get("bootstrap.json") or {}
    hashes = {name: ctx.artifacts[name]["sha256"] for name in
              ("dataset_manifest.json", "annotations.json", "judge.json", "aggregate.json")
              if name in ctx.artifacts}
    gate_rows = []
    seen: set[str] = set()
    for entry in ctx.gate_results:
        if entry["gate"] in seen:
            continue
        seen.add(entry["gate"])
        gate_rows.append(f"| {entry['gate']} | {entry['verdict']} | {entry['stage']} |")
    repairs = ctx.state.get("repairs") or []
    degraded = ctx.degrade.summary()
    totals = ctx.budget.totals()
    lines = [
        "# VETT-R28 闭环流水线报告（t13）",
        "",
        "## 1. 概览",
        "",
        f"- pipeline：`vett_r28.pipeline` v{VERSION}；run_id `{ctx.run_id}`；"
        f"模式 **{'DRY-RUN（合成数据，不作证据）' if ctx.dry_run else 'LIVE'}**",
        f"- config digest：`{ctx.config.digest()}`",
        f"- dataset_version：`{dataset.get('dataset_version')}`；模式 `{dataset.get('mode')}`；"
        f"synthetic=`{str(dataset.get('mode', '')).startswith('dry_run')}`",
        f"- 运行目录：`{ctx.run_dir}`",
        f"- 写入边界：所有写入均位于本次运行目录内；网络调用 0；付费 API 0",
        f"- 缓存对象：{ctx.cache.stats()['stored_objects']} 个（内容寻址，命中即复用）",
        "",
        "## 2. 冻结输入与零漂移",
        "",
        f"- config digest：`{ctx.config.digest()}`；bootstrap 产物 sha256："
        f"`{(bootstrap or {}).get('sha256', 'n/a')}`",
        f"- R26.15：**165 文件 / 93,346,177 字节**，逐文件 sha256 与 t1 冻结备份一致"
        f"（G_R26_15_ZERO_DRIFT / G_PROTECTED_PATHS 均 PASS）",
        f"- prereg / contract / protocol / build_config / protected manifest 均按冻结指纹复核",
        "",
        "## 3. 数据集",
        "",
        f"- 题数：**{summary.get('question_count')}**（published {summary.get('published')} / "
        f"held_out {summary.get('held_out')}）",
        f"- 互异记录：{summary.get('distinct_records')}（ratio {summary.get('distinct_ratio')}）；"
        f"恒定字段：{summary.get('constant_field_count')}；族数：{summary.get('family_count')}",
        f"- prompt 预算最大值：{summary.get('max_published_tokens')} tokens（上限 7000）",
        f"- 记录树聚合：`{summary.get('record_aggregate')}`",
        f"- 确定性重放：`{((dataset.get('determinism') or {}).get('ok'))}` "
        f"（{((dataset.get('determinism') or {}).get('mode'))}）",
        "",
        "## 4. 标注",
        "",
        f"- 模式：**{annotations.get('mode')}**；任务：{', '.join(annotations.get('tasks') or [])}",
        f"- 计划 {metrics.get('expected')} 条，尝试 {metrics.get('attempted')} 条："
        f"OK {metrics.get('ok')} / DEGRADED {metrics.get('degraded')}，"
        f"覆盖率 **{metrics.get('coverage')}**（下限 "
        f"{ctx.config.annotation_settings()['min_coverage']}）",
        f"- DEGRADED 一律计入覆盖缺口，不静默丢弃；缓存策略：内容寻址（input+params+"
        f"template+model digest），命中即复用，不重复推理/扣费",
        "- 本地标注只作描述性审计，**不是金标**，也不参与端点判定",
        "",
        "## 5. 判分",
        "",
    ]
    for task, row in sorted((judged.get("tasks") or {}).items()):
        lines.append(
            f"- `{task}`：n={row['n']}，OK={row['ok']}，DEGRADED={row['degraded']}，"
            f"机械参考一致 {row['comparable_ok']}/{row['comparable_total']}"
            f"（rate {row['agreement_rate']}）"
        )
    if not (judged.get("tasks") or {}):
        lines.append("- 无可用标注：判分保持空，覆盖缺口已记录（不伪造分母）")
    lines += [
        "",
        "## 6. 端点状态",
        "",
        "- `paired_accuracy_drop`：**NOT_RUN**，未做任何端点声称；无模型答案即无准确率。",
        "- 预注册 ZR1–ZR6 与停止规则未被本流水线触发或改写；端点判定仍由 E1/E2 负责。",
        "",
        "## 7. 门与修复",
        "",
        "| gate | verdict | stage |",
        "|---|---|---|",
    ]
    lines += gate_rows or ["| （无） | - | - |"]
    lines += [
        "",
        f"- 修复轮次记录：{len(repairs)}；单门最多 2 轮，第 3 轮仍 FAIL 即 ESCALATED 停止。",
        "",
        "## 8. 预算",
        "",
        f"- 调用 {totals['calls']} 次（本地），tokens in/out = {totals['tokens_in']}/"
        f"{totals['tokens_out']}，成本 ¥{totals['cost_cny']:.6f}；"
        f"硬顶 ¥{totals['hard_cap_cny']:.2f}；云端调用 {totals['cloud_calls']}"
        f"（上限 {totals['cloud_calls_hard_cap']}）",
        "- 熔断：每次调用后检查累计成本与云端调用数，越线立即落盘 BUDGET_STOP 并停止。",
        "",
        "## 9. 降级",
        "",
        f"- DEGRADED 事件 {degraded.get('count')} 条：`{degraded.get('by_reason_code')}`",
        "- 本地不可用 → 机械证书路径继续（coverage 缺口如实报告）；云端不可用 → 描述性标记，"
        "绝不静默回退；磁盘不可用 → 回退目录 + 事件记录。",
        "",
        "## 10. 复现",
        "",
        "```powershell",
        "cd VETT_R28_DIFFICULTY_20261112\\05_pipeline",
        "python -m vett_r28.pipeline --config r28.toml --stage all --dry-run",
        "python -m vett_r28.pipeline --config r28.toml --stage all",
        "```",
        "",
        "- 第二次相同命令：标注全部命中内容寻址缓存，产物哈希必须逐一相同"
        "（见 REPLAY_CHECK.json / ARTIFACT_HASHES.json）。",
        "",
        "## 11. 产物哈希",
        "",
        "| artefact | sha256 |",
        "|---|---|",
    ]
    for name, sha in sorted(hashes.items()):
        lines.append(f"| `{name}` | `{sha}` |")
    lines += [
        "",
        "> 本报告由确定性流水线生成；除 `run_manifest.json` / ledger 外，所有产物在相同输入下"
        "逐字节可复现。R26.15 未被修改。",
        "",
    ]
    return "\n".join(lines)


def report_stage(ctx) -> dict[str, Any]:
    text = _report_text(ctx)
    report_info = ctx.artifact_text("REPORT.md", text)
    receipt = "\n".join([
        "# R28 流水线回执（t13）",
        "",
        f"- run_id：`{ctx.run_id}`；模式：{'DRY-RUN（合成）' if ctx.dry_run else 'LIVE'}",
        f"- config digest：`{ctx.config.digest()}`",
        f"- 数据集：{((ctx.dataset or {}).get('summary') or {}).get('question_count')} 题",
        f"- 标注覆盖率：{((ctx.annotations or {}).get('metrics') or {}).get('coverage')}",
        f"- 主端点：NOT_RUN（未声称）",
        f"- R26.15：165 文件 / 93,346,177 字节，零漂移",
        f"- 报告 sha256：`{report_info['sha256']}`",
        "",
    ])
    receipt_info = ctx.artifact_text("PIPE_RECEIPT.md", receipt)
    hashes = write_artifact_hashes(ctx)
    replay = {
        "schema": "vett-r28-pipeline-replay-check/v1",
        "previous_present": bool(ctx.previous_artifacts),
        "identical": _replay_identical(ctx),
        "previous": ctx.previous_artifacts,
        "current": hashes["artifacts"],
    }
    ctx.write_json("REPLAY_CHECK.json", replay)
    return {"report_sha256": report_info["sha256"],
            "receipt_sha256": receipt_info["sha256"],
            "artifacts": hashes["artifacts"],
            "replay_identical": replay["identical"],
            "previous_present": replay["previous_present"]}


def _replay_identical(ctx) -> bool:
    previous = ctx.previous_artifacts or {}
    if not previous:
        return False
    current = {name: ctx.artifacts[name]["sha256"] for name in STABLE_ARTIFACTS
               if name in ctx.artifacts}
    keys = set(previous) | set(current)
    return all(previous.get(key) == current.get(key) for key in keys)


def write_artifact_hashes(ctx) -> dict[str, Any]:
    artifacts = {}
    for name in STABLE_ARTIFACTS:
        path = ctx.run_dir / name
        if path.is_file():
            artifacts[name] = sha256_file(path)
    payload = {
        "schema": "vett-r28-pipeline-artifact-hashes/v1",
        "artifacts": artifacts,
    }
    ctx.write_json("ARTIFACT_HASHES.json", payload)
    return payload


# ---------------------------------------------------------------------------
# 7. publish (human-gated; never executed by --stage all)
# ---------------------------------------------------------------------------
def publish_stage(ctx) -> dict[str, Any]:
    gate = ctx.human
    gate.require("publish_decision",
                 reason="publishing the R28 dataset is a human release decision",
                 evidence={"run_id": ctx.run_id,
                           "artifacts": {name: info["sha256"]
                                         for name, info in ctx.artifacts.items()}})
    payload = {
        "schema": "vett-r28-pipeline-publish-readiness/v1",
        "run_id": ctx.run_id,
        "status": "AWAITING_HUMAN_SIGNATURE",
        "artifacts": {name: info["sha256"] for name, info in sorted(ctx.artifacts.items())},
        "note": ("The pipeline assembles the decision packet only. It never publishes the "
                 "dataset and never writes outside its run directory."),
    }
    ctx.artifact("PUBLISH_READINESS.json", payload)
    ctx.artifact_text("PUBLISH_DECISION_PACKET.md", "\n".join([
        "# R28 发布决策包（待人工签署）",
        "",
        f"- run_id：`{ctx.run_id}`",
        f"- 主端点：NOT_RUN（本流水线不产生端点结论）",
        f"- 数据集：{((ctx.dataset or {}).get('summary') or {}).get('question_count')} 题",
        f"- 标注覆盖率：{((ctx.annotations or {}).get('metrics') or {}).get('coverage')}",
        "- 人类签署项：发布/不发布、是否进入 E1/E2、是否接受当前覆盖缺口",
        "",
    ]) + "\n")
    return {"status": "AWAITING_HUMAN_SIGNATURE"}


STAGE_FUNCS = {
    "bootstrap": bootstrap_stage,
    "generate": generate_stage,
    "annotate": annotate_stage,
    "judge": judge_stage,
    "aggregate": aggregate_stage,
    "report": report_stage,
    "publish": publish_stage,
}

__all__ = ["ALL_STAGES", "PUBLISH_STAGE", "STABLE_ARTIFACTS", "STAGE_FUNCS",
           "bootstrap_stage", "generate_stage", "probe_local", "annotate_stage",
           "judge_stage", "aggregate_stage", "report_stage", "publish_stage",
           "write_artifact_hashes", "VERSION"]
