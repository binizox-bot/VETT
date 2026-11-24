# R26 shortcut audit

Status: **FAIL**

| Gate | Result |
|---|---|
| no_public_level_labels | PASS |
| no_opaque_r25_identifiers_in_questions | PASS |
| no_normalized_answer_codes_in_questions | PASS |
| no_exact_question_duplicates | PASS |
| no_exact_generated_nonrule_duplicates | PASS |
| generated_role_max_skeleton_share_at_most_30pct | PASS |
| authority_style_macro_f1_at_most_60pct | FAIL |
| literal_top_k_recall_below_45pct_for_L3_L5 | PASS |
| top_20pct_document_recall_below_70pct_for_L5 | PASS |
| necessary_document_fraction_above_20pct_for_L4_L5 | PASS |

| Level | Literal top-k evidence recall | Top-20% document recall | Query/fact Jaccard | Necessary-document fraction |
|---|---:|---:|---:|---:|
| L1 | 52.6% | 53.2% | 0.110 | 26.1% |
| L2 | 42.1% | 38.3% | 0.079 | 37.3% |
| L3 | 22.8% | 29.0% | 0.027 | 41.6% |
| L4 | 20.4% | 30.7% | 0.022 | 44.2% |
| L5 | 17.4% | 30.0% | 0.021 | 45.3% |

Overall literal top-k evidence recall: 28.1%.
Overall top-20% document recall: 34.6%.

Authority-style-only leave-one-match-out accuracy: 80.9%.
Authority-style-only balanced accuracy: 87.8%.
Authority-style-only macro F1: 77.7%.

| Generated role | Largest normalized surface frame share |
|---|---:|
| authority_conflict | 30.0% |
| authority_policy | 7.5% |
| incident_fact | 7.9% |
| same_case_conflict | 12.8% |
| semantic_bridge | 8.1% |

These are static shortcut diagnostics. They do not replace question-only, ablation or full-model calibration.
