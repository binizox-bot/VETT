# R26 shortcut audit

Status: **PASS**

| Gate | Result |
|---|---|
| no_public_level_labels | PASS |
| no_opaque_r25_identifiers_in_questions | PASS |
| no_normalized_answer_codes_in_questions | PASS |
| no_exact_question_duplicates | PASS |
| no_exact_generated_nonrule_duplicates | PASS |
| generated_role_max_skeleton_share_at_most_30pct | PASS |
| authority_style_macro_f1_at_most_60pct | PASS |
| literal_top_k_recall_below_45pct_for_L3_L5 | PASS |
| top_20pct_document_recall_below_70pct_for_L5 | PASS |
| necessary_document_fraction_above_20pct_for_L4_L5 | PASS |

| Level | Literal top-k evidence recall | Top-20% document recall | Query/fact Jaccard | Necessary-document fraction |
|---|---:|---:|---:|---:|
| L1 | 52.6% | 53.8% | 0.099 | 26.1% |
| L2 | 40.5% | 37.5% | 0.066 | 37.3% |
| L3 | 23.0% | 30.4% | 0.020 | 41.6% |
| L4 | 19.9% | 31.0% | 0.019 | 44.2% |
| L5 | 17.9% | 31.0% | 0.017 | 45.3% |

Overall literal top-k evidence recall: 27.8%.
Overall top-20% document recall: 35.2%.

Authority-style-only leave-one-match-out accuracy: 60.9%.
Authority-style-only macro F1: 54.6%.

| Generated role | Largest normalized surface frame share |
|---|---:|
| authority_conflict | 10.0% |
| authority_policy | 5.0% |
| incident_fact | 1.8% |
| same_case_conflict | 2.8% |
| semantic_bridge | 8.1% |

These are static shortcut diagnostics. They do not replace question-only, ablation or full-model calibration.
