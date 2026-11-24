# match_0111 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 15w+1nb+1b+1lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=122 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 14→31→43→63→105→108→115→116→116 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠9→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 122−84=38 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+0nb+1b+1lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Sienna Carter — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 122−1(B)−1(LB)=120 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 84−1(B)−1(LB)=82 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 42 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Lakeside Herons Women
- `pom`: Sienna Carter
- `venue`: Willowbank Turf Ground, Southmere
- `toss`: Dusk Valley Women Won The Toss And Elected To Field
- `inn1_total`: 122/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 15
- `inn1_bowling_charged`: 120
- `inn2_total`: 84/10
- `inn2_overs`: 19.1 Overs
- `inn2_extras`: 13
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 11
- `inn2_bowling_charged`: 82
- `margin`: 38
- `margin_type`: runs