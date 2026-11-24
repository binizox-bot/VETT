# R25 decision-record model run: deepseek_v41_flash_r25_2_calibration5

- Factual record macro accuracy (primary): 40.00%
- Full-record exact (micro): 40.00%
- Decision-field accuracy (diagnostic): 76.33%
- Latent-state accuracy: 85.71%
- Minimal-evidence F1: 58.02%
- Counterfactual field accuracy: 69.33%
- Counterfactual full-record exact: 28.00%
- Paired factual/counterfactual exact: 28.00%
- Confidence Brier: 0.465448
- Actual cost (CNY): 1.231608
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 80.00% | 88.33% |
| L2 | 20.00% | 71.67% |
| L3 | 60.00% | 86.67% |
| L4 | 20.00% | 75.00% |
| L5 | 20.00% | 60.00% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 60.00% |
| L2-L3 | -40.00% |
| L3-L4 | 40.00% |
| L4-L5 | 0.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 76.00%
- State/status internally consistent: 92.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 15 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 4 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 6 |
