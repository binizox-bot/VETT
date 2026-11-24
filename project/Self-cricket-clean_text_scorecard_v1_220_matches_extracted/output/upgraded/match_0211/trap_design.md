# match_0211 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 20w+2nb+1b+3lb=26 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+26=304 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 22→35→151→190→257→277→288→294 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 304−72=232 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 5w+0nb+1b+1lb=7 | [OK] |
| 7 | D3 | POM cross-innings | Ethan Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 304−1(B)−3(LB)=300 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 72−1(B)−1(LB)=70 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 116 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Cedarbridge Falcons
- `pom`: Ethan Vale
- `venue`: Willowbank Oval, Eastport
- `toss`: Mariner Vale Dolphins won the Toss and elected to Field
- `inn1_total`: 304/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 26
- `inn1_byes`: 1
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 2
- `inn1_wides`: 20
- `inn1_bowling_charged`: 300
- `inn2_total`: 72/10
- `inn2_overs`: 29.3 Overs
- `inn2_extras`: 7
- `inn2_byes`: 1
- `inn2_leg_byes`: 1
- `inn2_no_balls`: 0
- `inn2_wides`: 5
- `inn2_bowling_charged`: 70
- `margin`: 232
- `margin_type`: runs