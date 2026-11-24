# match_0019 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+1nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=282 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 73→81→85→197→232→234→242→271→279 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 282, achieved 43/6 | [WARN] |
| 6 | D2 | Extras decomposition (Inn2) | 1w+0nb+0b+0lb=1 | [OK] |
| 7 | D3 | POM cross-innings |  — verify contribution across both innings | [WARN] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 282−1(B)−2(LB)=279 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 43−0(B)−0(LB)=43 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 112 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: 
- `pom`: 
- `venue`: North Summit Cricket Ground, Hillview
- `toss`: Sandvale Lions won the Toss and elected to Field
- `inn1_total`: 282/9
- `inn1_overs`: 42.0 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 8
- `inn1_bowling_charged`: 279
- `inn2_total`: 43/6
- `inn2_overs`: 9.3 Overs
- `inn2_extras`: 1
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 1
- `inn2_bowling_charged`: 43
- `margin`: None
- `margin_type`: no_result