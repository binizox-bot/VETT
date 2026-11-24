# match_0036 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+4b+2lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=128 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 3→16→21→39→82→89→102→114→126→128 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 128, achieved 130/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+0b+2lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Noah Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 128−4(B)−2(LB)=122 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 130−0(B)−2(LB)=128 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 43 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastport
- `pom`: Noah Reed
- `venue`: Meadow Park Oval, Westhaven
- `toss`: Westshore won the Toss and elected to bat
- `inn1_total`: 128/10
- `inn1_overs`: 34.2 Overs
- `inn1_extras`: 16
- `inn1_byes`: 4
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 122
- `inn2_total`: 130/3
- `inn2_overs`: 25.4 Overs
- `inn2_extras`: 12
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 128
- `margin`: 7
- `margin_type`: wickets