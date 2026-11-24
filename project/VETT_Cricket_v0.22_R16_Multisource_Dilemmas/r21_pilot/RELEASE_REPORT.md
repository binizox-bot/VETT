# VETT-Cricket R21 Evidence-Chain Pilot

## Release decision

**PASS** — 20/20 selected independent matches passed all machine gates.

## Scale

- Direct value targets: 7944
- Typed evidence claims: 22326
- Required evidence spans: 22326
- Required graph edges: 12778
- Public documents: 690
- Public words: 540567

## Mechanisms

The pilot mixes one-step and two-step supersession, copied-majority traps, explicit
retraction with independent replacement, and coordinate-scoped amendment. Public evidence
uses semantic row/table/column descriptions rather than literal target or table IDs.

| Public-only heuristic | Correct | Accuracy |
| --- | ---: | ---: |
| first_public_value | 3259/7944 | 41.02% |
| last_public_value | 3313/7944 | 41.70% |
| majority_value | 3346/7944 | 42.12% |

No external model result is included. The intended calibration target remains about 75%
for strong-model answer accuracy, with evidence and joint accuracy lower; this must be
measured by blind runs through the unified runner.
