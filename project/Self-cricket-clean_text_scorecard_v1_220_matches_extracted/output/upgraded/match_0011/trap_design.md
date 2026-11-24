# match_0011 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+0nb+1b+2lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=282 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→23→85→109→186→218→265→273 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 282−132=47 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+3lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Owen Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 282−1(B)−2(LB)=279 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 132−0(B)−3(LB)=129 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 77 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborstone XI
- `pom`: Owen Vale
- `venue`: Northbank Meadow Ground, Hillview
- `toss`: Emirates Bay XI won the Toss and elected to Field
- `inn1_total`: 282/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 13
- `inn1_bowling_charged`: 279
- `inn2_total`: 132/6
- `inn2_overs`: 30.0 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 129
- `margin`: 47
- `margin_type`: runs