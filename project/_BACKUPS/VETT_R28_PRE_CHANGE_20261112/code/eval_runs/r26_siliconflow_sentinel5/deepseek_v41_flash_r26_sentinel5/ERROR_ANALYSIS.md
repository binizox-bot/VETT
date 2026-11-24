# R25 structured error analysis: deepseek_v41_flash_r26_sentinel5

Labels are non-exclusive. This report deliberately does not infer free-text explanation contradictions.

## Factual exact by level

| Level | Correct | Accuracy |
| --- | ---: | ---: |
| L1 | 5/5 | 100.00% |
| L2 | 5/5 | 100.00% |
| L3 | 4/5 | 80.00% |
| L4 | 0/5 | 0.00% |
| L5 | 1/5 | 20.00% |

## Error taxonomy

| Error | Questions |
| --- | ---: |
| COUNTERFACTUAL_LEDGER_INVARIANT_FAILURE | 6 |
| COUNTERFACTUAL_RECORD_WRONG | 17 |
| CROSS_INCIDENT_CITATION | 7 |
| EVIDENCE_INCOMPLETE | 25 |
| EVIDENCE_OVERINCLUSIVE | 8 |
| FACTUAL_LEDGER_INVARIANT_FAILURE | 3 |
| FACTUAL_RECORD_WRONG | 10 |
| WRONG_RECORD_EQUALS_OTHER_GOLD | 2 |

## Factual field errors

| Field | Errors |
| --- | ---: |
| bowler_runs | 9 |
| batter_runs | 8 |
| ledger.BATTER | 8 |
| total_runs | 8 |
| delivery_status | 3 |
| ledger.NO_BALL_EXTRA | 3 |
| dismissal | 2 |
| counts_in_over | 2 |
| ledger.WIDE_EXTRA | 1 |
