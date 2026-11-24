# R10 isolated GPT-5.5 blind diagnostic

| Method | Correct | Wrong | Missing | Hallucinated | Cell error | Omission | Row exact | Table exact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct_no_cot | 234/336 | 101 | 1 | 0 | 30.36% | 0.30% | 48.78% | 9.09% |
| direct_cot | 253/336 | 82 | 1 | 0 | 24.70% | 0.30% | 59.76% | 36.36% |
| t3_paper_direct_integration_variant | 224/336 | 112 | 0 | 0 | 33.33% | 0.00% | 45.12% | 9.09% |
| t3_provenance_enhanced | 251/336 | 85 | 0 | 0 | 25.30% | 0.00% | 57.32% | 36.36% |
| mapmake_paper_style | 253/336 | 82 | 1 | 0 | 24.70% | 0.30% | 59.76% | 36.36% |
| mapmake_scope_version_enhanced | 253/336 | 82 | 1 | 0 | 24.70% | 0.30% | 59.76% | 36.36% |

## Interpretation boundary

This is a one-root, one-backbone construction diagnostic. It cannot establish population performance or a market-wide ranking.
