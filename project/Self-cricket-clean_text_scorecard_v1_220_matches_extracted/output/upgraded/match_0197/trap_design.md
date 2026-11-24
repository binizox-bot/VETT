# match_0197 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 16w+3nb+1b+2lb=22 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+22=407 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 136→154→297→318→380→403 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠6→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 407−43=364 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+1nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Noah Barrett (Northbridge) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 407−1(B)−2(LB)=404 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 43−0(B)−1(LB)=42 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 143 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbridge
- `pom`: Noah Barrett (Northbridge)
- `venue`: Cedarbrook Turf Ground, Westmere
- `toss`: Meadowvale Won The Toss And Elected To Field
- `inn1_total`: 407/6
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 22
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 3
- `inn1_wides`: 16
- `inn1_bowling_charged`: 404
- `inn2_total`: 43/10
- `inn2_overs`: 23.5 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 5
- `inn2_bowling_charged`: 42
- `margin`: 364
- `margin_type`: runs