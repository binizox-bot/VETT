# match_0108 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+3nb+1b+2lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=219 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 164→195 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 1≠2→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 219−55=164 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+0nb+1b+0lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Nora Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 219−1(B)−2(LB)=216 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 55−1(B)−0(LB)=54 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 164 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Bayview Royals Women
- `pom`: Nora Vale
- `venue`: Seabrook Oval, Eastport
- `toss`: Bayview Royals Women Won The Toss And Elected To Bat
- `inn1_total`: 219/2
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 3
- `inn1_wides`: 12
- `inn1_bowling_charged`: 216
- `inn2_total`: 55/10
- `inn2_overs`: 16.5 Overs
- `inn2_extras`: 8
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 7
- `inn2_bowling_charged`: 54
- `margin`: 164
- `margin_type`: runs