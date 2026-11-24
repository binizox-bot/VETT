# Map&Make progressive blind self-test

Date: 2026-07-22

## Protocol

The prediction side was restricted to the three-stage Map&Make pattern:

1. atomize the input into propositions;
2. construct the output schema from those propositions;
3. fill the tables proposition by proposition.

It did not use an explicit event ledger, NEW/DUPLICATE/REVISE classifier,
rollback state, semantic repair pass, SAT solver or integer-programming solver.
Gold JSON was generated but not read until after each prediction file had been
written. A deterministic scorer then compared every scalar field.

The method framing follows the official
[Map&Make ACL 2025 paper](https://aclanthology.org/2025.acl-long.1460/) and
[official implementation](https://github.com/coral-lab-asu/map-make).

## Results

| Level | Main added difficulty | Correct / total | Field accuracy | Table exact match |
| --- | --- | ---: | ---: | --- |
| 1 | Explicit delivery keys; ordinary late correction | 31 / 31 | 100% | Pass |
| 2 | More deliveries, duplicates, archives, three corrections | 40 / 40 | 100% | Pass |
| 3 | No delivery keys; semantic correction references; stale replay | 52 / 52 | 100% | Pass |
| 4 | 10 overs; cross-table propagation; partnerships; run-out reattribution | 106 / 106 | 100% | Pass |
| 5 | 14 binary packet readings; 10 overlapping audit constraints | 84 / 84 | 100% | Pass |
| 6 | 24 binary packet readings; 13 overlapping audit constraints; 12 overs | 84 / 127 | **66.14%** | **Fail** |

Level 6 produced 43 supported-but-blank cells, a blank/error rate of **33.86%**.
The generator verified that the full audit system had exactly one solution, so
the blank cells were not caused by missing evidence.

## Level-6 error propagation

| Affected table | Blank supported cells |
| --- | ---: |
| Innings summary | 2 |
| Batting runs | 6 |
| Bowling runs conceded | 12 |
| Fall-of-wicket scores | 5 |
| Partnership runs, extras and end scores | 18 |
| **Total** | **43** |

The certain parts remained correct: legal-ball counts, wicket identities,
bowler wicket credits, batter participation, partnership boundaries and the
one batter whose runs did not depend on a corrupted packet.

## Interpretation

The failure boundary was not ordinary noise, paraphrase, duplicate commentary
or a small number of corrections. Those survived through Level 4. It was also
not a modest globally coupled puzzle: the model solved Level 5.

The clear break occurred when many locally unresolved alternatives had to be
selected jointly from overlapping global constraints. Atomization preserved
the alternatives and audits, but proposition-by-proposition filling had no
persistent constraint state in which to solve them. One unresolved event then
propagated into batting, bowling, fall-of-wicket and partnership cells.

This supports a benchmark axis called **globally constrained event recovery**:
all evidence is present, the answer is unique, local propositions are
insufficient, and one event decision has measurable cross-table consequences.

## Recommended dataset route

Use three complementary strata:

1. **Natural revision stratum** — real or realistically generated commentary
   with duplicate feeds, stale replays, late scoring corrections and no
   explicit event IDs.
2. **Topology/propagation stratum** — corrections to event identity, batter or
   bowler attribution, wicket method and partnership boundary, requiring every
   dependent table to update.
3. **Globally constrained recovery stratum** — corrupted alternatives resolved
   only through overlapping official checks or aggregates. Keep the constraint
   language domain-plausible and verify computationally that every sample has
   exactly one solution.

Report at least:

- field accuracy;
- table exact match;
- supported-cell blank rate;
- cross-table consistency;
- accuracy by dependency depth;
- performance versus the number of jointly coupled uncertain events.

For the final benchmark, the audit-style stratum should be a hard diagnostic
split rather than the entire dataset. Natural commentary and scorer correction
logs are needed so the contribution cannot be dismissed as a synthetic logic
puzzle.

## Reproducibility notes

- Each level has a case file, hidden gold JSON, Map&Make trace, prediction JSON
  and deterministic scorer.
- Levels 3–6 were generated with fresh system randomness.
- This is a single-model self-test, not a published baseline run. Final claims
  should use fixed prompts, fixed model versions, fixed decoding settings and
  repeated runs across multiple current models.
