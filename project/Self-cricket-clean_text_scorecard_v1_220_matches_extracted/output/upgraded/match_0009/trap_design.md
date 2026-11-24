# match_0009 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+1b+3lb=19 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+19=184 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 9→25→32→84→96→105→129→129→146→184 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 184, achieved 187/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 11w+1nb+0b+1lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Noah Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 184−1(B)−3(LB)=180 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 187−0(B)−1(LB)=186 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 52 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coral Bay XI
- `pom`: Noah Reed
- `venue`: Eastbank Meadow Ground, Hillview
- `toss`: Coral Bay XI won the Toss and elected to Field
- `inn1_total`: 184/10
- `inn1_overs`: 46.5 Overs
- `inn1_extras`: 19
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 180
- `inn2_total`: 187/5
- `inn2_overs`: 34.2 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 11
- `inn2_bowling_charged`: 186
- `margin`: 5
- `margin_type`: wickets