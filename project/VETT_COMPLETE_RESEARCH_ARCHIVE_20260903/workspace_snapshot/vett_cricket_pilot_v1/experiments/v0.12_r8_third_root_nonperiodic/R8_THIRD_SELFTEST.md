# R8 Third-Root Self-Test

Status: **PASS**  
Decision: **ADMIT_THIRD_ROOT_PENDING_HUMAN_SUPPORT_REVIEW**

## Scale and mechanical gates

| Measure | Value |
| --- | ---: |
| Public words | 14789 |
| Segments / atomic events | 607 / 239 |
| Scored / challenge cells | 293 / 288 |
| Challenge density | 98.29% |
| Revision chains / stale returns | 60 / 36 |
| Same-event shadow-feed recaps | 170 |
| Distinct recap gaps | 6 |
| Ledger round trip | 294/294 |
| Public/private leaks | 0 |
| Missing evidence / span errors | 0 / 0 |
| Exact repeated sentences (>=8 words) | 0 |

## Controlled sensitivity tests

| Failure mechanism | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | 0 / 294 | 0.00% |
| Trust provisional claims | 114 / 294 | 38.78% |
| Count shadow-feed recaps as new | 165 / 294 | 56.12% |
| Combine revision + recap failures | 183 / 294 | 62.24% |
| Drop innings scope from delivery labels | 48 / 294 | 16.33% |
| Combine all three state failures | 192 / 294 | 65.31% |

These are deterministic mechanism ablations, not Direct, CoT, T3 or Map&Make outputs.

## Curation status

The derived root is `NEEDS_SUPPORT_ANNOTATION`. Four partnership component-ball cells were changed by an integer minimum-L1 repair while all runs, innings totals and other scorecard fields remained fixed. Human support review is required before this root can be frozen for blinded evaluation.

## Limitations

- Controlled ledger ablations are not Direct, CoT, T3 or Map&Make model evaluations.
- The delivery order is constrained synthetic data derived from a curated scorecard, not an observed ball-by-ball feed.
- Naturalness and unique full-table recovery still require independent human review.
- The third root passes mechanical gates but its four minimal partnership-ball repairs require human support review before freezing.
