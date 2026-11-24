# R10 Fourth-Root Self-Test

Status: **PASS**  
Decision: **ADMIT_FOURTH_ROOT_PENDING_SOURCE_SUPPORT_AUDIT**

| Measure | Value |
| --- | ---: |
| Root | `match_0032` |
| Public words | 23679 |
| Segments / atomic events | 888 / 436 |
| Scored / challenge cells | 336 / 330 |
| Challenge density | 98.21% |
| Revision chains / relational magnitudes | 60 / 42 |
| Implicit unique links / marker fallbacks | 55 / 5 |
| Recaps / interval checkpoints | 153 / 6 |
| Recap share of atomic events | 35.09% |
| Exact ledger round trip | 336/336 |
| Public/private leaks | 0 |
| Missing evidence / span errors | 0 / 0 |
| Relational cells missing three-part evidence | 0 |
| Exact repeated long sentences | 0 |

## Controlled mechanism sensitivity

| Failure | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | 0 / 336 | 0.00% |
| Trust provisional state | 123 / 336 | 36.61% |
| Count recaps as new events | 177 / 336 | 52.68% |
| Count interval checkpoints as new | 151 / 336 | 44.94% |
| Read class but miss magnitude | 69 / 336 | 20.54% |
| Read magnitude but miss class | 97 / 336 | 28.87% |
| Mislink implicit magnitudes | 75 / 336 | 22.32% |
| Collapse checkpoint intervals to endpoints | 15 / 336 | 4.46% |
| Combined six state failures | 215 / 336 | 63.99% |

These values are deterministic mechanism diagnostics. They are not named-method model scores.
