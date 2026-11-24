# match_0172 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+2nb+3b+2lb=21 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+21=196 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 12→40→41→86→107→126→188→196 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 196, achieved 199/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+0nb+0b+1lb=9 | [OK] |
| 7 | D3 | POM cross-innings | Leo Grant (Ridge Falcons) — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 196−3(B)−2(LB)=191 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 199−0(B)−1(LB)=198 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 62 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Ridge Falcons
- `pom`: Leo Grant (Ridge Falcons)
- `venue`: Meridian Youth Cricket Ground, Westhaven
- `toss`: Bayridge Won The Toss And Elected To Bat
- `inn1_total`: 196/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 21
- `inn1_byes`: 3
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 14
- `inn1_bowling_charged`: 191
- `inn2_total`: 199/7
- `inn2_overs`: 36.4 Overs
- `inn2_extras`: 9
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 8
- `inn2_bowling_charged`: 198
- `margin`: 3
- `margin_type`: wickets