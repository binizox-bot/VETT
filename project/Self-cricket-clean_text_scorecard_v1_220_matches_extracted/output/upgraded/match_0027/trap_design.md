# match_0027 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 28w+2nb+3b+2lb=35 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+35=304 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 24→225→248→281→296 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 5≠5→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 304−52=252 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 10w+1nb+4b+1lb=16 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 304−3(B)−2(LB)=299 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 52−4(B)−1(LB)=47 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 201 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Seabrook
- `pom`: Ethan Clarke
- `venue`: Meadow Park Oval, Westhaven
- `toss`: Seabrook won the Toss and elected to bat
- `inn1_total`: 304/5
- `inn1_overs`: 34.0 Overs
- `inn1_extras`: 35
- `inn1_byes`: 3
- `inn1_leg_byes`: 2
- `inn1_no_balls`: 2
- `inn1_wides`: 28
- `inn1_bowling_charged`: 299
- `inn2_total`: 52/10
- `inn2_overs`: 19.2 Overs
- `inn2_extras`: 16
- `inn2_byes`: 4
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 1
- `inn2_wides`: 10
- `inn2_bowling_charged`: 47
- `margin`: 252
- `margin_type`: runs