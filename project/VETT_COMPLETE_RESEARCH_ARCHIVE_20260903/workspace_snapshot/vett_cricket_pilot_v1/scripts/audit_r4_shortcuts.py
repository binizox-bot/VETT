#!/usr/bin/env python3
"""Red-team audit for construction traces and evaluation shortcuts in R4."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


PATTERNS = {
    "construction_state_language": (
        r"\b(?:candidate|branch|reconstruction|admissible state|accepted component|"
        r"surviving graph)\b"
    ),
    "constraint_meta_language": (
        r"\b(?:constraint|conserve|conservation|intersection|one-owner rule|"
        r"terminal register)\b"
    ),
    "answer_withholding_disclaimer": (
        r"\b(?:no final number|does not print|no completed scorecard|"
        r"without publishing target values|no compact score row)\b"
    ),
    "synthetic_registry_jargon": (
        r"\b(?:mirror node|event fingerprint|delivery signature|event signature|"
        r"scoring node)\b"
    ),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = read_jsonl(args.blind)
    failures: list[dict[str, Any]] = []
    unique_roots: dict[str, dict[str, Any]] = {}
    text_groups: dict[str, list[str]] = defaultdict(list)

    for row in rows:
        root_id = row["instance_id"].split(".", 1)[0]
        unique_roots.setdefault(root_id, row)
        full_text = "\n".join(doc["text"] for doc in row["documents"])
        text_groups[sha256_text(full_text)].append(row["instance_id"])

    duplicate_groups = [ids for ids in text_groups.values() if len(ids) > 1]
    if duplicate_groups:
        failures.append({
            "check": "same_source_packet_repeated_across_scoring_tracks",
            "severity": "critical",
            "groups": duplicate_groups,
        })

    pattern_counts: dict[str, int] = defaultdict(int)
    per_root: list[dict[str, Any]] = []
    for root_id, row in sorted(unique_roots.items()):
        # The first document is the inherited R3 broadcast; later documents are R4 additions.
        overlay = "\n".join(doc["text"] for doc in row["documents"][1:])
        counts = {
            name: len(re.findall(pattern, overlay, flags=re.I))
            for name, pattern in PATTERNS.items()
        }
        for name, count in counts.items():
            pattern_counts[name] += count
        per_root.append({"root_id": root_id, "overlay_pattern_counts": counts})

    for name, count in sorted(pattern_counts.items()):
        if count:
            failures.append({
                "check": name,
                "severity": "major",
                "unique_root_hits": count,
            })

    instruction_leak_instances = []
    for row in rows:
        instruction = row.get("instruction", "")
        if re.search(r"two locally coherent event assignments|resolve the accepted match state jointly", instruction, re.I):
            instruction_leak_instances.append(row["instance_id"])
    if instruction_leak_instances:
        failures.append({
            "check": "task_instruction_reveals_latent_construction",
            "severity": "critical",
            "instances": instruction_leak_instances,
        })

    if all(row["instance_id"].endswith(("R4S", "R4C")) for row in rows):
        failures.append({
            "check": "instance_id_exposes_scoring_track",
            "severity": "major",
            "instances": len(rows),
        })

    query_only = all("queries" in row and "tables" not in row for row in rows)
    if query_only:
        failures.append({
            "check": "cell_query_task_substituted_for_full_text_to_table_generation",
            "severity": "critical",
            "instances": len(rows),
        })

    report = {
        "audit_version": "0.1",
        "status": "FAIL" if failures else "PASS",
        "decision": "REJECT_R4_AS_RELEASE_BENCHMARK_RETAIN_AS_MECHANISM_PROBE",
        "instances": len(rows),
        "unique_roots": len(unique_roots),
        "duplicate_text_groups": duplicate_groups,
        "pattern_counts_on_unique_overlays": dict(sorted(pattern_counts.items())),
        "per_root": per_root,
        "failures": failures,
        "r5_mandatory_gates": [
            "Generic task instruction contains no latent-state or reasoning-method hints.",
            "No construction-state, constraint-meta, or answer-withholding language in public text.",
            "One source packet is generated once and scored on all cells; scoring slices do not become duplicate instances.",
            "Primary task is full fixed-schema table generation; cell queries are diagnostic views only.",
            "All train/dev/test splits are grouped by match root and generation family.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": len(failures)}, indent=2))


if __name__ == "__main__":
    main()
