# match_0206 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+2nb+3b+4lb=21 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+21=222 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 16→22→31→38→156→185→196→202→204→222 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 222−150=72 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+1nb+0b+2lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Nolan Vale (Coastline) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 222−3(B)−4(LB)=215 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 150−0(B)−2(LB)=148 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 118 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coastline
- `pom`: Nolan Vale (Coastline)
- `venue`: Brookfield Ground 2, Westhaven
- `toss`: Mesa Won The Toss And Elected To Field
- `inn1_total`: 222/10
- `inn1_overs`: 48.4 Overs
- `inn1_extras`: 21
- `inn1_byes`: 3
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 2
- `inn1_wides`: 12
- `inn1_bowling_charged`: 215
- `inn2_total`: 150/10
- `inn2_overs`: 47.5 Overs
- `inn2_extras`: 14
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 11
- `inn2_bowling_charged`: 148
- `margin`: 72
- `margin_type`: runs