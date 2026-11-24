# match_0029 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+0nb+1b+4lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=220 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→84→152→161→174→206→209→215 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 220−126=94 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+3nb+2b+5lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Tyler Stone — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 220−1(B)−4(LB)=215 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 126−2(B)−5(LB)=119 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 68 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayfront
- `pom`: Tyler Stone
- `venue`: Meadowbank Oval, Westhaven
- `toss`: Bayfront won the Toss and elected to bat
- `inn1_total`: 220/8
- `inn1_overs`: 35.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 0
- `inn1_wides`: 12
- `inn1_bowling_charged`: 215
- `inn2_total`: 126/10
- `inn2_overs`: 34.5 Overs
- `inn2_extras`: 19
- `inn2_byes`: 2
- `inn2_leg_byes`: 5
- `inn2_no_balls`: 3
- `inn2_wides`: 9
- `inn2_bowling_charged`: 119
- `margin`: 94
- `margin_type`: runs