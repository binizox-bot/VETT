# match_0075 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 20w+1nb+1b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=246 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 78→81→111→113→195→202→214→216→224 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 246, achieved 116/6 | [WARN] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+2nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings |  — verify contribution across both innings | [WARN] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 246−1(B)−2(LB)=243 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 116−0(B)−1(LB)=115 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 82 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: 
- `pom`: 
- `venue`: Greenfield Park, Fairmoor
- `toss`: Rivergate won the Toss and elected to Field
- `inn1_total`: 246/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 20
- `inn1_bowling_charged`: 243
- `inn2_total`: 116/6
- `inn2_overs`: 22.2 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 2
- `inn2_wides`: 6
- `inn2_bowling_charged`: 115
- `margin`: None
- `margin_type`: no_result