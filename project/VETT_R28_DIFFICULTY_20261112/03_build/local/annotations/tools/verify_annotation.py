"""t16 (annotator_alpha): independent audit of the cloud annotation artefacts.

Checks, in order:
  1. schema: every row in cloud_alpha.jsonl carries the required fields, judge_id=alpha,
     a non-empty rationale, and a packet_sha that recomputes from the frozen packet;
  2. coverage: T1 24 / T2 16 / T3 12, no duplicates, no missing task;
  3. blindness: every T1/T2 packet re-audits clean through judge_protocol.audit_packet,
     no packet text contains an item id (r28q_), a path, or a forbidden key;
  4. budgets: token_estimate within the routing-card caps (T1 3000 / T2 6000);
  5. T3 inputs carry no gold: no private_gold / certificate / decision_record_flat key.
Prints a JSON report and exits 0 only if every check passes.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_ROOT = ROOT.parents[2]
sys.path.insert(0, str(RUN_ROOT / "02_design" / "scripts"))
import judge_protocol as jp  # noqa: E402

PACKETS = ROOT / "packets"
PLAN = {"T1_factor_visibility": 48, "T2_naturalness": 16, "T3_adjudication": 12}
REQUIRED = ("schema_ver", "packet_id", "task", "judge_id", "labels", "rationale",
            "packet_sha", "judge_config_sha", "confidence", "unsure", "batch",
            "template_version", "ruler")
FORBIDDEN_TEXT = (re.compile(r"r28q_\d{4}"), re.compile(r"[A-Za-z]:\\"), re.compile(r"private_gold"))


def canon(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    problems: list[str] = []
    packets = {}
    for name in ("T1_packets.jsonl", "T1_localarm_packets.jsonl", "T2_packets.jsonl", "T3_items.jsonl"):
        for line in (PACKETS / name).read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                packets[row.get("packet_id") or row.get("submission_id")] = row

    rows = [json.loads(line) for line in (ROOT / "cloud_alpha.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = Counter(row["packet_id"] for row in rows)
    for key, count in seen.items():
        if count > 1:
            problems.append(f"duplicate row {key} x{count}")

    for row in rows:
        for field in REQUIRED:
            if field not in row:
                problems.append(f"{row.get('packet_id')}: missing {field}")
        if row.get("judge_id") != "alpha":
            problems.append(f"{row['packet_id']}: judge_id != alpha")
        if len(str(row.get("rationale") or "").split()) < 5:
            problems.append(f"{row['packet_id']}: rationale too short")
        packet = packets.get(row["packet_id"])
        if packet is None:
            problems.append(f"{row['packet_id']}: packet not found")
            continue
        if sha(canon(packet)) != row["packet_sha"]:
            problems.append(f"{row['packet_id']}: packet_sha mismatch")
        if not re.fullmatch(r"[0-9a-f]{64}", row["judge_config_sha"]):
            problems.append(f"{row['packet_id']}: judge_config_sha malformed")

    coverage = {task: sum(1 for row in rows if row["task"] == task) for task in PLAN}
    for task, planned in PLAN.items():
        if coverage[task] != planned:
            problems.append(f"coverage {task}: {coverage[task]} != {planned}")

    # blindness / budget / gold audit
    packet_checks = []
    for name, cap in (("T1_packets.jsonl", 3000), ("T1_localarm_packets.jsonl", 3000), ("T2_packets.jsonl", 6000)):
        for line in (PACKETS / name).read_text(encoding="utf-8").splitlines():
            packet = json.loads(line)
            violations = jp.audit_packet(packet)
            if violations:
                problems.append(f"{packet['packet_id']}: audit violations {violations}")
            if packet["token_estimate"] > cap:
                problems.append(f"{packet['packet_id']}: {packet['token_estimate']} > cap {cap}")
            text = canon(packet)
            for pattern in FORBIDDEN_TEXT:
                if pattern.search(text):
                    problems.append(f"{packet['packet_id']}: forbidden text {pattern.pattern}")
            packet_checks.append({"packet_id": packet["packet_id"], "task": packet["task"],
                                  "tokens": packet["token_estimate"],
                                  "contains_answer": packet["contains_answer"]})

    gold_keys = {"private_gold", "certificate", "decision_record_flat", "gold", "decision_answers"}
    for line in (PACKETS / "T3_items.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        found = gold_keys & set(row)
        if found:
            problems.append(f"{row['submission_id']}: gold keys {sorted(found)}")
        if any(p.search(canon(row)) for p in (re.compile(r"private_gold"), re.compile(r"[A-Za-z]:\\"))):
            problems.append(f"{row['submission_id']}: forbidden text in T3 input")

    report = {
        "rows": len(rows),
        "coverage": coverage,
        "coverage_complete": all(coverage[t] == PLAN[t] for t in PLAN),
        "unsure": sum(1 for row in rows if row["unsure"]),
        "packets_audited": len(packet_checks),
        "max_tokens": {"T1": max(c["tokens"] for c in packet_checks if c["task"] == "T1_factor_visibility"),
                       "T2": max(c["tokens"] for c in packet_checks if c["task"] == "T2_naturalness")},
        "schema_problems": problems,
        "ok": not problems,
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if not problems else 4


if __name__ == "__main__":
    raise SystemExit(main())

