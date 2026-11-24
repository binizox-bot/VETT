# match_0103 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+1nb+1b+1lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=154 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→28→45→67→106→139 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠6→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 154, achieved 157/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+2lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Victor Hale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 154−1(B)−1(LB)=152 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 157−0(B)−2(LB)=155 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 39 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline
- `pom`: Victor Hale
- `venue`: Riverside Cricket Ground, East Midlands
- `toss`: Harborline Won The Toss And Elected To Field
- `inn1_total`: 154/6
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 13
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 10
- `inn1_bowling_charged`: 152
- `inn2_total`: 157/5
- `inn2_overs`: 17.2 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 155
- `margin`: 5
- `margin_type`: wickets