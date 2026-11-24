# match_0178 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 17w+1nb+2b+1lb=21 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+21=282 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 62→62→138→144→169→184→252→258→265→282 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 282−74=208 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+1nb+0b+3lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Miles (Shoreline Rangers) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 282−2(B)−1(LB)=279 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 74−0(B)−3(LB)=71 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 76 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Shoreline Rangers
- `pom`: Aaron Miles (Shoreline Rangers)
- `venue`: South Meridian Institute Ground, Westhaven
- `toss`: Shoreline Rangers Won The Toss And Elected To Bat
- `inn1_total`: 282/10
- `inn1_overs`: 47.2 Overs
- `inn1_extras`: 21
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 17
- `inn1_bowling_charged`: 279
- `inn2_total`: 74/10
- `inn2_overs`: 24.4 Overs
- `inn2_extras`: 16
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 1
- `inn2_wides`: 12
- `inn2_bowling_charged`: 71
- `margin`: 208
- `margin_type`: runs