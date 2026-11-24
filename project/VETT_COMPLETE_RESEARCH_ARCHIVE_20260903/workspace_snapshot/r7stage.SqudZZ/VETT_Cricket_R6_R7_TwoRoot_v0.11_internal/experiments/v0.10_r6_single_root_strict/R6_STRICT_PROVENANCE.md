# R6 Strict Single-Root Provenance

## Admission path

| Stage | Roots retained |
| --- | ---: |
| Canonical inventory | 217 |
| Source automatic pass | 104 |
| Rule-screen event candidates | 10 |
| Ledger synthesis + exact validation pass | 2 |
| Selected strict pilot | 1 |

`match_0031` is selected. `match_0032` has the same match metadata and is kept
only as a near-duplicate backup. The earlier `match_0096` experiment remains an
engineering probe and is excluded from paper gold because its upstream cells
are marked `BLOCKED_BY_CONFLICT`.

## Source and curation

- Canonical root state: `READY_FOR_GENERATED_VIEWS`.
- All 420 retained canonical cell records: `CANONICAL_CANDIDATE`.
- Four batting roster placeholders have zero balls and no dismissal, so they
  cannot be supported by delivery events.
- The R6 view removes those four rows and their 28 cell records under the
  `event_observable_batting_rows_only` policy.
- The source root is preserved unchanged; the transformation is recorded in
  `r6_curation` inside the derived root.

## Synthetic-event disclosure

The 436-event delivery order is constrained synthetic data. It is solved from
the canonical scorecard and is not represented as an observed ball-by-ball
feed. The ledger must reproduce batting, bowling, extras, partnerships,
fall-of-wickets, legal-ball state, wickets, maidens, run rate and totals.

The strict derived root passes 336/336 ledger-to-scorecard checks. The original
uncurated root passes 356/356 in the solver screen; the 20-check difference is
caused by removal of four delivery-unobservable batting rows.

## Public/private boundary

The public artifact contains narrative commentary and blank scorecard cells.
Gold tables, event dependencies, evidence spans, revision identities and the
atomic ledger are private evaluation artifacts. Mechanical checks report zero
private-key leaks, zero filled target cells, zero evidence-span errors and zero
scored cells without evidence.

## Claim boundary

Controlled ledger corruptions are sensitivity tests only. They are not model
evaluations and cannot support claims about T3, Map&Make, CoT or Direct
prompting until blinded runs are performed on the admitted three-root pilot.
