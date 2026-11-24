# match_0195 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 23w+2nb+1b+3lb=29 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+29=286 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 15→74→74→140→212→234→251→282→284 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 9≠9→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 286−43=243 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+2nb+0b+1lb=8 | [OK] |
| 7 | D3 | POM cross-innings | Leo Voss (Harborstone) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 286−1(B)−3(LB)=282 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 43−0(B)−1(LB)=42 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 72 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborstone
- `pom`: Leo Voss (Harborstone)
- `venue`: Brookmere Club Ground, Westgate
- `toss`: Ridgebay Won The Toss And Elected To Field
- `inn1_total`: 286/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 29
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 2
- `inn1_wides`: 23
- `inn1_bowling_charged`: 282
- `inn2_total`: 43/10
- `inn2_overs`: 20.4 Overs
- `inn2_extras`: 8
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 2
- `inn2_wides`: 5
- `inn2_bowling_charged`: 42
- `margin`: 243
- `margin_type`: runs