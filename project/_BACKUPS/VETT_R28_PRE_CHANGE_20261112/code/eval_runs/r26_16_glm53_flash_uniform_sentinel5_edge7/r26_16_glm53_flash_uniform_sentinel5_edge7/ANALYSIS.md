# R26 decision-and-proof-graph model run: r26_16_glm53_flash_uniform_sentinel5_edge7

- Sentinel completion: 2/5 scoreable; 3/5 attempted
- Sentinel status: INCOMPLETE — subset metrics only; do not report as a complete Sentinel5 result
- Protocol evaluation: PARTIAL_SEMANTIC_COVERAGE
- Stop reason: match_0067 returned terminal batch status(es): ERROR
- Factual record macro accuracy: 20.00%
- Decision-field accuracy: 75.83%
- Minimal evidence-span F1: 55.80%
- Rejected evidence-span F1: 70.27%
- Minimal typed-edge F1: 47.47%
- Unknown evidence question rate: 0.00%
- Unknown evidence span references: 0
- Typed edges touching unknown evidence: 0
- Span-and-edge chain exact: 0.00%
- Factual-record-and-chain exact: 0.00%
- Paired factual/counterfactual exact: 10.00%
- Actual cost (CNY): 0.227339
- Protocol: C2_TABLE (target batch size 5)

| Level | Record exact | Field accuracy | Edge F1 |
| --- | ---: | ---: | ---: |
| L1 | 100.00% | 100.00% | 72.41% |
| L2 | 0.00% | 58.33% | 59.52% |
| L3 | 0.00% | 91.67% | 40.00% |
| L4 | 0.00% | 79.17% | 40.71% |
| L5 | 0.00% | 50.00% | 38.10% |

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 8 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 1 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_GRAPH_WRONG | 1 |
