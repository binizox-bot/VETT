# match_0215 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=151 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 7→25→49→52→65→82→123→141→143→151 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 151, achieved 152/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 14w+1nb+0b+1lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Mason Hale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 151−1(B)−2(LB)=148 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 152−0(B)−1(LB)=151 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 41 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborfield CC
- `pom`: Mason Hale
- `venue`: Kingsbridge Oval, Westhaven
- `toss`: Harborfield CC won the Toss and elected to Field
- `inn1_total`: 151/10
- `inn1_overs`: 42.3 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 148
- `inn2_total`: 152/7
- `inn2_overs`: 35.2 Overs
- `inn2_extras`: 16
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 14
- `inn2_bowling_charged`: 151
- `margin`: 3
- `margin_type`: wickets