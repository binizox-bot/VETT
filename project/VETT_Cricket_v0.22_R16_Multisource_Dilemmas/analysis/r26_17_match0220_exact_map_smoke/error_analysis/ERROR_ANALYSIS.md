# R26 structured error analysis: r26_17_glm53_match0220_exact_map_smoke

- Calibration stage: `single_protocol_gate`
- May trigger dataset changes: **False**
- Scope: Labels are non-exclusive. Single-gate or undeclared runs diagnose the evaluation pipeline only and must not trigger difficulty changes.

## Level diagnostics

| Level | Questions | Factual field accuracy | Full-record exact |
|---|---:|---:|---:|
| L1 | 1 | 100.00% | 100.00% |
| L2 | 1 | 41.67% | 0.00% |
| L3 | 1 | 41.67% | 0.00% |
| L4 | 1 | 41.67% | 0.00% |
| L5 | 1 | 41.67% | 0.00% |

## Matched anchor-by-level diagnostics

| Anchor | Level | Questions | Factual field accuracy | Full-record exact |
|---|---|---:|---:|---:|
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L3 | 1 | 41.67% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L4 | 1 | 41.67% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L5 | 1 | 41.67% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L1 | 1 | 100.00% | 100.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L2 | 1 | 41.67% | 0.00% |

## Non-exclusive error taxonomy

| Label | Questions |
|---|---:|
| AUTHORITY_RESOLUTION_INCOMPLETE | 5 |
| CONTENT_DEPENDENCY_INCOMPLETE | 5 |
| COUNTERFACTUAL_LEDGER_INVARIANT_FAILURE | 2 |
| COUNTERFACTUAL_RECORD_WRONG | 4 |
| COUNTERFACTUAL_STATE_WRONG | 4 |
| CROSS_INCIDENT_EVIDENCE_BINDING | 4 |
| DECISION_PROOF_INCOMPLETE | 5 |
| FACTUAL_LEDGER_INVARIANT_FAILURE | 2 |
| FACTUAL_RECORD_WRONG | 4 |
| IDENTITY_BINDING_INCOMPLETE | 2 |
| LATENT_STATE_WRONG | 4 |
| POSITIVE_EVIDENCE_EXTRA | 5 |
| POSITIVE_EVIDENCE_MISSING | 5 |
| PROOF_EDGE_EXTRA | 5 |
| PROOF_EDGE_MISSING | 5 |
| REJECTED_EVIDENCE_EXTRA | 2 |
| REJECTED_EVIDENCE_MISSING | 3 |
| WRONG_RECORD_EQUALS_OTHER_INCIDENT | 1 |
