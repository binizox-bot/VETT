# R13 spiral upgrade: local controls to cross-batch adjudication

## R12 failure diagnosis

R12 showed that claim density was not the limiting factor. CoT and provenance-enhanced T3 recovered all 317 scored facts because every row's authority could be resolved from explicit local language. Map&Make failed only on the exception-appendix topology, where it retained the general rule instead of applying the later override.

## Attempt A — rejected as final

- Root: `match_0045`
- Atomic cells: 101
- Batches: 7
- Cross-batch cells: 0
- Per-batch-only solver blank rate: 0.00%

Attempt A replaces row-level authority with multi-row control totals, but every batch remains independently solvable. It is retained as a failed intermediate version because a strong method can still split the dossier into seven local puzzles.

## Attempt B — admitted to blind evaluation

- Documents: 6
- Segments: 67
- Words: 2851
- Atomic cells: 101
- False claims: 303
- Supported claims: 101
- Cross-batch or distant-reconciliation cells: 36 (35.64%)
- Exact duplicate sentence excess: 0
- Aggressively normalized template duplicate rate: 20.90%
- Automated checks: 17/17

For batting, each local batch discloses only how many accepted papers came from one named source. A separate competition-wide roll-up supplies combined run, ball and boundary totals across both batches. For one bowling pair, a distant fielding reconciliation is required. The target can no longer be solved row by row or batch by batch.

## Deterministic shortcut screen

| Strategy | Error rate | Blank rate |
| --- | ---: | ---: |
| Full constraint oracle | 0.00% | 0.00% |
| Live/cache majority | 100.00% | 0.00% |
| Fixed named source | 54.46% | 0.00% |
| Per-batch-only solver | 0.00% on resolved cells | 35.64% |

These are deterministic diagnostics, not T3, Map&Make, CoT or model scores.

## Remaining risks before scale-up

1. Control totals remain somewhat audit-like; human naturalness review is required.
2. This is one independent root and one generated prose style.
3. No isolated model prediction has been run on R13-B yet.
4. If CoT/T3 again solve all cells, R13-C must replace explicit totals with partially observed cricket conservation relations and delayed event evidence rather than arbitrary extra noise.
