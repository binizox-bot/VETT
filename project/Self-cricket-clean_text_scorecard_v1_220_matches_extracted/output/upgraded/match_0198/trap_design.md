# match_0198 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+4b+1lb=15 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+15=38 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 1→4→10→14→15→15→22→27→36→38 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 38, achieved 39/2 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+1b+0lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Miles Carter (Westhaven) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 38−4(B)−1(LB)=33 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 39−1(B)−0(LB)=38 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 9 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westhaven
- `pom`: Miles Carter (Westhaven)
- `venue`: Elmbridge Turf Oval, Southmere
- `toss`: Rivergate Won The Toss And Elected To Bat
- `inn1_total`: 38/10
- `inn1_overs`: 21.3 Overs
- `inn1_extras`: 15
- `inn1_byes`: 4
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 33
- `inn2_total`: 39/2
- `inn2_overs`: 5.2 Overs
- `inn2_extras`: 5
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 38
- `margin`: 8
- `margin_type`: wickets