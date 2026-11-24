# R9 Split-Authority Self-Test

Status: **PASS**  
Decision: **ADMIT_R9_STRESS_VARIANT_PENDING_HUMAN_SUPPORT_REVIEW**

| Measure | Value |
| --- | ---: |
| Public words | 16131 |
| Segments / atomic events | 599 / 239 |
| Revision chains / authority fragments | 60 / 120 |
| Stale returns / retained recaps | 36 / 102 |
| Review delay | 14–63 segments |
| Full authority delay | 56–151 segments |
| Authority-to-stale delay | 10–62 segments |
| Exact ledger round trip | 294/294 |
| Leaks / missing evidence / span errors | 0 / 0 / 0 |
| Repeated sentences of >=8 words | 0 |

## Controlled mechanism sensitivity

| Failure | Wrong / checks | Error rate |
| --- | ---: | ---: |
| Event oracle | 0 / 294 | 0.00% |
| Trust provisional state | 114 / 294 | 38.78% |
| Read class fragment, miss magnitude fragment | 71 / 294 | 24.15% |
| Read magnitude fragment, miss class fragment | 93 / 294 | 31.63% |
| Count recaps as new events | 146 / 294 | 49.66% |
| Revision + recap failure | 174 / 294 | 59.18% |
| Revision + recap + innings-scope failure | 185 / 294 | 62.93% |

All percentages are deterministic mechanism ablations. They are not T3, Map&Make, CoT or Direct model results.
