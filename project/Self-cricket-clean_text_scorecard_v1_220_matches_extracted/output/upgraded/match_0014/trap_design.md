# match_0014 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+1nb+1b+3lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=225 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→39→108→121→161→207→212→225 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 225, achieved 226/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+1nb+1b+2lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Aiden Mercer — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 225−1(B)−3(LB)=221 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 226−1(B)−2(LB)=223 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 69 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harbor Peninsula XI
- `pom`: Aiden Mercer
- `venue`: East Ridge Cricket Ground, Hillview
- `toss`: Canyon Stars XI won the Toss and elected to bat
- `inn1_total`: 225/8
- `inn1_overs`: 36.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 12
- `inn1_bowling_charged`: 221
- `inn2_total`: 226/7
- `inn2_overs`: 35.2 Overs
- `inn2_extras`: 15
- `inn2_byes`: 1
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 11
- `inn2_bowling_charged`: 223
- `margin`: 3
- `margin_type`: wickets