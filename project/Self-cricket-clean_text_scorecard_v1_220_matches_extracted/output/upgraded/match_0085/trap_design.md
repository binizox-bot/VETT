# match_0085 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+0nb+1b+6lb=18 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+18=226 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→56→118→121→130→161→179→224→226 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠9→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 226, achieved 229/8 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 15w+0nb+0b+2lb=17 | [OK] |
| 7 | D3 | POM cross-innings | Milo Bell — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 226−1(B)−6(LB)=219 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 229−0(B)−2(LB)=227 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 62 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Metrovale
- `pom`: Milo Bell
- `venue`: Central Academy Ground, Eastport
- `toss`: Metrovale Won The Toss And Elected To Field
- `inn1_total`: 226/9
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 18
- `inn1_byes`: 1
- `inn1_leg_byes`: 6
- `inn1_no_balls`: 0
- `inn1_wides`: 11
- `inn1_bowling_charged`: 219
- `inn2_total`: 229/8
- `inn2_overs`: 48.5 Overs
- `inn2_extras`: 17
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 15
- `inn2_bowling_charged`: 227
- `margin`: 2
- `margin_type`: wickets