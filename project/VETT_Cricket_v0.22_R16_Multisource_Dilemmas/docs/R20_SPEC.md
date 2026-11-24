# Spec: VETT-Cricket R20 Full-Corpus Root Repair

## Objective

Create a reproducible 220-item repair layer before generating the long-form
full-table benchmark. The corpus contains 217 independent match roots and three
byte-identical duplicate-control matches. All 220 source identities remain
available, while scientific results report the independent-root count.

## Reliability policy

R20 never guesses which side of an unresolved source conflict is correct.
Source values are retained, failed checks are mapped to the smallest defensible
table regions, and affected cells are marked `R20_UNSCORED_SOURCE_CONFLICT`.
All unaffected cells become `R20_VERIFIED_SOURCE` even when the historical
root-level status blocked the whole match.

The repaired layer is therefore complete at the match level and conservative
at the cell level. Later public text may be generated only from verified cells.

## Text policy

Historical commentary remains source reference material, not solver input.
The three known construction-leak openings are deterministically rewritten and
the repaired text is scanned for construction-language fingerprints. Later
R20 public instances are generated from verified claims rather than copying
potentially conflicting source commentary.

## Difficulty target

The eventual long-form benchmark targets roughly 75% direct-fact accuracy for
the strongest evaluated model, with lower challenge-component and full-table
performance. This is an empirical release target, not a guaranteed property.
Difficulty may not be obtained by ambiguous gold or unsupported hidden rules.

## Build

```powershell
$env:PYTHONPATH = 'src'
python -m vett_r20.cli repair `
  --roots ..\VETT_COMPLETE_RESEARCH_ARCHIVE_20260903\workspace_snapshot\vett_cricket_pilot_v1\data\canonical_roots_217.jsonl `
  --raw ..\Self-cricket-clean_text_scorecard_v1_220_matches_extracted `
  --audit-csv ..\VETT_COMPLETE_RESEARCH_ARCHIVE_20260903\workspace_snapshot\cricket_220_audit_v1\results\per_match_audit.csv `
  --check-details ..\VETT_COMPLETE_RESEARCH_ARCHIVE_20260903\workspace_snapshot\cricket_220_audit_v1\results\check_details.csv `
  --output repair_r20
python -m vett_r20.cli audit-repair --release repair_r20
```

The output directory must be empty. R1–R19 sources and releases remain
unchanged.
