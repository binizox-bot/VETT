# match_0018 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+1b+5lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=288 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 8→23→81→85→140→236→267→280 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 288−252=36 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+1nb+3b+2lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Mason Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 288−1(B)−5(LB)=282 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 252−3(B)−2(LB)=247 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 96 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Dunecrest XI
- `pom`: Mason Vale
- `venue`: North Ridge Stadium, Hillview
- `toss`: Harborline XI won the Toss and elected to Field
- `inn1_total`: 288/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 5
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 282
- `inn2_total`: 252/10
- `inn2_overs`: 49.2 Overs
- `inn2_extras`: 19
- `inn2_byes`: 3
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 13
- `inn2_bowling_charged`: 247
- `margin`: 36
- `margin_type`: runs