# match_0116 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+0nb+1b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=96 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→11→14→22→40→80→82→96 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 96, achieved 97/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+1b+2lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Sera Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 96−1(B)−1(LB)=94 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 97−1(B)−2(LB)=94 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 40 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meadowvale Women
- `pom`: Sera Hart
- `venue`: Stonefield Club Ground, Rivermere
- `toss`: Meadowvale Women Won The Toss And Elected To Field
- `inn1_total`: 96/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 10
- `inn1_bowling_charged`: 94
- `inn2_total`: 97/7
- `inn2_overs`: 19.2 Overs
- `inn2_extras`: 13
- `inn2_byes`: 1
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 94
- `margin`: 3
- `margin_type`: wickets