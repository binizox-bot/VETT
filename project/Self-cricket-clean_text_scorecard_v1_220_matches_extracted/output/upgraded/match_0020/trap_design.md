# match_0020 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+1nb+3b+4lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=136 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 33→34→69→78→100→100→102→103→114→136 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 136, achieved 45/0 | [WARN] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+0lb=3 | [OK] |
| 7 | D3 | POM cross-innings |  — verify contribution across both innings | [WARN] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 136−3(B)−4(LB)=129 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 45−0(B)−0(LB)=45 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 35 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: 
- `pom`: 
- `venue`: Ridgeview Cricket Ground, Hillview
- `toss`: Gulf XI won the Toss and elected to Field
- `inn1_total`: 136/10
- `inn1_overs`: 32.1 Overs
- `inn1_extras`: 18
- `inn1_byes`: 3
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 1
- `inn1_wides`: 10
- `inn1_bowling_charged`: 129
- `inn2_total`: 45/0
- `inn2_overs`: 6.4 Overs
- `inn2_extras`: 3
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 45
- `margin`: None
- `margin_type`: no_result