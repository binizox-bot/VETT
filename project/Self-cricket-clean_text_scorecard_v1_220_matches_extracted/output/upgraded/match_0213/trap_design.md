# match_0213 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 21w+2nb+1b+3lb=27 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+27=272 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 20→51→105→212→236→252→264→271 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 272−114=158 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+2b+1lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Elias Grant — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 272−1(B)−3(LB)=268 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 114−2(B)−1(LB)=111 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 107 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborfield CC
- `pom`: Elias Grant
- `venue`: Cedarbrook Oval, Northmere
- `toss`: Harborfield CC won the Toss and elected to Bat
- `inn1_total`: 272/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 27
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 2
- `inn1_wides`: 21
- `inn1_bowling_charged`: 268
- `inn2_total`: 114/10
- `inn2_overs`: 34.2 Overs
- `inn2_extras`: 11
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 111
- `margin`: 158
- `margin_type`: runs