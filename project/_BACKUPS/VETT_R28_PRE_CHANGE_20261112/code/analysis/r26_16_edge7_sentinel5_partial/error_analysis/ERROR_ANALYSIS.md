# R26 structured error analysis: r26_16_glm53_flash_uniform_sentinel5_edge7

- Calibration stage: `sentinel5`
- May trigger dataset changes: **True**
- Scope: Labels are non-exclusive. Single-gate or undeclared runs diagnose the evaluation pipeline only and must not trigger difficulty changes.

## Level diagnostics

| Level | Questions | Factual field accuracy | Full-record exact |
|---|---:|---:|---:|
| L1 | 3 | 100.00% | 66.67% |
| L2 | 3 | 58.33% | 0.00% |
| L3 | 3 | 91.67% | 0.00% |
| L4 | 3 | 79.17% | 0.00% |
| L5 | 3 | 50.00% | 0.00% |

## Matched anchor-by-level diagnostics

| Anchor | Level | Questions | Factual field accuracy | Full-record exact |
|---|---|---:|---:|---:|
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L1 | 1 | 100.00% | 100.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L2 | 1 | 66.67% | 0.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L4 | 1 | 0.00% | 0.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L5 | 1 | 41.67% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L1 | 1 | 100.00% | 100.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L3 | 1 | 0.00% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L2 | 1 | 0.00% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L3 | 1 | 91.67% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L4 | 1 | 91.67% | 0.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L4 | 1 | 66.67% | 0.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L5 | 1 | 58.33% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L1 | 1 | 0.00% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L2 | 1 | 50.00% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L3 | 1 | 91.67% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L5 | 1 | 0.00% | 0.00% |

## Non-exclusive error taxonomy

| Label | Questions |
|---|---:|
| AUTHORITY_RESOLUTION_INCOMPLETE | 10 |
| CONTENT_DEPENDENCY_INCOMPLETE | 9 |
| COUNTERFACTUAL_RECORD_WRONG | 9 |
| COUNTERFACTUAL_STATE_WRONG | 9 |
| CROSS_INCIDENT_EVIDENCE_BINDING | 6 |
| DECISION_PROOF_INCOMPLETE | 10 |
| FACTUAL_RECORD_WRONG | 8 |
| IDENTITY_BINDING_INCOMPLETE | 5 |
| LATENT_STATE_WRONG | 8 |
| MISSING_PREDICTION | 5 |
| POSITIVE_EVIDENCE_EXTRA | 8 |
| POSITIVE_EVIDENCE_MISSING | 10 |
| PROOF_EDGE_EXTRA | 9 |
| PROOF_EDGE_MISSING | 10 |
| REJECTED_EVIDENCE_EXTRA | 2 |
| REJECTED_EVIDENCE_MISSING | 5 |
