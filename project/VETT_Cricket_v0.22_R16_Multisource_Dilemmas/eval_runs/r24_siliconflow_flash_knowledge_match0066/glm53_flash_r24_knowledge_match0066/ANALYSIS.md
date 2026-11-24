# R24 one-match GLM-5.3-Flash evaluation

## Scope

- Release: `dataset_r24_220`
- Instance: `match_0066`
- Track: R24 knowledge/evidence/counterfactual only; open QA and table reconstruction were intentionally not run.
- Model: `zai-org/GLM-5.3-Flash`
- Requests: one batch containing five questions, one from each of L1-L5.

## Result

| Metric | Result |
| --- | ---: |
| Fact answer exact | 5/5 (100%) |
| Reasoning-atom micro F1 | 100% |
| Decisive-span micro F1 | 100% |
| Misleading-span micro F1 | 100% |
| Scope assignment | 100% |
| Counterfactual answer | 5/5 (100%) |
| Full answer+atoms+evidence+counterfactual joint exact | 5/5 (100%) |
| Confidence Brier | 0.0025 |

All five levels were completely correct. This single match therefore provides no evidence for an adjacent-level accuracy gap.

## Cost

- Input tokens: 83,812
- Output tokens: 5,379
- Total tokens: 89,191
- Actual cost: CNY 0.082111
- Preflight zero-cache estimate: CNY 0.1166
- Hard ceiling: CNY 0.15

## Comparison with the earlier R23.1 run on the same match

R23.1 also had 5/5 factual answers and 100% reasoning atoms, but only 92.31% decisive-span F1, 40% misleading-span F1 and 40% joint exact. R24 reached 100% on all of those fields. On this matched example, the R24 rule/evidence track became easier for the model rather than harder.

## Diagnosis

The result exposes two construction shortcuts. First, decisive fragments often state the complete legal conclusion directly. Second, misleading fragments explicitly describe themselves as non-authoritative or not controlling, making role classification nearly lexical. The evidence-ablation counterfactual also always removes every decisive span and asks whether support remains, so `NO_UNDERDETERMINED` is mechanically predictable.

The run is only one match and cannot estimate full-corpus accuracy, but a perfect L1-L5 result is a strong warning that the intended strong-model ceiling of 65% is not yet demonstrated and is unlikely to be met without revising the evidence wording and counterfactual construction.
