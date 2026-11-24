"""Capability-matrix runner: measures each local task against mechanical truth.

Usage (from ``03_build/local``)::

    python -m local_inference matrix                # full 5-task matrix
    python -m local_inference matrix --pilot 6      # smoke subset (not gate-bearing)
    python -m local_inference matrix --no-cache     # force fresh model calls

The run is reproducible: samples are seeded, prompts are frozen, every actual
call is content-addressed in ``runs/cache.jsonl`` and every entry is written to
``cost_ledger.jsonl`` with the eight mandatory fields.  A second run with the
same seed hits the cache and reproduces ``summary_digest`` without GPU work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from pathlib import Path
from typing import Any

from . import config, corpus, ledger, policy, service, tasks

TASK_ORDER = tuple(config.DEFAULT_SAMPLE_SIZES)


# --------------------------------------------------------------------------
# content-addressed cache
# --------------------------------------------------------------------------
def prompt_cache_key(task_id: str, prompt: str, num_predict: int) -> str:
    spec = tasks.TASK_SPECS[task_id]
    basis = "|".join(
        [
            "vett-local-cache/v1",
            spec.template_version,
            config.MODEL_TAG,
            str(config.TEMPERATURE),
            str(config.SEED),
            str(config.NUM_CTX),
            str(num_predict),
            prompt,
        ]
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def load_cache(path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = path or config.CACHE_PATH
    cache: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return cache
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("cache_key") and isinstance(row.get("entry"), dict):
                cache[row["cache_key"]] = row["entry"]
    return cache


def append_cache(cache_key: str, entry: dict[str, Any], path: Path | None = None) -> None:
    path = path or config.CACHE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps({"cache_key": cache_key, "entry": entry}, ensure_ascii=False,
                       sort_keys=True, separators=(",", ":"))
            + "\n"
        )


def retest_cache_key(cache_key: str) -> str:
    return hashlib.sha256(f"retest|{cache_key}".encode("utf-8")).hexdigest()


def load_retest_cache(path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = path or config.RETEST_CACHE_PATH
    cache: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return cache
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("cache_key") and isinstance(row.get("entry"), dict):
                cache[row["cache_key"]] = row["entry"]
    return cache


def append_retest_cache(cache_key: str, entry: dict[str, Any], path: Path | None = None) -> None:
    path = path or config.RETEST_CACHE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps({"cache_key": cache_key, "entry": entry}, ensure_ascii=False,
                       sort_keys=True, separators=(",", ":"))
            + "\n"
        )


# --------------------------------------------------------------------------
# metric helpers
# --------------------------------------------------------------------------
def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 3)
    pos = (len(ordered) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return round(ordered[lo], 3)
    return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo), 3)


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None

    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(out):
            j = i
            while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
                j += 1
            rank = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                out[order[k]] = rank
            i = j + 1
        return out

    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return round(num / den, 4) if den else None


def _latency_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    # Wall clock is the original measured latency of exactly this prompt, so a
    # cache hit still carries valid latency evidence (flagged via n_cached).
    measured = [r["wall_clock"] for r in records if r["wall_clock"]]
    if not measured:
        return {"n": 0, "n_cached": 0, "mean": None, "p50": None, "p95": None,
                "max": None, "total_s": 0.0}
    return {
        "n": len(measured),
        "n_cached": sum(1 for r in records if r["cache_hit"] and r["wall_clock"]),
        "mean": round(statistics.fmean(measured), 3),
        "p50": _percentile(measured, 0.5),
        "p95": _percentile(measured, 0.95),
        "max": round(max(measured), 3),
        "total_s": round(sum(measured), 3),
    }


def _compact_truth(task_id: str, sample: dict[str, Any]) -> Any:
    if task_id == "T1_factor_visibility":
        return sample["truth_supported"]
    if task_id == "T2_naturalness":
        return sample["truth"]
    if task_id == "S1_span_topic":
        return sample["truth"]
    if task_id == "C1_cert_sentence_consistency":
        return sample["truth_consistent"]
    if task_id == "R1_readability":
        return {"band": sample["truth_band"], "fre": sample["truth_fre"]}
    return None


def task_metrics(
    task_id: str,
    records: list[dict[str, Any]],
    retest_records: list[dict[str, Any]],
    matrix_generated_at: str,
    *,
    mode: str,
) -> dict[str, Any]:
    spec = tasks.TASK_SPECS[task_id]
    attempted = len(records)
    complete = [r for r in records if r["ledger_complete"]]
    excluded = attempted - len(complete)
    usable = [r for r in complete if r["usable"]]
    correct = sum(1 for r in complete if r["score"]["correct"])
    agreement = round(correct / len(complete), 4) if complete else 0.0
    parse_failures = sum(1 for r in records if not r["parsed_ok"])
    transport_failures = sum(1 for r in records if not r["raw_output_present"])

    groups: dict[str, dict[str, Any]] = {}
    for record in complete:
        bucket = groups.setdefault(record["group"], {"n": 0, "correct": 0})
        bucket["n"] += 1
        bucket["correct"] += int(record["score"]["correct"])
    breakdown = {
        name: {"n": v["n"], "agreement": round(v["correct"] / v["n"], 4) if v["n"] else None}
        for name, v in sorted(groups.items())
    }

    latency = _latency_stats(records)
    gate_checks: dict[str, bool] = {
        "agreement_ge_threshold": agreement >= config.GATE_THRESHOLD,
        "samples_ge_30": len(complete) >= 30,
        "ledger_fields_complete": excluded == 0,
    }
    extra: dict[str, Any] = {}

    if task_id == "T2_naturalness":
        first_by_id = {r["sample_id"]: r for r in records}
        repeats = 0
        pairs = 0
        for second in retest_records:
            first = first_by_id.get(second["sample_id"])
            if not first or not first["parsed_ok"] or not second["parsed_ok"]:
                continue
            pairs += 1
            if (
                first["parsed"].get("score_a") == second["parsed"].get("score_a")
                and first["parsed"].get("score_b") == second["parsed"].get("score_b")
            ):
                repeats += 1
        repeat_rate = round(repeats / pairs, 4) if pairs else None
        extra = {"retest": {"pairs": pairs, "exact_repeat_rate": repeat_rate}}
        gate_checks["retest_repeat_ge_0.85"] = bool(repeat_rate is not None and repeat_rate >= 0.85)

    if task_id == "R1_readability":
        preds = [r["parsed"]["readability"] for r in complete if r["parsed_ok"]]
        truths = [int(r["sample"]["truth_band"]) for r in complete if r["parsed_ok"]]
        rho = _spearman([float(t) for t in truths], [float(p) for p in preds])
        distinct = len(set(preds))
        mean_by_band = {}
        for band in sorted(set(truths)):
            vals = [p for p, t in zip(preds, truths) if t == band]
            mean_by_band[str(band)] = round(statistics.fmean(vals), 3) if vals else None
        # require an actual monotone signal: lowest band mean < highest band mean
        bands = [b for b in sorted(mean_by_band) if mean_by_band[b] is not None]
        monotone = bool(
            len(bands) >= 2
            and mean_by_band[bands[0]] is not None
            and mean_by_band[bands[-1]] is not None
            and mean_by_band[bands[0]] < mean_by_band[bands[-1]]
        )
        discrimination_ok = bool(
            distinct >= config.R1_MIN_DISTINCT_SCORES
            and rho is not None
            and rho >= 0.3
            and monotone
        )
        exact = sum(1 for r in complete if r["parsed_ok"] and r["score"].get("exact"))
        extra = {
            "distinct_predicted_scores": distinct,
            "spearman_rho": rho,
            "mean_predicted_by_truth_band": mean_by_band,
            "monotone_band_ordering": monotone,
            "discrimination_ok": discrimination_ok,
            "exact_agreement": round(exact / len(complete), 4) if complete else 0.0,
            "tolerance": config.R1_AGREEMENT_TOLERANCE,
        }
        gate_checks["discrimination_ok"] = discrimination_ok

    if mode == "pilot":
        verdict = "PILOT"
        deny_reason = None
    else:
        verdict = "ALLOW" if all(gate_checks.values()) else "DENY"
        deny_reason = None
        if verdict == "DENY":
            failed = [k for k, ok in gate_checks.items() if not ok]
            detail = f"agreement {agreement:.3f} on n={len(complete)} (threshold {config.GATE_THRESHOLD})"
            if task_id == "T2_naturalness" and extra.get("retest", {}).get("exact_repeat_rate") is not None:
                detail += f"; retest repeat {extra['retest']['exact_repeat_rate']}"
            if task_id == "R1_readability":
                detail += f"; discrimination_ok={extra.get('discrimination_ok')} rho={extra.get('spearman_rho')}"
            deny_reason = f"{detail}; failed checks: {', '.join(failed)}"

    samples = [
        {
            "sample_id": r["sample_id"],
            "group": r["group"],
            "match": r.get("match"),
            "truth": r["truth_summary"],
            "predicted": r["score"].get("predicted"),
            "correct": bool(r["score"]["correct"]),
            "detail": r["score"].get("detail"),
            "parsed_ok": r["parsed_ok"],
            "wall_clock": r["wall_clock"],
            "cache_hit": r["cache_hit"],
            "input_sha256": r["input_sha256"],
            "cache_key": r["cache_key"],
        }
        for r in records
    ]
    samples_digest = hashlib.sha256(
        "".join(
            f"{s['sample_id']}:{s['input_sha256']}\n"
            for s in sorted(samples, key=lambda x: x["sample_id"])
        ).encode("utf-8")
    ).hexdigest()

    return {
        "task_id": task_id,
        "template_version": spec.template_version,
        "samples_digest": samples_digest,
        "template_version": spec.template_version,
        "gate_metric": spec.gate_metric,
        "threshold": config.GATE_THRESHOLD,
        "verdict": verdict,
        "deny_reason": deny_reason,
        "agreement": agreement,
        "n_requested": attempted,
        "n_attempted": attempted,
        "n_complete": len(complete),
        "n_scored": len(usable),
        "n_excluded_missing_fields": excluded,
        "n_correct": correct,
        "parse_failures": parse_failures,
        "parse_failure_rate": round(parse_failures / attempted, 4) if attempted else 1.0,
        "transport_failures": transport_failures,
        "breakdown": breakdown,
        "latency": latency,
        "gate_checks": gate_checks,
        "extra": extra,
        "matrix_generated_at": matrix_generated_at,
        "samples": samples,
    }


def _digest(task_metrics_map: dict[str, Any]) -> str:
    payload = {}
    for task_id, metrics in task_metrics_map.items():
        payload[task_id] = {
            "template_version": metrics.get("template_version"),
            "samples_digest": metrics.get("samples_digest"),
            "agreement": metrics["agreement"],
            "n_attempted": metrics["n_attempted"],
            "n_complete": metrics["n_complete"],
            "n_correct": metrics["n_correct"],
            "verdict": metrics["verdict"],
            "breakdown": metrics["breakdown"],
            "gate_checks": metrics["gate_checks"],
            "parse_failure_rate": metrics["parse_failure_rate"],
            # Continuous prediction diagnostics (e.g. R1 rho / band means) are
            # deliberately excluded: temperature=0 + fixed seed is not bitwise
            # deterministic across Ollama sessions (one 5-point score of 152 shifted
            # by 1 in an observed fresh run).  The digest covers the gate outcome,
            # agreement, per-group breakdown and sample set, which stayed identical.
            "retest": metrics["extra"].get("retest"),
        }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


# --------------------------------------------------------------------------
# main runner
# --------------------------------------------------------------------------
def run_matrix(
    *,
    seed: int = config.DEFAULT_SEED,
    pilot: int | None = None,
    task_filter: list[str] | None = None,
    use_cache: bool = True,
    cache_only: bool = False,
    write_run_dir: bool = True,
    out_path: Path | None = None,
    allow_low_vram: bool = False,
    quiet: bool = False,
) -> dict[str, Any]:
    def log(message: str) -> None:
        if not quiet:
            print(message, flush=True)

    if pilot is not None and out_path is None:
        out_path = config.LOCAL_ROOT / "capability_matrix_pilot.json"
    out_path = out_path or config.MATRIX_PATH
    mode = "pilot" if pilot is not None else "full"

    # 1) baseline integrity first: never measure against a mutated R26.15
    identity = corpus.dataset_identity()
    if not identity["tree"]["unchanged"]:
        raise RuntimeError(
            "R26.15 baseline integrity failure: tree aggregate/bytes/files differ from the "
            f"frozen values; refusing to run. got={identity['tree']}"
        )
    log(
        f"[matrix] R26.15 verified read-only: {identity['tree']['files']} files / "
        f"{identity['tree']['bytes']} bytes / aggregate {identity['tree']['tree_aggregate'][:16]}..."
    )

    # 2) service preflight and load (skipped for cache-only rebuilds)
    if cache_only:
        snapshot_path = config.SERVICE_SNAPSHOT_PATH
        if not snapshot_path.exists():
            raise RuntimeError("cache-only rebuild requires service_snapshot.json from the original run")
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        loaded = snapshot.get("loaded_model") or {}
        model = snapshot.get("model") or {}
        ollama_version = None
        for check in snapshot.get("checks") or []:
            if check.get("id") == "ollama_http_reachable":
                ollama_version = (check.get("detail") or {}).get("version")
        log("[matrix] cache-only rebuild: service preflight/load skipped, cache is mandatory")
    else:
        snapshot = service.preflight(allow_low_vram=allow_low_vram, require_gpu=True)
        loaded = service.ensure_loaded(num_ctx=config.NUM_CTX)
        snapshot["loaded_model"] = loaded
        snapshot["gpu_after_load"] = service.gpu_status()
        snapshot["warmed_at_utc"] = service.utc_now()
        service.write_snapshot(snapshot)
        model = snapshot["model"]
        ollama_version = None
        for check in snapshot["checks"]:
            if check["id"] == "ollama_http_reachable":
                ollama_version = (check.get("detail") or {}).get("version")
        log(
            f"[matrix] model={model['tag']} quant={model['quantization_level']} "
            f"digest={str(model['digest'])[:12]}... ollama={ollama_version} "
            f"gpu={snapshot['gpu'].get('name')} ps={loaded['gpu_percent']}%"
        )

    # 3) run
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    run_dir = config.RUNS_DIR / f"matrix_{run_id}_{mode}"
    if write_run_dir:
        run_dir.mkdir(parents=True, exist_ok=True)
    cache = load_cache() if use_cache else {}
    retest_cache = load_retest_cache() if use_cache else {}
    started_wall = time.time()
    tasks_to_run = [t for t in TASK_ORDER if not task_filter or t in task_filter]
    metrics_map: dict[str, dict[str, Any]] = {}
    vram_used_peak = 0
    vram_free_min: int | None = None
    gpu_residency: list[dict[str, Any]] = []
    total_actual_calls = 0
    total_cache_hits = 0
    total_failures = 0
    consecutive_failures = 0
    matrix_generated_at = service.utc_now()

    try:
        for task_id in tasks_to_run:
            spec = tasks.TASK_SPECS[task_id]
            n = pilot if pilot is not None else config.DEFAULT_SAMPLE_SIZES[task_id]
            samples = spec.build_samples(n, seed)
            records: list[dict[str, Any]] = []
            log(f"\n[matrix] === {task_id} ({spec.template_version}) n={len(samples)} ===")
            for index, sample in enumerate(samples, 1):
                prompt = tasks.build_prompt(task_id, sample)
                policy.enforce_input_cap(task_id, prompt)
                cache_key = prompt_cache_key(task_id, prompt, spec.num_predict)
                cache_hit = bool(use_cache and cache_key in cache)
                if cache_only and not cache_hit:
                    raise RuntimeError(f"cache-only rebuild: missing cache entry for {sample['sample_id']}")
                if cache_hit:
                    entry = cache[cache_key]
                else:
                    try:
                        call = service.generate(
                            prompt,
                            num_ctx=config.NUM_CTX,
                            num_predict=spec.num_predict,
                        )
                        parsed, parsed_ok, parse_error = spec.parse(call["raw_output"])
                        call["_num_predict"] = spec.num_predict
                        entry = ledger.build_entry(
                            task=task_id,
                            template_version=spec.template_version,
                            prompt=prompt,
                            raw_output=call["raw_output"],
                            parsed_output=parsed,
                            parsed_ok=parsed_ok,
                            wall_clock=call["wall_clock"],
                            call=call,
                            service_info=model,
                            error=parse_error,
                        )
                        consecutive_failures = 0
                    except service.LocalServiceError as exc:
                        entry = ledger.build_entry(
                            task=task_id,
                            template_version=spec.template_version,
                            prompt=prompt,
                            raw_output="",
                            parsed_output={"error": str(exc)},
                            parsed_ok=False,
                            wall_clock=0.0,
                            call={},
                            service_info=model,
                            error=str(exc),
                        )
                        consecutive_failures += 1
                        total_failures += 1
                        if consecutive_failures >= 5:
                            raise RuntimeError(
                                f"5 consecutive local-service failures; aborting matrix. last={exc}"
                            ) from exc
                    ledger.append_entry(entry)
                    if entry["raw_output"].strip():
                        append_cache(cache_key, entry)
                        cache[cache_key] = entry
                    total_actual_calls += 1
                if cache_hit:
                    total_cache_hits += 1

                parsed = entry.get("parsed_output")
                parsed_ok = bool(entry.get("parsed_ok"))
                score = spec.score(sample, parsed if isinstance(parsed, dict) else {},
                                   parsed_ok)
                complete = ledger.is_complete(entry)
                record = {
                    "sample_id": sample["sample_id"],
                    "group": sample["group"],
                    "match": sample.get("match"),
                    "sample": sample,
                    "truth_summary": _compact_truth(task_id, sample),
                    "input_sha256": entry.get("input_sha256"),
                    "cache_key": cache_key,
                    "cache_hit": cache_hit,
                    "parsed": parsed,
                    "parsed_ok": parsed_ok,
                    "score": score,
                    "wall_clock": float(entry.get("wall_clock") or 0.0),
                    "ledger_complete": complete,
                    "usable": ledger.is_usable(entry),
                    "raw_output_present": bool(str(entry.get("raw_output") or "").strip()),
                }
                records.append(record)

                gpu = service.gpu_status() if not cache_only else {"available": False}
                if gpu.get("available"):
                    vram_used_peak = max(vram_used_peak, int(gpu["memory_used_mib"]))
                    free = int(gpu["memory_free_mib"])
                    vram_free_min = free if vram_free_min is None else min(vram_free_min, free)
                if not quiet and (index % 10 == 0 or index == len(samples) or pilot):
                    status = "ok" if record["score"]["correct"] else "no"
                    log(
                        f"  [{index:>2}/{len(samples)}] {sample['sample_id']} "
                        f"{'cache' if cache_hit else f'{record['wall_clock']:.2f}s'} {status} "
                        f"parsed={parsed_ok}"
                    )

            # T2 retest validator: identical prompts, fresh calls (production cache bypassed;
            # cache-only rebuilds replay the stored retest entries).
            retest_records: list[dict[str, Any]] = []
            if task_id == "T2_naturalness" and mode == "full":
                retest_pool = samples[: config.T2_RETEST_PAIRS]
                if cache_only:
                    log(f"  [retest] replaying {len(retest_pool)} stored retest entries")
                else:
                    log(f"  [retest] re-issuing {len(retest_pool)} identical prompts (cache bypassed)")
                for sample in retest_pool:
                    prompt = tasks.build_prompt(task_id, sample)
                    cache_key = prompt_cache_key(task_id, prompt, spec.num_predict)
                    retest_key = retest_cache_key(cache_key)
                    if cache_only:
                        if retest_key not in retest_cache:
                            raise RuntimeError(
                                f"cache-only rebuild: missing retest cache entry for {sample['sample_id']}"
                            )
                        entry = retest_cache[retest_key]
                    else:
                        try:
                            call = service.generate(
                                prompt, num_ctx=config.NUM_CTX, num_predict=spec.num_predict
                            )
                            parsed, parsed_ok, parse_error = spec.parse(call["raw_output"])
                            call["_num_predict"] = spec.num_predict
                            entry = ledger.build_entry(
                                task=task_id,
                                template_version=spec.template_version,
                                prompt=prompt,
                                raw_output=call["raw_output"],
                                parsed_output=parsed,
                                parsed_ok=parsed_ok,
                                wall_clock=call["wall_clock"],
                                call=call,
                                service_info=model,
                                repeat_of=sample["sample_id"],
                                repeat_index=1,
                                error=parse_error,
                            )
                            total_actual_calls += 1
                        except service.LocalServiceError as exc:
                            entry = ledger.build_entry(
                                task=task_id,
                                template_version=spec.template_version,
                                prompt=prompt,
                                raw_output="",
                                parsed_output={"error": str(exc)},
                                parsed_ok=False,
                                wall_clock=0.0,
                                call={},
                                service_info=model,
                                repeat_of=sample["sample_id"],
                                repeat_index=1,
                                error=str(exc),
                            )
                            total_failures += 1
                        ledger.append_entry(entry)
                        append_retest_cache(retest_key, entry)
                        retest_cache[retest_key] = entry
                    parsed = entry.get("parsed_output")
                    parsed_ok = bool(entry.get("parsed_ok"))
                    retest_records.append(
                        {
                            "sample_id": sample["sample_id"],
                            "parsed": parsed,
                            "parsed_ok": parsed_ok,
                            "score": spec.score(sample, parsed, parsed_ok),
                            "wall_clock": float(entry.get("wall_clock") or 0.0),
                        }
                    )
                if write_run_dir:
                    (run_dir / f"{task_id}.retest.jsonl").write_text(
                        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in retest_records)
                        + ("\n" if retest_records else ""),
                        encoding="utf-8",
                        newline="\n",
                    )

            if write_run_dir:
                with open(run_dir / f"{task_id}.jsonl", "w", encoding="utf-8", newline="\n") as handle:
                    for record in records:
                        slim = {k: v for k, v in record.items() if k not in {"sample"}}
                        slim["prompt"] = tasks.build_prompt(task_id, record["sample"])
                        handle.write(json.dumps(slim, ensure_ascii=False, sort_keys=True) + "\n")

            metrics = task_metrics(
                task_id, records, retest_records, matrix_generated_at, mode=mode
            )
            metrics_map[task_id] = metrics
            log(
                f"  -> agreement={metrics['agreement']:.3f} n={metrics['n_complete']} "
                f"verdict={metrics['verdict']} p50={metrics['latency']['p50']}s "
                f"parse_fail={metrics['parse_failure_rate']:.2f}"
                + (f" retest={metrics['extra']['retest']['exact_repeat_rate']}"
                   if task_id == "T2_naturalness" else "")
                + (f" discrimination={metrics['extra']['discrimination_ok']}"
                   if task_id == "R1_readability" else "")
            )

            ps = service.ps_status() if not cache_only else None
            if ps:
                gpu_residency.append({"task": task_id, **ps})
                if ps["gpu_percent"] < 99.99:
                    gpu_residency[-1]["alert"] = "NOT_100_PERCENT_GPU"
    except Exception as exc:  # noqa: BLE001 - persist progress before propagating
        if write_run_dir:
            (run_dir / "ABORTED.json").write_text(
                json.dumps(
                    {
                        "error": f"{type(exc).__name__}: {exc}",
                        "completed_tasks": list(metrics_map),
                        "aborted_at_utc": service.utc_now(),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
        raise

    finished_wall = time.time()
    total_wall = round(finished_wall - started_wall, 3)
    residency_ok = all(item.get("gpu_percent", 0) >= 99.99 for item in gpu_residency) and bool(gpu_residency)
    matrix = {
        "schema_version": "vett-local-capability-matrix/v1",
        "generated_at": matrix_generated_at,
        "mode": mode,
        "gate": {
            "metric": config.GATE_METRIC,
            "threshold": config.GATE_THRESHOLD,
            "samples_per_task_min": 30,
            "notes": {
                "T2_naturalness": "primary = pairwise ordering (clean score > degraded score); tie counts wrong; retest exact-repeat must be >=0.85",
                "R1_readability": "primary = |predicted - FRE band| <= 1; anti-degenerate discrimination guard (>=3 distinct scores, Spearman rho >=0.3, monotone band means)",
                "missing_ledger_fields": "entries missing any of the eight mandatory fields are excluded from statistics and force the task verdict to DENY",
            },
        },
        "protocol": {
            "seed": seed,
            "sizes": {task: (pilot if pilot is not None else config.DEFAULT_SAMPLE_SIZES[task])
                      for task in tasks_to_run},
            "temperature": config.TEMPERATURE,
            "num_ctx": config.NUM_CTX,
            "num_predict": {task: tasks.TASK_SPECS[task].num_predict for task in tasks_to_run},
            "templates": {task: tasks.TASK_SPECS[task].template_version for task in tasks_to_run},
            "input_token_estimator": "ceil(utf8_bytes / 3.0) conservative pre-check; exact prompt_eval_count recorded per call",
            "input_caps": {task: tasks.TASK_SPECS[task].input_cap_tokens for task in tasks_to_run},
            "retest_pairs": config.T2_RETEST_PAIRS,
            "readability_tolerance": config.R1_AGREEMENT_TOLERANCE,
        },
        "dataset": identity,
        "service": {
            "model": model,
            "ollama_version": ollama_version,
            "gpu_name": snapshot["gpu"].get("name"),
            "gpu_memory_total_mib": snapshot["gpu"].get("memory_total_mib"),
            "loaded_model": loaded,
            "parameters": {
                "temperature": config.TEMPERATURE,
                "seed": config.SEED,
                "num_ctx": config.NUM_CTX,
                "keep_alive": config.KEEP_ALIVE,
                "timeout_s": config.TIMEOUT_S,
                "retries": config.RETRIES,
            },
        },
        "tasks": metrics_map,
        "overall": {
            "wall_clock_s": total_wall,
            "actual_model_calls": total_actual_calls,
            "cache_hits": total_cache_hits,
            "calls_per_minute": round(total_actual_calls / total_wall * 60, 2) if total_wall else None,
            "failures": total_failures,
            "vram_used_peak_mib": vram_used_peak or None,
            "vram_free_min_mib": vram_free_min,
            "gpu_residency_ok": residency_ok,
            "gpu_residency": gpu_residency,
            "cost_cny": 0.0,
        },
        "summary_digest": _digest(metrics_map),
        "mode_note": (
            "PILOT ONLY - not gate-bearing; routing card must be built from a full matrix"
            if mode == "pilot"
            else "gate-bearing full matrix"
        ),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    tmp_path.replace(out_path)

    run_meta = {
        "schema_version": "vett-local-matrix-run/v1",
        "run_id": run_id,
        "mode": mode,
        "started_at_utc": matrix_generated_at,
        "finished_at_utc": service.utc_now(),
        "out_path": str(out_path),
        "summary_digest": matrix["summary_digest"],
        "overall": matrix["overall"],
        "args": {
            "seed": seed,
            "pilot": pilot,
            "tasks": tasks_to_run,
            "use_cache": use_cache,
            "cache_only": cache_only,
            "allow_low_vram": allow_low_vram,
        },
    }
    if write_run_dir:
        (run_dir / "run_meta.json").write_text(
            json.dumps(run_meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    log(
        f"\n[matrix] done: {total_actual_calls} calls, {total_cache_hits} cache hits, "
        f"{total_failures} failures, {total_wall:.1f}s, {matrix['overall']['calls_per_minute']} calls/min, "
        f"VRAM peak={vram_used_peak} MiB free_min={vram_free_min} MiB gpu_ok={residency_ok}"
    )
    log(f"[matrix] digest={matrix['summary_digest']}")
    log(f"[matrix] wrote {out_path}")
    return matrix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local capability matrix")
    parser.add_argument("--pilot", type=int, default=None,
                        help="run only N samples/task into capability_matrix_pilot.json")
    parser.add_argument("--tasks", nargs="+", default=None, choices=list(TASK_ORDER))
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-only", action="store_true",
                        help="rebuild metrics from cached outputs only (reproducibility check)")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--allow-low-vram", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    matrix = run_matrix(
        seed=args.seed,
        pilot=args.pilot,
        task_filter=args.tasks,
        use_cache=not args.no_cache,
        cache_only=args.cache_only,
        out_path=args.out,
        allow_low_vram=args.allow_low_vram,
        quiet=args.quiet,
    )
    for task_id, metrics in matrix["tasks"].items():
        print(f"{task_id:<32} {metrics['verdict']:<6} agreement={metrics['agreement']:.3f} "
              f"n={metrics['n_complete']:<3} p50={metrics['latency']['p50']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
