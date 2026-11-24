# match_0167 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+1b+1lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=124 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 25→27→70→84→88→108→120 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 124−87=37 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+1b+0lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Mara Vale (Bayport Women) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 124−1(B)−1(LB)=122 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 87−1(B)−0(LB)=86 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 43 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayport Women
- `pom`: Mara Vale (Bayport Women)
- `venue`: Cedarbank Cricket Oval, Westmoor
- `toss`: Eastvale Women Won The Toss And Elected To Field
- `inn1_total`: 124/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 122
- `inn2_total`: 87/10
- `inn2_overs`: 19.2 Overs
- `inn2_extras`: 8
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 86
- `margin`: 37
- `margin_type`: runs