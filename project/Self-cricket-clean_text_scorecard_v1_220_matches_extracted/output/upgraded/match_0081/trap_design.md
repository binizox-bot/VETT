# match_0081 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 21w+1nb+0b+2lb=24 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+24=296 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 122→146→216→229→251→251→280→289→292 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠9→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 296−218=78 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+1nb+1b+1lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Adrian Wells — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 296−0(B)−2(LB)=294 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 218−1(B)−1(LB)=216 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 122 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northport Harbor
- `pom`: Adrian Wells
- `venue`: Central Academy Oval, Westbridge
- `toss`: Highland Vale Won The Toss And Elected To Field
- `inn1_total`: 296/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 24
- `inn1_byes`: 0
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 21
- `inn1_bowling_charged`: 294
- `inn2_total`: 218/10
- `inn2_overs`: 47.3 Overs
- `inn2_extras`: 11
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 8
- `inn2_bowling_charged`: 216
- `margin`: 78
- `margin_type`: runs