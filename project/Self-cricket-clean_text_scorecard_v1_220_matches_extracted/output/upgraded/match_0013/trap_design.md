# match_0013 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+1nb+1b+3lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=263 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 8→50→116→131→201→219→255→263 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 263, achieved 264/7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+1nb+1b+4lb=18 | [OK] |
| 7 | D3 | POM cross-innings | Connor Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 263−1(B)−3(LB)=259 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 264−1(B)−4(LB)=259 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 70 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Mirage Lions XI
- `pom`: Connor Vale
- `venue`: Eastbank Meadow Ground, Hillview
- `toss`: Mirage Lions XI won the Toss and elected to Field
- `inn1_total`: 263/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 12
- `inn1_bowling_charged`: 259
- `inn2_total`: 264/7
- `inn2_overs`: 46.2 Overs
- `inn2_extras`: 18
- `inn2_byes`: 1
- `inn2_leg_byes`: 4
- `inn2_no_balls`: 1
- `inn2_wides`: 12
- `inn2_bowling_charged`: 259
- `margin`: 3
- `margin_type`: wickets