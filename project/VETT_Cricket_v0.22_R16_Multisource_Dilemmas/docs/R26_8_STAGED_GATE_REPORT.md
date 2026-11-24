# R26.8 staged economic gate report

Date: 2026-10-19

## Decision

Stop the paid panel after the first GLM request. The free protocol gate succeeded, but the GLM gate produced a schema/protocol failure. No evidence supports spending money on the remaining four matches yet, and this run must not be used to justify increasing dataset difficulty.

## Gate 1: free protocol check

- Model: `Qwen/Qwen3.5-4B`
- Match: `match_0066`
- Batch status: `OK`
- Returned targets: 5/5
- Usage: 101,278 input tokens; 5,493 output tokens
- Cost: CNY 0
- Factual full-record macro accuracy: 0%
- Decision-field macro accuracy: 65%
- Positive evidence-span F1: 12.50%
- Typed evidence-edge F1: 6.45%
- Evidence-chain exact: 0%
- Adjacent field-accuracy gaps: L1-L2 +50.00 pp, L2-L3 -16.67 pp, L3-L4 -25.00 pp, L4-L5 +33.33 pp

Interpretation: the endpoint and bounded response protocol work, but this 4B model is too weak to calibrate benchmark difficulty. The single-match level ordering is not monotonic and is not a dataset-level estimate.

## Gate 2: paid strong-model check

- Model: `zai-org/GLM-5.3-Flash`
- Match: `match_0066`
- Batch status: `INVALID_OUTPUT`
- Provider finish reason: `stop`
- Output truncation: false
- Returned targets: 5/5
- Usage: 91,229 input tokens; 7,675 output tokens
- Actual cost: CNY 0.094473
- Configured ceiling: CNY 0.20
- Validation error: prediction 2 repeats rejected evidence span IDs
- Official semantic coverage: 0/1 matches

The failure was not a timeout or token-limit truncation. One question's `rejected_evidence_spans` array contained invalid repeated material. The runner correctly kept the checkpoint, marked the batch invalid, stopped the run and did not retry.

For debugging only, the parseable factual fields in the invalid checkpoint yielded 1/5 full records, 75% decision-field accuracy, 35.20% positive-span F1 and 27.08% typed-edge F1. These values are not official model scores and must not appear in a benchmark results table.

## What is necessary next

1. Necessary, zero-cost: make the output protocol resilient to a single evidence-list corruption while preserving strict official scoring. Keep protocol status separate from field-level diagnostic recovery.
2. Necessary, zero-cost: add regression fixtures from this exact GLM response and verify that factual diagnostics cannot be mistaken for official evidence-chain scores.
3. Necessary after those checks: run one new GLM request on one match under a new run ID and a hard CNY 0.20 ceiling.
4. Necessary only if that request is fully valid: run the remaining four GLM sentinels.
5. Not necessary now: Step-3.5-Flash, Qwen3.5-35B-A3B, all 20 pilot matches, or the 220-match expansion.

## Dataset conclusion

This experiment validates the cost-control and failure-separation framework. It does not yet validate the target strong-model accuracy or the five-level spacing. Therefore the current evidence supports improving the evaluation protocol first, not making the text harder and not expanding R26.7 to 220 matches.

## Follow-up status

The zero-cost protocol-v2 repair is complete. It adds public-ID and graph-consistency validation, exact target constraints, structural record checks, evidence-only factual diagnostics, a real-failure regression fixture and a new unexecuted single-match gate. See `docs/R26_8_PROTOCOL_V2_REPAIR_REPORT.md`. No API request was made during the repair.
