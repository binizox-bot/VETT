# R6 Single-Root Self-Test

Status: **PASS**  
Decision: **ADVANCE_TO_TWO_ADDITIONAL_ROOTS**

## Instance scale

| Measure | Value |
| --- | ---: |
| Public words | 5095 |
| Text segments | 327 |
| Atomic delivery events | 247 |
| Scored cells | 274 |
| Challenge cells | 270 |
| Challenge density | 98.54% |
| Delayed corrections | 12 |
| Stale graphics | 6 |
| Same-delivery replays | 19 |
| Correction delay | 11–13 segments |

## Integrity gates

| Gate | Result |
| --- | ---: |
| Ledger-to-scorecard checks | 275/275 correct |
| Ledger round-trip failures | 0 |
| Public/private key leaks | 0 |
| Nonblank target violations | 0 |
| Evidence-span errors | 0 |
| Scored cells without evidence | 0 |
| Compact/meta-language hits | 0 |
| Exact repeated sentences (>=8 words, >=3 copies) | 0 |

## Controlled ledger ablations

| Condition | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | 0 / 275 | 0.00% |
| Trust provisional graphics | 73 / 275 | 26.55% |
| Count same-delivery replays as new | 89 / 275 | 32.36% |
| Combine both mistakes | 117 / 275 | 42.55% |

These are deterministic error injections, not Direct, CoT, T3, or Map&Make model evaluations.

## Source feasibility

The event-reversibility audit examined 217 canonical roots. It found 10 strict roots that passed all automatic source constraints. The selected root required a documented curation step that removed delivery-unobservable did-not-bat placeholders; the original source remains unchanged.

## Remaining limitations

- Controlled ledger ablations are not Direct, CoT, T3 or Map&Make model evaluations.
- The delivery order is constrained synthetic data derived from a curated scorecard, not an observed ball-by-ball feed.
- Naturalness and unique full-table recovery still require independent human review.
- Only one root is included; advancement permits two more roots, not corpus-scale expansion.
