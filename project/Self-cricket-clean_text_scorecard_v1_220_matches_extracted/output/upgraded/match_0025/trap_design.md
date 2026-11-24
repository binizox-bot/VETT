# match_0025 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 5w+1nb+1b+1lb=8 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+8=64 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 6→10→17→21→30→52 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠6→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 64−57=7 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 3w+0nb+1b+0lb=4 | [OK] |
| 7 | D3 | POM cross-innings | Elena Frost — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 64−1(B)−1(LB)=62 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 57−1(B)−0(LB)=56 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 22 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Harbor A Women
- `pom`: Elena Frost
- `venue`: Oakfield Community Ground, Eastport
- `toss`: Harbor A Women won the Toss and elected to bat
- `inn1_total`: 64/6
- `inn1_overs`: 9.0 Overs
- `inn1_extras`: 8
- `inn1_byes`: 1
- `inn1_leg_byes`: 1
- `inn1_no_balls`: 1
- `inn1_wides`: 5
- `inn1_bowling_charged`: 62
- `inn2_total`: 57/5
- `inn2_overs`: 9.0 Overs
- `inn2_extras`: 4
- `inn2_byes`: 1
- `inn2_leg_byes`: 0
- `inn2_no_balls`: 0
- `inn2_wides`: 3
- `inn2_bowling_charged`: 56
- `margin`: 7
- `margin_type`: runs