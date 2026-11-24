# match_0008 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+1b+4lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=262 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 27→27→111→178→219→225→234→251 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 6≠8→2 non-bowler | [OK] |
| 5 | D2 | Result margin | 262−157=105 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+2b+1lb=11 | [OK] |
| 7 | D3 | POM cross-innings | Lucas Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 262−1(B)−4(LB)=257 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 157−2(B)−1(LB)=154 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 84 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Coral Coast XI
- `pom`: Lucas Hart
- `venue`: Eastbank Meadow Ground, Hillview
- `toss`: Coral Coast XI won the Toss and elected to bat
- `inn1_total`: 262/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 257
- `inn2_total`: 157/10
- `inn2_overs`: 43.3 Overs
- `inn2_extras`: 11
- `inn2_byes`: 2
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 154
- `margin`: 105
- `margin_type`: runs