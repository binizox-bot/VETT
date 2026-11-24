# match_0026 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 19w+3nb+1b+1lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=251 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 29→179→230→242 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠4→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 251−33=218 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+1nb+0b+0lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Nathan Wells — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 251−1(B)−1(LB)=249 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 33−0(B)−0(LB)=33 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 150 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridgeport
- `pom`: Nathan Wells
- `venue`: Meadowbank Oval, Eastbridge
- `toss`: Ridgeport won the Toss and elected to bat
- `inn1_total`: 251/4
- `inn1_overs`: 31.0 Overs
- `inn1_extras`: 24
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 3
- `inn1_wides`: 19
- `inn1_bowling_charged`: 249
- `inn2_total`: 33/10
- `inn2_overs`: 17.5 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 1
- `inn2_wides`: 12
- `inn2_bowling_charged`: 33
- `margin`: 218
- `margin_type`: runs