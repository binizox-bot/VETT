#!/usr/bin/env python3
"""Export R9 readable artifacts and the R8-to-R9 attack audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from export_r6_single_readable import pct, render_table, table_heading


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r9-dir", type=Path, required=True)
    parser.add_argument("--r8-selftest", type=Path, required=True)
    args = parser.parse_args()
    base = args.r9_dir
    public = json.loads((base / "instance/r9_public.json").read_text(encoding="utf-8"))
    private = json.loads((base / "instance/r9_private_gold.json").read_text(encoding="utf-8"))
    r9 = json.loads((base / "R9_SELFTEST.json").read_text(encoding="utf-8"))
    r8 = json.loads(args.r8_selftest.read_text(encoding="utf-8"))

    public_parts = [
        "# R9 Split-Authority Public Stress Variant", "", f"Instance: `{public['instance_id']}`", "",
        public["instruction"], "", "## Radio and scoring-console transcript", "",
        public["document"]["text"], "", "## Blank scorecard", "",
    ]
    for table in public["tables"]:
        public_parts.extend([table_heading(table), "", render_table(table), ""])
    public_parts.extend(["## Output rule", "", public["output_rule"], ""])
    (base / "R9_PUBLIC.md").write_text("\n".join(public_parts), encoding="utf-8")

    gold_parts = [
        "# R9 Private Gold", "",
        "Evaluation-only artifact. Do not expose this file to systems under test.", "",
    ]
    for table in private["gold_tables"]:
        gold_parts.extend([table_heading(table), "", render_table(table), ""])
    (base / "R9_PRIVATE_GOLD.md").write_text("\n".join(gold_parts), encoding="utf-8")

    ab = r9["controlled_ledger_ablations"]
    selftest = f"""# R9 Split-Authority Self-Test

Status: **{r9['status']}**  
Decision: **{r9['decision']}**

| Measure | Value |
| --- | ---: |
| Public words | {r9['public_words']} |
| Segments / atomic events | {r9['segments']} / {r9['atomic_events']} |
| Revision chains / authority fragments | {r9['revisions']} / {r9['revisions'] * 2} |
| Stale returns / retained recaps | {r9['stale_graphics']} / {r9['same_delivery_replays']} |
| Review delay | {r9['review_delay_segments']['min']}–{r9['review_delay_segments']['max']} segments |
| Full authority delay | {r9['revision_delay_segments']['min']}–{r9['revision_delay_segments']['max']} segments |
| Authority-to-stale delay | {r9['post_correction_stale_delay_segments']['min']}–{r9['post_correction_stale_delay_segments']['max']} segments |
| Exact ledger round trip | {r9['mechanical_checks']['ledger_round_trip_checks']}/{r9['mechanical_checks']['ledger_round_trip_checks']} |
| Leaks / missing evidence / span errors | {r9['mechanical_checks']['public_private_key_leaks']} / {r9['mechanical_checks']['missing_scored_cell_evidence']} / {r9['mechanical_checks']['evidence_span_errors']} |
| Repeated sentences of >=8 words | {len(r9['mechanical_checks']['exact_repeated_sentences_ge8_words'])} |

## Controlled mechanism sensitivity

| Failure | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | {ab['event_oracle']['wrong']} / {ab['event_oracle']['checks']} | {pct(ab['event_oracle']['error_rate'])} |
| Trust provisional state | {ab['trust_provisional_graphics']['wrong']} / {ab['trust_provisional_graphics']['checks']} | {pct(ab['trust_provisional_graphics']['error_rate'])} |
| Read class fragment, miss magnitude fragment | {ab['split_authority_classification_only']['wrong']} / {ab['split_authority_classification_only']['checks']} | {pct(ab['split_authority_classification_only']['error_rate'])} |
| Read magnitude fragment, miss class fragment | {ab['split_authority_magnitude_only']['wrong']} / {ab['split_authority_magnitude_only']['checks']} | {pct(ab['split_authority_magnitude_only']['error_rate'])} |
| Count recaps as new events | {ab['count_same_delivery_replays_as_new']['wrong']} / {ab['count_same_delivery_replays_as_new']['checks']} | {pct(ab['count_same_delivery_replays_as_new']['error_rate'])} |
| Revision + recap failure | {ab['combined_provisional_and_replay_failure']['wrong']} / {ab['combined_provisional_and_replay_failure']['checks']} | {pct(ab['combined_provisional_and_replay_failure']['error_rate'])} |
| Revision + recap + innings-scope failure | {ab['combined_revision_replay_and_cross_innings_alias_failure']['wrong']} / {ab['combined_revision_replay_and_cross_innings_alias_failure']['checks']} | {pct(ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate'])} |

All percentages are deterministic mechanism ablations. They are not T3, Map&Make, CoT or Direct model results.
"""
    (base / "R9_SELFTEST.md").write_text(selftest, encoding="utf-8")

    r8_ab = r8["controlled_ledger_ablations"]
    audit = f"""# R8-to-R9 Construction-Fingerprint Attack Audit

## Finding

R8 passes its mechanical gates, but its 170 same-event recaps create a density that is too conspicuous for corpus-scale use. R9 deliberately accepts a slightly lower controlled error in exchange for a less artificial surface and a harder evidence-composition requirement.

| Measure | R8 | R9 | Change |
| --- | ---: | ---: | ---: |
| Words | {r8['public_words']} | {r9['public_words']} | {r9['public_words']-r8['public_words']:+d} |
| Segments | {r8['segments']} | {r9['segments']} | {r9['segments']-r8['segments']:+d} |
| Recaps | {r8['same_delivery_replays']} | {r9['same_delivery_replays']} | {r9['same_delivery_replays']-r8['same_delivery_replays']:+d} |
| Most-common recap-gap share | {pct(r8['replay_gap_summary']['most_common_share'])} | {pct(r9['replay_gap_summary']['most_common_share'])} | {100*(r9['replay_gap_summary']['most_common_share']-r8['replay_gap_summary']['most_common_share']):+.2f} pp |
| Long exact repeated sentences | {len(r8['mechanical_checks']['exact_repeated_sentences_ge8_words'])} | {len(r9['mechanical_checks']['exact_repeated_sentences_ge8_words'])} | 0 |
| Revision + recap error | {pct(r8_ab['combined_provisional_and_replay_failure']['error_rate'])} | {pct(ab['combined_provisional_and_replay_failure']['error_rate'])} | {100*(ab['combined_provisional_and_replay_failure']['error_rate']-r8_ab['combined_provisional_and_replay_failure']['error_rate']):+.2f} pp |
| Three-state controlled error | {pct(r8_ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate'])} | {pct(ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate'])} | {100*(ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate']-r8_ab['combined_revision_replay_and_cross_innings_alias_failure']['error_rate']):+.2f} pp |

## Structural gain

- R9 removes 68 of R8's 170 recaps.
- Every one of the 60 revisions now requires two nonadjacent authority fragments.
- The first fragment establishes event category and legal-ball status while withholding the number.
- The later fragment supplies only the accepted magnitude and refers back by production cue.
- Missing either half causes a measurable, independently reported error pattern.
- R9 is a discourse variant of `match_0122`, not a fourth independent root.
- The same four partnership-ball repairs remain blocked on human support review.
"""
    (base / "R8_R9_ATTACK_AUDIT.md").write_text(audit, encoding="utf-8")

    history = """# R9 Iteration History

| Attempt | Configuration | Result |
| --- | --- | --- |
| 1 | Keep 48% of R8 recaps; split corrections | FAIL: 60.88% three-state error, repeated magnitude templates, stale delay minimum 7 |
| 2 | Keep 60%; vary magnitude wording; enforce >=10-segment stale return | PASS: 62.93% three-state error, zero repeated long sentences |
"""
    (base / "R9_ITERATION_HISTORY.md").write_text(history, encoding="utf-8")

    decision = """# R9 Decision

Retain R9 as the preferred high-difficulty discourse variant for the third root. Keep R8 as an explicit upper-bound stress ablation rather than the default distribution template.

The next corpus step should reproduce split-authority reasoning on additional independent roots with varied surfaces and lower recap ratios. Freeze no sample until the four repaired partnership cells receive support review and isolated named-method evaluations are run.
"""
    (base / "R9_DECISION.md").write_text(decision, encoding="utf-8")


if __name__ == "__main__":
    main()
