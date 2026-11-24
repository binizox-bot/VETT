# match_0006 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+2nb+1b+4lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=211 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 42→65→106→118→138→170→191→192 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 211, achieved 214/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+1nb+0b+4lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Mason Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 211−1(B)−4(LB)=206 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 214−0(B)−4(LB)=210 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 42 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgeway XI
- `pom`: Mason Vale
- `venue`: Brookfield Oval, Eastmere
- `toss`: Bayside XI won the Toss and elected to Bat
- `inn1_total`: 211/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 2
- `inn1_wides`: 11
- `inn1_bowling_charged`: 206
- `inn2_total`: 214/6
- `inn2_overs`: 45.2 Overs
- `inn2_extras`: 16
- `inn2_byes`: 0
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 1
- `inn2_wides`: 11
- `inn2_bowling_charged`: 210
- `margin`: 4
- `margin_type`: wickets