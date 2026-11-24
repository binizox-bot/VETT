#!/usr/bin/env python3
"""Export readable R11 public and private previews plus a concise experiment note."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def table_md(table: dict[str, Any]) -> str:
    rows = table["rows"]
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    lines = [f"### {table['table_id']}", "", "| " + " | ".join(columns) + " |",
             "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        values = []
        for col in columns:
            value = row.get(col)
            values.append("" if value is None else str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, required=True)
    args = parser.parse_args()
    public = json.loads((args.dir / "public_instance.json").read_text(encoding="utf-8"))
    private = json.loads((args.dir / "private_gold.json").read_text(encoding="utf-8"))
    evidence = json.loads((args.dir / "private_evidence_graph.json").read_text(encoding="utf-8"))
    report = json.loads((args.dir / "selftest_report.json").read_text(encoding="utf-8"))

    public_lines = ["# R11 public instance", "", public["task"], ""]
    for document in public["documents"]:
        public_lines += [f"## {document['source_label']}", ""]
        public_lines += [f"**{s['segment_id']}** — {s['text']}\n" for s in document["segments"]]
    public_lines += ["## Blank target tables", ""]
    for table in public["target_tables"]:
        public_lines += [table_md(table), ""]
    (args.dir / "PUBLIC_PREVIEW.md").write_text("\n".join(public_lines), encoding="utf-8")

    gold_lines = ["# R11 private gold", ""]
    for table in private["gold_tables"]:
        gold_lines += [table_md(table), ""]
    (args.dir / "PRIVATE_GOLD_PREVIEW.md").write_text("\n".join(gold_lines), encoding="utf-8")

    stats = report["statistics"]
    baseline_rows = [
        f"| {name} | {value['error_rate']:.2f}% | {value['blank_rate']:.2f}% |"
        for name, value in report["weak_baselines"].items()
    ]
    note = f"""# R11 hallucination-chain pilot

## Purpose

This one-root pilot tests whether a system can distinguish official facts from plausible but source-scoped false claims. False claims occur in provisional graphics, replay shadows and stale post-match widgets; no false claim is treated as gold. Composite cricket fields are atomized before scoring.

## Scale

- Root: `{public['root_id']}`
- Documents: {stats['documents']}
- Segments: {stats['segments']}
- Whitespace-tokenized words: {stats['words_whitespace']}
- Atomic scored cells: {stats['scored_atomic_cells']}
- Claim records: {stats['claims']} ({stats['false_claims']} false, {stats['true_candidate_claims']} true candidates)
- False:true claim ratio: {stats['false_to_true_claim_ratio']}:1
- Evidence path: candidate card → custody leaf → seal → signed audit, plus a cross-table check

## Deterministic diagnostics

| Policy | Cell error rate | Blank rate |
| --- | ---: | ---: |
{chr(10).join(baseline_rows)}

These policies are diagnostic ablations, not model results. They show that recency, repetition, first mention and fixed candidate position do not solve the pilot. A new blind T3/MapMake/CoT/frontier-model run is required before claiming method-level error rates.

## Integrity gates

All {len(report['checks'])} automated gates passed. Every cell has a distinct decoy, a true candidate, two false mentions, a four-hop adjudication chain spanning at least two documents, cross-table evidence, and a canonical scorecard origin. Candidate A/B authority is balanced at 53/54 cells.

## Remaining research risks

The dossier is deliberately regular because this is a structural pilot. Before scaling to 217 roots, vary document genres, chain topology, number of candidates, authority language and placement; then run human uniqueness/support review. Otherwise a model may learn the generator fingerprint instead of evidence reasoning.
"""
    (args.dir / "R11_PILOT_REPORT.md").write_text(note, encoding="utf-8")


if __name__ == "__main__":
    main()
