# R26 pre-220 difficulty stability audit

- Status: **EXPANSION_BLOCKED**
- Blocking findings: `['transition_axis_dominance:L2-L3', 'transition_axis_dominance:L3-L4', 'transition_axis_dominance:L4-L5', 'cross_level_anchor_families:0']`
- Current pilot semantics invalidated: False
- Unique structural vectors: 72/100 (72.0%)
- Single-level scenario-family share: 100.0%
- Complete cross-level anchor families: 0

| Transition | Minimum structural delta | Minimum positive axes | Largest dominant-axis share |
|---|---:|---:|---:|
| L1-L2 | 0.065 | 3 | 40.0% |
| L2-L3 | 0.052 | 2 | 100.0% |
| L3-L4 | 0.090 | 2 | 100.0% |
| L4-L5 | 0.107 | 4 | 100.0% |

This report is a structural expansion gate. It cannot be used as an empirical difficulty result and does not alter the frozen metric contract.
