# match_0217 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+1nb+1b+2lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=197 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 12→30→58→108→146→154→171→189→194→197 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 197−119=78 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+0nb+1b+2lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Oliver Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 197−1(B)−2(LB)=194 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 119−1(B)−2(LB)=116 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 50 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Rivermere CC
- `pom`: Oliver Reed
- `venue`: Alderbrook Ground, Westmere
- `toss`: Ashford CC won the Toss and elected to Field
- `inn1_total`: 197/10
- `inn1_overs`: 48.5 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 13
- `inn1_bowling_charged`: 194
- `inn2_total`: 119/10
- `inn2_overs`: 34.1 Overs
- `inn2_extras`: 15
- `inn2_byes`: 1
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 12
- `inn2_bowling_charged`: 116
- `margin`: 78
- `margin_type`: runs