# match_0130 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+2nb+0b+1lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=158 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 39→44→64→136→141→151→153→155→155 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠9→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 158−140=18 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Darren Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 158−0(B)−1(LB)=157 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 140−0(B)−1(LB)=139 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 72 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Marina XI
- `pom`: Darren Vale
- `venue`: Riverside Turf - 2, Eastport
- `toss`: Upland XI Won The Toss And Elected To Field
- `inn1_total`: 158/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 10
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 7
- `inn1_bowling_charged`: 157
- `inn2_total`: 140/8
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 139
- `margin`: 18
- `margin_type`: runs