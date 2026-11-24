# R2 blind-query shortcut re-audit

Audited only `package/r2_blind_queries_3.jsonl`. A query is flagged only when a named shortcut pattern is sufficient by itself to determine the requested cell. Target values are intentionally omitted.

## Overall result

| Instance | Flagged | Total | Rate |
|---|---:|---:|---:|
| `match_0185.R2FS` | 1 | 12 | 8.33% |
| `match_0106.R2FS` | 2 | 12 | 16.67% |
| `match_0178.R2FS` | 7 | 12 | 58.33% |
| **Overall** | **10** | **36** | **27.78%** |

Category counts are non-exclusive: local sum/subtraction 6; compact accepted-victim ledger 3; one-sentence answer 1; direct summary 1; single correction/decrement 1; last-number heuristic 0; explicit equation 0.

## `match_0185.R2FS`

| Q | Requested cell | Flag | Shortcut type(s) | Evidence |
|---:|---|:---:|---|---|
| 1 | I1 Batting — Rohan Blake — R | No | — | P2 and P5 describe live scoring; P16 and P25 separately remove replay-related entries. No final personal line, local remainder, or single sufficient correction is supplied. |
| 2 | I1 Batting — Owen Marsh — R | No | — | Genuine scoring events are split between P9 and P15, and the dead-ball entry is resolved only in P19. Event reconciliation across separated passages is required. |
| 3 | I2 Batting — Arlo Finch (wk) — R | No | — | The opening-share correction is delayed to P39; the second-stand reclassification and terminal run occur in P36 and P40. The innings row must be joined across partnership windows. |
| 4 | I1 Bowling — Noah Vance — W | No | — | Valid dismissals are dispersed across P1, P3, P6, and P8, with a replay overcount removed in P16. There is no compact accepted-victim recap. |
| 5 | I1 Bowling — Arjun Wells — W | No | — | Accepted wickets appear across P12, P13, P17, P18, and P21; P18 and P26 repair a misattribution. No compact ledger or cumulative figure is present. |
| 6 | I2 Bowling — Owen Marsh — W | **Yes** | one-sentence answer; direct summary; compact accepted-victim ledger | P41 puts the accepted Ben catch and cancelled Finch catch in one sentence, directly closing the bowling row. |
| 7 | I1 Innings Summary — Total — Value | No | — | No accepted final total is printed. The terminal state requires the corrected middle-innings sequence, later ninth-wicket state, and last-stand addition. |
| 8 | I1 Innings Summary — Total Extras — Value | No | — | Wides, leg-bye, no-ball, and bye decisions are separated across P25–P28. No local aggregate or explicit equation appears. |
| 9 | I2 Innings Summary — Total — Value | No | — | The chase total is expressed through target relation, level state, replay rejection, and the terminal legal run in P29 and P37–P40. |
| 10 | I1 Partnerships — Caleb Frost & Owen Marsh — Runs | No | — | The lower boundary is in P8; the upper boundary passes through the queued card and separate corrections in P11, P19, and P22. |
| 11 | I2 Partnerships — Noah Vance & Arlo Finch — Runs | No | — | Batter shares and stand extras must be reconstructed from P34, P36, and P38–P41 after separating the opening stand. |
| 12 | I1 Fall of Wickets — Wkt 5 — At | No | — | P42 fixes wicket identity but withholds its figure; the accepted state comes from P11 plus two separately resolved removals in P19 and P22. |

## `match_0106.R2FS`

| Q | Requested cell | Flag | Shortcut type(s) | Evidence |
|---:|---|:---:|---|---|
| 1 | I1 Batting — Elena Cross (wk) — R | No | — | The stand total, Mira's share, and corrected opening extras are split across P3, P8, and P21–P22. |
| 2 | I1 Batting — Nora Finch (c) — R | No | — | Nora's contributions span P13, P16, P19, P20, and P24, with the major component corrected only in P25. |
| 3 | I2 Batting — Emilia Shaw (c) — R | No | — | Contributions are partitioned across many stands from P34 through P50, including a delayed correction and explicit zero intervals. |
| 4 | I1 Bowling — Aila Rowan — W | No | — | Accepted dismissals are separated in P3 and P6; the later Mira attribution is removed from Aila only in P23. |
| 5 | I1 Bowling — Celeste Reed — W | No | — | Delivered wickets are spread across P14, P19, and P24, and the run-out credit is separately removed in P28. |
| 6 | I2 Bowling — Jade Sinclair — W | **Yes** | compact accepted-victim ledger | P32–P34 place every accepted Jade dismissal in a tight consecutive opening sequence; replays do not interrupt the easy count. |
| 7 | I1 Innings Summary — Total Extras — Value | No | — | Bye, wide, leg-bye, and no-ball components are resolved in P5, P18, P21, and P29. |
| 8 | I2 Innings Summary — Total Extras — Value | No | — | Extras are distributed across ten partnership intervals from P32 through P49, with a delayed fifth-interval correction. |
| 9 | I1 Partnerships — Rowan Hayes & Nora Finch — Runs | No | — | Rowan's share, Nora's revised share, and corrected extras are scattered across P11, P25, and P27. |
| 10 | I2 Partnerships — Sienna Park & Emilia Shaw — Runs | No | — | Sienna's share is in P36, Emilia's revised component in P40, and extras are finalized only in P43. |
| 11 | I1 Fall of Wickets — Wkt 4 — At | No | — | The prior wicket state is in P9, the next wicket identity in P23, and the intervening stand requires scattered corrected components. |
| 12 | I2 Fall of Wickets — Wkt 10 — At | **Yes** | local sum/subtraction | P45–P50 colocate the accepted ninth-wicket boundary, both final-stand batter contributions, and zero extras; P52 merely confirms ordinal identity. |

## `match_0178.R2FS`

| Q | Requested cell | Flag | Shortcut type(s) | Evidence |
|---:|---|:---:|---|---|
| 1 | I1 Batting — Finn Archer — R | **Yes** | local sum/subtraction | P1–P6 contain all stand components, an explicit zero component, and one-unit repairs to the two provisional components. |
| 2 | I1 Batting — Dylan Vale — R | **Yes** | single correction/decrement | P9 exposes a cached personal card whose only remaining defect is the Connor-stand leg-bye already moved out in P7. One decrement is sufficient. |
| 3 | I2 Batting — Arin Wells (wk) — R | **Yes** | local sum/subtraction | P16–P19 colocate the first-stand run, provisional Carter-stand share and correction, and full Tyler-stand share. |
| 4 | I2 Batting — Tyler Quinn — R | **Yes** | local sum/subtraction | P18 and P21 provide the provisional Arin-stand component, its one-unit reclassification, and the later fixed component. |
| 5 | I1 Bowling — Zane Cooper — W | No | — | Live dismissals and replay traps are distributed across P2, P3, P7, P8, and P16. |
| 6 | I1 Bowling — Miles Benton — W | No | — | Accepted wickets occur across P5, P9, P10, and P12 amid surname and replay traps; no closing summary is supplied. |
| 7 | I2 Bowling — Aaron Miles — W | **Yes** | compact accepted-victim ledger | P21–P28 contain the entire Aaron victim sequence in one contiguous chase segment and finish with the add-one/delete-one replay repair. |
| 8 | I1 Innings Summary — Total — Value | No | — | The repaired batting subtotal is in P11, while extras classes are resolved elsewhere in P2, P6–P7, and P12–P15. |
| 9 | I2 Innings Summary — Total Extras — Value | No | — | Wides, no-ball, leg-byes, and byes are resolved across P17, P21–P23, and P28. |
| 10 | I1 Partnerships — Finn Archer & Miles Carter — Runs | **Yes** | local sum/subtraction | P3–P4 colocate both provisional batter shares, extras, and the one-unit boundary repair to each batter panel. |
| 11 | I2 Partnerships — Evan Carter & Arin Wells — Runs | **Yes** | local sum/subtraction | P17–P19 colocate both batter shares, extras, and the paired one-unit feed corrections. |
| 12 | I2 Fall of Wickets — Wkt 3 — At | No | — | P29 requires joining the prior score, completed stand, withdrawn feed unit, wicket order, and separately supplied legal-ball position. |

No target values are reproduced in this report.
