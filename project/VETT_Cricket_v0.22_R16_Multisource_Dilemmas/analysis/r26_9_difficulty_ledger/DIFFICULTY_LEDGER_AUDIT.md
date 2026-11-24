# R26.9 private difficulty-feature ledger audit

- Status: **PASS**
- Rows: 100 questions across 20 matches
- Level balance: {'L1': 20, 'L2': 20, 'L3': 20, 'L4': 20, 'L5': 20}
- Scenario families: 25; every family occurs four times
- Public level leaks: 0
- Difficulty-vector reproduction errors: 0
- Exact duplicate rows: 0
- Ledger SHA-256: `3e5fcb4113c9a37f05300712cfd9f71c07fc5cd36d9a46b1577b6c3dd0a0d134`

| Level | Binding | Authority/conflict | Rule | Temporal | Evidence | Counterfactual | Structural index |
|---|---:|---:|---:|---:|---:|---:|---:|
| L1 | 0.100 | 0.125 | 0.317 | 0.000 | 0.422 | 0.444 | 0.235 |
| L2 | 0.367 | 0.125 | 0.619 | 0.000 | 0.625 | 0.589 | 0.388 |
| L3 | 0.467 | 0.125 | 0.661 | 0.500 | 0.743 | 0.667 | 0.527 |
| L4 | 0.733 | 0.875 | 0.681 | 0.500 | 0.785 | 0.667 | 0.707 |
| L5 | 1.000 | 1.000 | 0.764 | 1.000 | 0.850 | 0.767 | 0.897 |

Raw feature crossovers are intentional audit findings, not failures. They preserve mechanism diversity; only the aggregate structural index is required to increase strictly. This ledger is private and must not be packaged with public inputs.
