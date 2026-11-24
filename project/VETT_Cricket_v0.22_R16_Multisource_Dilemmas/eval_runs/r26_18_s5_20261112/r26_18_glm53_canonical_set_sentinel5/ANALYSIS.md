# R26 decision-and-proof-graph model run: r26_18_glm53_canonical_set_sentinel5

- Sentinel completion: 5/5 scoreable; 5/5 attempted
- Sentinel status: COMPLETE
- Protocol evaluation: COMPLETE_SEMANTIC_COVERAGE
- Stop reason: none
- Factual record macro accuracy: 28.00%
- Decision-field accuracy: 66.33%
- Minimal evidence-span F1: 45.22%
- Rejected evidence-span F1: 43.04%
- Minimal typed-edge F1: 29.93%
- Unknown evidence question rate: 0.00%
- Unknown evidence span references: 0
- Typed edges touching unknown evidence: 0
- Span-and-edge chain exact: 0.00%
- Factual-record-and-chain exact: 0.00%
- Output-conformance question rate: 92.00%
- Factual-record-and-chain-and-conformance exact: 0.00%
- Paired factual/counterfactual exact: 12.00%
- Actual cost (CNY): 0.649936
- Protocol: C2_TABLE (target batch size 5)

| Level | Record exact | Field accuracy | Edge F1 |
| --- | ---: | ---: | ---: |
| L1 | 100.00% | 100.00% | 67.48% |
| L2 | 20.00% | 56.67% | 35.10% |
| L3 | 20.00% | 63.33% | 20.08% |
| L4 | 0.00% | 60.00% | 12.95% |
| L5 | 0.00% | 51.67% | 29.17% |

| Outcome | Count |
| --- | ---: |
| BOTH_RECORDS_WRONG | 18 |
| FACTUAL_RECORD_CORRECT_COUNTERFACTUAL_WRONG | 4 |
| RECORD_PAIR_CORRECT_TRACE_OR_EVIDENCE_GRAPH_WRONG | 3 |
