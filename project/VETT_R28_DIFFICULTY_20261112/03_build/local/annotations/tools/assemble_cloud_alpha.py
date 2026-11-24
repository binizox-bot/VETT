"""t16 (annotator_alpha): append hand-authored labels to the append-only judgment log.

The annotator authors labels in ``alpha_labels/*.json``; this tool
  * resolves each label row to its frozen packet/case (never editing it),
  * recomputes packet_sha and judge_config_sha from bytes,
  * enforces the record schema and the per-task label schema,
  * appends one JSON line per row to ``cloud_alpha.jsonl`` (idempotent: a packet_id
    already present is never rewritten, so the log is append-only by construction),
  * prints coverage against the frozen plan (T1=24, T2=16, T3=12) and the unsure tally.

Usage:  python tools/assemble_cloud_alpha.py [--check-only]
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKETS = ROOT / "packets"
LABELS = ROOT / "alpha_labels"
OUT = ROOT / "cloud_alpha.jsonl"
CONFIG = Path(__file__).resolve().parent / "judge_config.json"

SCHEMA_VER = "vett-annotation-record/v1"
PLAN = {"T1_factor_visibility": 48, "T2_naturalness": 16, "T3_adjudication": 12}
SUBPLAN = {"T1_r28_stratified": 24, "T1_local_arm_crosscheck": 24, "T2_r28_pairs": 16, "T3_adjudication": 12}
REQUIRED = ("schema_ver", "packet_id", "task", "judge_id", "labels", "rationale",
            "packet_sha", "judge_config_sha", "confidence", "unsure", "batch")
DIMENSIONS = ("fields", "span", "edge", "abstain", "conformance")


def canon(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_packets() -> dict[str, dict]:
    packets: dict[str, dict] = {}
    for name, task in (("T1_packets.jsonl", "T1_factor_visibility"),
                       ("T2_packets.jsonl", "T2_naturalness"),
                       ("T1_localarm_packets.jsonl", "T1_factor_visibility"),
                       ("T3_items.jsonl", "T3_adjudication")):
        path = PACKETS / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            key = row.get("packet_id") or row.get("submission_id")
            packets[key] = {"task": task, "row": row}
    return packets


def validate_labels(task: str, labels: dict) -> list[str]:
    problems: list[str] = []
    if task == "T1_factor_visibility":
        if set(labels) - {"supported", "evidence_phrase", "note"}:
            problems.append(f"T1 unexpected label keys {sorted(set(labels) - {'supported','evidence_phrase','note'})}")
        if not isinstance(labels.get("supported"), bool):
            problems.append("T1 labels.supported must be boolean")
    elif task == "T2_naturalness":
        for key in ("score_a", "score_b", "more_natural"):
            if key not in labels:
                problems.append(f"T2 missing {key}")
        for key in ("score_a", "score_b"):
            value = labels.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 5:
                problems.append(f"T2 {key} must be int in 1..5")
        if labels.get("more_natural") not in ("a", "b"):
            problems.append("T2 more_natural must be 'a' or 'b'")
    elif task == "T3_adjudication":
        for dimension in DIMENSIONS:
            block = labels.get(dimension)
            if not isinstance(block, dict) or block.get("verdict") not in ("PASS", "DEFECT", "UNSURE"):
                problems.append(f"T3 dimension {dimension} needs verdict PASS/DEFECT/UNSURE")
        if labels.get("overall") not in ("ACCEPT", "DEFECT", "UNSURE"):
            problems.append("T3 overall must be ACCEPT/DEFECT/UNSURE")
    return problems


def main(argv: list[str]) -> int:
    check_only = "--check-only" in argv
    packets = load_packets()
    config_sha = hashlib.sha256(CONFIG.read_bytes()).hexdigest()
    existing: dict[str, dict] = {}
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                existing[row["packet_id"]] = row

    problems: list[str] = []
    appended = 0
    label_files = sorted(LABELS.glob("*.json"))
    if not label_files:
        print("no label files yet")
    out_handle = None if check_only else OUT.open("a", encoding="utf-8", newline="\n")
    try:
        for path in label_files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            task = payload["task"]
            batch = int(payload["batch"])
            for row in payload["rows"]:
                key = row["id"]
                if key in existing:
                    continue                       # append-only: never rewrite history
                if key not in packets:
                    problems.append(f"{path.name}: unknown id {key}")
                    continue
                packet = packets[key]
                if packet["task"] != task:
                    problems.append(f"{key}: task mismatch {packet['task']} vs {task}")
                    continue
                labels = row["labels"]
                problems.extend(f"{key}: {p}" for p in validate_labels(task, labels))
                record = {
                    "schema_ver": SCHEMA_VER,
                    "packet_id": key,
                    "task": task,
                    "judge_id": "alpha",
                    "ruler": "cloud",
                    "template_version": json.loads(CONFIG.read_text(encoding="utf-8"))["task_templates"][task],
                    "labels": labels,
                    "confidence": float(row.get("confidence", 0.0)),
                    "unsure": bool(row.get("unsure", False)),
                    "rationale": str(row["rationale"]),
                    "packet_sha": sha(canon(packet["row"])),
                    "judge_config_sha": config_sha,
                    "batch": batch,
                    "label_source": path.name,
                    "labelled_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                missing = [field for field in REQUIRED if field not in record]
                if missing:
                    problems.append(f"{key}: record missing {missing}")
                    continue
                if len(record["rationale"].split()) < 5:
                    problems.append(f"{key}: rationale too thin")
                if out_handle is not None:
                    out_handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                existing[key] = record
                appended += 1
    finally:
        if out_handle is not None:
            out_handle.close()

    counts = Counter(row["task"] for row in existing.values())
    unsure = Counter(row["task"] for row in existing.values() if row["unsure"])
    coverage = {task: {"done": counts.get(task, 0), "planned": planned,
                       "pct": round(100.0 * counts.get(task, 0) / planned, 1)}
                for task, planned in PLAN.items()}
    report = {
        "appended_now": appended,
        "total_rows": len(existing),
        "coverage": coverage,
        "coverage_complete": all(counts.get(task, 0) == planned for task, planned in PLAN.items()),
        "subplan": SUBPLAN,
        "cloud_rows_vs_hard_cap": {"rows": len(existing), "hard_cap": 80},
        "unsure": dict(unsure),
        "judge_config_sha": config_sha,
        "schema_problems": problems,
        "schema_ok": not problems,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if not problems else 4


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

