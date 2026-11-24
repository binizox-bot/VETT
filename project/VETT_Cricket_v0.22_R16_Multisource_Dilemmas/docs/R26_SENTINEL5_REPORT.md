# R26 paired five-match sentinel

Status: **REVISE**

| Model | Factual exact | Evidence F1 | Paired exact | R26 L1/L2/L3/L4/L5 |
|---|---:|---:|---:|---:|
| zai-org/GLM-5.3-Flash | 32% → 40% | 46.8% → 67.6% | 20% → 36% | 80%/80%/20%/0%/20% |
| deepseek-ai/DeepSeek-V4.1-Flash | 40% → 60% | 58.0% → 57.6% | 28% → 32% | 100%/100%/80%/0%/20% |

| Gate | Result |
|---|---|
| all_models_below_65pct_factual | PASS |
| no_model_factual_regression | FAIL |
| no_model_evidence_regression | FAIL |
| no_model_paired_regression | FAIL |
| all_models_adjacent_gap_pass | FAIL |

Five questions per level imply 20-point resolution. This sentinel is a gate, not a final level-effect estimate.
