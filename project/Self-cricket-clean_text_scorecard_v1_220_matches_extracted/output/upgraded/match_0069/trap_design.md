# match_0069 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+0b+1lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=152 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 35→137→146 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 3≠3→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 152−44=96 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+1nb+0b+0lb=4 | [OK] |
| 7 | D3 | POM cross-innings | Aaron Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 152−0(B)−1(LB)=151 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 44−0(B)−0(LB)=44 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 102 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northbridge
- `pom`: Aaron Vale
- `venue`: Kingsgate Park, Riverton
- `toss`: Oakfield won the Toss and elected to Field
- `inn1_total`: 152/3
- `inn1_overs`: 25.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 0
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 151
- `inn2_total`: 44/9
- `inn2_overs`: 12.1 Overs
- `inn2_extras`: 4
- `inn2_byes`: 0
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 1
- `inn2_wides`: 3
- `inn2_bowling_charged`: 44
- `margin`: 96
- `margin_type`: runs