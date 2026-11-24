# Isolated same-model probe results

These are real blind outputs from isolated agents using the same model family. They are a three-root development probe, not final paper estimates.

| Method | Cell error | Incorrect | Omission | Hallucination | Table exact |
| --- | ---: | ---: | ---: | ---: | ---: |
| direct_no_cot | 0.78% (strict 24.03%) | 0.78% | 0.00% | 0.93% | 0.00% |
| direct_cot | 28.84% (strict 35.89%) | 1.16% | 27.67% | 47.44% | 0.00% |
| t3_paper_direct_integration_variant | 34.55% (strict 41.14%) | 4.96% | 29.59% | 30.47% | 0.00% |
| t3_provenance_enhanced | 1.24% (strict 20.16%) | 1.24% | 0.00% | 1.86% | 0.00% |
| mapmake_paper_style | 0.78% (strict 24.03%) | 0.78% | 0.00% | 0.00% | 33.33% |
| mapmake_scope_version_enhanced | 4.57% (strict 20.16%) | 0.78% | 3.80% | 8.53% | 0.00% |

## Cell error by view

| Method | V1 | V2 | V3 |
| --- | ---: | ---: | ---: |
| direct_no_cot | 0.78% | 0.78% | 0.78% |
| direct_cot | 28.84% | 28.84% | 28.84% |
| t3_paper_direct_integration_variant | 33.10% | 33.10% | 37.44% |
| t3_provenance_enhanced | 1.24% | 1.24% | 1.24% |
| mapmake_paper_style | 0.78% | 0.78% | 0.78% |
| mapmake_scope_version_enhanced | 4.57% | 4.57% | 4.57% |

## Caveats

- Only three development roots are included.
- Cell observations within a match are not statistically independent.
- The six runs use isolated agents with the same model family, not official paper checkpoints.
- T3 paper-style result is the paper's direct-integration variant, not its generated-code main path.
