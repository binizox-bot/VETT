# R25.2 empirical calibration

Final disposition: **PILOT_DELIVERABLE_NOT_PROMOTED**.

- Model: `zai-org/GLM-5.3-Flash`
- Question-only factual record macro: 0.0%
- C2-Table factual record macro: 32.0%
- C2-Isolated factual record macro: 60.0%
- C2-Table minimal-evidence F1: 46.8%
- Final calibration cost known to be incurred: CNY 0.494948

| Level | C2-Table full-record exact | Decision-field accuracy |
| --- | ---: | ---: |
| L1 | 80.0% | 90.0% |
| L2 | 40.0% | 71.7% |
| L3 | 20.0% | 70.0% |
| L4 | 20.0% | 68.3% |
| L5 | 0.0% | 53.3% |

| Gate | Result |
| --- | --- |
| static_audit_pass | PASS |
| question_only_record_macro_le_20pct | PASS |
| table_record_macro_le_65pct | PASS |
| full_input_minus_question_only_ge_10pct | PASS |
| table_exact_nonincreasing_by_level | PASS |
| table_field_strictly_decreasing_by_level | PASS |
| all_adjacent_exact_gaps_ge_8pct | FAIL |
| two_model_families_tested | FAIL |

The pilot is deliverable for research and error analysis, but it is not approved for 220-match expansion. The adjacent L3-L4 exact gap is zero, only one model family was tested, and isolated estimates have one item per level. These limitations must accompany any paper claim.
