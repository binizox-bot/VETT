# R26.9 Gate4 edge-derived protocol result

- Model: `zai-org/GLM-5.3-Flash`
- Instance: `match_0066`
- Evidence-role protocol: `edge_derived_v3`
- Evaluation contract: `R26-C3-EDGE-4-DERIVED-REJECTION`
- Requested/returned targets: 5/5
- Batch status: `OK`
- Semantic coverage: `COMPLETE_SEMANTIC_COVERAGE`
- Frozen single-match gate: `PASS`
- Officially eligible: yes
- Difficulty conclusion permitted: no
- Finish reason: `stop`
- Provider truncation: no
- JSON closure repair: no
- Parse error: no
- Elapsed time: 65.943134 seconds
- Usage: 91,309 input tokens; 9,819 output tokens; 101,128 total tokens
- Actual cost: CNY 0.100540

## Semantic scores

- Decision-field accuracy: 70.00%
- Factual full-record accuracy: 20.00%
- Counterfactual field accuracy: 68.33%
- Paired factual/counterfactual exact: 20.00%
- Positive evidence span F1: 39.39%
- Rejected evidence span F1: 26.67%
- Typed evidence edge F1: 31.00%
- Evidence-chain joint exact: 0.00%
- Factual/evidence-chain joint exact: 0.00%
- Confidence Brier score: 0.6929

The low evidence scores and zero joint-exact scores demonstrate that deriving the rejected span set
from `rejects` edges did not repair the model's reasoning. It only prevented a redundant field mismatch
from converting a semantic evidence error into an unscoreable protocol failure.

## Private level diagnostic

Decision-field accuracy for this single match was L1 100.00%, L2 41.67%, L3 58.33%, L4 91.67%,
and L5 58.33%. This curve is non-monotonic, but the frozen metric contract explicitly prohibits a
single match from establishing level ordering or triggering dataset changes.

## Decision

The single-match protocol gate is passed. A fixed five-match Sentinel may now be considered, but it
must be separately authorized and remains a screen rather than a paper-level estimate.
