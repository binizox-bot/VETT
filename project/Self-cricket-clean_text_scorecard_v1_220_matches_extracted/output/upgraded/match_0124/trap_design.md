# match_0124 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+0b+1lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=216 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→70→125→134→146→162 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠6→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 216−185=31 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+0nb+0b+1lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Rohan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 216−0(B)−1(LB)=215 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 185−0(B)−1(LB)=184 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 55 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Stonecrest
- `pom`: Rohan Vale
- `venue`: Red Mesa Ground, Eastmere
- `toss`: Stonecrest Won The Toss And Elected To Bat
- `inn1_total`: 216/6
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 11
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 215
- `inn2_total`: 185/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 12
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 11
- `inn2_bowling_charged`: 184
- `margin`: 31
- `margin_type`: runs