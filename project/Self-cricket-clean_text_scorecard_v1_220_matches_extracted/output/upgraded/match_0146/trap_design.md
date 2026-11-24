# match_0146 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 4w+0nb+0b+2lb=6 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+6=152 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 58→80→82→124→140 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 152, achieved 154/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+0nb+2b+1lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Maya Rowan — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 152−0(B)−2(LB)=150 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 154−2(B)−1(LB)=151 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 58 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Silver Coast Women
- `pom`: Maya Rowan
- `venue`: Willowbank Lakeside Ground, Eastport
- `toss`: Silver Coast Women Won The Toss And Elected To Field
- `inn1_total`: 152/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 6
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 4
- `inn1_bowling_charged`: 150
- `inn2_total`: 154/7
- `inn2_overs`: 19.3 Overs
- `inn2_extras`: 12
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 9
- `inn2_bowling_charged`: 151
- `margin`: 3
- `margin_type`: wickets