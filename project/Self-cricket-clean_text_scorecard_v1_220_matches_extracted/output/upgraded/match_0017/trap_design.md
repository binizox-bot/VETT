# match_0017 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+1b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=174 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 9→24→58→75→83→101→109→119→130→174 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 174−106=68 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+2lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Miles Carter — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 174−1(B)−2(LB)=171 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 106−0(B)−2(LB)=104 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 44 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgevale XI
- `pom`: Miles Carter
- `venue`: North Ridge Oval, Hillview
- `toss`: Sandmere XI won the Toss and elected to Field
- `inn1_total`: 174/10
- `inn1_overs`: 43.5 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 171
- `inn2_total`: 106/10
- `inn2_overs`: 28.3 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 104
- `margin`: 68
- `margin_type`: runs