# match_0214 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+1b+1lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=74 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 8→15→15→19→41→44→64→69→72→74 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 74, achieved 76/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Mason Hale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 74−1(B)−1(LB)=72 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 76−0(B)−1(LB)=75 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 22 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Valleygate CC
- `pom`: Mason Hale
- `venue`: Brookmere Cricket Ground, North Valley
- `toss`: Ridgefield CC won the Toss and elected to Bat
- `inn1_total`: 74/10
- `inn1_overs`: 24.5 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 72
- `inn2_total`: 76/3
- `inn2_overs`: 10.2 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 75
- `margin`: 7
- `margin_type`: wickets