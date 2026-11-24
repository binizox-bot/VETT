# R20 Model Run Analysis: oracle_smoke

## Outcome

- Micro cell exact: 100.00%
- Macro match cell accuracy: 100.00%
- Row exact: 100.00%
- Table exact: 100.00%
- Match exact: 100.00%
- Missing cells: 0
- Extra cells: 0

## Error taxonomy

| Category | Count |
| --- | ---: |
| CORRECT | 783 |

`STALE_REVISION` means the model selected an explicitly superseded value.
`ROW_MISALIGNMENT` and `CROSS_INNINGS_CONFUSION` identify values copied from another
valid coordinate. `FORMAT_ONLY` is semantically equivalent after conservative
normalization but still fails exact match. `UNSUPPORTED_VALUE` matches none of these.
