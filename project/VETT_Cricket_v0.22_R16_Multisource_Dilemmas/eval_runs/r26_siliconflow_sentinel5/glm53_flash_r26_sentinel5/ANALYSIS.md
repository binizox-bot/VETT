# R25 decision-record model run: glm53_flash_r26_sentinel5

- Factual record macro accuracy (primary): 40.00%
- Full-record exact (micro): 40.00%
- Decision-field accuracy (diagnostic): 78.67%
- Latent-state accuracy: 74.86%
- Minimal-evidence F1: 67.63%
- Counterfactual field accuracy: 75.67%
- Counterfactual full-record exact: 36.00%
- Paired factual/counterfactual exact: 36.00%
- Confidence Brier: 0.524004
- Actual cost (CNY): 0.506032
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 80.00% | 98.33% |
| L2 | 80.00% | 91.67% |
| L3 | 20.00% | 81.67% |
| L4 | 0.00% | 61.67% |
| L5 | 20.00% | 60.00% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 0.00% |
| L2-L3 | 60.00% |
| L3-L4 | 20.00% |
| L4-L5 | -20.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 68.00%
- State/status internally consistent: 96.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 15 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 1 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 9 |
