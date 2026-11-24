# R3 primary scalar blind shortcut audit

## Scope and rule

This audit covers the 36 scalar queries in the three instances ending `.R3S`. A query is flagged when a plausible solver can recover the requested scalar from one sentence, adjacent paragraphs, explicit arithmetic-correction language, or a direct compact ledger without reconstructing shared nonlocal state. Target values are intentionally omitted.

## Aggregate result

| Instance | Queries | Flagged | Unflagged |
|---|---:|---:|---:|
| `match_0185.R3S` | 12 | 3 | 9 |
| `match_0106.R3S` | 12 | 8 | 4 |
| `match_0178.R3S` | 12 | 6 | 6 |
| **Total** | **36** | **17** | **19** |

## Query decisions

### `match_0185.R3S`

| Q | Identity | Flagged | Shortcut type | Rationale |
|---:|---|:---:|---|---|
| 1 | Batting · I1 · Batter=`Rohan Blake` · R | No | none | Replay collapse and ownership resolution in P02-P04 must be reconciled against the P05 wicket boundary; no local accepted component ledger is closed. |
| 2 | Batting · I1 · Batter=`Owen Marsh` · R | No | none | P06-P08 are incomplete because P25 supplies another distinct accepted event; replay, dead-ball, and ownership evidence must be combined nonlocally. |
| 3 | Batting · I2 · Batter=`Arlo Finch (wk)` · R | No | none | Finch spans two stands and several replay, wide, and no-ball decisions across P15-P24, plus the distant terminal state. |
| 4 | Batting · I2 · Batter=`Ben Cole` · R | No | none | The shot in P16 and separately authenticated running event in P24 require the P17 opening boundary as a check. |
| 5 | Bowling · I1 · Bowler=`Noah Vance` · W | No | none | Dismissals are distributed through P01-P05, with replay completeness resolved only in P14. |
| 6 | Bowling · I1 · Bowler=`Arjun Wells` · W | No | none | Accepted and rejected candidates span P08-P12 and the P14 audit; Theo's ownership requires nonlocal authority resolution. |
| 7 | Bowling · I2 · Bowler=`Owen Marsh` · W | Yes | direct compact ledger | P22 states the retained dismissal, excluded apparent dismissal, and absence of later dismissals in one reconciliation paragraph. |
| 8 | Innings Summary · I1 · Field=`Wides` · Value | No | none | The class must be accumulated across spells and replay decisions in P05, P07, P11-P13, and P26. |
| 9 | Innings Summary · I1 · Field=`Leg Byes` · Value | Yes | single-event component | P06 directly classifies the only described candidate, and P13 reconfirms it while separating the other extras classes. |
| 10 | Innings Summary · I2 · Field=`No Balls` · Value | Yes | direct compact ledger | P22 enumerates the retained chase oversteps and rejects the competing apparent overstep in the same paragraph. |
| 11 | Partnerships · I1 · Partnership=`Caleb Frost & Owen Marsh` · Runs | No | none | Distant boundaries in P05 and P14 enclose reclassification, replay, wide, and dead-ball decisions in P06-P08. |
| 12 | Partnerships · I2 · Partnership=`Noah Vance & Arlo Finch` · Runs | No | none | The P17 start closes only through terminal-state and legal-ball evidence in P21-P28, with ownership decisions spread across P18-P24. |

### `match_0106.R3S`

| Q | Identity | Flagged | Shortcut type | Rationale |
|---:|---|:---:|---|---|
| 1 | Batting · I1 · Batter=`Elena Cross (wk)` · R | Yes | explicit arithmetic correction | P22 places the partnership envelope and the two other accepted shares in one sentence and explicitly constrains Elena by those operands. |
| 2 | Batting · I1 · Batter=`Nora Finch (c)` · R | No | none | Nora's components span P15-P25 and the long-stand component changes only after replay-identity resolution. |
| 3 | Batting · I2 · Batter=`Emilia Shaw (c)` · R | No | none | Accepted components span P33-P50 and include a boundary-wide reassignment in P35-P38. |
| 4 | Bowling · I1 · Bowler=`Aila Rowan` · W | Yes | direct compact ledger | P30 names every dismissal owned by Aila inside a closed wicket reconciliation. |
| 5 | Bowling · I1 · Bowler=`Celeste Reed` · W | Yes | direct compact ledger | P30 directly enumerates Celeste's accepted dismissal owners. |
| 6 | Bowling · I2 · Bowler=`Jade Sinclair` · W | Yes | single sentence | P52 states Jade's reconciled bowling allocation directly in one sentence. |
| 7 | Innings Summary · I1 · Field=`Leg Byes` · Value | Yes | direct compact ledger | P29 places the certified entries and the additional delayed card together, closing the category locally. |
| 8 | Innings Summary · I1 · Field=`No Balls` · Value | Yes | explicit arithmetic correction | P24 keeps the independently signed cards, retains one row of the matched pair, and strikes its twin in one paragraph. |
| 9 | Innings Summary · I2 · Field=`Wides` · Value | Yes | adjacent-paragraph ledger | P45 lists the accepted non-Sienna signatures; P46 adds the live boundary event and rejects the old clip. |
| 10 | Partnerships · I1 · Partnership=`Rowan Hayes & Nora Finch` · Runs | No | none | Batter and non-batter components plus the duplicate-frame decision are separated across P11-P25. |
| 11 | Partnerships · I2 · Partnership=`Sienna Park & Emilia Shaw` · Runs | No | none | P35's components are corrected in P38 but remain unsigned until the distant identity audit in P46. |
| 12 | Partnerships · I2 · Partnership=`Ruth Elms & Emilia Shaw` · Runs | Yes | adjacent-paragraph ledger | P43 lists both batter components and the sole extra; P44 identifies the later image as a same-fingerprint replay. |

### `match_0178.R3S`

| Q | Identity | Flagged | Shortcut type | Rationale |
|---:|---|:---:|---|---|
| 1 | Batting · I1 · Batter=`Finn Archer` · R | No | none | Finn spans several windows and two corrections across P02-P15, with completeness checked remotely in P31. |
| 2 | Batting · I1 · Batter=`Dylan Vale` · R | No | none | Four partnership components and two different corrections are distributed across P05-P11 and P30. |
| 3 | Batting · I2 · Batter=`Arin Wells (wk)` · R | Yes | explicit arithmetic correction | P29 places all three windows together and explicitly rejects the duplicate packet from the middle window. |
| 4 | Batting · I2 · Batter=`Tyler Quinn` · R | No | none | The provisional component, pad reclassification, later contribution, and conservation role span P20-P32. |
| 5 | Bowling · I1 · Bowler=`Zane Cooper` · W | Yes | direct compact ledger | P16 names the complete distinct dismissal set and marks replay views as duplicates. |
| 6 | Bowling · I1 · Bowler=`Miles Benton` · W | Yes | direct compact ledger | P12 names every distinct Benton dismissal and excludes nearby identity distractors; P16 repeats the closed allocation. |
| 7 | Bowling · I2 · Bowler=`Aaron Miles` · W | Yes | direct compact ledger | P27 locally retains Leo, assigns Cameron under the bowler-credit rule, and preserves Tyler and Blake as distinct earlier signatures. |
| 8 | Innings Summary · I1 · Field=`Leg Byes` · Value | Yes | adjacent-paragraph ledger | P07 and P08 resolve the two described pad-contact units into the same class in adjacent paragraphs. |
| 9 | Innings Summary · I1 · Field=`Wides` · Value | Yes | direct compact ledger | P13 gives every accepted bowler component and handles the refresh duplicate in one paragraph. |
| 10 | Innings Summary · I2 · Field=`Wides` · Value | No | none | Components are split across P18 and P25; rejection and completeness appear only later in P28 and P32. |
| 11 | Partnerships · I1 · Partnership=`Finn Archer & Miles Carter` · Runs | No | none | P04's provisional card is altered by P15's distant camera decision and checked against remote wicket states in P33. |
| 12 | Partnerships · I2 · Partnership=`Evan Carter & Arin Wells` · Runs | No | none | Components and extras begin in P17, the boundary is P19, the duplicate resolves in P21, and Arin's corrected window appears in P29. |
