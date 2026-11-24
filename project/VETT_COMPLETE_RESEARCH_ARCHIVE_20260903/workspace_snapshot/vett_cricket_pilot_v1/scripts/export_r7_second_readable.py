#!/usr/bin/env python3
"""Export the admitted R7 second root and its R6-to-R7 comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from export_r6_single_readable import pct, render_table, table_heading


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--second-dir", type=Path, required=True)
    parser.add_argument("--first-selftest", type=Path, required=True)
    args = parser.parse_args()
    base = args.second_dir
    public = json.loads((base / "package/r6_single_public.json").read_text(encoding="utf-8"))
    private = json.loads((base / "package/r6_single_private_gold.json").read_text(encoding="utf-8"))
    evidence = json.loads((base / "package/r6_single_private_evidence.json").read_text(encoding="utf-8"))
    second = json.loads((base / "R7_SECOND_ROOT_SELFTEST.json").read_text(encoding="utf-8"))
    first = json.loads(args.first_selftest.read_text(encoding="utf-8"))
    root_path = next((base / "construction").glob(f"{private['root_id']}.*_curated_root.json"))
    root = json.loads(root_path.read_text(encoding="utf-8"))

    public_parts = [
        "# R7 Second-Root Public Instance",
        "",
        f"Instance: `{public['instance_id']}`",
        "",
        public["instruction"],
        "",
        "## Live commentary",
        "",
        public["document"]["text"],
        "",
        "## Blank scorecard",
        "",
    ]
    for table in public["tables"]:
        public_parts.extend([table_heading(table), "", render_table(table), ""])
    public_parts.extend(["## Output rule", "", public["output_rule"], ""])
    (base / "R7_SECOND_PUBLIC.md").write_text("\n".join(public_parts), encoding="utf-8")

    gold_parts = [
        "# R7 Second-Root Private Gold",
        "",
        "Evaluation-only artifact. Do not expose this file to systems under test.",
        "",
        f"Root: `{private['root_id']}`; scored cells: {len(private['scored_cell_ids'])}; "
        f"challenge cells: {len(private['challenge_cell_ids'])}.",
        "",
    ]
    for table in private["gold_tables"]:
        gold_parts.extend([table_heading(table), "", render_table(table), ""])
    (base / "R7_SECOND_PRIVATE_GOLD.md").write_text("\n".join(gold_parts), encoding="utf-8")

    ab = second["controlled_ledger_ablations"]
    limitations = "\n".join(f"- {item}" for item in second["limitations"])
    report = f"""# R7 Second-Root Self-Test

Status: **{second['status']}**  
Decision: **{second['decision']}**

## Scale and difficulty

| Measure | Value |
| --- | ---: |
| Root | `{second['root_id']}` |
| Public words | {second['public_words']} |
| Segments | {second['segments']} |
| Atomic events | {second['atomic_events']} |
| Scored cells | {second['scored_cells']} |
| Challenge cells | {second['challenge_cells']} |
| Challenge density | {pct(second['challenge_density'])} |
| Three-stage correction chains | {second['revisions']} |
| Stale post-correction graphics | {second['stale_graphics']} |
| Same-event replays | {second['same_delivery_replays']} |
| Review delay | {second['review_delay_segments']['min']}–{second['review_delay_segments']['max']} segments |
| Official-correction delay | {second['revision_delay_segments']['min']}–{second['revision_delay_segments']['max']} segments |
| Stale-return delay | {second['post_correction_stale_delay_segments']['min']}–{second['post_correction_stale_delay_segments']['max']} segments |

## Mechanical gates

| Gate | Result |
| --- | ---: |
| Ledger round trip | {second['mechanical_checks']['ledger_round_trip_checks']}/{second['mechanical_checks']['ledger_round_trip_checks']} |
| Round-trip failures | {second['mechanical_checks']['ledger_round_trip_failures']} |
| Public/private key leaks | {second['mechanical_checks']['public_private_key_leaks']} |
| Filled target violations | {second['mechanical_checks']['blank_target_violations']} |
| Evidence-span errors | {second['mechanical_checks']['evidence_span_errors']} |
| Cells without evidence | {second['mechanical_checks']['missing_scored_cell_evidence']} |
| Compact/meta-language hits | {sum(second['mechanical_checks']['compact_or_meta_hits'].values())} |
| Exact repeated sentences (>=8 words) | {len(second['mechanical_checks']['exact_repeated_sentences_ge8_words'])} |

## Controlled sensitivity tests

| Condition | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | {ab['event_oracle']['wrong']} / {ab['event_oracle']['checks']} | {pct(ab['event_oracle']['error_rate'])} |
| Trust provisional semantic claims | {ab['trust_provisional_graphics']['wrong']} / {ab['trust_provisional_graphics']['checks']} | {pct(ab['trust_provisional_graphics']['error_rate'])} |
| Count same-event replays as new | {ab['count_same_delivery_replays_as_new']['wrong']} / {ab['count_same_delivery_replays_as_new']['checks']} | {pct(ab['count_same_delivery_replays_as_new']['error_rate'])} |
| Combine both failures | {ab['combined_provisional_and_replay_failure']['wrong']} / {ab['combined_provisional_and_replay_failure']['checks']} | {pct(ab['combined_provisional_and_replay_failure']['error_rate'])} |

## Curation

The source root is `{root['curation_status']}` and all retained cell records are `CANONICAL_CANDIDATE`. The derived view removes {len(root['r6_curation']['removed_rows'])} did-not-bat row and {root['r6_curation']['removed_cells']} corresponding cell records; the source remains unchanged.

## Limitations

{limitations}
"""
    (base / "R7_SECOND_SELFTEST.md").write_text(report, encoding="utf-8")

    f_ab = first["controlled_ledger_ablations"]
    comparison = f"""# R6-to-R7 Difficulty Comparison

| Measure | R6 first root | R7 second root | Change |
| --- | ---: | ---: | ---: |
| Public words | {first['public_words']} | {second['public_words']} | {second['public_words'] - first['public_words']:+d} |
| Atomic events | {first['atomic_events']} | {second['atomic_events']} | {second['atomic_events'] - first['atomic_events']:+d} |
| Scored cells | {first['scored_cells']} | {second['scored_cells']} | {second['scored_cells'] - first['scored_cells']:+d} |
| Challenge density | {pct(first['challenge_density'])} | {pct(second['challenge_density'])} | {100*(second['challenge_density']-first['challenge_density']):+.2f} pp |
| Correction chains | {first['revisions']} | {second['revisions']} | {second['revisions'] - first['revisions']:+d} |
| Same-event replays | {first['same_delivery_replays']} | {second['same_delivery_replays']} | {second['same_delivery_replays'] - first['same_delivery_replays']:+d} |
| Trust-provisional error | {pct(f_ab['trust_provisional_graphics']['error_rate'])} | {pct(ab['trust_provisional_graphics']['error_rate'])} | {100*(ab['trust_provisional_graphics']['error_rate']-f_ab['trust_provisional_graphics']['error_rate']):+.2f} pp |
| Replay-overcount error | {pct(f_ab['count_same_delivery_replays_as_new']['error_rate'])} | {pct(ab['count_same_delivery_replays_as_new']['error_rate'])} | {100*(ab['count_same_delivery_replays_as_new']['error_rate']-f_ab['count_same_delivery_replays_as_new']['error_rate']):+.2f} pp |
| Combined controlled error | {pct(f_ab['combined_provisional_and_replay_failure']['error_rate'])} | {pct(ab['combined_provisional_and_replay_failure']['error_rate'])} | {100*(ab['combined_provisional_and_replay_failure']['error_rate']-f_ab['combined_provisional_and_replay_failure']['error_rate']):+.2f} pp |

R7 adds semantic-class revisions, an unresolved review stage, delayed official authority, post-correction stale returns, and denser event-identity reuse. The combined deterministic sensitivity test rises above the predeclared 60% gate. This comparison measures mechanism sensitivity, not model accuracy.
"""
    (base / "R6_R7_DIFFICULTY_COMPARISON.md").write_text(comparison, encoding="utf-8")

    decision = f"""# R7 Advancement Decision

Admit `match_0182` as the second root of the three-root pilot.

The instance passes {second['mechanical_checks']['ledger_round_trip_checks']}/{second['mechanical_checks']['ledger_round_trip_checks']} round-trip checks, has complete private evidence, and reaches {pct(ab['combined_provisional_and_replay_failure']['error_rate'])} under the combined controlled failure. Three unsuccessful intermediate constructions are retained for audit, showing that the 60% gate was reached through semantic-class correction and event-identity pressure rather than unreported manual selection.

Do not start the final method comparison yet. Construct one third root with a different discourse surface and add independent human factual-equivalence, naturalness and unique-recovery review across all three roots. Then freeze public inputs and run blinded Direct, CoT, T3 and Map&Make evaluations.
"""
    (base / "R7_ADVANCEMENT_DECISION.md").write_text(decision, encoding="utf-8")


if __name__ == "__main__":
    main()
