# match_0012 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 8w+1nb+1b+2lb=12 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+12=247 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 23→68→101→165→184→197→215→219→231→247 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 247, achieved 249/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+1nb+0b+2lb=13 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 247−1(B)−2(LB)=244 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 249−0(B)−2(LB)=247 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 64 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Westmere XI
- `pom`: Ethan Vale
- `venue`: Eastbank Meadow Ground, Hillview
- `toss`: Westmere XI won the Toss and elected to Field
- `inn1_total`: 247/10
- `inn1_overs`: 49.3 Overs
- `inn1_extras`: 12
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 8
- `inn1_bowling_charged`: 244
- `inn2_total`: 249/5
- `inn2_overs`: 38.2 Overs
- `inn2_extras`: 13
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 10
- `inn2_bowling_charged`: 247
- `margin`: 5
- `margin_type`: wickets