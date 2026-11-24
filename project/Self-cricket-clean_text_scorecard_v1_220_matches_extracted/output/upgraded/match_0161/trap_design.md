# match_0161 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+2nb+0b+2lb=13 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+13=157 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 10→15→20→48 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 4≠4→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 157−61=96 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+0nb+0b+2lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Clara Mason — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 157−0(B)−2(LB)=155 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 61−0(B)−2(LB)=59 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 109 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborline Women
- `pom`: Clara Mason
- `venue`: Northshore Youth Oval, Lakeside City
- `toss`: Harborline Women Won The Toss And Elected To Bat
- `inn1_total`: 157/4
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 13
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 9
- `inn1_bowling_charged`: 155
- `inn2_total`: 61/6
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 9
- `inn2_bowling_charged`: 59
- `margin`: 96
- `margin_type`: runs