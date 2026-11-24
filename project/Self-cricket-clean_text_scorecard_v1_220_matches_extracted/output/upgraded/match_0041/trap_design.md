# match_0041 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+1nb+0b+2lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=181 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 1→27→40→48→51→109→160→169→173→181 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 181, achieved 184/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Liam Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 181−0(B)−2(LB)=179 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 184−0(B)−1(LB)=183 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 58 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Southport A
- `pom`: Liam Reed
- `venue`: Lakeside Cricket Ground, Eastport
- `toss`: Moorland A won the Toss and elected to bat
- `inn1_total`: 181/10
- `inn1_overs`: 42.5 Overs
- `inn1_extras`: 16
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 13
- `inn1_bowling_charged`: 179
- `inn2_total`: 184/3
- `inn2_overs`: 30.2 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 183
- `margin`: 7
- `margin_type`: wickets