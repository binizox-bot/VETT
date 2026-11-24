# R26.17 Edge7 four-match diagnostic ledger

- Status: `DIAGNOSTIC_ONLY_INCOMPLETE_COHORT`
- Dataset mutation authorized: no
- Frozen primary: 71.67%
- Informative fields: 62.22%
- Informative value-balanced: 38.83%

The raw primary is 9.44 points above the informative-field score. Therefore the 71.67% result must not be interpreted as pure document understanding or used to justify global hardening.

## Most frequent factual field errors

| Field | Error questions | Accuracy over 20 |
|---|---:|---:|
| `bowler_runs` | 12 | 40.00% |
| `dismissal` | 11 | 45.00% |
| `total_runs` | 11 | 45.00% |
| `batter_runs` | 8 | 60.00% |
| `ledger.BATTER` | 8 | 60.00% |
| `delivery_status` | 7 | 65.00% |
| `counts_in_over` | 5 | 75.00% |
| `ledger.WIDE_EXTRA` | 3 | 85.00% |

## Candidate contributors to the L2→L3 inversion

| Field | L2 errors | L3 errors | L3 ease contribution (points) |
|---|---:|---:|---:|
| `total_runs` | 3 | 1 | 50.00 |
| `batter_runs` | 2 | 1 | 25.00 |
| `bowler_runs` | 3 | 2 | 25.00 |
| `delivery_status` | 2 | 1 | 25.00 |
| `ledger.BATTER` | 2 | 1 | 25.00 |
| `ledger.NO_BALL_EXTRA` | 1 | 0 | 25.00 |
| `ledger.WIDE_EXTRA` | 1 | 0 | 25.00 |

Every level is missing one matched anchor family, so the raw L2–L3 difference is composition-confounded. These are candidate mechanisms from four matches, not edit instructions. Complete protocol-valid replication is required before changing any scenario or text.
