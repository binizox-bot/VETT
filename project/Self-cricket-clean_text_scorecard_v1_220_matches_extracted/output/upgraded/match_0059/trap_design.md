# match_0059 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 20w+1nb+1b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=255 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 9→91→109→136→146→154→197→241 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 255−218=22 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 18w+1nb+4b+3lb=26 | [OK] |
| 7 | D3 | POM cross-innings | Harvey Dean — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 255−1(B)−2(LB)=252 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 218−4(B)−3(LB)=211 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 82 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northmoor
- `pom`: Harvey Dean
- `venue`: Kingsfield Park, Riverhaven
- `toss`: Eastbrook won the Toss and elected to Field
- `inn1_total`: 255/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 20
- `inn1_bowling_charged`: 252
- `inn2_total`: 218/8
- `inn2_overs`: 43.0 Overs
- `inn2_extras`: 26
- `inn2_byes`: 4
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 1
- `inn2_wides`: 18
- `inn2_bowling_charged`: 211
- `margin`: 22
- `margin_type`: runs