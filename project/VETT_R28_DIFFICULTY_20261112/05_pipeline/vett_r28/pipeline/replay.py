"""Byte-level replay verifier: recompute metrics from persisted ``raw_output``.

Replay is **not** regeneration.  It re-parses stored model text and recomputes
every metric from that text; it never calls the model.  R28 measured that
``temperature=0`` + fixed seed is *not* bitwise deterministic across Ollama
sessions (1 of 152 scores moved by 1 point, verdicts unchanged), so a claim that
re-running the model reproduces the same bytes is explicitly forbidden.

Usage::

    python -m vett_r28.pipeline.replay \
        --ledger runs/<run>/local_cost_ledger.jsonl \
        --annotations runs/<run>/annotations.json \
        --judge runs/<run>/judge.json \
        --out runs/<run>/REPLAY_REPORT.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

from .canonical import canon, sha256_text

DEFAULT_NONDETERMINISM = (
    pathlib.Path(__file__).resolve().parents[2].parent
    / "03_build" / "local" / "runs" / "repro" / "nondeterminism_evidence.json"
)


def load_jsonl(path: pathlib.Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _tasks_module(local_root: pathlib.Path):
    root = str(local_root)
    if root not in sys.path:
        sys.path.insert(0, root)
    from local_inference import tasks as local_tasks  # type: ignore

    return local_tasks


def reparse_entry(entry: dict[str, Any], tasks_module) -> dict[str, Any]:
    task = str(entry.get("task"))
    raw = entry.get("raw_output")
    spec = tasks_module.TASK_SPECS.get(task)
    if spec is None:
        return {"task": task, "skipped": True, "ok": False,
                "error": f"no parser for task {task} (not part of the main path)",
                "parsed": None, "raw_output_sha256": sha256_text(str(raw))}
    parsed, parsed_ok, parse_error = spec.parse(str(raw or ""))
    return {
        "task": task,
        "skipped": False,
        "ok": bool(parsed_ok),
        "parsed": parsed,
        "error": parse_error,
        "raw_output_sha256": sha256_text(str(raw or "")),
    }


def _ledger_map(entries: list[dict[str, Any]]) -> dict[tuple, dict[str, Any]]:
    out: dict[tuple, dict[str, Any]] = {}
    for entry in entries:
        if not entry.get("task") or not entry.get("input_sha256"):
            continue
        key = (str(entry["task"]), str(entry["input_sha256"]), entry.get("repeat_index", 0))
        out[key] = entry
    return out


def _annotation_rows(path: pathlib.Path) -> tuple[list[dict[str, Any]], str]:
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        return rows, "jsonl_rows"
    if isinstance(payload, dict) and "records" in payload:
        return list(payload["records"]), "pipeline_annotations"
    if isinstance(payload, list):
        return payload, "jsonl_rows"
    raise ValueError(f"unsupported annotations file: {path}")


def _task_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_task: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_task.setdefault(str(row["task"]), []).append(row)
    metrics: dict[str, Any] = {}
    for task, items in sorted(by_task.items()):
        ok_rows = [row for row in items if str(row.get("status", "OK")) == "OK"]
        comparable_total = 0
        comparable_ok = 0
        for row in ok_rows:
            annotation = row.get("annotation") or row.get("parsed_output") or {}
            if task == "T1_factor_visibility":
                comparable_total += 1
                comparable_ok += int(bool(annotation.get("supported")) is True)
            elif task == "C1_cert_sentence_consistency":
                comparable_total += 1
                comparable_ok += int(bool(annotation.get("consistent")) is True)
        metrics[task] = {
            "n": len(items),
            "ok": len(ok_rows),
            "degraded": len(items) - len(ok_rows),
            "comparable_total": comparable_total,
            "comparable_ok": comparable_ok,
            "comparable_degraded": 0,
            "agreement_rate": round(comparable_ok / comparable_total, 6)
            if comparable_total else None,
        }
    return metrics


def replay(*, ledger_paths: list[pathlib.Path], local_root: pathlib.Path,
           annotations_paths: list[pathlib.Path] | None = None,
           judge_path: pathlib.Path | None = None,
           nondeterminism_path: pathlib.Path | None = None,
           expect_t1: float | None = None) -> dict[str, Any]:
    tasks_module = _tasks_module(local_root)
    ledger: list[dict[str, Any]] = []
    for path in ledger_paths:
        ledger.extend(load_jsonl(path))
    mapping = _ledger_map(ledger)

    # 1) re-parse every ledger row from its stored raw_output
    reparse_rows = []
    parse_mismatches = []
    skipped_no_parser: dict[str, int] = {}
    for entry in ledger:
        result = reparse_entry(entry, tasks_module)
        if result.get("skipped"):
            task = str(result["task"])
            skipped_no_parser[task] = skipped_no_parser.get(task, 0) + 1
            continue
        stored = entry.get("parsed_output")
        identical = result["parsed"] == stored
        reparse_rows.append({"task": result["task"], "ok": identical,
                             "parsed_ok": result["ok"],
                             "input_sha256": entry.get("input_sha256"),
                             "raw_output_sha256": result["raw_output_sha256"],
                             "template": entry.get("prompt_template_version")})
        if not identical:
            parse_mismatches.append({"task": result["task"],
                                     "input_sha256": entry.get("input_sha256"),
                                     "replayed": result["parsed"],
                                     "stored": stored,
                                     "error": result["error"]})
    template_counts: dict[str, int] = {}
    for row in ledger:
        template = str(row.get("prompt_template_version"))
        template_counts[template] = template_counts.get(template, 0) + 1

    # 2) compare replayed annotations with the persisted annotation artefact
    annotation_checks = []
    annotation_mismatches = []
    metric_rows: list[dict[str, Any]] = []
    sources = []
    for path in annotations_paths or []:
        rows, kind = _annotation_rows(path)
        sources.append({"path": str(path), "kind": kind, "rows": len(rows)})
        for row in rows:
            task = str(row.get("task"))
            key = row.get("prompt_sha256") or row.get("input_sha256")
            entry = mapping.get((task, str(key), row.get("repeat_index", 0))) \
                or mapping.get((task, str(key), 0)) \
                or mapping.get((task, str(key), None))
            stored_annotation = row.get("annotation") or row.get("parsed_output")
            metric_rows.append({
                "task": task,
                "status": row.get("status", "OK"),
                "annotation": row.get("parsed_output") if kind == "jsonl_rows" else row.get("annotation"),
                "mechanical": (row.get("mechanical")
                               or ({"truth": row.get("mechanical_truth")}
                                   if "mechanical_truth" in row else {})),
            })
            if entry is None:
                source = str(row.get("source") or "")
                if row.get("cache_hit") or "mechanical" in source.lower():
                    # No model call happened (cache hit or mechanical fallback):
                    # nothing to replay for this row, counted separately.
                    annotation_checks.append({"task": task, "input_sha256": key,
                                              "matched": None,
                                              "reason": "no model call (cache/mechanical)"})
                    continue
                annotation_checks.append({"task": task, "input_sha256": key,
                                          "matched": False, "reason": "ledger row not found"})
                annotation_mismatches.append({"task": task, "input_sha256": key,
                                              "reason": "ledger row not found"})
                continue
            replay_result = reparse_entry(entry, tasks_module)
            if replay_result.get("skipped"):
                annotation_checks.append({"task": task, "input_sha256": key,
                                          "matched": None,
                                          "reason": "no parser for task (non-main-path row)"})
                continue
            replayed = replay_result["parsed"]
            if isinstance(stored_annotation, dict) and isinstance(replayed, dict):
                parser_keys = set(replayed)
                missing = [name for name in parser_keys if name not in stored_annotation]
                identical = (not missing
                             and {name: stored_annotation.get(name) for name in parser_keys}
                             == replayed)
            else:
                identical = replayed == stored_annotation
            annotation_checks.append({"task": task, "input_sha256": key,
                                      "matched": identical})
            if not identical:
                annotation_mismatches.append({
                    "task": task, "input_sha256": key,
                    "replayed": replay_result["parsed"],
                    "stored": stored_annotation,
                })
    metrics = _task_metrics(metric_rows) if metric_rows else {}

    # 3) compare recomputed metrics with the persisted judge artefact
    judge_comparison: dict[str, Any] = {"present": False}
    if judge_path and judge_path.is_file():
        judged = json.loads(judge_path.read_text(encoding="utf-8"))
        stored_tasks = judged.get("tasks") or {}
        compared = {
            task: {
                "stored": stored_tasks.get(task),
                "replayed": metrics.get(task),
                "identical": stored_tasks.get(task) == metrics.get(task),
            }
            for task in sorted(set(stored_tasks) | set(metrics))
        }
        judge_comparison = {
            "present": True,
            "path": str(judge_path),
            "tasks": compared,
            "identical": all(row["identical"] for row in compared.values()),
        }

    # 4) T1 agreement cross-check (t14 real labels)
    t1_rows = [row for row in metric_rows if row["task"] == "T1_factor_visibility"]
    t1_correct = 0
    for row in t1_rows:
        annotation = row.get("annotation") or {}
        truth = (row.get("mechanical") or {}).get("truth")
        if truth is None:
            continue
        t1_correct += int(bool(annotation.get("supported")) == bool(truth))
    t1_metric = None
    if t1_rows:
        t1_metric = {
            "n": len(t1_rows),
            "correct": t1_correct,
            "agreement": round(t1_correct / len(t1_rows), 6),
            "expected": expect_t1,
            "matches_expected": (expect_t1 is None
                                 or abs(t1_correct / len(t1_rows) - expect_t1) < 1e-9),
        }

    nondeterminism = None
    nd_path = nondeterminism_path or DEFAULT_NONDETERMINISM
    if nd_path.is_file():
        nd = json.loads(nd_path.read_text(encoding="utf-8"))
        nondeterminism = {
            "path": str(nd_path),
            "n_samples_compared": nd.get("n_samples_compared"),
            "n_prediction_diffs": nd.get("n_prediction_diffs"),
            "temperature": nd.get("temperature"),
            "note": nd.get("note"),
        }

    all_identical = (not parse_mismatches
                     and not annotation_mismatches
                     and (not judge_comparison.get("present")
                          or judge_comparison.get("identical"))
                     and (t1_metric is None or t1_metric["matches_expected"]))
    report = {
        "schema": "vett-r28-pipeline-replay-report/v1",
        "replay_basis": "persisted raw_output (never re-generated)",
        "regenerated_model_output": False,
        "model_calls_during_replay": 0,
        "ledger_rows": len(ledger),
        "reparse_ok": len(reparse_rows) - len(parse_mismatches),
        "reparse_mismatched": len(parse_mismatches),
        "skipped_no_parser": skipped_no_parser,
        "parsed_ok_rows": sum(1 for row in reparse_rows if row.get("parsed_ok")),
        "parse_failed_rows": sum(1 for row in reparse_rows if not row.get("parsed_ok")),
        "parse_mismatches": parse_mismatches[:20],
        "templates": template_counts,
        "annotations_sources": sources,
        "annotations_checked": len(annotation_checks),
        "annotations_matched": sum(1 for row in annotation_checks if row["matched"] is True),
        "annotations_cached_skipped": sum(1 for row in annotation_checks
                                          if row["matched"] is None),
        "annotations_mismatched": len(annotation_mismatches),
        "annotation_mismatches": annotation_mismatches[:20],
        "recomputed_metrics": metrics,
        "judge_comparison": judge_comparison,
        "t1_metric": t1_metric,
        "nondeterminism_evidence": nondeterminism,
        "all_identical": bool(all_identical),
        "statement": (
            "Replay re-parses stored raw_output and recomputes metrics without calling the "
            "model. It is not regeneration: R28 measured one 5-point score of 152 moving by "
            "1 across runs at temperature=0, so re-running the model is not claimed to "
            "reproduce the same bytes."
        ),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m vett_r28.pipeline.replay")
    parser.add_argument("--ledger", action="append", required=True,
                        help="ledger JSONL containing raw_output (repeatable)")
    parser.add_argument("--annotations", action="append", default=None,
                        help="annotations file (pipeline annotations.json or t14 JSONL)")
    parser.add_argument("--judge", default=None, help="judge.json to compare recomputed metrics")
    parser.add_argument("--local-root", default=None,
                        help="03_build/local (defaults to the pipeline config location)")
    parser.add_argument("--nondeterminism", default=None,
                        help="nondeterminism_evidence.json path")
    parser.add_argument("--expect-t1", type=float, default=None,
                        help="expected T1 agreement (e.g. 0.975)")
    parser.add_argument("--out", required=True, help="output REPLAY_REPORT.json")
    args = parser.parse_args(argv)
    pipe_root = pathlib.Path(__file__).resolve().parents[2]
    local_root = pathlib.Path(args.local_root) if args.local_root else (
        pipe_root.parent / "03_build" / "local")
    report = replay(
        ledger_paths=[pathlib.Path(item) for item in args.ledger],
        local_root=local_root,
        annotations_paths=[pathlib.Path(item) for item in (args.annotations or [])],
        judge_path=pathlib.Path(args.judge) if args.judge else None,
        nondeterminism_path=pathlib.Path(args.nondeterminism) if args.nondeterminism else None,
        expect_t1=args.expect_t1,
    )
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps({
        "ledger_rows": report["ledger_rows"],
        "reparse_mismatched": report["reparse_mismatched"],
        "annotations_mismatched": report["annotations_mismatched"],
        "judge_identical": report["judge_comparison"].get("identical"),
        "all_identical": report["all_identical"],
        "out": str(out),
    }, ensure_ascii=False, sort_keys=True))
    return 0 if report["all_identical"] else 1


if __name__ == "__main__":
    sys.exit(main())
