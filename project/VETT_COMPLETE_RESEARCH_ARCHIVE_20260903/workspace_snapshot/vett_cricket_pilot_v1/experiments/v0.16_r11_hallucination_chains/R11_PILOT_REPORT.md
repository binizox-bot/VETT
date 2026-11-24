# R11 hallucination-chain pilot

## Purpose

This one-root pilot tests whether a system can distinguish official facts from plausible but source-scoped false claims. False claims occur in provisional graphics, replay shadows and stale post-match widgets; no false claim is treated as gold. Composite cricket fields are atomized before scoring.

## Scale

- Root: `match_0007`
- Documents: 4
- Segments: 162
- Whitespace-tokenized words: 5657
- Atomic scored cells: 107
- Claim records: 428 (321 false, 107 true candidates)
- False:true claim ratio: 3.0:1
- Evidence path: candidate card → custody leaf → seal → signed audit, plus a cross-table check

## Deterministic diagnostics

| Policy | Cell error rate | Blank rate |
| --- | ---: | ---: |
| oracle_chain_following | 0.00% | 0.00% |
| first_numeric_or_string_claim | 100.00% | 0.00% |
| latest_mention | 100.00% | 0.00% |
| source_blind_claim_majority | 100.00% | 0.00% |
| always_candidate_A | 50.47% | 0.00% |
| always_candidate_B | 49.53% | 0.00% |
| authority_without_link_resolution | 100.00% | 100.00% |

These policies are diagnostic ablations, not model results. They show that recency, repetition, first mention and fixed candidate position do not solve the pilot. A new blind T3/MapMake/CoT/frontier-model run is required before claiming method-level error rates.

## Integrity gates

All 10 automated gates passed. Every cell has a distinct decoy, a true candidate, two false mentions, a four-hop adjudication chain spanning at least two documents, cross-table evidence, and a canonical scorecard origin. Candidate A/B authority is balanced at 53/54 cells.

## Remaining research risks

The dossier is deliberately regular because this is a structural pilot. Before scaling to 217 roots, vary document genres, chain topology, number of candidates, authority language and placement; then run human uniqueness/support review. Otherwise a model may learn the generator fingerprint instead of evidence reasoning.
