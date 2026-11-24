# V4-SDC three-root isolated probe

| Method | V3C challenge error | V4-SDC challenge error | Delta | V4 omission | V4 exact |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct_no_cot | 0.00% | 47.22% | 47.22% | 36.11% | 0.00% |
| direct_cot | 25.00% | 47.22% | 22.22% | 47.22% | 0.00% |
| t3_paper_direct_integration_variant | 38.89% | 47.22% | 8.33% | 27.78% | 0.00% |
| t3_provenance_enhanced | 8.33% | 47.22% | 38.89% | 47.22% | 0.00% |
| mapmake_paper_style | 0.00% | 36.11% | 36.11% | 36.11% | 0.00% |
| mapmake_scope_version_enhanced | 11.11% | 36.11% | 25.00% | 25.00% | 0.00% |

## Retention decision

- Degraded method families: 4/4.
- Predeclared degradation gate passed: True.

## Query-guided recoverability check

- V4-SDC queried cells correct: 36/36.
- Query-guided V4-SDC cell error: 0.00%.
- Final decision: RETAIN_AS_SCHEMA_COVERAGE_SLICE_REVISE_FOR_FACTUAL_HARDNESS.

All 36 treatment challenge cells were recovered when their value-free schema locations were supplied; the observed full-table errors are therefore dominated by row/table coverage and omission.

## Interpretation boundary

This is a three-root same-model construction diagnostic. It supports the next dataset-design decision and does not support a paper-level claim about T3, Map&Make or CoT population performance.
