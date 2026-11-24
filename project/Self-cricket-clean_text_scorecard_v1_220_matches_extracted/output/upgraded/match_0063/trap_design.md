# match_0063 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 19w+3nb+1b+2lb=25 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+25=218 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 20→41→120→163→173→174→184→199→215→218 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠10→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 218−164=54 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 15w+1nb+0b+4lb=20 | [OK] |
| 7 | D3 | POM cross-innings | Finn Grant — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 218−1(B)−2(LB)=215 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 164−0(B)−4(LB)=160 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 79 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Brookfield
- `pom`: Finn Grant
- `venue`: Eastbank Park, Midland Vale
- `toss`: Northmoor won the Toss and elected to Field
- `inn1_total`: 218/10
- `inn1_overs`: 43.2 Overs
- `inn1_extras`: 25
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 3
- `inn1_wides`: 19
- `inn1_bowling_charged`: 215
- `inn2_total`: 164/10
- `inn2_overs`: 39.1 Overs
- `inn2_extras`: 20
- `inn2_byes`: 0
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 1
- `inn2_wides`: 15
- `inn2_bowling_charged`: 160
- `margin`: 54
- `margin_type`: runs