# match_0049 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 12w+4nb+2b+4lb=22 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+22=342 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 9→26→173→187→280→290→293→297→324→342 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | 342−96=246 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+2nb+2b+3lb=14 | [OK] |
| 7 | D3 | POM cross-innings | Elias Vale — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 342−2(B)−4(LB)=336 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 96−2(B)−3(LB)=91 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 147 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Northmoor
- `pom`: Elias Vale
- `venue`: Cedar Park Oval, Ashford
- `toss`: Stoneford won the Toss and elected to Field
- `inn1_total`: 342/10
- `inn1_overs`: 42.0 Overs
- `inn1_extras`: 22
- `inn1_byes`: 2
- `inn1_leg_byes`: 4
- `inn1_no_balls`: 4
- `inn1_wides`: 12
- `inn1_bowling_charged`: 336
- `inn2_total`: 96/10
- `inn2_overs`: 28.4 Overs
- `inn2_extras`: 14
- `inn2_byes`: 2
- `inn2_leg_byes`: 3
- `inn2_no_balls`: 2
- `inn2_wides`: 7
- `inn2_bowling_charged`: 91
- `margin`: 246
- `margin_type`: runs