# match_0030 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 19w+1nb+1b+0lb=21 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+21=52 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 9→33→34→41→43→44→48→49→49→52 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 52, achieved 53/1 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+0nb+0b+0lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Logan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 52−1(B)−0(LB)=51 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 53−0(B)−0(LB)=53 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 24 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborfield
- `pom`: Logan Vale
- `venue`: Meadow Park Oval, Westhaven
- `toss`: Lagoon won the Toss and elected to bat
- `inn1_total`: 52/10
- `inn1_overs`: 19.2 Overs
- `inn1_extras`: 21
- `inn1_byes`: 1
- `inn1_leg_byes`: 0
- `inn1_no_balls`: 1
- `inn1_wides`: 19
- `inn1_bowling_charged`: 51
- `inn2_total`: 53/1
- `inn2_overs`: 8.1 Overs
- `inn2_extras`: 12
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 12
- `inn2_bowling_charged`: 53
- `margin`: 9
- `margin_type`: wickets