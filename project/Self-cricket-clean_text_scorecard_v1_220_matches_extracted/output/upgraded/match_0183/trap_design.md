# match_0183 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 22w+3nb+1b+2lb=28 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+28=306 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 37→191→213→227→255→287→302 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 306−101=205 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 23w+2nb+3b+4lb=32 | [OK] |
| 7 | D3 | POM cross-innings | Oliver Kent (Seabrook) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 306−1(B)−2(LB)=303 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 101−3(B)−4(LB)=94 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 154 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Seabrook
- `pom`: Oliver Kent (Seabrook)
- `venue`: Meadowbank School Oval, Westhaven
- `toss`: Northvale Won The Toss And Elected To Field
- `inn1_total`: 306/7
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 28
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 3
- `inn1_wides`: 22
- `inn1_bowling_charged`: 303
- `inn2_total`: 101/10
- `inn2_overs`: 38.2 Overs
- `inn2_extras`: 32
- `inn2_byes`: 3
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 2
- `inn2_wides`: 23
- `inn2_bowling_charged`: 94
- `margin`: 205
- `margin_type`: runs