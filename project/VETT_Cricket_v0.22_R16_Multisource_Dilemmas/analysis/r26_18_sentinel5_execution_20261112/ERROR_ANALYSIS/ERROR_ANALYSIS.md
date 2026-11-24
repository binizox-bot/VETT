# R26 structured error analysis: r26_18_glm53_canonical_set_sentinel5

- Calibration stage: `sentinel5_collection`
- May trigger dataset changes: **False**
- Scope: Labels are non-exclusive. Single-gate or undeclared runs diagnose the evaluation pipeline only and must not trigger difficulty changes.

## Level diagnostics

| Level | Questions | Factual field accuracy | Full-record exact |
|---|---:|---:|---:|
| L1 | 5 | 100.00% | 100.00% |
| L2 | 5 | 56.67% | 20.00% |
| L3 | 5 | 63.33% | 20.00% |
| L4 | 5 | 60.00% | 0.00% |
| L5 | 5 | 51.67% | 0.00% |

## Matched anchor-by-level diagnostics

| Anchor | Level | Questions | Factual field accuracy | Full-record exact |
|---|---|---:|---:|---:|
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L1 | 1 | 100.00% | 100.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L2 | 1 | 100.00% | 100.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L3 | 1 | 66.67% | 0.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L4 | 1 | 41.67% | 0.00% |
| BOUNDARY_AND_LEDGER_ATTRIBUTION | L5 | 1 | 58.33% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L1 | 1 | 100.00% | 100.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L2 | 1 | 50.00% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L3 | 1 | 50.00% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L4 | 1 | 41.67% | 0.00% |
| CALL_PRECEDENCE_AND_EXTRAS | L5 | 1 | 41.67% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L1 | 1 | 100.00% | 100.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L2 | 1 | 50.00% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L3 | 1 | 100.00% | 100.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L4 | 1 | 91.67% | 0.00% |
| DISMISSAL_AND_APPEAL_CONTROL | L5 | 1 | 41.67% | 0.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L1 | 1 | 100.00% | 100.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L2 | 1 | 41.67% | 0.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L3 | 1 | 41.67% | 0.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L4 | 1 | 66.67% | 0.00% |
| EVENT_ORDER_AND_TERMINAL_STATE | L5 | 1 | 58.33% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L1 | 1 | 100.00% | 100.00% |
| INVALID_DELIVERY_WICKET_GATE | L2 | 1 | 41.67% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L3 | 1 | 58.33% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L4 | 1 | 58.33% | 0.00% |
| INVALID_DELIVERY_WICKET_GATE | L5 | 1 | 58.33% | 0.00% |

## Non-exclusive error taxonomy

| Label | Questions |
|---|---:|
| AUTHORITY_RESOLUTION_INCOMPLETE | 24 |
| CONTENT_DEPENDENCY_INCOMPLETE | 24 |
| COUNTERFACTUAL_LEDGER_INVARIANT_FAILURE | 4 |
| COUNTERFACTUAL_RECORD_WRONG | 22 |
| COUNTERFACTUAL_STATE_WRONG | 21 |
| CROSS_INCIDENT_EVIDENCE_BINDING | 17 |
| DECISION_PROOF_INCOMPLETE | 25 |
| FACTUAL_LEDGER_INVARIANT_FAILURE | 1 |
| FACTUAL_RECORD_WRONG | 18 |
| IDENTITY_BINDING_INCOMPLETE | 14 |
| LATENT_STATE_WRONG | 19 |
| POSITIVE_EVIDENCE_EXTRA | 21 |
| POSITIVE_EVIDENCE_MISSING | 25 |
| PROOF_EDGE_EXTRA | 25 |
| PROOF_EDGE_MISSING | 25 |
| REJECTED_EVIDENCE_EXTRA | 11 |
| REJECTED_EVIDENCE_MISSING | 13 |
| WRONG_RECORD_EQUALS_OTHER_INCIDENT | 8 |
