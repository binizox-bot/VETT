# R8 Iteration History

| Attempt | Design | Combined controlled error | Decision |
| --- | --- | ---: | --- |
| 1 | 36 scoring revisions; 44% hashed recaps | 54.76% | Reject |
| 2 | 44 scoring revisions; 62% hashed recaps | 58.84% | Reject |
| 3 | 60 mixed scoring/dot revisions; 68% hashed recaps | 58.16% | Reject; non-scoring perturbations diluted propagation |
| 4 | 60 scoring revisions; 95% dual-feed recaps | 62.24% | Pass old 60% target, fail R8 65% gate |
| 5 | Add independent innings-scope alias diagnostic | 65.31% | Pass R8 controlled gate |

All rejected outcomes are retained in this history. The final gate uses three explicitly reported failure mechanisms; it does not relabel the 62.24% two-mechanism result.
