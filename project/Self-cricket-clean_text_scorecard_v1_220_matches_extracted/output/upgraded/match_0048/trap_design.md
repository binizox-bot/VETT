# match_0048 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 10w+3nb+2b+1lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=236 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 62→93→102→145→189→195→215→225→234→236 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠10→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 236−178=58 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 13w+2nb+6b+2lb=23 | [OK] |
| 7 | D3 | POM cross-innings | Nathan Dale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 236−2(B)−1(LB)=233 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 178−6(B)−2(LB)=170 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 62 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westhaven
- `pom`: Nathan Dale
- `venue`: Northfield Park, Riverton
- `toss`: Westhaven won the Toss and elected to bat
- `inn1_total`: 236/10
- `inn1_overs`: 48.1 Overs
- `inn1_extras`: 16
- `inn1_byes`: 2
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 3
- `inn1_wides`: 10
- `inn1_bowling_charged`: 233
- `inn2_total`: 178/10
- `inn2_overs`: 37.3 Overs
- `inn2_extras`: 23
- `inn2_byes`: 6
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 2
- `inn2_wides`: 13
- `inn2_bowling_charged`: 170
- `margin`: 58
- `margin_type`: runs