# R25 decision-record model run: glm53_flash_r25_1_question_only5_rescore

- Factual record macro accuracy (primary): 4.00%
- Full-record exact (micro): 4.00%
- Decision-field accuracy (diagnostic): 63.67%
- Latent-state accuracy: 47.20%
- Minimal-evidence F1: 0.00%
- Counterfactual field accuracy: 63.67%
- Counterfactual full-record exact: 4.00%
- Paired factual/counterfactual exact: 0.00%
- Confidence Brier: 0.04
- Actual cost (CNY): 0.069463
- Protocol: C2_TABLE (target batch size 5)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 20.00% | 68.33% |
| L2 | 0.00% | 68.33% |
| L3 | 0.00% | 70.00% |
| L4 | 0.00% | 61.67% |
| L5 | 0.00% | 50.00% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 20.00% |
| L2-L3 | 0.00% |
| L3-L4 | 0.00% |
| L4-L5 | 0.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 76.00%
- State/status internally consistent: 100.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 23 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 1 |
| FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT | 1 |
