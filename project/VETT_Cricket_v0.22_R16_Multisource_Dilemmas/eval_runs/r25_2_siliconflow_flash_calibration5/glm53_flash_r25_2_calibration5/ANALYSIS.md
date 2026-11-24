# R25 decision-record model run: glm53_flash_r25_2_calibration5

- Factual record macro accuracy (primary): 32.00%
- Full-record exact (micro): 32.00%
- Decision-field accuracy (diagnostic): 70.67%
- Latent-state accuracy: 71.43%
- Minimal-evidence F1: 46.81%
- Counterfactual field accuracy: 68.33%
- Counterfactual full-record exact: 20.00%
- Paired factual/counterfactual exact: 20.00%
- Confidence Brier: 0.572268
- Actual cost (CNY): 0.241791
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 80.00% | 90.00% |
| L2 | 40.00% | 71.67% |
| L3 | 20.00% | 70.00% |
| L4 | 20.00% | 68.33% |
| L5 | 0.00% | 53.33% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 40.00% |
| L2-L3 | 20.00% |
| L3-L4 | 0.00% |
| L4-L5 | 20.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 80.00%
- State/status internally consistent: 92.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 17 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 3 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 5 |
