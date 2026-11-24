# match_0023 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+1b+1lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=42 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 2→8→20→26→31→42 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠6→1 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 42, achieved 43/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 6w+0nb+0b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Chloe Foster — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 42−1(B)−1(LB)=40 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 43−0(B)−1(LB)=42 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 12 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Emirates Women
- `pom`: Chloe Foster
- `venue`: Northlake Recreation Oval, Northport
- `toss`: Emirates Women won the Toss and elected to Field
- `inn1_total`: 42/6
- `inn1_overs`: 5.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 40
- `inn2_total`: 43/5
- `inn2_overs`: 4.4 Overs
- `inn2_extras`: 7
- `inn2_byes`: 0
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 6
- `inn2_bowling_charged`: 42
- `margin`: 5
- `margin_type`: wickets