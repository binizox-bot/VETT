# R2 fixed-schema three-root self-test

The row and column locations were supplied without values. Errors therefore measure value resolution after schema localization, not full-table coverage.

| Method | Correct | Wrong | Missing | Strict error | Scalar-fact error | Omission |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct_no_cot | 27/36 | 9 | 0 | 25.00% | 6.90% | 0.00% |
| direct_cot | 27/36 | 9 | 0 | 25.00% | 6.90% | 0.00% |
| t3_paper_direct_integration_variant | 28/36 | 8 | 0 | 22.22% | 3.45% | 0.00% |
| t3_provenance_enhanced | 28/36 | 8 | 0 | 22.22% | 3.45% | 0.00% |
| mapmake_paper_style | 27/36 | 9 | 0 | 25.00% | 6.90% | 0.00% |
| mapmake_scope_version_enhanced | 27/36 | 9 | 0 | 25.00% | 6.90% | 0.00% |

## Cross-version factual-hardness diagnostic

- V4 query-guided error: 0.00% (36/36 correct).
- R2 query-guided strong error: 25.00% (27/36 correct).
- R2 query-guided strong scalar-fact error: 6.90% (27/29 correct).
- Increase: 25.00%.

## Gate

- Method families at or above 20% strict fixed-schema error: 4/4.
- Method families at or above 20% scalar-fact error: 0/4.
- Errors not dominated by missing cells: True.
- Frozen predictions unchanged: True.
- Decision: **REVISE_AND_RETEST**.

## Interpretation boundary

This is a construction and scorer self-test, not a paper-level leaderboard. The strict error gate alone would justify expansion, but the scalar-fact audit overturns that decision: R2 must be revised before expansion. The probe cannot establish population performance for T3, Map&Make, CoT or Direct prompting.
