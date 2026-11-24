# match_0074 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 23w+0nb+1b+3lb=27 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+27=318 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→59→150→181→196→236→237→244→300→318 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 318−128=190 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 27w+1nb+2b+6lb=36 | [OK] |
| 7 | D3 | POM cross-innings | Riley Bennett — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 318−1(B)−3(LB)=314 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 128−2(B)−6(LB)=120 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 91 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Fairmont
- `pom`: Riley Bennett
- `venue`: Southbank Oval, Fairhaven
- `toss`: Fairmont won the Toss and elected to bat
- `inn1_total`: 318/10
- `inn1_overs`: 49.1 Overs
- `inn1_extras`: 27
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 0
- `inn1_wides`: 23
- `inn1_bowling_charged`: 314
- `inn2_total`: 128/10
- `inn2_overs`: 38.1 Overs
- `inn2_extras`: 36
- `inn2_byes`: 2
- `inn2_leg_byes`: 6
- `inn2_no_balls`: 1
- `inn2_wides`: 27
- `inn2_bowling_charged`: 120
- `margin`: 190
- `margin_type`: runs