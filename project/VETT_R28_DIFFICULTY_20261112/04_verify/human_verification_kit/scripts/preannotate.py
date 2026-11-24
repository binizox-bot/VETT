"""Pre-annotation candidate pack for the R28 human-verification kit.

The local model (t18: Ollama + qwen2.5:7b-instruct-q4_K_M) may only perform the
closed-form ALLOW tasks.  For gold verification that means it may **hint**
something about a span or a certificate sentence; it may **never** produce the
12-field record, a scope decision, a rule-version decision or a proof set.  The
R28 contract §10.10 forbids language models from generating facts / gold /
certificates, and a candidate derived from the solver would be circular anyway.

This pack therefore emits:

* ``S1_span_topic`` candidates (RUNS / DISMISSAL / BOWLING / IDENTITY) for public
  spans, so an annotator can find the span that talks about a field faster;
* optional ``T1_factor_visibility`` candidates (supported true/false) for the same
  spans, which are only triage hints;
* a deterministic lexicon fallback, always marked ``DEGRADED`` with reason
  ``RULE_BASELINE_ONLY``, so the pack is usable without the model and the coverage
  gap is explicit.

Every output line carries ``not_gold=true`` and ``usable_as_gold=false``.  A
candidate is editable, never authoritative, and never enters kappa or the gate.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

DEFAULT_LOCAL_DIR = os.path.join(common.run_root(), "03_build", "local")

TOPIC_PATTERNS = (
    ("RUNS", re.compile(r"\b(runs?|fours?|sixes?|score[sd]?|total|boundary|boundaries|partnership)\b", re.I)),
    ("DISMISSAL", re.compile(r"\b(dismissal|dismissed|wicket|caught|bowled|lbw|stumped|run[- ]out|not[- ]out|out)\b", re.I)),
    ("BOWLING", re.compile(r"\b(over|overs|maiden|wides?|no[- ]balls?|byes?|leg[- ]byes?|economy|bowling)\b", re.I)),
    ("IDENTITY", re.compile(r"\b(name|batter|bowler|player|identity|entered|register)\b", re.I)),
)


def _stub_topic(span_text: str) -> str | None:
    scores = {label: len(pattern.findall(span_text)) for label, pattern in TOPIC_PATTERNS}
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else None


def _stub_candidate(item_id: str, span: dict[str, Any], task: str) -> dict[str, Any]:
    topic = _stub_topic(span.get("text") or "")
    candidate = {"topic": topic} if task == "S1_span_topic" else {"supported": None}
    return {
        "item_id": item_id,
        "span_id": span["span_id"],
        "task": task,
        "candidate": candidate,
        "provenance": {
            "adapter": "stub_lexicon",
            "model_tag": None,
            "status": "DEGRADED",
            "reason_code": "RULE_BASELINE_ONLY",
            "reason": "deterministic lexicon hint; not a model call and not measured against mechanical truth",
            "template_version": "S1.span_topic.v4" if task == "S1_span_topic" else "T1.factor_visibility.v1",
        },
        "usable_as_gold": False,
        "not_gold": True,
        "editable": True,
        "note": "offline fallback; coverage counted as DEGRADED",
    }


def _load_local_api(local_dir: str):
    if local_dir not in sys.path:
        sys.path.insert(0, local_dir)
    try:
        from local_inference import api  # type: ignore

        return api
    except Exception as exc:  # pragma: no cover - exercised only when t18 is present
        raise common.KitError("LOCAL_IMPORT", f"cannot import local_inference from {local_dir}: {exc}")


def _local_candidate(api, item_id: str, span: dict[str, Any], task: str) -> dict[str, Any]:
    span_text = (span.get("text") or "")[:2400]
    sample = {"span_text": span_text} if task == "S1_span_topic" else {"passage": span_text}
    try:
        envelope = api.annotate(task, sample, caller="t24")
    except Exception as exc:  # fail safe: DEGRADED event, never a fabricated label
        return _degraded_candidate(item_id, span, task, "SERVICE_UNAVAILABLE", str(exc)[:300])
    status = envelope.get("status")
    if status == "OK":
        annotation = envelope.get("annotation") or {}
        candidate = {"topic": annotation.get("topic")} if task == "S1_span_topic" else {"supported": annotation.get("supported")}
        return {
            "item_id": item_id,
            "span_id": span["span_id"],
            "task": task,
            "candidate": candidate,
            "provenance": {
                "adapter": "local_inference",
                "model_tag": (envelope.get("ledger_entry") or {}).get("model_tag"),
                "status": "OK",
                "reason_code": None,
                "template_version": (envelope.get("ledger_entry") or {}).get("prompt_template_version"),
                "input_sha256": (envelope.get("ledger_entry") or {}).get("input_sha256"),
            },
            "usable_as_gold": False,
            "not_gold": True,
            "editable": True,
            "note": "local model hint; ALLOW only means agreement with mechanical truth on its own task, not correctness of gold",
        }
    degraded = envelope.get("degraded") or {}
    return _degraded_candidate(item_id, span, task, degraded.get("reason_code") or "DEGRADED", degraded.get("reason") or "")


def _degraded_candidate(item_id: str, span: dict[str, Any], task: str, reason_code: str, reason: str) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "span_id": span["span_id"],
        "task": task,
        "candidate": None,
        "provenance": {
            "adapter": "local_inference",
            "model_tag": None,
            "status": "DEGRADED",
            "reason_code": reason_code,
            "reason": reason[:400],
            "template_version": None,
        },
        "usable_as_gold": False,
        "not_gold": True,
        "editable": True,
        "note": "DEGRADED must be reported as a coverage gap; it is not silently dropped",
    }


def run(
    bundle_path: str,
    out_dir: str,
    adapter: str,
    local_dir: str,
    max_spans_per_item: int,
    tasks: list[str],
) -> dict[str, Any]:
    bundle = common.load_json(bundle_path)
    if bundle.get("kind") != "PUBLIC":
        raise common.KitError("PRE_BUNDLE", f"{bundle_path}: expected a PUBLIC bundle")
    api = None
    if adapter == "local":
        try:
            api = _load_local_api(local_dir)
        except common.KitError as exc:
            common.eprint(f"[preannotate] {exc}; every candidate will be DEGRADED")
            api = None
    lines: list[dict[str, Any]] = []
    coverage: dict[str, dict[str, int]] = {task: {"attempted": 0, "ok": 0, "degraded": 0} for task in tasks}
    reason_counts: dict[str, int] = {}
    for item in bundle.get("items", []):
        item_id = item["item_id"]
        spans = []
        for doc in item.get("documents") or []:
            for span in doc.get("spans") or []:
                spans.append(span)
        spans = spans[:max_spans_per_item]
        for task in tasks:
            for span in spans:
                coverage[task]["attempted"] += 1
                if adapter == "local" and api is not None:
                    row = _local_candidate(api, item_id, span, task)
                else:
                    row = _stub_candidate(item_id, span, task)
                row["schema"] = f"{common.SCHEMA_PREFIX}.preannotation.v1"
                row["kit_version"] = common.KIT_VERSION
                row["created_at_utc"] = common.utc_now()
                row["bundle_sha256"] = common.sha256_file(bundle_path)
                lines.append(row)
                status = row["provenance"]["status"]
                if status == "OK":
                    coverage[task]["ok"] += 1
                else:
                    coverage[task]["degraded"] += 1
                    code = row["provenance"].get("reason_code") or "UNKNOWN"
                    reason_counts[code] = reason_counts.get(code, 0) + 1
    common.ensure_dir(out_dir)
    out_path = os.path.join(out_dir, "preannotations.jsonl")
    common.write_jsonl(out_path, lines)
    report = {
        "schema": f"{common.SCHEMA_PREFIX}.preannotation_coverage.v1",
        "kit_version": common.KIT_VERSION,
        "generated_at_utc": common.utc_now(),
        "inputs": {"bundle": os.path.abspath(bundle_path), "bundle_sha256": common.sha256_file(bundle_path)},
        "adapter": adapter,
        "tasks": tasks,
        "n_lines": len(lines),
        "coverage": {
            task: {
                **counts,
                "ok_rate": round(counts["ok"] / counts["attempted"], 6) if counts["attempted"] else None,
            }
            for task, counts in coverage.items()
        },
        "degraded_reason_counts": reason_counts,
        "usable_as_gold": False,
        "not_gold": True,
        "policy": [
            "Candidates are hints only; they are editable and excluded from kappa and from the verification gates.",
            "The 12-field record is never pre-annotated: local model gold generation is forbidden by contract §10.10 and would be circular.",
            "DEGRADED is a coverage gap that must be reported, not silently dropped.",
            "No network and no paid provider API is used; the only model path is the local t18 service.",
        ],
        "output": os.path.abspath(out_path),
    }
    common.write_json(os.path.join(out_dir, "PREANNOTATION_COVERAGE.json"), report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="R28 pre-annotation candidate pack (hints only, never gold)")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--adapter", choices=("stub", "local"), default="stub")
    parser.add_argument("--local-dir", default=DEFAULT_LOCAL_DIR)
    parser.add_argument("--max-spans-per-item", type=int, default=40)
    parser.add_argument("--tasks", default="S1_span_topic", help="comma-separated: S1_span_topic,T1_factor_visibility")
    args = parser.parse_args(argv)
    tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]
    allowed = {"S1_span_topic", "T1_factor_visibility"}
    if not set(tasks) <= allowed:
        raise common.KitError("PRE_TASK", f"tasks must be a subset of {sorted(allowed)}")
    report = run(args.bundle, args.out_dir, args.adapter, args.local_dir, args.max_spans_per_item, tasks)
    print(
        common.canonical_json(
            {
                "n_lines": report["n_lines"],
                "adapter": report["adapter"],
                "coverage": report["coverage"],
                "usable_as_gold": report["usable_as_gold"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except common.KitError as exc:
        common.eprint(f"ERROR {exc}")
        raise SystemExit(4)
