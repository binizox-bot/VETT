# match_0117 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+0b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=108 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 14→66→101→106 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 3≠4→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 108−90=18 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Sienna Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 108−0(B)−1(LB)=107 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 90−0(B)−1(LB)=89 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 52 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coveguard Women
- `pom`: Sienna Vale
- `venue`: Willowmere Oval, Southbay
- `toss`: Coveguard Women Won The Toss And Elected To Bat
- `inn1_total`: 108/4
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 107
- `inn2_total`: 90/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 89
- `margin`: 18
- `margin_type`: runs