# match_0072 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+2nb+2b+3lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=290 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 21→23→148→201→259→269→276→289 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 290−188=23 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+1b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Cross — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 290−2(B)−3(LB)=285 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 188−1(B)−1(LB)=186 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 125 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbank
- `pom`: Ethan Cross
- `venue`: Riverbend Park, Eastmoor
- `toss`: Northbank won the Toss and elected to bat
- `inn1_total`: 290/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 2
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 2
- `inn1_wides`: 11
- `inn1_bowling_charged`: 285
- `inn2_total`: 188/10
- `inn2_overs`: 28.4 Overs
- `inn2_extras`: 6
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 186
- `margin`: 23
- `margin_type`: runs