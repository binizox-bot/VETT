# R7 Second-Root Self-Test

Status: **PASS**  
Decision: **ADMIT_SECOND_ROOT_FOR_THREE_ROOT_PILOT**

## Scale and difficulty

| Measure | Value |
| --- | ---: |
| Root | `match_0182` |
| Public words | 16158 |
| Segments | 921 |
| Atomic events | 581 |
| Scored cells | 380 |
| Challenge cells | 376 |
| Challenge density | 98.95% |
| Three-stage correction chains | 24 |
| Stale post-correction graphics | 12 |
| Same-event replays | 183 |
| Review delay | 12–16 segments |
| Official-correction delay | 28–31 segments |
| Stale-return delay | 9–11 segments |

## Mechanical gates

| Gate | Result |
| --- | ---: |
| Ledger round trip | 380/380 |
| Round-trip failures | 0 |
| Public/private key leaks | 0 |
| Filled target violations | 0 |
| Evidence-span errors | 0 |
| Cells without evidence | 0 |
| Compact/meta-language hits | 0 |
| Exact repeated sentences (>=8 words) | 0 |

## Controlled sensitivity tests

| Condition | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | 0 / 380 | 0.00% |
| Trust provisional semantic claims | 142 / 380 | 37.37% |
| Count same-event replays as new | 219 / 380 | 57.63% |
| Combine both failures | 233 / 380 | 61.32% |

## Curation

The source root is `READY_FOR_GENERATED_VIEWS` and all retained cell records are `CANONICAL_CANDIDATE`. The derived view removes 1 did-not-bat row and 7 corresponding cell records; the source remains unchanged.

## Limitations

- Controlled ledger ablations are not Direct, CoT, T3 or Map&Make model evaluations.
- The delivery order is constrained synthetic data derived from a curated scorecard, not an observed ball-by-ball feed.
- Naturalness and unique full-table recovery still require independent human review.
- Two distinct roots are now admitted; one more distinct root is required before blinded model evaluation.
