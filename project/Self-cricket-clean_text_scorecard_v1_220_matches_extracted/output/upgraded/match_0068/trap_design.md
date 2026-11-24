# match_0068 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 19w+2nb+1b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=331 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 76→254→254→269→303→316→328 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 331−45=286 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+1lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Caleb Sutton — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 331−1(B)−2(LB)=328 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 45−0(B)−1(LB)=44 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 178 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbridge
- `pom`: Caleb Sutton
- `venue`: Stonehaven Harbour Oval, Riverton
- `toss`: Westhaven won the Toss and elected to Field
- `inn1_total`: 331/7
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 19
- `inn1_bowling_charged`: 328
- `inn2_total`: 45/10
- `inn2_overs`: 20.2 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 44
- `margin`: 286
- `margin_type`: runs