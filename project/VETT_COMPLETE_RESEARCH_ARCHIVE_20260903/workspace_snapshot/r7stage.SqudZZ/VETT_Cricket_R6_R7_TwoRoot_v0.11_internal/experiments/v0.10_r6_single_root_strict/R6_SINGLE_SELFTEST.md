# R6 Single-Root Self-Test

Status: **PASS**  
Decision: **ADVANCE_TO_TWO_ADDITIONAL_ROOTS**

## Instance scale

| Measure | Value |
| --- | ---: |
| Public words | 9061 |
| Text segments | 564 |
| Atomic delivery events | 436 |
| Scored cells | 336 |
| Challenge cells | 330 |
| Challenge density | 98.21% |
| Delayed corrections | 12 |
| Stale graphics | 6 |
| Same-delivery replays | 38 |
| Correction delay | 11–13 segments |

## Integrity gates

| Gate | Result |
| --- | ---: |
| Ledger-to-scorecard checks | 336/336 correct |
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
| Event oracle | 0 / 336 | 0.00% |
| Trust provisional graphics | 57 / 336 | 16.96% |
| Count same-delivery replays as new | 130 / 336 | 38.69% |
| Combine both mistakes | 146 / 336 | 43.45% |

These are deterministic error injections, not Direct, CoT, T3, or Map&Make model evaluations.

## Source feasibility

The source audit examined 217 canonical roots and retained 10 rule-screen candidates. Ledger synthesis plus full round-trip validation retained 2 roots: match_0031, match_0032. The selected root removed 4 delivery-unobservable did-not-bat rows and 28 corresponding cell records; the original source remains unchanged. The earlier `match_0096` engineering probe is excluded because its upstream cells are marked `BLOCKED_BY_CONFLICT`.

## Remaining limitations

- Controlled ledger ablations are not Direct, CoT, T3 or Map&Make model evaluations.
- The delivery order is constrained synthetic data derived from a curated scorecard, not an observed ball-by-ball feed.
- Naturalness and unique full-table recovery still require independent human review.
- Only one root is included; advancement permits two more roots, not corpus-scale expansion.
