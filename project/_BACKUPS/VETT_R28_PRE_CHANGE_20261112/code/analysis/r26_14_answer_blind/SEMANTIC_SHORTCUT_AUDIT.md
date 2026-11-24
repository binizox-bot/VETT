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
| L1 | 38.8% | 43.3% | 0.187 | 26.1% |
| L2 | 28.9% | 32.1% | 0.150 | 37.3% |
| L3 | 18.0% | 27.5% | 0.105 | 41.6% |
| L4 | 21.0% | 31.0% | 0.122 | 44.2% |
| L5 | 17.9% | 29.3% | 0.104 | 45.3% |

Overall literal top-k evidence recall: 23.2%.
Overall top-20% document recall: 31.7%.

Authority-style-only leave-one-match-out accuracy: 34.6%.
Authority-style-only balanced accuracy: 57.5%.
Authority-style-only macro F1: 34.2%.

| Generated role | Largest normalized surface frame share |
|---|---:|
| authority_conflict | 10.0% |
| authority_policy | 2.5% |
| incident_fact | 1.7% |
| same_case_conflict | 2.8% |
| semantic_bridge | 8.8% |

These are static shortcut diagnostics. They do not replace question-only, ablation or full-model calibration.
