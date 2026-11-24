# match_0005 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 11w+1nb+1b+4lb=17 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+17=259 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 39→151→171→195→212→236→236→252 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 8≠8→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 259, achieved 263/6 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 8w+1nb+0b+3lb=12 | [OK] |
| 7 | D3 | POM cross-innings | Leo Harper — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 259−1(B)−4(LB)=254 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 263−0(B)−3(LB)=260 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 112 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Meadowbrook XI
- `pom`: Leo Harper
- `venue`: Eastfield Sports Ground, Brookhaven
- `toss`: Stonebridge XI won the Toss and elected to Bat
- `inn1_total`: 259/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 17
- `inn1_byes`: 1
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 1
- `inn1_wides`: 11
- `inn1_bowling_charged`: 254
- `inn2_total`: 263/6
- `inn2_overs`: 46.4 Overs
- `inn2_extras`: 12
- `inn2_byes`: 0
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 1
- `inn2_wides`: 8
- `inn2_bowling_charged`: 260
- `margin`: 4
- `margin_type`: wickets