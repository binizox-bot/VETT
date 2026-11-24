# R25 decision-record model run: deepseek_v41_flash_r26_sentinel5

- Factual record macro accuracy (primary): 60.00%
- Full-record exact (micro): 60.00%
- Decision-field accuracy (diagnostic): 85.33%
- Latent-state accuracy: 74.29%
- Minimal-evidence F1: 57.58%
- Counterfactual field accuracy: 73.00%
- Counterfactual full-record exact: 32.00%
- Paired factual/counterfactual exact: 32.00%
- Confidence Brier: 0.309368
- Actual cost (CNY): 1.405652
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 100.00% | 100.00% |
| L2 | 100.00% | 100.00% |
| L3 | 80.00% | 98.33% |
| L4 | 0.00% | 70.00% |
| L5 | 20.00% | 58.33% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 0.00% |
| L2-L3 | 20.00% |
| L3-L4 | 80.00% |
| L4-L5 | -20.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 68.00%
- State/status internally consistent: 92.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 10 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 7 |
| FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT | 1 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 7 |
