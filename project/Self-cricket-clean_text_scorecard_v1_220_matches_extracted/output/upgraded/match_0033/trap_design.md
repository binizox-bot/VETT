# match_0033 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 22w+3nb+2b+1lb=28 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+28=262 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 139→214→246→251→255 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 262−71=191 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 14w+0nb+4b+2lb=20 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 262−2(B)−1(LB)=259 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 71−4(B)−2(LB)=65 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 139 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline
- `pom`: Ethan Clarke
- `venue`: Meadowbank Oval, Westhaven
- `toss`: Harborline won the Toss and elected to bat
- `inn1_total`: 262/5
- `inn1_overs`: 35.0 Overs
- `inn1_extras`: 28
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 3
- `inn1_wides`: 22
- `inn1_bowling_charged`: 259
- `inn2_total`: 71/10
- `inn2_overs`: 25.4 Overs
- `inn2_extras`: 20
- `inn2_byes`: 4
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 14
- `inn2_bowling_charged`: 65
- `margin`: 191
- `margin_type`: runs