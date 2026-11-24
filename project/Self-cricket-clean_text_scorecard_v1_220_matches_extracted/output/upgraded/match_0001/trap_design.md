# match_0001 — Reasoning Trap Design

## Core (7 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 1 | D2 | Extras decomposition (Inn1) | 15w+1nb+2b+3lb=21 | [OK] |
| 2 | D2 | Batting+Extras=Total (Inn1) | bat_sum+21=144 | [OK] |
| 3 | D2 | FOW chain (Inn1) | 21→38→46→48→93→111→128→132→132→144 | [OK] |
| 4 | D2 | Bowler wicket sum + non-bowler | 10≠10→0 non-bowler | [OK] |
| 5 | D2 | Result margin | Target 144, achieved 145/5 | [OK] |
| 6 | D2 | Extras decomposition (Inn2) | 7w+1nb+0b+2lb=10 | [OK] |
| 7 | D3 | POM cross-innings | Nolan Hart — verify contribution across both innings | [OK] |

## Hard (+5 traps)

| # | Lvl | Trap | Formula | Valid |
|---|---|---|---|---|
| 8 | D3 | Bowling charged (Inn1) — rule implicit | 144−2(B)−3(LB)=139 | [OK] |
| 9 | D3 | Bowling charged (Inn2) — rule implicit | 145−0(B)−2(LB)=143 | [OK] |
| 10 | D2 | Max partnership (Inn1) | 45 | [OK] |
| 11 | D2 | Partnership extras gap | computed from max partnership | [OK] |
| 12 | D3 | Noise filtering | ~30 numbers in text, ~22 canonical | [OK] |

## Canonical Evidence

- `winner`: Brookfield XI
- `pom`: Nolan Hart
- `venue`: Eastgate Sports Oval, Harbor City
- `toss`: Brookfield XI won the Toss and elected to Field
- `inn1_total`: 144/10
- `inn1_overs`: 35.3 Overs
- `inn1_extras`: 21
- `inn1_byes`: 2
- `inn1_leg_byes`: 3
- `inn1_no_balls`: 1
- `inn1_wides`: 15
- `inn1_bowling_charged`: 139
- `inn2_total`: 145/5
- `inn2_overs`: 33.2 Overs
- `inn2_extras`: 10
- `inn2_byes`: 0
- `inn2_leg_byes`: 2
- `inn2_no_balls`: 1
- `inn2_wides`: 7
- `inn2_bowling_charged`: 143
- `margin`: 5
- `margin_type`: wickets