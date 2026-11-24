# match_0218 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+0nb+1b+1lb=11 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+11=86 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→8→18→19→30→35→39→69→84→86 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 86, achieved 89/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Caleb Rowan — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 86−1(B)−1(LB)=84 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 89−0(B)−1(LB)=88 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 30 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Lakeshore CC
- `pom`: Caleb Rowan
- `venue`: Ridgefield Oval, Northmere
- `toss`: Hillcrest CC won the Toss and elected to Bat
- `inn1_total`: 86/10
- `inn1_overs`: 27.3 Overs
- `inn1_extras`: 11
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 9
- `inn1_bowling_charged`: 84
- `inn2_total`: 89/3
- `inn2_overs`: 18.2 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 88
- `margin`: 7
- `margin_type`: wickets