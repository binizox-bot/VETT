# R25 decision-record model run: glm53_flash_r25_1_match0066_isolated

- Factual record macro accuracy (primary): 60.00%
- Full-record exact (micro): 60.00%
- Decision-field accuracy (diagnostic): 86.67%
- Latent-state accuracy: 96.00%
- Minimal-evidence F1: 80.00%
- Counterfactual field accuracy: 93.33%
- Counterfactual full-record exact: 80.00%
- Paired factual/counterfactual exact: 60.00%
- Confidence Brier: 0.3489
- Actual cost (CNY): 0.169147
- Protocol: C2_ISOLATED (target batch size 1)

| Level | Full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 100.00% | 100.00% |
| L2 | 100.00% | 100.00% |
| L3 | 100.00% | 100.00% |
| L4 | 0.00% | 66.67% |
| L5 | 0.00% | 66.67% |

| Adjacent levels | Exact-accuracy drop |
| --- | ---: |
| L1-L2 | 0.00% |
| L2-L3 | 0.00% |
| L3-L4 | 100.00% |
| L4-L5 | 0.00% |

- Required adjacent drop: 8.00%
- All adjacent drops pass: False
- Structured ledger/schema valid: 80.00%
- State/status internally consistent: 100.00%

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 1 |
| FACTUAL_RECORD_WRONG_COUNTERFACTUAL_CORRECT | 1 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_WRONG | 3 |
