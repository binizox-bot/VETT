# match_0135 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 6w+3nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=194 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 18→27→79→120→134→160→190→190→194 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠9→3 non-bowler | [OK] |
| 5 | D2 | Result margin | 194−152=42 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+1nb+0b+1lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Arman Reed — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 194−1(B)−2(LB)=191 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 152−0(B)−1(LB)=151 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 52 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Cedarbridge XI
- `pom`: Arman Reed
- `venue`: Maplebank Oval, Eastford
- `toss`: Falcon Bay XI Won The Toss And Elected To Field
- `inn1_total`: 194/9
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 3
- `inn1_wides`: 6
- `inn1_bowling_charged`: 191
- `inn2_total`: 152/9
- `inn2_overs`: 20.0 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 8
- `inn2_bowling_charged`: 151
- `margin`: 42
- `margin_type`: runs