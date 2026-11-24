# match_0219 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+1b+2lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=64 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 4→12→12→22→31→33→44→53→62→64 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 64, achieved 65/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+0b+1lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Caleb Rowan — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 64−1(B)−2(LB)=61 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 65−0(B)−1(LB)=64 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 11 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Brookhaven XI
- `pom`: Caleb Rowan
- `venue`: Ashfield Park, East Midlands
- `toss`: Brookhaven XI won the Toss and elected to Field
- `inn1_total`: 64/10
- `inn1_overs`: 26.2 Overs
- `inn1_extras`: 10
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 61
- `inn2_total`: 65/3
- `inn2_overs`: 11.4 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 64
- `margin`: 7
- `margin_type`: wickets