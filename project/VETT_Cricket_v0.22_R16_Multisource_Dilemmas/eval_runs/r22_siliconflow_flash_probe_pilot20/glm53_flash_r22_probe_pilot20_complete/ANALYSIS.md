# R22 Model Run Analysis: glm53_flash_r22_probe_pilot20_complete

- Probe answer exact / FAM: 57.20% / 57.20%
- Answer + decisive proof exact (ASP): 13.20%
- Decisive span / edge F1: 69.67% / 61.22%
- Provenance span / edge F1: 2.15% / 0.86%
- Brier score: 0.412633
- Actual cost (CNY): 3.365486

## Accuracy by level

| Level | FAM | ASP |
| --- | ---: | ---: |
| L1 | 79.00% | 39.00% |
| L2 | 63.00% | 14.00% |
| L3 | 67.00% | 12.00% |
| L4 | 46.00% | 1.00% |
| L5 | 31.00% | 0.00% |

## Accuracy by target family

| Target family | FAM | ASP |
| --- | ---: | ---: |
| cell_value | 93.00% | 7.00% |
| entity_scope | 74.00% | 19.00% |
| event_state | 34.00% | 15.00% |
| derived_indicator | 60.00% | 14.00% |
| consistency_provenance | 25.00% | 11.00% |

## Adjacent-level separation

| Pair | Accuracy drop |
| --- | ---: |
| L1->L2 | 16.00% |
| L2->L3 | -4.00% |
| L3->L4 | 21.00% |
| L4->L5 | 15.00% |

- Required minimum drop: 8.00%
- Pass: False

## Outcome categories

| Category | Count |
| --- | ---: |
| ANSWER_AND_PROOF_CORRECT | 66 |
| ANSWER_AND_PROOF_WRONG | 202 |
| ANSWER_CORRECT_PROOF_INCOMPLETE | 220 |
| PROOF_CORRECT_ANSWER_WRONG | 12 |
