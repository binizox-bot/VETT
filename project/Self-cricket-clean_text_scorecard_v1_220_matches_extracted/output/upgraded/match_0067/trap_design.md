# match_0067 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+0b+3lb=15 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+15=68 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 12→20→24→28→39→65→70→75→76→68 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 68, achieved 70/0 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+1lb=4 | [OK] |
| 7 | D3 | POM cross-innings | Noah Carter — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 68−0(B)−3(LB)=65 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 70−0(B)−1(LB)=69 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 26 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Kingsbridge
- `pom`: Noah Carter
- `venue`: Riverton Park Ground, Kingsmead
- `toss`: Southford won the Toss and elected to bat
- `inn1_total`: 68/10
- `inn1_overs`: 34.4 Overs
- `inn1_extras`: 15
- `inn1_byes`: 0
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 65
- `inn2_total`: 70/0
- `inn2_overs`: 8.2 Overs
- `inn2_extras`: 4
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 69
- `margin`: 10
- `margin_type`: wickets