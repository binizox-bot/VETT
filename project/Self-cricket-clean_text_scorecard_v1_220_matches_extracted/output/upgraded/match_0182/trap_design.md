# match_0182 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+1nb+1b+3lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=312 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 94→101→162→163→259→298→302→310 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 312−172=140 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 9w+2nb+2b+5lb=18 | [OK] |
| 7 | D3 | POM cross-innings | Liam Hart (Cedar Vale) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 312−1(B)−3(LB)=308 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 172−2(B)−5(LB)=165 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 96 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Cedar Vale
- `pom`: Liam Hart (Cedar Vale)
- `venue`: Riverside College Ground, Eastport
- `toss`: Cedar Vale Won The Toss And Elected To Bat
- `inn1_total`: 312/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 12
- `inn1_bowling_charged`: 308
- `inn2_total`: 172/10
- `inn2_overs`: 42.5 Overs
- `inn2_extras`: 18
- `inn2_byes`: 2
- `inn2_leg_byes`: 5
- `inn2_no_balls`: 2
- `inn2_wides`: 9
- `inn2_bowling_charged`: 165
- `margin`: 140
- `margin_type`: runs