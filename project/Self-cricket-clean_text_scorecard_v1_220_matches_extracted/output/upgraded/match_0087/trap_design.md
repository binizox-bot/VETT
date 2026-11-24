# match_0087 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 24w+0nb+2b+3lb=29 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+29=196 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→13→16→43→67→68→152→157→181→196 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 196, achieved 198/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+0nb+4b+4lb=19 | [OK] |
| 7 | D3 | POM cross-innings | Jordan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 196−2(B)−3(LB)=191 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 198−4(B)−4(LB)=190 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 84 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastmoor
- `pom`: Jordan Vale
- `venue`: Central Academy Ground No 2, Ashford
- `toss`: Eastmoor Won The Toss And Elected To Field
- `inn1_total`: 196/10
- `inn1_overs`: 43.1 Overs
- `inn1_extras`: 29
- `inn1_byes`: 2
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 0
- `inn1_wides`: 24
- `inn1_bowling_charged`: 191
- `inn2_total`: 198/6
- `inn2_overs`: 43.0 Overs
- `inn2_extras`: 19
- `inn2_byes`: 4
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 0
- `inn2_wides`: 11
- `inn2_bowling_charged`: 190
- `margin`: 4
- `margin_type`: wickets