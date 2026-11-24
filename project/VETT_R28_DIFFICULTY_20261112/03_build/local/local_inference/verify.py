"""Independent consistency checks for the local-inference service (t18 acceptance).

Run: ``python -m local_inference verify``

Verifies, in order:
  1. capability matrix present, gate-bearing, internally consistent, digest stable
  2. dataset identity unchanged since the matrix was produced
  3. routing card equals the card regenerated from the current code
  4. every ALLOW verdict has measured agreement >= 0.85 on >= 30 samples
  5. runtime assertions match the card (ALLOW runs, DENY raises, caps raise)
  6. DENY reasons cite the measured 40K / 80K / confidence evidence
  7. cost ledger is complete (eight mandatory fields), zero-cost, frozen params
  8. every matrix prompt is cached (content-addressed) and ledgered
  9. the matrix rebuilds from cache alone with an identical summary digest
 10. the DEGRADED interface behaves for static DENY / unmeasured / below-gate /
     over-cap / service-down / parse-failure / success paths
 11. service snapshot records model tag, quantization digest and 100% GPU
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from . import config, corpus, degrade, ledger, matrix, policy, service, tasks


def _check(check_id: str, ok: bool, detail: Any) -> dict[str, Any]:
    return {"id": check_id, "ok": bool(ok), "detail": detail}


def _canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# --------------------------------------------------------------------------
# self-test of the DEGRADED interface (no GPU calls)
# --------------------------------------------------------------------------
def run_selftest() -> dict[str, Any]:
    sandbox = config.SELFTEST_DIR
    sandbox.mkdir(parents=True, exist_ok=True)
    events_path = sandbox / "DEGRADED_EVENTS.jsonl"
    ledger_path = sandbox / "cost_ledger.jsonl"
    for path in (events_path, ledger_path):
        if path.exists():
            path.unlink()

    allow_matrix = {
        "generated_at": "selftest",
        "tasks": {
            "T1_factor_visibility": {
                "verdict": "ALLOW", "agreement": 0.93, "n_attempted": 30,
                "threshold": 0.85, "gate_metric": "agreement_with_mechanical_truth",
                "parse_failure_rate": 0.0,
            }
        },
    }
    sample = {
        "sample_id": "selftest-T1",
        "group": "POS_OVERRIDE",
        "truth_supported": True,
        "match": "selftest",
        "passage": "The desk issued N1 against N2: the seventh row now carries \"7\".",
    }
    info = {"digest": "selftest", "quantization_level": "Q4_K_M"}

    results: list[dict[str, Any]] = []

    def run_case(name: str, fn: Callable[[], dict[str, Any]],
                 expected_status: str, expected_reason: str | None) -> None:
        try:
            envelope = fn()
            status = envelope.get("status")
            reason = (envelope.get("degraded") or {}).get("reason_code")
            ok = status == expected_status and (expected_reason is None or reason == expected_reason)
            results.append({"case": name, "ok": ok, "status": status, "reason_code": reason,
                            "expected_status": expected_status,
                            "expected_reason_code": expected_reason})
        except Exception as exc:  # noqa: BLE001 - selftest must record any failure
            results.append({"case": name, "ok": False, "error": f"{type(exc).__name__}: {exc}",
                            "expected_status": expected_status,
                            "expected_reason_code": expected_reason})

    from . import api

    run_case(
        "static_deny_12_field_derivation",
        lambda: api.annotate("D1_12_field_record_derivation", {}, caller="selftest",
                             matrix=allow_matrix, degraded_path=events_path,
                             service_info=info, ledger_path=ledger_path),
        "DEGRADED", "MEASURED_BELOW_PRIOR",
    )
    run_case(
        "unmeasured_task_denied",
        lambda: api.annotate("T1_factor_visibility", sample, caller="selftest",
                             matrix={}, degraded_path=events_path,
                             service_info=info, ledger_path=ledger_path),
        "DEGRADED", "CAPABILITY_UNMEASURED",
    )
    below_matrix = {
        "tasks": {
            "T1_factor_visibility": {
                "verdict": "DENY", "agreement": 0.42, "n_attempted": 30,
                "deny_reason": "selftest: agreement 0.42 < 0.85",
            }
        }
    }
    run_case(
        "below_gate_denied",
        lambda: api.annotate("T1_factor_visibility", sample, caller="selftest",
                             matrix=below_matrix, degraded_path=events_path,
                             service_info=info, ledger_path=ledger_path),
        "DEGRADED", "CAPABILITY_BELOW_THRESHOLD",
    )
    run_case(
        "input_cap_exceeded",
        lambda: api.annotate("T1_factor_visibility",
                             {**sample, "passage": "x" * 12000}, caller="selftest",
                             matrix=allow_matrix, degraded_path=events_path,
                             service_info=info, ledger_path=ledger_path),
        "DEGRADED", "INPUT_CAP_EXCEEDED",
    )
    run_case(
        "missing_input",
        lambda: api.annotate("T1_factor_visibility", {"sample_id": "x"}, caller="selftest",
                             matrix=allow_matrix, degraded_path=events_path,
                             service_info=info, ledger_path=ledger_path),
        "DEGRADED", "NO_INPUT",
    )

    original_generate = service.generate

    def unavailable(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise service.LocalServiceError("selftest: ollama down")

    try:
        service.generate = unavailable  # type: ignore[assignment]
        run_case(
            "service_unavailable",
            lambda: api.annotate("T1_factor_visibility", sample, caller="selftest",
                                 matrix=allow_matrix, degraded_path=events_path,
                                 service_info=info, ledger_path=ledger_path),
            "DEGRADED", "SERVICE_UNAVAILABLE",
        )
    finally:
        service.generate = original_generate

    def bad_json(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "raw_output": "this is not json", "wall_clock": 0.01,
            "prompt_eval_count": 12, "eval_count": 2, "attempt_count": 1,
            "attempts": [], "done_reason": "stop", "context_length": config.NUM_CTX,
            "total_duration_s": 0.01, "load_duration_s": 0.0,
        }

    try:
        service.generate = bad_json  # type: ignore[assignment]
        run_case(
            "parse_failure",
            lambda: api.annotate("T1_factor_visibility", sample, caller="selftest",
                                 matrix=allow_matrix, degraded_path=events_path,
                                 service_info=info, ledger_path=ledger_path),
            "DEGRADED", "PARSE_FAILURE",
        )
    finally:
        service.generate = original_generate

    def good_json(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "raw_output": '{"supported": true, "evidence": "the seventh row now carries"}',
            "wall_clock": 0.02,
            "prompt_eval_count": 30, "eval_count": 12, "attempt_count": 1,
            "attempts": [], "done_reason": "stop", "context_length": config.NUM_CTX,
            "total_duration_s": 0.02, "load_duration_s": 0.0,
        }

    try:
        service.generate = good_json  # type: ignore[assignment]
        run_case(
            "success_path_ledgered",
            lambda: api.annotate("T1_factor_visibility", sample, caller="selftest",
                                 matrix=allow_matrix, degraded_path=events_path,
                                 service_info=info, ledger_path=ledger_path),
            "OK", None,
        )
    finally:
        service.generate = original_generate

    events = degrade.load_events(events_path)
    sandbox_ledger = ledger.validate_file(ledger_path)
    ok = all(case["ok"] for case in results) and sandbox_ledger["ok"] and len(events) >= 6
    result = {
        "ok": ok,
        "cases": results,
        "event_count": len(events),
        "event_reason_codes": sorted({e["reason_code"] for e in events}),
        "degraded_events_path": str(events_path),
        "sandbox_ledger": sandbox_ledger,
    }
    (sandbox / "selftest_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def run_checks(*, rebuild: bool = True) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    matrix_data = policy.load_matrix()

    # 1-2) matrix presence and dataset identity ------------------------------
    if matrix_data is None:
        checks.append(_check("matrix_present", False, "capability_matrix.json missing"))
        checks.append(_check("matrix_dataset_unchanged", False, "no matrix"))
        checks.append(_check("matrix_gate_consistent", False, "no matrix"))
        checks.append(_check("matrix_digest_stable", False, "no matrix"))
        checks.append(_check("dataset_still_unchanged", False, "no matrix"))
    else:
        checks.append(_check("matrix_present", matrix_data.get("mode") == "full",
                             {"mode": matrix_data.get("mode"),
                              "generated_at": matrix_data.get("generated_at")}))
        tree = (matrix_data.get("dataset") or {}).get("tree") or {}
        checks.append(_check("matrix_dataset_unchanged", bool(tree.get("unchanged")),
                             {"files": tree.get("files"), "bytes": tree.get("bytes"),
                              "tree_aggregate": tree.get("tree_aggregate")}))
        current_tree = corpus.tree_aggregate_v1()
        checks.append(_check("dataset_still_unchanged", bool(current_tree["unchanged"]),
                             current_tree))
        task_problems = []
        for task_id, metrics in (matrix_data.get("tasks") or {}).items():
            if metrics.get("n_complete", 0) < 30:
                task_problems.append(f"{task_id}: n={metrics.get('n_complete')} < 30")
            gates = metrics.get("gate_checks") or {}
            expected = "ALLOW" if all(gates.values()) else "DENY"
            if metrics.get("verdict") != expected:
                task_problems.append(
                    f"{task_id}: verdict {metrics.get('verdict')} != recomputed {expected}"
                )
            if metrics.get("verdict") == "ALLOW" and metrics.get("agreement", 0) < config.GATE_THRESHOLD:
                task_problems.append(f"{task_id}: ALLOW below threshold")
            if metrics.get("verdict") == "DENY" and not metrics.get("deny_reason"):
                task_problems.append(f"{task_id}: DENY without reason")
            if metrics.get("n_excluded_missing_fields", 0):
                task_problems.append(f"{task_id}: {metrics['n_excluded_missing_fields']} entries missing ledger fields")
        checks.append(_check("matrix_gate_consistent", not task_problems, task_problems))
        recomputed_digest = matrix._digest(matrix_data.get("tasks") or {})
        checks.append(_check(
            "matrix_digest_stable",
            recomputed_digest == matrix_data.get("summary_digest"),
            {"stored": matrix_data.get("summary_digest"), "recomputed": recomputed_digest},
        ))

    # 3-4) routing card ----------------------------------------------------
    card = None
    if config.ROUTING_CARD_PATH.exists():
        card = json.loads(config.ROUTING_CARD_PATH.read_text(encoding="utf-8"))
    if matrix_data is None or card is None:
        checks.append(_check("routing_card_present", False, "card or matrix missing"))
        checks.append(_check("routing_card_matches_code", False, "card or matrix missing"))
        checks.append(_check("routing_task_set", False, "card or matrix missing"))
        checks.append(_check("routing_allow_measured", False, "card or matrix missing"))
    else:
        checks.append(_check("routing_card_present", True,
                             {"generated_at": card.get("generated_at"),
                              "tasks": len(card.get("tasks") or {})}))
        rebuilt = policy.build_routing_card(matrix_data)
        stored_cmp = json.loads(json.dumps(card))
        rebuilt_cmp = json.loads(json.dumps(rebuilt))
        stored_cmp.pop("generated_at", None)
        rebuilt_cmp.pop("generated_at", None)
        checks.append(_check(
            "routing_card_matches_code",
            _canonical(stored_cmp) == _canonical(rebuilt_cmp),
            {"stored_sha": service.sha256_text(_canonical(stored_cmp))[:16],
             "rebuilt_sha": service.sha256_text(_canonical(rebuilt_cmp))[:16]},
        ))
        expected_tasks = set(tasks.TASK_SPECS) | set(policy.DENY_ROUTES)
        actual_tasks = set((card.get("tasks") or {}).keys())
        checks.append(_check("routing_task_set", expected_tasks == actual_tasks,
                             {"missing": sorted(expected_tasks - actual_tasks),
                              "extra": sorted(actual_tasks - expected_tasks)}))
        problems = []
        for task_id, spec in tasks.TASK_SPECS.items():
            entry = (card.get("tasks") or {}).get(task_id) or {}
            measured = (entry.get("measured") or {}).get("agreement")
            if entry.get("verdict") == "ALLOW":
                if measured is None or measured < config.GATE_THRESHOLD:
                    problems.append(f"{task_id}: ALLOW with agreement {measured}")
                if (matrix_data.get("tasks") or {}).get(task_id, {}).get("verdict") != "ALLOW":
                    problems.append(f"{task_id}: card ALLOW but matrix not ALLOW")
            if entry.get("input_cap_tokens") != spec.input_cap_tokens:
                problems.append(f"{task_id}: cap mismatch")
            if entry.get("prompt_template_version") != spec.template_version:
                problems.append(f"{task_id}: template version mismatch")
        checks.append(_check("routing_allow_measured", not problems, problems))

    # 5) DENY reasons cite measured evidence -------------------------------
    if card is None:
        checks.append(_check("deny_reasons_cite_evidence", False, "no card"))
    else:
        deny_problems = []
        tasks_card = card.get("tasks") or {}
        for task_id, entry in tasks_card.items():
            if entry.get("verdict") != "DENY":
                continue
            if not entry.get("deny_reason") or not entry.get("reason_code"):
                deny_problems.append(f"{task_id}: empty reason/reason_code")
        evidence_blob = _canonical(tasks_card) + _canonical(card.get("deny_evidence"))
        for token in ("4.20/9", "4.77/9", "60.53", "17.7", "8192"):
            if token not in evidence_blob:
                deny_problems.append(f"missing measured evidence token {token}")
        checks.append(_check("deny_reasons_cite_evidence", not deny_problems, deny_problems))

    # 6) runtime assertions vs card ----------------------------------------
    runtime_problems: list[str] = []
    if card is not None:
        for task_id, entry in (card.get("tasks") or {}).items():
            try:
                policy.assert_allowed(task_id, "x")
                allowed = True
            except service.TaskDenied:
                allowed = False
            except service.InputCapExceeded as exc:
                runtime_problems.append(f"{task_id}: tiny prompt rejected by cap: {exc}")
                allowed = None
            if entry.get("verdict") == "ALLOW" and allowed is not True:
                runtime_problems.append(f"{task_id}: card ALLOW but assert_allowed did not permit")
            if entry.get("verdict") == "DENY" and allowed is not False:
                runtime_problems.append(f"{task_id}: card DENY but assert_allowed permitted")
        allow_tasks = [t for t, e in (card.get("tasks") or {}).items() if e.get("verdict") == "ALLOW"]
        for task_id in allow_tasks:
            cap = tasks.TASK_SPECS[task_id].input_cap_tokens
            try:
                policy.assert_allowed(task_id, "x" * (cap * 3 + 3))
                runtime_problems.append(f"{task_id}: over-cap prompt accepted")
            except service.InputCapExceeded:
                pass
        if allow_tasks:
            probe = allow_tasks[0]
            try:
                policy.assert_allowed(probe, "x" * (config.NUM_CTX * 3 + 30))
                runtime_problems.append("hard 8K ceiling not enforced")
            except service.InputCapExceeded as exc:
                if exc.cap != config.NUM_CTX:
                    runtime_problems.append(f"hard ceiling raised with cap {exc.cap} != {config.NUM_CTX}")
        for task_id in policy.DENY_ROUTES:
            try:
                policy.assert_allowed(task_id, "x")
                runtime_problems.append(f"{task_id}: DENY route permitted")
            except service.TaskDenied:
                pass
        if any(spec.input_cap_tokens > config.NUM_CTX for spec in tasks.TASK_SPECS.values()):
            runtime_problems.append("a task cap exceeds the hard 8K ceiling")
        checks.append(_check("runtime_assertions_match_card", not runtime_problems, runtime_problems))

    # 7-8) ledger completeness and coverage --------------------------------
    ledger_report = ledger.validate_file()
    checks.append(_check("ledger_fields_complete", ledger_report["ok"], ledger_report))
    entries = ledger.load_entries()
    param_problems = []
    for entry in entries:
        if entry.get("schema_version") == "CORRUPT":
            param_problems.append(f"corrupt line {entry.get('_line')}")
            continue
        if entry.get("temperature") != config.TEMPERATURE:
            param_problems.append("temperature drift")
        if entry.get("seed") != config.SEED:
            param_problems.append("seed drift")
        if entry.get("model_tag") != config.MODEL_TAG:
            param_problems.append(f"model drift {entry.get('model_tag')}")
        if float(entry.get("cost_cny") or 0.0) != 0.0:
            param_problems.append("non-zero cost")
    checks.append(_check("ledger_frozen_parameters", not param_problems,
                         sorted(set(param_problems))))

    if card is not None:
        cache = matrix.load_cache()
        ledger_shas = {e.get("input_sha256") for e in entries}
        coverage_problems = []
        for task_id, entry in (card.get("tasks") or {}).items():
            if entry.get("verdict") != "ALLOW":
                continue
            samples = ((matrix_data or {}).get("tasks", {}).get(task_id, {}) or {}).get("samples") or []
            for sample in samples:
                if sample.get("cache_key") not in cache:
                    coverage_problems.append(f"{task_id}/{sample.get('sample_id')}: no cache entry")
                if sample.get("input_sha256") not in ledger_shas:
                    coverage_problems.append(f"{task_id}/{sample.get('sample_id')}: not in ledger")
        checks.append(_check("matrix_prompts_cached_and_ledgered", not coverage_problems,
                             coverage_problems[:20]))
    else:
        checks.append(_check("matrix_prompts_cached_and_ledgered", False, "no card"))

    # 9) cache-only rebuild -------------------------------------------------
    if rebuild and matrix_data is not None:
        rebuild_path = config.RUNS_DIR / "verify" / "capability_matrix_rebuild.json"
        try:
            rebuilt_matrix = matrix.run_matrix(
                cache_only=True, write_run_dir=False, out_path=rebuild_path, quiet=True
            )
            same = rebuilt_matrix["summary_digest"] == matrix_data.get("summary_digest")
            checks.append(_check(
                "matrix_rebuild_from_cache_identical",
                same,
                {"stored": matrix_data.get("summary_digest"),
                 "rebuilt": rebuilt_matrix["summary_digest"],
                 "rebuild_path": str(rebuild_path)},
            ))
        except Exception as exc:  # noqa: BLE001 - report failure, don't crash the verifier
            checks.append(_check("matrix_rebuild_from_cache_identical", False,
                                 f"{type(exc).__name__}: {exc}"))
    else:
        checks.append(_check("matrix_rebuild_from_cache_identical", False,
                             "rebuild skipped"))

    # 10) degradation interface self-test ----------------------------------
    selftest = run_selftest()
    checks.append(_check("degraded_interface_selftest", selftest["ok"], {
        "cases": selftest["cases"],
        "reason_codes": selftest["event_reason_codes"],
        "events": selftest["degraded_events_path"],
    }))

    # 11) service snapshot --------------------------------------------------
    snapshot_path = config.SERVICE_SNAPSHOT_PATH
    if snapshot_path.exists():
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        model = snapshot.get("model") or {}
        loaded = snapshot.get("loaded_model") or {}
        ok = bool(model.get("tag") and model.get("digest") and model.get("quantization_level")
                  and loaded.get("gpu_percent") == 100.0)
        checks.append(_check("service_snapshot_recorded", ok, {
            "model": model,
            "loaded_gpu_percent": loaded.get("gpu_percent"),
            "gpu": snapshot.get("gpu"),
            "path": str(snapshot_path),
        }))
    else:
        checks.append(_check("service_snapshot_recorded", False, "service_snapshot.json missing"))

    failed = [c for c in checks if not c["ok"]]
    result = {
        "schema_version": "vett-local-verify/v1",
        "checked_at_utc": service.utc_now(),
        "ok": not failed,
        "n_checks": len(checks),
        "n_passed": len(checks) - len(failed),
        "n_failed": len(failed),
        "checks": checks,
    }
    out_dir = config.RUNS_DIR / "verify"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "verify_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Verify local-inference artifacts")
    parser.add_argument("--no-rebuild", action="store_true",
                        help="skip the cache-only matrix rebuild check")
    args = parser.parse_args(argv)
    result = run_checks(rebuild=not args.no_rebuild)
    for check in result["checks"]:
        mark = "PASS" if check["ok"] else "FAIL"
        print(f"[{mark}] {check['id']}")
        if not check["ok"]:
            print(f"       {json.dumps(check['detail'], ensure_ascii=False)[:600]}")
    print(f"\n{result['n_passed']}/{result['n_checks']} checks passed")
    print(f"wrote {config.RUNS_DIR / 'verify' / 'verify_result.json'}")
    return 0 if result["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
