# match_0164 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+0b+1lb=7 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+7=108 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 2→28→32→71→95→105 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠6→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 108, achieved 109/4 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+0nb+0b+4lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Isla Rowan (Meadowridge Women) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 108−0(B)−1(LB)=107 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 109−0(B)−4(LB)=105 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 39 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meadowridge Women
- `pom`: Isla Rowan (Meadowridge Women)
- `venue`: Northbay Cricket Oval, Eastport
- `toss`: Silverbank Women Won The Toss And Elected To Bat
- `inn1_total`: 108/6
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 7
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 107
- `inn2_total`: 109/4
- `inn2_overs`: 19.0 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 0
- `inn2_wides`: 9
- `inn2_bowling_charged`: 105
- `margin`: 6
- `margin_type`: wickets