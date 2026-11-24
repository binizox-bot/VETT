# match_0032 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+0nb+1b+1lb=14 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+14=136 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→48→104→111→114→122→126→131 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 136, achieved 137/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 21w+0nb+0b+1lb=22 | [OK] |
| 7 | D3 | POM cross-innings | Evan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 136−1(B)−1(LB)=134 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 137−0(B)−1(LB)=136 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 56 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline
- `pom`: Evan Vale
- `venue`: Meadowbank Oval, Westhaven
- `toss`: Atoll Bay won the Toss and elected to bat
- `inn1_total`: 136/8
- `inn1_overs`: 35.0 Overs
- `inn1_extras`: 14
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 12
- `inn1_bowling_charged`: 134
- `inn2_total`: 137/6
- `inn2_overs`: 32.1 Overs
- `inn2_extras`: 22
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 21
- `inn2_bowling_charged`: 136
- `margin`: 4
- `margin_type`: wickets