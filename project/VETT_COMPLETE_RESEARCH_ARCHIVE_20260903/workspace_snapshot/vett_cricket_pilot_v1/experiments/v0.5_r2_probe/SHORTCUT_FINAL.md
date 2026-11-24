# R2 Named-Shortcut Sufficiency Audit

This audit tests only the seven named shortcuts. It does not report any requested cricket value.

## Counts

| Instance | Queries | Flagged | Unflagged |
|---|---:|---:|---:|
| match_0185.R2FS | 12 | 1 | 11 |
| match_0106.R2FS | 12 | 0 | 12 |
| match_0178.R2FS | 12 | 1 | 11 |
| **Overall** | **36** | **2** | **34** |

| Shortcut | Sufficient-query count |
|---|---:|
| last-number | 0 |
| one-sentence answer | 0 |
| direct summary | 0 |
| explicit equation | 0 |
| colocated local sum/subtraction | 0 |
| single decrement | 1 |
| compact victim ledger | 1 |

## Per-query findings

### match_0185.R2FS

| Query | Requested row | Sufficient shortcut(s) | Evidence |
|---:|---|---|---|
| 1 | I1 Batting — Rohan Blake | None | Requires live scoring events plus two independently resolved replay mistakes across P2-P7, P16, and P25. |
| 2 | I1 Batting — Owen Marsh | None | Genuine shots, a dead-ball exclusion, and the revised dismissal boundary are separated across P9, P15, P19, and P22. |
| 3 | I2 Batting — Arlo Finch (wk) | None | Requires a corrected opening share and a later stand with a reclassification and terminal addition; the two windows are not displayed together. |
| 4 | I1 Bowling — Noah Vance | None | Distinct victims are dispersed and P16 removes a replay duplicate without summarizing the legitimate ledger. |
| 5 | I1 Bowling — Arjun Wells | None | Victims are dispersed, with a separate attribution transfer and a later return by the bowler. |
| 6 | I2 Bowling — Owen Marsh | compact victim ledger | P41 closes the local ledger by retaining the valid Ben dismissal and cancelling the Finch event, with its replays marked historical. |
| 7 | I1 Innings Summary — Total | None | Must combine the earlier ninth-wicket state with the last stand's only accepted addition; no final total or local arithmetic is supplied. |
| 8 | I1 Innings Summary — Total Extras | None | The component categories are settled separately across P25-P28; one category's decrement does not close the aggregate. |
| 9 | I2 Innings Summary — Total | None | The terminal passing run acts on a level state that itself depends on the reconstructed first-innings terminal state. |
| 10 | I1 Partnerships — Caleb Frost & Owen Marsh | None | The stand's start and its twice-corrected accepted end are in separate passages. |
| 11 | I2 Partnerships — Noah Vance & Arlo Finch | None | Both batter shares and extras are distributed across P34-P41. |
| 12 | I1 Fall of Wickets — fifth wicket | None | The queued dismissal card undergoes two independent reductions, defeating both last-number and single-decrement shortcuts. |

### match_0106.R2FS

| Query | Requested row | Sufficient shortcut(s) | Evidence |
|---:|---|---|---|
| 1 | I1 Batting — Elena Cross (wk) | None | The stand boundary, partner share, and corrected extras allocation appear in P3, P8, and P21-P22. |
| 2 | I1 Batting — Nora Finch (c) | None | Several partnership components and a separate correction must be combined. |
| 3 | I2 Batting — Emilia Shaw (c) | None | Contributions span P34-P50 and include a revision and explicit zero intervals. |
| 4 | I1 Bowling — Aila Rowan | None | Genuine dismissals are separated, and P23 later removes a provisional attribution. |
| 5 | I1 Bowling — Celeste Reed | None | Delivered dismissals are nonadjacent and a run-out bowling credit is separately removed. |
| 6 | I2 Bowling — Jade Sinclair | None | Separate early events amid replay warnings are not a compact complete victim ledger or summary. |
| 7 | I1 Innings Summary — Total Extras | None | All component categories are distributed, with late corrections to different categories. |
| 8 | I2 Innings Summary — Total Extras | None | Extras are partitioned over many stands, including separated corrections. |
| 9 | I1 Partnerships — Rowan Hayes & Nora Finch | None | Both batter shares and the extras component are separated and revised on different sheets. |
| 10 | I2 Partnerships — Sienna Park & Emilia Shaw | None | Each batter share and extras receive separate treatment and corrections across P36-P43. |
| 11 | I1 Fall of Wickets — fourth wicket | None | The ordinal is direct, but its requested score requires a distributed partnership reconstruction. |
| 12 | I2 Fall of Wickets — tenth wicket | None | Requires roll-forward from the ninth-wicket state with separated batter additions, zero extras, and replay retraction. |

### match_0178.R2FS

| Query | Requested row | Sufficient shortcut(s) | Evidence |
|---:|---|---|---|
| 1 | I1 Batting — Finn Archer | None | Combines a corrected opening component, a separately repaired middle component, and a late-confirmed zero component. |
| 2 | I1 Batting — Dylan Vale | None | Four stand components and two independent corrections are required; P9 explicitly rejects a single-decrement solution. |
| 3 | I2 Batting — Arin Wells (wk) | None | Three separated components are needed, with one revised only in P27. |
| 4 | I2 Batting — Tyler Quinn | None | Two partnership contributions must be combined after a late correction to one of them. |
| 5 | I1 Bowling — Zane Cooper | None | Two early victims and a later distinct victim are separated by replay traps. |
| 6 | I1 Bowling — Miles Benton | None | Dismissals are distributed across P5, P9, P10, and P12. |
| 7 | I2 Bowling — Aaron Miles | None | Victims are dispersed; a duplicate is removed and a missing stumping is added only in the closing sweep. |
| 8 | I1 Innings Summary — Total | None | The repaired batter subtotal and extras categories are separated; P11 says no completed innings number is supplied. |
| 9 | I2 Innings Summary — Total Extras | None | The final wide ledger and the other extras categories are scattered across the chase. |
| 10 | I1 Partnerships — Finn Archer & Miles Carter | None | The stand boundaries are far apart, and the component route also requires separated corrections. |
| 11 | I2 Partnerships — Evan Carter & Arin Wells | None | Boundaries, batter shares, and corrected extras are distributed across P16-P27. |
| 12 | I2 Fall of Wickets — third wicket | single decrement | P24 marks the provisional third-wicket score as containing the single Carter-stand feed duplicate, and P19 records that phantom entry being removed once. |

