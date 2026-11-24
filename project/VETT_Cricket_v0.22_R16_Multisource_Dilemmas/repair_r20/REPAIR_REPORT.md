# R20 220-Match Root Repair Report

## Decision

**PASS** — all 220 source match IDs are represented.

## Corpus identity

- Independent canonical roots: 217
- Duplicate-consistency controls: 3
- Source commentaries sanitized for construction leakage: 10

## Cell reliability

- Total source cells: 98447
- Verified scored cells: 91555
- Conflict-implicated cells excluded from scoring: 6892
- Matches with at least one masked cell: 113
- Minimum verified cells retained in one match: 198

No ambiguous value is silently rewritten. A source-conflict mask removes only the table
regions implicated by a failed cricket-consistency check. The original value, original
status, failure code and audit detail remain in the repaired root for review.

The three exact duplicate source matches remain available as duplicate-consistency tests,
but scientific sample counts must report 217 independent matches rather than 220.
