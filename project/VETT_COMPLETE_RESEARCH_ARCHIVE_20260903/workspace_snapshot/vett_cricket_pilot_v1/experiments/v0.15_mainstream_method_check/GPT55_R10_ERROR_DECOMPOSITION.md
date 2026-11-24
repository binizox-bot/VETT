# GPT-5.5 R10 blind evaluation: error decomposition

| Method | Strict error | Scalar-core error | Partnership composite errors | Share of all errors |
| --- | ---: | ---: | ---: | ---: |
| direct_no_cot | 30.36% | 18/232 (7.76%) | 62 | 60.78% |
| direct_cot | 24.70% | 0/232 (0.00%) | 62 | 74.70% |
| t3_paper_direct_integration_variant | 33.33% | 27/232 (11.64%) | 62 | 55.36% |
| t3_provenance_enhanced | 25.30% | 0/232 (0.00%) | 62 | 72.94% |
| mapmake_paper_style | 24.70% | 0/232 (0.00%) | 62 | 74.70% |
| mapmake_scope_version_enhanced | 24.70% | 0/232 (0.00%) | 62 | 74.70% |

## Audit finding

The fixed-schema public contract leaves the exact semantics of several composite columns unspecified. The strict score remains reproducible, but it cannot be interpreted as a pure state-reasoning failure rate.

The public commentary contains neither `Samuel Moore` nor a referee label. The Referee gold cell is unsupported and must be removed or evidenced.

The scalar-core slice contains 232 cells with unambiguous numeric or categorical targets. It is diagnostic and post-hoc, so it must be reported as an error analysis rather than a replacement leaderboard.
