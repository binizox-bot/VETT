# match_0165 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+0nb+2b+1lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=142 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 37→41→51→76→82 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 142−38=104 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+3b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Mira Lawson (Aurora Bay Women) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 142−2(B)−1(LB)=139 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 38−3(B)−1(LB)=34 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 60 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Aurora Bay Women
- `pom`: Mira Lawson (Aurora Bay Women)
- `venue`: Maple Coast Oval, Brookhaven
- `toss`: Aurora Bay Women Won The Toss And Elected To Bat
- `inn1_total`: 142/5
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 6
- `inn1_bowling_charged`: 139
- `inn2_total`: 38/10
- `inn2_overs`: 14.5 Overs
- `inn2_extras`: 10
- `inn2_byes`: 3
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 34
- `margin`: 104
- `margin_type`: runs