# match_0090 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+0nb+1b+2lb=14 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+14=78 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 14→25→32→38→43→55→63→72 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 78, achieved 82/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Daniel Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 78−1(B)−2(LB)=75 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 82−0(B)−1(LB)=81 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 14 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Norchester
- `pom`: Daniel Hart
- `venue`: Greenfield Park, Midlands
- `toss`: Norchester Won The Toss And Elected To Field
- `inn1_total`: 78/8
- `inn1_overs`: 20.0 Overs
- `inn1_extras`: 14
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 11
- `inn1_bowling_charged`: 75
- `inn2_total`: 82/3
- `inn2_overs`: 10.1 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 81
- `margin`: 7
- `margin_type`: wickets