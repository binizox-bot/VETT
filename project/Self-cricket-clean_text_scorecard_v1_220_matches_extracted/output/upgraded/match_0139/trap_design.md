# match_0139 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+1nb+1b+2lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=196 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 82→124→175→182→192 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠5→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 196−147=49 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+2lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Rohan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 196−1(B)−2(LB)=193 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 147−0(B)−2(LB)=145 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 82 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborview XI
- `pom`: Rohan Vale
- `venue`: Oakridge Oval, Fairhaven
- `toss`: Stonegate XI Won The Toss And Elected To Field
- `inn1_total`: 196/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 4
- `inn1_bowling_charged`: 193
- `inn2_total`: 147/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 145
- `margin`: 49
- `margin_type`: runs