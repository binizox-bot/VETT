#!/usr/bin/env python3
"""Export the R6 single-root pilot as readable Markdown artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_table(table: dict[str, Any]) -> str:
    columns = table["columns"]
    lines = [
        "| " + " | ".join(esc(c) for c in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend("| " + " | ".join(esc(row.get(c)) for c in columns) + " |" for row in table["rows"])
    return "\n".join(lines)


def table_heading(table: dict[str, Any]) -> str:
    suffix = f" — {table['innings_id']}" if table.get("innings_id") else ""
    return f"### {table['table_type']}{suffix}"


def pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, required=True)
    args = parser.parse_args()
    base = args.experiment_dir
    public = json.loads((base / "package/r6_single_public.json").read_text(encoding="utf-8"))
    private = json.loads((base / "package/r6_single_private_gold.json").read_text(encoding="utf-8"))
    selftest = json.loads((base / "R6_SINGLE_SELFTEST.json").read_text(encoding="utf-8"))
    source_audit = json.loads((base / "R6_SOURCE_EVENT_FEASIBILITY_AUDIT.json").read_text(encoding="utf-8"))
    solver_audit = json.loads((base / "R6_CANDIDATE_SOLVER_AUDIT.json").read_text(encoding="utf-8"))
    curated_root = json.loads(
        (base / f"construction/{private['root_id']}.r6_curated_root.json").read_text(encoding="utf-8")
    )
    ledger_validation = json.loads(
        (base / f"construction/{private['root_id']}.ledger_validation.json").read_text(encoding="utf-8")
    )

    public_parts = [
        "# R6 Single-Root Public Instance",
        "",
        f"Instance: `{public['instance_id']}`",
        "",
        public["instruction"],
        "",
        "## Commentary",
        "",
        public["document"]["text"],
        "",
        "## Blank scorecard",
        "",
    ]
    for table in public["tables"]:
        public_parts.extend([table_heading(table), "", render_table(table), ""])
    public_parts.extend(["## Output rule", "", public["output_rule"], ""])
    (base / "R6_SINGLE_PUBLIC.md").write_text("\n".join(public_parts), encoding="utf-8")

    gold_parts = [
        "# R6 Single-Root Private Gold",
        "",
        "Evaluation-only artifact. Do not expose this file to systems under test.",
        "",
        f"Root: `{private['root_id']}`; scored cells: {len(private['scored_cell_ids'])}; "
        f"challenge cells: {len(private['challenge_cell_ids'])}.",
        "",
    ]
    for table in private["gold_tables"]:
        gold_parts.extend([table_heading(table), "", render_table(table), ""])
    (base / "R6_SINGLE_PRIVATE_GOLD.md").write_text("\n".join(gold_parts), encoding="utf-8")

    ablations = selftest["controlled_ledger_ablations"]
    repeated = selftest["mechanical_checks"]["exact_repeated_sentences_ge8_words"]
    limitations_md = "\n".join(f"- {item}" for item in selftest["limitations"])
    selftest_md = f"""# R6 Single-Root Self-Test

Status: **{selftest['status']}**  
Decision: **{selftest['decision']}**

## Instance scale

| Measure | Value |
| --- | ---: |
| Public words | {selftest['public_words']} |
| Text segments | {selftest['segments']} |
| Atomic delivery events | {selftest['atomic_events']} |
| Scored cells | {selftest['scored_cells']} |
| Challenge cells | {selftest['challenge_cells']} |
| Challenge density | {pct(selftest['challenge_density'])} |
| Delayed corrections | {selftest['revisions']} |
| Stale graphics | {selftest['stale_graphics']} |
| Same-delivery replays | {selftest['same_delivery_replays']} |
| Correction delay | {selftest['revision_delay_segments']['min']}–{selftest['revision_delay_segments']['max']} segments |

## Integrity gates

| Gate | Result |
| --- | ---: |
| Ledger-to-scorecard checks | {ledger_validation['checks']}/{ledger_validation['checks']} correct |
| Ledger round-trip failures | {ledger_validation['failure_count']} |
| Public/private key leaks | {selftest['mechanical_checks']['public_private_key_leaks']} |
| Nonblank target violations | {selftest['mechanical_checks']['blank_target_violations']} |
| Evidence-span errors | {selftest['mechanical_checks']['evidence_span_errors']} |
| Scored cells without evidence | {selftest['mechanical_checks']['missing_scored_cell_evidence']} |
| Compact/meta-language hits | {sum(selftest['mechanical_checks']['compact_or_meta_hits'].values())} |
| Exact repeated sentences (>=8 words, >=3 copies) | {sum(1 for row in repeated if row['count'] >= 3)} |

## Controlled ledger ablations

| Condition | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | {ablations['event_oracle']['wrong']} / {ablations['event_oracle']['checks']} | {pct(ablations['event_oracle']['error_rate'])} |
| Trust provisional graphics | {ablations['trust_provisional_graphics']['wrong']} / {ablations['trust_provisional_graphics']['checks']} | {pct(ablations['trust_provisional_graphics']['error_rate'])} |
| Count same-delivery replays as new | {ablations['count_same_delivery_replays_as_new']['wrong']} / {ablations['count_same_delivery_replays_as_new']['checks']} | {pct(ablations['count_same_delivery_replays_as_new']['error_rate'])} |
| Combine both mistakes | {ablations['combined_provisional_and_replay_failure']['wrong']} / {ablations['combined_provisional_and_replay_failure']['checks']} | {pct(ablations['combined_provisional_and_replay_failure']['error_rate'])} |

These are deterministic error injections, not Direct, CoT, T3, or Map&Make model evaluations.

## Source feasibility

The source audit examined {source_audit['canonical_roots']} canonical roots and retained {source_audit['strict_event_reversible_roots']} rule-screen candidates. Ledger synthesis plus full round-trip validation retained {solver_audit['full_round_trip_pass_roots']} roots: {', '.join(solver_audit['full_round_trip_pass_ids'])}. The selected root removed {len(curated_root['r6_curation']['removed_rows'])} delivery-unobservable did-not-bat rows and {curated_root['r6_curation']['removed_cells']} corresponding cell records; the original source remains unchanged. The earlier `match_0096` engineering probe is excluded because its upstream cells are marked `BLOCKED_BY_CONFLICT`.

## Remaining limitations

{limitations_md}
"""
    (base / "R6_SINGLE_SELFTEST.md").write_text(selftest_md, encoding="utf-8")

    decision_md = f"""# R6 Small-Sample Advancement Decision

## Decision

Advance from one root to **two additional roots only**. Do not yet expand to all 220 matches.

The single-root pipeline now passes every mechanical gate: {ledger_validation['checks']}/{ledger_validation['checks']} ledger-to-table checks, zero target leakage, complete evidence coverage, and {pct(selftest['challenge_density'])} event-aggregation challenge density. The controlled combined mistake reaches {pct(ablations['combined_provisional_and_replay_failure']['error_rate'])}, showing that temporal revision and replay identity can propagate widely through a full scorecard. Of {solver_audit['rule_screen_candidates']} rule-screen candidates, only {solver_audit['full_round_trip_pass_roots']} passed ledger synthesis and exact validation; this is why expansion remains deliberately small.

## What this establishes

- A full scorecard can be reconstructed exactly from a machine-auditable atomic event ledger.
- Delayed correction, stale-display rejection, replay identity, aggregation, and derived-field calculation can coexist in one instance.
- Errors in event acceptance propagate across batting, bowling, extras, partnerships, fall-of-wickets, run rate, and team totals.

## What this does not establish

- It does not yet establish a T3, Map&Make, CoT, or Direct prompting error rate.
- It does not prove naturalness to independent annotators.
- It does not justify a claim that the full 220-match corpus is event-reversible.

## Two-root next gate

Construct two more instances with distinct discourse surfaces:

1. a radio-style narrative with delayed official scorer corrections and cross-over references;
2. a live-blog style narrative with quotations, replayed clips, and stale graphic collisions.

Each instance must independently satisfy:

- 100% ledger-to-table round-trip accuracy;
- zero public/private leakage and zero nonblank targets;
- at least 95% challenge-cell density;
- correction delay of at least eight segments;
- no exact sentence of eight or more words repeated three or more times;
- a documented source-curation record; and
- independent human checks for factual equivalence and naturalness before model evaluation.

Only after all three roots pass should blinded Direct, CoT, T3, and Map&Make evaluation begin. Model error is then reported at cell, row, table, and full-instance exact-match levels, with confidence intervals and failure-family annotations.
"""
    (base / "R6_SINGLE_DECISION.md").write_text(decision_md, encoding="utf-8")


if __name__ == "__main__":
    main()
