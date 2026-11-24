# match_0125 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+2nb+0b+1lb=9 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+9=150 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→35→43→45→55→100→112 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠7→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 150−137=13 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+0nb+0b+1lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Caleb Grant — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 150−0(B)−1(LB)=149 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 137−0(B)−1(LB)=136 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 45 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Eastmoor
- `pom`: Caleb Grant
- `venue`: Red Mesa Ground, Eastmere
- `toss`: Eastmoor Won The Toss And Elected To Bat
- `inn1_total`: 150/7
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 9
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 2
- `inn1_wides`: 6
- `inn1_bowling_charged`: 149
- `inn2_total`: 137/10
- `inn2_overs`: 19.4 Overs
- `inn2_extras`: 11
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 10
- `inn2_bowling_charged`: 136
- `margin`: 13
- `margin_type`: runs