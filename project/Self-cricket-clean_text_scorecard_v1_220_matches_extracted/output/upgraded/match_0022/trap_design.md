# match_0022 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+0b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=94 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→38→39→58→63→67→69→93→93 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 94−86=8 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+1b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Zoe Carter — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 94−0(B)−1(LB)=93 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 86−1(B)−1(LB)=84 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 34 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Crescent A Women
- `pom`: Zoe Carter
- `venue`: Northlake Recreation Oval, Northport
- `toss`: Highland Women won the Toss and elected to Field
- `inn1_total`: 94/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 93
- `inn2_total`: 86/7
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 8
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 84
- `margin`: 8
- `margin_type`: runs