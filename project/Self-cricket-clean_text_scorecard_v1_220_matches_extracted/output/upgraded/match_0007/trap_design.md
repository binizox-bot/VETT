# match_0007 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 14w+1nb+2b+3lb=20 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+20=314 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 16→21→55→227→269→292→305→312 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 7≠8→1 non-bowler | [OK] |
| 5 | D2 | Result margin | 314−227=87 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 12w+1nb+0b+2lb=15 | [OK] |
| 7 | D3 | POM cross-innings | Owen Clarke — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 314−2(B)−3(LB)=309 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 227−0(B)−2(LB)=225 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 172 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Cedar Heights XI
- `pom`: Owen Clarke
- `venue`: Brookfield Oval, Eastmere
- `toss`: Dune Rangers won the Toss and elected to Field
- `inn1_total`: 314/8
- `inn1_overs`: 50.0 Overs
- `inn1_extras`: 20
- `inn1_byes`: 2
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 14
- `inn1_bowling_charged`: 309
- `inn2_total`: 227/10
- `inn2_overs`: 42.5 Overs
- `inn2_extras`: 15
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 12
- `inn2_bowling_charged`: 225
- `margin`: 87
- `margin_type`: runs