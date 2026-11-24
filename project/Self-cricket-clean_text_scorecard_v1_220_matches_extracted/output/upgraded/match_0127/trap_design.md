# match_0127 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 9w+1nb+0b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=204 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 31→115→148→152→190→193→193→194 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 204−151=53 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+0b+3lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Ronald Stone — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 204−0(B)−2(LB)=202 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 151−0(B)−3(LB)=148 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 84 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northvale
- `pom`: Ronald Stone
- `venue`: Red Mesa Oval, Eastmere
- `toss`: Northvale Won The Toss And Elected To Bat
- `inn1_total`: 204/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 12
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 9
- `inn1_bowling_charged`: 202
- `inn2_total`: 151/10
- `inn2_overs`: 18.5 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 148
- `margin`: 53
- `margin_type`: runs