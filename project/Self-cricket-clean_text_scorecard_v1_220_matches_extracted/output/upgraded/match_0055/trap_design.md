# match_0055 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+0nb+1b+2lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=81 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→17→21→23→29→44→69→78→81→81 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 81, achieved 82/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 14w+1nb+0b+1lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Gavin Stone — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 81−1(B)−2(LB)=78 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 82−0(B)−1(LB)=81 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 25 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastford
- `pom`: Gavin Stone
- `venue`: Greenfield Academy Ground, Midlands
- `toss`: Southmere won the Toss and elected to bat
- `inn1_total`: 81/10
- `inn1_overs`: 30.5 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 14
- `inn1_bowling_charged`: 78
- `inn2_total`: 82/3
- `inn2_overs`: 14.3 Overs
- `inn2_extras`: 16
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 14
- `inn2_bowling_charged`: 81
- `margin`: 7
- `margin_type`: wickets