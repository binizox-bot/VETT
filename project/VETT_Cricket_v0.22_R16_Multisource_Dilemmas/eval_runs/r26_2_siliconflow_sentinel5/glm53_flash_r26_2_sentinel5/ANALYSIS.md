# R25 decision-record model run: glm53_flash_r26_2_sentinel5

- Factual record macro accuracy (primary): 40.00%
- Full-record exact (micro): 40.00%
- Decision-field accuracy (diagnostic): 83.33%
- Latent-state accuracy: 88.57%
- Minimal-evidence F1: 67.16%
- Counterfactual field accuracy: 86.67%
- Counterfactual full-record exact: 60.00%
- Paired factual/counterfactual exact: 40.00%
- Confidence Brier: 0.45992
- Actual cost (CNY): 0.092834
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 100.00% | 100.00% |
| L2 | 100.00% | 100.00% |
| L3 | 0.00% | 91.67% |
| L4 | 0.00% | 58.33% |
| L5 | 0.00% | 66.67% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 0.00% |
| L2-L3 | 100.00% |
| L3-L4 | 0.00% |
| L4-L5 | 0.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 100.00%
- State/status internally consistent: 100.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 2 |
| FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT | 1 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 2 |
