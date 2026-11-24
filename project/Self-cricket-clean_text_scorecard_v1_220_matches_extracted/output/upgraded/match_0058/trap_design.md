# match_0058 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+1nb+1b+2lb=16 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+16=152 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 5→41→102→118→123→128→130→146→152→152 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 152, achieved 154/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 16w+1nb+0b+1lb=18 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 152−1(B)−2(LB)=149 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 154−0(B)−1(LB)=153 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 61 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harborford
- `pom`: Ethan Vale
- `venue`: Riverside Training Ground, Lakeford
- `toss`: Harborford won the Toss and elected to Field
- `inn1_total`: 152/10
- `inn1_overs`: 42.3 Overs
- `inn1_extras`: 16
- `inn1_byes`: 1
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 1
- `inn1_wides`: 12
- `inn1_bowling_charged`: 149
- `inn2_total`: 154/6
- `inn2_overs`: 25.2 Overs
- `inn2_extras`: 18
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 16
- `inn2_bowling_charged`: 153
- `margin`: 4
- `margin_type`: wickets