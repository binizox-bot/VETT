# R25 decision-record model run: glm53_flash_r25_1_calibration5

- Factual record macro accuracy (primary): 24.00%
- Full-record exact (micro): 24.00%
- Decision-field accuracy (diagnostic): 71.00%
- Latent-state accuracy: 72.80%
- Minimal-evidence F1: 39.06%
- Counterfactual field accuracy: 66.67%
- Counterfactual full-record exact: 24.00%
- Paired factual/counterfactual exact: 20.00%
- Confidence Brier: 0.639664
- Actual cost (CNY): 0.485197
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 60.00% | 86.67% |
| L2 | 40.00% | 88.33% |
| L3 | 20.00% | 71.67% |
| L4 | 0.00% | 56.67% |
| L5 | 0.00% | 51.67% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 20.00% |
| L2-L3 | 20.00% |
| L3-L4 | 20.00% |
| L4-L5 | 0.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 56.00%
- State/status internally consistent: 84.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 18 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 1 |
| FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT | 1 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 5 |
