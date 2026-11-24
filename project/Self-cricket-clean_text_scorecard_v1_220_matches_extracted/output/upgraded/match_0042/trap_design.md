# match_0042 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+1nb+1b+4lb=19 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+19=298 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 29→37→43→152→228→246→273→296 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 298−272=26 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 16w+0nb+0b+3lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Declan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 298−1(B)−4(LB)=293 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 272−0(B)−3(LB)=269 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 109 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westmere
- `pom`: Declan Vale
- `venue`: Greenfield Cricket Ground, Eastport
- `toss`: Westmere won the Toss and elected to bat
- `inn1_total`: 298/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 19
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 1
- `inn1_wides`: 13
- `inn1_bowling_charged`: 293
- `inn2_total`: 272/8
- `inn2_overs`: 50.0 Overs
- `inn2_extras`: 19
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 16
- `inn2_bowling_charged`: 269
- `margin`: 26
- `margin_type`: runs