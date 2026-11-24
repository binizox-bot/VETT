# match_0047 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+4b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=337 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 116→134→182→192→203→303→315→324 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 337−222=115 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+3b+5lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Marcus Ward — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 337−4(B)−2(LB)=331 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 222−3(B)−5(LB)=214 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 116 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgefield
- `pom`: Marcus Ward
- `venue`: Lakeside Cricket Ground, Eastport
- `toss`: Southport won the Toss and elected to Field
- `inn1_total`: 337/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 4
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 331
- `inn2_total`: 222/10
- `inn2_overs`: 41.2 Overs
- `inn2_extras`: 15
- `inn2_byes`: 3
- `inn2_leg_byes`: 5
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 214
- `margin`: 115
- `margin_type`: runs