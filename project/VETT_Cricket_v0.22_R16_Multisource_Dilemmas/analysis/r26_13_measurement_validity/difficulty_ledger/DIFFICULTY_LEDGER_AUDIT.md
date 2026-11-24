# R26.9 private difficulty-feature ledger audit

- Status: **PASS**
- Rows: 100 questions across 20 matches
- Level balance: {'L1': 20, 'L2': 20, 'L3': 20, 'L4': 20, 'L5': 20}
- Scenario families: 25; every family occurs four times
- Public level leaks: 0
- Difficulty-vector reproduction errors: 0
- Exact duplicate rows: 0
- Ledger SHA-256: `cbdcdb197911b6d2daf4dbcc0ffea4cdc78f617c3f72b17fdedc845e52a22933`

| Level | Binding | Authority/conflict | Rule | Temporal | Evidence | Counterfactual | Structural index |
|---|---:|---:|---:|---:|---:|---:|---:|
| L1 | 0.100 | 0.625 | 0.317 | 0.100 | 0.422 | 0.444 | 0.335 |
| L2 | 0.367 | 0.625 | 0.619 | 0.000 | 0.625 | 0.589 | 0.471 |
| L3 | 0.467 | 0.625 | 0.661 | 0.300 | 0.743 | 0.667 | 0.577 |
| L4 | 0.733 | 0.875 | 0.681 | 0.800 | 0.785 | 0.667 | 0.757 |
| L5 | 1.000 | 1.000 | 0.764 | 0.900 | 0.850 | 0.767 | 0.880 |

Raw feature crossovers are intentional audit findings, not failures. They preserve mechanism diversity; only the aggregate structural index is required to increase strictly. This ledger is private and must not be packaged with public inputs.
