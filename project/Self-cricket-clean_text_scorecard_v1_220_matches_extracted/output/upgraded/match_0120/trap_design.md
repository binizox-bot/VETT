# match_0120 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+1b+0lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=111 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 82→87→100→108 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 3≠4→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 111−74=37 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Elina Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 111−1(B)−0(LB)=110 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 74−0(B)−1(LB)=73 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 82 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meridian Women
- `pom`: Elina Reed
- `venue`: Rosebank Oval, Eastmere
- `toss`: Meridian Women Won The Toss And Elected To Bat
- `inn1_total`: 111/4
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 1
- `inn1_leg_byes`: 0
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 110
- `inn2_total`: 74/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 73
- `margin`: 37
- `margin_type`: runs