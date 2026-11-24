# R26.9 Gate3 protocol result

- Model: `zai-org/GLM-5.3-Flash`
- Instance: `match_0066`
- Requested/returned targets: 5/5
- Runner status: `INVALID_OUTPUT`
- Frozen metric gate: `INELIGIBLE_PROTOCOL`
- Officially scored instances: 0/1
- Difficulty conclusion permitted: no
- Finish reason: `stop`
- Provider truncation: no
- JSON closure repair: no
- Elapsed time: 57.544435 seconds
- Usage: 91,305 input tokens; 8,282 output tokens; 99,587 total tokens
- Actual cost: CNY 0.096234

## Failure diagnosis

The terminal validation error was `prediction 2 rejected evidence spans do not match rejects edges`.
All five requested predictions were present. Four predictions maintained the explicit cross-field
invariant. For question `r25q_f5e0fd0fce0d982bd9` (private level L3), the model returned rejected
span `r25shadow_7970fa304e678bc1ce55` and no `rejects` edge. The private gold requires rejected
span `r25shadow_a733f32cf3e9efb8c7ba`, targeted by a `rejects` edge from
`r26bridge_28d22c7976c5c356d0a0`.

This is a cross-incident evidence-binding error plus a missing proof edge, not transport truncation,
JSON damage, or a validator false positive. The failure must remain protocol-invalid; repairing or
deriving the missing evidence after generation would hide the capability being evaluated.

## Non-official diagnostic

Complete factual fields could be recovered for diagnostics only. Their decision-field accuracy was
81.6667%. This value is excluded from official benchmark tables, difficulty gates, and dataset
changes because the evidence protocol failed.

## Decision

Do not launch Sentinel5 with this unchanged model/configuration. Do not change dataset difficulty
from this run. Preserve the receipt and use it as evidence that the current model/configuration does
not yet satisfy the single-match proof-graph protocol gate.

The forward-only correction is documented in `docs/R26_9_PROTOCOL_FAILURE_CORRECTION.md`.
It introduces `edge_derived_v3` as a new request contract and does not alter this v2 result.
