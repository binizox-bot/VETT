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
| L1 | 52.3% | 57.1% | 0.123 | 23.9% |
| L2 | 46.1% | 40.0% | 0.090 | 35.0% |
| L3 | 23.3% | 30.4% | 0.038 | 41.6% |
| L4 | 19.9% | 30.0% | 0.020 | 44.2% |
| L5 | 17.2% | 28.3% | 0.018 | 45.3% |

Overall literal top-k evidence recall: 28.2%.
Overall top-20% document recall: 34.9%.

These are static shortcut diagnostics. They do not replace question-only, ablation or full-model calibration.
