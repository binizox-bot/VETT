#!/usr/bin/env python3
"""Export the R8 third-root pilot, audit, and three-root comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from export_r6_single_readable import pct, render_table, table_heading


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--third-dir", type=Path, required=True)
    parser.add_argument("--r6-selftest", type=Path, required=True)
    parser.add_argument("--r7-selftest", type=Path, required=True)
    args = parser.parse_args()
    base = args.third_dir
    package = base / "package"
    public = json.loads((package / "r8_third_public.json").read_text(encoding="utf-8"))
    private = json.loads((package / "r8_third_private_gold.json").read_text(encoding="utf-8"))
    evidence = json.loads((package / "r8_third_private_evidence.json").read_text(encoding="utf-8"))
    r8 = json.loads((base / "selftest/r8_selftest.json").read_text(encoding="utf-8"))
    r6 = json.loads(args.r6_selftest.read_text(encoding="utf-8"))
    r7 = json.loads(args.r7_selftest.read_text(encoding="utf-8"))
    root = json.loads((base / "construction/match_0122.r8_curated_root.json").read_text(encoding="utf-8"))

    public_parts = [
        "# R8 Third-Root Public Instance", "", f"Instance: `{public['instance_id']}`", "",
        public["instruction"], "", "## Dual-feed radio transcript", "",
        public["document"]["text"], "", "## Blank scorecard", "",
    ]
    for table in public["tables"]:
        public_parts.extend([table_heading(table), "", render_table(table), ""])
    public_parts.extend(["## Output rule", "", public["output_rule"], ""])
    (base / "R8_THIRD_PUBLIC.md").write_text("\n".join(public_parts), encoding="utf-8")

    gold_parts = [
        "# R8 Third-Root Private Gold", "",
        "Evaluation-only artifact. Do not expose this file to systems under test.", "",
        f"Root: `{private['root_id']}`; scored cells: {len(private['scored_cell_ids'])}; "
        f"challenge cells: {len(private['challenge_cell_ids'])}.", "",
    ]
    for table in private["gold_tables"]:
        gold_parts.extend([table_heading(table), "", render_table(table), ""])
    (base / "R8_THIRD_PRIVATE_GOLD.md").write_text("\n".join(gold_parts), encoding="utf-8")

    ab = r8["controlled_ledger_ablations"]
    limitations = "\n".join(f"- {item}" for item in r8["limitations"])
    report = f"""# R8 Third-Root Self-Test

Status: **{r8['status']}**  
Decision: **{r8['decision']}**

## Scale and mechanical gates

| Measure | Value |
| --- | ---: |
| Public words | {r8['public_words']} |
| Segments / atomic events | {r8['segments']} / {r8['atomic_events']} |
| Scored / challenge cells | {r8['scored_cells']} / {r8['challenge_cells']} |
| Challenge density | {pct(r8['challenge_density'])} |
| Revision chains / stale returns | {r8['revisions']} / {r8['stale_graphics']} |
| Same-event shadow-feed recaps | {r8['same_delivery_replays']} |
| Distinct recap gaps | {r8['replay_gap_summary']['distinct_gaps']} |
| Ledger round trip | {r8['mechanical_checks']['ledger_round_trip_checks']}/{r8['mechanical_checks']['ledger_round_trip_checks']} |
| Public/private leaks | {r8['mechanical_checks']['public_private_key_leaks']} |
| Missing evidence / span errors | {r8['mechanical_checks']['missing_scored_cell_evidence']} / {r8['mechanical_checks']['evidence_span_errors']} |
| Exact repeated sentences (>=8 words) | {len(r8['mechanical_checks']['exact_repeated_sentences_ge8_words'])} |

## Controlled sensitivity tests

| Failure mechanism | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | {ab['event_oracle']['wrong']} / {ab['event_oracle']['checks']} | {pct(ab['event_oracle']['error_rate'])} |
| Trust provisional claims | {ab['trust_provisional_graphics']['wrong']} / {ab['trust_provisional_graphics']['checks']} | {pct(ab['trust_provisional_graphics']['error_rate'])} |
| Count shadow-feed recaps as new | {ab['count_same_delivery_replays_as_new']['wrong']} / {ab['count_same_delivery_replays_as_new']['checks']} | {pct(ab['count_same_delivery_replays_as_new']['error_rate'])} |
| Combine revision + recap failures | {ab['combined_provisional_and_replay_failure']['wrong']} / {ab['combined_provisional_and_replay_failure']['checks']} | {pct(ab['combined_provisional_and_replay_failure']['error_rate'])} |
| Drop innings scope from delivery labels | {ab['cross_innings_delivery_label_alias']['wrong']} / {ab['cross_innings_delivery_label_alias']['checks']} | {pct(ab['cross_innings_delivery_label_alias']['error_rate'])} |
| Combine all three state failures | {ab['combined_revision_replay_and_cross_innings_alias_failure']['wrong']} / {ab['combined_revision_replay_and_cross_innings_alias_failure']['checks']} | {pct(ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate'])} |

These are deterministic mechanism ablations, not Direct, CoT, T3 or Map&Make outputs.

## Curation status

The derived root is `{root['curation_status']}`. Four partnership component-ball cells were changed by an integer minimum-L1 repair while all runs, innings totals and other scorecard fields remained fixed. Human support review is required before this root can be frozen for blinded evaluation.

## Limitations

{limitations}
"""
    (base / "R8_THIRD_SELFTEST.md").write_text(report, encoding="utf-8")

    rows = []
    for label, row in (("R6", r6), ("R7", r7), ("R8", r8)):
        row_ab = row["controlled_ledger_ablations"]
        rows.append(
            f"| {label} / `{row['root_id']}` | {row['public_words']} | {row['atomic_events']} | "
            f"{row['revisions']} | {row['same_delivery_replays']} | "
            f"{pct(row_ab['combined_provisional_and_replay_failure']['error_rate'])} | "
            f"{pct(row_ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate'])} |"
        )
    comparison = """# R6–R8 Three-Root Difficulty Comparison

| Stage / root | Words | Events | Revisions | Recaps | Revision+recap error | Three-state error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "\n".join(rows) + """

R6 introduces event aggregation, R7 adds delayed semantic-class correction and stale returns, and R8 adds a nonperiodic dual-feed surface plus innings-scoped delivery identities. The three-state column is shown consistently for diagnosis, but only R8 predeclares it as its hardness gate. No row is a named-method accuracy result.
"""
    (base / "R6_R8_THREE_ROOT_COMPARISON.md").write_text(comparison, encoding="utf-8")

    history = """# R8 Iteration History

| Attempt | Design | Combined controlled error | Decision |
| --- | --- | ---: | --- |
| 1 | 36 scoring revisions; 44% hashed recaps | 54.76% | Reject |
| 2 | 44 scoring revisions; 62% hashed recaps | 58.84% | Reject |
| 3 | 60 mixed scoring/dot revisions; 68% hashed recaps | 58.16% | Reject; non-scoring perturbations diluted propagation |
| 4 | 60 scoring revisions; 95% dual-feed recaps | 62.24% | Pass old 60% target, fail R8 65% gate |
| 5 | Add independent innings-scope alias diagnostic | 65.31% | Pass R8 controlled gate |

All rejected outcomes are retained in this history. The final gate uses three explicitly reported failure mechanisms; it does not relabel the 62.24% two-mechanism result.
"""
    (base / "R8_ITERATION_HISTORY.md").write_text(history, encoding="utf-8")

    decision = f"""# R8 Advancement Decision

Admit `{r8['root_id']}` as the third mechanical pilot root, **pending human support review** of four repaired partnership component-ball cells.

The root passes {r8['mechanical_checks']['ledger_round_trip_checks']}/{r8['mechanical_checks']['ledger_round_trip_checks']} exact round-trip checks, has no public/private leakage, no missing evidence, no repeated long sentences, and reaches {pct(ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate'])} under the predeclared R8 three-state controlled failure.

Do not claim T3, Map&Make, CoT or Direct error rates from this artifact. After the four-cell support review, freeze all three public instances and prompts, then run isolated blind evaluations with exact-cell, row, table and provenance-aware metrics.
"""
    (base / "R8_ADVANCEMENT_DECISION.md").write_text(decision, encoding="utf-8")

    audit = {
        "root_id": root["root_id"],
        "curation_status": root["curation_status"],
        "r8_partnership_ball_curation": root["r8_partnership_ball_curation"],
        "ledger_round_trip": {
            "checks": r8["mechanical_checks"]["ledger_round_trip_checks"],
            "failures": r8["mechanical_checks"]["ledger_round_trip_failures"],
        },
        "freeze_blocker": "human_support_review_of_four_changed_cells",
    }
    (base / "R8_ROOT_CURATION_AUDIT.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    manifest = {
        "pilot_version": "v0.12-r8-three-root",
        "roots": [r6["root_id"], r7["root_id"], r8["root_id"]],
        "r8_status": r8["status"],
        "r8_decision": r8["decision"],
        "r8_public_sha256": evidence["document_sha256"],
        "named_method_evaluations_run": False,
        "freeze_ready": False,
        "freeze_blocker": "R8 four-cell human support review",
    }
    (base / "THREE_ROOT_PILOT_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
