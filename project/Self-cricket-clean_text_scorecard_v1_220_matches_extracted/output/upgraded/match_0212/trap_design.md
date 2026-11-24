# match_0212 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 7w+0nb+1b+2lb=10 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+10=106 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 8→18→32→38→66→78→88→94→101→106 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 106, achieved 109/3 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 4w+0nb+0b+2lb=6 | [OK] |
| 7 | D3 | POM cross-innings | Noah Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 106−1(B)−2(LB)=103 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 109−0(B)−2(LB)=107 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 28 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Silvergate CC
- `pom`: Noah Vale
- `venue`: Willowmere Ground, Eastford
- `toss`: Silvergate CC won the Toss and elected to Field
- `inn1_total`: 106/10
- `inn1_overs`: 31.2 Overs
- `inn1_extras`: 10
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 0
- `inn1_wides`: 7
- `inn1_bowling_charged`: 103
- `inn2_total`: 109/3
- `inn2_overs`: 21.2 Overs
- `inn2_extras`: 6
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 0
- `inn2_wides`: 4
- `inn2_bowling_charged`: 107
- `margin`: 7
- `margin_type`: wickets