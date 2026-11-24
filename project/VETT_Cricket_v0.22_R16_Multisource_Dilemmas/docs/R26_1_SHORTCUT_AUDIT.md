# R26 shortcut audit

Status: **PASS**

| Gate | Result |
|---|---|
| no_public_level_labels | PASS |
| no_opaque_r25_identifiers_in_questions | PASS |
| no_normalized_answer_codes_in_questions | PASS |
| no_exact_question_duplicates | PASS |
| no_exact_generated_nonrule_duplicates | PASS |
| literal_top_k_recall_below_45pct_for_L3_L5 | PASS |
| top_20pct_document_recall_below_70pct_for_L5 | PASS |
| necessary_document_fraction_above_20pct_for_L4_L5 | PASS |

| Level | Literal top-k evidence recall | Top-20% document recall | Query/fact Jaccard | Necessary-document fraction |
|---|---:|---:|---:|---:|
| L1 | 41.3% | 45.7% | 0.071 | 26.6% |
| L2 | 21.1% | 31.9% | 0.028 | 36.9% |
| L3 | 23.9% | 32.2% | 0.028 | 41.6% |
| L4 | 20.7% | 32.8% | 0.024 | 44.2% |
| L5 | 19.6% | 31.0% | 0.022 | 45.3% |

Overall literal top-k evidence recall: 23.7%.
Overall top-20% document recall: 33.8%.

These are static shortcut diagnostics. They do not replace question-only, ablation or full-model calibration.
