# match_0157 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+0b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=176 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→57→117→120→125 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠5→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 176−70=106 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+0b+2lb=5 | [OK] |
| 7 | D3 | POM cross-innings | Ronan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 176−0(B)−1(LB)=175 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 70−0(B)−2(LB)=68 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 60 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline XI
- `pom`: Ronan Vale
- `venue`: Harborline Training Oval, Northport
- `toss`: Harborline XI Won The Toss And Elected To Bat
- `inn1_total`: 176/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 175
- `inn2_total`: 70/10
- `inn2_overs`: 16.2 Overs
- `inn2_extras`: 5
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 68
- `margin`: 106
- `margin_type`: runs