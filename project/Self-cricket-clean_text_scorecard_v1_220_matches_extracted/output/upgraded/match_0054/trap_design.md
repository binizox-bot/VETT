# match_0054 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 13w+1nb+3b+2lb=19 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+19=176 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 23→115→149→153→160→164→167→167→172→176 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 176−168=8 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 18w+2nb+3b+8lb=31 | [OK] |
| 7 | D3 | POM cross-innings | Cameron Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 176−3(B)−2(LB)=171 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 168−3(B)−8(LB)=157 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 92 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northmere
- `pom`: Cameron Vale
- `venue`: Greenfield Oval, Fairmont
- `toss`: Southbay won the Toss and elected to Field
- `inn1_total`: 176/10
- `inn1_overs`: 44.2 Overs
- `inn1_extras`: 19
- `inn1_byes`: 3
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 13
- `inn1_bowling_charged`: 171
- `inn2_total`: 168/10
- `inn2_overs`: 34.3 Overs
- `inn2_extras`: 31
- `inn2_byes`: 3
- `inn2_leg_byes`: 8
- `inn2_no_balls`: 2
- `inn2_wides`: 18
- `inn2_bowling_charged`: 157
- `margin`: 8
- `margin_type`: runs